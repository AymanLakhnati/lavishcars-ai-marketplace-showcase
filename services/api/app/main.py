import io
import hashlib
import json
import os
import re
import secrets
import time
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from sqlalchemy import func, select, cast, String, delete
from sqlalchemy.exc import IntegrityError

from . import schemas as s
from .catalog import listing_dict, page, public_query, record_dict, resolve_listing
from .concierge import recommend
from .taxonomy import router as taxonomy_router
from typing import Literal
from .db import get_db
from .models import (
    Upload,
    Audit,
    Brand,
    Category,
    Lead,
    Listing,
    Location,
    Outbox,
    Session,
    Supplier,
    User,
    VehicleModel,
    SupplierUser,
    SupplierLocation,
    ListingCategory,
    ListingView,
)
from .relationships import sync_listing
from .image_quality import inspect_image
from .security import (
    admin_user,
    bearer,
    current_user,
    hash_password,
    issue_token,
    supplier_user,
    token_hash,
    user_dict,
    verify_password,
)

app = FastAPI(title="LavishCars concept marketplace", version="1.0.0")
app.include_router(taxonomy_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(","),
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
uploads = Path(os.getenv("UPLOAD_DIR", "./uploads"))
DATABASE_UPLOADS = os.getenv("UPLOAD_STORAGE") == "database" or bool(
    os.getenv("VERCEL")
)
if not DATABASE_UPLOADS:
    uploads.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads), name="uploads")
prefix = "/api/v1"
requests_by_client = defaultdict(deque)
rate_lock = Lock()


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.method == "POST" and request.url.path in (
        prefix + "/auth/login",
        prefix + "/auth/register",
        prefix + "/leads",
        prefix + "/ai/concierge",
        prefix + "/ai/recommendations",
        prefix + "/ai/listing-assistant",
    ):
        key = (request.client.host if request.client else "unknown", request.url.path)
        timestamp = time.monotonic()
        with rate_lock:
            if len(requests_by_client) > 10000:
                requests_by_client.clear()
            bucket = requests_by_client[key]
            while bucket and timestamp - bucket[0] > 60:
                bucket.popleft()
            if len(bucket) >= 30:
                return JSONResponse(
                    {"detail": "Too many requests. Try again shortly."},
                    status_code=429,
                    headers={"Retry-After": "60"},
                )
            bucket.append(timestamp)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/health")
def health():
    return {"status": "ok", "concept": True}


