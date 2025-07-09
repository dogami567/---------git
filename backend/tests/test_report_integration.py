import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.app.api.endpoints.reports import router as reports_router
from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat
from backend.app.schemas.report import ReportFormatEnum, GenerateReportRequest, ProjectReportRequest, ReportFormattingOptions


class TestReportIntegration:
    """报告生成模块集成测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录作为报告目录
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # 使用补丁修改设置中的报告目录
        self.settings_patcher = patch('backend.app.services.report_service.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.REPORTS_DIR = self.temp_dir.name
        
        # 创建模拟数据库会话
        self.db = MagicMock()
        
        # 创建报告服务
        self.report_service = ReportService(self.db)
        
        # 创建FastAPI应用
        self.app = FastAPI()
        self.app.include_router(reports_router, prefix="/reports")
        
        # 创建测试客户端
        self.client = TestClient(self.app)
        
        # 模拟数据库依赖
        def override_get_db():
            return self.db
        
        self.app.dependency_overrides = {
            "get_db": override_get_db
        }
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 停止补丁
        self.settings_patcher.stop()
        
        # 清理临时目录
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
        
        # 验证内容
        assert "# 项目报告" in content
        assert "## 目录" in content
        assert "## 项目概述" in content
    
    @pytest.mark.skipif(not hasattr(pytest, "docx_available") or not pytest.docx_available, 
                       reason="python-docx not installed")
    def test_generate_docx_report(self):
        """测试生成DOCX报告（如果安装了python-docx）"""
        # 检查是否可以导入docx
        try:
            import docx
            
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
            
        except ImportError:
            pytest.skip("python-docx not installed")
    
    def test_generate_report_with_charts(self):
        """测试生成带有图表的报告"""
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
    
    def test_api_generate_report(self):
        """测试通过API生成报告"""
        # 准备请求数据
        request_data = {
            "data": {
                "project_name": "API测试项目",
                "author": "API测试用户",
                "date": "2023-11-15"
            },
            "format": "markdown",
            "formatting": {
                "include_toc": True,
                "include_code_highlighting": True
            }
        }
        
        # 发送请求
        with patch('backend.app.api.endpoints.reports.get_db', return_value=self.db):
            response = self.client.post("/reports/generate", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert "file_path" in response_data
        assert response_data["format"] == "markdown"
    
    def test_api_generate_project_report(self):
        """测试通过API生成项目报告"""
        # 准备请求数据
        request_data = {
            "project_id": 1,
            "include_code_samples": True,
            "include_api_docs": True,
            "include_database_schema": True,
            "format": "markdown",
            "formatting": {
                "include_toc": True,
                "include_code_highlighting": True
            }
        }
        
        # 发送请求
        with patch('backend.app.api.endpoints.reports.get_db', return_value=self.db):
            response = self.client.post("/reports/project", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert "file_path" in response_data
        assert response_data["format"] == "markdown"
    
    def test_api_get_default_template(self):
        """测试通过API获取默认模板"""
        # 发送请求
        with patch('backend.app.api.endpoints.reports.get_db', return_value=self.db):
            response = self.client.get("/reports/templates/default")
        
        # 验证响应
        assert response.status_code == 200
        template_data = response.json()
        assert template_data["title"] == "项目报告"
        assert "sections" in template_data
        assert len(template_data["sections"]) > 0 