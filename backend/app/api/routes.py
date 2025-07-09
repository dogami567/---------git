from fastapi import APIRouter

from backend.app.api.endpoints import users, competitions, subscriptions, components, ai_engine, reports, simple_reports

# 创建API路由器
api_router = APIRouter()

# 导入和包含其他路由模块
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(components.router, prefix="/components", tags=["components"])
api_router.include_router(ai_engine.router, prefix="/ai", tags=["ai"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(simple_reports.router, prefix="/simple-reports", tags=["reports"])

@api_router.get("/status")
async def get_status():
    """
    获取API状态
    """
    return {"status": "operational", "message": "API is running"} 