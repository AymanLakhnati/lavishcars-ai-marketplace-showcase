import json
from unittest.mock import patch
import httpx
from app.provider import travel_tokens, extract
from test_marketplace import auth, payload


def test_taxonomy_authorization_cycles_and_brand_consistency(env):
    client, _ = env
    supplier, admin = auth(client), auth(client, "admin@lavish.demo")
    base = "/api/v1/admin/taxonomy/"
    assert (
        client.post(
            base + "brands", json={"name": "New Brand"}, headers=supplier
        ).status_code
        == 403
    )
    brand = client.post(
        base + "brands", json={"name": "New Brand"}, headers=admin
    ).json()
    assert (
        client.post(
            base + "brands", json={"name": "new brand"}, headers=admin
        ).status_code
        == 409
    )
    assert (
        client.post(
            base + "models",
            json={"name": "New Model", "brand_id": 99999},
            headers=admin,
        ).status_code
        == 422
    )
    assert (
        client.post(
            base + "models",
            json={"name": "New Model", "brand_id": brand["id"]},
            headers=admin,
        ).status_code
        == 201
    )
    locations = client.get(base + "locations", headers=admin).json()["items"]
    dubai = next(x for x in locations if x["name"] == "Dubai")
    area = client.post(
        base + "locations",
        json={"name": "Demo area", "kind": "area", "parent_id": dubai["id"]},
        headers=admin,
    ).json()
    assert (
        client.put(
            base + f"locations/{area['id']}",
            json={"name": "Demo area", "kind": "area", "parent_id": area["id"]},
            headers=admin,
        ).status_code
        == 422
    )
    assert (
        client.put(
            base + f"locations/{dubai['id']}",
            json={"name": "Dubai", "kind": "country"},
            headers=admin,
        ).status_code
        == 409
    )
    assert (
        client.post(
            base + "locations",
            json={"name": "No parent", "kind": "city"},
            headers=admin,
        ).status_code
        == 422
    )


def test_admin_edit_audit_and_recommendations(env):
    client, _ = env
    admin = auth(client, "admin@lavish.demo")
    assert (
        client.put(
            "/api/v1/admin/listings/1", json=payload(), headers=admin
        ).status_code
        == 200
    )
    logs = client.get("/api/v1/admin/audit-logs", headers=admin).json()["items"]
    assert any(x["action"] == "listing.edit" for x in logs)
    body = {
        "city": "Dubai",
        "currency": "AED",
        "max_price": 1000,
        "min_seats": 7,
        "occasion": "family",
        "preferred_categories": ["SUV"],
        "features": ["Bluetooth"],
    }
    result = client.post("/api/v1/ai/recommendations", json=body)
    assert result.status_code == 200, result.text
    rows = result.json()["recommendations"]
    assert len(rows) == 1 and rows[0]["score"] == 30
    assert (
        rows[0]["listing"]["seats"] >= 7 and rows[0]["listing"]["daily_price"] <= 1000
    )
    assert (
        client.post(
            "/api/v1/ai/recommendations", json={**body, "currency": "USD"}
        ).status_code
        == 422
    )
    assert not client.post(
        "/api/v1/ai/recommendations", json={**body, "features": ["Nonexistent amenity"]}
    ).json()["recommendations"]
    assert (
        client.post(
            "/api/v1/ai/recommendations", json={**body, "listing_id": 999}
        ).status_code
        == 422
    )


def test_insights_scoped_and_period_prices(env):
    client, _ = env
    supplier = auth(client)
    pending = auth(client, "pending@lavish.demo")
    insight = client.get("/api/v1/ai/marketplace-insights", headers=pending).json()
    assert insight["totals"] == {"listings": 0, "leads": 0}
    assert insight["scope"] == "supplier" and not insight["top_listings"]
    insight = client.get("/api/v1/ai/marketplace-insights", headers=supplier).json()
    assert insight["totals"]["listings"] > 0 and insight["summaries"]
    result = client.get(
        "/api/v1/listings?city=Dubai&period=weekly&max_price=6000&features=Bluetooth"
    ).json()
    assert result["items"] and all(
        x["weekly_price"] <= 6000 and "Bluetooth" in x["features"]
        for x in result["items"]
    )
    assert client.get("/api/v1/listings?city=Dubai&period=yearly").status_code == 422


def test_provider_privacy_validation_and_fallback(env, monkeypatch):
    client, _ = env
    monkeypatch.setenv("AI_API_KEY", "test-secret")
    monkeypatch.setenv("AI_MODEL", "test-model")
    safe = travel_tokens(
        "My name is PersonName email someone@example.com phone +1 555 222 3333 password=DontSendMe Dubai family under AED 900",
        ["Dubai"],
    )
    assert all(
        value not in safe
        for value in (
            "personname",
            "someone",
            "example",
            "555",
            "dontsendme",
            "password",
        )
    )
    with patch("app.provider.ProviderClient") as mocked:
        mocked.return_value.__enter__.return_value.post.side_effect = (
            httpx.ConnectError("offline")
        )
        result = client.post(
            "/api/v1/ai/concierge", json={"message": "Dubai SUV under AED 1000"}
        ).json()
        assert result["mode"] == "deterministic" and len(result["recommendations"]) == 3
    response = httpx.Response(
        200,
        request=httpx.Request("POST", "https://example.com"),
        json={
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {"city": "Dubai", "occasion": "family", "max_price": 99999}
                        )
                    }
                }
            ]
        },
    )
    with patch("app.provider.ProviderClient") as mocked:
        call = mocked.return_value.__enter__.return_value.post
        call.return_value = response
        result = client.post(
            "/api/v1/ai/concierge",
            json={"message": "Dubai family SUV under AED 900 email person@example.com"},
        ).json()
        assert result["mode"] == "provider-assisted"
        assert all(x["listing"]["daily_price"] < 900 for x in result["recommendations"])
        assert "person@example.com" not in str(call.call_args.kwargs["json"])
    response = httpx.Response(
        200,
        request=httpx.Request("POST", "https://example.com"),
        json={
            "choices": [
                {"message": {"content": '{"listing_id":999,"city":"Invented"}'}}
            ]
        },
    )
    with patch("app.provider.ProviderClient") as mocked:
        mocked.return_value.__enter__.return_value.post.return_value = response
        assert extract("Dubai", ["Dubai"], ["SUV"]) is None


def test_durable_database_uploads(env, monkeypatch):
    import io
    from PIL import Image
    from app.main import stored_image

    client, factory = env
    monkeypatch.setattr("app.main.DATABASE_UPLOADS", True)
    data = io.BytesIO()
    Image.new("RGB", (20, 20)).save(data, format="PNG")
    supplier = auth(client)
    result = client.post(
        "/api/v1/supplier/uploads",
        files={"file": ("demo.png", data.getvalue(), "image/png")},
        headers=supplier,
    )
    assert result.status_code == 200
    url = result.json()["url"]
    assert (
        client.post(
            "/api/v1/supplier/listings",
            json={**payload(), "images": [url]},
            headers=supplier,
        ).status_code
        == 201
    )
    with factory() as db:
        response = stored_image(1, url.rsplit("/", 1)[-1], db)
        assert response.media_type == "image/webp" and len(response.body) > 0
    other = auth(client, "houston@lavish.demo")
    assert (
        client.post(
            "/api/v1/supplier/listings",
            json={**payload(), "images": [url]},
            headers=other,
        ).status_code
        == 422
    )
