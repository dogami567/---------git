from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status, Body
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.core.exceptions import handle_exceptions
from backend.app.models.component import Component, ComponentVersion
from backend.app.services.component_service import ComponentService
from backend.app.services.repository_service import RepositoryService
from backend.app.services.validation_service import ValidationService
from backend.app.services.metadata_service import MetadataService
from backend.app.schemas.component import (
    ComponentCreate, 
    ComponentUpdate, 
    ComponentResponse, 
    ComponentVersionResponse,
    ComponentList
)


router = APIRouter()


@router.get("/", response_model=ComponentList)
@handle_exceptions
async def list_components(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    获取组件列表
    """
    component_service = ComponentService(db)
    components = component_service.get_components(
        skip=skip, 
        limit=limit,
        category=category,
        tag=tag,
        active_only=active_only
    )
    
    total_count = db.query(Component).count()
    
    return {
        "items": components,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }


@router.post("/", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_component(
    name: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    version: str = Form("1.0.0"),
    author: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    创建组件
    """
    # 解析标签
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    # 准备组件数据
    component_data = {
        "name": name,
        "category": category,
        "description": description,
        "version": version,
        "author": author,
        "tags": tag_list
    }
    
    # 读取组件文件
    component_files = {}
    for file in files:
        file_content = await file.read()
        component_files[file.filename] = file_content
    
    # 验证组件
    validation_service = ValidationService()
    is_valid, messages = validation_service.validate_component("", component_files)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "组件验证失败",
                "validation_messages": messages
            }
        )
    
    # 创建组件
    component_service = ComponentService(db)
    component = component_service.create_component(component_data, component_files)
    
    return component


@router.get("/{component_id}", response_model=ComponentResponse)
@handle_exceptions
async def get_component(component_id: int, db: Session = Depends(get_db)):
    """
    获取组件
    """
    component_service = ComponentService(db)
    return component_service.get_component(component_id)


