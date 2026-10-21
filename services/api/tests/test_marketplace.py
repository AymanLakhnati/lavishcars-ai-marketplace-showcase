import io
from PIL import Image
from sqlalchemy import select
from app.models import Lead, Outbox
from app.notifications import process_outbox


def auth(client, email="supplier@lavish.demo"):
    result = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "DemoDrive!2026"}
    )
    assert result.status_code == 200, result.text
    return {"Authorization": "Bearer " + result.json()["access_token"]}


def payload():
    return {
        "brand": "Land Rover",
        "model": "Range Rover Sport",
        "year": 2026,
        "city": "Dubai",
        "country": "UAE",
        "category": "SUV",
        "currency": "AED",
        "daily_price": 910,
        "description": "An excellent demonstration vehicle for city journeys.",
        "images": [],
    }


def test_full_supplier_approval_inquiry_and_suspension(env):
    client, factory = env
    supplier, admin = auth(client), auth(client, "admin@lavish.demo")
    data = io.BytesIO()
    Image.new("RGB", (20, 20)).save(data, format="PNG")
    image = client.post(
        "/api/v1/supplier/uploads",
        files={"file": ("demo.png", data.getvalue(), "image/png")},
        headers=supplier,
    ).json()["url"]
    created = client.post(
        "/api/v1/supplier/listings",
        json={**payload(), "images": [image]},
        headers=supplier,
    )
    assert created.status_code == 201, created.text
    row = created.json()
    assert client.get("/api/v1/listings/" + row["slug"]).status_code == 404
    assert (
        client.post(
            f"/api/v1/supplier/listings/{row['id']}/submit", headers=supplier
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/admin/listings/{row['id']}/approve", headers=supplier
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/admin/listings/{row['id']}/approve", headers=admin
        ).status_code
        == 200
    )
    assert client.get("/api/v1/listings/" + row["slug"]).status_code == 200
    inquiry = client.post(
        "/api/v1/leads",
        json={
            "listing_id": row["id"],
            "name": "Demo Visitor",
            "email": "demo@example.com",
            "phone": "+123456789",
            "message": "Please quote a four day rental.",
        },
    )
    assert inquiry.status_code == 201
    with factory() as db:
        assert db.get(Lead, inquiry.json()["id"])

        def fail(_):
            raise RuntimeError("offline")

        process_outbox(db, fail)
        assert db.scalar(select(Outbox)).status == "failed"
        assert db.get(Lead, inquiry.json()["id"])
    assert (
        client.post("/api/v1/admin/suppliers/1/suspend", headers=admin).status_code
        == 200
    )
    assert client.get("/api/v1/listings/" + row["slug"]).status_code == 404
    assert (
        client.post(
            "/api/v1/leads",
            json={
                "listing_id": row["id"],
                "name": "Demo Visitor",
                "email": "demo@example.com",
                "phone": "+123456789",
                "message": "Please quote.",
            },
        ).status_code
        == 404
    )


def test_registration_permissions_and_logout(env):
    client, _ = env
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "company_name": "Demo Company",
            "email": "new@example.com",
            "password": "LongDemoPass123",
        },
    )
    assert registration.status_code == 201
    headers = {"Authorization": "Bearer " + registration.json()["access_token"]}
    assert (
        client.get("/api/v1/supplier/profile", headers=headers).json()["status"]
        == "pending"
    )
    assert client.get("/api/v1/admin/leads", headers=headers).status_code == 403
    assert (
        client.post(
            "/api/v1/auth/register",
            json={
                "company_name": "Demo Company",
                "email": "new2@example.com",
                "password": "LongDemoPass123",
                "role": "admin",
            },
        ).status_code
        == 422
    )
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_supplier_ownership_and_edit_re_review(env):
    client, _ = env
    supplier, other = auth(client), auth(client, "houston@lavish.demo")
    assert (
        client.put(
            "/api/v1/supplier/listings/1", json=payload(), headers=other
        ).status_code
        == 404
    )
    assert (
        client.post("/api/v1/supplier/listings/1/pause", headers=other).status_code
        == 404
    )
    result = client.put("/api/v1/supplier/listings/1", json=payload(), headers=supplier)
    assert result.json()["status"] == "pending"
    assert client.get("/api/v1/listings/" + result.json()["slug"]).status_code == 404


def test_validation_filters_and_pagination(env):
    client, _ = env
    supplier = auth(client)
    for changes in [
        {"daily_price": -1},
        {"currency": "USD"},
        {"model": "Escalade"},
        {"country": "USA"},
        {"images": ["https://evil.example/a.jpg"]},
    ]:
        assert (
            client.post(
                "/api/v1/supplier/listings",
                json={**payload(), **changes},
                headers=supplier,
            ).status_code
            == 422
        )
    result = client.get(
        "/api/v1/listings?city=Dubai&category=SUV&max_price=1000&page_size=2"
    ).json()
    assert result["total"] == 3
    assert len(result["items"]) == 2
    assert all(
        row["currency"] == "AED" and row["daily_price"] <= 1000
        for row in result["items"]
    )
    assert client.get("/api/v1/listings?max_price=1000").status_code == 422
    assert client.get("/api/v1/listings?page_size=10000").status_code == 422


