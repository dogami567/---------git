"""
测试报告API功能

使用外部API服务测试报告生成功能。
"""

import os
import sys
import json
import shutil
import tempfile
import requests
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# API配置
API_KEY = "sk-7BfwheOHkGkT47A5mi5ammTRj4biI6Nv4KjphjwIjHI5wHdK"
API_BASE = "https://api.aiclaude.site"
MODEL = "gemini-2.5-flash-lite-preview-06-17"


def check_server_running(url="http://localhost:8000/docs", timeout=5):
    """检查FastAPI服务器是否正在运行"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def test_generate_report_with_service(skip_ai=False, save_to_project=False):
    """使用报告服务直接测试报告生成功能"""
    print("开始使用服务直接测试报告生成...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        report_content = ""
        
        if not skip_ai:
            # 准备AI请求数据
            prompt = """
            请为我生成一个大学生竞赛项目的报告内容。报告应包括以下部分：
            1. 项目概述
            2. 技术栈描述
            3. 系统架构
            4. 主要功能
            5. 未来展望
            
            请确保内容详细但简洁，适合大学生竞赛项目展示。
            每个部分生成100-200字左右的内容。
            """
            
            # 调用AI API生成内容
            try:
                print(f"正在调用AI API ({API_BASE})生成报告内容...")
                response = requests.post(
                    f"{API_BASE}/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {API_KEY}"
                    },
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": "你是一个专业的技术文档撰写助手。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"❌ AI API请求失败: {response.status_code}")
                    print(response.text)
                    return False
                
                # 解析响应
                ai_response = response.json()
                report_content = ai_response["choices"][0]["message"]["content"]
                
                print("✅ AI内容生成成功")
                print("\nAI生成的内容预览:")
                print("-" * 80)
                print(report_content[:300] + "...")
                print("-" * 80)
                
                # 保存AI生成的内容到文件
                report_file = os.path.join(temp_dir, "ai_report_content.md")
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report_content)
                
            except Exception as e:
                print(f"❌ AI内容生成失败: {str(e)}")
                print("使用预设内容继续测试...")
                skip_ai = True
        
        if skip_ai:
            print("使用预设内容进行测试...")
            report_content = """
# 大学生竞赛信息聚合与订阅平台

## 项目概述
大学生竞赛信息聚合与订阅平台是一个为高校学生提供全面竞赛信息服务的一站式平台。该平台整合了各类学科竞赛、创新创业大赛、技能比赛等信息，通过智能推荐算法为用户提供个性化的赛事推送。平台支持竞赛日历、团队组建、资源分享等功能，有效解决了大学生获取竞赛信息分散、不及时、不全面的痛点问题。

## 技术栈描述
本项目采用前后端分离架构，前端使用Vue.js框架构建响应式用户界面，结合Element UI组件库提供一致的视觉体验。后端采用FastAPI框架，以Python为主要开发语言，提供高性能的RESTful API服务。数据库使用PostgreSQL存储结构化数据，Redis用于缓存和会话管理。全文检索功能通过Elasticsearch实现，消息推送系统基于WebSocket协议。云服务部署采用Docker容器化技术，结合CI/CD流程实现自动化部署。

## 系统架构
系统采用微服务架构设计，主要包括用户服务、竞赛信息服务、推荐服务、通知服务和报告生成服务五大核心模块。各服务之间通过REST API和消息队列进行通信，确保系统的高可用性和可扩展性。数据层设计遵循数据规范化原则，并通过ORM框架实现对象关系映射。前端采用组件化开发方式，实现了PC端和移动端的自适应布局，提供一致的用户体验。

## 主要功能
平台主要功能包括：(1)竞赛信息聚合与分类展示，支持多维度筛选和搜索；(2)个性化推荐系统，基于用户专业、兴趣和历史行为推送相关竞赛；(3)竞赛日历与提醒，自动同步重要日期至个人日历；(4)团队组建与管理，支持在线招募队员、任务分配；(5)资源分享与协作，提供往届优秀作品和学习资料；(6)智能报告生成，辅助用户快速生成项目文档；(7)竞赛经验交流社区，促进知识分享与传承。

