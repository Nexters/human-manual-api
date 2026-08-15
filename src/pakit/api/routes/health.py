from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.pakit.core.database import get_db
from src.pakit.infrastructure.models import Submission

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    database: Literal["ok", "error"] = "ok"


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    try:
        # Perform a simple read operation on the Submission table
        await db.execute(select(Submission).limit(1))
        return HealthResponse(status="ok", database="ok")
    except Exception:
        # If the table doesn't exist yet, this will raise an error,
        # which is expected behavior until migrations/setup are fully applied.
        return HealthResponse(status="ok", database="error")
