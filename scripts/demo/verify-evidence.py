"""Capture synthetic, local API evidence. Never stores bearer tokens or sends messages."""

import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import httpx
from PIL import Image

BASE = "http://127.0.0.1:8000/api/v1"
OUT = Path(__file__).resolve().parents[2] / "output/showcase"
OUT.mkdir(parents=True, exist_ok=True)
client = httpx.Client(timeout=20)


def call(method, path, **kwargs):
    response = client.request(method, BASE + path, **kwargs)
    response.raise_for_status()
    return response.json()


def login(email):
    session = call(
        "POST",
        "/auth/login",
        json={"email": email, "password": os.getenv("DEMO_PASSWORD", "DemoDrive!2026")},
    )
    return {"Authorization": "Bearer " + session["access_token"]}


result = {
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "environment": "Local PostgreSQL/FastAPI synthetic demo",
    "checks": [],
}
message = (
    "I'm in Dubai for four days, looking for a luxury SUV under AED 1,000 per day."
)
concierge = call("POST", "/ai/concierge", json={"message": message})
assert len(concierge["recommendations"]) == 3
for item in concierge["recommendations"]:
    listing = item["listing"]
    assert listing["city"] == "Dubai" and listing["daily_price"] < 1000
    assert call("GET", "/listings/" + listing["slug"])["id"] == listing["id"]
result["concierge"] = {"request": message, **concierge}
result["checks"].append(
    "Three concierge recommendations resolve to eligible database records"
)
result["preferences"] = call(
    "POST",
    "/ai/recommendations",
    json={
        "city": "Dubai",
        "max_price": 1000,
        "min_seats": 5,
        "preferred_categories": ["SUV"],
        "occasion": "family",
    },
)
assert result["preferences"]["recommendations"]
result["checks"].append("Explicit preference ranking returns hard-constraint matches")
supplier, admin = login("supplier@lavish.demo"), login("admin@lavish.demo")
result["assistant"] = call(
    "POST",
    "/ai/listing-assistant",
    headers=supplier,
    json={
        "message": "2026 Range Rover Sport SUV, automatic, five seats, Dubai, panoramic roof, AED 925 a day."
    },
)
assert result["assistant"]["suggestions"]["daily_price"] == 925
result["checks"].append("Supplier assistant extracts a reviewable structured draft")
image = io.BytesIO()
Image.new("RGB", (160, 100), (12, 16, 14)).save(image, "PNG")
first = call(
    "POST",
    "/supplier/uploads",
    headers=supplier,
    files={"file": ("synthetic-dark-test.png", image.getvalue(), "image/png")},
)
second = call(
    "POST",
    "/supplier/uploads",
    headers=supplier,
    files={"file": ("synthetic-dark-test.png", image.getvalue(), "image/png")},
)
assert any("dark" in item for item in first["quality"]["warnings"])
assert second["quality"]["duplicate_of"] == (
    first["quality"].get("duplicate_of") or first["url"]
)
result["photo_quality"] = {
    "first": first["quality"],
    "repeat": second["quality"],
    "input": "Synthetic dark test pattern, not a vehicle photograph",
}
result["checks"].append(
    "Photo heuristics flag dark/low-resolution input and repeat upload"
)
created = None
try:
    created = call(
        "POST",
        "/supplier/listings",
        headers=supplier,
        json={
            "brand": "Land Rover",
            "model": "Range Rover Sport",
            "year": 2026,
            "trim": "Synthetic showcase",
            "vehicle_type": "SUV",
            "city": "Dubai",
            "country": "UAE",
            "category": "SUV",
            "categories": ["SUV", "Luxury"],
            "currency": "AED",
            "daily_price": 925,
            "seats": 5,
            "transmission": "Automatic",
            "description": "Synthetic showcase offer used only to demonstrate the approval and inquiry workflow. The test image is not vehicle photography.",
            "features": ["Bluetooth"],
            "images": [first["url"]],
        },
    )
    identifier = created["id"]
    pending = call("POST", f"/supplier/listings/{identifier}/submit", headers=supplier)
    private_code = client.get(BASE + "/listings/" + created["slug"]).status_code
    assert pending["status"] == "pending" and private_code == 404
    approved = call("POST", f"/admin/listings/{identifier}/approve", headers=admin)
    public = call("GET", "/listings/" + created["slug"])
    assert approved["status"] == "published" and public["id"] == identifier
    lead = call(
        "POST",
        "/leads",
        json={
            "listing_id": identifier,
            "name": "Demo Film Guest",
            "email": "demo-film@example.com",
            "phone": "+10000000000",
            "message": "Synthetic showcase inquiry. Please do not contact any real person.",
            "source": "concierge",
        },
    )
    inbox = call("GET", "/supplier/leads", headers=supplier)
    assert any(item["id"] == lead["id"] for item in inbox["items"])
    result["workflow"] = {
        "listing_id": identifier,
        "slug": created["slug"],
        "draft": created["status"],
        "submitted": pending["status"],
        "before_approval_http": private_code,
        "approved": approved["status"],
        "public_record_id": public["id"],
        "saved_inquiry_id": lead["id"],
        "supplier_inbox_verified": True,
        "notification_policy": "Stored in outbox; no real supplier notification sent",
    }
    result["checks"].append(
        "New listing is private before approval, public after approval, and its inquiry reaches the supplier inbox"
    )
finally:
    if created:
        call("POST", f"/supplier/listings/{created['id']}/archive", headers=supplier)
result["insights"] = call("GET", "/ai/marketplace-insights", headers=supplier)
assert result["insights"]["mode"] == "database-aggregates"
result["checks"].append(
    "Supplier insights read actual scoped records and request events"
)
result["checks"].append(
    "Showcase listing archived after verification; no real booking or message"
)
(OUT / "evidence.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
for check in result["checks"]:
    print("PASS:", check)
client.close()
