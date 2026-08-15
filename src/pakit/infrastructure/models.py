from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from pakit.core.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    result_code: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    assessment_version: Mapped[str] = mapped_column(String(50), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    mbti: Mapped[str] = mapped_column(String(4), nullable=False)
    answers: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    result_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
