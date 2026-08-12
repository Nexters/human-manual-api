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
