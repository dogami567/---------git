#!/usr/bin/env python
"""
环境测试脚本
用于验证所有依赖是否正确安装
"""

import sys
import importlib
from typing import List, Tuple


def check_dependencies() -> List[Tuple[str, bool]]:
    """检查关键依赖是否已正确安装"""
    dependencies = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "dotenv",
        "openai",
        "langchain",
        "tiktoken",
    ]
    
    results = []
    for dep in dependencies:
        try:
            # 处理包名中的连字符
            module_name = dep.replace("-", "_")
            importlib.import_module(module_name)
            results.append((dep, True))
        except ImportError:
            results.append((dep, False))
    
    return results


def main():
    """主函数"""
    print("正在检查开发环境...")
    print(f"Python 版本: {sys.version}")
    
    results = check_dependencies()
    all_installed = all(success for _, success in results)
    
    print("\n依赖检查结果:")
    for dep, success in results:
        status = "✅ 已安装" if success else "❌ 未安装"
        print(f"{dep}: {status}")
    
    if all_installed:
        print("\n✨ 所有依赖已成功安装，开发环境设置完成！")
    else:
        print("\n⚠️ 部分依赖未安装，请检查requirements.txt并重新安装。")
        sys.exit(1)


if __name__ == "__main__":
    main() 