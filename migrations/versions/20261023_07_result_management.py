"""account primary result and soft deletion

Revision ID: 20261023_07
Revises: 20261007_06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261023_07"
down_revision: str | None = "20261007_06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("primary_result_code", sa.String(8), nullable=True))
    op.add_column(
        "assessment_results", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("assessment_results", "deleted_at")
    op.drop_column("users", "primary_result_code")
