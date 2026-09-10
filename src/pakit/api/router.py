from fastapi import APIRouter

from pakit.api.routes import admin, assessments, auth, compatibility, health, romantic_reports

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(assessments.router)
api_router.include_router(assessments.results_router)
api_router.include_router(compatibility.router)
api_router.include_router(compatibility.ranking_router)
api_router.include_router(romantic_reports.router)
api_router.include_router(admin.router)
