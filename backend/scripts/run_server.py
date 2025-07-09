#!/usr/bin/env python
"""
启动FastAPI服务器的脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import start

if __name__ == "__main__":
    print("启动FastAPI服务器...")
    start() 