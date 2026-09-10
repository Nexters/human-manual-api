"""create romantic relationship reports

Revision ID: 20260910_05
Revises: 20260908_04
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260910_05"
down_revision: str | None = "20260908_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "romantic_relationship_reports",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("report_code", sa.String(length=12), nullable=False),
        sa.Column("mine_result_code", sa.String(length=8), nullable=False),
        sa.Column("partner_result_code", sa.String(length=8), nullable=False),
        sa.Column("mine_gender", sa.String(length=20), nullable=False),
        sa.Column("partner_gender", sa.String(length=20), nullable=False),
        sa.Column("prompt_version", sa.String(length=32), nullable=False),
        sa.Column("profile_version", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("provider_response_id", sa.String(length=128), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint(
            "mine_result_code",
            "partner_result_code",
            "mine_gender",
            "partner_gender",
            "prompt_version",
            "profile_version",
            "model",
            name="uq_romantic_report_generation_input",
        ),
    )
    op.create_index(
        "ix_romantic_relationship_reports_report_code",
        "romantic_relationship_reports",
        ["report_code"],
        unique=True,
    )
    op.create_index(
        "ix_romantic_relationship_reports_mine_result_code",
        "romantic_relationship_reports",
        ["mine_result_code"],
    )
    op.create_index(
        "ix_romantic_relationship_reports_partner_result_code",
        "romantic_relationship_reports",
        ["partner_result_code"],
    )
    op.create_index(
        "ix_romantic_relationship_reports_created_at",
        "romantic_relationship_reports",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_table("romantic_relationship_reports")
