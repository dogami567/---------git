#!/usr/bin/env python
"""
调试报告格式脚本
用于打印报告内容，帮助调试格式问题
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入需要测试的模块
from app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat


def debug_report_format():
    """调试报告格式"""
    print("开始调试报告格式...")
    
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
        template = report_service.create_project_report_template()
        
        # 准备数据
        data = {
            "project_name": "测试项目",
            "author": "测试用户",
            "date": "2023-11-15"
        }
        
        # 生成报告
        output_path = report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN,
            include_toc=True,
            include_code_highlighting=True
        )
        
        print(f"报告已生成: {output_path}")
        
        # 读取报告内容
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 打印报告内容
        print("\n===== 报告内容 =====\n")
        print(content)
        print("\n===== 报告内容结束 =====\n")
        
        # 检查特定内容
        print("\n===== 内容检查 =====\n")
        print(f"'项目报告' 存在: {'项目报告' in content}")
        print(f"'目录' 存在: {'目录' in content}")
        print(f"'项目概述' 存在: {'项目概述' in content}")
        print(f"'# 项目概述' 存在: {'# 项目概述' in content}")
        print(f"'## 项目概述' 存在: {'## 项目概述' in content}")
        print(f"'[项目概述]' 存在: {'[项目概述]' in content}")
        
        # 返回报告路径
        return output_path


if __name__ == "__main__":
    try:
        report_path = debug_report_format()
        print(f"\n调试完成，报告路径: {report_path}")
    except Exception as e:
        print(f"调试失败: {str(e)}")
        import traceback
        traceback.print_exc() 