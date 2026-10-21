"""Deterministic recommendations with explicit hard filters and explainable soft scoring."""

from fastapi import HTTPException
from sqlalchemy import select, func
from .catalog import active_location_ids, country_for, public_query, listing_dict
from .models import Listing, Location, Category, ListingCategory

OCCASION_CATEGORIES = {
    "business": ["Luxury", "Electric"],
    "family": ["SUV"],
    "celebration": ["Luxury", "Convertible", "Supercar"],
    "leisure": ["Sports", "Convertible"],
}


def recommendations(db, constraints):
    city = db.scalar(
        select(Location).where(
            func.lower(Location.name) == constraints.city.lower(),
            Location.kind == "city",
            Location.active.is_(True),
            Location.id.in_(active_location_ids()),
        )
    )
    if not city:
        raise HTTPException(422, "Choose an active city from the catalog")
    currency = "AED" if country_for(db, city) == "UAE" else "USD"
    if constraints.currency and constraints.currency != currency:
        raise HTTPException(
            422, "Currency does not match the city; conversion is not supported"
        )
    names = set(db.scalars(select(Category.name)))
    if (
        constraints.category
        and constraints.category not in names
        or any(x not in names for x in constraints.preferred_categories)
    ):
        raise HTTPException(422, "Unknown category")
    query = public_query().where(
        Listing.location_id == city.id, Listing.currency == currency
    )
    if constraints.category:
        query = query.where(
            Listing.id.in_(
                select(ListingCategory.listing_id)
                .join(Category, Category.id == ListingCategory.category_id)
                .where(Category.name == constraints.category)
            )
        )
    if constraints.max_price is not None:
        query = query.where(Listing.daily_price <= constraints.max_price)
    if constraints.min_seats:
        query = query.where(Listing.seats >= constraints.min_seats)
    # Bounded candidate pool, explicitly disclosed; no invented features or availability.
    rows = db.scalars(query.order_by(Listing.daily_price, Listing.id).limit(500)).all()
    ranked = []
    for row in rows:
        item = listing_dict(db, row)
        actual_features = {x.lower() for x in row.features}
        if any(x.lower() not in actual_features for x in constraints.features):
            continue
        score = 0
        reasons = [
            f"Listed in {city.name}",
            f"{currency} {item['daily_price']:,.0f}/day",
            f"{row.seats} seats",
        ]
        actual_categories = set(item["categories"]) | {item["category"]}
        if actual_categories.intersection(constraints.preferred_categories):
            score += 20
            reasons.append("Preferred category: +20 ranking points")
        if actual_categories.intersection(
            OCCASION_CATEGORIES.get(constraints.occasion, [])
        ):
            score += 10
            reasons.append(
                f"Category suited to {constraints.occasion} by our stated editorial rule: +10 points"
            )
        for feature in constraints.features:
            reasons.append("Required listed feature: " + feature)
        ranked.append({"listing": item, "match_reasons": reasons, "score": score})
    ranked.sort(
        key=lambda x: (-x["score"], x["listing"]["daily_price"], x["listing"]["id"])
    )
    return {
        "filters": constraints.model_dump(mode="json"),
        "recommendations": ranked[:3],
        "mode": "deterministic",
        "needs_clarification": False,
        "message": "Database-grounded suggestions. Hard constraints are never relaxed. Preferred category adds 20 points; occasion-category fit adds 10. Ties use lower daily price, then listing ID. The lowest-priced 500 eligible candidates are considered. Supplier confirmation is required for dates and final terms.",
    }
