from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from pakit.api.schemas.romantic_reports import RomanticReportCreateInput
from pakit.services.payment_service import PaymentOrder, PaymentReadyResult


class KakaoPayReadyInput(RomanticReportCreateInput):
    pass


class KakaoPayRedirectOutput(BaseModel):
    app: str
    mobile: str
    pc: str

    @classmethod
    def from_result(cls, result: PaymentReadyResult) -> "KakaoPayRedirectOutput":
        return cls(
            app=result.next_redirect_app_url,
            mobile=result.next_redirect_mobile_url,
            pc=result.next_redirect_pc_url,
        )


class PaymentOrderOutput(BaseModel):
    order_id: str
    product_code: str
    product_name: str
    status: Literal["CREATED", "READY", "APPROVED", "CANCELED", "FAILED"]
    amount: int
    currency: Literal["KRW"] = "KRW"
    fulfillment_reference: str | None
    created_at: datetime
    approved_at: datetime | None

    @classmethod
    def from_order(cls, order: PaymentOrder) -> "PaymentOrderOutput":
        return cls(
            order_id=order.order_id,
            product_code=order.product_code,
            product_name=order.product_name,
            status=order.status,
            amount=order.amount,
            fulfillment_reference=order.fulfillment_reference,
            created_at=order.created_at,
            approved_at=order.approved_at,
        )


class MyPaymentOrderOutput(PaymentOrderOutput):
    mine_result_code: str = Field(description="구매자 본인의 테스트 결과 코드")
    partner_result_code: str = Field(description="상대방의 테스트 결과 코드")
    mine_gender: str = Field(description="구매 당시 본인의 성별")
    partner_gender: str = Field(description="구매 당시 상대방의 성별")

    @classmethod
    def from_order(cls, order: PaymentOrder) -> "MyPaymentOrderOutput":
        return cls(
            **PaymentOrderOutput.from_order(order).model_dump(),
            mine_result_code=order.purchase.mine_result_code,
            partner_result_code=order.purchase.partner_result_code,
            mine_gender=order.purchase.mine_gender,
            partner_gender=order.purchase.partner_gender,
        )


class MyPaymentOrdersOutput(BaseModel):
    total: int = Field(ge=0)
    items: list[MyPaymentOrderOutput]


class KakaoPayReadyOutput(PaymentOrderOutput):
    redirect_url: KakaoPayRedirectOutput = Field(description="접속 환경별 카카오페이 결제 화면 URL")
