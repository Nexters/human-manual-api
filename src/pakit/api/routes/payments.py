from typing import Annotated
from urllib.parse import urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse

from pakit.api.auth_dependencies import require_current_user
from pakit.api.dependencies import get_payment_gateway, get_payment_repository
from pakit.api.schemas.assessment_submissions import ErrorResponse
from pakit.api.schemas.payments import (
    KakaoPayReadyInput,
    KakaoPayReadyOutput,
    KakaoPayRedirectOutput,
    PaymentOrderOutput,
)
from pakit.core.config import ALLOWED_CORS_ORIGINS, Settings, get_settings
from pakit.services.payment_service import (
    PaymentGateway,
    PaymentGatewayError,
    PaymentOrderNotFoundError,
    PaymentOrderStateError,
    PaymentRepository,
    PaymentResultNotFoundError,
    PaymentResultNotOwnedError,
    RomanticReportPurchase,
    approve_payment,
    prepare_payment,
)
from pakit.services.user_repository import StoredUser

router = APIRouter(prefix="/payments/kakaopay", tags=["Payment"])
OrderId = Annotated[
    str,
    Path(min_length=16, max_length=32, pattern=r"^[A-Za-z0-9_-]+$"),
]


@router.post(
    "/ready",
    response_model=KakaoPayReadyOutput,
    responses={
        401: {"model": ErrorResponse, "description": "로그인 필요"},
        403: {"model": ErrorResponse, "description": "본인 결과가 아님"},
        404: {"model": ErrorResponse, "description": "결과 코드 없음"},
        502: {"model": ErrorResponse, "description": "카카오페이 요청 실패"},
        503: {"model": ErrorResponse, "description": "카카오페이 설정 없음"},
    },
)
async def ready_kakaopay_payment(
    body: KakaoPayReadyInput,
    request: Request,
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
    gateway: Annotated[PaymentGateway | None, Depends(get_payment_gateway)],
) -> KakaoPayReadyOutput | JSONResponse:
    if gateway is None:
        return _error(503, "KAKAOPAY_NOT_CONFIGURED", "카카오페이 설정이 필요합니다.")
    purchase = RomanticReportPurchase(**body.model_dump())
    try:
        frontend_origin = _safe_frontend_origin(request.headers.get("origin"))
        ready = await prepare_payment(
            user_id=user.id,
            purchase=purchase,
            approval_url=_gateway_callback_url(
                request, "approve_kakaopay_payment", frontend_origin
            ),
            cancel_url=_gateway_callback_url(request, "cancel_kakaopay_payment", frontend_origin),
            fail_url=_gateway_callback_url(request, "fail_kakaopay_payment", frontend_origin),
            repository=repository,
            gateway=gateway,
        )
    except PaymentResultNotFoundError:
        return _error(404, "PAYMENT_RESULT_NOT_FOUND", "테스트 결과를 찾을 수 없습니다.")
    except PaymentResultNotOwnedError:
        return _error(403, "PAYMENT_RESULT_NOT_OWNED", "본인 계정의 결과만 구매할 수 있습니다.")
    except PaymentGatewayError:
        return _error(502, "KAKAOPAY_READY_FAILED", "카카오페이 결제 준비에 실패했습니다.")
    base = PaymentOrderOutput.from_order(ready.order).model_dump()
    return KakaoPayReadyOutput(
        **base,
        redirect_url=KakaoPayRedirectOutput.from_result(ready.redirect),
    )


@router.get("/{order_id}/approve", response_model=PaymentOrderOutput)
async def approve_kakaopay_payment(
    order_id: OrderId,
    pg_token: Annotated[str, Query(min_length=1, max_length=256)],
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
    gateway: Annotated[PaymentGateway | None, Depends(get_payment_gateway)],
    settings: Annotated[Settings, Depends(get_settings)],
    frontend_origin: Annotated[str | None, Query(max_length=200)] = None,
) -> RedirectResponse | JSONResponse:
    if gateway is None:
        return _error(503, "KAKAOPAY_NOT_CONFIGURED", "카카오페이 설정이 필요합니다.")
    try:
        order = await approve_payment(
            order_id=order_id,
            user_id=user.id,
            pg_token=pg_token,
            repository=repository,
            gateway=gateway,
        )
    except PaymentOrderNotFoundError:
        return _error(404, "PAYMENT_ORDER_NOT_FOUND", "결제 주문을 찾을 수 없습니다.")
    except PaymentOrderStateError:
        return _error(409, "PAYMENT_ORDER_STATE_INVALID", "승인할 수 없는 결제 상태입니다.")
    except PaymentGatewayError:
        return _error(502, "KAKAOPAY_APPROVAL_FAILED", "카카오페이 결제 승인에 실패했습니다.")
    return RedirectResponse(
        _frontend_result_url(settings, order.order_id, "approved", frontend_origin)
    )


@router.get("/{order_id}/cancel", response_model=PaymentOrderOutput)
async def cancel_kakaopay_payment(
    order_id: OrderId,
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
    frontend_origin: Annotated[str | None, Query(max_length=200)] = None,
) -> RedirectResponse | JSONResponse:
    order = await repository.set_canceled(order_id, user.id)
    if order is None:
        return _error(404, "PAYMENT_ORDER_NOT_FOUND", "결제 주문을 찾을 수 없습니다.")
    return RedirectResponse(
        _frontend_result_url(settings, order.order_id, "canceled", frontend_origin)
    )


@router.get("/{order_id}/fail", response_model=PaymentOrderOutput)
async def fail_kakaopay_payment(
    order_id: OrderId,
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
    frontend_origin: Annotated[str | None, Query(max_length=200)] = None,
) -> RedirectResponse | JSONResponse:
    order = await repository.set_failed(order_id, user.id)
    if order is None:
        return _error(404, "PAYMENT_ORDER_NOT_FOUND", "결제 주문을 찾을 수 없습니다.")
    return RedirectResponse(
        _frontend_result_url(settings, order.order_id, "failed", frontend_origin)
    )


@router.get("/{order_id}", response_model=PaymentOrderOutput)
async def get_payment_order(
    order_id: OrderId,
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
) -> PaymentOrderOutput | JSONResponse:
    order = await repository.get_for_user(order_id, user.id)
    if order is None:
        return _error(404, "PAYMENT_ORDER_NOT_FOUND", "결제 주문을 찾을 수 없습니다.")
    return PaymentOrderOutput.from_order(order)


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def _safe_frontend_origin(value: str | None) -> str | None:
    if value is None:
        return None
    parsed = urlsplit(value)
    origin = urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
    return origin if value == origin and origin in ALLOWED_CORS_ORIGINS else None


def _gateway_callback_url(request: Request, route_name: str, frontend_origin: str | None) -> str:
    callback_url = str(request.url_for(route_name, order_id="ORDER_ID"))
    if frontend_origin is None:
        return callback_url
    return f"{callback_url}?{urlencode({'frontend_origin': frontend_origin})}"


def _frontend_result_url(
    settings: Settings,
    order_id: str,
    status: str,
    frontend_origin: str | None = None,
) -> str:
    redirect_url = settings.frontend_payment_redirect_url
    safe_origin = _safe_frontend_origin(frontend_origin)
    if safe_origin is not None:
        configured = urlsplit(redirect_url)
        origin = urlsplit(safe_origin)
        redirect_url = urlunsplit(
            (origin.scheme, origin.netloc, configured.path, configured.query, "")
        )
    separator = "&" if "?" in redirect_url else "?"
    query = urlencode({"order_id": order_id, "status": status})
    return f"{redirect_url}{separator}{query}"
