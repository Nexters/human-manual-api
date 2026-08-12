from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pakit import __version__
from pakit.api.router import api_router
from pakit.api.routes.health import HealthResponse
from pakit.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        openapi_tags=[
            {
                "name": "테스트",
                "description": (
                    "'나 사용 설명서' 테스트의 답변 제출, 검증, 결과 분류 API입니다. "
                    "문항과 선택지의 고정 ID는 "
                    "`docs/assessment-identifiers.v1.json`을 기준으로 사용합니다."
                ),
            },
            {"name": "system", "description": "서버 상태 확인 API입니다."},
        ],
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    async def root_health() -> HealthResponse:
        return HealthResponse()

    return application


app = create_app()
