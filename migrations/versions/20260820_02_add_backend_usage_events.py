"""add backend usage events

Revision ID: 20260820_02
Revises: 20260815_01
Create Date: 2026-08-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260820_02"
down_revision: str | None = "20260815_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_assessment_results_created_at",
        "assessment_results",
        ["created_at"],
        unique=False,
    )
    op.create_table(
        "backend_usage_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("event_name", sa.String(length=32), nullable=False),
        sa.Column("result_code", sa.String(length=8), nullable=False),
        sa.Column("related_result_code", sa.String(length=8), nullable=True),
        sa.Column("compatibility_score", sa.Integer(), nullable=True),
        sa.Column("compatibility_version", sa.String(length=32), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_backend_usage_events_name_occurred",
        "backend_usage_events",
        ["event_name", "occurred_at"],
        unique=False,
    )
    op.create_index(
        "ix_backend_usage_events_result_name",
        "backend_usage_events",
        ["result_code", "event_name"],
        unique=False,
    )
    op.create_index(
        "ix_backend_usage_events_related_name",
        "backend_usage_events",
        ["related_result_code", "event_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_backend_usage_events_related_name",
        table_name="backend_usage_events",
    )
    op.drop_index(
        "ix_backend_usage_events_result_name",
        table_name="backend_usage_events",
    )
    op.drop_index(
        "ix_backend_usage_events_name_occurred",
        table_name="backend_usage_events",
    )
    op.drop_table("backend_usage_events")
    op.drop_index("ix_assessment_results_created_at", table_name="assessment_results")