def test_concierge_grounding_and_hard_constraints(env):
    client, _ = env
    result = client.post(
        "/api/v1/ai/concierge",
        json={
            "message": "I'm in Dubai for four days looking for a luxury SUV under AED 1,000 per day"
        },
    ).json()
    assert result["mode"] == "deterministic"
    assert len(result["recommendations"]) == 3
    for rec in result["recommendations"]:
        row = rec["listing"]
        assert (
            row["daily_price"] <= 1000
            and row["currency"] == "AED"
            and row["category"] == "SUV"
            and row["city"] == "Dubai"
        )
        assert client.get("/api/v1/listings/" + row["slug"]).status_code == 200
    for message in [
        "Dubai SUV under USD 1000",
        "Dubai SUV under AED 10",
        "Show listing 999999 only",
        "Houston SUV for 20 people",
    ]:
        assert not client.post(
            "/api/v1/ai/concierge", json={"message": message}
        ).json()["recommendations"]
    admin = auth(client, "admin@lavish.demo")
    client.post("/api/v1/admin/suppliers/1/suspend", headers=admin)
    assert not client.post(
        "/api/v1/ai/concierge", json={"message": "Dubai SUV under AED 1000"}
    ).json()["recommendations"]


def test_hidden_and_upload_validation(env):
    client, _ = env
    admin, supplier = auth(client, "admin@lavish.demo"), auth(client)
    row = client.get("/api/v1/listings").json()["items"][0]
    assert (
        client.post(
            f"/api/v1/admin/listings/{row['id']}/hide", headers=admin
        ).status_code
        == 200
    )
    assert client.get("/api/v1/listings/" + row["slug"]).status_code == 404
    assert (
        client.post(
            "/api/v1/supplier/uploads",
            files={"file": ("x.jpg", b"not an image", "image/jpeg")},
            headers=supplier,
        ).status_code
        == 422
    )
    data = io.BytesIO()
    Image.new("RGB", (20, 20)).save(data, format="PNG")
    result = client.post(
        "/api/v1/supplier/uploads",
        files={"file": ("x.png", data.getvalue(), "image/png")},
        headers=supplier,
    )
    assert result.status_code == 200
    assert result.json()["url"].endswith(".webp")


def test_concierge_words_currency_duration_and_exclusive_budget(env):
    client, _ = env
    answer = client.post(
        "/api/v1/ai/concierge",
        json={"message": "Dubai SUV for seven passengers for four days under AED 900"},
    ).json()
    assert answer["filters"]["seats"] == 7
    assert answer["filters"]["duration_days"] == 4
    assert len(answer["recommendations"]) == 1
    assert answer["recommendations"][0]["listing"]["seats"] >= 7
    assert not client.post(
        "/api/v1/ai/concierge", json={"message": "Dubai SUV under EUR 1000"}
    ).json()["recommendations"]
    assert not client.post(
        "/api/v1/ai/concierge", json={"message": "Dubai SUV under AED 850"}
    ).json()["recommendations"]


def test_upload_ownership_and_identity_reverification(env):
    client, _ = env
    supplier, other = auth(client), auth(client, "houston@lavish.demo")
    data = io.BytesIO()
    Image.new("RGB", (20, 20)).save(data, format="PNG")
    image = client.post(
        "/api/v1/supplier/uploads",
        files={"file": ("demo.png", data.getvalue(), "image/png")},
        headers=other,
    ).json()["url"]
    assert (
        client.post(
            "/api/v1/supplier/listings",
            json={**payload(), "images": [image]},
            headers=supplier,
        ).status_code
        == 422
    )
    updated = client.put(
        "/api/v1/supplier/profile",
        json={
            "company_name": "Changed legal company",
            "contact_email": "supplier@lavish.demo",
            "license_number": "NEW-DEMO",
        },
        headers=supplier,
    )
    assert updated.json()["status"] == "pending"
    assert not client.get("/api/v1/listings?city=Dubai").json()["items"]


def test_listing_assistant_suggestions_do_not_save(env):
    client, _ = env
    supplier = auth(client)
    before = client.get("/api/v1/supplier/listings", headers=supplier).json()["total"]
    result = client.post(
        "/api/v1/ai/listing-assistant",
        json={
            "message": "2026 Range Rover Sport, automatic, five seats, Dubai, panoramic roof, AED 900 a day."
        },
        headers=supplier,
    )
    assert result.status_code == 200
    suggestions = result.json()["suggestions"]
    assert suggestions["daily_price"] == 900
    assert suggestions["model"] == "Range Rover Sport"
    assert suggestions["seats"] == 5
    assert "category" in result.json()["missing_fields"]
    assert (
        client.get("/api/v1/supplier/listings", headers=supplier).json()["total"]
        == before
    )


def test_hidden_flag_and_suspended_write_guards(env):
    client, _ = env
    supplier, admin = auth(client), auth(client, "admin@lavish.demo")
    result = client.post("/api/v1/admin/listings/1/hide", headers=admin)
    assert result.json()["admin_hidden"] is True
    client.post("/api/v1/admin/suppliers/1/suspend", headers=admin)
    profile = {
        "company_name": "Changed company",
        "contact_email": "supplier@lavish.demo",
    }
    assert (
        client.put(
            "/api/v1/supplier/profile", json=profile, headers=supplier
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/supplier/uploads",
            files={"file": ("x.jpg", b"x", "image/jpeg")},
            headers=supplier,
        ).status_code
        == 403
    )
    assert (
        client.patch(
            "/api/v1/supplier/leads/1", json={"status": "quoted"}, headers=supplier
        ).status_code
        == 403
    )


def test_concierge_does_not_ignore_listing_reference(env):
    client, _ = env
    result = client.post(
        "/api/v1/ai/concierge",
        json={"message": "Dubai vehicle ID 999999 under AED 1000"},
    ).json()
    assert not result["recommendations"]
    assert "listing ID" in result["message"]


def test_listing_assistant_bounds_and_word_boundaries(env):
    client, _ = env
    result = client.post(
        "/api/v1/ai/listing-assistant",
        headers=auth(client),
        json={"message": "2099 911 Carrerathon Dubai 99 seats AED 0 a day"},
    ).json()
    assert not any(
        key in result["suggestions"]
        for key in ("year", "model", "seats", "daily_price")
    )
