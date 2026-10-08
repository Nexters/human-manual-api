from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from pakit.services.usage_event_repository import UsageEventName


@dataclass(frozen=True)
class StoredResult:
    result_code: str
    assessment_version: str
    content_version: str
    snapshot: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class StoredUsageEvent:
    event_name: UsageEventName
    result_code: str
    related_result_code: str | None
    compatibility_score: int | None
    compatibility_version: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class StoredAdminPayment:
    order_id: str
    user_id: int
    product_code: str
    product_name: str
    product_payload: dict[str, Any]
    amount: int
    currency: str
    status: str
    kakaopay_tid: str | None
    kakaopay_aid: str | None
    payment_method_type: str | None
    report_code: str | None
    created_at: datetime
    approved_at: datetime | None


@dataclass(frozen=True)
class StoredAdminUser:
    user_id: int
    created_at: datetime
    last_logged_in_at: datetime
    result_codes: tuple[str, ...]
    order_ids: tuple[str, ...]
    report_codes: tuple[str, ...]
    approved_payment_count: int
    total_paid_amount: int


@dataclass(frozen=True)
class StoredAdminPaidReport:
    report_code: str
    order_ids: tuple[str, ...]
    user_ids: tuple[int, ...]
    mine_result_code: str
    partner_result_code: str
    mine_gender: str
    partner_gender: str
    prompt_version: str
    profile_version: str
    model: str
    input_snapshot: dict[str, Any]
    content: str
    provider_response_id: str | None
    input_tokens: int | None
    output_tokens: int | None
    created_at: datetime


class AdminRepository(Protocol):
    async def list_results(self) -> list[StoredResult]: ...

    async def get_result(self, result_code: str) -> StoredResult | None: ...

    async def list_usage_events(self) -> list[StoredUsageEvent]: ...

    async def list_payments(self) -> list[StoredAdminPayment]: ...

    async def get_payment(self, order_id: str) -> StoredAdminPayment | None: ...

    async def list_users(self) -> list[StoredAdminUser]: ...

    async def get_user(self, user_id: int) -> StoredAdminUser | None: ...

    async def list_paid_reports(self) -> list[StoredAdminPaidReport]: ...

    async def get_paid_report(self, report_code: str) -> StoredAdminPaidReport | None: ...
