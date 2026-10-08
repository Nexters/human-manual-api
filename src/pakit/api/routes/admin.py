from datetime import date
from math import ceil
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from pakit.api.admin_auth import require_admin
from pakit.api.dependencies import get_admin_repository
from pakit.api.schemas.admin import (
    AdminDashboardOutput,
    AdminPaidReportListOutput,
    AdminPaidReportOutput,
    AdminPaidReportSummaryOutput,
    AdminPaymentListOutput,
    AdminPaymentOutput,
    AdminPaymentSummaryOutput,
    AdminResultDetailOutput,
    AdminResultListOutput,
    AdminUserListOutput,
    AdminUserOutput,
    AdminUserSummaryOutput,
    CompatibilityAnalyticsOutput,
    ResultAnalyticsOutput,
)
from pakit.core.config import get_settings
from pakit.services.admin_repository import AdminRepository
from pakit.services.admin_service import (
    build_compatibility_analytics,
    build_dashboard,
    build_result_analytics,
    filter_admin_paid_reports,
    filter_admin_payments,
    filter_admin_users,
    filter_results,
    filter_usage_events,
    result_summary,
    usage_counts,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/dashboard", response_model=AdminDashboardOutput)
async def get_admin_dashboard(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
) -> AdminDashboardOutput:
    return AdminDashboardOutput.model_validate(
        build_dashboard(
            await repository.list_results(),
            await repository.list_usage_events(),
            tracking_started_at=get_settings().usage_tracking_started_at,
        )
    )


@router.get("/results", response_model=AdminResultListOutput)
async def get_admin_results(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: date | None = None,
    date_to: date | None = None,
    result_code: str | None = None,
    nickname: str | None = None,
    mbti: str | None = None,
    character_id: str | None = None,
    tag: str | None = None,
    assessment_version: str | None = None,
    content_version: str | None = None,
    has_compatibility: bool | None = None,
    sort: Literal["newest", "oldest"] = "newest",
) -> AdminResultListOutput:
    events = await repository.list_usage_events()
    views, compatibility = usage_counts(events)
    results = filter_results(
        await repository.list_results(),
        date_from=date_from,
        date_to=date_to,
        result_code=result_code,
        nickname=nickname,
        mbti=mbti,
        character_id=character_id,
        tag=tag,
        assessment_version=assessment_version,
        content_version=content_version,
    )
    if has_compatibility is not None:
        results = [
            result
            for result in results
            if (compatibility[result.result_code] > 0) is has_compatibility
        ]
    results.sort(key=lambda result: result.created_at, reverse=sort == "newest")
    total = len(results)
    start = (page - 1) * page_size
    items = [
        result_summary(
            result,
            view_count=views[result.result_code],
            compatibility_count=compatibility[result.result_code],
        )
        for result in results[start : start + page_size]
    ]
    return AdminResultListOutput(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/results/{result_code}", response_model=AdminResultDetailOutput)
async def get_admin_result_detail(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    result_code: Annotated[str, Path(min_length=8, max_length=8)],
) -> AdminResultDetailOutput:
    result = await repository.get_result(result_code)
    if result is None:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
    events = await repository.list_usage_events()
    _, compatibility = usage_counts(events)
    views = [
        event
        for event in events
        if event.event_name == "result_viewed" and event.result_code == result_code
    ]
    participant = result.snapshot.get("participant")
    nickname = participant.get("nickname") if isinstance(participant, dict) else None
    return AdminResultDetailOutput(
        result_code=result.result_code,
        created_at=result.created_at,
        nickname=nickname if isinstance(nickname, str) else None,
        assessment_version=result.assessment_version,
        content_version=result.content_version,
        usage={
            "view_count": len(views),
            "last_viewed_at": max((event.occurred_at for event in views), default=None),
            "compatibility_count": compatibility[result_code],
        },
        snapshot=result.snapshot,
    )


@router.get("/payments", response_model=AdminPaymentListOutput)
async def get_admin_payments(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: date | None = None,
    date_to: date | None = None,
    order_id: str | None = None,
    user_id: Annotated[int | None, Query(ge=1)] = None,
    status: str | None = None,
    product_code: str | None = None,
) -> AdminPaymentListOutput:
    payments = filter_admin_payments(
        await repository.list_payments(),
        date_from=date_from,
        date_to=date_to,
        order_id=order_id,
        user_id=user_id,
        status=status,
        product_code=product_code,
    )
    payments.sort(key=lambda payment: payment.created_at, reverse=True)
    total = len(payments)
    start = (page - 1) * page_size
    return AdminPaymentListOutput(
        items=[
            AdminPaymentSummaryOutput(
                order_id=payment.order_id,
                user_id=payment.user_id,
                product_code=payment.product_code,
                product_name=payment.product_name,
                amount=payment.amount,
                currency=payment.currency,
                status=payment.status,
                report_code=payment.report_code,
                created_at=payment.created_at,
                approved_at=payment.approved_at,
            )
            for payment in payments[start : start + page_size]
        ],
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/payments/{order_id}", response_model=AdminPaymentOutput)
async def get_admin_payment_detail(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    order_id: Annotated[str, Path(min_length=16, max_length=32)],
) -> AdminPaymentOutput:
    payment = await repository.get_payment(order_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="결제 주문을 찾을 수 없습니다.")
    return AdminPaymentOutput.model_validate(payment, from_attributes=True)


@router.get("/users", response_model=AdminUserListOutput)
async def get_admin_users(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    user_id: Annotated[int | None, Query(ge=1)] = None,
) -> AdminUserListOutput:
    users = filter_admin_users(await repository.list_users(), user_id=user_id)
    users.sort(key=lambda user: user.created_at, reverse=True)
    total = len(users)
    start = (page - 1) * page_size
    return AdminUserListOutput(
        items=[
            AdminUserSummaryOutput(
                user_id=user.user_id,
                created_at=user.created_at,
                last_logged_in_at=user.last_logged_in_at,
                result_count=len(user.result_codes),
                approved_payment_count=user.approved_payment_count,
                total_paid_amount=user.total_paid_amount,
                report_count=len(user.report_codes),
            )
            for user in users[start : start + page_size]
        ],
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/users/{user_id}", response_model=AdminUserOutput)
async def get_admin_user_detail(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    user_id: Annotated[int, Path(ge=1)],
) -> AdminUserOutput:
    user = await repository.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return AdminUserOutput.model_validate(user, from_attributes=True)


@router.get("/paid-reports", response_model=AdminPaidReportListOutput)
async def get_admin_paid_reports(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: date | None = None,
    date_to: date | None = None,
    report_code: str | None = None,
    user_id: Annotated[int | None, Query(ge=1)] = None,
) -> AdminPaidReportListOutput:
    reports = filter_admin_paid_reports(
        await repository.list_paid_reports(),
        date_from=date_from,
        date_to=date_to,
        report_code=report_code,
        user_id=user_id,
    )
    reports.sort(key=lambda report: report.created_at, reverse=True)
    total = len(reports)
    start = (page - 1) * page_size
    return AdminPaidReportListOutput(
        items=[
            AdminPaidReportSummaryOutput(
                report_code=report.report_code,
                order_count=len(report.order_ids),
                user_ids=report.user_ids,
                mine_result_code=report.mine_result_code,
                partner_result_code=report.partner_result_code,
                mine_gender=report.mine_gender,
                partner_gender=report.partner_gender,
                prompt_version=report.prompt_version,
                profile_version=report.profile_version,
                model=report.model,
                created_at=report.created_at,
            )
            for report in reports[start : start + page_size]
        ],
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/paid-reports/{report_code}", response_model=AdminPaidReportOutput)
async def get_admin_paid_report_detail(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    report_code: Annotated[str, Path(min_length=8, max_length=32)],
) -> AdminPaidReportOutput:
    report = await repository.get_paid_report(report_code)
    if report is None:
        raise HTTPException(status_code=404, detail="유료 결과를 찾을 수 없습니다.")
    return AdminPaidReportOutput.model_validate(report, from_attributes=True)


@router.get("/analytics/results", response_model=ResultAnalyticsOutput)
async def get_result_analytics(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    date_from: date | None = None,
    date_to: date | None = None,
) -> ResultAnalyticsOutput:
    results = filter_results(await repository.list_results(), date_from=date_from, date_to=date_to)
    return ResultAnalyticsOutput.model_validate(build_result_analytics(results))


@router.get("/analytics/compatibility", response_model=CompatibilityAnalyticsOutput)
async def get_compatibility_analytics(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    date_from: date | None = None,
    date_to: date | None = None,
) -> CompatibilityAnalyticsOutput:
    results = filter_results(await repository.list_results(), date_from=date_from, date_to=date_to)
    events = filter_usage_events(
        await repository.list_usage_events(), date_from=date_from, date_to=date_to
    )
    return CompatibilityAnalyticsOutput.model_validate(
        build_compatibility_analytics(
            results,
            events,
            tracking_started_at=get_settings().usage_tracking_started_at,
        )
    )
