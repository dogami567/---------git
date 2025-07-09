import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from backend.app.db.database import Base, engine, SessionLocal
from backend.app.models.competition import Competition
from backend.app.models.report import ReportTemplate
from backend.app.core.logging import logger
from backend.app.services.ai_service import AIService
from backend.app.schemas.competition import CompetitionCreate


def init_db() -> None:
    """
    初始化数据库
    创建所有表并添加初始数据
    """
    try:
        # 先删除所有旧表，确保从干净状态开始
        logger.info("删除旧的数据库表...")
        Base.metadata.drop_all(bind=engine)
        logger.info("旧表删除成功。")

        # 创建所有表
        logger.info("创建数据库表")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
        # 初始化AI服务（创建默认模型和模板）
        logger.info("初始化AI服务")
        db = SessionLocal()
        try:
            ai_service = AIService(db)
            result = ai_service.initialize_defaults()
            if result["success"]:
                if result.get("models_created", 0) > 0:
                    logger.info(f"成功创建 {result['models_created']} 个AI模型")
                if result.get("templates_created", 0) > 0:
                    logger.info(f"成功创建 {result['templates_created']} 个模板")
            elif "message" in result:
                logger.info(result["message"])

            # 创建默认报告模板
            logger.info("创建默认报告模板")
            create_default_report_templates(db)

            # 添加示例竞赛数据
            logger.info("创建示例竞赛数据")
            create_sample_competitions(db)

        except Exception as e:
            logger.error(f"初始化AI服务或竞赛数据时出错: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"初始化数据库时出错: {str(e)}")
        raise

def create_default_report_templates(db: Session):
    """
    创建默认的报告模板
    """
    templates_to_create = [
        {
            "title": "项目分析报告",
            "description": "一份标准的项目分析报告模板，包含基本信息、SWOT分析和总结建议。",
            "structure": {
                "sections": [
                    {"title": "项目简介", "content": "关于项目的基本介绍..."},
                    {"title": "SWOT分析", "content": "优势、劣势、机会、威胁..."},
                    {"title": "总结与建议", "content": "对项目的总结和未来建议..."}
                ]
            }
        }
    ]

    existing_templates = {t.title for t in db.query(ReportTemplate).all()}

    for template_data in templates_to_create:
        if template_data["title"] not in existing_templates:
            db_template = ReportTemplate(
                title=template_data["title"],
                description=template_data["description"],
                structure=template_data["structure"]
            )
            db.add(db_template)
            logger.info(f"添加报告模板: {template_data['title']}")

    db.commit()

def create_sample_competitions(db: Session):
    """
    创建一些示例竞赛数据
    """
    competitions_to_create = [
        {
            "title": "蓝桥杯大赛",
            "description": "全国性的IT学科竞赛，旨在提高大学生的自主创新意识和工程实践能力。",
            "start_date": datetime.utcnow() + timedelta(days=10),
            "end_date": datetime.utcnow() + timedelta(days=40),
            "registration_deadline": datetime.utcnow() + timedelta(days=5),
            "organizer": "工业和信息化部人才交流中心",
            "category": "编程",
            "website": "https://dasai.lanqiao.cn/"
        },
        {
            "title": "全国大学生数学建模竞赛",
            "description": "培养学生的创新意识、团队精神和应用数学解决实际问题的能力。",
            "start_date": datetime.utcnow() + timedelta(days=20),
            "end_date": datetime.utcnow() + timedelta(days=23),
            "registration_deadline": datetime.utcnow() + timedelta(days=15),
            "organizer": "中国工业与应用数学学会",
            "category": "数学建模",
            "website": "http://www.mcm.edu.cn/"
        },
        {
            "title": "“挑战杯”全国大学生课外学术科技作品竞赛",
            "description": '被誉为当代大学生科技创新的"奥林匹克"盛会。',
            "start_date": datetime.utcnow() - timedelta(days=5),
            "end_date": datetime.utcnow() + timedelta(days=60),
            "registration_deadline": datetime.utcnow() - timedelta(days=10),
            "organizer": "共青团中央、中国科协、教育部、全国学联",
            "category": "科技创新",
            "website": "http://www.tiaozhanbei.net/"
        },
        {
            "title": "ACM-ICPC国际大学生程序设计竞赛",
            "description": "世界上规模最大、水平最高的国际大学生程序设计竞赛之一。",
            "start_date": datetime.utcnow() + timedelta(days=50),
            "end_date": datetime.utcnow() + timedelta(days=51),
            "registration_deadline": datetime.utcnow() + timedelta(days=40),
            "organizer": "ACM",
            "category": "算法竞赛",
            "website": "https://icpc.global/"
        },
        {
            "title": '中国"互联网+"大学生创新创业大赛',
            "description": "覆盖全国所有高校、面向全体大学生、影响最大的赛事活动之一。",
            "start_date": datetime.utcnow() - timedelta(days=20),
            "end_date": datetime.utcnow() - timedelta(days=1),
            "registration_deadline": datetime.utcnow() - timedelta(days=30),
            "organizer": "教育部等",
            "category": "创新创业",
            "website": "https://cy.ncss.cn/"
        }
    ]

    existing_competitions = {c.title for c in db.query(Competition).all()}
    
    for comp_data in competitions_to_create:
        if comp_data["title"] not in existing_competitions:
            db_comp = Competition(**comp_data)
            db.add(db_comp)
            logger.info(f"添加竞赛: {comp_data['title']}")

    db.commit()
    logger.info("示例竞赛数据创建完成")

if __name__ == "__main__":
    logger.info("开始数据库初始化...")
    init_db()
    logger.info("数据库初始化完成。") 