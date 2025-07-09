import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.models.ai_engine import PersonalizationTemplate, AIModel
from backend.app.core.exceptions import AIServiceException


class TemplateInitializationService:
    """
    模板初始化服务,用于创建默认的个性化模板
    """
    
    def __init__(self, db: Session):
        """
        初始化模板初始化服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        
    def initialize_templates(self) -> List[PersonalizationTemplate]:
        """
        初始化默认模板
        
        Returns:
            List[PersonalizationTemplate]: 创建的模板列表
        """
        default_templates = [
            {
                "name": "项目周报模板",
                "task_type": "report_generation",
                "prompt_template": "请根据以下信息生成项目周报：\n项目名称：{project_name}\n本周进展：{progress}\n下周计划：{plan}\n风险与问题：{risks}",
                "is_active": True
            }
        ]
        
        created_templates = []
        for template_data in default_templates:
            existing_template = self.db.query(PersonalizationTemplate).filter_by(name=template_data["name"]).first()
            if not existing_template:
                # 找到一个活跃的AI模型来关联
                default_model = self.db.query(AIModel).filter_by(is_active=True).first()
                if not default_model:
                    self.logger.warning(f"没有找到活跃的AI模型，无法创建模板 {template_data['name']}")
                    continue
                    
                new_template = PersonalizationTemplate(
                    name=template_data["name"],
                    task_type=template_data["task_type"],
                    prompt_template=template_data["prompt_template"],
                    is_active=template_data["is_active"],
                    ai_model_id=default_model.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(new_template)
                created_templates.append(new_template)
                self.logger.info(f"创建默认模板: {new_template.name}")

        self.db.commit()
        return created_templates 