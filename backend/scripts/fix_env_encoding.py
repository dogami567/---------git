#!/usr/bin/env python
"""
修复.env文件编码问题
将UTF-16编码的.env文件转换为UTF-8编码
"""

import os
import sys
import shutil
from pathlib import Path


def fix_env_encoding():
    """修复.env文件编码问题"""
    print("开始修复.env文件编码问题...")
    
    # 确定项目根目录
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    project_dir = backend_dir.parent
    
    # 确定.env文件路径
    env_file = project_dir / ".env"
    backup_file = project_dir / ".env.backup"
    temp_file = project_dir / ".env.utf8"
    
    if not env_file.exists():
        print(f"错误：找不到.env文件：{env_file}")
        return 1
    
    # 备份原始文件
    print(f"备份原始.env文件到：{backup_file}")
    shutil.copy2(env_file, backup_file)
    
    try:
        # 尝试以不同编码读取文件
        encodings = ["utf-16", "utf-16-le", "utf-16-be", "utf-8-sig", "utf-8", "gbk", "gb2312"]
        env_content = None
        
        for encoding in encodings:
            try:
                with open(env_file, "r", encoding=encoding) as f:
                    env_content = f.read()
                print(f"成功使用 {encoding} 编码读取.env文件")
                break
            except UnicodeDecodeError:
                continue
        
        if env_content is None:
            print("错误：无法使用任何已知编码读取.env文件")
            return 1
        
        # 以UTF-8编码写入新文件
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        
        # 替换原始文件
        os.replace(temp_file, env_file)
        
        print("成功将.env文件转换为UTF-8编码")
        return 0
    
    except Exception as e:
        print(f"错误：{e}")
        # 恢复备份
        if backup_file.exists():
            print("恢复备份文件...")
            os.replace(backup_file, env_file)
        return 1


if __name__ == "__main__":
    sys.exit(fix_env_encoding()) 