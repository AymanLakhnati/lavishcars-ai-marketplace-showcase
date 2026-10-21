"""Constraint-first interpretation; recommendation facts always come from inventory."""

import re
from sqlalchemy import select
from .catalog import active_location_ids, country_for, listing_dict, public_query
from .models import Category, Listing, Location, Brand, VehicleModel, ListingCategory

WORDS = dict(
    zip(
        "one two three four five six seven eight nine ten eleven twelve".split(),
        range(1, 13),
    )
)


def normalize(message):
    text = message.lower().replace(",", "")
    return re.sub(
        r"\b(" + "|".join(WORDS) + r")\b", lambda m: str(WORDS[m.group()]), text
    )


def recommend(db, message):
    text = normalize(message)
    filters = {}

    def clarify(message):
        return {
            "filters": filters,
            "recommendations": [],
            "mode": "deterministic",
            "needs_clarification": True,
            "message": message,
        }

    if re.search(r"\b(?:listing|vehicle)\s*(?:id\s*)?#?\d+\b", text):
        return clarify(
            "Please describe your destination and vehicle preferences instead of a listing ID. Vehicle details are available through the public catalog."
        )
    cities = db.scalars(
        select(Location).where(
            Location.kind == "city", Location.id.in_(active_location_ids())
        )
    ).all()
    matches = [
        city
        for city in cities
        if re.search(r"\b" + re.escape(city.name.lower()) + r"\b", text)
    ]
    if len(matches) != 1:
        return clarify(
            "Which single city are you visiting? Try Dubai or Houston so I can match the location and currency accurately."
        )
    filters["city"] = matches[0].name
    currency = "AED" if country_for(db, matches[0]) == "UAE" else "USD"
    if re.search(r"\b(eur|gbp|mad|sar|cad|aud|euro|euros|pounds|riyals)\b|[€£]", text):
        return clarify(
            f"Please provide your budget in {currency}. Currency conversion is not supported."
        )
    explicit_currency = (
        "AED"
        if re.search(r"\baed\b|dirham", text)
        else "USD"
        if re.search(r"\busd\b|\$|dollar", text)
        else None
    )
    if explicit_currency and explicit_currency != currency:
        return clarify(
            f"This destination is priced in {currency}. Please provide a budget in {currency}; I do not convert currencies."
        )
    filters["currency"] = currency
    budget = re.search(
        r"(under|below|less than|max(?:imum)?|budget(?: of)?|up to)\s*(?:aed|usd|\$)?\s*(\d+(?:\.\d+)?)",
        text,
    )
    if budget:
        if re.search(
            r"per\s+(?:week|month)|total budget|in total|for the (?:trip|week|month)",
            text,
        ):
            return clarify(
                "Please give your daily rental budget. Weekly, monthly and whole-trip rates are separate and cannot be inferred from a daily price."
            )
        filters["max_price"] = float(budget.group(2))
        filters["budget_exclusive"] = budget.group(1) in ("under", "below", "less than")
    duration = re.search(r"(\d+)\s*days?", text)
    if duration:
        filters["duration_days"] = int(duration.group(1))
    for category in (
        "SUV",
        "Convertible",
        "Electric",
        "Supercar",
        "Sports",
        "Economy",
        "Luxury",
    ):
        if category.lower() in text:
            filters["category"] = category
            break
    seats = re.search(r"(\d+)\s*(?:seats?|people|passengers?|adults?)", text)
    if seats:
        filters["seats"] = int(seats.group(1))
    elif "with my wife" in text or "with my husband" in text or "couple" in text:
        filters["seats"] = 2
    if "max_price" in filters and not 0 < filters["max_price"] <= 100000:
        return clarify(
            "Please provide a positive daily budget no greater than 100,000 in the destination currency."
        )
    if "seats" in filters and not 1 <= filters["seats"] <= 20:
        return clarify(
            "How many passengers are travelling? Please choose between 1 and 20."
        )
    if "duration_days" in filters and not 1 <= filters["duration_days"] <= 365:
        return clarify("Please provide a trip duration between 1 and 365 days.")
    from .provider import extract

    provider_result = extract(
        message, [city.name for city in cities], list(db.scalars(select(Category.name)))
    )
    provider_used = provider_result is not None
    # Additional extracted constraints require evidence in the sanitized request.
    # A model cannot change an already recognized hard constraint.
    if provider_result:
        if (
            "max_price" not in filters
            and provider_result.max_price is not None
            and re.search(r"\b(?:budget|under|below|max|maximum)\b", text)
            and re.search(
                r"(?<!\d)" + re.escape(f"{provider_result.max_price:g}") + r"(?!\d)",
                text,
            )
        ):
            filters["max_price"] = provider_result.max_price
            filters["budget_exclusive"] = bool(re.search(r"\b(?:under|below)\b", text))
        if (
            "seats" not in filters
            and provider_result.min_seats
            and re.search(r"\b(?:people|passengers|seats|adults)\b", text)
            and re.search(r"\b" + str(provider_result.min_seats) + r"\b", text)
        ):
            filters["seats"] = provider_result.min_seats
        if (
            "category" not in filters
            and provider_result.category
            and provider_result.category.lower() in text
        ):
            filters["category"] = provider_result.category
    # Deterministic hard constraints remain authoritative. Model output can only
    # contribute an explicitly mentioned occasion; it never selects inventory.
    occasion = (
        provider_result.occasion
        if provider_result
        and provider_result.occasion
        and provider_result.occasion in text
        else None
    )
    if occasion:
        filters["occasion"] = occasion
    query = (
        public_query()
        .join(Location, Listing.location_id == Location.id)
        .where(Location.name == filters["city"], Listing.currency == currency)
    )
    if "category" in filters:
        query = query.where(
            Listing.id.in_(
                select(ListingCategory.listing_id)
                .join(Category, Category.id == ListingCategory.category_id)
                .where(Category.name == filters["category"])
            )
        )
    if "max_price" in filters:
        query = query.where(
            Listing.daily_price < filters["max_price"]
            if filters["budget_exclusive"]
            else Listing.daily_price <= filters["max_price"]
        )
    if "seats" in filters:
        query = query.where(Listing.seats >= filters["seats"])
    # Bound candidates; hard constraints remain SQL predicates. Soft amenities rank
    # within eligible vehicles and never fabricate features or relax constraints.
    rows = db.scalars(query.order_by(Listing.daily_price, Listing.id).limit(100)).all()
    preferences = [
        feature
        for feature in (
            "navigation",
            "bluetooth",
            "leather",
            "panoramic",
            "climate control",
        )
        if feature in text
    ]

    def score(row):
        from .recommendations import OCCASION_CATEGORIES

        category = db.get(Category, row.category_id).name
        return sum(any(p in f.lower() for f in row.features) for p in preferences) + (
            2 if category in OCCASION_CATEGORIES.get(occasion, []) else 0
        )

    rows.sort(key=lambda row: (-score(row), row.daily_price, row.id))
    recommendations = []
    for row in rows[:3]:
        listing = listing_dict(db, row)
        reasons = [
            f"Listed in {listing['city']}",
            f"{currency} {listing['daily_price']:,.0f}/day"
            + (" within your daily budget" if budget else " illustrative daily rate"),
            f"{listing['seats']} seats · {listing['category']}",
        ]
        for preference in preferences:
            if any(preference in f.lower() for f in row.features):
                reasons.append(f"Listed feature: {preference}")
        recommendations.append({"listing": listing, "match_reasons": reasons})
    return {
        "filters": filters,
        "recommendations": recommendations,
        "mode": "provider-assisted" if provider_used else "deterministic",
        "needs_clarification": False,
        "message": (
            f"I found {len(recommendations)} matching vehicles in {filters['city']}. "
            if rows
            else "No approved vehicles match all those constraints. Try another budget or category. "
        )
        + "Location, category, budget and passenger count are matched when recognized. Dates and special requests need supplier confirmation. These illustrative rates do not confirm availability.",
    }


