#!/usr/bin/env python
"""
数据库模型修复脚本

用于创建必要的数据库表和初始数据，以便集成测试可以正常运行。
这个脚本会创建一个SQLite内存数据库，并初始化所需的表结构。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入必要的模块
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.database import Base
from backend.app.models.ai_engine import AIModel, PersonalizationTemplate, PersonalizationLog
from backend.app.models.project import Project
from backend.app.models.report import ReportTemplate, Report, ReportFormatEnum
from backend.app.core.config import settings

def fix_database_models():
    """修复数据库模型问题"""
    print("开始修复数据库模型...")
    
    # 创建SQLite内存数据库
    engine = create_engine("sqlite:///./app.db", connect_args={"check_same_thread": False})
    
    # 创建所有表
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功")
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 创建默认AI模型
        print("创建默认AI模型...")
        default_model = AIModel(
            name="Default GPT Model",
            provider="OpenAI",
            model_id="gpt-4",
            api_key_name="OPENAI_API_KEY",
            is_active=True,
            max_tokens=4096,
            temperature=0.7,
            config={
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
        )
        
        db.add(default_model)
        db.commit()
        db.refresh(default_model)
        print(f"默认AI模型创建成功: {default_model.name}")
        
        # 创建一个简单的模板
        print("创建默认模板...")
        template = PersonalizationTemplate(
            name="Default Template",
            description="默认代码个性化模板",
            prompt_template="请优化以下代码：\n{code}",
            task_type="optimize",
            ai_model_id=default_model.id,
            is_active=True
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        print(f"默认模板创建成功: {template.name}")
        
        # 创建测试项目
        print("创建测试项目...")
        project = Project(
            name="测试项目",
            description="用于测试的项目"
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"测试项目创建成功: {project.name}")
        
        # 创建报告模板
        print("创建报告模板...")
        report_template = ReportTemplate(
            title="测试报告模板",
            description="用于测试的报告模板",
            structure={
                "sections": [
                    {"title": "项目概述", "content": "# 项目概述\n\n{{project_name}} 由 {{author}} 创建于 {{date}}。"},
                    {"title": "目录", "content": "## 目录"},
                    {"title": "技术栈", "content": "## 技术栈\n\n本项目使用的主要技术包括："},
                    {"title": "系统架构", "content": "## 系统架构\n\n系统的整体架构如下："}
                ]
            },
            metadata={"version": "1.0"}
        )
        
        db.add(report_template)
        db.commit()
        db.refresh(report_template)
        print(f"报告模板创建成功: {report_template.title}")
        
        print("数据库模型修复成功")
        
    except Exception as e:
        print(f"修复数据库模型时出错: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_database_models() 