import asyncio
from datetime import datetime
from typing import Any, ClassVar

from pytest import MonkeyPatch

from pakit.core.kakaopay import KakaoPayClient
from pakit.services.payment_service import PaymentReadyRequest


class FakeResponse:
    def __init__(self, url: str) -> None:
        self.url = url

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        if self.url.endswith("/ready"):
            return {
                "tid": "T1234567890123456789",
                "next_redirect_app_url": "https://pay.test/app",
                "next_redirect_mobile_url": "https://pay.test/mobile",
                "next_redirect_pc_url": "https://pay.test/pc",
            }
        return {
            "aid": "A1234567890123456789",
            "tid": "T1234567890123456789",
            "partner_order_id": "order-1",
            "partner_user_id": "pakit-42",
            "payment_method_type": "MONEY",
            "amount": {"total": 990},
            "approved_at": "2026-10-07T12:00:00+09:00",
        }


class FakeAsyncClient:
    requests: ClassVar[list[dict[str, Any]]] = []

    def __init__(self, *, timeout: float) -> None:
        self.timeout = timeout

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, url: str, **kwargs: Any) -> FakeResponse:
        type(self).requests.append({"url": url, **kwargs})
        return FakeResponse(url)


def test_sends_kakaopay_ready_and_approve_requests(monkeypatch: MonkeyPatch) -> None:
    FakeAsyncClient.requests = []
    monkeypatch.setattr("pakit.core.kakaopay.httpx2.AsyncClient", FakeAsyncClient)
    client = KakaoPayClient(cid="TC0ONETIME", secret_key="dev-secret")

    async def run() -> None:
        ready = await client.ready(
            PaymentReadyRequest(
                order_id="order-1",
                partner_user_id="pakit-42",
                item_name="Pakit 연인 관계 설명서",
                item_code="romantic-report-v1",
                amount=990,
                approval_url="https://api.test/approve",
                cancel_url="https://api.test/cancel",
                fail_url="https://api.test/fail",
            )
        )
        approved = await client.approve(
            tid=ready.tid,
            order_id="order-1",
            partner_user_id="pakit-42",
            pg_token="pg-token",
            amount=990,
        )
        assert approved.amount == 990
        assert approved.approved_at == datetime.fromisoformat("2026-10-07T12:00:00+09:00")

    asyncio.run(run())

    ready_request, approve_request = FakeAsyncClient.requests
    assert ready_request["headers"]["Authorization"] == "SECRET_KEY dev-secret"
    assert ready_request["json"]["cid"] == "TC0ONETIME"
    assert ready_request["json"]["total_amount"] == 990
    assert ready_request["json"]["tax_free_amount"] == 0
    assert approve_request["json"]["pg_token"] == "pg-token"
    assert approve_request["json"]["total_amount"] == 990
