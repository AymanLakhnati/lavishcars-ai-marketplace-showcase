import io
from PIL import Image
from sqlalchemy import select
from app.models import ListingCategory, ListingImage, SupplierUser, Location
from test_marketplace import auth, payload


def photo(client, supplier):
    output = io.BytesIO()
    Image.new("RGB", (30, 30), "black").save(output, "PNG")
    return client.post(
        "/api/v1/supplier/uploads",
        files={"file": ("demo.png", output.getvalue(), "image/png")},
        headers=supplier,
    )


def test_normalized_listing_categories_images_and_vehicle_detail(env):
    client, factory = env
    supplier, admin = auth(client), auth(client, "admin@lavish.demo")
    image = photo(client, supplier).json()["url"]
    body = {
        **payload(),
        "trim": "HSE",
        "vehicle_type": "SUV",
        "categories": ["SUV", "Luxury"],
        "images": [image],
    }
    created = client.post("/api/v1/supplier/listings", json=body, headers=supplier)
    assert created.status_code == 201, created.text
    listing = created.json()
    assert listing["trim"] == "HSE" and set(listing["categories"]) == {"SUV", "Luxury"}
    with factory() as db:
        assert (
            len(
                db.scalars(
                    select(ListingCategory).where(
                        ListingCategory.listing_id == listing["id"]
                    )
                ).all()
            )
            == 2
        )
        assert (
            db.scalar(
                select(ListingImage).where(ListingImage.listing_id == listing["id"])
            ).url
            == image
        )
    assert (
        client.post(
            f"/api/v1/supplier/listings/{listing['id']}/submit", headers=supplier
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/admin/listings/{listing['id']}/approve", headers=admin
        ).status_code
        == 200
    )
    assert any(
        item["id"] == listing["id"]
        for item in client.get(
            "/api/v1/listings?category=Luxury&vehicle_type=SUV"
        ).json()["items"]
    )


def test_service_areas_and_normalized_team_permissions(env):
    client, factory = env
    supplier = auth(client)
    cities = client.get("/api/v1/locations").json()
    dubai = next(x["id"] for x in cities if x["name"] == "Dubai")
    houston = next(x["id"] for x in cities if x["name"] == "Houston")
    assert (
        client.put(
            "/api/v1/supplier/service-areas",
            json={"location_ids": []},
            headers=supplier,
        ).status_code
        == 409
    )
    assert (
        client.put(
            "/api/v1/supplier/service-areas",
            json={"location_ids": [dubai, houston]},
            headers=supplier,
        ).status_code
        == 200
    )
    teammate = client.post(
        "/api/v1/supplier/team",
        json={"email": "colleague@example.com", "password": "LongDemoPass123"},
        headers=supplier,
    )
    assert teammate.status_code == 201
    colleague = client.post(
        "/api/v1/auth/login",
        json={"email": "colleague@example.com", "password": "LongDemoPass123"},
    ).json()
    headers = {"Authorization": "Bearer " + colleague["access_token"]}
    assert client.get("/api/v1/supplier/listings", headers=headers).json()["total"] > 0
    assert client.get("/api/v1/admin/leads", headers=headers).status_code == 403
    assert (
        client.post(
            "/api/v1/supplier/team",
            json={"email": "extra@example.com", "password": "LongDemoPass123"},
            headers=headers,
        ).status_code
        == 403
    )
    with factory() as db:
        assert (
            db.get(SupplierUser, (1, colleague["user"]["id"])).membership_role
            == "member"
        )


def test_image_quality_duplicate_and_measured_views(env):
    client, _ = env
    supplier = auth(client)
    first, second = photo(client, supplier).json(), photo(client, supplier).json()
    assert first["quality"]["brightness"] == 0
    assert any("dark" in item for item in first["quality"]["warnings"])
    assert second["quality"]["duplicate_of"] == first["url"]
    assert 0 <= first["quality"]["cover_candidate_score"] <= 100
    listing = client.get("/api/v1/listings").json()["items"][0]
    client.get("/api/v1/listings/" + listing["slug"])
    insights = client.get("/api/v1/ai/marketplace-insights", headers=supplier).json()
    assert insights["most_viewed"][0]["detail_requests"] == 1
    assert "not unique visitors" in insights["view_definition"]


def test_disabled_parent_market_blocks_all_public_discovery_and_inquiries(env):
    client, factory = env
    listing = client.get("/api/v1/listings?city=Dubai").json()["items"][0]
    with factory() as db:
        country = db.scalar(select(Location).where(Location.name == "UAE"))
        country.active = False
        db.commit()
    assert client.get("/api/v1/listings?city=Dubai").json()["total"] == 0
    assert client.get("/api/v1/listings/" + listing["slug"]).status_code == 404
    result = client.post(
        "/api/v1/ai/concierge", json={"message": "SUV in Dubai under AED 1000"}
    ).json()
    assert not result["recommendations"]
    assert (
        client.post("/api/v1/ai/recommendations", json={"city": "Dubai"}).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/leads",
            json={
                "listing_id": listing["id"],
                "name": "Demo Reviewer",
                "email": "reviewer@example.com",
                "phone": "+971500000000",
                "message": "Synthetic inquiry",
            },
        ).status_code
        == 404
    )


def test_concierge_clarifies_invalid_numeric_constraints(env):
    client, _ = env
    for message in (
        "Dubai SUV under AED 0",
        "Dubai for 0 passengers",
        "Dubai for 400 days",
    ):
        result = client.post("/api/v1/ai/concierge", json={"message": message}).json()
        assert result["needs_clarification"] and not result["recommendations"]
