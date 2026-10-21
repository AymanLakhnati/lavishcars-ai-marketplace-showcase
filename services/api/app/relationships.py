"""Normalized associations; legacy listing arrays are compatibility write mirrors."""

from fastapi import HTTPException
from sqlalchemy import select, delete
from .models import (
    Category,
    Listing,
    ListingCategory,
    ListingImage,
    SupplierLocation,
    SupplierUser,
    User,
)


def listing_images(db, listing):
    return list(
        db.scalars(
            select(ListingImage.url)
            .where(ListingImage.listing_id == listing.id)
            .order_by(ListingImage.position)
        )
    )


def listing_categories(db, listing):
    return list(
        db.scalars(
            select(Category.name)
            .join(ListingCategory, ListingCategory.category_id == Category.id)
            .where(ListingCategory.listing_id == listing.id)
            .order_by(Category.name)
        )
    )


def sync_listing(db, listing, body):
    requested = set(body.categories) | {body.category}
    categories = db.scalars(select(Category).where(Category.name.in_(requested))).all()
    if {x.name for x in categories} != requested:
        raise HTTPException(422, "Choose existing categories")
    served = list(
        db.scalars(
            select(SupplierLocation.location_id).where(
                SupplierLocation.supplier_id == listing.supplier_id
            )
        )
    )
    if served and listing.location_id not in served:
        raise HTTPException(422, "The listing city must be a supplier service area")
    if not served:
        db.add(
            SupplierLocation(
                supplier_id=listing.supplier_id, location_id=listing.location_id
            )
        )
    db.flush()
    db.execute(delete(ListingCategory).where(ListingCategory.listing_id == listing.id))
    db.execute(delete(ListingImage).where(ListingImage.listing_id == listing.id))
    db.add_all(
        ListingCategory(listing_id=listing.id, category_id=x.id) for x in categories
    )
    db.add_all(
        ListingImage(listing_id=listing.id, position=i, url=url)
        for i, url in enumerate(body.images)
    )
    db.flush()


def seed_associations(db):
    for user in db.scalars(select(User).where(User.supplier_id.is_not(None))):
        if not db.get(SupplierUser, (user.supplier_id, user.id)):
            db.add(
                SupplierUser(
                    supplier_id=user.supplier_id,
                    user_id=user.id,
                    membership_role="owner",
                )
            )
    db.flush()
    for listing in db.scalars(select(Listing)):
        if not db.get(SupplierLocation, (listing.supplier_id, listing.location_id)):
            db.add(
                SupplierLocation(
                    supplier_id=listing.supplier_id, location_id=listing.location_id
                )
            )
        if not db.get(ListingCategory, (listing.id, listing.category_id)):
            category = db.get(Category, listing.category_id)
            listing.vehicle_type = {
                "SUV": "SUV",
                "Convertible": "Convertible",
                "Sports": "Coupe",
                "Supercar": "Coupe",
            }.get(category.name, "Sedan")
            db.add(
                ListingCategory(listing_id=listing.id, category_id=listing.category_id)
            )
        if not db.scalar(
            select(ListingImage.id).where(ListingImage.listing_id == listing.id)
        ):
            db.add_all(
                ListingImage(listing_id=listing.id, position=i, url=url)
                for i, url in enumerate(listing.images)
            )
        db.flush()
