import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional
import json
from datetime import datetime

from backend.app.core.config import settings

# 创建一个自定义日志格式化器
class CustomFormatter(logging.Formatter):
    """自定义日志格式化器，支持颜色和结构化输出"""
    
    # 定义颜色代码
    COLORS = {
        logging.DEBUG: "\033[38;5;246m",  # 灰色
        logging.INFO: "\033[38;5;39m",    # 蓝色
        logging.WARNING: "\033[38;5;226m", # 黄色
        logging.ERROR: "\033[38;5;196m",  # 红色
        logging.CRITICAL: "\033[48;5;196m\033[38;5;15m", # 红底白字
    }
    
    RESET = "\033[0m"
    
    def __init__(self, use_colors: bool = True):
        """
        初始化格式化器
        
        Args:
            use_colors: 是否使用彩色输出
        """
        self.use_colors = use_colors
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: 格式化后的日志字符串
        """
        log_message = super().format(record)
        
        if self.use_colors:
            color = self.COLORS.get(record.levelno)
            if color:
                log_message = f"{color}{log_message}{self.RESET}"
                
        return log_message


class JsonFormatter(logging.Formatter):
    """JSON格式的日志格式化器，用于文件日志"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        将日志记录格式化为JSON字符串
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: 格式化后的JSON字符串
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加自定义字段
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_data.update(record.extra_data)
            
        return json.dumps(log_data)


# 确保日志目录存在
def ensure_log_dir():
    """
    确保日志目录存在
    """
    if settings.LOG_FILE:
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            return True
    return False

# 创建日志处理器
def create_handlers():
    """
    创建日志处理器
    """
    handlers = []
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
    console_handler.setFormatter(CustomFormatter(use_colors=True))
    handlers.append(console_handler)
    
    # 如果设置了有效的日志文件路径，添加文件处理程序
    if ensure_log_dir():
        # 按大小轮转的文件处理器
        size_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_SIZE,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_format = "%(asctime)s - %(levelname)s - [%(name)s] - %(pathname)s:%(lineno)d - %(message)s"
        size_handler.setFormatter(logging.Formatter(file_format))
        handlers.append(size_handler)
        
        # 按时间轮转的文件处理器（每天一个文件）
        if settings.LOG_DAILY_FILE:
            time_handler = TimedRotatingFileHandler(
                settings.LOG_DAILY_FILE,
                when="midnight",
                interval=1,
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding="utf-8",
            )
            time_handler.setFormatter(logging.Formatter(file_format))
            handlers.append(time_handler)
    
    return handlers

# 配置根日志记录器
def setup_logging(
    log_level: str = settings.LOG_LEVEL,
    log_dir: Optional[Path] = None,
    service_name: str = "backend"
) -> logging.Logger:
    """
    设置全局日志配置
    
    Args:
        log_level: 日志级别
        log_dir: 日志目录
        service_name: 服务名称
        
    Returns:
        logging.Logger: 根日志记录器
    """
    # 设置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 移除已有的处理器
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter(use_colors=True))
    root_logger.addHandler(console_handler)
    
    # 如果提供了日志目录，添加文件处理器
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 常规日志文件
        log_file = log_dir / f"{service_name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JsonFormatter())
        root_logger.addHandler(file_handler)
        
        # 错误日志文件
        error_log_file = log_dir / f"{service_name}.error.log"
        error_file_handler = logging.FileHandler(error_log_file)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(JsonFormatter())
        root_logger.addHandler(error_file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # 创建应用程序日志记录器
    logger = logging.getLogger("app")
    
    logger.info(f"日志系统初始化完成，级别: {log_level}")
    return logger

# 创建中间件记录请求
class RequestLoggingMiddleware:
    """
    记录HTTP请求的中间件
    """
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("app.request")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        start_time = time.time()
        
        # 提取请求信息
        method = scope.get("method", "")
        path = scope.get("path", "")
        query_string = scope.get("query_string", b"").decode("utf-8")
        client = scope.get("client", ("", ""))[0]
        
        # 记录请求开始
        self.logger.debug(f"请求开始: {method} {path}?{query_string} from {client}")
        
        # 处理请求
        try:
            await self.app(scope, receive, send)
            # 计算处理时间
            process_time = time.time() - start_time
            # 记录请求完成
            self.logger.info(f"请求完成: {method} {path} - 处理时间: {process_time:.4f}s")
        except Exception as e:
            # 记录请求异常
            self.logger.error(f"请求异常: {method} {path} - {str(e)}")
            raise

# 创建一个提供额外上下文的日志记录器类
class ContextLogger:
    """
    带有上下文信息的日志记录器包装器
    """
    
    def __init__(self, logger: logging.Logger, context: Optional[Dict[str, Any]] = None):
        """
        初始化上下文日志记录器
        
        Args:
            logger: 基础日志记录器
            context: 上下文信息
        """
        self.logger = logger
        self.context = context or {}
    
    def with_context(self, **context) -> 'ContextLogger':
        """
        创建带有附加上下文的新日志记录器
        
        Args:
            **context: 上下文键值对
            
        Returns:
            ContextLogger: 新的上下文日志记录器
        """
        new_context = self.context.copy()
        new_context.update(context)
        return ContextLogger(self.logger, new_context)
    
    def _log(self, level: int, msg: str, *args, **kwargs):
        """
        通用日志方法
        
        Args:
            level: 日志级别
            msg: 日志消息
            *args: 格式化参数
            **kwargs: 关键字参数
        """
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        kwargs["extra"]["extra_data"] = self.context
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        """记录DEBUG级别日志"""
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """记录INFO级别日志"""
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """记录WARNING级别日志"""
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """记录ERROR级别日志"""
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """记录CRITICAL级别日志"""
        self._log(logging.CRITICAL, msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """记录异常信息"""
        kwargs.setdefault("exc_info", True)
        self._log(logging.ERROR, msg, *args, **kwargs)


# 创建AI服务专用日志记录器
def get_ai_logger() -> ContextLogger:
    """
    获取AI服务专用日志记录器
    
    Returns:
        ContextLogger: AI服务日志记录器
    """
    logger = logging.getLogger("app.ai_service")
    return ContextLogger(logger, {"service": "ai"})


# 默认日志记录器
logger = setup_logging() 