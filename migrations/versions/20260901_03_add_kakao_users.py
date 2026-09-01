"""add kakao users and result ownership

Revision ID: 20260901_03
Revises: 20260820_02
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260901_03"
down_revision: str | None = "20260820_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("kakao_user_id", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "last_logged_in_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_kakao_user_id", "users", ["kakao_user_id"], unique=True)
    op.add_column("assessment_results", sa.Column("user_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_assessment_results_user_id_users",
        "assessment_results",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_assessment_results_user_id",
        "assessment_results",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_results_user_id", table_name="assessment_results")
    op.drop_constraint(
        "fk_assessment_results_user_id_users",
        "assessment_results",
        type_="foreignkey",
    )
    op.drop_column("assessment_results", "user_id")
    op.drop_index("ix_users_kakao_user_id", table_name="users")
    op.drop_table("users")
