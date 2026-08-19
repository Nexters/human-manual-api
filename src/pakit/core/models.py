from datetime import datetime
from typing import Any

from sqlalchemy import JSON, BigInteger, DateTime, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AssessmentResultRecord(Base):
    __tablename__ = "assessment_results"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    )
    result_code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    assessment_version: Mapped[str] = mapped_column(String(32))
    content_version: Mapped[str] = mapped_column(String(32))
    result_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )


class BackendUsageEventRecord(Base):
    __tablename__ = "backend_usage_events"
    __table_args__ = (
        Index("ix_backend_usage_events_name_occurred", "event_name", "occurred_at"),
        Index("ix_backend_usage_events_result_name", "result_code", "event_name"),
        Index("ix_backend_usage_events_related_name", "related_result_code", "event_name"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    )
    event_name: Mapped[str] = mapped_column(String(32))
    result_code: Mapped[str] = mapped_column(String(8))
    related_result_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    compatibility_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    compatibility_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
