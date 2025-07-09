import os
import sys
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from backend.app.core.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    DatabaseException,
    ErrorHandlingMiddleware,
    ExternalServiceException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    UnauthorizedException,
    ValidationException,
    handle_exceptions,
    setup_exception_handlers,
)


class TestExceptions(unittest.TestCase):
    """
    异常处理测试类
    """
    
    def setUp(self):
        """
        测试前的设置
        """
        # 创建测试应用
        self.app = FastAPI()
        setup_exception_handlers(self.app)
        self.app.add_middleware(ErrorHandlingMiddleware)
        
        # 添加测试路由
        @self.app.get("/test-not-found")
        async def test_not_found():
            raise NotFoundException(detail="测试资源未找到")
        
        @self.app.get("/test-bad-request")
        async def test_bad_request():
            raise BadRequestException(detail="测试请求错误")
        
        @self.app.get("/test-unauthorized")
        async def test_unauthorized():
            raise UnauthorizedException()
        
        @self.app.get("/test-forbidden")
        async def test_forbidden():
            raise ForbiddenException()
        
        @self.app.get("/test-validation")
        async def test_validation():
            raise ValidationException(detail="测试数据验证失败")
        
        @self.app.get("/test-database")
        async def test_database():
            raise DatabaseException(detail="测试数据库错误")
        
        @self.app.get("/test-external-service")
        async def test_external_service():
            raise ExternalServiceException(detail="测试外部服务错误")
        
        @self.app.get("/test-conflict")
        async def test_conflict():
            raise ConflictException(detail="测试资源冲突")
        
        @self.app.get("/test-rate-limit")
        async def test_rate_limit():
            raise RateLimitException()
        
        @self.app.get("/test-generic")
        async def test_generic():
            # 故意引发除零错误
            # 注意：FastAPI的异常处理器会捕获这个错误
            # 并返回500状态码和通用错误消息
            1 / 0
            return {"message": "这段代码永远不会执行"}
        
        @self.app.get("/test-decorator")
        @handle_exceptions
        async def test_decorator():
            # 测试装饰器是否正确处理异常
            raise Exception("未处理的异常")
            return {"message": "这段代码永远不会执行"}
        
        # 创建测试客户端
        self.client = TestClient(self.app)
    
    def test_not_found_exception(self):
        """
        测试资源未找到异常
        """
        response = self.client.get("/test-not-found")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "测试资源未找到"})
    
    def test_bad_request_exception(self):
        """
        测试请求错误异常
        """
        response = self.client.get("/test-bad-request")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "测试请求错误"})
    
    def test_unauthorized_exception(self):
        """
        测试未授权异常
        """
        response = self.client.get("/test-unauthorized")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "未授权访问"})
    
    def test_forbidden_exception(self):
        """
        测试禁止访问异常
        """
        response = self.client.get("/test-forbidden")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "禁止访问"})
    
    def test_validation_exception(self):
        """
        测试数据验证异常
        """
        response = self.client.get("/test-validation")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {"detail": "测试数据验证失败"})
    
    def test_database_exception(self):
        """
        测试数据库异常
        """
        response = self.client.get("/test-database")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "测试数据库错误"})
    
    def test_external_service_exception(self):
        """
        测试外部服务异常
        """
        response = self.client.get("/test-external-service")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "测试外部服务错误"})
    
    def test_conflict_exception(self):
        """
        测试资源冲突异常
        """
        response = self.client.get("/test-conflict")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "测试资源冲突"})
    
    def test_rate_limit_exception(self):
        """
        测试请求速率限制异常
        """
        response = self.client.get("/test-rate-limit")
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json(), {"detail": "请求过于频繁，请稍后再试"})
    
    def test_generic_exception(self):
        """
        测试通用异常处理
        """
        # 使用try-except块捕获预期的异常
        try:
            response = self.client.get("/test-generic")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "服务器内部错误"})
        except Exception as e:
            self.fail(f"测试失败，未能正确处理除零错误: {e}")
    
    def test_decorator_exception(self):
        """
        测试异常处理装饰器
        """
        response = self.client.get("/test-decorator")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "服务器内部错误"})


if __name__ == "__main__":
    unittest.main() 