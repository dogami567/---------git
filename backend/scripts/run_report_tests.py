#!/usr/bin/env python
"""
报告生成模块测试脚本
运行所有与报告生成相关的测试
"""

import os
import sys
import pytest
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("report_tests")


def run_report_tests():
    """运行所有报告模块的测试"""
    logger.info("开始运行报告模块测试...")
    
    # 检查依赖项
    try:
        import markdown
        pytest.markdown_available = True
        logger.info("检测到markdown库，将运行相关测试")
    except ImportError:
        pytest.markdown_available = False
        logger.warning("未检测到markdown库，部分测试将被跳过")
    
    try:
        import docx
        pytest.docx_available = True
        logger.info("检测到python-docx库，将运行相关测试")
    except ImportError:
        pytest.docx_available = False
        logger.warning("未检测到python-docx库，部分测试将被跳过")
    
    # 确定测试文件路径
    test_dir = Path(__file__).parent.parent / "tests"
    report_test_files = [
        test_dir / "test_report_formatter.py",
        test_dir / "test_report_integration.py",
        test_dir / "test_report_performance.py"
    ]
    
    # 过滤出存在的测试文件
    existing_test_files = [str(f) for f in report_test_files if f.exists()]
    
    if not existing_test_files:
        logger.error("未找到任何报告模块测试文件！")
        return 1
    
    logger.info(f"找到 {len(existing_test_files)} 个测试文件")
    
    # 运行测试
    logger.info("运行测试...")
    result = pytest.main(["-v"] + existing_test_files)
    
    if result == 0:
        logger.info("所有测试通过！")
    else:
        logger.error(f"测试失败，退出代码: {result}")
    
    return result


if __name__ == "__main__":
    sys.exit(run_report_tests()) 