"""add KakaoPay payment orders

Revision ID: 20261007_06
Revises: 20260910_05
Create Date: 2026-10-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261007_06"
down_revision: str | None = "20260910_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payment_orders",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("product_code", sa.String(length=32), nullable=False),
        sa.Column("product_name", sa.String(length=100), nullable=False),
        sa.Column("product_payload", postgresql.JSONB(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("kakaopay_tid", sa.String(length=20), nullable=True),
        sa.Column("kakaopay_aid", sa.String(length=20), nullable=True),
        sa.Column("payment_method_type", sa.String(length=16), nullable=True),
        sa.Column("fulfillment_reference", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_payment_orders_order_id", "payment_orders", ["order_id"], unique=True)
    op.create_index("ix_payment_orders_user_id", "payment_orders", ["user_id"])
    op.create_index("ix_payment_orders_status", "payment_orders", ["status"])
    op.create_index(
        "ix_payment_orders_kakaopay_tid", "payment_orders", ["kakaopay_tid"], unique=True
    )


def downgrade() -> None:
    op.drop_table("payment_orders")
