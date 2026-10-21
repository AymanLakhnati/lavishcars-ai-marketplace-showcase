"""Administrative reference data controls with hierarchy validation and audit history."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from .db import get_db
from .security import admin_user
from .schemas import TaxonomyInput
from .models import Location, Brand, VehicleModel, Category, Audit, Listing
from .catalog import record_dict

router = APIRouter(prefix="/api/v1/admin/taxonomy")
TABLES = {
    "locations": Location,
    "brands": Brand,
    "models": VehicleModel,
    "categories": Category,
}


def table_for(kind):
    if kind not in TABLES:
        raise HTTPException(404, "Unknown taxonomy")
    return TABLES[kind]


@router.get("/{kind}")
def read(kind: str, user=Depends(admin_user), db=Depends(get_db)):
    table = table_for(kind)
    rows = db.scalars(select(table).order_by(table.id).limit(1000)).all()
    return {
        "items": [record_dict(row) for row in rows],
        "total": db.scalar(select(func.count()).select_from(table)),
    }


def save(kind, body, user, db, identifier=None):
    table = table_for(kind)
    row = db.get(table, identifier) if identifier else table()
    if row is None:
        raise HTTPException(404, "Taxonomy record not found")
    if kind == "locations":
        if not body.kind:
            raise HTTPException(422, "Location kind is required")
        parent = db.get(Location, body.parent_id) if body.parent_id else None
        allowed = {
            "country": set(),
            "state": {"country"},
            "city": {"country", "state"},
            "area": {"city", "area"},
            "airport": {"city", "area"},
        }
        if (
            body.kind == "country"
            and body.parent_id
            or body.kind != "country"
            and (not parent or parent.kind not in allowed[body.kind])
        ):
            raise HTTPException(422, "Invalid location parent hierarchy")
        seen = {identifier} if identifier else set()
        ancestor = parent
        while ancestor:
            if ancestor.id in seen:
                raise HTTPException(422, "Location hierarchy cannot contain cycles")
            seen.add(ancestor.id)
            ancestor = (
                db.get(Location, ancestor.parent_id) if ancestor.parent_id else None
            )
        if identifier and (row.parent_id != body.parent_id or row.kind != body.kind):
            if db.scalar(
                select(Location.id).where(Location.parent_id == identifier).limit(1)
            ) or db.scalar(
                select(Listing.id).where(Listing.location_id == identifier).limit(1)
            ):
                raise HTTPException(
                    409,
                    "Cannot restructure a location with children or existing inventory",
                )
        row.kind, row.parent_id, row.active = body.kind, body.parent_id, body.active
    elif kind == "models":
        if not body.brand_id or not db.get(Brand, body.brand_id):
            raise HTTPException(422, "Choose an existing brand")
        if (
            identifier
            and row.brand_id != body.brand_id
            and db.scalar(
                select(Listing.id).where(Listing.model_id == identifier).limit(1)
            )
        ):
            raise HTTPException(
                409, "Cannot change the brand of a model referenced by inventory"
            )
        row.brand_id = body.brand_id
    if (
        kind != "locations"
        and (body.parent_id is not None or body.kind is not None)
        or kind != "models"
        and body.brand_id is not None
    ):
        raise HTTPException(422, "Fields do not apply to this taxonomy")
    duplicate = select(table).where(func.lower(table.name) == body.name.lower())
    if identifier:
        duplicate = duplicate.where(table.id != identifier)
    if kind == "models":
        duplicate = duplicate.where(VehicleModel.brand_id == body.brand_id)
    if kind == "locations":
        duplicate = duplicate.where(Location.parent_id == body.parent_id)
    if db.scalar(duplicate):
        raise HTTPException(409, "Name already exists in this scope")
    row.name = body.name
    db.add(row)
    try:
        db.flush()
        db.add(
            Audit(
                user_id=user.id,
                action=f"taxonomy.{kind}." + ("update" if identifier else "create"),
                entity_id=row.id,
                reason="Reference data maintenance",
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Reference data conflicts with existing records")
    return record_dict(row)


@router.post("/{kind}", status_code=201)
def create(
    kind: str, body: TaxonomyInput, user=Depends(admin_user), db=Depends(get_db)
):
    return save(kind, body, user, db)


@router.put("/{kind}/{identifier}")
def update(
    kind: str,
    identifier: int,
    body: TaxonomyInput,
    user=Depends(admin_user),
    db=Depends(get_db),
):
    return save(kind, body, user, db, identifier)
