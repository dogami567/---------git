import os
import sys
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient

from backend.app.main import app


class TestAPI(unittest.TestCase):
    """
    API测试类
    """
    
    def setUp(self):
        """
        测试前的设置
        """
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """
        测试根端点
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
    
    def test_health_endpoint(self):
        """
        测试健康检查端点
        """
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
    
    def test_api_status_endpoint(self):
        """
        测试API状态端点
        """
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "operational")


if __name__ == "__main__":
    unittest.main() 