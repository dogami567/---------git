from backend.app.api.endpoints import (
    login,
    users,
    competitions,
    reports
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    competitions.router, prefix="/competitions", tags=["competitions"]
)
api_router.include_router(reports.router, prefix="/reports", tags=["reports"]) 