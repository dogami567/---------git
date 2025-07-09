from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.core.exceptions import (
    handle_exceptions,
    AIServiceException,
    AIModelNotFoundException,
    AIModelInactiveException,
    AITemplateNotFoundException,
    AITemplateInactiveException,
    AIProviderException,
    AIRateLimitException,
    AITokenLimitException,
    AIContextLengthException,
    AIInvalidParameterException,
    AIAuthenticationException,
    AIServiceUnavailableException,
    AITimeoutException
)
from backend.app.models.ai_engine import AIModel, PersonalizationTemplate, PersonalizationLog
from backend.app.services.ai_service import AIService
from backend.app.services.code_personalization_service import CodePersonalizationService
from backend.app.schemas.ai_engine import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelList,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateList,
    PersonalizeCodeRequest,
    PersonalizeCodeResponse,
    LogResponse,
    UserPreferenceRequest,
    InitializeResponse,
    PersonalizationSettingsResponse,
    UserHistoryResponse,
    AddCommentsRequest,
    RenameVariablesRequest,
    OptimizeCodeRequest,
    RefactorCodeRequest,
    ConvertLanguageRequest,
    CodeResponse,
    TaskTypeResponse
)


router = APIRouter()


@router.get("/models", response_model=AIModelList)
@handle_exceptions
async def list_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取所有AI模型列表
    """
    try:
        models = db.query(AIModel).offset(skip).limit(limit).all()
        total = db.query(AIModel).count()
        return {"items": models, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise AIServiceException(f"获取AI模型列表失败: {str(e)}")


@router.post("/models", response_model=AIModelResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_model(
    model: AIModelCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的AI模型
    """
    try:
        # 检查名称是否已存在
        existing_model = db.query(AIModel).filter(AIModel.name == model.name).first()
        if existing_model:
            raise AIServiceException(f"模型名称 '{model.name}' 已存在")
        
        # 创建新模型
        db_model = AIModel(**model.dict())
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    except Exception as e:
        db.rollback()
        if "已存在" in str(e):
            raise AIServiceException(str(e))
        raise AIServiceException(f"创建AI模型失败: {str(e)}")


@router.get("/models/{model_id}", response_model=AIModelResponse)
@handle_exceptions
async def get_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    获取特定AI模型详情
    """
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise AIModelNotFoundException(f"模型ID {model_id} 不存在")
    return model


@router.put("/models/{model_id}", response_model=AIModelResponse)
@handle_exceptions
async def update_model(
    model_id: int,
    model_update: AIModelUpdate,
    db: Session = Depends(get_db)
):
    """
    更新AI模型
    """
    try:
        # 获取现有模型
        db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
        if not db_model:
            raise AIModelNotFoundException(f"模型ID {model_id} 不存在")
        
        # 更新模型字段
        for key, value in model_update.dict(exclude_unset=True).items():
            setattr(db_model, key, value)
        
        db.commit()
        db.refresh(db_model)
        return db_model
    except AIModelNotFoundException:
        raise
    except Exception as e:
        db.rollback()
        raise AIServiceException(f"更新AI模型失败: {str(e)}")


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    删除AI模型
    """
    try:
        # 获取现有模型
        db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
        if not db_model:
            raise AIModelNotFoundException(f"模型ID {model_id} 不存在")
        
        # 检查是否有关联的模板
        templates = db.query(PersonalizationTemplate).filter(
            PersonalizationTemplate.ai_model_id == model_id
        ).count()
        
        if templates > 0:
            raise AIServiceException(f"模型ID {model_id} 有 {templates} 个关联模板，无法删除")
        
        # 删除模型
        db.delete(db_model)
        db.commit()
        return None
    except AIModelNotFoundException:
        raise
    except AIServiceException:
        raise
    except Exception as e:
        db.rollback()
        raise AIServiceException(f"删除AI模型失败: {str(e)}")


@router.get("/templates", response_model=TemplateList)
@handle_exceptions
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取所有模板列表，可按任务类型筛选
    """
    try:
        query = db.query(PersonalizationTemplate)
        
        # 如果指定了任务类型，进行筛选
        if task_type:
            query = query.filter(PersonalizationTemplate.task_type == task_type)
            
        # 获取分页数据
        templates = query.offset(skip).limit(limit).all()
        total = query.count()
        
        return {"items": templates, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise AIServiceException(f"获取模板列表失败: {str(e)}")


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的模板
    """
    try:
        # 检查名称是否已存在
        existing_template = db.query(PersonalizationTemplate).filter(
            PersonalizationTemplate.name == template.name
        ).first()
        
        if existing_template:
            raise AIServiceException(f"模板名称 '{template.name}' 已存在")
        
        # 检查关联的模型是否存在
        model = db.query(AIModel).filter(AIModel.id == template.ai_model_id).first()
        if not model:
            raise AIModelNotFoundException(f"模型ID {template.ai_model_id} 不存在")
        
        # 创建新模板
        db_template = PersonalizationTemplate(**template.dict())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return db_template
    except (AIModelNotFoundException, AIServiceException):
        raise
    except Exception as e:
        db.rollback()
        raise AIServiceException(f"创建模板失败: {str(e)}")


