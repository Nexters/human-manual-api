from fastapi import APIRouter

from pakit.api.routes import assessments, compatibility, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(assessments.router)
api_router.include_router(assessments.results_router)
api_router.include_router(compatibility.router)