@router.put("/{component_id}", response_model=ComponentResponse)
@handle_exceptions
async def update_component(
    component_id: int,
    name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """
    更新组件
    """
    # 解析标签
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    # 准备组件数据
    component_data = {}
    if name:
        component_data["name"] = name
    if category:
        component_data["category"] = category
    if description:
        component_data["description"] = description
    if version:
        component_data["version"] = version
    if author:
        component_data["author"] = author
    if tag_list:
        component_data["tags"] = tag_list
    
    # 读取组件文件
    component_files = {}
    if files:
        for file in files:
            file_content = await file.read()
            component_files[file.filename] = file_content
    
    # 更新组件
    component_service = ComponentService(db)
    component = component_service.update_component(component_id, component_data, component_files)
    
    return component


@router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_component(component_id: int, db: Session = Depends(get_db)):
    """
    删除组件
    """
    component_service = ComponentService(db)
    component_service.delete_component(component_id)
    
    return None


@router.get("/{component_id}/versions", response_model=List[ComponentVersionResponse])
@handle_exceptions
async def get_component_versions(component_id: int, db: Session = Depends(get_db)):
    """
    获取组件版本列表
    """
    component_service = ComponentService(db)
    return component_service.get_component_versions(component_id)


# 仓库相关操作

@router.get("/repository/status")
@handle_exceptions
async def get_repository_status():
    """
    获取组件仓库状态
    
    返回仓库的基本信息，包括是否已初始化、最近提交等
    """
    repo_service = RepositoryService()
    
    # 确保仓库已设置
    repo_service.setup_repository()
    
    # 获取仓库状态
    status_info = {
        "initialized": True,
        "local_path": str(repo_service.local_path),
        "has_remote": repo_service.repo_url is not None,
        "remote_url": repo_service.repo_url,
        "branch": repo_service.repo_branch
    }
    
    # 获取最新提交信息
    try:
        latest_commit = repo_service.repo.head.commit
        status_info["latest_commit"] = {
            "id": latest_commit.hexsha,
            "author": f"{latest_commit.author.name} <{latest_commit.author.email}>",
            "date": latest_commit.committed_datetime.isoformat(),
            "message": latest_commit.message,
        }
    except:
        status_info["latest_commit"] = None
    
    return status_info


@router.post("/repository/setup")
@handle_exceptions
async def setup_repository():
    """
    设置组件仓库
    
    如果仓库已设置，则忽略；如果未设置，则设置
    """
    repo_service = RepositoryService()
    success = repo_service.setup_repository()
    
    return {"success": success, "message": "仓库设置成功"}


@router.post("/repository/commit")
@handle_exceptions
async def commit_changes(message: str = Body(..., embed=True)):
    """
    提交更改
    
    Args:
        message: 提交信息
    """
    repo_service = RepositoryService()
    commit_id = repo_service.commit_changes(message)
    
    return {
        "success": True,
        "commit_id": commit_id,
        "message": f"提交成功，提交ID为 {commit_id}"
    }


@router.post("/repository/reset")
@handle_exceptions
async def reset_changes():
    """
    重置更改
    
    重置所有更改
    """
    repo_service = RepositoryService()
    success = repo_service.reset_changes()
    
    return {"success": success, "message": "重置成功，所有更改已重置"}


@router.get("/repository/files/{path:path}")
@handle_exceptions
async def get_file_content(path: str):
    """
    获取文件内容
    
    Args:
        path: 文件路径，从仓库根目录开始
    """
    repo_service = RepositoryService()
    content = repo_service.get_file_content(path)
    
    return {"path": path, "content": content}


@router.get("/repository/history/{path:path}")
@handle_exceptions
async def get_file_history(path: str, max_count: int = 10):
    """
    获取文件历史
    
    Args:
        path: 文件路径，从仓库根目录开始
        max_count: 获取的提交数量
    """
    repo_service = RepositoryService()
    history = repo_service.get_file_history(path, max_count)
    
    return {"path": path, "history": history}


# 组件元数据操作

@router.get("/{component_id}/metadata")
@handle_exceptions
async def get_component_metadata(component_id: int, db: Session = Depends(get_db)):
    """
    获取组件元数据
    
    Args:
        component_id: 组件ID
    """
    metadata_service = MetadataService(db)
    component_meta = metadata_service.get_component_metadata(component_id)
    
    return component_meta


@router.put("/{component_id}/metadata")
@handle_exceptions
async def update_component_metadata(
    component_id: int, 
    meta_data: Dict[str, Any] = Body(...), 
    db: Session = Depends(get_db)
):
    """
    更新组件元数据
    
    Args:
        component_id: 组件ID
        meta_data: 更新的元数据
    """
    metadata_service = MetadataService(db)
    updated_meta = metadata_service.update_component_metadata(component_id, meta_data)
    
    return updated_meta


@router.get("/search")
@handle_exceptions
async def search_components(
    query: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    author: Optional[str] = None,
    version: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    搜索组件
    
    Args:
        query: 搜索关键词
        category: 组件类别
        tags: 组件标签，多个标签用逗号分隔
        author: 组件作者
        version: 组件版本
        skip: 跳过数量
        limit: 获取数量
    """
    metadata_service = MetadataService(db)
    
    # 解析标签
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    results, total = metadata_service.search_components(
        query=query,
        category=category,
        tags=tag_list,
        author=author,
        version=version,
        skip=skip,
        limit=limit
    )
    
    return {
        "items": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/categories")
@handle_exceptions
async def get_component_categories(db: Session = Depends(get_db)):
    """
    获取组件类别列表
    """
    metadata_service = MetadataService(db)
    categories = metadata_service.get_component_categories()
    
    return categories


@router.get("/tags")
@handle_exceptions
async def get_component_tags(db: Session = Depends(get_db)):
    """
    获取组件标签列表
    """
    metadata_service = MetadataService(db)
    tags = metadata_service.get_component_tags()
    
    return tags


@router.get("/authors")
@handle_exceptions
async def get_component_authors(db: Session = Depends(get_db)):
    """
    获取组件作者列表
    """
    metadata_service = MetadataService(db)
    authors = metadata_service.get_component_authors()
    
    return authors


@router.post("/{component_id}/validate")
@handle_exceptions
async def validate_component(component_id: int, db: Session = Depends(get_db)):
    """
    验证组件
    
    Args:
        component_id: 组件ID
    """
    component_service = ComponentService(db)
    is_valid, messages = component_service.validate_component(component_id)
    
    return {
        "component_id": component_id,
        "is_valid": is_valid,
        "messages": messages
    } 