import re
import logging
from typing import Dict, Any, List, Tuple, Optional

from backend.app.core.exceptions import AIServiceException
from backend.app.services.ai_service import AIService


class CodePersonalizationService:
    """
    代码个性化服务，提供各种代码个性化功能
    """

    def __init__(self, ai_service: AIService):
        """
        初始化代码个性化服务
        
        Args:
            ai_service: AI服务实例
        """
        self.ai_service = ai_service
        self.logger = logging.getLogger(__name__)
        
        # 预定义任务类型
        self.task_types = {
            "add_comments": "添加注释",
            "rename_variables": "重命名变量",
            "optimize_code": "优化代码",
            "refactor_code": "重构代码",
            "convert_language": "转换语言",
            "explain_code": "解释代码",
            "add_types": "添加类型注解",
            "generate_tests": "生成测试用例",
            "fix_bugs": "修复Bug"
        }
    
    def get_available_task_types(self) -> Dict[str, str]:
        """
        获取所有可用的任务类型
        
        Returns:
            Dict[str, str]: 任务类型ID到描述的映射
        """
        return self.task_types
    
    def add_comments(
        self, 
        code: str, 
        language: str, 
        comment_style: str = "detailed", 
        user_id: Optional[int] = None
    ) -> str:
        """
        为代码添加注释
        
        Args:
            code: 输入代码
            language: 代码语言（python, javascript等）
            comment_style: 注释风格（simple, detailed, docstring）
            user_id: 用户ID（可选）
            
        Returns:
            str: 添加注释后的代码
            
        Raises:
            AIServiceException: AI服务异常
        """
        # 获取添加注释的模板
        templates = self.ai_service.get_templates_by_task_type("add_comments")
        
        if not templates:
            raise AIServiceException("没有找到添加注释的模板")
            
        # 选择合适的模板
        template = self._select_template_by_preference(templates, language, comment_style)
        
        # 准备参数
        parameters = {
            "language": language,
            "comment_style": comment_style
        }
        
        # 调用AI服务处理代码
        try:
            result, _ = self.ai_service.personalize_code(
                template.id, 
                code, 
                parameters,
                user_id
            )
            return result
        except Exception as e:
            self.logger.error(f"添加注释失败: {str(e)}")
            raise AIServiceException(f"添加注释失败: {str(e)}")
    
    def rename_variables(
        self, 
        code: str, 
        language: str, 
        naming_convention: str = "camelCase", 
        user_id: Optional[int] = None
    ) -> str:
        """
        重命名变量
        
        Args:
            code: 输入代码
            language: 代码语言（python, javascript等）
            naming_convention: 命名规范（camelCase, snake_case, PascalCase等）
            user_id: 用户ID（可选）
            
        Returns:
            str: 重命名后的代码
            
        Raises:
            AIServiceException: AI服务异常
        """
        # 获取重命名变量的模板
        templates = self.ai_service.get_templates_by_task_type("rename_variables")
        
        if not templates:
            raise AIServiceException("没有找到重命名变量的模板")
            
        # 选择合适的模板
        template = self._select_template_by_preference(templates, language, naming_convention)
        
        # 准备参数
        parameters = {
            "language": language,
            "naming_convention": naming_convention
        }
        
        # 调用AI服务处理代码
        try:
            result, _ = self.ai_service.personalize_code(
                template.id, 
                code, 
                parameters,
                user_id
            )
            return result
        except Exception as e:
            self.logger.error(f"重命名变量失败: {str(e)}")
            raise AIServiceException(f"重命名变量失败: {str(e)}")
    
    def optimize_code(
        self, 
        code: str, 
        language: str, 
        optimization_goal: str = "performance", 
        user_id: Optional[int] = None
    ) -> str:
        """
        优化代码
        
        Args:
            code: 输入代码
            language: 代码语言（python, javascript等）
            optimization_goal: 优化目标（performance, readability, memory等）
            user_id: 用户ID（可选）
            
        Returns:
            str: 优化后的代码
            
        Raises:
            AIServiceException: AI服务异常
        """
        # 获取优化代码的模板
        templates = self.ai_service.get_templates_by_task_type("optimize_code")
        
        if not templates:
            raise AIServiceException("没有找到优化代码的模板")
            
        # 选择合适的模板
        template = self._select_template_by_preference(templates, language, optimization_goal)
        
        # 准备参数
        parameters = {
            "language": language,
            "optimization_goal": optimization_goal
        }
        
        # 调用AI服务处理代码
        try:
            result, _ = self.ai_service.personalize_code(
                template.id, 
                code, 
                parameters,
                user_id
            )
            return result
        except Exception as e:
            self.logger.error(f"优化代码失败: {str(e)}")
            raise AIServiceException(f"优化代码失败: {str(e)}")
    
    def refactor_code(
        self, 
        code: str, 
        language: str, 
        refactor_type: str = "general", 
        specific_instructions: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> str:
        """
        重构代码
        
        Args:
            code: 输入代码
            language: 代码语言（python, javascript等）
            refactor_type: 重构类型（general, extract_method, reduce_complexity等）
            specific_instructions: 特定的重构指示（可选）
            user_id: 用户ID（可选）
            
        Returns:
            str: 重构后的代码
            
        Raises:
            AIServiceException: AI服务异常
        """
        # 获取重构代码的模板
        templates = self.ai_service.get_templates_by_task_type("refactor_code")
        
        if not templates:
            raise AIServiceException("没有找到重构代码的模板")
            
        # 选择合适的模板
        template = self._select_template_by_preference(templates, language, refactor_type)
        
        # 准备参数
        parameters = {
            "language": language,
            "refactor_type": refactor_type
        }
        
        if specific_instructions:
            parameters["specific_instructions"] = specific_instructions
        
        # 调用AI服务处理代码
        try:
            result, _ = self.ai_service.personalize_code(
                template.id, 
                code, 
                parameters,
                user_id
            )
            return result
        except Exception as e:
            self.logger.error(f"重构代码失败: {str(e)}")
            raise AIServiceException(f"重构代码失败: {str(e)}")
    
    def convert_language(
        self, 
        code: str, 
        from_language: str,
        to_language: str,
        maintain_comments: bool = True,
        user_id: Optional[int] = None
    ) -> str:
        """
        转换代码语言
        
        Args:
            code: 输入代码
            from_language: 源代码语言
            to_language: 目标代码语言
            maintain_comments: 是否保留注释
            user_id: 用户ID（可选）
            
        Returns:
            str: 转换后的代码
            
        Raises:
            AIServiceException: AI服务异常
        """
        # 获取转换语言的模板
        templates = self.ai_service.get_templates_by_task_type("convert_language")
        
        if not templates:
            raise AIServiceException("没有找到转换语言的模板")
            
        # 选择合适的模板
        template = self._select_template_for_language_conversion(templates, from_language, to_language)
        
        # 准备参数
        parameters = {
            "from_language": from_language,
            "to_language": to_language,
            "maintain_comments": maintain_comments
        }
        
        # 调用AI服务处理代码
        try:
            result, _ = self.ai_service.personalize_code(
                template.id, 
                code, 
                parameters,
                user_id
            )
            return result
        except Exception as e:
            self.logger.error(f"转换语言失败: {str(e)}")
            raise AIServiceException(f"转换语言失败: {str(e)}")
    
    def process_custom_task(
        self,
        code: str,
        task_type: str,
        parameters: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """
        处理自定义任务
        
        Args:
            code: 输入代码
            task_type: 任务类型
            parameters: 任务参数
            user_id: 用户ID（可选）
            
        Returns:
            str: 处理后的代码
            
        Raises:
            AIServiceException: AI服务异常
        """
        # 获取指定任务类型的模板
        templates = self.ai_service.get_templates_by_task_type(task_type)
        
        if not templates:
            raise AIServiceException(f"没有找到任务类型 '{task_type}' 的模板")
            
        # 选择第一个模板
        template = templates[0]
        
        # 调用AI服务处理代码
        try:
            result, _ = self.ai_service.personalize_code(
                template.id, 
                code, 
                parameters,
                user_id
            )
            return result
        except Exception as e:
            self.logger.error(f"处理自定义任务失败: {str(e)}")
            raise AIServiceException(f"处理自定义任务失败: {str(e)}")
    
    def _select_template_by_preference(self, templates, language, preference):
        """
        根据语言和偏好选择最合适的模板
        """
        # 优先选择与语言和偏好都匹配的模板
        for template in templates:
            template_name = template.name.lower()
            if language.lower() in template_name and preference.lower() in template_name:
                return template
                
        # 其次选择与语言匹配的模板
        for template in templates:
            template_name = template.name.lower()
            if language.lower() in template_name:
                return template
                
        # 最后返回第一个模板
        return templates[0]
    
    def _select_template_for_language_conversion(self, templates, from_language, to_language):
        """
        选择最合适的语言转换模板
        """
        # 优先选择匹配源语言和目标语言的模板
        for template in templates:
            template_name = template.name.lower()
            if from_language.lower() in template_name and to_language.lower() in template_name:
                return template
                
        # 其次选择通用转换模板
        for template in templates:
            template_name = template.name.lower()
            if "general" in template_name or "universal" in template_name:
                return template
                
        # 最后返回第一个模板
        return templates[0] 