#!/usr/bin/env python
"""
报告服务独立测试脚本

此脚本用于测试报告服务的功能，不依赖数据库。
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入报告服务
from backend.app.services.report_service import ReportService, ReportFormat, ReportTemplate, ReportSection

def test_report_service():
    """测试报告服务功能"""
    print("开始测试报告服务...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"临时目录: {temp_dir}")
    
    # 创建模拟数据库会话
    db = MagicMock()
    
    # 创建报告服务
    with patch('backend.app.core.config.settings') as mock_settings:
        mock_settings.REPORTS_DIR = temp_dir
        report_service = ReportService(db)
        
        # 创建报告模板
        template = ReportTemplate("测试报告", "这是一个测试报告模板")
        
        # 添加报告部分
        template.add_section(ReportSection("标题", "# {{title}}", level=1))
        template.add_section(ReportSection("摘要", "## 摘要\n\n{{summary}}", level=2))
        template.add_section(ReportSection("内容", "## 内容\n\n{{content}}", level=2))
        template.add_section(ReportSection("结论", "## 结论\n\n{{conclusion}}", level=2))
        
        # 准备数据
        data = {
            "title": "测试报告标题",
            "summary": "这是一个测试报告的摘要。",
            "content": "这里是报告的主要内容。\n\n* 第一点\n* 第二点\n* 第三点",
            "conclusion": "这是测试报告的结论。"
        }
        
        # 生成Markdown报告
        print("生成Markdown报告...")
        md_path = report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN
        )
        
        print(f"Markdown报告已生成: {md_path}")
        
        # 读取报告内容
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            print("\n--- Markdown报告内容 ---")
            print(md_content[:500] + "..." if len(md_content) > 500 else md_content)
        
        # 生成DOCX报告
        try:
            print("\n生成DOCX报告...")
            docx_path = report_service.generate_report(
                template=template,
                data=data,
                format=ReportFormat.DOCX
            )
            print(f"DOCX报告已生成: {docx_path}")
        except Exception as e:
            print(f"生成DOCX报告时出错: {e}")
        
        # 生成PDF报告
        try:
            print("\n生成PDF报告...")
            pdf_path = report_service.generate_report(
                template=template,
                data=data,
                format=ReportFormat.PDF
            )
            print(f"PDF报告已生成: {pdf_path}")
        except Exception as e:
            print(f"生成PDF报告时出错: {e}")
        
        print("\n测试完成")
        return md_path

if __name__ == "__main__":
    test_report_service() 