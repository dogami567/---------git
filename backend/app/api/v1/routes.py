"""
API v1路由

包含API v1版本的所有路由。
"""

from fastapi import APIRouter

from backend.app.api.endpoints import (
    users,
    competitions,
    subscriptions,
    components,
    ai_engine,
    reports,
)

# 创建API v1路由器
api_v1_router = APIRouter()

# 导入和包含其他路由模块
api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_v1_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_v1_router.include_router(components.router, prefix="/components", tags=["components"])
api_v1_router.include_router(ai_engine.router, prefix="/ai", tags=["ai"])
api_v1_router.include_router(reports.router, prefix="/reports", tags=["reports"])

@api_v1_router.get("/status")
async def get_status():
    """
    获取API状态
    """
    return {"status": "operational", "message": "API v1 is running", "version": "1.0"} 