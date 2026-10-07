from datetime import datetime
from typing import Any

import httpx2

from pakit.services.payment_service import (
    PaymentApprovalResult,
    PaymentGateway,
    PaymentGatewayError,
    PaymentReadyRequest,
    PaymentReadyResult,
)

KAKAOPAY_API_BASE_URL = "https://open-api.kakaopay.com/online/v1/payment"


class KakaoPayClient(PaymentGateway):
    def __init__(self, *, cid: str, secret_key: str, timeout_seconds: float = 10.0) -> None:
        self._cid = cid
        self._secret_key = secret_key
        self._timeout_seconds = timeout_seconds

    async def ready(self, request: PaymentReadyRequest) -> PaymentReadyResult:
        payload = await self._post(
            "/ready",
            {
                "cid": self._cid,
                "partner_order_id": request.order_id,
                "partner_user_id": request.partner_user_id,
                "item_name": request.item_name,
                "item_code": request.item_code,
                "quantity": 1,
                "total_amount": request.amount,
                "tax_free_amount": 0,
                "approval_url": request.approval_url,
                "cancel_url": request.cancel_url,
                "fail_url": request.fail_url,
            },
        )
        try:
            return PaymentReadyResult(
                tid=_required_string(payload, "tid"),
                next_redirect_app_url=_required_string(payload, "next_redirect_app_url"),
                next_redirect_mobile_url=_required_string(payload, "next_redirect_mobile_url"),
                next_redirect_pc_url=_required_string(payload, "next_redirect_pc_url"),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise PaymentGatewayError("카카오페이 결제 준비 응답이 올바르지 않습니다.") from error

    async def approve(
        self,
        *,
        tid: str,
        order_id: str,
        partner_user_id: str,
        pg_token: str,
        amount: int,
    ) -> PaymentApprovalResult:
        payload = await self._post(
            "/approve",
            {
                "cid": self._cid,
                "tid": tid,
                "partner_order_id": order_id,
                "partner_user_id": partner_user_id,
                "pg_token": pg_token,
                "total_amount": amount,
            },
        )
        try:
            amount_payload = payload["amount"]
            if not isinstance(amount_payload, dict):
                raise TypeError
            return PaymentApprovalResult(
                aid=_required_string(payload, "aid"),
                tid=_required_string(payload, "tid"),
                partner_order_id=_required_string(payload, "partner_order_id"),
                partner_user_id=_required_string(payload, "partner_user_id"),
                amount=int(amount_payload["total"]),
                payment_method_type=_required_string(payload, "payment_method_type"),
                approved_at=datetime.fromisoformat(_required_string(payload, "approved_at")),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise PaymentGatewayError("카카오페이 결제 승인 응답이 올바르지 않습니다.") from error

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx2.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{KAKAOPAY_API_BASE_URL}{path}",
                    headers={
                        "Authorization": f"SECRET_KEY {self._secret_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                payload: dict[str, Any] = response.json()
                return payload
        except (httpx2.HTTPError, TypeError, ValueError) as error:
            raise PaymentGatewayError("카카오페이 API 요청에 실패했습니다.") from error


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload[key]
    if not isinstance(value, str) or not value:
        raise ValueError
    return value
