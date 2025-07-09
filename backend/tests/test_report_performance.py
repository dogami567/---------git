import os
import time
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat


class TestReportPerformance:
    """报告生成模块性能测试类"""
    
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
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 停止补丁
        self.settings_patcher.stop()
        
        # 清理临时目录
        self.temp_dir.cleanup()
    
    def test_markdown_report_generation_time(self):
        """测试Markdown报告生成时间"""
        # 创建模板
        template = self.report_service.create_project_report_template()
        
        # 准备数据
        data = {
            "project_name": "性能测试项目",
            "author": "性能测试用户",
            "date": "2023-11-15"
        }
        
        # 测量生成时间
        start_time = time.time()
        output_path = self.report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN
        )
        end_time = time.time()
        
        # 计算生成时间
        generation_time = end_time - start_time
        
        # 验证结果
        assert os.path.exists(output_path)
        assert generation_time < 1.0  # 生成时间应小于1秒
        
        # 打印性能信息
        print(f"Markdown报告生成时间: {generation_time:.4f}秒")
    
    @pytest.mark.skipif(not hasattr(pytest, "docx_available") or not pytest.docx_available, 
                       reason="python-docx not installed")
    def test_docx_report_generation_time(self):
        """测试DOCX报告生成时间（如果安装了python-docx）"""
        # 检查是否可以导入docx
        try:
            import docx
            
            # 创建模板
            template = self.report_service.create_project_report_template()
            
            # 准备数据
            data = {
                "project_name": "性能测试项目",
                "author": "性能测试用户",
                "date": "2023-11-15"
            }
            
            # 测量生成时间
            start_time = time.time()
            output_path = self.report_service.generate_report(
                template=template,
                data=data,
                format=ReportFormat.DOCX
            )
            end_time = time.time()
            
            # 计算生成时间
            generation_time = end_time - start_time
            
            # 验证结果
            assert os.path.exists(output_path)
            assert generation_time < 2.0  # DOCX生成时间应小于2秒
            
            # 打印性能信息
            print(f"DOCX报告生成时间: {generation_time:.4f}秒")
            
        except ImportError:
            pytest.skip("python-docx not installed")
    
    def test_large_report_generation(self):
        """测试大型报告生成性能"""
        # 创建大型模板
        template = ReportTemplate(
            title="大型报告测试",
            description="这是一个用于测试大型报告生成性能的模板",
            metadata={"测试类型": "性能测试"}
        )
        
        # 添加多个部分
        for i in range(20):
            section = ReportSection(
                title=f"部分 {i+1}",
                content=f"这是部分 {i+1} 的内容，包含了大量文本用于测试报告生成性能。" * 10
            )
            
            # 添加子部分
            for j in range(5):
                subsection = ReportSection(
                    title=f"子部分 {i+1}.{j+1}",
                    content=f"这是子部分 {i+1}.{j+1} 的内容，包含了大量文本用于测试报告生成性能。" * 5,
                    level=2
                )
                section.add_subsection(subsection)
            
            template.add_section(section)
        
        # 准备数据
        data = {
            "project_name": "大型性能测试项目",
            "author": "性能测试用户",
            "date": "2023-11-15"
        }
        
        # 测量生成时间
        start_time = time.time()
        output_path = self.report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN
        )
        end_time = time.time()
        
        # 计算生成时间
        generation_time = end_time - start_time
        
        # 验证结果
        assert os.path.exists(output_path)
        
        # 获取文件大小
        file_size = os.path.getsize(output_path) / 1024  # KB
        
        # 打印性能信息
        print(f"大型报告生成时间: {generation_time:.4f}秒")
        print(f"大型报告文件大小: {file_size:.2f} KB")
    
    def test_concurrent_report_generation(self):
        """测试并发报告生成性能"""
        import concurrent.futures
        
        # 创建模板
        template = self.report_service.create_project_report_template()
        
        # 准备数据
        data = {
            "project_name": "并发测试项目",
            "author": "并发测试用户",
            "date": "2023-11-15"
        }
        
        # 定义生成报告的函数
        def generate_report(index):
            start_time = time.time()
            output_path = self.report_service.generate_report(
                template=template,
                data={**data, "index": index},
                format=ReportFormat.MARKDOWN
            )
            end_time = time.time()
            return end_time - start_time, output_path
        
        # 并发生成多个报告
        num_reports = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_reports) as executor:
            futures = [executor.submit(generate_report, i) for i in range(num_reports)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 分析结果
        generation_times = [result[0] for result in results]
        output_paths = [result[1] for result in results]
        
        # 验证结果
        for output_path in output_paths:
            assert os.path.exists(output_path)
        
        # 计算平均生成时间
        avg_generation_time = sum(generation_times) / len(generation_times)
        
        # 打印性能信息
        print(f"并发报告生成平均时间: {avg_generation_time:.4f}秒")
        print(f"并发报告生成总时间: {sum(generation_times):.4f}秒") 