@router.get("/templates/{template_id}", response_model=TemplateResponse)
@handle_exceptions
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    获取特定模板详情
    """
    template = db.query(PersonalizationTemplate).filter(
        PersonalizationTemplate.id == template_id
    ).first()
    
    if not template:
        raise AITemplateNotFoundException(f"模板ID {template_id} 不存在")
        
    return template


@router.put("/templates/{template_id}", response_model=TemplateResponse)
@handle_exceptions
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """
    更新模板
    """
    try:
        # 获取现有模板
        db_template = db.query(PersonalizationTemplate).filter(
            PersonalizationTemplate.id == template_id
        ).first()
        
        if not db_template:
            raise AITemplateNotFoundException(f"模板ID {template_id} 不存在")
        
        # 检查关联的模型是否存在
        if template_update.ai_model_id is not None:
            model = db.query(AIModel).filter(AIModel.id == template_update.ai_model_id).first()
            if not model:
                raise AIModelNotFoundException(f"模型ID {template_update.ai_model_id} 不存在")
        
        # 更新模板字段
        for key, value in template_update.dict(exclude_unset=True).items():
            setattr(db_template, key, value)
        
        db.commit()
        db.refresh(db_template)
        
        return db_template
    except (AIModelNotFoundException, AITemplateNotFoundException):
        raise
    except Exception as e:
        db.rollback()
        raise AIServiceException(f"更新模板失败: {str(e)}")


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    删除模板
    """
    try:
        # 获取现有模板
        db_template = db.query(PersonalizationTemplate).filter(
            PersonalizationTemplate.id == template_id
        ).first()
        
        if not db_template:
            raise AITemplateNotFoundException(f"模板ID {template_id} 不存在")
        
        # 检查是否有相关联的日志
        logs = db.query(PersonalizationLog).filter(
            PersonalizationLog.template_id == template_id
        ).count()
        
        if logs > 0:
            # 将模板标记为不活动，而不是删除
            db_template.is_active = False
            db.commit()
            return None
        
        # 删除模板
        db.delete(db_template)
        db.commit()
        
        return None
    except AITemplateNotFoundException:
        raise
    except Exception as e:
        db.rollback()
        raise AIServiceException(f"删除模板失败: {str(e)}")


