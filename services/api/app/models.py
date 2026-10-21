from datetime import datetime, timezone
from sqlalchemy import (
    LargeBinary,
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def now():
    return datetime.now(timezone.utc)


class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(160))
    contact_email: Mapped[str] = mapped_column(String(254))
    phone: Mapped[str] = mapped_column(String(40), default="")
    license_number: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    active: Mapped[bool] = mapped_column(default=True)
    rejection_reason: Mapped[str] = mapped_column(Text, default="")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(24), default="supplier")
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    kind: Mapped[str] = mapped_column(String(20))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    active: Mapped[bool] = mapped_column(default=True)


class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class VehicleModel(Base):
    __tablename__ = "models"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class Listing(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(240), unique=True, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), index=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    year: Mapped[int] = mapped_column(Integer)
    trim: Mapped[str] = mapped_column(String(100), default="")
    vehicle_type: Mapped[str] = mapped_column(String(30), default="SUV")
    currency: Mapped[str] = mapped_column(String(3))
    daily_price: Mapped[float] = mapped_column(Numeric(12, 2))
    weekly_price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    monthly_price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    deposit: Mapped[float | None] = mapped_column(Numeric(12, 2))
    mileage: Mapped[int] = mapped_column(default=250)
    seats: Mapped[int] = mapped_column(default=5)
    transmission: Mapped[str] = mapped_column(String(20), default="Automatic")
    description: Mapped[str] = mapped_column(Text, default="")
    features: Mapped[list] = mapped_column(JSON, default=list)
    images: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
    rejection_reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    admin_hidden: Mapped[bool] = mapped_column(default=False)
    __table_args__ = (
        Index(
            "ix_listing_discovery", "status", "location_id", "currency", "daily_price"
        ),
    )


class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254))
    phone: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(40), default="website")
    start_date: Mapped[datetime | None] = mapped_column(Date)
    end_date: Mapped[datetime | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(24), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Outbox(Base):
    __tablename__ = "notification_outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"))
    status: Mapped[str] = mapped_column(String(24), default="pending")
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str] = mapped_column(Text, default="")


class Audit(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[int] = mapped_column()
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Upload(Base):
    __tablename__ = "uploads"
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    data: Mapped[bytes] = mapped_column(LargeBinary)
    content_hash: Mapped[str] = mapped_column(String(64), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SupplierUser(Base):
    __tablename__ = "supplier_users"
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, unique=True
    )
    membership_role: Mapped[str] = mapped_column(String(20), default="member")


class SupplierLocation(Base):
    __tablename__ = "supplier_locations"
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"), primary_key=True
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), primary_key=True
    )


class ListingCategory(Base):
    __tablename__ = "listing_categories"
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), primary_key=True
    )


class ListingImage(Base):
    __tablename__ = "listing_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(240))


class ListingView(Base):
    __tablename__ = "listing_views"
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
