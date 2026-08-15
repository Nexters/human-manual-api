from typing import Any
from sqlmodel import Field, SQLModel, Column, JSON

class AssessmentResult(SQLModel, table=True):
    result_code: str = Field(primary_key=True)
    data: dict[str, Any] = Field(sa_column=Column(JSON))