## 未来展望
未来平台将重点发展以下方向：(1)引入AI辅助功能，提供竞赛方案智能评估和优化建议；(2)拓展校企合作模块，对接企业资源和实习就业机会；(3)建立竞赛数据分析系统，为高校提供决策支持；(4)开发开放API，支持第三方应用集成；(5)构建跨校交流平台，促进高校间竞赛资源共享与合作。随着用户规模增长，平台将持续优化推荐算法和用户体验，打造成为全国大学生竞赛领域的权威平台。
            """
        
        # 准备报告数据
        sections = []
        current_section = None
        
        # 简单解析AI生成的内容，提取标题和内容
        for line in report_content.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # 检测标题
            if line.startswith("# ") or line.startswith("## "):
                if current_section:
                    sections.append(current_section)
                
                level = 1 if line.startswith("# ") else 2
                title = line.lstrip("#").strip()
                current_section = {
                    "title": title,
                    "content": "",
                    "level": level,
                    "subsections": []
                }
            elif current_section:
                current_section["content"] += line + "\n"
        
        # 添加最后一个部分
        if current_section:
            sections.append(current_section)
        
        # 如果没有解析出部分，使用默认部分
        if not sections:
            sections = [
                {
                    "title": "项目概述",
                    "content": report_content,
                    "level": 1,
                    "subsections": []
                }
            ]
        
        # 准备报告数据
        report_data = {
            "title": "大学生竞赛项目报告",
            "description": "使用AI生成的项目报告",
            "format": "markdown",
            "sections": sections,
            "data": {
                "project_name": "大学生竞赛信息聚合与订阅平台",
                "author": "AI助手",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            "formatting_options": {
                "include_toc": True,
                "include_code_highlighting": True
            }
        }
        
        # 保存请求数据到文件（用于调试）
        request_file = os.path.join(temp_dir, "api_request.json")
        with open(request_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n请求数据已保存到: {request_file}")
        
        # 直接调用报告服务
        try:
            print("\n正在直接调用报告服务...")
            
            # 导入报告服务
            try:
                from backend.app.services.report_service import ReportService, ReportSection, ReportTemplate, ReportFormat
                
                # 创建报告服务实例
                report_service = ReportService()
                
                # 创建报告模板
                template = ReportTemplate(
                    title=report_data["title"],
                    description=report_data["description"]
                )
                
                # 添加各部分到模板
                for section_data in report_data["sections"]:
                    section = ReportSection(
                        title=section_data["title"],
                        content=section_data["content"],
                        level=section_data["level"]
                    )
                    template.add_section(section)
                
                # 生成报告
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = report_service.generate_report(
                    template=template,
                    data=report_data["data"],
                    format=ReportFormat.MARKDOWN,
                    include_toc=report_data["formatting_options"]["include_toc"],
                    include_code_highlighting=report_data["formatting_options"]["include_code_highlighting"]
                )
                
                print(f"报告已生成: {report_path}")
                
                # 读取生成的报告内容
                with open(report_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                
                # 保存到临时文件
                report_output = os.path.join(temp_dir, "generated_report.md")
                with open(report_output, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                print(f"报告已复制到临时目录: {report_output}")
                
                # 如果需要生成Word文档
                try:
                    # 生成DOCX格式报告
                    docx_path = report_service.generate_report(
                        template=template,
                        data=report_data["data"],
                        format=ReportFormat.DOCX,
                        include_toc=report_data["formatting_options"]["include_toc"],
                        include_code_highlighting=report_data["formatting_options"]["include_code_highlighting"]
                    )
                    print(f"Word文档已生成: {docx_path}")
                except Exception as e:
                    print(f"生成Word文档时出错: {str(e)}")
                    docx_path = None
                
                # 如果要求保存到项目目录
                if save_to_project:
                    project_root = Path(__file__).parent.parent.parent
                    reports_dir = project_root / "reports"
                    os.makedirs(reports_dir, exist_ok=True)
                    
                    # 保存Markdown报告
                    project_report_path = reports_dir / f"report_{timestamp}.md"
                    with open(project_report_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print(f"报告已保存到项目目录: {project_report_path}")
                    
                    # 如果生成了Word文档，也保存到项目目录
                    if docx_path and os.path.exists(docx_path):
                        target_path = reports_dir / f"report_{timestamp}.docx"
                        shutil.copy2(docx_path, target_path)
                        print(f"Word文档已保存到项目目录: {target_path}")
                
                print("\n报告生成成功！")
                return True
                
            except ImportError as e:
                print(f"❌ 导入报告服务失败: {str(e)}")
                print("请确保后端代码结构正确，且报告服务模块可用。")
                return False
                
        except Exception as e:
            print(f"❌ 调用报告服务时出错: {str(e)}")
            return False


def test_generate_report_with_ai(api_base_url="http://localhost:8000", skip_ai=False, save_to_project=False):
    """使用AI生成报告内容并测试报告API"""
    print("开始测试使用AI生成报告内容...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        report_content = ""
        
        if not skip_ai:
            # 准备AI请求数据
            prompt = """
            请为我生成一个大学生竞赛项目的报告内容。报告应包括以下部分：
            1. 项目概述
            2. 技术栈描述
            3. 系统架构
            4. 主要功能
            5. 未来展望
            
            请确保内容详细但简洁，适合大学生竞赛项目展示。
            每个部分生成100-200字左右的内容。
            """
            
            # 调用AI API生成内容
            try:
                print(f"正在调用AI API ({API_BASE})生成报告内容...")
                response = requests.post(
                    f"{API_BASE}/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {API_KEY}"
                    },
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": "你是一个专业的技术文档撰写助手。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"❌ AI API请求失败: {response.status_code}")
                    print(response.text)
                    return False
                
                # 解析响应
                ai_response = response.json()
                report_content = ai_response["choices"][0]["message"]["content"]
                
                print("✅ AI内容生成成功")
                print("\nAI生成的内容预览:")
                print("-" * 80)
                print(report_content[:300] + "...")
                print("-" * 80)
                
                # 保存AI生成的内容到文件
                report_file = os.path.join(temp_dir, "ai_report_content.md")
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report_content)
                
            except Exception as e:
                print(f"❌ AI内容生成失败: {str(e)}")
                print("使用预设内容继续测试...")
                skip_ai = True
        
        if skip_ai:
            print("使用预设内容进行测试...")
            report_content = """
