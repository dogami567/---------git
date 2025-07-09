from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from functools import wraps
import logging
from typing import Callable, Type, Dict, Any, Optional
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import asyncio

from backend.app.core.logging import logger


class BaseAppException(Exception):
    """应用基础异常类"""
    
    def __init__(self, message: str, code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(BaseAppException):
    """数据库异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)


class AuthenticationException(BaseAppException):
    """认证异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)


class AuthorizationException(BaseAppException):
    """授权异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)


class ResourceNotFoundException(BaseAppException):
    """资源未找到异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, details)


class ValidationException(BaseAppException):
    """验证异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)


class ComponentException(BaseAppException):
    """组件异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)


class ReportGenerationException(BaseAppException):
    """报告生成异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)


class AIEngineException(BaseAppException):
    """AI引擎异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)


class NotAuthenticatedException(BaseAppException):
    """未认证异常"""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "认证失败"
    headers = {"WWW-Authenticate": "Bearer"}


class NotAuthorizedException(BaseAppException):
    """未授权异常"""
    status_code = status.HTTP_403_FORBIDDEN
    detail = "权限不足"


class NotFoundException(BaseAppException):
    """资源未找到异常"""
    status_code = status.HTTP_404_NOT_FOUND
    detail = "请求的资源不存在"


class DuplicateException(BaseAppException):
    """重复资源异常"""
    status_code = status.HTTP_409_CONFLICT
    detail = "资源已存在"


class AIServiceException(BaseAppException):
    """AI服务异常"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "AI服务调用失败"


class AIModelNotFoundException(AIServiceException):
    """AI模型未找到异常"""
    status_code = status.HTTP_404_NOT_FOUND
    detail = "指定的AI模型不存在"


class AIModelInactiveException(AIServiceException):
    """AI模型未激活异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "指定的AI模型未激活"


class AITemplateNotFoundException(AIServiceException):
    """AI模板未找到异常"""
    status_code = status.HTTP_404_NOT_FOUND
    detail = "指定的个性化模板不存在"


class AITemplateInactiveException(AIServiceException):
    """AI模板未激活异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "指定的个性化模板未激活"


class AIProviderException(AIServiceException):
    """AI提供商异常"""
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "AI提供商服务调用失败"


class AIRateLimitException(AIProviderException):
    """AI接口调用频率限制异常"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "AI接口调用频率超限"


class AITokenLimitException(AIServiceException):
    """AI模型令牌超限异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "输入或输出令牌数量超出模型限制"


class AIContextLengthException(AIServiceException):
    """AI模型上下文长度超限异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "输入上下文长度超出模型限制"


class AIInvalidParameterException(AIServiceException):
    """AI服务参数无效异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "提供的参数无效或缺少必要参数"


class AIAuthenticationException(AIServiceException):
    """AI服务认证异常"""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "AI服务认证失败，请检查API密钥"


class AIServiceUnavailableException(AIServiceException):
    """AI服务不可用异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "AI服务暂时不可用，请稍后重试"


class AITimeoutException(AIServiceException):
    """AI服务超时异常"""
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    detail = "AI服务请求超时"


class AppException(Exception):
    """
    应用程序自定义异常基类
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class RepositoryException(AppException):
    """
    仓库操作相关异常
    """
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class BadRequestException(AppException):
    """
    错误请求异常
    """
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ExternalServiceException(AppException):
    """
    外部服务异常
    """
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class ConflictException(AppException):
    """
    资源冲突异常（例如，尝试创建已存在的资源）
    """
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class RateLimitException(AppException):
    """
    请求速率限制异常
    """
    def __init__(self, detail: str = "请求过于频繁，请稍后再试"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    错误处理中间件
    捕获所有未处理的异常并返回适当的响应
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"未处理的异常: {str(e)}")
            
            if isinstance(e, AppException):
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
                
            # 处理其他未知异常
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "服务器内部错误"}
            )


def handle_exceptions(func):
    """
    一个装饰器，用于捕获和处理路由函数中的异常，并返回统一的JSON响应。
    能够智能处理同步和异步函数。
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            logger.debug(f"调用路由: {func.__name__}")
            if asyncio.iscoroutinefunction(func):
                response = await func(*args, **kwargs)
            else:
                response = func(*args, **kwargs)
            logger.debug(f"路由 {func.__name__} 调用成功")
            return response
        except HTTPException as e:
            logger.error(f"HTTP异常: {e.status_code}: {e.detail}")
            # 直接重新抛出HTTPException，让FastAPI的处理器来处理
            raise
        except Exception as e:
            # 对于所有其他未预料的异常，记录日志并返回500错误
            logger.error(f"在路由 '{func.__name__}' 中发生未处理的异常: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部发生未知错误。"
            )
    return wrapper


