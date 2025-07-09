"""
调试报告格式化功能

用于测试报告格式化和变量替换功能。
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat


def test_variable_replacement():
    """测试变量替换功能"""
    print("开始测试变量替换功能...")
    
    # 创建报告服务
    report_service = ReportService()
    
    # 创建测试模板
    template = ReportTemplate(
        title="测试模板 - {{project_name}}",
        description="这是一个测试模板，用于测试变量替换功能。作者：{{author}}",
        metadata={
            "生成日期": "{{date}}",
            "版本": "1.0.0"
        }
    )
    
    # 添加测试部分
    section1 = ReportSection(
        title="第一部分：{{section1_title}}",
        content=(
            "这是第一部分的内容，包含多种格式的变量：\n"
            "- 双大括号格式：{{variable1}}\n"
            "- 单大括号格式：{variable2}\n"
            "- 美元符号格式：${variable3}\n"
        )
    )
    template.add_section(section1)
    
    section2 = ReportSection(
        title="第二部分：嵌套变量",
        content=(
            "这是第二部分的内容，测试嵌套变量：\n"
            "- 嵌套变量1：{{nested.value1}}\n"
            "- 嵌套变量2：{nested.value2}\n"
            "- 嵌套变量3：${nested.value3}\n"
        )
    )
    template.add_section(section2)
    
    # 准备测试数据
    data = {
        "project_name": "变量替换测试项目",
        "author": "测试作者",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "section1_title": "变量测试",
        "variable1": "这是双大括号变量的值",
        "variable2": "这是单大括号变量的值",
        "variable3": "这是美元符号变量的值",
        "nested.value1": "这是嵌套变量1的值",
        "nested.value2": "这是嵌套变量2的值",
        "nested.value3": "这是嵌套变量3的值"
    }
    
    # 获取模板内容
    template_content = template.to_markdown()
    print("\n原始模板内容:")
    print("-" * 80)
    print(template_content)
    print("-" * 80)
    
    # 替换变量
    report_content = report_service._replace_variables(template_content, data)
    print("\n替换变量后的内容:")
    print("-" * 80)
    print(report_content)
    print("-" * 80)
    
    # 检查替换结果
    success = True
    for key, value in data.items():
        # 检查双大括号格式
        if f"{{{{" + key + "}}}}" in report_content:
            print(f"❌ 双大括号变量 '{key}' 未被替换")
            success = False
        
        # 检查单大括号格式
        if "{" + key + "}" in report_content:
            print(f"❌ 单大括号变量 '{key}' 未被替换")
            success = False
        
        # 检查美元符号格式
        if "${" + key + "}" in report_content:
            print(f"❌ 美元符号变量 '{key}' 未被替换")
            success = False
    
    if success:
        print("✅ 所有变量都已正确替换")
    
    return success


def test_report_generation():
    """测试报告生成功能"""
    print("\n开始测试报告生成功能...")
    
    # 创建报告服务
    report_service = ReportService()
    
    # 创建项目报告模板
    template = report_service.create_project_report_template()
    
    # 准备报告数据
    data = {
        "project_name": "大学生竞赛信息聚合与订阅平台",
        "author": "测试作者",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "project_id": "test-001",
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project_type": "Web应用",
        "project_goal": "为大学生提供竞赛信息聚合与订阅服务",
        "project_start_date": "2023-01-01",
        "project_end_date": "2023-12-31",
        "project_background": "随着高校竞赛数量的增加，学生需要一个集中的平台来获取和管理竞赛信息。",
        "frontend_tech": "React, TypeScript, Ant Design",
        "backend_tech": "Python, FastAPI, SQLAlchemy",
        "database_tech": "PostgreSQL",
        "deployment_tech": "Docker, Nginx",
        "other_tools": "Git, GitHub Actions",
        "system_architecture_description": "本系统采用前后端分离架构，后端使用FastAPI提供RESTful API，前端使用React构建用户界面。",
        "system_components": "- 前端：用户界面、状态管理、API调用\n- 后端：API服务、业务逻辑、数据访问\n- 数据库：数据存储\n- 缓存：提高性能",
        "data_flow": "1. 用户通过前端界面发起请求\n2. 请求经过API网关到达后端服务\n3. 后端服务处理请求并访问数据库\n4. 数据返回给前端展示",
        "features_description": "- 竞赛信息浏览与搜索\n- 个性化竞赛推荐\n- 竞赛订阅与提醒\n- 团队协作功能\n- 竞赛资源共享",
        "implementation_details": "系统实现采用模块化设计，主要包括用户管理、竞赛管理、订阅管理、推荐系统等模块。",
        "key_algorithms": "- 基于协同过滤的推荐算法\n- 全文搜索算法\n- 自动标签提取算法",
        "challenges_and_solutions": "- 挑战1：数据量大导致查询性能下降\n  解决方案：引入缓存机制和索引优化\n- 挑战2：个性化推荐准确性不足\n  解决方案：结合内容和协同过滤的混合推荐算法",
        "testing_methodology": "采用单元测试、集成测试和端到端测试相结合的测试策略。",
        "testing_results": "- 单元测试覆盖率：85%\n- API测试通过率：95%\n- 端到端测试通过率：90%",
        "performance_evaluation": "- 页面加载时间：<2秒\n- API响应时间：<200ms\n- 并发用户支持：1000+",
        "conclusion": "本项目成功构建了一个功能完善、性能良好的大学生竞赛信息聚合与订阅平台，满足了用户的核心需求。",
        "future_work": "- 引入AI助手功能\n- 添加移动应用支持\n- 扩展国际竞赛资源\n- 优化推荐算法"
    }
    
    # 生成报告
    try:
        # 生成Markdown报告
        md_output_path = report_service.generate_report(
            template=template,
            data=data,
            format=ReportFormat.MARKDOWN,
            include_toc=True
        )
        print(f"✅ Markdown报告生成成功：{md_output_path}")
        
        # 尝试生成DOCX报告（如果支持）
        try:
            docx_output_path = report_service.generate_report(
                template=template,
                data=data,
                format=ReportFormat.DOCX,
                include_toc=True,
                include_code_highlighting=True
            )
            print(f"✅ DOCX报告生成成功：{docx_output_path}")
        except Exception as e:
            print(f"⚠️ DOCX报告生成失败（可能是缺少python-docx库）：{str(e)}")
        
        return True
    except Exception as e:
        print(f"❌ 报告生成失败：{str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("报告格式化功能调试")
    print("=" * 80)
    
    var_success = test_variable_replacement()
    gen_success = test_report_generation()
    
    if var_success and gen_success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！") 