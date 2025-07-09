from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ComponentBase(BaseModel):
    """组件基础模型"""
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    category: str
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[Dict[str, str]] = None
    meta_info: Optional[Dict[str, Any]] = None


class ComponentCreate(ComponentBase):
    """创建组件请求模型"""
    pass


class ComponentUpdate(BaseModel):
    """更新组件请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[Dict[str, str]] = None
    meta_info: Optional[Dict[str, Any]] = None
    changes: Optional[str] = None  # 版本变更说明


class ComponentVersionBase(BaseModel):
    """组件版本基础模型"""
    version: str
    commit_id: str
    changes: Optional[str] = None
    created_at: datetime


class ComponentVersionResponse(ComponentVersionBase):
    """组件版本响应模型"""
    id: int
    component_id: int

    class Config:
        from_attributes = True


class ComponentResponse(ComponentBase):
    """组件响应模型"""
    id: int
    path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    versions: List[ComponentVersionResponse] = []

    class Config:
        from_attributes = True


class ComponentList(BaseModel):
    """组件列表响应模型"""
    items: List[ComponentResponse]
    total: int
    skip: int
    limit: int 