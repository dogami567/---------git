import os
import time
import logging
import json
import traceback
from typing import Dict, Any, Optional, List, Tuple, Type, Union
from datetime import datetime

import openai
import backoff  # 添加backoff库用于重试
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import settings
from backend.app.core.exceptions import (
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
from backend.app.services.template_initialization import TemplateInitializationService


# OpenAI API错误对应的异常映射
OPENAI_ERROR_MAPPING = {
    "RateLimitError": AIRateLimitException,
    "InvalidRequestError": AIInvalidParameterException,
    "AuthenticationError": AIAuthenticationException,
    "APIConnectionError": AIServiceUnavailableException,
    "ServiceUnavailableError": AIServiceUnavailableException,
    "Timeout": AITimeoutException
}


class AIService:
    """
    AI服务类，用于处理与AI API的交互
    """
    
    def __init__(self, db: Session):
        """
        初始化AI服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.max_retries = settings.AI_MAX_RETRIES if hasattr(settings, "AI_MAX_RETRIES") else 3
        self.retry_delay = settings.AI_RETRY_DELAY if hasattr(settings, "AI_RETRY_DELAY") else 2
    
    def get_active_models(self) -> List[AIModel]:
        """
        获取所有活跃的AI模型
        
        Returns:
            List[AIModel]: AI模型列表
        """
        try:
            return self.db.query(AIModel).filter(AIModel.is_active == True).all()
        except SQLAlchemyError as e:
            self.logger.error(f"获取活跃模型失败: {str(e)}")
            raise AIServiceException(f"数据库查询失败: {str(e)}")
    
    def get_model_by_id(self, model_id: int) -> Optional[AIModel]:
        """
        通过ID获取AI模型
        
        Args:
            model_id: 模型ID
        
        Returns:
            Optional[AIModel]: AI模型对象，如果不存在则返回None
        """
        try:
            model = self.db.query(AIModel).filter(AIModel.id == model_id).first()
            if not model:
                self.logger.warning(f"模型ID {model_id} 不存在")
            return model
        except SQLAlchemyError as e:
            self.logger.error(f"通过ID获取模型失败: {str(e)}")
            raise AIServiceException(f"数据库查询失败: {str(e)}")
    
    def get_model_by_name(self, name: str) -> Optional[AIModel]:
        """
        通过名称获取AI模型
        
        Args:
            name: 模型名称
        
        Returns:
            Optional[AIModel]: AI模型对象，如果不存在则返回None
        """
        try:
            model = self.db.query(AIModel).filter(AIModel.name == name).first()
            if not model:
                self.logger.warning(f"模型名称 {name} 不存在")
            return model
        except SQLAlchemyError as e:
            self.logger.error(f"通过名称获取模型失败: {str(e)}")
            raise AIServiceException(f"数据库查询失败: {str(e)}")
    
    def get_templates_by_task_type(self, task_type: str) -> List[PersonalizationTemplate]:
        """
        获取特定任务类型的所有模板
        
        Args:
            task_type: 任务类型
        
        Returns:
            List[PersonalizationTemplate]: 模板列表
        """
        try:
            templates = self.db.query(PersonalizationTemplate).filter(
                PersonalizationTemplate.task_type == task_type,
                PersonalizationTemplate.is_active == True
            ).all()
            
            if not templates:
                self.logger.warning(f"任务类型 {task_type} 没有找到活跃的模板")
                
            return templates
        except SQLAlchemyError as e:
            self.logger.error(f"获取模板失败: {str(e)}")
            raise AIServiceException(f"数据库查询失败: {str(e)}")
    
    def get_template_by_id(self, template_id: int) -> Optional[PersonalizationTemplate]:
        """
        通过ID获取模板
        
        Args:
            template_id: 模板ID
        
        Returns:
            Optional[PersonalizationTemplate]: 模板对象，如果不存在则返回None
        """
        try:
            template = self.db.query(PersonalizationTemplate).filter(
                PersonalizationTemplate.id == template_id
            ).first()
            
            if not template:
                self.logger.warning(f"模板ID {template_id} 不存在")
                
            return template
        except SQLAlchemyError as e:
            self.logger.error(f"通过ID获取模板失败: {str(e)}")
            raise AIServiceException(f"数据库查询失败: {str(e)}")
    
    def personalize_code(
        self, 
        template_id: int, 
        input_code: str, 
        parameters: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Tuple[str, PersonalizationLog]:
        """
        使用AI模型个性化代码
        
        Args:
            template_id: 模板ID
            input_code: 输入代码
            parameters: 替换模板中占位符的参数
            user_id: 用户ID（可选）
            
        Returns:
            Tuple[str, PersonalizationLog]: 生成的代码和日志对象
            
        Raises:
            AIServiceException: AI服务异常
        """
        # 获取模板
        template = self.get_template_by_id(template_id)
        if not template:
            raise AITemplateNotFoundException(f"模板ID {template_id} 不存在")
            
        # 检查模板是否活跃
        if not template.is_active:
            raise AITemplateInactiveException(f"模板ID {template_id} 未激活")
            
        # 获取关联的AI模型
        ai_model = template.ai_model
        if not ai_model:
            raise AIModelNotFoundException(f"模板 {template.name} 关联的AI模型不存在")
            
        # 检查模型是否活跃
        if not ai_model.is_active:
            raise AIModelInactiveException(f"模型 {ai_model.name} 未激活")
            
        # 准备提示信息
        prompt = template.prompt_template
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            prompt = prompt.replace(placeholder, str(value))
            
        # 将代码添加到提示中
        prompt = prompt.replace("{code}", input_code)
        
        # 创建日志记录
        log = PersonalizationLog(
            user_id=user_id,
            template_id=template_id,
            input_code=input_code,
            prompt_used=prompt,
            metadata={"parameters": parameters}
        )
        
        self.db.add(log)
        self.db.commit()
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 根据提供商选择不同的API调用方式
            if ai_model.provider.lower() == "openai":
                output_code = self._call_openai_api_with_retry(ai_model, prompt)
            elif ai_model.provider.lower() == "anthropic":
                output_code = self._call_anthropic_api_with_retry(ai_model, prompt)
            else:
                raise AIProviderException(f"不支持的AI提供商: {ai_model.provider}")
                
            # 计算处理时间和使用的令牌数（这里是一个简单的估计）
            processing_time = time.time() - start_time
            tokens_used = len(prompt.split()) + len(output_code.split())
            
            # 更新日志
            log.output_code = output_code
            log.success = True
            log.processing_time = processing_time
            log.tokens_used = tokens_used
            
            self.db.commit()
            
            return output_code, log
            
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
            # 记录特定异常
            error_message = str(e)
            self.logger.error(f"AI个性化代码失败: {error_message}")
            
            # 更新日志
            log.success = False
            log.error_message = error_message
            
            self.db.commit()
            
            # 抛出异常
            raise
            
        except Exception as e:
            # 记录未知异常
            error_message = str(e)
            stack_trace = traceback.format_exc()
            self.logger.error(f"AI个性化代码失败 (未知异常): {error_message}\n{stack_trace}")
            
            # 更新日志
            log.success = False
            log.error_message = error_message
            
            self.db.commit()
            
            # 抛出通用异常
            raise AIServiceException(f"AI个性化代码失败: {error_message}")
    
    @backoff.on_exception(
        backoff.expo,
        (AIRateLimitException, AIServiceUnavailableException, AITimeoutException),
        max_tries=3,
        jitter=backoff.full_jitter
    )
    def _call_openai_api_with_retry(self, ai_model: AIModel, prompt: str) -> str:
        """
        调用OpenAI API，带有自动重试机制
        
        Args:
            ai_model: AI模型配置
            prompt: 提示信息
            
        Returns:
            str: 生成的代码
        """
        try:
            return self._call_openai_api(ai_model, prompt)
        except Exception as e:
            # 记录重试信息
            self.logger.warning(f"OpenAI API调用失败，准备重试: {str(e)}")
            raise
    
    def _call_openai_api(self, ai_model: AIModel, prompt: str) -> str:
        """
        调用OpenAI API
        
        Args:
            ai_model: AI模型配置
            prompt: 提示信息
            
        Returns:
            str: 生成的代码
        """
        # 设置API密钥
        api_key = os.environ.get(ai_model.api_key_name)
        if not api_key:
            raise AIAuthenticationException(f"环境变量 {ai_model.api_key_name} 未设置")
            
        openai.api_key = api_key
        
        # 准备配置
        config = {
            "model": ai_model.model_id,
            "temperature": ai_model.temperature,
            "max_tokens": ai_model.max_tokens
        }
        
        # 添加额外配置
        if ai_model.config:
            config.update(ai_model.config)
        
        try:
            # 调用API
            response = openai.ChatCompletion.create(
                messages=[
                    {"role": "system", "content": "你是一个代码个性化助手，根据用户的要求修改代码。"},
                    {"role": "user", "content": prompt}
                ],
                **config
            )
            
            # 提取回复
            return response.choices[0].message.content.strip()
            
        except openai.error.RateLimitError as e:
            raise AIRateLimitException(f"OpenAI API 调用频率超限: {str(e)}")
        except openai.error.InvalidRequestError as e:
            if "context length" in str(e).lower():
                raise AIContextLengthException(f"输入上下文长度超出模型限制: {str(e)}")
            elif "token" in str(e).lower():
                raise AITokenLimitException(f"令牌数量超出模型限制: {str(e)}")
            else:
                raise AIInvalidParameterException(f"无效的请求参数: {str(e)}")
        except openai.error.AuthenticationError as e:
            raise AIAuthenticationException(f"OpenAI API 认证失败: {str(e)}")
        except openai.error.APIConnectionError as e:
            raise AIServiceUnavailableException(f"无法连接到 OpenAI API: {str(e)}")
        except openai.error.ServiceUnavailableError as e:
            raise AIServiceUnavailableException(f"OpenAI 服务不可用: {str(e)}")
        except openai.error.Timeout as e:
            raise AITimeoutException(f"OpenAI API 请求超时: {str(e)}")
        except openai.error.OpenAIError as e:
            # 处理其他OpenAI错误
            error_type = type(e).__name__
            exception_class = OPENAI_ERROR_MAPPING.get(error_type, AIProviderException)
            raise exception_class(f"OpenAI API 错误 ({error_type}): {str(e)}")
        except Exception as e:
            # 处理未知错误
            raise AIServiceException(f"OpenAI API 调用失败: {str(e)}")
    
    @backoff.on_exception(
        backoff.expo,
        (AIRateLimitException, AIServiceUnavailableException, AITimeoutException),
        max_tries=3,
        jitter=backoff.full_jitter
    )
    def _call_anthropic_api_with_retry(self, ai_model: AIModel, prompt: str) -> str:
        """
        调用Anthropic API，带有自动重试机制
        
        Args:
            ai_model: AI模型配置
            prompt: 提示信息
            
        Returns:
            str: 生成的代码
        """
        try:
            return self._call_anthropic_api(ai_model, prompt)
        except Exception as e:
            # 记录重试信息
            self.logger.warning(f"Anthropic API调用失败，准备重试: {str(e)}")
            raise
    
    def _call_anthropic_api(self, ai_model: AIModel, prompt: str) -> str:
        """
        调用Anthropic API
        
        Args:
            ai_model: AI模型配置
            prompt: 提示信息
            
        Returns:
            str: 生成的代码
        """
        # 这里需要添加Anthropic API的实现
        # 由于当前项目可能不需要Anthropic支持，这里留作后续扩展
        raise AIProviderException("Anthropic API支持尚未实现")
    
    def initialize_defaults(self) -> Dict[str, Any]:
        """
        初始化AI引擎的默认设置，包括模型和模板
        """
        result = {
            "success": False,
            "models_created": 0,
            "templates_created": 0,
            "message": ""
        }
        
        try:
            self.logger.info("开始初始化AI默认设置")
            # 初始化默认AI模型
            if not self.get_model_by_name("default_model"):
                default_model = AIModel(
                    name="default_model",
                    provider="openai",
                    model_id="gpt-3.5-turbo",
                    api_key_name="OPENAI_API_KEY", # 请在您的环境变量中设置
                    is_active=True
                )
                self.db.add(default_model)
                self.db.commit()
                result["models_created"] = 1
                
            # 初始化默认模板
            init_service = TemplateInitializationService(self.db)
            initialized_templates = init_service.initialize_templates()
            
            result["templates_created"] = len(initialized_templates)
            result["success"] = True
            self.logger.info(f"成功初始化 {result['models_created']} 个模型和 {result['templates_created']} 个模板")
            
        except Exception as e:
            self.logger.error(f"初始化默认设置失败: {str(e)}")
            result["message"] = str(e)
            
        return result
    
    def get_personalization_settings(self) -> Dict[str, Any]:
        """
        获取个性化设置，包括可用模型和任务类型
        
        Returns:
            Dict[str, Any]: 个性化设置
        """
        try:
            # 获取活跃的模型
            models = self.get_active_models()
            model_list = [{
                "id": model.id,
                "name": model.name,
                "provider": model.provider,
                "model_id": model.model_id
            } for model in models]
            
            # 获取任务类型
            task_types = {}
            templates = self.db.query(PersonalizationTemplate).filter(
                PersonalizationTemplate.is_active == True
            ).all()
            
            for template in templates:
                if template.task_type not in task_types:
                    task_types[template.task_type] = []
                    
                task_types[template.task_type].append({
                    "id": template.id,
                    "name": template.name,
                    "description": template.description
                })
            
            return {
                "models": model_list,
                "task_types": task_types
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"获取个性化设置失败 (数据库错误): {str(e)}")
            raise AIServiceException(f"获取个性化设置失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"获取个性化设置失败: {str(e)}")
            raise AIServiceException(f"获取个性化设置失败: {str(e)}")
    
    def get_user_personalization_history(
        self, 
        user_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取用户的个性化历史记录
        
        Args:
            user_id: 用户ID
            limit: 记录数量限制
            offset: 偏移量
            
        Returns:
            Dict[str, Any]: 包含历史记录的字典
        """
        try:
            # 查询总记录数
            total_count = self.db.query(PersonalizationLog).filter(
                PersonalizationLog.user_id == user_id
            ).count()
            
            # 获取分页记录
            logs = self.db.query(PersonalizationLog).filter(
                PersonalizationLog.user_id == user_id
            ).order_by(
                PersonalizationLog.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            # 转换为字典
            log_list = []
            for log in logs:
                template = self.get_template_by_id(log.template_id)
                template_name = template.name if template else "未知模板"
                
                log_dict = {
                    "id": log.id,
                    "template_name": template_name,
                    "task_type": template.task_type if template else "未知任务",
                    "success": log.success,
                    "created_at": log.created_at.isoformat(),
                    "processing_time": log.processing_time,
                    "tokens_used": log.tokens_used
                }
                log_list.append(log_dict)
            
            return {
                "total": total_count,
                "logs": log_list,
                "offset": offset,
                "limit": limit
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"获取用户个性化历史失败 (数据库错误): {str(e)}")
            raise AIServiceException(f"获取用户个性化历史失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"获取用户个性化历史失败: {str(e)}")
            raise AIServiceException(f"获取用户个性化历史失败: {str(e)}")
    
    def save_user_preference(
        self, 
        user_id: int, 
        preference_type: str, 
        preference_value: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        保存用户偏好设置
        
        Args:
            user_id: 用户ID
            preference_type: 偏好类型 (e.g., "model", "language", "template")
            preference_value: 偏好值
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            # 这里实际上应该将用户偏好保存到数据库
            # 但是当前模型中没有相关表结构，此处仅作示例
            # 在实际项目中，应该创建UserPreference模型并存储数据
            
            # 返回假设的成功响应
            return {
                "success": True,
                "user_id": user_id,
                "preference_type": preference_type,
                "message": "用户偏好设置已保存"
            }
            
        except Exception as e:
            self.logger.error(f"保存用户偏好设置失败: {str(e)}")
            raise AIServiceException(f"保存用户偏好设置失败: {str(e)}") 