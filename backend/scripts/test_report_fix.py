#!/usr/bin/env python
"""
测试报告生成功能修复

这个脚本用于验证报告生成功能是否正常工作，特别是模板变量替换功能。
不依赖于完整的API测试，只测试核心功能。
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 检查依赖库是否可用
try:
    import markdown
    MARKDOWN_AVAILABLE = True
    print("Markdown库可用")
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Markdown库不可用")

try:
    import docx
    DOCX_AVAILABLE = True
    print("python-docx库可用")
except ImportError:
    DOCX_AVAILABLE = False
    print("python-docx库不可用")

try:
    from pygments import highlight
    PYGMENTS_AVAILABLE = True
    print("Pygments库可用")
except ImportError:
    PYGMENTS_AVAILABLE = False
    print("Pygments库不可用")

# 导入需要测试的模块
from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat
from backend.app.services.report_formatter_service import ReportFormatterService


def test_report_generation():
    """测试报告生成功能"""
    print("开始测试报告生成功能...")
    
    # 创建临时目录作为报告目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 设置报告目录
        reports_dir = Path(temp_dir)
        
        # 创建报告服务（不使用数据库）
        report_service = ReportService(db=None)
        report_service.reports_dir = reports_dir  # 手动设置报告目录
        
        # 创建模板
        template = report_service.create_project_report_template()
        
        # 准备数据
        data = {
            "project_name": "测试项目",
            "author": "测试用户",
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 生成报告
        output_path = report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN
        )
        
        # 验证结果
        if not os.path.exists(output_path):
            print(f"❌ 测试失败：报告文件不存在 - {output_path}")
            return False
        
        # 读取报告内容
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 验证内容
        checks = [
            ("项目报告", "标题"),
            ("目录", "目录"),
            ("测试项目", "项目名称替换"),
            ("测试用户", "作者替换")
        ]
        
        all_passed = True
        for text, desc in checks:
            if text in content:
                print(f"✅ 通过：{desc} - 找到文本 '{text}'")
            else:
                print(f"❌ 失败：{desc} - 未找到文本 '{text}'")
                all_passed = False
        
        # 打印报告内容（用于调试）
        print("\n报告内容预览（前500个字符）:")
        print("-" * 80)
        print(content[:500])
        print("-" * 80)
        
        return all_passed


def test_formatter_service():
    """测试格式化服务"""
    print("\n开始测试格式化服务...")
    
    # 创建格式化服务
    formatter_service = ReportFormatterService()
    
    # 测试Markdown格式化
    markdown_content = "# 标题\n\n## 子标题\n\n这是一些内容。\n\n```python\nprint('Hello, World!')\n```"
    try:
        formatted_markdown = formatter_service.format_markdown(
            markdown_content,
            include_toc=True,
            include_code_highlighting=MARKDOWN_AVAILABLE and PYGMENTS_AVAILABLE
        )
        print("Markdown格式化成功")
        print(f"格式化后内容预览:\n{formatted_markdown[:200]}...")
    except Exception as e:
        print(f"Markdown格式化失败: {str(e)}")
        raise
    
    # 测试表格生成
    try:
        table = formatter_service.add_table_to_markdown(
            headers=["列1", "列2", "列3"],
            rows=[["数据1", "数据2", "数据3"], ["数据4", "数据5", "数据6"]]
        )
        print("表格生成成功")
        print(f"表格内容:\n{table}")
    except Exception as e:
        print(f"表格生成失败: {str(e)}")
        raise
    
    # 测试代码块生成
    try:
        code_block = formatter_service.add_code_block_to_markdown(
            code="def hello():\n    print('Hello, World!')",
            language="python"
        )
        print("代码块生成成功")
        print(f"代码块内容:\n{code_block}")
    except Exception as e:
        print(f"代码块生成失败: {str(e)}")
        raise
    
    print("格式化服务测试完成")
    return True


if __name__ == "__main__":
    try:
        # 测试报告生成
        success = test_report_generation()
        
        # 测试格式化服务
        test_formatter_service()
        
        if success:
            print("\n✅ 所有测试通过！报告生成功能正常工作。")
        else:
            print("\n❌ 测试失败！报告生成功能存在问题。")
        
        sys.exit(0)
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 