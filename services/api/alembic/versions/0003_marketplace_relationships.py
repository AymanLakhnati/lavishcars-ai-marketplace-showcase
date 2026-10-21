"""Normalized supplier/listing associations, vehicle detail and view events."""

import json
import hashlib
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "suppliers",
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "listings", sa.Column("trim", sa.String(100), nullable=False, server_default="")
    )
    op.add_column(
        "listings",
        sa.Column("vehicle_type", sa.String(30), nullable=False, server_default="SUV"),
    )
    op.add_column(
        "uploads",
        sa.Column("content_hash", sa.String(64), nullable=False, server_default=""),
    )
    op.create_index("ix_uploads_content_hash", "uploads", ["content_hash"])
    op.create_table(
        "supplier_users",
        sa.Column(
            "supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id"), primary_key=True
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            primary_key=True,
            unique=True,
        ),
        sa.Column("membership_role", sa.String(20), nullable=False),
    )
    op.create_table(
        "supplier_locations",
        sa.Column(
            "supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id"), primary_key=True
        ),
        sa.Column(
            "location_id", sa.Integer(), sa.ForeignKey("locations.id"), primary_key=True
        ),
    )
    op.create_table(
        "listing_categories",
        sa.Column(
            "listing_id", sa.Integer(), sa.ForeignKey("listings.id"), primary_key=True
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id"),
            primary_key=True,
        ),
    )
    op.create_table(
        "listing_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "listing_id", sa.Integer(), sa.ForeignKey("listings.id"), nullable=False
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(240), nullable=False),
    )
    op.create_index("ix_listing_images_listing_id", "listing_images", ["listing_id"])
    op.create_table(
        "listing_views",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "listing_id", sa.Integer(), sa.ForeignKey("listings.id"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_listing_views_listing_id", "listing_views", ["listing_id"])
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "INSERT INTO supplier_users (supplier_id,user_id,membership_role) SELECT supplier_id,id,'owner' FROM users WHERE supplier_id IS NOT NULL"
        )
    )
    bind.execute(
        sa.text(
            "INSERT INTO supplier_locations (supplier_id,location_id) SELECT DISTINCT supplier_id,location_id FROM listings"
        )
    )
    bind.execute(
        sa.text(
            "INSERT INTO listing_categories (listing_id,category_id) SELECT id,category_id FROM listings"
        )
    )
    bind.execute(
        sa.text("UPDATE suppliers SET active = false WHERE status = 'suspended'")
    )
    bind.execute(
        sa.text(
            "UPDATE listings SET vehicle_type = (SELECT CASE WHEN name='SUV' THEN 'SUV' WHEN name='Convertible' THEN 'Convertible' WHEN name IN ('Sports','Supercar') THEN 'Coupe' ELSE 'Sedan' END FROM categories WHERE categories.id=listings.category_id)"
        )
    )
    listings = sa.table(
        "listings", sa.column("id", sa.Integer()), sa.column("images", sa.JSON())
    )
    images = sa.table(
        "listing_images",
        sa.column("listing_id", sa.Integer()),
        sa.column("position", sa.Integer()),
        sa.column("url", sa.String()),
    )
    for row in bind.execute(sa.select(listings.c.id, listings.c.images)):
        urls = json.loads(row.images) if isinstance(row.images, str) else row.images
        if urls:
            bind.execute(
                images.insert(),
                [
                    {"listing_id": row.id, "position": i, "url": url}
                    for i, url in enumerate(urls)
                ],
            )
    uploads = sa.table(
        "uploads",
        sa.column("id", sa.Integer()),
        sa.column("data", sa.LargeBinary()),
        sa.column("content_hash", sa.String()),
    )
    for row in bind.execute(sa.select(uploads.c.id, uploads.c.data)):
        bind.execute(
            uploads.update()
            .where(uploads.c.id == row.id)
            .values(content_hash=hashlib.sha256(row.data).hexdigest())
        )


def downgrade():
    op.drop_index("ix_uploads_content_hash", table_name="uploads")
    op.drop_column("uploads", "content_hash")
    op.drop_table("listing_views")
    op.drop_table("listing_images")
    op.drop_table("listing_categories")
    op.drop_table("supplier_locations")
    op.drop_table("supplier_users")
    op.drop_column("listings", "vehicle_type")
    op.drop_column("listings", "trim")
    op.drop_column("suppliers", "active")
