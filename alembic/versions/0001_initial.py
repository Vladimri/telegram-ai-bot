"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-12
"""

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "cars",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("make", sa.String, nullable=False),
        sa.Column("model", sa.String, nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("mileage_km", sa.Integer, nullable=False),
        sa.Column("color", sa.String, nullable=False),
        sa.Column("is_new", sa.Boolean, nullable=False),
        sa.Column("owners_count", sa.Integer, nullable=False),
        sa.Column("condition", sa.String, nullable=False),
        sa.Column("price_eur", sa.Numeric(10, 2), nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("status", sa.String, nullable=False, server_default="available"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "condition IN ('new', 'excellent', 'good', 'average', 'poor')",
            name="cars_condition_check",
        ),
        sa.CheckConstraint("status IN ('available', 'reserved')", name="cars_status_check"),
    )
    # Note: the ivfflat index on cars.embedding is intentionally NOT created here.
    # ivfflat needs existing rows to train its clusters on, so it is built by
    # scripts/seed_cars.py after the catalog is seeded, not against an empty table.

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("car_id", sa.Integer, sa.ForeignKey("cars.id"), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger, nullable=False),
        sa.Column("contact_name", sa.String, nullable=True),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled')", name="bookings_status_check"
        ),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("telegram_chat_id", sa.BigInteger, nullable=False),
        sa.Column("role", sa.String, nullable=False),
        sa.Column("content", sa.String, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="chat_messages_role_check"),
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("bookings")
    op.drop_table("cars")
    op.execute("DROP EXTENSION IF EXISTS vector")
