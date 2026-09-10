from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RomanticReportCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    mine_result_code: str = Field(
        min_length=8,
        max_length=8,
        pattern=r"^[A-Za-z0-9_-]{8}$",
        description="설명서를 요청하는 사람의 결과 코드",
    )
    partner_result_code: str = Field(
        min_length=8,
        max_length=8,
        pattern=r"^[A-Za-z0-9_-]{8}$",
        description="상대방의 결과 코드",
    )
    mine_gender: str = Field(
        min_length=1,
        max_length=20,
        pattern=r"^[가-힣A-Za-z ]+$",
        description="설명서를 요청하는 사람이 직접 입력한 성별",
    )
    partner_gender: str = Field(
        min_length=1,
        max_length=20,
        pattern=r"^[가-힣A-Za-z ]+$",
        description="상대방에 대해 직접 입력한 성별",
    )

    @model_validator(mode="after")
    def require_two_results(self) -> "RomanticReportCreateInput":
        if self.mine_result_code == self.partner_result_code:
            raise ValueError("서로 다른 두 결과 코드가 필요합니다.")
        return self


class RomanticReportOutput(BaseModel):
    report_code: str = Field(description="저장된 관계 설명서의 고유 코드")
    content: str = Field(description="Markdown 형식의 연인 관계 설명서")
    created_at: datetime = Field(description="처음 생성해 저장한 시각")


ROMANTIC_REPORT_REQUEST_EXAMPLE = {
    "mine_result_code": "GU26BwcL",
    "partner_result_code": "877ApB1D",
    "mine_gender": "여자",
    "partner_gender": "남자",
}
