#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复文件编码问题

这个脚本用于修复项目中的文件编码问题，特别是删除空字节。
"""

import os
import sys
import glob
import codecs
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def fix_file_encoding(file_path):
    """
    修复文件编码问题
    
    Args:
        file_path: 文件路径
    """
    print(f"处理文件: {file_path}")
    
    try:
        # 尝试以不同编码读取文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"  成功以 {encoding} 编码读取")
                break
            except UnicodeDecodeError:
                print(f"  {encoding} 编码读取失败")
                continue
        
        if content is None:
            print(f"  无法以任何编码读取文件: {file_path}")
            return False
        
        # 移除空字节
        content = content.replace('\x00', '')
        
        # 以UTF-8编码写回文件
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"  文件已修复并以UTF-8编码保存: {file_path}")
        return True
    
    except Exception as e:
        print(f"  处理文件时出错: {e}")
        return False


def scan_directory(directory, extensions=None):
    """
    扫描目录中的所有文件
    
    Args:
        directory: 目录路径
        extensions: 文件扩展名列表，如果为None则处理所有文件
    
    Returns:
        list: 文件路径列表
    """
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if extensions is None or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files


def main():
    """
    主函数
    """
    # 获取项目根目录
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    # 定义要处理的文件模式
    patterns = [
        os.path.join(project_root, "app", "api", "endpoints", "*.py"),
        os.path.join(project_root, "app", "api", "v1", "*.py"),
        os.path.join(project_root, "app", "core", "*.py"),
        os.path.join(project_root, "app", "models", "*.py"),
        os.path.join(project_root, "app", "schemas", "*.py"),
        os.path.join(project_root, "app", "services", "*.py"),
    ]
    
    # 收集所有匹配的文件
    files_to_process = []
    for pattern in patterns:
        files_to_process.extend(glob.glob(pattern))
    
    print(f"找到 {len(files_to_process)} 个文件需要处理")
    
    # 处理每个文件
    success_count = 0
    for file_path in files_to_process:
        if fix_file_encoding(file_path):
            success_count += 1
    
    print(f"处理完成: {success_count}/{len(files_to_process)} 个文件成功修复")


if __name__ == "__main__":
    main() 