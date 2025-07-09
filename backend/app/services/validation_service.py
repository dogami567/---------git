import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import ValidationException


class ValidationService:
    """
    验证服务
    负责验证组件的质量和合规性
    """
    
    def __init__(self):
        """
        初始化验证服务
        """
        # 定义必需文件
        self.required_files = ["README.md", "metadata.json"]
        
        # 定义最小文档覆盖率（百分比）
        self.min_doc_coverage = 60
        
        # 定义最大代码复杂度
        self.max_complexity = 10
        
    def validate_component(self, component_path: str, files: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证组件
        
        Args:
            component_path: 组件目录路径
            files: 组件文件
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 验证消息列表)
        """
        messages = []
        
        # 验证组件结构
        structure_valid, structure_messages = self._validate_structure(component_path, files)
        messages.extend(structure_messages)
        
        # 验证元数据
        metadata_valid, metadata_messages = self._validate_metadata(component_path)
        messages.extend(metadata_messages)
        
        # 验证代码质量
        code_valid, code_messages = self._validate_code_quality(component_path, files)
        messages.extend(code_messages)
        
        # 验证文档
        doc_valid, doc_messages = self._validate_documentation(component_path, files)
        messages.extend(doc_messages)
        
        # 所有验证都通过才返回True
        is_valid = structure_valid and metadata_valid and code_valid and doc_valid
        
        return is_valid, messages
    
    def _validate_structure(self, component_path: str, files: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证组件结构
        
        Args:
            component_path: 组件目录路径
            files: 组件文件
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 验证消息列表)
        """
        messages = []
        is_valid = True
        
        # 检查必需文件
        for required_file in self.required_files:
            file_path = os.path.join(component_path, required_file)
            if not os.path.exists(file_path) and required_file not in files:
                is_valid = False
                messages.append(f"缺少必需文件: {required_file}")
        
        # 检查目录结构
        if not any(f.endswith(".py") or f.endswith(".js") or f.endswith(".ts") or f.endswith(".java") or f.endswith(".c") or f.endswith(".cpp") for f in os.listdir(component_path) if os.path.isfile(os.path.join(component_path, f))):
            if not any(f.endswith(".py") or f.endswith(".js") or f.endswith(".ts") or f.endswith(".java") or f.endswith(".c") or f.endswith(".cpp") for f in files):
                is_valid = False
                messages.append("组件必须包含至少一个源代码文件 (.py, .js, .ts, .java, .c, .cpp)")
        
        # 检查是否有测试文件
        has_test = False
        for root, _, filenames in os.walk(component_path):
            for filename in filenames:
                if filename.startswith("test_") or filename.endswith("_test.py") or filename.endswith(".test.js") or filename.endswith(".spec.js"):
                    has_test = True
                    break
        
        if not has_test:
            for filename in files:
                if filename.startswith("test_") or filename.endswith("_test.py") or filename.endswith(".test.js") or filename.endswith(".spec.js"):
                    has_test = True
                    break
        
        if not has_test:
            messages.append("警告: 未发现测试文件，建议添加测试")
        
        return is_valid, messages
    
    def _validate_metadata(self, component_path: str) -> Tuple[bool, List[str]]:
        """
        验证组件元数据
        
        Args:
            component_path: 组件目录路径
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 验证消息列表)
        """
        messages = []
        is_valid = True
        
        metadata_path = os.path.join(component_path, "metadata.json")
        
        if not os.path.exists(metadata_path):
            return False, ["缺少元数据文件: metadata.json"]
        
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                
            # 检查必需字段
            required_fields = ["name", "version", "category"]
            for field in required_fields:
                if field not in metadata or not metadata[field]:
                    is_valid = False
                    messages.append(f"元数据缺少必需字段: {field}")
            
            # 检查版本格式
            if "version" in metadata and metadata["version"]:
                version_pattern = r"^\d+\.\d+\.\d+$"
                if not re.match(version_pattern, metadata["version"]):
                    is_valid = False
                    messages.append(f"版本格式无效: {metadata['version']}，应为 x.y.z 格式")
            
            # 检查依赖项
            if "dependencies" in metadata and metadata["dependencies"]:
                if not isinstance(metadata["dependencies"], dict):
                    is_valid = False
                    messages.append("依赖项必须是字典格式")
                    
        except json.JSONDecodeError:
            is_valid = False
            messages.append("元数据文件不是有效的JSON格式")
        except Exception as e:
            is_valid = False
            messages.append(f"验证元数据时出错: {str(e)}")
            
        return is_valid, messages
    
    def _validate_code_quality(self, component_path: str, files: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证代码质量
        
        Args:
            component_path: 组件目录路径
            files: 组件文件
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 验证消息列表)
        """
        messages = []
        is_valid = True
        
        # 检查Python文件
        python_files = [f for f in os.listdir(component_path) if f.endswith(".py") and os.path.isfile(os.path.join(component_path, f))]
        python_files.extend([f for f in files if f.endswith(".py")])
        
        for py_file in python_files:
            if py_file in files:
                content = files[py_file].decode("utf-8")
            else:
                try:
                    with open(os.path.join(component_path, py_file), "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    is_valid = False
                    messages.append(f"读取文件 {py_file} 时出错: {str(e)}")
                    continue
            
            # 检查行长度
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if len(line.strip()) > 100:
                    messages.append(f"警告: {py_file}:{i+1} 行过长 ({len(line)} > 100)")
            
            # 检查函数长度
            functions = re.findall(r"def\s+\w+\([^)]*\):", content)
            for func in functions:
                func_name = re.search(r"def\s+(\w+)", func).group(1)
                # 简单估算函数长度
                func_start = content.find(func)
                next_func = content.find("def ", func_start + 1)
                if next_func == -1:
                    next_func = len(content)
                func_content = content[func_start:next_func]
                func_lines = func_content.count("\n")
                if func_lines > 50:
                    messages.append(f"警告: {py_file} 中的函数 {func_name} 过长 ({func_lines} 行)")
            
            # 检查类长度
            classes = re.findall(r"class\s+\w+[^:]*:", content)
            for cls in classes:
                cls_name = re.search(r"class\s+(\w+)", cls).group(1)
                # 简单估算类长度
                cls_start = content.find(cls)
                next_cls = content.find("class ", cls_start + 1)
                if next_cls == -1:
                    next_cls = len(content)
                cls_content = content[cls_start:next_cls]
                cls_lines = cls_content.count("\n")
                if cls_lines > 200:
                    messages.append(f"警告: {py_file} 中的类 {cls_name} 过长 ({cls_lines} 行)")
        
        # 检查JavaScript/TypeScript文件
        js_files = [f for f in os.listdir(component_path) if (f.endswith(".js") or f.endswith(".ts")) and os.path.isfile(os.path.join(component_path, f))]
        js_files.extend([f for f in files if f.endswith(".js") or f.endswith(".ts")])
        
        for js_file in js_files:
            if js_file in files:
                content = files[js_file].decode("utf-8")
            else:
                try:
                    with open(os.path.join(component_path, js_file), "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    is_valid = False
                    messages.append(f"读取文件 {js_file} 时出错: {str(e)}")
                    continue
            
            # 检查行长度
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if len(line.strip()) > 100:
                    messages.append(f"警告: {js_file}:{i+1} 行过长 ({len(line)} > 100)")
            
            # 检查函数长度
            functions = re.findall(r"function\s+\w+\([^)]*\)", content)
            functions.extend(re.findall(r"const\s+\w+\s*=\s*\([^)]*\)\s*=>", content))
            for func in functions:
                func_name = re.search(r"(function|const)\s+(\w+)", func).group(2)
                # 简单估算函数长度
                func_start = content.find(func)
                next_func = content.find("function ", func_start + 1)
                if next_func == -1:
                    next_func = content.find("const ", func_start + 1)
                if next_func == -1:
                    next_func = len(content)
                func_content = content[func_start:next_func]
                func_lines = func_content.count("\n")
                if func_lines > 50:
                    messages.append(f"警告: {js_file} 中的函数 {func_name} 过长 ({func_lines} 行)")
        
        return is_valid, messages
    
    def _validate_documentation(self, component_path: str, files: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证文档
        
        Args:
            component_path: 组件目录路径
            files: 组件文件
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 验证消息列表)
        """
        messages = []
        is_valid = True
        
        # 检查README.md
        readme_path = os.path.join(component_path, "README.md")
        if readme_path in files:
            readme_content = files["README.md"].decode("utf-8")
        elif os.path.exists(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    readme_content = f.read()
            except Exception as e:
                is_valid = False
                messages.append(f"读取README.md时出错: {str(e)}")
                readme_content = ""
        else:
            is_valid = False
            messages.append("缺少README.md文件")
            readme_content = ""
        
        # 检查README内容
        if readme_content:
            # 检查标题
            if not re.search(r"^#\s+\w+", readme_content, re.MULTILINE):
                messages.append("警告: README.md缺少标题")
                
            # 检查章节
            if not re.search(r"^##\s+\w+", readme_content, re.MULTILINE):
                messages.append("警告: README.md缺少章节标题")
                
            # 检查长度
            if len(readme_content) < 100:
                messages.append("警告: README.md内容过短")
        
        # 检查代码文档
        python_files = [f for f in os.listdir(component_path) if f.endswith(".py") and os.path.isfile(os.path.join(component_path, f))]
        python_files.extend([f for f in files if f.endswith(".py")])
        
        for py_file in python_files:
            if py_file in files:
                content = files[py_file].decode("utf-8")
            else:
                try:
                    with open(os.path.join(component_path, py_file), "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    continue
            
            # 检查模块文档
            if not re.search(r'"""[^"]+"""', content):
                messages.append(f"警告: {py_file} 缺少模块级文档字符串")
            
            # 检查函数文档
            functions = re.findall(r"def\s+\w+\([^)]*\):", content)
            total_funcs = len(functions)
            documented_funcs = 0
            
            for func in functions:
                func_name = re.search(r"def\s+(\w+)", func).group(1)
                func_start = content.find(func)
                next_line_start = content.find("\n", func_start) + 1
                if next_line_start < len(content) and content[next_line_start:].strip().startswith('"""'):
                    documented_funcs += 1
            
            if total_funcs > 0:
                doc_coverage = (documented_funcs / total_funcs) * 100
                if doc_coverage < self.min_doc_coverage:
                    messages.append(f"警告: {py_file} 的函数文档覆盖率低 ({doc_coverage:.1f}% < {self.min_doc_coverage}%)")
        
        return is_valid, messages 