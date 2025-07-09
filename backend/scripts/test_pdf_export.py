#!/usr/bin/env python
"""
测试PDF导出功能
用于测试报告生成服务的PDF导出功能
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入需要测试的模块
from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat


def test_pdf_export():
    """测试PDF导出功能"""
    print("开始测试PDF导出功能...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"临时目录: {temp_dir}")
    
    # 创建模拟数据库会话
    db = MagicMock()
    
    # 创建报告服务
    with patch('app.services.report_service.settings') as mock_settings:
        mock_settings.REPORTS_DIR = temp_dir
        report_service = ReportService(db)
        
        # 创建报告模板
        template = create_test_template()
        
        # 准备数据
        data = {
            "title": "PDF导出测试报告",
            "author": "测试用户",
            "date": "2025-07-07",
            "content": "这是测试报告的内容，包含一些格式化内容如**粗体**和*斜体*。",
            "code_example": "def hello_world():\n    print('Hello, World!')",
            "chart_data": {
                "labels": ["一月", "二月", "三月", "四月", "五月"],
                "values": [10, 20, 15, 25, 30]
            }
        }
        
        # 准备图表数据
        chart_data = {
            "charts": [
                {
                    "title": "测试图表",
                    "type": "bar",
                    "data": {
                        "labels": data["chart_data"]["labels"],
                        "datasets": [
                            {
                                "label": "数据集1",
                                "data": data["chart_data"]["values"],
                                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                                "borderColor": "rgba(75, 192, 192, 1)",
                                "borderWidth": 1
                            }
                        ]
                    },
                    "options": {
                        "scales": {
                            "y": {
                                "beginAtZero": True
                            }
                        }
                    }
                }
            ]
        }
        
        try:
            # 尝试生成PDF报告
            output_path = report_service.generate_report(
                template=template,
                data=data,
                format=ReportFormat.PDF,
                include_toc=True,
                include_code_highlighting=True,
                include_charts=True,
                chart_data=chart_data
            )
            
            print(f"PDF报告已生成: {output_path}")
            print(f"报告文件大小: {os.path.getsize(output_path)} 字节")
            print("PDF导出测试成功!")
            
            return output_path
            
        except ImportError as e:
            print(f"跳过PDF测试，原因: {str(e)}")
            
        except Exception as e:
            print(f"PDF导出测试失败: {str(e)}")
            import traceback
            traceback.print_exc()


def create_test_template() -> ReportTemplate:
    """创建测试模板"""
    template = ReportTemplate(
        title="{{title}}",
        description="测试PDF导出功能的模板",
        metadata={
            "作者": "{{author}}",
            "日期": "{{date}}"
        }
    )
    
    # 添加标题部分
    title_section = ReportSection(
        title="PDF导出功能测试",
        content="本报告用于测试PDF导出功能。\n\n{{content}}"
    )
    template.add_section(title_section)
    
    # 添加代码示例部分
    code_section = ReportSection(
        title="代码示例",
        content="以下是一个Python代码示例:\n\n```python\n{{code_example}}\n```"
    )
    template.add_section(code_section)
    
    # 添加图表部分
    chart_section = ReportSection(
        title="图表示例",
        content="以下是一个图表示例，展示了近几个月的数据趋势。"
    )
    template.add_section(chart_section)
    
    # 添加表格部分
    table_section = ReportSection(
        title="表格示例",
        content="| 月份 | 数值 |\n| ---- | ---- |\n"
                "| 一月 | 10 |\n"
                "| 二月 | 20 |\n"
                "| 三月 | 15 |\n"
                "| 四月 | 25 |\n"
                "| 五月 | 30 |"
    )
    template.add_section(table_section)
    
    return template


if __name__ == "__main__":
    try:
        report_path = test_pdf_export()
        if report_path:
            print(f"\n测试完成，报告路径: {report_path}")
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc() 