from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from pakit import __version__
from pakit.api.admin_auth import require_admin
from pakit.api.router import api_router
from pakit.api.routes.health import HealthResponse
from pakit.core.config import ALLOWED_CORS_ORIGINS, get_settings
from pakit.web.admin import render_admin_page
from pakit.web.result_map import render_result_map


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        root_path="",
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        openapi_tags=[
            {
                "name": "Test",
                "description": (
                    "'나 사용 설명서' 테스트의 답변 제출, 검증, 결과 조회 API입니다. "
                    "문항과 선택지의 고정 ID는 "
                    "`docs/assessment-identifiers.v1.json`을 기준으로 사용합니다."
                ),
            },
            {
                "name": "Compatibility",
                "description": "두 테스트 결과를 비교하는 친구 궁합 API입니다.",
            },
            {
                "name": "Admin",
                "description": "인증된 운영자만 사용하는 읽기 전용 결과·통계 API입니다.",
            },
            {"name": "system", "description": "서버 상태 확인 API입니다."},
        ],
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(ALLOWED_CORS_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def prevent_admin_caching(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        if request.url.path == "/admin" or request.url.path.startswith(("/admin/", "/api/admin/")):
            response.headers["Cache-Control"] = "no-store"
        return response

    application.mount(
        "/assets",
        StaticFiles(directory=Path(__file__).parent / "static"),
        name="assets",
    )
    application.mount(
        "/test",
        StaticFiles(directory=Path(__file__).parent / "static" / "test", html=True),
        name="test-page",
    )
    application.mount(
        "/compatibility-test",
        StaticFiles(
            directory=Path(__file__).parent / "static" / "compatibility_test",
            html=True,
        ),
        name="compatibility-test-page",
    )
    application.include_router(api_router, prefix=settings.api_prefix)

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    async def root_health() -> HealthResponse:
        return HealthResponse()

    @application.get("/result-map", response_class=HTMLResponse, include_in_schema=False)
    async def result_map_page() -> HTMLResponse:
        """결과 문구 검토용 조합 지도 페이지 (내부용)."""
        return HTMLResponse(render_result_map())

    @application.get(
        "/admin",
        response_class=HTMLResponse,
        include_in_schema=False,
        dependencies=[Depends(require_admin)],
    )
    async def admin_dashboard_page() -> HTMLResponse:
        return HTMLResponse(render_admin_page("dashboard"), headers={"Cache-Control": "no-store"})

    @application.get(
        "/admin/results",
        response_class=HTMLResponse,
        include_in_schema=False,
        dependencies=[Depends(require_admin)],
    )
    async def admin_results_page() -> HTMLResponse:
        return HTMLResponse(render_admin_page("results"), headers={"Cache-Control": "no-store"})

    @application.get(
        "/admin/results/{result_code}",
        response_class=HTMLResponse,
        include_in_schema=False,
        dependencies=[Depends(require_admin)],
    )
    async def admin_result_detail_page(result_code: str) -> HTMLResponse:
        return HTMLResponse(
            render_admin_page("detail", result_code), headers={"Cache-Control": "no-store"}
        )

    @application.get(
        "/admin/analytics",
        response_class=HTMLResponse,
        include_in_schema=False,
        dependencies=[Depends(require_admin)],
    )
    async def admin_analytics_page() -> HTMLResponse:
        return HTMLResponse(render_admin_page("analytics"), headers={"Cache-Control": "no-store"})

    return application


app = create_app()
