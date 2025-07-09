import os
import json
import shutil
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.exceptions import NotFoundException, BadRequestException, RepositoryException, ValidationException
from backend.app.core.logging import logger
from backend.app.models.component import Component, ComponentVersion
from backend.app.services.repository_service import RepositoryService
from backend.app.services.validation_service import ValidationService


class ComponentService:
    """
    组件服务
    负责组件的存储、检索和验证
    """
    
    def __init__(self, db: Session):
        """
        初始化组件服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.repo_service = RepositoryService()
        self.validation_service = ValidationService()
        
    def get_components(
        self, 
        skip: int = 0, 
        limit: int = 100,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        active_only: bool = True
    ) -> List[Component]:
        """
        获取组件列表
        
        Args:
            skip: 分页偏移量
            limit: 分页大小
            category: 按类别过滤
            tag: 按标签过滤
            active_only: 是否只返回活跃组件
            
        Returns:
            List[Component]: 组件列表
        """
        query = self.db.query(Component)
        
        # 过滤条件
        if active_only:
            query = query.filter(Component.is_active == True)
            
        if category:
            query = query.filter(Component.category == category)
            
        if tag:
            # 标签存储为逗号分隔的字符串，使用LIKE查询
            query = query.filter(Component.tags.like(f"%{tag}%"))
            
        # 分页
        components = query.offset(skip).limit(limit).all()
        
        return components
    
    def get_component(self, component_id: int) -> Component:
        """
        根据ID获取组件
        
        Args:
            component_id: 组件ID
            
        Returns:
            Component: 组件对象
            
        Raises:
            NotFoundException: 组件不存在
        """
        component = self.db.query(Component).filter(Component.id == component_id).first()
        
        if not component:
            raise NotFoundException(f"组件ID {component_id} 不存在")
            
        return component
    
    def get_component_by_name(self, name: str) -> Optional[Component]:
        """
        根据名称获取组件
        
        Args:
            name: 组件名称
            
        Returns:
            Optional[Component]: 组件对象，如果不存在则返回None
        """
        return self.db.query(Component).filter(Component.name == name).first()
    
    def create_component(self, component_data: Dict[str, Any], files: Dict[str, Any]) -> Component:
        """
        创建新组件
        
        Args:
            component_data: 组件数据
            files: 组件文件
            
        Returns:
            Component: 创建的组件对象
            
        Raises:
            BadRequestException: 组件名称已存在
            ValidationException: 组件验证失败
        """
        # 检查组件名称是否已存在
        existing_component = self.get_component_by_name(component_data["name"])
        if existing_component:
            raise BadRequestException(f"组件名称 '{component_data['name']}' 已存在")
            
        # 确保仓库已设置
        self.repo_service.setup_repository()
        
        # 创建组件目录
        component_path = self._create_component_directory(component_data["name"], component_data["category"])
        
        # 保存组件文件
        self._save_component_files(component_path, files)
        
        # 创建元数据文件
        meta_info = self._create_metadata_file(component_path, component_data)
        
        # 验证组件
        is_valid, validation_messages = self.validation_service.validate_component(component_path, files)
        
        if not is_valid:
            # 如果验证失败，删除组件目录
            shutil.rmtree(component_path)
            raise ValidationException(f"组件验证失败: {'; '.join(validation_messages)}")
        
        # 提交到Git仓库
        commit_id = self.repo_service.commit_changes(f"添加新组件: {component_data['name']}")
        
        # 创建组件记录
        component = Component(
            name=component_data["name"],
            description=component_data.get("description", ""),
            version=component_data.get("version", "1.0.0"),
            category=component_data["category"],
            path=str(component_path),
            author=component_data.get("author", ""),
            tags=",".join(component_data.get("tags", [])),
            dependencies=component_data.get("dependencies", {}),
            meta_info=meta_info
        )
        
        self.db.add(component)
        self.db.commit()
        self.db.refresh(component)
        
        # 创建组件版本记录
        component_version = ComponentVersion(
            component_id=component.id,
            version=component.version,
            commit_id=commit_id,
            changes="初始版本"
        )
        
        self.db.add(component_version)
        self.db.commit()
        
        return component
    
    def update_component(self, component_id: int, component_data: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Component:
        """
        更新组件
        
        Args:
            component_id: 组件ID
            component_data: 组件数据
            files: 组件文件（可选）
            
        Returns:
            Component: 更新后的组件对象
            
        Raises:
            NotFoundException: 组件不存在
            ValidationException: 组件验证失败
        """
        # 获取组件
        component = self.get_component(component_id)
        
        # 确保仓库已设置
        self.repo_service.setup_repository()
        
        # 更新组件文件（如果提供）
        if files:
            self._save_component_files(component.path, files)
            
        # 更新元数据文件
        meta_info = self._update_metadata_file(component.path, component_data)
        
        # 验证组件
        is_valid, validation_messages = self.validation_service.validate_component(component.path, files or {})
        
        if not is_valid:
            # 如果验证失败，回滚更改
            self.repo_service.reset_changes()
            raise ValidationException(f"组件验证失败: {'; '.join(validation_messages)}")
        
        # 提交到Git仓库
        commit_message = f"更新组件: {component.name}"
        if "version" in component_data and component_data["version"] != component.version:
            commit_message = f"更新组件 {component.name} 到版本 {component_data['version']}"
            
        commit_id = self.repo_service.commit_changes(commit_message)
        
        # 检查是否需要创建新版本
        create_new_version = False
        if "version" in component_data and component_data["version"] != component.version:
            create_new_version = True
            
        # 更新组件记录
        for key, value in component_data.items():
            if key == "tags" and isinstance(value, list):
                setattr(component, key, ",".join(value))
            elif hasattr(component, key):
                setattr(component, key, value)
                
        # 更新元数据
        component.meta_info = meta_info
        
        self.db.commit()
        self.db.refresh(component)
        
        # 创建新版本记录（如果需要）
        if create_new_version:
            component_version = ComponentVersion(
                component_id=component.id,
                version=component.version,
                commit_id=commit_id,
                changes=component_data.get("changes", "更新版本")
            )
            
            self.db.add(component_version)
            self.db.commit()
            
        return component
    
    def delete_component(self, component_id: int) -> bool:
        """
        删除组件
        
        Args:
            component_id: 组件ID
            
        Returns:
            bool: 是否成功删除
            
        Raises:
            NotFoundException: 组件不存在
        """
        # 获取组件
        component = self.get_component(component_id)
        
        # 确保仓库已设置
        self.repo_service.setup_repository()
        
        # 删除组件目录
        try:
            if os.path.exists(component.path):
                shutil.rmtree(component.path)
                
            # 提交到Git仓库
            self.repo_service.commit_changes(f"删除组件: {component.name}")
        except Exception as e:
            logger.error(f"删除组件文件时出错: {str(e)}")
            # 即使文件删除失败，也继续删除数据库记录
            
        # 删除组件记录（级联删除版本记录）
        self.db.delete(component)
        self.db.commit()
        
        return True
    
    def get_component_versions(self, component_id: int) -> List[ComponentVersion]:
        """
        获取组件版本历史
        
        Args:
            component_id: 组件ID
            
        Returns:
            List[ComponentVersion]: 版本列表
            
        Raises:
            NotFoundException: 组件不存在
        """
        # 检查组件是否存在
        component = self.get_component(component_id)
        
        # 获取版本历史
        versions = self.db.query(ComponentVersion).filter(
            ComponentVersion.component_id == component_id
        ).order_by(ComponentVersion.created_at.desc()).all()
        
        return versions
    
    def validate_component(self, component_id: int) -> Tuple[bool, List[str]]:
        """
        验证组件质量
        
        Args:
            component_id: 组件ID
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 验证消息列表)
            
        Raises:
            NotFoundException: 组件不存在
        """
        # 获取组件
        component = self.get_component(component_id)
        
        # 验证组件
        return self.validation_service.validate_component(component.path, {})
    
    def _create_component_directory(self, name: str, category: str) -> Path:
        """
        创建组件目录
        
        Args:
            name: 组件名称
            category: 组件类别
            
        Returns:
            Path: 组件目录路径
        """
        # 构建组件路径
        repo_path = Path(self.repo_service.local_path)
        components_dir = repo_path / "components"
        category_dir = components_dir / category
        component_dir = category_dir / name
        
        # 创建目录
        os.makedirs(category_dir, exist_ok=True)
        
        # 如果组件目录已存在，则清空它
        if os.path.exists(component_dir):
            shutil.rmtree(component_dir)
            
        # 创建组件目录
        os.makedirs(component_dir)
        
        return component_dir
    
    def _save_component_files(self, component_path: str, files: Dict[str, Any]) -> None:
        """
        保存组件文件
        
        Args:
            component_path: 组件目录路径
            files: 组件文件
        """
        for file_name, file_content in files.items():
            file_path = os.path.join(component_path, file_name)
            
            # 确保父目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件内容
            with open(file_path, "wb") as f:
                f.write(file_content)
                
        logger.info(f"已保存组件文件到: {component_path}")
    
    def _create_metadata_file(self, component_path: str, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建元数据文件
        
        Args:
            component_path: 组件目录路径
            component_data: 组件数据
            
        Returns:
            Dict[str, Any]: 元数据
        """
        meta_info = {
            "name": component_data["name"],
            "description": component_data.get("description", ""),
            "version": component_data.get("version", "1.0.0"),
            "category": component_data["category"],
            "author": component_data.get("author", ""),
            "tags": component_data.get("tags", []),
            "dependencies": component_data.get("dependencies", {}),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # 添加自定义元数据
        if "meta_info" in component_data and isinstance(component_data["meta_info"], dict):
            meta_info.update(component_data["meta_info"])
            
        # 写入元数据文件
        metadata_path = os.path.join(component_path, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta_info, f, ensure_ascii=False, indent=2)
            
        return meta_info
    
    def _update_metadata_file(self, component_path: str, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新元数据文件
        
        Args:
            component_path: 组件目录路径
            component_data: 组件数据
            
        Returns:
            Dict[str, Any]: 更新后的元数据
        """
        # 读取现有元数据
        metadata_path = os.path.join(component_path, "metadata.json")
        meta_info = {}
        
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta_info = json.load(f)
                
        # 更新元数据
        for key, value in component_data.items():
            if key == "meta_info" and isinstance(value, dict):
                # 对于嵌套的元数据，更新而不是替换
                if "meta_info" not in meta_info:
                    meta_info["meta_info"] = {}
                meta_info["meta_info"].update(value)
            elif key != "meta_info":
                meta_info[key] = value
                
        # 更新时间戳
        meta_info["updated_at"] = datetime.utcnow().isoformat()
        
        # 写入元数据文件
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta_info, f, ensure_ascii=False, indent=2)
            
        return meta_info 