from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from backend.app.db.database import Base


class ReportFormatEnum(str, enum.Enum):
    """报告格式枚举"""
    MARKDOWN = "markdown"
    DOCX = "docx"
    PDF = "pdf"


class ReportStatusEnum(str, enum.Enum):
    """报告状态枚举"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportTemplate(Base):
    """报告模板模型"""
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    structure = Column(JSON, nullable=False)  # 存储模板结构
    extra_info = Column(JSON, nullable=True)  # 存储元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    reports = relationship("Report", back_populates="template")


class Report(Base):
    """报告模型"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    format = Column(Enum(ReportFormatEnum), nullable=False, default=ReportFormatEnum.MARKDOWN)
    status = Column(Enum(ReportStatusEnum), nullable=False, default=ReportStatusEnum.PENDING)
    content = Column(Text, nullable=True)  # 存储Markdown格式的报告内容
    file_path = Column(String(255), nullable=True)  # 报告文件路径
    extra_info = Column(JSON, nullable=True)  # 存储元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键关系
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # 关联关系
    owner = relationship("User", back_populates="reports")
    template = relationship("ReportTemplate", back_populates="reports")
    project = relationship("Project", back_populates="reports") 
    sections = relationship("ReportSection", back_populates="report", cascade="all, delete-orphan")


class ReportSection(Base):
    """报告章节模型"""
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)

    report = relationship("Report", back_populates="sections") 