@router.post("/personalize", response_model=PersonalizeCodeResponse)
@handle_exceptions
async def personalize_code(
    request: PersonalizeCodeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    使用AI个性化代码
    """
    try:
        ai_service = AIService(db)
        
        # 使用AI服务生成代码
        output_code, log = ai_service.personalize_code(
            template_id=request.template_id,
            input_code=request.input_code,
            parameters=request.parameters or {},
            user_id=current_user_id
        )
        
        # 返回生成的代码和日志信息
        return {
            "output_code": output_code,
            "template_id": request.template_id,
            "log_id": log.id,
            "processing_time": log.processing_time,
            "tokens_used": log.tokens_used
        }
    except (
        AIModelNotFoundException, 
        AIModelInactiveException,
        AITemplateNotFoundException,
        AITemplateInactiveException,
        AIProviderException,
        AIRateLimitException,
        AITokenLimitException,
        AIContextLengthException,
        AIInvalidParameterException,
        AIAuthenticationException,
        AIServiceUnavailableException,
        AITimeoutException
    ) as e:
        # 使用handle_exceptions处理异常，并返回给客户端
        raise
    except Exception as e:
        raise AIServiceException(f"使用AI个性化代码失败: {str(e)}")


@router.post("/initialize", response_model=InitializeResponse)
@handle_exceptions
async def initialize_defaults(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    初始化默认的AI模型和模板
    """
    try:
        ai_service = AIService(db)
        result = ai_service.initialize_defaults()
        return result
    except Exception as e:
        raise AIServiceException(f"初始化默认AI模型和模板失败: {str(e)}")


@router.get("/settings", response_model=PersonalizationSettingsResponse)
@handle_exceptions
async def get_personalization_settings(db: Session = Depends(get_db)):
    """
    获取个性化设置和相关信息
    """
    try:
        ai_service = AIService(db)
        settings = ai_service.get_personalization_settings()
        return settings
    except Exception as e:
        raise AIServiceException(f"获取个性化设置失败: {str(e)}")


@router.get("/user/history", response_model=UserHistoryResponse)
@handle_exceptions
async def get_user_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    获取用户个性化历史记录
    """
    try:
        # 如果没有提供用户ID，则使用默认值
        user_id = current_user_id or 1  # 默认用户ID为1
        
        ai_service = AIService(db)
        history = ai_service.get_user_personalization_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return history
    except Exception as e:
        raise AIServiceException(f"获取用户个性化历史记录失败: {str(e)}")


@router.post("/user/preferences", status_code=status.HTTP_200_OK)
@handle_exceptions
async def save_user_preference(
    preference: UserPreferenceRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    保存用户偏好设置
    """
    try:
        # 如果没有提供用户ID，则使用默认值
        user_id = current_user_id or 1  # 默认用户ID为1
        
        ai_service = AIService(db)
        result = ai_service.save_user_preference(
            user_id=user_id,
            preference_type=preference.preference_type,
            preference_value=preference.preference_value
        )
        
        return result
    except Exception as e:
        raise AIServiceException(f"保存用户偏好设置失败: {str(e)}")


@router.post("/code/add-comments", response_model=CodeResponse)
@handle_exceptions
async def add_comments(
    request: AddCommentsRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    添加代码注释
    """
    try:
        ai_service = AIService(db)
        code_service = CodePersonalizationService(ai_service)
        
        # 处理代码
        output_code = code_service.add_comments(
            code=request.code,
            language=request.language,
            style=request.style,
            user_id=current_user_id
        )
        
        return {"output_code": output_code}
    except Exception as e:
        raise AIServiceException(f"添加代码注释失败: {str(e)}")


@router.post("/code/rename-variables", response_model=CodeResponse)
@handle_exceptions
async def rename_variables(
    request: RenameVariablesRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    重命名变量
    """
    try:
        ai_service = AIService(db)
        code_service = CodePersonalizationService(ai_service)
        
        # 处理代码
        output_code = code_service.rename_variables(
            code=request.code,
            language=request.language,
            style=request.style,
            user_id=current_user_id
        )
        
        return {"output_code": output_code}
    except Exception as e:
        raise AIServiceException(f"重命名变量失败: {str(e)}")


@router.post("/code/optimize", response_model=CodeResponse)
@handle_exceptions
async def optimize_code(
    request: OptimizeCodeRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    优化代码
    """
    try:
        ai_service = AIService(db)
        code_service = CodePersonalizationService(ai_service)
        
        # 处理代码
        output_code = code_service.optimize_code(
            code=request.code,
            language=request.language,
            focus=request.focus,
            user_id=current_user_id
        )
        
        return {"output_code": output_code}
    except Exception as e:
        raise AIServiceException(f"优化代码失败: {str(e)}")


@router.post("/code/refactor", response_model=CodeResponse)
@handle_exceptions
async def refactor_code(
    request: RefactorCodeRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    重构代码
    """
    try:
        ai_service = AIService(db)
        code_service = CodePersonalizationService(ai_service)
        
        # 处理代码
        output_code = code_service.refactor_code(
            code=request.code,
            language=request.language,
            refactor_type=request.refactor_type,
            instructions=request.instructions,
            user_id=current_user_id
        )
        
        return {"output_code": output_code}
    except Exception as e:
        raise AIServiceException(f"重构代码失败: {str(e)}")


@router.post("/code/convert", response_model=CodeResponse)
@handle_exceptions
async def convert_language(
    request: ConvertLanguageRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None  # 可选参数，用于从上下文中获取用户ID
):
    """
    转换代码语言
    """
    try:
        ai_service = AIService(db)
        code_service = CodePersonalizationService(ai_service)
        
        # 处理代码
        output_code = code_service.convert_language(
            code=request.code,
            source_language=request.source_language,
            target_language=request.target_language,
            user_id=current_user_id
        )
        
        return {"output_code": output_code}
    except Exception as e:
        raise AIServiceException(f"转换代码语言失败: {str(e)}")


@router.get("/code/task-types", response_model=TaskTypeResponse)
@handle_exceptions
async def get_task_types(db: Session = Depends(get_db)):
    """
    获取所有任务类型的代码生成信息
    """
    try:
        ai_service = AIService(db)
        code_service = CodePersonalizationService(ai_service)
        
        task_types = code_service.get_task_types()
        return {"task_types": task_types}
    except Exception as e:
        raise AIServiceException(f"获取任务类型代码生成信息失败: {str(e)}") 