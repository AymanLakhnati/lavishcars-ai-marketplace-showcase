from fastapi import HTTPException
from sqlalchemy import select, func
from .models import Brand, Category, Listing, Location, Supplier, VehicleModel
from .relationships import listing_categories, listing_images


def active_location_ids():
    """A market is enabled only when it and every ancestor are active."""
    tree = (
        select(Location.id)
        .where(Location.parent_id.is_(None), Location.active.is_(True))
        .cte("active_locations", recursive=True)
    )
    tree = tree.union_all(
        select(Location.id)
        .join(tree, Location.parent_id == tree.c.id)
        .where(Location.active.is_(True))
    )
    return select(tree.c.id)


def public_query():
    return (
        select(Listing)
        .join(Supplier)
        .where(
            Listing.status == "published",
            Supplier.status == "approved",
            Supplier.active.is_(True),
            Listing.admin_hidden.is_(False),
            Listing.location_id.in_(active_location_ids()),
        )
    )


def country_for(db, location):
    while location.parent_id:
        location = db.get(Location, location.parent_id)
    return location.name


def listing_dict(db, item):
    model = db.get(VehicleModel, item.model_id)
    brand = db.get(Brand, model.brand_id)
    city = db.get(Location, item.location_id)
    return {
        "id": item.id,
        "slug": item.slug,
        "title": f"{brand.name} {model.name}",
        "brand": brand.name,
        "model": model.name,
        "year": item.year,
        "city": city.name,
        "country": country_for(db, city),
        "category": db.get(Category, item.category_id).name,
        "categories": listing_categories(db, item),
        "images": listing_images(db, item),
        "supplier_name": db.get(Supplier, item.supplier_id).company_name,
        **{
            key: getattr(item, key)
            for key in (
                "currency",
                "seats",
                "transmission",
                "description",
                "features",
                "status",
                "rejection_reason",
                "mileage",
                "admin_hidden",
                "trim",
                "vehicle_type",
            )
        },
        **{
            key: float(getattr(item, key)) if getattr(item, key) is not None else None
            for key in ("daily_price", "weekly_price", "monthly_price", "deposit")
        },
    }


def resolve_listing(db, payload):
    brand = db.scalar(
        select(Brand).where(func.lower(Brand.name) == payload.brand.lower())
    )
    model = (
        db.scalar(
            select(VehicleModel).where(
                VehicleModel.brand_id == brand.id,
                func.lower(VehicleModel.name) == payload.model.lower(),
            )
        )
        if brand
        else None
    )
    if not model:
        raise HTTPException(422, "Choose an existing brand and its matching model")
    city = db.scalar(
        select(Location).where(
            func.lower(Location.name) == payload.city.lower(),
            Location.kind == "city",
            Location.active.is_(True),
            Location.id.in_(active_location_ids()),
        )
    )
    if not city or country_for(db, city).lower() != payload.country.lower():
        raise HTTPException(
            422, "City must belong to the selected country and be active"
        )
    if payload.currency != ("AED" if country_for(db, city) == "UAE" else "USD"):
        raise HTTPException(422, "Currency must match the location's market")
    category = db.scalar(
        select(Category).where(func.lower(Category.name) == payload.category.lower())
    )
    if not category:
        raise HTTPException(422, "Unknown category")
    values = payload.model_dump(
        exclude={"brand", "model", "city", "country", "category", "categories"}
    )
    values["vehicle_type"] = payload.vehicle_type or {
        "SUV": "SUV",
        "Convertible": "Convertible",
        "Sports": "Coupe",
        "Supercar": "Coupe",
    }.get(payload.category, "Sedan")
    return {
        **values,
        "model_id": model.id,
        "location_id": city.id,
        "category_id": category.id,
    }


def page(db, query, serialize, page=1, page_size=24):
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [serialize(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def record_dict(item):
    return {
        column.name: getattr(item, column.name) for column in item.__table__.columns
    }
