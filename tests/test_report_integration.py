import os
import tempfile
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.db.database import get_db
from backend.app.services.report_service import ReportService, ReportFormat
from backend.app.core.config import settings


class TestReportIntegration:
    """报告集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # 模拟设置
        self.settings_patcher = patch('backend.app.core.config.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.REPORTS_DIR = self.temp_dir.name
        
        # 创建测试客户端
        self.client = TestClient(app)
        
        # 创建数据库会话
        self.db = next(get_db())
        
        # 创建报告服务
        self.report_service = ReportService(self.db)
        
        # 模拟数据库依赖
        def get_db():
            return self.db
        
        app.dependency_overrides[get_db] = get_db
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.settings_patcher.stop()
        self.temp_dir.cleanup()
    
    def test_generate_markdown_report(self):
        """测试生成Markdown报告"""
        # 创建模板
        template = self.report_service.create_project_report_template()
        
        # 准备数据
        data = {
            "project_name": "测试项目",
            "author": "测试用户",
            "date": "2023-11-15"
        }
        
        # 生成报告
        output_path = self.report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN
        )
        
        # 验证结果
        assert os.path.exists(output_path)
        assert output_path.endswith(".md")
        
        # 读取报告内容
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 验证内容 - 不依赖具体格式，只检查关键内容是否存在
        assert "项目报告" in content
        assert "目录" in content
        assert "项目概述" in content
        assert "技术栈" in content
        assert "系统架构" in content
        assert "测试项目" in content  # 验证数据替换
        assert "测试用户" in content  # 验证数据替换
        
        # 验证目录生成 - 检查是否包含链接，而不是具体格式
        assert "[项目概述]" in content or "项目概述](" in content
        assert "[技术栈]" in content or "技术栈](" in content
        assert "[系统架构]" in content or "系统架构](" in content
    
    def test_generate_docx_report(self):
        """测试生成DOCX报告"""
        # 检查python-docx是否可用
        try:
            import docx
        except ImportError:
            pytest.skip("python-docx库不可用，跳过测试")
        
        # 创建模板
        template = self.report_service.create_project_report_template()
        
        # 准备数据
        data = {
            "project_name": "测试项目",
            "author": "测试用户",
            "date": "2023-11-15"
        }
        
        # 生成报告
        output_path = self.report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.DOCX
        )
        
        # 验证结果
        assert os.path.exists(output_path)
        assert output_path.endswith(".docx")
        
        # 验证文件大小（简单检查文件是否有内容）
        assert os.path.getsize(output_path) > 0
    
    def test_generate_report_with_charts(self):
        """测试带有图表的报告生成"""
        # 创建模板
        template = self.report_service.create_project_report_template()
        
        # 准备数据
        data = {
            "project_name": "测试项目",
            "author": "测试用户",
            "date": "2023-11-15"
        }
        
        # 准备图表数据
        chart_data = {
            "charts": [
                {
                    "title": "测试图表",
                    "type": "bar",
                    "data": {
                        "categories": ["类别1", "类别2", "类别3"],
                        "series": {
                            "系列1": [10, 20, 30],
                            "系列2": [15, 25, 35]
                        }
                    }
                }
            ]
        }
        
        # 生成报告
        output_path = self.report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN,
            include_charts=True,
            chart_data=chart_data
        )
        
        # 验证结果
        assert os.path.exists(output_path)
    
    @pytest.mark.skip(reason="API路由尚未完全实现")
    def test_api_generate_report(self):
        """测试通过API生成报告"""
        # 准备请求数据
        request_data = {
            "title": "API测试报告",
            "description": "通过API生成的测试报告",
            "format": "markdown",
            "sections": [
                {
                    "title": "第一部分",
                    "content": "这是第一部分的内容",
                    "level": 1
                },
                {
                    "title": "第二部分",
                    "content": "这是第二部分的内容",
                    "level": 1,
                    "subsections": [
                        {
                            "title": "子部分",
                            "content": "这是子部分的内容",
                            "level": 2
                        }
                    ]
                }
            ],
            "data": {
                "project_name": "API测试项目",
                "author": "API测试用户"
            },
            "formatting_options": {
                "include_toc": True,
                "include_code_highlighting": True
            }
        }
        
        # 发送请求
        response = self.client.post("/api/v1/reports/generate", json=request_data)
        
        # 验证结果
        assert response.status_code == 200
        result = response.json()
        assert "report_path" in result
        assert os.path.exists(result["report_path"])
    
    @pytest.mark.skip(reason="API路由尚未完全实现")
    def test_api_generate_project_report(self):
        """测试通过API生成项目报告"""
        # 准备请求数据
        request_data = {
            "format": "markdown",
            "data": {
                "project_name": "API项目报告测试",
                "author": "API测试用户",
                "date": "2023-11-15"
            },
            "formatting_options": {
                "include_toc": True,
                "include_code_highlighting": True
            }
        }
        
        # 发送请求
        response = self.client.post("/api/v1/reports/project", json=request_data)
        
        # 验证结果
        assert response.status_code == 200
        result = response.json()
        assert "report_path" in result
        assert os.path.exists(result["report_path"])
    
    @pytest.mark.skip(reason="API路由尚未完全实现")
    def test_api_get_default_template(self):
        """测试获取默认模板"""
        # 发送请求
        response = self.client.get("/api/v1/reports/templates/default")
        
        # 验证结果
        assert response.status_code == 200
        result = response.json()
        assert "title" in result
        assert "description" in result
        assert "sections" in result
        assert len(result["sections"]) > 0 