# 大学生竞赛信息聚合与订阅平台

## 项目概述
大学生竞赛信息聚合与订阅平台是一个为高校学生提供全面竞赛信息服务的一站式平台。该平台整合了各类学科竞赛、创新创业大赛、技能比赛等信息，通过智能推荐算法为用户提供个性化的赛事推送。平台支持竞赛日历、团队组建、资源分享等功能，有效解决了大学生获取竞赛信息分散、不及时、不全面的痛点问题。

## 技术栈描述
本项目采用前后端分离架构，前端使用Vue.js框架构建响应式用户界面，结合Element UI组件库提供一致的视觉体验。后端采用FastAPI框架，以Python为主要开发语言，提供高性能的RESTful API服务。数据库使用PostgreSQL存储结构化数据，Redis用于缓存和会话管理。全文检索功能通过Elasticsearch实现，消息推送系统基于WebSocket协议。云服务部署采用Docker容器化技术，结合CI/CD流程实现自动化部署。

## 系统架构
系统采用微服务架构设计，主要包括用户服务、竞赛信息服务、推荐服务、通知服务和报告生成服务五大核心模块。各服务之间通过REST API和消息队列进行通信，确保系统的高可用性和可扩展性。数据层设计遵循数据规范化原则，并通过ORM框架实现对象关系映射。前端采用组件化开发方式，实现了PC端和移动端的自适应布局，提供一致的用户体验。

## 主要功能
平台主要功能包括：(1)竞赛信息聚合与分类展示，支持多维度筛选和搜索；(2)个性化推荐系统，基于用户专业、兴趣和历史行为推送相关竞赛；(3)竞赛日历与提醒，自动同步重要日期至个人日历；(4)团队组建与管理，支持在线招募队员、任务分配；(5)资源分享与协作，提供往届优秀作品和学习资料；(6)智能报告生成，辅助用户快速生成项目文档；(7)竞赛经验交流社区，促进知识分享与传承。

