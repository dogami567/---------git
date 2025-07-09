#!/usr/bin/env python
"""
测试报告服务的PDF导出功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    # 导入报告服务
    from backend.app.services.report_service import ReportService, ReportFormat, ReportSection, ReportTemplate

    # 创建一个简单的报告模板
    def create_test_template():
        """创建测试用的报告模板"""
        template = ReportTemplate("测试报告", "这是一个用于测试PDF导出功能的报告模板")
        
        # 添加标题部分
        template.add_section(ReportSection("标题", "# {{title}}", level=1))
        
        # 添加摘要部分
        template.add_section(ReportSection("摘要", "## 摘要\n\n{{summary}}", level=2))
        
        # 添加内容部分
        template.add_section(ReportSection("内容", "## 内容\n\n{{content}}", level=2))
        
        # 添加结论部分
        template.add_section(ReportSection("结论", "## 结论\n\n{{conclusion}}", level=2))
        
        return template

    # 测试PDF导出
    def test_pdf_export():
        """测试PDF导出功能"""
        print("开始测试PDF导出功能...")
        
        # 创建报告服务（不使用数据库）
        report_service = ReportService(None)
        
        # 创建报告模板
        template = create_test_template()
        
        # 准备数据
        data = {
            "title": "PDF导出功能测试报告",
            "summary": "这是一个测试报告，用于验证PDF导出功能是否正常工作。",
            "content": "这里是报告的主要内容。\n\n* 第一点\n* 第二点\n* 第三点",
            "conclusion": "测试成功完成，PDF导出功能正常工作。"
        }
        
        # 生成报告
        try:
            report_path = report_service.generate_report(
                template=template,
                data=data,
                format=ReportFormat.PDF,  # 注意：参数名是format而不是output_format
                output_path="test_report_service.pdf"
            )
            
            print(f"报告已生成: {report_path}")
            return True
        except Exception as e:
            print(f"生成报告时发生错误: {e}")
            raise
    
    # 执行测试
    if __name__ == "__main__":
        test_pdf_export()

except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已正确安装所有依赖项，并且可以访问报告服务模块。")
except Exception as e:
    print(f"测试过程中发生错误: {e}") 