def setup_exception_handlers(app: FastAPI):
    """
    设置全局异常处理器
    """
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"请求验证错误: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )
        
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"HTTP异常: {str(exc)}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
        
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(f"应用程序异常: {str(exc)}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
        
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"未处理的异常: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "服务器内部错误"}
        )

    @app.exception_handler(BaseAppException)
    async def api_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        logger.error(f"API异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.error(f"验证异常: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "message": "数据验证失败",
                "details": exc.errors(),
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
        logger.error(f"数据库异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(request: Request, exc: AuthenticationException) -> JSONResponse:
        logger.error(f"认证异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(request: Request, exc: AuthorizationException) -> JSONResponse:
        logger.error(f"授权异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(ResourceNotFoundException)
    async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundException) -> JSONResponse:
        logger.error(f"资源未找到异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
        logger.error(f"验证异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(ComponentException)
    async def component_exception_handler(request: Request, exc: ComponentException) -> JSONResponse:
        logger.error(f"组件异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(ReportGenerationException)
    async def report_generation_exception_handler(request: Request, exc: ReportGenerationException) -> JSONResponse:
        logger.error(f"报告生成异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(AIEngineException)
    async def ai_engine_exception_handler(request: Request, exc: AIEngineException) -> JSONResponse:
        logger.error(f"AI引擎异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(NotAuthenticatedException)
    async def not_authenticated_exception_handler(request: Request, exc: NotAuthenticatedException) -> JSONResponse:
        logger.error(f"未认证异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "WWW-Authenticate": exc.headers["WWW-Authenticate"]}
        )

    @app.exception_handler(NotAuthorizedException)
    async def not_authorized_exception_handler(request: Request, exc: NotAuthorizedException) -> JSONResponse:
        logger.error(f"未授权异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
        logger.error(f"资源未找到异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(DuplicateException)
    async def duplicate_exception_handler(request: Request, exc: DuplicateException) -> JSONResponse:
        logger.error(f"重复资源异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(request: Request, exc: AIServiceException) -> JSONResponse:
        logger.error(f"AI服务异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AIModelNotFoundException)
    async def ai_model_not_found_exception_handler(request: Request, exc: AIModelNotFoundException) -> JSONResponse:
        logger.error(f"AI模型未找到异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(AIModelInactiveException)
    async def ai_model_inactive_exception_handler(request: Request, exc: AIModelInactiveException) -> JSONResponse:
        logger.error(f"AI模型未激活异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(AITemplateNotFoundException)
    async def ai_template_not_found_exception_handler(request: Request, exc: AITemplateNotFoundException) -> JSONResponse:
        logger.error(f"AI模板未找到异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(AITemplateInactiveException)
    async def ai_template_inactive_exception_handler(request: Request, exc: AITemplateInactiveException) -> JSONResponse:
        logger.error(f"AI模板未激活异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(AIProviderException)
    async def ai_provider_exception_handler(request: Request, exc: AIProviderException) -> JSONResponse:
        logger.error(f"AI提供商异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AIRateLimitException)
    async def ai_rate_limit_exception_handler(request: Request, exc: AIRateLimitException) -> JSONResponse:
        logger.error(f"AI接口调用频率限制异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AITokenLimitException)
    async def ai_token_limit_exception_handler(request: Request, exc: AITokenLimitException) -> JSONResponse:
        logger.error(f"AI模型令牌超限异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AIContextLengthException)
    async def ai_context_length_exception_handler(request: Request, exc: AIContextLengthException) -> JSONResponse:
        logger.error(f"AI模型上下文长度超限异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AIInvalidParameterException)
    async def ai_invalid_parameter_exception_handler(request: Request, exc: AIInvalidParameterException) -> JSONResponse:
        logger.error(f"AI服务参数无效异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AIAuthenticationException)
    async def ai_authentication_exception_handler(request: Request, exc: AIAuthenticationException) -> JSONResponse:
        logger.error(f"AI服务认证异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AIServiceUnavailableException)
    async def ai_service_unavailable_exception_handler(request: Request, exc: AIServiceUnavailableException) -> JSONResponse:
        logger.error(f"AI服务不可用异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(AITimeoutException)
    async def ai_timeout_exception_handler(request: Request, exc: AITimeoutException) -> JSONResponse:
        logger.error(f"AI服务超时异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.code
            }
        )

    @app.exception_handler(ReportGenerationException)
    async def report_generation_exception_handler(request: Request, exc: ReportGenerationException) -> JSONResponse:
        logger.error(f"报告生成异常: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "code": exc.code
            }
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(f"应用程序异常: {str(exc)}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RepositoryException)
    async def repository_exception_handler(request: Request, exc: RepositoryException) -> JSONResponse:
        logger.error(f"仓库操作相关异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.status_code
            }
        )

    @app.exception_handler(BadRequestException)
    async def bad_request_exception_handler(request: Request, exc: BadRequestException) -> JSONResponse:
        logger.error(f"错误请求异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(ExternalServiceException)
    async def external_service_exception_handler(request: Request, exc: ExternalServiceException) -> JSONResponse:
        logger.error(f"外部服务异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.status_code
            }
        )

    @app.exception_handler(ConflictException)
    async def conflict_exception_handler(request: Request, exc: ConflictException) -> JSONResponse:
        logger.error(f"资源冲突异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RateLimitException)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitException) -> JSONResponse:
        """
        处理速率限制异常
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        ) 