import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from backend.app.core.config import settings
from backend.app.core.exceptions import NotFoundException, BadRequestException
from backend.app.core.logging import logger
from backend.app.models.component import Component, ComponentVersion


class MetadataService:
    """
    元数据管理服务
    负责组件元数据的存储、检索和管理
    """
    
    def __init__(self, db: Session):
        """
        初始化元数据服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def get_component_metadata(self, component_id: int) -> Dict[str, Any]:
        """
        获取组件元数据
        
        Args:
            component_id: 组件ID
            
        Returns:
            Dict[str, Any]: 组件元数据
            
        Raises:
            NotFoundException: 组件不存在
        """
        component = self.db.query(Component).filter(Component.id == component_id).first()
        
        if not component:
            raise NotFoundException(f"组件ID {component_id} 不存在")
            
        # 获取版本历史
        versions = self.db.query(ComponentVersion).filter(
            ComponentVersion.component_id == component_id
        ).order_by(ComponentVersion.created_at.desc()).all()
        
        # 构建元数据
        component_meta = {
            "id": component.id,
            "name": component.name,
            "description": component.description,
            "version": component.version,
            "category": component.category,
            "path": component.path,
            "author": component.author,
            "tags": component.tags.split(",") if component.tags else [],
            "dependencies": component.dependencies or {},
            "meta_info": component.meta_info or {},
            "is_active": component.is_active,
            "created_at": component.created_at.isoformat() if component.created_at else None,
            "updated_at": component.updated_at.isoformat() if component.updated_at else None,
            "versions": [
                {
                    "id": v.id,
                    "version": v.version,
                    "commit_id": v.commit_id,
                    "changes": v.changes,
                    "created_at": v.created_at.isoformat() if v.created_at else None
                }
                for v in versions
            ]
        }
        
        return component_meta
    
    def search_components(
        self,
        query: str = None,
        category: str = None,
        tags: List[str] = None,
        author: str = None,
        version: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        搜索组件
        
        Args:
            query: 搜索关键词
            category: 按类别过滤
            tags: 按标签过滤
            author: 按作者过滤
            version: 按版本过滤
            skip: 分页偏移量
            limit: 分页大小
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: (组件列表, 总数)
        """
        # 构建查询
        db_query = self.db.query(Component)
        
        # 应用过滤条件
        if query:
            search = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    Component.name.ilike(search),
                    Component.description.ilike(search),
                    Component.tags.ilike(search)
                )
            )
            
        if category:
            db_query = db_query.filter(Component.category == category)
            
        if tags:
            # 对每个标签应用LIKE过滤
            for tag in tags:
                db_query = db_query.filter(Component.tags.ilike(f"%{tag}%"))
                
        if author:
            db_query = db_query.filter(Component.author.ilike(f"%{author}%"))
            
        if version:
            db_query = db_query.filter(Component.version == version)
            
        # 获取总数
        total = db_query.count()
        
        # 应用分页
        components = db_query.order_by(Component.updated_at.desc()).offset(skip).limit(limit).all()
        
        # 构建结果
        results = []
        for component in components:
            results.append({
                "id": component.id,
                "name": component.name,
                "description": component.description,
                "version": component.version,
                "category": component.category,
                "author": component.author,
                "tags": component.tags.split(",") if component.tags else [],
                "updated_at": component.updated_at.isoformat() if component.updated_at else None
            })
            
        return results, total
    
    def get_component_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有组件类别及其计数
        
        Returns:
            List[Dict[str, Any]]: 类别列表
        """
        categories = self.db.query(
            Component.category,
            func.count(Component.id).label("count")
        ).group_by(Component.category).all()
        
        return [{"name": c.category, "count": c.count} for c in categories]
    
    def get_component_tags(self) -> List[Dict[str, Any]]:
        """
        获取所有组件标签及其计数
        
        Returns:
            List[Dict[str, Any]]: 标签列表
        """
        # 从数据库获取所有标签（逗号分隔的字符串）
        components = self.db.query(Component.tags).filter(Component.tags != None).all()
        
        # 解析并计数标签
        tag_counts = {}
        for c in components:
            if c.tags:
                tags = c.tags.split(",")
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
                        
        # 构建结果
        return [{"name": tag, "count": count} for tag, count in tag_counts.items()]
    
    def get_component_authors(self) -> List[Dict[str, Any]]:
        """
        获取所有组件作者及其计数
        
        Returns:
            List[Dict[str, Any]]: 作者列表
        """
        authors = self.db.query(
            Component.author,
            func.count(Component.id).label("count")
        ).filter(Component.author != None).group_by(Component.author).all()
        
        return [{"name": a.author, "count": a.count} for a in authors]
    
    def update_component_metadata(self, component_id: int, meta_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新组件元数据
        
        Args:
            component_id: 组件ID
            meta_data: 更新的元数据
            
        Returns:
            Dict[str, Any]: 更新后的元数据
            
        Raises:
            NotFoundException: 组件不存在
            BadRequestException: 元数据无效
        """
        component = self.db.query(Component).filter(Component.id == component_id).first()
        
        if not component:
            raise NotFoundException(f"组件ID {component_id} 不存在")
            
        # 验证元数据
        self._validate_metadata(meta_data)
        
        # 更新组件元数据
        if "name" in meta_data:
            component.name = meta_data["name"]
            
        if "description" in meta_data:
            component.description = meta_data["description"]
            
        if "category" in meta_data:
            component.category = meta_data["category"]
            
        if "author" in meta_data:
            component.author = meta_data["author"]
            
        if "tags" in meta_data and isinstance(meta_data["tags"], list):
            component.tags = ",".join(meta_data["tags"])
            
        if "dependencies" in meta_data and isinstance(meta_data["dependencies"], dict):
            component.dependencies = meta_data["dependencies"]
            
        if "meta_info" in meta_data and isinstance(meta_data["meta_info"], dict):
            component.meta_info = meta_data["meta_info"]
            
        # 保存更改
        self.db.commit()
        
        # 返回更新后的元数据
        return self.get_component_metadata(component_id)
    
    def _validate_metadata(self, meta_data: Dict[str, Any]) -> None:
        """
        验证元数据格式
        
        Args:
            meta_data: 要验证的元数据
            
        Raises:
            BadRequestException: 元数据无效
        """
        # 验证必要字段
        required_fields = []
        for field in required_fields:
            if field not in meta_data:
                raise BadRequestException(f"缺少必要的元数据字段: {field}")
                
        # 验证字段类型
        if "name" in meta_data and not isinstance(meta_data["name"], str):
            raise BadRequestException("name字段必须是字符串")
            
        if "description" in meta_data and not isinstance(meta_data["description"], str):
            raise BadRequestException("description字段必须是字符串")
            
        if "category" in meta_data and not isinstance(meta_data["category"], str):
            raise BadRequestException("category字段必须是字符串")
            
        if "author" in meta_data and not isinstance(meta_data["author"], str):
            raise BadRequestException("author字段必须是字符串")
            
        if "tags" in meta_data and not isinstance(meta_data["tags"], list):
            raise BadRequestException("tags字段必须是列表")
            
        if "dependencies" in meta_data and not isinstance(meta_data["dependencies"], dict):
            raise BadRequestException("dependencies字段必须是对象")
            
        if "meta_info" in meta_data and not isinstance(meta_data["meta_info"], dict):
            raise BadRequestException("meta_info字段必须是对象") 