from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pakit import __version__
from pakit.api.router import api_router
from pakit.api.routes.health import HealthResponse
from pakit.core.config import get_settings


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
            {"name": "system", "description": "서버 상태 확인 API입니다."},
        ],
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
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
    application.include_router(api_router, prefix=settings.api_prefix)

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    async def root_health() -> HealthResponse:
        return HealthResponse()

    return application


app = create_app()
