"""create assessment results

Revision ID: 20260815_01
Revises:
Create Date: 2026-08-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260815_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assessment_results",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("result_code", sa.String(length=8), nullable=False),
        sa.Column("assessment_version", sa.String(length=32), nullable=False),
        sa.Column("content_version", sa.String(length=32), nullable=False),
        sa.Column("result_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_assessment_results_result_code",
        "assessment_results",
        ["result_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_results_result_code", table_name="assessment_results")
    op.drop_table("assessment_results")
