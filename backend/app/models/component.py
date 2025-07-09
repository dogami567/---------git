from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


class Component(Base):
    """
    组件模型
    存储代码组件信息
    """
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String, nullable=False, default="1.0.0")
    category = Column(String, index=True, nullable=False)
    path = Column(String, nullable=False)  # 组件在仓库中的路径
    author = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # 以逗号分隔的标签列表
    dependencies = Column(JSON, nullable=True)  # 组件依赖关系
    extra_info = Column(JSON, nullable=True)  # 其他元数据
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    versions = relationship("ComponentVersion", back_populates="component", cascade="all, delete-orphan")


class ComponentVersion(Base):
    """
    组件版本模型
    存储组件的不同版本信息
    """
    __tablename__ = "component_versions"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    version = Column(String, nullable=False)
    commit_id = Column(String, nullable=False)  # Git提交ID
    changes = Column(Text, nullable=True)  # 版本变更说明
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    component = relationship("Component", back_populates="versions") 