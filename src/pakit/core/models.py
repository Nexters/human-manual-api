from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    )
    kakao_user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_logged_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


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
    response_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSON(none_as_null=True).with_variant(JSONB(none_as_null=True), "postgresql"),
        nullable=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
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


class RomanticRelationshipReportRecord(Base):
    __tablename__ = "romantic_relationship_reports"
    __table_args__ = (
        UniqueConstraint(
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

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    report_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    mine_result_code: Mapped[str] = mapped_column(String(8), index=True)
    partner_result_code: Mapped[str] = mapped_column(String(8), index=True)
    mine_gender: Mapped[str] = mapped_column(String(20))
    partner_gender: Mapped[str] = mapped_column(String(20))
    prompt_version: Mapped[str] = mapped_column(String(32))
    profile_version: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(64))
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
    content: Mapped[str] = mapped_column(Text)
    provider_response_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class PaymentOrderRecord(Base):
    __tablename__ = "payment_orders"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    )
    order_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    product_code: Mapped[str] = mapped_column(String(32))
    product_name: Mapped[str] = mapped_column(String(100))
    product_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
    amount: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="KRW")
    status: Mapped[str] = mapped_column(String(16), index=True)
    kakaopay_tid: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    kakaopay_aid: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_method_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    fulfillment_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
