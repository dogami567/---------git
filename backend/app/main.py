import sys
from pathlib import Path

# 将项目根目录添加到 sys.path
# 这确保了无论从哪里启动应用，都可以正确解析 'backend.app' 这样的模块路径
# __file__ 是当前文件路径 (C:\...\大学生\backend\app\main.py)
# .parent.parent.parent 会上溯三级目录，到达项目根目录 C:\...\大学生
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from backend.app.api.routes import api_router
from backend.app.api.v1.routes import api_v1_router
from backend.app.core.config import settings
from backend.app.core.exceptions import ErrorHandlingMiddleware, setup_exception_handlers
from backend.app.core.logging import RequestLoggingMiddleware, logger
from backend.app.db.init_db import init_db

# 创建FastAPI应用
app = FastAPI(
    title="大学生竞赛信息聚合与订阅平台",
    description="为大学生提供竞赛信息聚合与订阅服务的平台",
    version="0.1.0",
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志记录中间件
app.add_middleware(RequestLoggingMiddleware)

# 添加错误处理中间件
app.add_middleware(ErrorHandlingMiddleware)

# 设置异常处理器
setup_exception_handlers(app)

# 包含API路由
app.include_router(api_router, prefix="/api")
app.include_router(api_v1_router, prefix="/api/v1")

# 添加根路由
@app.get("/")
async def root():
    """
    API根路由
    """
    return {
        "message": "欢迎使用大学生竞赛信息聚合与订阅平台API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    """
    logger.info("应用启动")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件
    """
    logger.info("应用关闭") 