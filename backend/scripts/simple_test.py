#!/usr/bin/env python
"""
简单测试脚本
用于验证报告生成模块的基本功能，不依赖任何项目模块
"""

import os
import tempfile


class ReportSection:
    """报告部分类"""
    def __init__(self, title, content, level=1):
        self.title = title
        self.content = content
        self.level = level
        self.subsections = []
    
    def add_subsection(self, subsection):
        """添加子部分"""
        self.subsections.append(subsection)
        return subsection


class ReportTemplate:
    """报告模板类"""
    def __init__(self, title, description=None, metadata=None):
        self.title = title
        self.description = description or ""
        self.metadata = metadata or {}
        self.sections = []
    
    def add_section(self, section):
        """添加部分"""
        self.sections.append(section)
        return section


def generate_markdown_report(template, data):
    """生成Markdown报告"""
    # 创建临时文件
    temp_file = tempfile.mktemp(suffix=".md")
    
    with open(temp_file, "w", encoding="utf-8") as f:
        # 写入标题
        f.write(f"# {template.title}\n\n")
        
        # 写入描述
        if template.description:
            f.write(f"{template.description}\n\n")
        
        # 写入元数据
        if template.metadata:
            f.write("## 元数据\n\n")
            for key, value in template.metadata.items():
                f.write(f"- **{key}**: {value}\n")
            f.write("\n")
        
        # 写入目录
        f.write("## 目录\n\n")
        for section in template.sections:
            f.write(f"- {section.title}\n")
            for subsection in section.subsections:
                f.write(f"  - {subsection.title}\n")
        f.write("\n")
        
        # 写入内容
        for section in template.sections:
            f.write(f"## {section.title}\n\n")
            
            # 替换数据变量
            content = section.content
            for key, value in data.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
            
            f.write(f"{content}\n\n")
            
            # 写入子部分
            for subsection in section.subsections:
                f.write(f"### {subsection.title}\n\n")
                
                # 替换数据变量
                subcontent = subsection.content
                for key, value in data.items():
                    subcontent = subcontent.replace(f"{{{{{key}}}}}", str(value))
                
                f.write(f"{subcontent}\n\n")
    
    return temp_file


def run_simple_test():
    """运行简单测试"""
    print("开始运行简单测试...")
    
    # 创建模板
    template = ReportTemplate(
        title="项目报告",
        description="这是一个项目详细报告",
        metadata={"生成时间": "2023-11-15"}
    )
    
    # 添加部分
    overview_section = ReportSection(
        title="项目概述",
        content="项目名称: {{project_name}}\n作者: {{author}}\n日期: {{date}}"
    )
    template.add_section(overview_section)
    
    # 添加子部分
    overview_section.add_subsection(
        ReportSection(
            title="项目目标",
            content="这是项目 {{project_name}} 的目标描述。",
            level=2
        )
    )
    
    # 添加另一个部分
    details_section = ReportSection(
        title="详细信息",
        content="这里包含项目的详细信息。"
    )
    template.add_section(details_section)
    
    # 准备数据
    data = {
        "project_name": "测试项目",
        "author": "测试用户",
        "date": "2023-11-15"
    }
    
    # 生成报告
    output_path = generate_markdown_report(template, data)
    
    # 验证结果
    if os.path.exists(output_path):
        print(f"报告生成成功: {output_path}")
        
        # 读取报告内容
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 验证内容
        if "# 项目报告" in content and "## 项目概述" in content:
            print("报告内容验证通过")
            print("\n报告内容预览:")
            print("=" * 40)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("=" * 40)
        else:
            print("报告内容验证失败")
    else:
        print("报告生成失败")
    
    print("简单测试完成")


if __name__ == "__main__":
    run_simple_test() 