def listing_suggestions(db, message):
    text = normalize(message)
    suggestions = {}
    candidates = list(
        db.execute(
            select(VehicleModel, Brand).join(Brand, VehicleModel.brand_id == Brand.id)
        )
    )
    for model, brand in sorted(candidates, key=lambda pair: -len(pair[0].name)):
        if re.search(r"\b" + re.escape(model.name.lower()) + r"\b", text):
            suggestions.update(brand=brand.name, model=model.name)
            break
    year = re.search(r"\b(20\d{2})\b", text)
    if year and 1990 <= int(year.group(1)) <= 2030:
        suggestions["year"] = int(year.group(1))
    for city in db.scalars(
        select(Location).where(Location.kind == "city", Location.active.is_(True))
    ):
        if city.active and re.search(
            r"\b" + re.escape(city.name.lower()) + r"\b", text
        ):
            from .catalog import country_for

            suggestions.update(city=city.name, country=country_for(db, city))
            break
    price = re.search(r"\b(aed|usd)\s*(\d+(?:\.\d+)?)\s*(?:a|per|/)?\s*day", text)
    if price and 0 < float(price.group(2)) <= 100000:
        suggestions.update(
            currency=price.group(1).upper(), daily_price=float(price.group(2))
        )
    seats = re.search(r"(\d+)\s*seats?", text)
    if seats and 1 <= int(seats.group(1)) <= 20:
        suggestions["seats"] = int(seats.group(1))
    for transmission in ("Automatic", "Manual"):
        if transmission.lower() in text:
            suggestions["transmission"] = transmission
    for category in db.scalars(select(Category)):
        if category.name.lower() in text:
            suggestions["category"] = category.name
            break
    features = [
        f
        for f in (
            "Panoramic roof",
            "Bluetooth",
            "Navigation",
            "Leather interior",
            "Climate control",
        )
        if f.lower() in text
    ]
    if features:
        suggestions["features"] = features
    if "model" in suggestions:
        title = f"{suggestions.get('year', '')} {suggestions['brand']} {suggestions['model']}".strip()
        suggestions["description"] = (
            title
            + (f" in {suggestions['city']}." if "city" in suggestions else ".")
            + (" Listed features: " + ", ".join(features) + "." if features else "")
            + " Contact the supplier to confirm rental terms and availability."
        )
    required = [
        "brand",
        "model",
        "year",
        "city",
        "country",
        "category",
        "currency",
        "daily_price",
        "seats",
        "transmission",
    ]
    return {
        "suggestions": suggestions,
        "missing_fields": [k for k in required if k not in suggestions],
        "warnings": [
            "Review every suggestion. Only explicitly recognized details are filled; no technical specifications are inferred.",
            "Upload actual vehicle photos before submitting for review.",
        ],
        "mode": "deterministic",
    }
