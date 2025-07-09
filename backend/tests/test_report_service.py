import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat


class TestReportService:
    """报告生成服务测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建模拟数据库会话
        self.db = MagicMock()
        
        # 创建临时目录作为报告目录
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # 使用补丁修改设置中的报告目录
        self.settings_patcher = patch('backend.app.services.report_service.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.REPORTS_DIR = self.temp_dir.name
        
        # 创建报告服务
        self.report_service = ReportService(self.db)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 停止补丁
        self.settings_patcher.stop()
        
        # 清理临时目录
        self.temp_dir.cleanup()
    
    def test_create_project_report_template(self):
        """测试创建项目报告模板"""
        # 调用方法
        template = self.report_service.create_project_report_template()
        
        # 验证结果
        assert template.title == "项目报告"
        assert "本报告提供项目的详细信息和分析" in template.description
        assert len(template.sections) > 0
        assert "生成日期" in template.metadata
        assert "版本" in template.metadata
    
    def test_generate_markdown_report(self):
        """测试生成Markdown格式的报告"""
        # 创建简单模板
        template = ReportTemplate(
            title="测试报告",
            description="这是一个测试报告",
            metadata={"测试": "值"}
        )
        
        # 添加部分
        section = ReportSection(title="测试部分", content="这是测试内容")
        template.add_section(section)
        
        # 准备数据
        data = {"name": "测试名称", "value": 123}
        
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
        assert "# 测试报告" in content
        assert "这是一个测试报告" in content
        assert "测试部分" in content
        assert "这是测试内容" in content
    
    @pytest.mark.skipif(not hasattr(pytest, "docx_available") or not pytest.docx_available, 
                       reason="python-docx not installed")
    def test_generate_docx_report(self):
        """测试生成DOCX格式的报告（如果安装了python-docx）"""
        # 检查是否可以导入docx
        try:
            import docx
            # 创建简单模板
            template = ReportTemplate(
                title="测试报告",
                description="这是一个测试报告",
                metadata={"测试": "值"}
            )
            
            # 添加部分
            section = ReportSection(title="测试部分", content="这是测试内容")
            template.add_section(section)
            
            # 准备数据
            data = {"name": "测试名称", "value": 123}
            
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
    
    def test_report_section_to_markdown(self):
        """测试报告部分转换为Markdown"""
        # 创建部分
        section = ReportSection(title="测试标题", content="测试内容", level=2)
        
        # 添加子部分
        subsection = ReportSection(title="子标题", content="子内容", level=3)
        section.add_subsection(subsection)
        
        # 转换为Markdown
        markdown = section.to_markdown()
        
        # 验证结果
        assert "## 测试标题" in markdown
        assert "测试内容" in markdown
        assert "### 子标题" in markdown
        assert "子内容" in markdown
    
    def test_template_to_markdown(self):
        """测试模板转换为Markdown"""
        # 创建模板
        template = ReportTemplate(
            title="测试模板",
            description="测试描述",
            metadata={"键": "值"}
        )
        
        # 添加部分
        section = ReportSection(title="测试部分", content="测试内容")
        template.add_section(section)
        
        # 转换为Markdown
        markdown = template.to_markdown()
        
        # 验证结果
        assert "# 测试模板" in markdown
        assert "测试描述" in markdown
        assert "## 元数据" in markdown
        assert "**键**: 值" in markdown
        assert "# 测试部分" in markdown
        assert "测试内容" in markdown 