@app.post(prefix + "/auth/register", status_code=201)
def register(body: s.Register, db=Depends(get_db)):
    email = str(body.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    supplier = Supplier(company_name=body.company_name, contact_email=email)
    db.add(supplier)
    db.flush()
    user = User(
        email=email, password_hash=hash_password(body.password), supplier_id=supplier.id
    )
    db.add(user)
    db.flush()
    db.add(
        SupplierUser(supplier_id=supplier.id, user_id=user.id, membership_role="owner")
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered")
    return issue_token(db, user)


@app.post(prefix + "/auth/login")
def login(body: s.Login, db=Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(body.email).lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return issue_token(db, user)


@app.get(prefix + "/auth/me")
def me(user=Depends(current_user)):
    return user_dict(user)


@app.post(prefix + "/auth/logout")
def logout(user=Depends(current_user), credentials=Depends(bearer), db=Depends(get_db)):
    session = db.scalar(
        select(Session).where(Session.token_hash == token_hash(credentials.credentials))
    )
    db.delete(session)
    db.commit()
    return {"message": "Signed out"}


@app.get(prefix + "/locations")
def locations(db=Depends(get_db)):
    return [
        record_dict(item) for item in db.scalars(select(Location).order_by(Location.id))
    ]


@app.get(prefix + "/brands")
def brands(db=Depends(get_db)):
    return [
        record_dict(item) for item in db.scalars(select(Brand).order_by(Brand.name))
    ]


@app.get(prefix + "/models")
def models(brand_id: int | None = None, db=Depends(get_db)):
    query = select(VehicleModel)
    if brand_id:
        query = query.where(VehicleModel.brand_id == brand_id)
    return [record_dict(item) for item in db.scalars(query)]


@app.get(prefix + "/categories")
def categories(db=Depends(get_db)):
    return [
        record_dict(item)
        for item in db.scalars(select(Category).order_by(Category.name))
    ]


@app.get(prefix + "/listings")
def listings(
    city: str | None = None,
    country: str | None = None,
    brand: str | None = None,
    model: str | None = None,
    category: str | None = None,
    currency: str | None = None,
    q: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    seats: int | None = Query(None, ge=1),
    transmission: str | None = None,
    vehicle_type: str | None = None,
    sort: str = "recommended",
    period: Literal["daily", "weekly", "monthly"] = "daily",
    features: str | None = Query(None, max_length=500),
    page_number: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(24, ge=1, le=100),
    db=Depends(get_db),
):
    query = (
        public_query()
        .join(Location, Listing.location_id == Location.id)
        .join(VehicleModel)
        .join(Brand)
        .join(Category)
    )
    for column, value in (
        (Location.name, city),
        (Brand.name, brand),
        (VehicleModel.name, model),
        (Listing.currency, currency),
        (Listing.transmission, transmission),
        (Listing.vehicle_type, vehicle_type),
    ):
        if value:
            query = query.where(func.lower(column) == value.lower())
    if category:
        query = query.where(
            Listing.id.in_(
                select(ListingCategory.listing_id)
                .join(Category, Category.id == ListingCategory.category_id)
                .where(func.lower(Category.name) == category.lower())
            )
        )
    if country:
        from .catalog import country_for

        ids = [
            loc.id
            for loc in db.scalars(select(Location).where(Location.kind == "city"))
            if country_for(db, loc).lower() == country.lower()
        ]
        query = query.where(Listing.location_id.in_(ids))
    if q:
        query = query.where(
            (Brand.name + " " + VehicleModel.name).ilike("%" + q[:100] + "%")
        )
    if (min_price is not None or max_price is not None) and not (currency or city):
        raise HTTPException(422, "Select a currency or city when filtering prices")
    price_column = getattr(Listing, period + "_price")
    query = query.where(price_column.is_not(None))
    if features:
        for feature in [x.strip() for x in features.split(",") if x.strip()]:
            query = query.where(
                cast(Listing.features, String).contains(
                    json.dumps(feature), autoescape=True
                )
            )
    if min_price is not None:
        query = query.where(price_column >= min_price)
    if max_price is not None:
        query = query.where(price_column <= max_price)
    if seats:
        query = query.where(Listing.seats >= seats)
    orders = {
        "price_asc": (Listing.currency, price_column),
        "price_desc": (Listing.currency, price_column.desc()),
        "year": (Listing.year.desc(),),
        "year_desc": (Listing.year.desc(),),
        "recommended": (Listing.id,),
    }
    if sort not in orders:
        raise HTTPException(422, "Unsupported sort")
    return page(
        db,
        query.order_by(*orders[sort]),
        lambda item: listing_dict(db, item),
        page_number,
        page_size,
    )


@app.get(prefix + "/listings/{slug}")
def detail(slug: str, db=Depends(get_db)):
    listing = db.scalar(public_query().where(Listing.slug == slug))
    if not listing:
        raise HTTPException(404, "Listing not found")
    db.add(ListingView(listing_id=listing.id))
    db.commit()
    return listing_dict(db, listing)


@app.post(prefix + "/leads", status_code=201)
def create_lead(body: s.LeadInput, db=Depends(get_db)):
    listing = db.scalar(public_query().where(Listing.id == body.listing_id))
    if not listing:
        raise HTTPException(404, "Listing not available for inquiry")
    lead = Lead(
        **body.model_dump(),
        supplier_id=listing.supplier_id,
        location_id=listing.location_id,
    )
    db.add(lead)
    db.flush()
    db.add(Outbox(lead_id=lead.id))
    db.commit()
    return {
        "id": lead.id,
        "status": lead.status,
        "message": "Inquiry saved. The supplier must confirm price and availability.",
    }


@app.get(prefix + "/supplier/profile")
def supplier_profile(user=Depends(supplier_user), db=Depends(get_db)):
    return record_dict(db.get(Supplier, user.supplier_id))


@app.get(prefix + "/supplier/service-areas")
def service_areas(user=Depends(supplier_user), db=Depends(get_db)):
    return {
        "location_ids": list(
            db.scalars(
                select(SupplierLocation.location_id).where(
                    SupplierLocation.supplier_id == user.supplier_id
                )
            )
        )
    }


@app.put(prefix + "/supplier/service-areas")
def update_service_areas(
    body: s.ServiceAreas, user=Depends(supplier_user), db=Depends(get_db)
):
    if db.get(Supplier, user.supplier_id).status == "suspended":
        raise HTTPException(403, "Supplier account suspended")
    selected = set(body.location_ids)
    valid = set(
        db.scalars(
            select(Location.id).where(
                Location.id.in_(selected),
                Location.kind == "city",
                Location.active.is_(True),
            )
        )
    )
    if valid != selected:
        raise HTTPException(422, "Select active rental cities")
    published = set(
        db.scalars(
            select(Listing.location_id).where(
                Listing.supplier_id == user.supplier_id, Listing.status == "published"
            )
        )
    )
    if not published.issubset(selected):
        raise HTTPException(
            409, "Pause published listings before removing their service city"
        )
    db.execute(
        delete(SupplierLocation).where(SupplierLocation.supplier_id == user.supplier_id)
    )
    db.add_all(
        SupplierLocation(supplier_id=user.supplier_id, location_id=i) for i in selected
    )
    db.commit()
    return {"location_ids": sorted(selected)}


@app.get(prefix + "/supplier/team")
def supplier_team(user=Depends(supplier_user), db=Depends(get_db)):
    rows = db.execute(
        select(User, SupplierUser)
        .join(SupplierUser, SupplierUser.user_id == User.id)
        .where(SupplierUser.supplier_id == user.supplier_id)
    ).all()
    return {
        "items": [
            {"id": u.id, "email": u.email, "role": membership.membership_role}
            for u, membership in rows
        ]
    }


@app.post(prefix + "/supplier/team", status_code=201)
def add_teammate(body: s.Teammate, user=Depends(supplier_user), db=Depends(get_db)):
    membership = db.get(SupplierUser, (user.supplier_id, user.id))
    if (
        membership.membership_role != "owner"
        or db.get(Supplier, user.supplier_id).status == "suspended"
    ):
        raise HTTPException(403, "An active supplier owner is required")
    if db.scalar(select(User.id).where(User.email == str(body.email).lower())):
        raise HTTPException(409, "This email already belongs to an account")
    teammate = User(
        email=str(body.email).lower(),
        password_hash=hash_password(body.password),
        supplier_id=user.supplier_id,
    )
    db.add(teammate)
    db.flush()
    db.add(
        SupplierUser(
            supplier_id=user.supplier_id, user_id=teammate.id, membership_role="member"
        )
    )
    db.add(
        Audit(
            user_id=user.id,
            action="supplier.team.add",
            entity_id=teammate.id,
            reason="Owner added an authorized colleague",
        )
    )
    db.commit()
    return {"id": teammate.id, "email": teammate.email, "role": "member"}


@app.put(prefix + "/supplier/profile")
def update_profile(body: s.Profile, user=Depends(supplier_user), db=Depends(get_db)):
    supplier = db.get(Supplier, user.supplier_id)
    if supplier.status == "suspended":
        raise HTTPException(403, "Supplier account suspended")
    if supplier.status == "approved" and (
        supplier.company_name != body.company_name
        or supplier.license_number != body.license_number
    ):
        supplier.status = "pending"
    for key, value in body.model_dump().items():
        setattr(supplier, key, value)
    db.commit()
    return record_dict(supplier)


def validate_images(images, supplier_id, db):
    for url in images:
        if not re.fullmatch(
            r"/uploads/" + str(supplier_id) + r"/[a-f0-9]{40}\.webp", url
        ) or not (
            db.scalar(
                select(Upload.id).where(
                    Upload.supplier_id == supplier_id,
                    Upload.name == url.rsplit("/", 1)[-1],
                )
            )
            if DATABASE_UPLOADS
            else (uploads / str(supplier_id) / url.rsplit("/", 1)[-1]).is_file()
        ):
            raise HTTPException(422, "Use images uploaded by your supplier account")


def owned_listing(db, user, listing_id):
    listing = db.scalar(
        select(Listing).where(
            Listing.id == listing_id, Listing.supplier_id == user.supplier_id
        )
    )
    if not listing:
        raise HTTPException(404, "Listing not found")
    if db.get(Supplier, user.supplier_id).status == "suspended":
        raise HTTPException(403, "Supplier account suspended")
    return listing


@app.get(prefix + "/supplier/listings")
def supplier_listings(
    page_number: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(24, ge=1, le=100),
    user=Depends(supplier_user),
    db=Depends(get_db),
):
    return page(
        db,
        select(Listing)
        .where(Listing.supplier_id == user.supplier_id)
        .order_by(Listing.id.desc()),
        lambda item: listing_dict(db, item),
        page_number,
        page_size,
    )


@app.post(prefix + "/supplier/listings", status_code=201)
def create_listing(
    body: s.ListingInput, user=Depends(supplier_user), db=Depends(get_db)
):
    if db.get(Supplier, user.supplier_id).status == "suspended":
        raise HTTPException(403, "Supplier account suspended")
    validate_images(body.images, user.supplier_id, db)
    values = resolve_listing(db, body)
    slug = (
        re.sub(
            r"[^a-z0-9]+", "-", f"{body.brand}-{body.model}-{body.city}".lower()
        ).strip("-")
        + "-"
        + secrets.token_hex(4)
    )
    listing = Listing(**values, supplier_id=user.supplier_id, slug=slug)
    db.add(listing)
    db.flush()
    sync_listing(db, listing, body)
    db.commit()
    return listing_dict(db, listing)


@app.put(prefix + "/supplier/listings/{listing_id}")
def edit_listing(
    listing_id: int,
    body: s.ListingInput,
    user=Depends(supplier_user),
    db=Depends(get_db),
):
    listing = owned_listing(db, user, listing_id)
    if listing.status == "archived":
        raise HTTPException(409, "Archived listings cannot be edited")
    validate_images(body.images, user.supplier_id, db)
    for key, value in resolve_listing(db, body).items():
        setattr(listing, key, value)
    sync_listing(db, listing, body)
    if listing.status in ("published", "pending"):
        listing.status = "pending"
    db.commit()
    return listing_dict(db, listing)


@app.post(prefix + "/supplier/listings/{listing_id}/{action}")
def listing_action(
    listing_id: int, action: str, user=Depends(supplier_user), db=Depends(get_db)
):
    listing = owned_listing(db, user, listing_id)
    transitions = {
        "submit": (("draft", "rejected", "paused"), "pending"),
        "pause": (("published",), "paused"),
        "archive": (
            ("draft", "pending", "published", "rejected", "paused"),
            "archived",
        ),
    }
    if action not in transitions:
        raise HTTPException(404, "Unknown action")
    allowed, destination = transitions[action]
    if listing.status not in allowed:
        raise HTTPException(409, "Invalid listing state transition")
    if action == "submit" and (not listing.images or len(listing.description) < 20):
        raise HTTPException(
            422, "Add a photo and a description of at least 20 characters before review"
        )
    listing.status = destination
    listing.rejection_reason = ""
    db.commit()
    return listing_dict(db, listing)


@app.post(prefix + "/supplier/uploads")
async def upload(
    file: UploadFile = File(...), user=Depends(supplier_user), db=Depends(get_db)
):
    if db.get(Supplier, user.supplier_id).status == "suspended":
        raise HTTPException(403, "Supplier account suspended")
    data = await file.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(413, "Maximum image size is 8 MB")
    try:
        Image.MAX_IMAGE_PIXELS = 25_000_000
        image = Image.open(io.BytesIO(data))
        if image.format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError()
        image.load()
        quality = inspect_image(image)
        image.thumbnail((2400, 1600))
        name = secrets.token_hex(20) + ".webp"
        output = io.BytesIO()
        image.convert("RGB").save(output, "WEBP", quality=85)
        digest = hashlib.sha256(output.getvalue()).hexdigest()
        duplicate = db.scalar(
            select(Upload.name)
            .where(
                Upload.supplier_id == user.supplier_id, Upload.content_hash == digest
            )
            .limit(1)
        )
        if duplicate:
            quality["warnings"].append(
                "Exact duplicate of an image already uploaded by your supplier account."
            )
            quality["duplicate_of"] = f"/uploads/{user.supplier_id}/{duplicate}"
        if DATABASE_UPLOADS:
            db.add(
                Upload(
                    supplier_id=user.supplier_id,
                    name=name,
                    data=output.getvalue(),
                    content_hash=digest,
                )
            )
            db.commit()
        else:
            folder = uploads / str(user.supplier_id)
            folder.mkdir(exist_ok=True)
            (folder / name).write_bytes(output.getvalue())
            db.add(
                Upload(
                    supplier_id=user.supplier_id,
                    name=name,
                    data=output.getvalue(),
                    content_hash=digest,
                )
            )
            db.commit()
    except (UnidentifiedImageError, ValueError, OSError, Image.DecompressionBombError):
        raise HTTPException(422, "Upload a valid JPG, PNG or WebP image")
    return {"url": f"/uploads/{user.supplier_id}/" + name, "quality": quality}


def lead_dict(db, lead):
    return {
        **record_dict(lead),
        "listing_title": listing_dict(db, db.get(Listing, lead.listing_id))["title"],
    }


@app.get(prefix + "/supplier/leads")
def supplier_leads(
    page_number: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(24, ge=1, le=100),
    user=Depends(supplier_user),
    db=Depends(get_db),
):
    return page(
        db,
        select(Lead)
        .where(Lead.supplier_id == user.supplier_id)
        .order_by(Lead.id.desc()),
        lambda item: lead_dict(db, item),
        page_number,
        page_size,
    )


@app.patch(prefix + "/supplier/leads/{lead_id}")
def change_supplier_lead(
    lead_id: int, body: s.LeadStatus, user=Depends(supplier_user), db=Depends(get_db)
):
    if db.get(Supplier, user.supplier_id).status == "suspended":
        raise HTTPException(403, "Supplier account suspended")
    lead = db.scalar(
        select(Lead).where(Lead.id == lead_id, Lead.supplier_id == user.supplier_id)
    )
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.status = body.status
    db.commit()
    return lead_dict(db, lead)


@app.get(prefix + "/admin/suppliers")
def admin_suppliers(
    page_number: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(24, ge=1, le=100),
    user=Depends(admin_user),
    db=Depends(get_db),
):
    return page(
        db, select(Supplier).order_by(Supplier.id), record_dict, page_number, page_size
    )


@app.post(prefix + "/admin/suppliers/{supplier_id}/{action}")
def moderate_supplier(
    supplier_id: int,
    action: str,
    body: s.Decision = s.Decision(),
    user=Depends(admin_user),
    db=Depends(get_db),
):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(404, "Supplier not found")
    transitions = {"approve": "approved", "reject": "rejected", "suspend": "suspended"}
    if action not in transitions:
        raise HTTPException(404, "Unknown action")
    if action == "reject" and not body.reason:
        raise HTTPException(422, "A rejection reason is required")
    supplier.status = transitions[action]
    supplier.active = action != "suspend"
    supplier.rejection_reason = body.reason
    db.add(
        Audit(
            user_id=user.id,
            action="supplier." + action,
            entity_id=supplier.id,
            reason=body.reason,
        )
    )
    db.commit()
    return record_dict(supplier)


@app.get(prefix + "/admin/listings")
def admin_listings(
    page_number: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(24, ge=1, le=100),
    user=Depends(admin_user),
    db=Depends(get_db),
):
    return page(
        db,
        select(Listing).order_by(Listing.id.desc()),
        lambda item: listing_dict(db, item),
        page_number,
        page_size,
    )


@app.post(prefix + "/admin/listings/{listing_id}/{action}")
def moderate_listing(
    listing_id: int,
    action: str,
    body: s.Decision = s.Decision(),
    user=Depends(admin_user),
    db=Depends(get_db),
):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if action not in ("approve", "reject", "pause", "hide", "unhide"):
        raise HTTPException(404, "Unknown action")
    if action in ("approve", "reject") and listing.status != "pending":
        raise HTTPException(409, "Only pending listings can be approved or rejected")
    if (
        action == "approve"
        and db.get(Supplier, listing.supplier_id).status != "approved"
    ):
        raise HTTPException(409, "Approve the supplier first")
    if action == "reject" and not body.reason:
        raise HTTPException(422, "A rejection reason is required")
    if action in ("hide", "unhide"):
        listing.admin_hidden = action == "hide"
    else:
        listing.status = {
            "approve": "published",
            "reject": "rejected",
            "pause": "paused",
        }[action]
    listing.rejection_reason = body.reason
    db.add(
        Audit(
            user_id=user.id,
            action="listing." + action,
            entity_id=listing.id,
            reason=body.reason,
        )
    )
    db.commit()
    return listing_dict(db, listing)


@app.get(prefix + "/admin/leads")
def admin_leads(
    page_number: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(24, ge=1, le=100),
    user=Depends(admin_user),
    db=Depends(get_db),
):
    return page(
        db,
        select(Lead).order_by(Lead.id.desc()),
        lambda item: lead_dict(db, item),
        page_number,
        page_size,
    )


@app.patch(prefix + "/admin/leads/{lead_id}")
def change_admin_lead(
    lead_id: int, body: s.LeadStatus, user=Depends(admin_user), db=Depends(get_db)
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.status = body.status
    db.commit()
    return lead_dict(db, lead)


@app.get(prefix + "/admin/audit-logs")
def audit_logs(
    page_number: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(24, ge=1, le=100),
    user=Depends(admin_user),
    db=Depends(get_db),
):
    return page(
        db, select(Audit).order_by(Audit.id.desc()), record_dict, page_number, page_size
    )


@app.post(prefix + "/ai/concierge")
def concierge(body: s.Concierge, db=Depends(get_db)):
    return recommend(db, body.message)


@app.get(prefix + "/ai/marketplace-insights")
def insights(user=Depends(current_user), db=Depends(get_db)):
    listing_query = select(Listing.status, func.count()).group_by(Listing.status)
    lead_query = select(Lead.status, func.count()).group_by(Lead.status)
    if user.role != "admin":
        listing_query = listing_query.where(Listing.supplier_id == user.supplier_id)
        lead_query = lead_query.where(Lead.supplier_id == user.supplier_id)
    listing_counts = dict(db.execute(listing_query).all())
    lead_counts = dict(db.execute(lead_query).all())
    categories_query = (
        select(Category.name, func.count(Lead.id))
        .select_from(Lead)
        .join(Listing, Lead.listing_id == Listing.id)
        .join(Category, Listing.category_id == Category.id)
        .group_by(Category.name)
    )
    top_query = (
        select(Lead.listing_id, func.count(Lead.id).label("inquiries"))
        .group_by(Lead.listing_id)
        .order_by(func.count(Lead.id).desc(), Lead.listing_id)
        .limit(5)
    )
    if user.role != "admin":
        categories_query = categories_query.where(Lead.supplier_id == user.supplier_id)
        top_query = top_query.where(Lead.supplier_id == user.supplier_id)
    category_counts = dict(db.execute(categories_query).all())
    top = [
        {
            "listing_id": identifier,
            "title": listing_dict(db, db.get(Listing, identifier))["title"],
            "inquiries": count,
        }
        for identifier, count in db.execute(top_query)
    ]
    view_query = (
        select(ListingView.listing_id, func.count(ListingView.id))
        .join(Listing, Listing.id == ListingView.listing_id)
        .group_by(ListingView.listing_id)
        .order_by(func.count(ListingView.id).desc(), ListingView.listing_id)
        .limit(5)
    )
    if user.role != "admin":
        view_query = view_query.where(Listing.supplier_id == user.supplier_id)
    most_viewed = [
        {
            "listing_id": identifier,
            "title": listing_dict(db, db.get(Listing, identifier))["title"],
            "detail_requests": count,
        }
        for identifier, count in db.execute(view_query)
    ]
    for item in top:
        views = (
            db.scalar(
                select(func.count(ListingView.id)).where(
                    ListingView.listing_id == item["listing_id"]
                )
            )
            or 0
        )
        item["detail_requests"] = views
        item["inquiries_per_100_detail_requests"] = (
            round(item["inquiries"] / views * 100, 1) if views else None
        )
    total_listings, total_leads = (
        sum(listing_counts.values()),
        sum(lead_counts.values()),
    )
    summaries = [
        f"{total_listings} listings and {total_leads} recorded inquiries in this account scope.",
        f"{listing_counts.get('published', 0)} listings have published status; supplier eligibility and administrator visibility still apply.",
        f"{lead_counts.get('new', 0)} inquiries await an initial status update.",
    ]
    if category_counts:
        name, count = max(category_counts.items(), key=lambda pair: pair[1])
        summaries.append(
            f"{name} has {count} recorded inquiries, the highest category count (ties may exist)."
        )
    return {
        "listings_by_status": listing_counts,
        "leads_by_status": lead_counts,
        "totals": {"listings": total_listings, "leads": total_leads},
        "leads_by_category": category_counts,
        "top_listings": top,
        "most_viewed": most_viewed,
        "view_definition": "Detail API requests, including repeated, automated and demonstration requests; not unique visitors or confirmed bookings.",
        "summaries": summaries,
        "scope": "marketplace" if user.role == "admin" else "supplier",
        "mode": "database-aggregates",
    }


@app.post(prefix + "/ai/listing-assistant")
def listing_assistant(
    body: s.Concierge, user=Depends(supplier_user), db=Depends(get_db)
):
    from .concierge import listing_suggestions

    return listing_suggestions(db, body.message)


@app.post(prefix + "/ai/recommendations")
def personalized_recommendations(body: s.RecommendationInput, db=Depends(get_db)):
    from .recommendations import recommendations

    return recommendations(db, body)


@app.put(prefix + "/admin/listings/{listing_id}")
def admin_edit_listing(
    listing_id: int, body: s.ListingInput, user=Depends(admin_user), db=Depends(get_db)
):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.status == "archived":
        raise HTTPException(409, "Archived listings cannot be edited")
    validate_images(body.images, listing.supplier_id, db)
    for key, value in resolve_listing(db, body).items():
        setattr(listing, key, value)
    sync_listing(db, listing, body)
    db.add(
        Audit(
            user_id=user.id,
            action="listing.edit",
            entity_id=listing.id,
            reason="Administrative moderation",
        )
    )
    db.commit()
    return listing_dict(db, listing)


@app.get("/uploads/{supplier_id}/{name}")
def stored_image(supplier_id: int, name: str, db=Depends(get_db)):
    if not re.fullmatch(r"[a-f0-9]{40}\.webp", name):
        raise HTTPException(404, "Image not found")
    image = db.scalar(
        select(Upload).where(Upload.supplier_id == supplier_id, Upload.name == name)
    )
    if not image:
        raise HTTPException(404, "Image not found")
    return Response(
        image.data,
        media_type="image/webp",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Content-Type-Options": "nosniff",
        },
    )
