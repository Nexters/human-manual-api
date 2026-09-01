from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field

from pakit.api.schemas.image_urls import absolute_image_url
from pakit.services.user_repository import UserCompatibilitySummary, UserResultSummary

RESULT_CODE_PATTERN = r"^[A-Za-z0-9_-]{8}$"
ResultCode = Annotated[
    str,
    Field(min_length=8, max_length=8, pattern=RESULT_CODE_PATTERN),
]


class CurrentUserOutput(BaseModel):
    user_id: int = Field(description="Pakit 내부 사용자 ID")
    created_at: datetime = Field(description="Pakit 최초 가입 시각")


class ResultSyncInput(BaseModel):
    result_codes: list[ResultCode] = Field(
        min_length=1,
        max_length=100,
        description="비회원 상태에서 이 브라우저에 저장한 결과 코드 목록",
    )


class ResultSyncOutput(BaseModel):
    synced: list[str] = Field(description="현재 사용자에게 새로 연결한 결과 코드")
    already_synced: list[str] = Field(description="이미 현재 사용자에게 연결된 결과 코드")
    rejected: list[str] = Field(description="없거나 다른 사용자에게 연결되어 거부된 결과 코드")


class MyResultItemOutput(BaseModel):
    result_code: ResultCode
    nickname: str | None
    result_name: str
    noun: str
    character_id: str
    image_url: str
    created_at: datetime

    @classmethod
    def from_summary(
        cls,
        summary: UserResultSummary,
        *,
        public_base_url: str,
    ) -> "MyResultItemOutput":
        return cls(
            result_code=summary.result_code,
            nickname=summary.nickname,
            result_name=summary.result_name,
            noun=summary.noun,
            character_id=summary.character_id,
            image_url=absolute_image_url(
                summary.image_url,
                public_base_url=public_base_url,
            ),
            created_at=summary.created_at,
        )


class MyResultsOutput(BaseModel):
    total: int = Field(ge=0)
    items: list[MyResultItemOutput]


class MyCompatibilityItemOutput(BaseModel):
    mine: MyResultItemOutput
    friend: MyResultItemOutput
    score: int = Field(ge=0, le=100)
    tested_at: datetime

    @classmethod
    def from_summary(
        cls,
        summary: UserCompatibilitySummary,
        *,
        public_base_url: str,
    ) -> "MyCompatibilityItemOutput":
        return cls(
            mine=MyResultItemOutput.from_summary(
                summary.mine,
                public_base_url=public_base_url,
            ),
            friend=MyResultItemOutput.from_summary(
                summary.friend,
                public_base_url=public_base_url,
            ),
            score=summary.score,
            tested_at=summary.tested_at,
        )


class MyCompatibilitiesOutput(BaseModel):
    total: int = Field(ge=0)
    items: list[MyCompatibilityItemOutput]


AUTH_ERROR_EXAMPLE: dict[str, Any] = {"detail": "로그인이 필요합니다."}
