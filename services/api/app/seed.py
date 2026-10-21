"""Idempotent synthetic development fixtures. Never run in production."""

import os
from sqlalchemy import select
from .db import SessionLocal
from .models import Brand, Category, Listing, Location, Supplier, User, VehicleModel
from .security import hash_password


def seed(db):
    if os.getenv("APP_ENV", "development") == "production":
        raise RuntimeError("Demo seeding is disabled in production")
    if db.scalar(select(User).where(User.email == "admin@lavish.demo")):
        from .relationships import seed_associations

        seed_associations(db)
        db.commit()
        return
    password = os.getenv("DEMO_PASSWORD", "DemoDrive!2026")
    approved = Supplier(
        company_name="Desert Atelier Motors · Demo",
        contact_email="supplier@lavish.demo",
        status="approved",
        license_number="DEMO-UAE-001",
    )
    pending = Supplier(
        company_name="Horizon Drive · Demo",
        contact_email="pending@lavish.demo",
        status="pending",
        license_number="DEMO-UAE-002",
    )
    houston = Supplier(
        company_name="Lone Star Collection · Demo",
        contact_email="houston@lavish.demo",
        status="approved",
        license_number="DEMO-US-003",
    )
    db.add_all([approved, pending, houston])
    db.flush()
    for email, role, supplier in [
        ("admin@lavish.demo", "admin", None),
        ("supplier@lavish.demo", "supplier", approved),
        ("pending@lavish.demo", "supplier", pending),
        ("houston@lavish.demo", "supplier", houston),
    ]:
        db.add(
            User(
                email=email,
                role=role,
                supplier_id=supplier.id if supplier else None,
                password_hash=hash_password(password),
            )
        )
    uae, usa = (
        Location(name="UAE", kind="country"),
        Location(name="USA", kind="country"),
    )
    db.add_all([uae, usa])
    db.flush()
    texas = Location(name="Texas", kind="state", parent_id=usa.id)
    florida = Location(name="Florida", kind="state", parent_id=usa.id, active=False)
    dubai = Location(name="Dubai", kind="city", parent_id=uae.id)
    db.add_all([texas, florida, dubai])
    db.flush()
    hou = Location(name="Houston", kind="city", parent_id=texas.id)
    db.add_all(
        [
            hou,
            Location(name="Abu Dhabi", kind="city", parent_id=uae.id, active=False),
            Location(name="Sharjah", kind="city", parent_id=uae.id, active=False),
            Location(name="Miami", kind="city", parent_id=florida.id, active=False),
        ]
    )
    categories = {}
    for name in [
        "Luxury",
        "SUV",
        "Sports",
        "Supercar",
        "Economy",
        "Electric",
        "Convertible",
    ]:
        categories[name] = Category(name=name)
        db.add(categories[name])
    db.flush()
    fixtures = [
        (
            "Land Rover",
            "Range Rover Sport",
            "SUV",
            900,
            dubai,
            "published",
            "/images/range-rover.svg",
        ),
        (
            "Mercedes-Benz",
            "G-Class",
            "SUV",
            990,
            dubai,
            "published",
            "/images/g-class.svg",
        ),
        (
            "Cadillac",
            "Escalade",
            "SUV",
            850,
            dubai,
            "published",
            "/images/escalade.svg",
        ),
        (
            "Porsche",
            "911 Carrera",
            "Sports",
            1250,
            dubai,
            "published",
            "/images/porsche.svg",
        ),
        (
            "Lamborghini",
            "Urus",
            "Supercar",
            2200,
            dubai,
            "published",
            "/images/urus.svg",
        ),
        (
            "Ferrari",
            "Roma",
            "Supercar",
            2800,
            dubai,
            "published",
            "/images/ferrari.svg",
        ),
        (
            "Rolls-Royce",
            "Ghost",
            "Luxury",
            2400,
            dubai,
            "published",
            "/images/rolls-royce.svg",
        ),
        ("BMW", "7 Series", "Luxury", 750, dubai, "published", "/images/bmw.svg"),
        ("Tesla", "Model S", "Electric", 195, hou, "published", "/images/tesla.svg"),
        (
            "Ford",
            "Mustang",
            "Convertible",
            165,
            hou,
            "published",
            "/images/mustang.svg",
        ),
        ("Cadillac", "Escalade", "SUV", 290, hou, "published", "/images/escalade.svg"),
        (
            "Mercedes-Benz",
            "G-Class",
            "SUV",
            390,
            hou,
            "published",
            "/images/g-class.svg",
        ),
        (
            "Land Rover",
            "Range Rover Sport",
            "SUV",
            800,
            dubai,
            "pending",
            "/images/range-rover.svg",
        ),
        ("BMW", "7 Series", "Luxury", 700, dubai, "rejected", "/images/bmw.svg"),
        (
            "Porsche",
            "911 Carrera",
            "Sports",
            1200,
            dubai,
            "paused",
            "/images/porsche.svg",
        ),
    ]
    brand_cache, model_cache = {}, {}
    for index, (
        brand_name,
        model_name,
        category,
        price,
        city,
        status,
        image,
    ) in enumerate(fixtures):
        if brand_name not in brand_cache:
            brand_cache[brand_name] = Brand(name=brand_name)
            db.add(brand_cache[brand_name])
            db.flush()
        key = (brand_name, model_name)
        if key not in model_cache:
            model_cache[key] = VehicleModel(
                name=model_name, brand_id=brand_cache[brand_name].id
            )
            db.add(model_cache[key])
            db.flush()
        supplier = houston if city == hou else approved
        db.add(
            Listing(
                slug=f"{brand_name}-{model_name}-{city.name}-{index + 1}".lower().replace(
                    " ", "-"
                ),
                supplier_id=supplier.id,
                model_id=model_cache[key].id,
                location_id=city.id,
                category_id=categories[category].id,
                year=2026,
                currency="USD" if city == hou else "AED",
                daily_price=price,
                weekly_price=price * 6,
                monthly_price=price * 23,
                deposit=price * 2,
                mileage=250,
                seats=7
                if model_name == "Escalade"
                else 5
                if category in ("SUV", "Luxury", "Electric")
                else 2,
                transmission="Automatic",
                description=f"A considered choice for your next journey. This {brand_name} {model_name} is synthetic demonstration inventory; request a quote to confirm dates, final pricing and rental terms.",
                features=[
                    "Bluetooth",
                    "Climate control",
                    "Leather interior",
                    "Navigation",
                ],
                images=[],
                status=status,
                rejection_reason="Please verify the vehicle specification and replace the cover image."
                if status == "rejected"
                else "",
            )
        )
    db.flush()
    from .relationships import seed_associations

    seed_associations(db)
    db.commit()


if __name__ == "__main__":
    with SessionLocal() as db:
        seed(db)
    print("Synthetic demonstration inventory is ready.")
