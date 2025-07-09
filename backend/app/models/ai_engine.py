from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


class AIModel(Base):
    """AI模型配置"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(100), nullable=False)  # OpenAI, Anthropic, 等
    model_id = Column(String(100), nullable=False)  # gpt-4, claude-3, 等
    api_key_name = Column(String(100), nullable=False)  # 环境变量名称
    is_active = Column(Boolean, default=True)
    max_tokens = Column(Integer, default=4096)
    temperature = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config = Column(JSON, nullable=True)  # 其他配置参数

    # 关系
    personalization_templates = relationship("PersonalizationTemplate", back_populates="ai_model")


class PersonalizationTemplate(Base):
    """代码个性化模板"""
    __tablename__ = "personalization_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    prompt_template = Column(Text, nullable=False)  # 带有占位符的提示模板
    task_type = Column(String(50), nullable=False)  # 任务类型：重命名变量、添加注释、重构等
    example_input = Column(Text, nullable=True)  # 示例输入
    example_output = Column(Text, nullable=True)  # 示例输出
    parameters = Column(JSON, nullable=True)  # 默认参数
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    ai_model_id = Column(Integer, ForeignKey("ai_models.id"))
    
    # 关系
    ai_model = relationship("AIModel", back_populates="personalization_templates")
    personalization_logs = relationship("PersonalizationLog", back_populates="template")


class PersonalizationLog(Base):
    """代码个性化日志"""
    __tablename__ = "personalization_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # 可选关联到用户
    template_id = Column(Integer, ForeignKey("personalization_templates.id"))
    input_code = Column(Text, nullable=False)
    output_code = Column(Text, nullable=True)
    prompt_used = Column(Text, nullable=False)
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)  # 处理时间（秒）
    extra_info = Column(JSON, nullable=True)  # 附加元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    template = relationship("PersonalizationTemplate", back_populates="personalization_logs") 