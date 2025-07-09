import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """
    应用程序配置设置
    从环境变量中加载配置
    """
    # 应用程序设置
    APP_NAME: str = "大学生竞赛信息聚合与订阅平台"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:8080",
        "http://localhost",
        "http://127.0.0.1",
        "http://127.0.0.1:8080"
    ]

    # 数据库配置
    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # AI API密钥
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = None

    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"
    REPORTS_TEMPLATES_DIR: str = "reports/templates"
    REPORTS_CACHE_DIR: str = "reports/cache"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    LOG_DAILY_FILE: str = "./logs/app_daily.log"
    LOG_MAX_SIZE: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_REQUEST_BODY: bool = False  # 是否记录请求体
    LOG_RESPONSE_BODY: bool = False  # 是否记录响应体

    # 安全
    JWT_SECRET_KEY: str = "dev_jwt_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # Git仓库设置
    COMPONENTS_REPO_URL: Optional[str] = None
    COMPONENTS_REPO_BRANCH: str = "main"
    COMPONENTS_REPO_LOCAL_PATH: str = "./components_repo"

    # API配置
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "竞赛组件管理系统"

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:8000", "http://localhost:3000"]

    # JWT配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天

    # AI服务配置
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # 默认AI配置
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_AI_MAX_TOKENS: int = 1500
    DEFAULT_AI_TEMPERATURE: float = 0.7

    # AI错误处理配置
    AI_MAX_RETRIES: int = 3
    AI_RETRY_DELAY: int = 2  # 秒
    AI_TIMEOUT: int = 60  # 秒

    # 组件设置
    MAX_COMPONENT_NAME_LENGTH: int = 100
    MAX_COMPONENT_DESCRIPTION_LENGTH: int = 1000

    # AI引擎相关配置
    AI_ENGINE: str = "openai"

    @field_validator("ALLOWED_HOSTS")
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator("COMPONENTS_REPO_LOCAL_PATH", pre=True)
    def assemble_components_repo_local_path(cls, v: str, values: Dict[str, Any]) -> str:
        if v == "./components_repo":
            return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "components_repo")
        return v

    model_config = SettingsConfigDict(
        env_file=None,  # 禁用.env文件加载
        case_sensitive=True,
    )


# 创建全局设置实例
settings = Settings() 