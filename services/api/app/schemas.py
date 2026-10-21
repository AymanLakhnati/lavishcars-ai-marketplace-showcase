from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
    field_validator,
)


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Register(Login):
    company_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=10, max_length=128)


class Profile(Input):
    company_name: str = Field(min_length=2, max_length=160)
    contact_email: EmailStr
    phone: str = Field(default="", max_length=40)
    license_number: str = Field(default="", max_length=100)


class ListingInput(Input):
    brand: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(default=2026, ge=1990, le=2030)
    trim: str = Field(default="", max_length=100)
    vehicle_type: (
        Literal["SUV", "Sedan", "Coupe", "Convertible", "Hatchback", "Van"] | None
    ) = None
    city: str
    country: str
    category: str
    categories: list[str] = Field(default_factory=list, max_length=10)
    currency: Literal["AED", "USD"]
    daily_price: Decimal = Field(gt=0, le=100000, decimal_places=2)
    weekly_price: Decimal | None = Field(
        default=None, gt=0, le=1000000, decimal_places=2
    )
    monthly_price: Decimal | None = Field(
        default=None, gt=0, le=1000000, decimal_places=2
    )
    deposit: Decimal | None = Field(default=None, ge=0, le=1000000, decimal_places=2)
    mileage: int = Field(default=250, ge=0, le=10000)
    seats: int = Field(default=5, ge=1, le=20)
    transmission: Literal["Automatic", "Manual"] = "Automatic"
    description: str = Field(default="", max_length=5000)
    features: list[str] = Field(default_factory=list, max_length=30)
    images: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("images")
    @classmethod
    def safe_images(cls, values):
        for value in values:
            if (
                not value.startswith(("/uploads/", "/images/"))
                or ".." in value
                or "\\" in value
            ):
                raise ValueError(
                    "Images must use uploaded or local demonstration assets"
                )
        return values


class LeadInput(Input):
    listing_id: int
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=40)
    message: str = Field(min_length=5, max_length=3000)
    start_date: date | None = None
    end_date: date | None = None
    source: Literal["website", "concierge", "wordpress"] = "website"

    @model_validator(mode="after")
    def valid_dates(self):
        if bool(self.start_date) != bool(self.end_date):
            raise ValueError("Provide both rental dates")
        if self.start_date and self.end_date < self.start_date:
            raise ValueError("End date cannot precede start date")
        return self


class Decision(Input):
    reason: str = Field(default="", max_length=1000)


class LeadStatus(Input):
    status: Literal["new", "contacted", "quoted", "booked", "lost"]


class Concierge(Input):
    message: str = Field(min_length=3, max_length=2000)


class RecommendationInput(Input):
    city: str = Field(min_length=1, max_length=100)
    currency: Literal["AED", "USD"] | None = None
    category: str | None = Field(default=None, max_length=80)
    max_price: Decimal | None = Field(default=None, gt=0, le=100000)
    min_seats: int | None = Field(default=None, ge=1, le=20)
    features: list[str] = Field(default_factory=list, max_length=20)
    preferred_categories: list[str] = Field(default_factory=list, max_length=10)
    occasion: Literal["business", "family", "celebration", "leisure"] | None = None


class TaxonomyInput(Input):
    name: str = Field(min_length=1, max_length=80)
    kind: Literal["country", "state", "city", "area", "airport"] | None = None
    parent_id: int | None = None
    active: bool = True
    brand_id: int | None = None


class ServiceAreas(Input):
    location_ids: list[int] = Field(max_length=30)


class Teammate(Input):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
