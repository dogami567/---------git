import os
import sys
import unittest
import json
import tempfile
import shutil
from unittest import mock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.database import Base, engine, SessionLocal
from backend.app.models.component import Component, ComponentVersion
from backend.app.services.repository_service import RepositoryService


class TestComponentRepository(unittest.TestCase):
    """
    组件仓库API测试类
    """
    
    @classmethod
    def setUpClass(cls):
        """
        在所有测试前执行一次
        创建所有表和测试目录
        """
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 创建临时目录作为组件仓库
        cls.temp_dir = tempfile.mkdtemp()
        
        # 保存原始设置
        cls.original_repo_path = settings.COMPONENTS_REPO_LOCAL_PATH
        
        # 修改设置以使用临时目录
        settings.COMPONENTS_REPO_LOCAL_PATH = cls.temp_dir
    
    @classmethod
    def tearDownClass(cls):
        """
        在所有测试后执行一次
        删除所有表和测试目录
        """
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        
        # 恢复原始设置
        settings.COMPONENTS_REPO_LOCAL_PATH = cls.original_repo_path
        
        # 删除临时目录
        shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """
        每个测试前的设置
        """
        # 创建测试客户端
        self.client = TestClient(app)
        
        # 创建会话
        self.db = SessionLocal()
        
        # 创建测试组件
        self.test_component = Component(
            name="test-component",
            description="测试组件",
            version="1.0.0",
            category="测试",
            path=os.path.join(self.temp_dir, "components/test/test-component"),
            author="测试作者",
            tags="测试,组件",
            meta_info={"test_key": "test_value"}
        )
        
        # 添加到会话
        self.db.add(self.test_component)
        self.db.commit()
        self.db.refresh(self.test_component)
        
        # 创建测试组件版本
        self.test_version = ComponentVersion(
            component_id=self.test_component.id,
            version="1.0.0",
            commit_id="test-commit-id",
            changes="初始版本"
        )
        
        # 添加到会话
        self.db.add(self.test_version)
        self.db.commit()
    
    def tearDown(self):
        """
        每个测试后的清理
        """
        # 删除测试数据
        self.db.query(ComponentVersion).delete()
        self.db.query(Component).delete()
        self.db.commit()
        
        # 关闭会话
        self.db.close()
    
    @mock.patch.object(RepositoryService, 'setup_repository')
    def test_repository_status(self, mock_setup):
        """
        测试获取仓库状态
        """
        # 模拟仓库设置
        mock_setup.return_value = True
        
        # 模拟仓库属性
        with mock.patch.object(RepositoryService, 'repo_url', 'https://example.com/repo.git'), \
             mock.patch.object(RepositoryService, 'repo_branch', 'main'), \
             mock.patch.object(RepositoryService, 'repo', mock.MagicMock()):
            
            # 发送请求
            response = self.client.get("/api/components/repository/status")
            
            # 验证响应
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["initialized"])
            self.assertEqual(data["remote_url"], "https://example.com/repo.git")
            self.assertEqual(data["branch"], "main")
    
    @mock.patch.object(RepositoryService, 'setup_repository')
    def test_setup_repository(self, mock_setup):
        """
        测试设置仓库
        """
        # 模拟仓库设置
        mock_setup.return_value = True
        
        # 发送请求
        response = self.client.post("/api/components/repository/setup")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "仓库设置成功")
    
    @mock.patch.object(RepositoryService, 'commit_changes')
    def test_commit_changes(self, mock_commit):
        """
        测试提交更改
        """
        # 模拟提交
        mock_commit.return_value = "test-commit-id"
        
        # 发送请求
        response = self.client.post(
            "/api/components/repository/commit",
            json={"message": "测试提交"}
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["commit_id"], "test-commit-id")
        self.assertEqual(data["message"], "更改已提交: 测试提交")
    
    @mock.patch.object(RepositoryService, 'reset_changes')
    def test_reset_changes(self, mock_reset):
        """
        测试重置更改
        """
        # 模拟重置
        mock_reset.return_value = True
        
        # 发送请求
        response = self.client.post("/api/components/repository/reset")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "未提交的更改已重置")
    
    @mock.patch.object(RepositoryService, 'get_file_content')
    def test_get_file_content(self, mock_get_content):
        """
        测试获取文件内容
        """
        # 模拟文件内容
        mock_get_content.return_value = "测试文件内容"
        
        # 发送请求
        response = self.client.get("/api/components/repository/files/test/file.txt")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["path"], "test/file.txt")
        self.assertEqual(data["content"], "测试文件内容")
    
    @mock.patch.object(RepositoryService, 'get_file_history')
    def test_get_file_history(self, mock_get_history):
        """
        测试获取文件历史
        """
        # 模拟文件历史
        mock_get_history.return_value = [
            {
                "commit_id": "test-commit-id",
                "author": "Test Author <test@example.com>",
                "date": "2023-01-01T00:00:00",
                "message": "测试提交"
            }
        ]
        
        # 发送请求
        response = self.client.get("/api/components/repository/history/test/file.txt")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["path"], "test/file.txt")
        self.assertEqual(len(data["history"]), 1)
        self.assertEqual(data["history"][0]["commit_id"], "test-commit-id")
    
    def test_get_component_metadata(self):
        """
        测试获取组件元数据
        """
        # 发送请求
        response = self.client.get(f"/api/components/{self.test_component.id}/metadata")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.test_component.id)
        self.assertEqual(data["name"], "test-component")
        self.assertEqual(data["description"], "测试组件")
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["category"], "测试")
        self.assertEqual(data["author"], "测试作者")
        self.assertEqual(data["tags"], ["测试", "组件"])
        self.assertEqual(data["meta_info"], {"test_key": "test_value"})
        self.assertEqual(len(data["versions"]), 1)
        self.assertEqual(data["versions"][0]["version"], "1.0.0")
    
    def test_update_component_metadata(self):
        """
        测试更新组件元数据
        """
        # 准备更新数据
        update_data = {
            "description": "更新的测试组件",
            "tags": ["测试", "组件", "更新"],
            "meta_info": {
                "test_key": "updated_value",
                "new_key": "new_value"
            }
        }
        
        # 发送请求
        response = self.client.put(
            f"/api/components/{self.test_component.id}/metadata",
            json=update_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        
        # 验证数据库更新
        updated_component = self.db.query(Component).get(self.test_component.id)
        self.assertEqual(updated_component.description, "更新的测试组件")
        self.assertTrue("更新" in updated_component.tags)
    
    def test_search_components(self):
        """
        测试搜索组件
        """
        # 发送请求
        response = self.client.get("/api/components/search", params={"query": "测试"})
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["name"], "test-component")
    
    def test_get_component_categories(self):
        """
        测试获取组件类别
        """
        # 发送请求
        response = self.client.get("/api/components/categories")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "测试")
        self.assertEqual(data[0]["count"], 1)
    
    def test_get_component_tags(self):
        """
        测试获取组件标签
        """
        # 发送请求
        response = self.client.get("/api/components/tags")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        tag_names = [tag["name"] for tag in data]
        self.assertIn("测试", tag_names)
        self.assertIn("组件", tag_names)
    
    def test_get_component_authors(self):
        """
        测试获取组件作者
        """
        # 发送请求
        response = self.client.get("/api/components/authors")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "测试作者")
        self.assertEqual(data[0]["count"], 1)
    
    @mock.patch('backend.app.services.component_service.ComponentService.validate_component')
    def test_validate_component(self, mock_validate):
        """
        测试验证组件
        """
        # 模拟验证结果
        mock_validate.return_value = (True, ["验证通过"])
        
        # 发送请求
        response = self.client.post(f"/api/components/{self.test_component.id}/validate")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["component_id"], self.test_component.id)
        self.assertTrue(data["is_valid"])
        self.assertEqual(data["messages"], ["验证通过"])


if __name__ == "__main__":
    unittest.main() 