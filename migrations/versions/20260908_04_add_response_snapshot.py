"""preserve original assessment responses

Revision ID: 20260908_04
Revises: 20260901_03
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260908_04"
down_revision: str | None = "20260901_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "assessment_results",
        sa.Column("response_snapshot", postgresql.JSONB(none_as_null=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("assessment_results", "response_snapshot")
