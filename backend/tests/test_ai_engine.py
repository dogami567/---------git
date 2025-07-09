import os
import sys
import unittest
import json
from unittest import mock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import Base, engine, SessionLocal
from backend.app.models.ai_engine import AIModel, PersonalizationTemplate, PersonalizationLog
from backend.app.services.ai_service import AIService
from backend.app.services.code_personalization_service import CodePersonalizationService
from backend.app.services.template_initialization import TemplateInitializationService
from backend.app.core.exceptions import (
    AIServiceException, 
    AIModelNotFoundException,
    AIModelInactiveException,
    AITemplateNotFoundException,
    AITemplateInactiveException,
    AIProviderException,
    AIRateLimitException
)


class TestAIEngine(unittest.TestCase):
    """
    AI引擎API测试类
    """
    
    @classmethod
    def setUpClass(cls):
        """
        在所有测试前执行一次
        创建所有表
        """
        # 创建所有表
        Base.metadata.create_all(bind=engine)
    
    @classmethod
    def tearDownClass(cls):
        """
        在所有测试后执行一次
        删除所有表
        """
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
    
    def setUp(self):
        """
        每个测试前执行
        设置测试客户端和数据库会话
        """
        self.client = TestClient(app)
        self.db = SessionLocal()
        
        # 清理已有数据
        self._cleanup_data()
        
        # 创建测试数据
        self._create_test_data()
    
    def tearDown(self):
        """
        每个测试后执行
        关闭数据库会话
        """
        self._cleanup_data()
        self.db.close()
    
    def _cleanup_data(self):
        """
        清理测试数据
        """
        self.db.query(PersonalizationLog).delete()
        self.db.query(PersonalizationTemplate).delete()
        self.db.query(AIModel).delete()
        self.db.commit()
    
    def _create_test_data(self):
        """
        创建测试数据
        """
        # 创建测试AI模型
        test_model = AIModel(
            name="Test GPT Model",
            provider="OpenAI",
            model_id="gpt-3.5-turbo",
            api_key_name="TEST_OPENAI_API_KEY",
            is_active=True,
            max_tokens=2048,
            temperature=0.5
        )
        self.db.add(test_model)
        self.db.commit()
        self.db.refresh(test_model)
        self.test_model_id = test_model.id
        
        # 创建测试模板
        test_template = PersonalizationTemplate(
            name="Test Python Comments",
            description="测试Python注释模板",
            prompt_template="请为以下Python代码添加注释：\n{code}",
            task_type="add_comments",
            parameters={"language": "python", "comment_style": "simple"},
            is_active=True,
            ai_model_id=test_model.id
        )
        self.db.add(test_template)
        self.db.commit()
        self.db.refresh(test_template)
        self.test_template_id = test_template.id
    
    def test_list_models(self):
        """
        测试获取AI模型列表
        """
        response = self.client.get("/api/ai/models")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("items", data)
        self.assertGreater(len(data["items"]), 0)
        self.assertEqual(data["items"][0]["name"], "Test GPT Model")
    
    def test_get_model(self):
        """
        测试获取单个AI模型详情
        """
        response = self.client.get(f"/api/ai/models/{self.test_model_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["name"], "Test GPT Model")
        self.assertEqual(data["provider"], "OpenAI")
    
    def test_get_nonexistent_model(self):
        """
        测试获取不存在的AI模型
        """
        response = self.client.get("/api/ai/models/9999")
        self.assertEqual(response.status_code, 404)
    
    def test_list_templates(self):
        """
        测试获取模板列表
        """
        response = self.client.get("/api/ai/templates")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("items", data)
        self.assertGreater(len(data["items"]), 0)
        self.assertEqual(data["items"][0]["name"], "Test Python Comments")
    
    def test_get_template(self):
        """
        测试获取单个模板详情
        """
        response = self.client.get(f"/api/ai/templates/{self.test_template_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["name"], "Test Python Comments")
        self.assertEqual(data["task_type"], "add_comments")
    
    @mock.patch.object(AIService, "personalize_code")
    def test_personalize_code(self, mock_personalize_code):
        """
        测试代码个性化API
        """
        # 模拟AI服务返回值
        mock_personalize_code.return_value = (
            "# 这是个性化后的代码\ndef hello():\n    print('Hello, world!')",
            PersonalizationLog(id=1, processing_time=0.5, tokens_used=100)
        )
        
        # 发送请求
        response = self.client.post(
            "/api/ai/personalize",
            json={
                "template_id": self.test_template_id,
                "input_code": "def hello():\n    print('Hello, world!')",
                "parameters": {"language": "python"}
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("output_code", data)
        self.assertEqual(data["output_code"], "# 这是个性化后的代码\ndef hello():\n    print('Hello, world!')")
    
    def test_settings(self):
        """
        测试获取个性化设置
        """
        response = self.client.get("/api/ai/settings")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("models", data)
        self.assertIn("task_types", data)
    
    @mock.patch.object(CodePersonalizationService, "add_comments")
    def test_add_comments(self, mock_add_comments):
        """
        测试添加注释API
        """
        # 模拟代码个性化服务返回值
        mock_add_comments.return_value = "# 这是添加了注释的代码\ndef hello():\n    # 打印问候语\n    print('Hello, world!')"
        
        # 发送请求
        response = self.client.post(
            "/api/ai/code/add-comments",
            json={
                "code": "def hello():\n    print('Hello, world!')",
                "language": "python",
                "style": "simple"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("output_code", data)
        self.assertIn("# 这是添加了注释的代码", data["output_code"])
    
    @mock.patch.object(CodePersonalizationService, "rename_variables")
    def test_rename_variables(self, mock_rename_variables):
        """
        测试重命名变量API
        """
        # 模拟代码个性化服务返回值
        mock_rename_variables.return_value = "def say_hello():\n    greeting_message = 'Hello, world!'\n    print(greeting_message)"
        
        # 发送请求
        response = self.client.post(
            "/api/ai/code/rename-variables",
            json={
                "code": "def hello():\n    msg = 'Hello, world!'\n    print(msg)",
                "language": "python",
                "style": "snake_case"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("output_code", data)
        self.assertIn("greeting_message", data["output_code"])
    
    @mock.patch.object(AIService, "initialize_defaults")
    def test_initialize_defaults(self, mock_initialize_defaults):
        """
        测试初始化默认设置API
        """
        # 模拟AI服务返回值
        mock_initialize_defaults.return_value = {
            "success": True,
            "models_created": 1,
            "templates_created": 8,
            "message": "成功初始化默认模型和模板"
        }
        
        # 发送请求
        response = self.client.post("/api/ai/initialize")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["models_created"], 1)
        self.assertEqual(data["templates_created"], 8)
    
    def test_task_types(self):
        """
        测试获取任务类型API
        """
        response = self.client.get("/api/ai/code/task-types")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("task_types", data)
        self.assertIsInstance(data["task_types"], dict)
    
    @mock.patch.object(AIService, "personalize_code")
    def test_personalize_code_error_handling(self, mock_personalize_code):
        """
        测试AI个性化代码时的错误处理
        """
        # 模拟各种异常情况
        exceptions = [
            (AIModelNotFoundException("模型不存在"), 404),
            (AIModelInactiveException("模型未激活"), 400),
            (AITemplateNotFoundException("模板不存在"), 404),
            (AITemplateInactiveException("模板未激活"), 400),
            (AIProviderException("不支持的提供商"), 502),
            (AIRateLimitException("调用频率超限"), 429),
            (AIServiceException("通用错误"), 500)
        ]
        
        for exception, status_code in exceptions:
            mock_personalize_code.side_effect = exception
            
            # 发送请求
            response = self.client.post(
                "/api/ai/personalize",
                json={
                    "template_id": self.test_template_id,
                    "input_code": "def hello(): pass",
                    "parameters": {}
                }
            )
            
            self.assertEqual(response.status_code, status_code)
            self.assertIn("detail", response.json())
    
    @mock.patch.object(AIService, "personalize_code")
    def test_retry_mechanism(self, mock_personalize_code):
        """
        测试重试机制
        """
        # 先抛出两次异常，然后返回正常结果
        mock_personalize_code.side_effect = [
            AIRateLimitException("第一次调用失败"),
            AIRateLimitException("第二次调用失败"),
            ("# 这是第三次调用成功后的代码\ndef hello():\n    print('Hello')", 
             PersonalizationLog(id=1, processing_time=1.0, tokens_used=50))
        ]
        
        # 发送请求
        response = self.client.post(
            "/api/ai/personalize",
            json={
                "template_id": self.test_template_id,
                "input_code": "def hello(): pass",
                "parameters": {}
            }
        )
        
        # 验证重试后最终成功
        self.assertEqual(response.status_code, 200)
        self.assertIn("output_code", response.json())
        
        # 确认调用了三次
        self.assertEqual(mock_personalize_code.call_count, 3)
    
    @mock.patch.object(CodePersonalizationService, "add_comments")
    def test_invalid_parameters(self, mock_add_comments):
        """
        测试无效参数处理
        """
        # 设置模拟函数抛出异常
        mock_add_comments.side_effect = AIServiceException("代码参数无效")
        
        # 发送请求，提供无效的代码
        response = self.client.post(
            "/api/ai/code/add-comments",
            json={
                "code": "",  # 空代码
                "language": "python",
                "style": "simple"
            }
        )
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertIn("代码参数无效", response.json()["detail"])
    
    @mock.patch.object(AIService, "initialize_defaults")
    def test_initialize_fail(self, mock_initialize_defaults):
        """
        测试初始化默认设置失败
        """
        # 设置模拟函数返回失败结果
        mock_initialize_defaults.return_value = {
            "success": False,
            "error": "初始化失败，数据库错误"
        }
        
        # 发送请求
        response = self.client.post("/api/ai/initialize")
        
        # 虽然操作失败，但API端点仍返回成功状态码
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], False)
        self.assertIn("error", data)
    
    def test_template_lifecycle(self):
        """
        测试模板的完整生命周期
        """
        # 1. 创建新模板
        template_data = {
            "name": "Test Template Lifecycle",
            "description": "测试模板生命周期",
            "prompt_template": "请对下面的{language}代码进行重构：\n{code}",
            "task_type": "refactor",
            "example_input": "function test() { var x = 1; return x; }",
            "example_output": "function test() {\n  const x = 1;\n  return x;\n}",
            "is_active": True,
            "ai_model_id": self.test_model_id,
            "parameters": {"quality": "high", "style": "modern"}
        }
        
        response = self.client.post("/api/ai/templates", json=template_data)
        self.assertEqual(response.status_code, 201)
        created_template = response.json()
        template_id = created_template["id"]
        
        # 2. 获取模板详情
        response = self.client.get(f"/api/ai/templates/{template_id}")
        self.assertEqual(response.status_code, 200)
        template = response.json()
        self.assertEqual(template["name"], template_data["name"])
        
        # 3. 更新模板
        update_data = {
            "description": "更新后的描述",
            "is_active": False
        }
        response = self.client.put(f"/api/ai/templates/{template_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        updated_template = response.json()
        self.assertEqual(updated_template["description"], "更新后的描述")
        self.assertEqual(updated_template["is_active"], False)
        
        # 4. 删除模板
        response = self.client.delete(f"/api/ai/templates/{template_id}")
        self.assertEqual(response.status_code, 204)
        
        # 5. 确认已删除
        response = self.client.get(f"/api/ai/templates/{template_id}")
        self.assertEqual(response.status_code, 404)
    
    def test_model_validation(self):
        """
        测试模型验证
        """
        # 尝试创建无效的模型（缺少必填字段）
        invalid_model = {
            "name": "Invalid Model"
            # 缺少其他必填字段
        }
        
        response = self.client.post("/api/ai/models", json=invalid_model)
        self.assertEqual(response.status_code, 422)  # 验证失败
        
        # 尝试创建名称重复的模型
        duplicate_model = {
            "name": "Test GPT Model",  # 与setUp中创建的模型同名
            "provider": "OpenAI",
            "model_id": "gpt-3.5-turbo-duplicate",
            "api_key_name": "TEST_API_KEY",
            "max_tokens": 1000,
            "temperature": 0.5
        }
        
        response = self.client.post("/api/ai/models", json=duplicate_model)
        self.assertNotEqual(response.status_code, 201)  # 应该不是201 Created
    
    def test_filter_templates_by_task_type(self):
        """
        测试按任务类型筛选模板
        """
        # 创建不同任务类型的模板
        for task_type in ["add_comments", "rename_variables", "optimize_code"]:
            template = PersonalizationTemplate(
                name=f"Test Template {task_type}",
                description=f"测试{task_type}模板",
                prompt_template=f"请执行{task_type}任务：\n{{code}}",
                task_type=task_type,
                is_active=True,
                ai_model_id=self.test_model_id
            )
            self.db.add(template)
        
        self.db.commit()
        
        # 测试筛选
        response = self.client.get("/api/ai/templates?task_type=add_comments")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证筛选结果
        found_task_types = [template["task_type"] for template in data["items"]]
        self.assertTrue(all(task_type == "add_comments" for task_type in found_task_types))
    
    @mock.patch.object(CodePersonalizationService, "get_task_types")
    def test_task_types_error(self, mock_get_task_types):
        """
        测试获取任务类型失败的情况
        """
        mock_get_task_types.side_effect = Exception("获取任务类型失败")
        
        response = self.client.get("/api/ai/code/task-types")
        self.assertEqual(response.status_code, 500)
    
    def test_settings_endpoint(self):
        """
        测试个性化设置端点
        """
        response = self.client.get("/api/ai/settings")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("models", data)
        self.assertIn("task_types", data)
        
        # 验证模型信息
        models = data["models"]
        self.assertTrue(len(models) > 0)
        self.assertEqual(models[0]["name"], "Test GPT Model")
    
    def test_endpoint_security(self):
        """
        测试API端点的安全性
        """
        # 测试使用无效的模板ID
        response = self.client.post(
            "/api/ai/personalize",
            json={
                "template_id": 9999,  # 不存在的ID
                "input_code": "def test(): pass",
                "parameters": {}
            }
        )
        self.assertEqual(response.status_code, 404)
        
        # 测试使用过大的代码输入
        large_code = "def test(): pass\n" * 10000  # 非常大的代码
        response = self.client.post(
            "/api/ai/code/add-comments",
            json={
                "code": large_code,
                "language": "python",
                "style": "simple"
            }
        )
        # 应该返回错误，而不是服务器崩溃
        self.assertNotEqual(response.status_code, 200)
    
    @mock.patch.object(AIService, "personalize_code")
    def test_error_logging(self, mock_personalize_code):
        """
        测试错误日志记录
        """
        # 设置模拟函数抛出异常
        mock_personalize_code.side_effect = AIServiceException("测试错误")
        
        # 发送请求
        self.client.post(
            "/api/ai/personalize",
            json={
                "template_id": self.test_template_id,
                "input_code": "def hello(): pass",
                "parameters": {}
            }
        )
        
        # 此测试主要验证错误日志记录功能
        # 正常情况下应该验证日志内容，但单元测试中难以直接验证
        # 这里仅验证API不会因异常而崩溃
        
        # 验证模拟函数被调用
        mock_personalize_code.assert_called_once()


if __name__ == "__main__":
    unittest.main() 