from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class AIModelBase(BaseModel):
    name: str
    provider: str
    model_id: str
    api_key_name: str
    max_tokens: int = 4096
    temperature: float = 0.7
    is_active: bool = True
    config: Optional[Dict[str, Any]] = None


class AIModelCreate(AIModelBase):
    pass


class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model_id: Optional[str] = None
    api_key_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class AIModelResponse(AIModelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AIModelList(BaseModel):
    items: List[AIModelResponse]
    total: int
    skip: int
    limit: int


class TemplateBase(BaseModel):
    name: str
    description: str
    prompt_template: str
    task_type: str
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    is_active: bool = True
    parameters: Optional[Dict[str, Any]] = None


class TemplateCreate(TemplateBase):
    ai_model_id: int


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_template: Optional[str] = None
    task_type: Optional[str] = None
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    is_active: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None
    ai_model_id: Optional[int] = None


class TemplateResponse(TemplateBase):
    id: int
    ai_model_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TemplateList(BaseModel):
    items: List[TemplateResponse]
    total: int
    skip: int
    limit: int


class PersonalizeCodeRequest(BaseModel):
    template_id: int
    input_code: str
    parameters: Dict[str, Any]
    user_id: Optional[int] = None


class PersonalizeCodeResponse(BaseModel):
    output_code: str
    processing_time: float
    tokens_used: int
    log_id: int


class LogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    template_id: int
    input_code: str
    output_code: Optional[str]
    prompt_used: str
    success: bool
    error_message: Optional[str]
    processing_time: Optional[float]
    tokens_used: Optional[int]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        orm_mode = True


# 新增的Schema类

class InitializeResponse(BaseModel):
    """初始化响应"""
    success: bool
    models_created: int = 0
    templates_created: int = 0
    message: Optional[str] = None
    error: Optional[str] = None


class PersonalizationSettingsResponse(BaseModel):
    """个性化设置响应"""
    models: List[Dict[str, Any]]
    task_types: Dict[str, List[Dict[str, Any]]]


class UserPreferenceRequest(BaseModel):
    """用户偏好设置请求"""
    preference_type: str
    preference_value: Dict[str, Any]


class CodeTaskRequest(BaseModel):
    """代码任务请求"""
    code: str
    language: str
    style: Optional[str] = "default"
    user_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


class UserHistoryResponse(BaseModel):
    """用户历史记录响应"""
    history: List[LogResponse]
    total: int


class AddCommentsRequest(CodeTaskRequest):
    pass


class RenameVariablesRequest(CodeTaskRequest): # 应该是 CodeTaskRequest
    rename_map: Dict[str, str]


class OptimizeCodeRequest(CodeTaskRequest):
    optimization_level: str = "default"


class RefactorCodeRequest(CodeTaskRequest):
    refactor_instructions: str


class ConvertLanguageRequest(CodeTaskRequest): # 应该是 CodeTaskRequest
    target_language: str


class CodeResponse(BaseModel):
    """通用代码响应"""
    code: str
    log_id: int


class TaskTypeResponse(BaseModel):
    """任务类型响应"""
    task_types: List[str] 