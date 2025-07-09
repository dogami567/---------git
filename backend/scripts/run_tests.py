#!/usr/bin/env python
"""
运行测试的脚本
"""
import os
import sys
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def run_tests():
    """
    运行所有测试
    """
    # 发现并运行所有测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.join(os.path.dirname(__file__), "../tests"))
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == "__main__":
    print("运行测试...")
    success = run_tests()
    sys.exit(0 if success else 1) 