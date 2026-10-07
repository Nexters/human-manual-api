from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol

ROMANTIC_REPORT_PRICE_KRW = 990
ROMANTIC_REPORT_PRODUCT_CODE = "romantic-report-v1"

PaymentStatus = Literal["CREATED", "READY", "APPROVED", "CANCELED", "FAILED"]


@dataclass(frozen=True)
class RomanticReportPurchase:
    mine_result_code: str
    partner_result_code: str
    mine_gender: str
    partner_gender: str


@dataclass(frozen=True)
class PaymentOrder:
    order_id: str
    user_id: int
    product_code: str
    product_name: str
    purchase: RomanticReportPurchase
    amount: int
    status: PaymentStatus
    tid: str | None
    aid: str | None
    fulfillment_reference: str | None
    created_at: datetime
    approved_at: datetime | None


@dataclass(frozen=True)
class ResultAccess:
    mine_exists: bool
    mine_owned_by_user: bool
    partner_exists: bool


@dataclass(frozen=True)
class PaymentReadyRequest:
    order_id: str
    partner_user_id: str
    item_name: str
    item_code: str
    amount: int
    approval_url: str
    cancel_url: str
    fail_url: str


@dataclass(frozen=True)
class PaymentReadyResult:
    tid: str
    next_redirect_app_url: str
    next_redirect_mobile_url: str
    next_redirect_pc_url: str


@dataclass(frozen=True)
class PaymentApprovalResult:
    aid: str
    tid: str
    partner_order_id: str
    partner_user_id: str
    amount: int
    payment_method_type: str
    approved_at: datetime


@dataclass(frozen=True)
class ReadyPayment:
    order: PaymentOrder
    redirect: PaymentReadyResult


class PaymentRepository(Protocol):
    async def get_result_access(
        self, user_id: int, mine_result_code: str, partner_result_code: str
    ) -> ResultAccess: ...

    async def create_order(
        self, user_id: int, purchase: RomanticReportPurchase
    ) -> PaymentOrder: ...

    async def set_ready(self, order_id: str, tid: str) -> PaymentOrder: ...

    async def set_failed(self, order_id: str, user_id: int) -> PaymentOrder | None: ...

    async def set_canceled(self, order_id: str, user_id: int) -> PaymentOrder | None: ...

    async def get_for_user(self, order_id: str, user_id: int) -> PaymentOrder | None: ...

    async def set_approved(
        self,
        order_id: str,
        user_id: int,
        approval: PaymentApprovalResult,
    ) -> PaymentOrder | None: ...

    async def attach_report(
        self, order_id: str, user_id: int, report_code: str
    ) -> PaymentOrder | None: ...


class PaymentGateway(Protocol):
    async def ready(self, request: PaymentReadyRequest) -> PaymentReadyResult: ...

    async def approve(
        self,
        *,
        tid: str,
        order_id: str,
        partner_user_id: str,
        pg_token: str,
        amount: int,
    ) -> PaymentApprovalResult: ...


class PaymentConfigurationError(RuntimeError):
    pass


class PaymentGatewayError(RuntimeError):
    pass


class PaymentResultNotFoundError(RuntimeError):
    pass


class PaymentResultNotOwnedError(RuntimeError):
    pass


class PaymentOrderNotFoundError(RuntimeError):
    pass


class PaymentOrderStateError(RuntimeError):
    pass


def payment_partner_user_id(user_id: int) -> str:
    return f"pakit-{user_id}"


async def prepare_payment(
    *,
    user_id: int,
    purchase: RomanticReportPurchase,
    approval_url: str,
    cancel_url: str,
    fail_url: str,
    repository: PaymentRepository,
    gateway: PaymentGateway,
) -> ReadyPayment:
    access = await repository.get_result_access(
        user_id, purchase.mine_result_code, purchase.partner_result_code
    )
    if not access.mine_exists or not access.partner_exists:
        raise PaymentResultNotFoundError
    if not access.mine_owned_by_user:
        raise PaymentResultNotOwnedError

    order = await repository.create_order(user_id, purchase)
    try:
        redirect = await gateway.ready(
            PaymentReadyRequest(
                order_id=order.order_id,
                partner_user_id=payment_partner_user_id(user_id),
                item_name="Pakit 연인 관계 설명서",
                item_code=ROMANTIC_REPORT_PRODUCT_CODE,
                amount=ROMANTIC_REPORT_PRICE_KRW,
                approval_url=approval_url.replace("ORDER_ID", order.order_id),
                cancel_url=cancel_url.replace("ORDER_ID", order.order_id),
                fail_url=fail_url.replace("ORDER_ID", order.order_id),
            )
        )
    except PaymentGatewayError:
        await repository.set_failed(order.order_id, user_id)
        raise
    ready_order = await repository.set_ready(order.order_id, redirect.tid)
    return ReadyPayment(order=ready_order, redirect=redirect)


async def approve_payment(
    *,
    order_id: str,
    user_id: int,
    pg_token: str,
    repository: PaymentRepository,
    gateway: PaymentGateway,
) -> PaymentOrder:
    order = await repository.get_for_user(order_id, user_id)
    if order is None:
        raise PaymentOrderNotFoundError
    if order.status == "APPROVED":
        return order
    if order.status != "READY" or order.tid is None:
        raise PaymentOrderStateError
    partner_user_id = payment_partner_user_id(user_id)
    approval = await gateway.approve(
        tid=order.tid,
        order_id=order.order_id,
        partner_user_id=partner_user_id,
        pg_token=pg_token,
        amount=order.amount,
    )
    if (
        approval.tid != order.tid
        or approval.partner_order_id != order.order_id
        or approval.partner_user_id != partner_user_id
        or approval.amount != order.amount
    ):
        raise PaymentGatewayError("카카오페이 승인 응답이 주문과 일치하지 않습니다.")
    approved = await repository.set_approved(order_id, user_id, approval)
    if approved is None:
        raise PaymentOrderStateError
    return approved
