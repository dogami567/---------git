import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用程序配置设置
    从环境变量和.env文件中加载配置
    """
    # 应用程序设置
    APP_NAME: str = "大学生竞赛信息聚合与订阅平台"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # 数据库配置
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # AI API密钥
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None

    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    # 安全
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # Git仓库设置
    COMPONENTS_REPO_URL: str
    COMPONENTS_REPO_BRANCH: str = "main"
    COMPONENTS_REPO_LOCAL_PATH: str = "./components_repo"

    @field_validator("ALLOWED_HOSTS")
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# 创建全局设置实例
settings = Settings() 