"""Durable optimized image storage for serverless deployment."""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "uploads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id"), nullable=False
        ),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_uploads_supplier_id", "uploads", ["supplier_id"])


def downgrade():
    op.drop_index("ix_uploads_supplier_id", table_name="uploads")
    op.drop_table("uploads")