## 未来展望
未来平台将重点发展以下方向：(1)引入AI辅助功能，提供竞赛方案智能评估和优化建议；(2)拓展校企合作模块，对接企业资源和实习就业机会；(3)建立竞赛数据分析系统，为高校提供决策支持；(4)开发开放API，支持第三方应用集成；(5)构建跨校交流平台，促进高校间竞赛资源共享与合作。随着用户规模增长，平台将持续优化推荐算法和用户体验，打造成为全国大学生竞赛领域的权威平台。
            """
        
        # 准备报告数据
        sections = []
        current_section = None
        
        # 简单解析AI生成的内容，提取标题和内容
        for line in report_content.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # 检测标题
            if line.startswith("# ") or line.startswith("## "):
                if current_section:
                    sections.append(current_section)
                
                level = 1 if line.startswith("# ") else 2
                title = line.lstrip("#").strip()
                current_section = {
                    "title": title,
                    "content": "",
                    "level": level,
                    "subsections": []
                }
            elif current_section:
                current_section["content"] += line + "\n"
        
        # 添加最后一个部分
        if current_section:
            sections.append(current_section)
        
        # 如果没有解析出部分，使用默认部分
        if not sections:
            sections = [
                {
                    "title": "项目概述",
                    "content": report_content,
                    "level": 1,
                    "subsections": []
                }
            ]
        
        # 准备API请求数据
        request_data = {
            "title": "大学生竞赛项目报告",
            "description": "使用AI生成的项目报告",
            "format": "markdown",
            "sections": sections,
            "data": {
                "project_name": "大学生竞赛信息聚合与订阅平台",
                "author": "AI助手",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            "formatting_options": {
                "include_toc": True,
                "include_code_highlighting": True
            }
        }
        
        # 保存请求数据到文件（用于调试）
        request_file = os.path.join(temp_dir, "api_request.json")
        with open(request_file, "w", encoding="utf-8") as f:
            json.dump(request_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n请求数据已保存到: {request_file}")
        
        # 调用报告生成API
        try:
            print("\n正在调用报告生成API...")
            
            # 使用简化的API端点
            api_url = f"{api_base_url}/api/v1/simple-reports/generate"
            
            api_response = requests.post(
                api_url,
                json=request_data,
                timeout=60  # 报告生成可能需要更长时间
            )
            
            # 如果简化API失败，尝试使用标准API
            if api_response.status_code != 200:
                print(f"简化API调用失败: HTTP {api_response.status_code}")
                print("尝试使用标准API...")
                
                # 准备标准API请求数据
                standard_request_data = {
                    "template": {
                        "title": request_data["title"],
                        "description": request_data["description"],
                        "sections": request_data["sections"]
                    },
                    "data": request_data["data"],
                    "format": request_data["format"],
                    "include_toc": request_data["formatting_options"]["include_toc"],
                    "include_code_highlighting": request_data["formatting_options"]["include_code_highlighting"],
                    "include_styles": True,
                    "include_charts": False
                }
                
                # 调用标准API
                standard_api_url = f"{api_base_url}/api/v1/reports/generate"
                api_response = requests.post(
                    standard_api_url,
                    json=standard_request_data,
                    timeout=60
                )
            
            if api_response.status_code == 200:
                print("✅ 报告API调用成功！")
                result = api_response.json()
                
                # 保存生成的报告
                if "markdown_content" in result:
                    report_output = os.path.join(temp_dir, "generated_report.md")
                    with open(report_output, "w", encoding="utf-8") as f:
                        f.write(result["markdown_content"])
                    print(f"报告已保存到: {report_output}")
                    
                    # 如果要求保存到项目目录
                    if save_to_project:
                        project_root = Path(__file__).parent.parent.parent
                        reports_dir = project_root / "reports"
                        os.makedirs(reports_dir, exist_ok=True)
                        
                        # 使用时间戳创建唯一文件名
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        project_report_path = reports_dir / f"report_{timestamp}.md"
                        
                        # 复制报告内容
                        with open(project_report_path, "w", encoding="utf-8") as f:
                            f.write(result["markdown_content"])
                        print(f"报告已保存到项目目录: {project_report_path}")
                
                if "file_path" in result:
                    print(f"报告文件路径: {result['file_path']}")
                    
                    # 如果API返回了docx文件路径且用户要求保存到项目目录
                    if save_to_project and result["file_path"].endswith(".docx"):
                        try:
                            source_path = result["file_path"]
                            if os.path.exists(source_path):
                                project_root = Path(__file__).parent.parent.parent
                                reports_dir = project_root / "reports"
                                os.makedirs(reports_dir, exist_ok=True)
                                
                                # 使用时间戳创建唯一文件名
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                target_path = reports_dir / f"report_{timestamp}.docx"
                                
                                # 复制文件
                                shutil.copy2(source_path, target_path)
                                print(f"Word文档已保存到项目目录: {target_path}")
                        except Exception as e:
                            print(f"复制Word文档时出错: {e}")
                
                print("\n报告生成成功！")
                return True
            else:
                print(f"❌ 报告API调用失败: HTTP {api_response.status_code}")
                print(f"错误信息: {api_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 调用报告API时出错: {str(e)}")
            print("你可以使用以下请求数据手动测试报告API端点: /api/v1/reports/generate")
            return False


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试报告API功能")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API服务器URL")
    parser.add_argument("--skip-ai", action="store_true", help="跳过AI内容生成，使用预设内容")
    parser.add_argument("--check-only", action="store_true", help="只检查服务器是否运行")
    parser.add_argument("--save-to-project", action="store_true", help="将生成的报告保存到项目的reports目录")
    parser.add_argument("--direct", action="store_true", help="直接调用报告服务而不是通过API")
    args = parser.parse_args()
    
    if args.direct:
        # 直接调用报告服务
        success = test_generate_report_with_service(args.skip_ai, args.save_to_project)
    else:
        # 检查服务器是否运行
        api_base_url = args.api_url
        if not check_server_running(f"{api_base_url}/docs"):
            print(f"❌ API服务器未运行或无法访问: {api_base_url}")
            print("请先启动FastAPI服务器，然后再运行此测试脚本。")
            print("可使用以下命令启动服务器:")
            print("cd backend")
            print("python -m scripts.run_server")
            print("\n或者使用 --direct 参数直接调用报告服务而不是通过API。")
            sys.exit(1)
            
        print(f"✅ API服务器正在运行: {api_base_url}")
        
        if args.check_only:
            print("服务器检查完成，退出测试。")
            sys.exit(0)
        
        success = test_generate_report_with_ai(api_base_url, args.skip_ai, args.save_to_project)
    
    if success:
        print("\n✅ 测试成功完成！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1) 