"""
报告生成服务

提供报告模板管理和报告生成功能。支持多种格式输出，包括Markdown、DOCX和PDF。
"""

import os
import re
import json
import logging
import hashlib
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.core.exceptions import ReportGenerationException
from backend.app.services.report_formatter_service import ReportFormatterService
from backend.app.models.report import Report, ReportStatusEnum, ReportTemplate as ReportTemplateModel
from backend.app.schemas.report import CompetitionReportCreate
from backend.app.models.competition import Competition
from backend.app.models.user import User


# 配置日志
logger = logging.getLogger(__name__)


class ReportFormat(str, Enum):
    """报告格式枚举"""
    MARKDOWN = "markdown"
    DOCX = "docx"
    PDF = "pdf"  # 新增PDF格式支持


class ReportSection:
    """
    报告部分类
    
    表示报告中的一个部分，包括标题、内容和子部分。
    支持嵌套结构，可以构建复杂的报告层次。
    """
    
    def __init__(self, title: str, content: str = "", level: int = 1):
        """
        初始化报告部分
        
        Args:
            title: 部分标题
            content: 部分内容
            level: 标题级别（1-6）
        """
        self.title = title
        self.content = content
        self.level = max(1, min(6, level))  # 确保级别在1-6之间
        self.subsections: List[ReportSection] = []
    
    def add_subsection(self, subsection: 'ReportSection') -> None:
        """
        添加子部分
        
        Args:
            subsection: 子部分
        """
        self.subsections.append(subsection)
    
    def to_markdown(self) -> str:
        """
        将部分转换为Markdown格式
        
        Returns:
            str: Markdown格式的部分内容
        """
        # 创建标题
        md = f"{'#' * self.level} {self.title}\n\n"
        
        # 添加内容
        if self.content:
            md += f"{self.content}\n\n"
        
        # 添加子部分
        for subsection in self.subsections:
            md += subsection.to_markdown()
        
        return md
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将部分转换为字典格式，用于序列化
        
        Returns:
            Dict[str, Any]: 字典格式的部分内容
        """
        return {
            "title": self.title,
            "content": self.content,
            "level": self.level,
            "subsections": [subsection.to_dict() for subsection in self.subsections]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportSection':
        """
        从字典创建部分
        
        Args:
            data: 字典格式的部分内容
            
        Returns:
            ReportSection: 创建的部分
        """
        section = cls(
            title=data["title"],
            content=data.get("content", ""),
            level=data.get("level", 1)
        )
        
        # 添加子部分
        for subsection_data in data.get("subsections", []):
            section.add_subsection(cls.from_dict(subsection_data))
        
        return section


class ReportTemplate:
    """
    报告模板类
    
    定义报告的整体结构，包括标题、描述、元数据和各部分内容。
    可以序列化为JSON格式以便存储和传输。
    """
    
    def __init__(self, title: str, description: str = "", metadata: Dict[str, Any] = None):
        """
        初始化报告模板
        
        Args:
            title: 模板标题
            description: 模板描述
            metadata: 元数据
        """
        self.title = title
        self.description = description
        self.metadata = metadata or {}
        self.sections: List[ReportSection] = []
        self.version = "1.1.0"  # 添加版本号便于后续升级时的兼容性处理
        self.created_at = datetime.now().isoformat()
    
    def add_section(self, section: ReportSection) -> None:
        """
        添加部分
        
        Args:
            section: 部分
        """
        self.sections.append(section)
    
    def to_markdown(self) -> str:
        """
        将模板转换为Markdown格式
        
        Returns:
            str: Markdown格式的模板内容
        """
        # 创建标题
        md = f"# {self.title}\n\n"
        
        # 添加描述（如果有）
        if self.description:
            md += f"{self.description}\n\n"
        
        # 添加元数据（如果有）
        if self.metadata:
            md += "## 元数据\n\n"
            for key, value in self.metadata.items():
                md += f"- **{key}**: {value}\n"
            md += "\n"
        
        # 添加部分
        for section in self.sections:
            md += section.to_markdown()
        
        return md
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将模板转换为字典格式，用于序列化
        
        Returns:
            Dict[str, Any]: 字典格式的模板内容
        """
        return {
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
            "sections": [section.to_dict() for section in self.sections],
            "version": self.version,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportTemplate':
        """
        从字典创建模板
        
        Args:
            data: 字典格式的模板内容
            
        Returns:
            ReportTemplate: 创建的模板
        """
        template = cls(
            title=data["title"],
            description=data.get("description", ""),
            metadata=data.get("metadata", {})
        )
        
        # 添加版本和创建时间
        template.version = data.get("version", "1.0.0")
        template.created_at = data.get("created_at", datetime.now().isoformat())
        
        # 添加部分
        for section_data in data.get("sections", []):
            template.add_section(ReportSection.from_dict(section_data))
        
        return template
    
    def save_to_file(self, file_path: str) -> None:
        """
        将模板保存到文件
        
        Args:
            file_path: 文件路径
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ReportTemplate':
        """
        从文件加载模板
        
        Args:
            file_path: 文件路径
            
        Returns:
            ReportTemplate: 加载的模板
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"加载模板文件失败：{str(e)}")
            raise ReportGenerationException(f"加载模板文件失败：{str(e)}")


def delete_report(db: Session, report_id: int, user_id: int):
    """
    删除指定ID的报告记录
    Args:
        db: 数据库会话
        report_id: 要删除的报告ID
        user_id: 当前操作的用户ID（用于权限验证）
    """
    db_report = db.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为 {report_id} 的报告未找到"
        )
    if db_report.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此报告"
        )
    db.delete(db_report)
    db.commit()


def get_all_templates(db: Session) -> List[ReportTemplateModel]:
    """
    获取所有报告模板
    
    Args:
        db: 数据库会话
        
    Returns:
        List[ReportTemplate]: 模板对象列表
    """
    return db.query(ReportTemplateModel).all()


class ReportService:
    """
    报告服务类
    
    提供报告模板管理和报告生成功能。
    支持多种格式输出，包括Markdown、DOCX和PDF。
    实现了变量替换、目录生成、样式应用等功能。
    """
    
    def __init__(self, db: Session):
        """
        初始化报告服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.formatter = ReportFormatterService()
        self.reports_dir = Path(settings.REPORTS_DIR)
        self.cache_dir = Path(settings.REPORTS_CACHE_DIR)
        self.templates_dir = Path(settings.REPORTS_TEMPLATES_DIR)
        
        # 确保目录存在
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def create_competition_report(self, report_in: CompetitionReportCreate, user_id: int) -> Report:
        """
        在数据库中创建竞赛报告记录。
        """
        # 创建报告对象
        db_report = Report(
            title=report_in.title,
            format=report_in.format,
            status=ReportStatusEnum.PENDING,
            owner_id=user_id,
            extra_info={
                "competition_ids": report_in.competition_ids,
                "template_id": report_in.template_id,
                "included_sections": report_in.included_sections,
            }
        )
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        return db_report

    def get_reports_by_user(self, user_id: int) -> List[Report]:
        """
        根据用户ID获取其所有报告
        """
        return self.db.query(Report).filter(Report.owner_id == user_id).order_by(Report.created_at.desc()).all()

    @lru_cache(maxsize=32)
    def get_template_by_name(self, name: str) -> ReportTemplate:
        """
        根据名称获取模板
        
        Args:
            name: 模板名称
            
        Returns:
            ReportTemplate: 模板对象
            
        Raises:
            ValueError: 如果模板不存在
        """
        template_path = self.templates_dir / f"{name}.json"
        if not template_path.exists():
            raise ValueError(f"模板不存在：{name}")
        
        return ReportTemplate.load_from_file(str(template_path))
    
    def save_template(self, template: ReportTemplate, name: str) -> str:
        """
        保存模板
        
        Args:
            template: 模板对象
            name: 模板名称
            
        Returns:
            str: 模板文件路径
        """
        template_path = self.templates_dir / f"{name}.json"
        template.save_to_file(str(template_path))
        
        # 清除缓存
        self.get_template_by_name.cache_clear()
        
        return str(template_path)
    
    def create_project_report_template(self) -> ReportTemplate:
        """
        创建项目报告模板
        
        Returns:
            ReportTemplate: 项目报告模板
        """
        template = ReportTemplate(
            title="{{project_name}} - 项目报告",
            description="本报告由系统自动生成，包含项目的基本信息和详细说明。",
            metadata={
                "作者": "{{author}}",
                "日期": "{{date}}",
                "项目ID": "{{project_id}}",
                "生成时间": "{{generation_date}}"
            }
        )
        
        # 添加项目概述部分
        overview_section = ReportSection(
            title="项目概述",
            content=(
                "本项目是一个{{project_type}}，主要目标是{{project_goal}}。\n"
                "项目开始于{{project_start_date}}，计划完成于{{project_end_date}}。\n"
                "\n"
                "## 项目背景\n"
                "\n"
                "{{project_background}}\n"
            )
        )
        template.add_section(overview_section)
        
        # 添加技术栈部分
        tech_stack_section = ReportSection(
            title="技术栈",
            content=(
                "本项目使用了以下技术栈：\n"
                "\n"
                "- 前端：{{frontend_tech}}\n"
                "- 后端：{{backend_tech}}\n"
                "- 数据库：{{database_tech}}\n"
                "- 部署：{{deployment_tech}}\n"
                "- 其他工具：{{other_tools}}\n"
            )
        )
        template.add_section(tech_stack_section)
        
        # 添加系统架构部分
        architecture_section = ReportSection(
            title="系统架构",
            content=(
                "{{system_architecture_description}}\n"
                "\n"
                "### 主要组件\n"
                "\n"
                "{{system_components}}\n"
                "\n"
                "### 数据流\n"
                "\n"
                "{{data_flow}}\n"
            )
        )
        template.add_section(architecture_section)
        
        # 添加功能特性部分
        features_section = ReportSection(
            title="功能特性",
            content="{{features_description}}"
        )
        template.add_section(features_section)
        
        # 添加实现细节部分
        implementation_section = ReportSection(
            title="实现细节",
            content=(
                "{{implementation_details}}\n"
                "\n"
                "### 关键算法\n"
                "\n"
                "{{key_algorithms}}\n"
                "\n"
                "### 挑战与解决方案\n"
                "\n"
                "{{challenges_and_solutions}}\n"
            )
        )
        template.add_section(implementation_section)
        
        # 添加测试与评估部分
        testing_section = ReportSection(
            title="测试与评估",
            content=(
                "{{testing_methodology}}\n"
                "\n"
                "### 测试结果\n"
                "\n"
                "{{testing_results}}\n"
                "\n"
                "### 性能评估\n"
                "\n"
                "{{performance_evaluation}}\n"
            )
        )
        template.add_section(testing_section)
        
        # 添加结论与展望部分
        conclusion_section = ReportSection(
            title="结论与展望",
            content=(
                "{{conclusion}}\n"
                "\n"
                "### 未来工作\n"
                "\n"
                "{{future_work}}\n"
            )
        )
        template.add_section(conclusion_section)
        
        # 添加参考文献部分
        references_section = ReportSection(
            title="参考文献",
            content="{{references}}"
        )
        template.add_section(references_section)
        
        # 添加附录部分
        appendix_section = ReportSection(
            title="附录",
            content="{{appendix}}"
        )
        template.add_section(appendix_section)
        
        return template
    
    def generate_report(
        self,
        template: ReportTemplate,
        data: Dict[str, Any],
        format: ReportFormat = ReportFormat.MARKDOWN,
        output_path: Optional[str] = None,
        include_toc: bool = True,
        include_code_highlighting: bool = True,
        include_styles: bool = True,
        include_charts: bool = False,
        chart_data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> str:
        """
        生成报告
        
        Args:
            template: 报告模板
            data: 报告数据
            format: 报告格式
            output_path: 输出路径
            include_toc: 是否包含目录
            include_code_highlighting: 是否包含代码高亮
            include_styles: 是否包含样式
            include_charts: 是否包含图表
            chart_data: 图表数据
            use_cache: 是否使用缓存
            
        Returns:
            str: 报告文件路径
            
        Raises:
            ReportGenerationException: 生成报告失败
        """
        try:
            # 计算缓存键
            if use_cache:
                cache_key = self._generate_cache_key(template, data, format, include_toc, 
                                                    include_code_highlighting, include_styles,
                                                    include_charts, chart_data)
                cache_path = self.cache_dir / f"{cache_key}"
                
                # 检查缓存
                if cache_path.exists():
                    logger.info(f"从缓存加载报告：{cache_path}")
                    
                    # 确定输出路径
                    if not output_path:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"report_{timestamp}"
                        
                        if format == ReportFormat.MARKDOWN:
                            filename += ".md"
                        elif format == ReportFormat.DOCX:
                            filename += ".docx"
                        elif format == ReportFormat.PDF:
                            filename += ".pdf"
                        
                        output_path = str(self.reports_dir / filename)
                    
                    # 复制缓存文件到输出路径
                    import shutil
                    shutil.copy2(cache_path, output_path)
                    
                    return output_path
            
            # 获取模板内容
            template_content = template.to_markdown()
            
            # 替换变量
            report_content = self._replace_variables(template_content, data)
            
            # 如果需要目录，添加目录
            if include_toc:
                report_content = f"[TOC]\n\n{report_content}"
            
            # 确定输出路径
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}"
                
                if format == ReportFormat.MARKDOWN:
                    filename += ".md"
                elif format == ReportFormat.DOCX:
                    filename += ".docx"
                elif format == ReportFormat.PDF:
                    filename += ".pdf"
                
                output_path = str(self.reports_dir / filename)
            
            # 根据格式生成报告
            if format == ReportFormat.MARKDOWN:
                # 直接保存Markdown内容
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
                    
                # 缓存报告
                if use_cache:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(report_content)
                
            elif format == ReportFormat.DOCX:
                # 使用格式化服务将Markdown转换为DOCX
                self.formatter.markdown_to_docx(
                    report_content,
                    output_path,
                    include_toc=include_toc,
                    include_code_highlighting=include_code_highlighting,
                    include_styles=include_styles,
                    include_charts=include_charts,
                    chart_data=chart_data
                )
                
                # 缓存报告
                if use_cache:
                    import shutil
                    shutil.copy2(output_path, cache_path)
                
            elif format == ReportFormat.PDF:
                # 先生成Markdown文件
                md_path = output_path.replace(".pdf", ".md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
                
                # 使用格式化服务将Markdown转换为PDF
                self.formatter.markdown_to_pdf(
                    report_content,
                    output_path,
                    include_toc=include_toc,
                    include_code_highlighting=include_code_highlighting,
                    include_styles=include_styles,
                    include_charts=include_charts,
                    chart_data=chart_data
                )
                
                # 删除临时Markdown文件
                if os.path.exists(md_path):
                    os.remove(md_path)
                
                # 缓存报告
                if use_cache:
                    import shutil
                    shutil.copy2(output_path, cache_path)
            
            logger.info(f"报告已生成：{output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"生成报告失败：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise ReportGenerationException(f"生成报告失败：{str(e)}")
    
    def _generate_cache_key(self, template: ReportTemplate, data: Dict[str, Any], 
                           format: ReportFormat, include_toc: bool, 
                           include_code_highlighting: bool, include_styles: bool,
                           include_charts: bool, chart_data: Optional[Dict[str, Any]]) -> str:
        """
        生成缓存键
        
        Args:
            template: 报告模板
            data: 报告数据
            format: 报告格式
            include_toc: 是否包含目录
            include_code_highlighting: 是否包含代码高亮
            include_styles: 是否包含样式
            include_charts: 是否包含图表
            chart_data: 图表数据
            
        Returns:
            str: 缓存键
        """
        # 组合参数
        cache_data = {
            "template": template.to_dict(),
            "data": data,
            "format": str(format),
            "include_toc": include_toc,
            "include_code_highlighting": include_code_highlighting,
            "include_styles": include_styles,
            "include_charts": include_charts,
            "chart_data": chart_data
        }
        
        # 序列化并计算哈希
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode('utf-8')).hexdigest() + f".{format}"
    
    def _replace_variables(self, content: str, data: Dict[str, Any]) -> str:
        """
        替换内容中的变量占位符
        
        支持多种占位符格式：
        1. {{variable}} - 双大括号
        2. {variable} - 单大括号
        3. ${variable} - 美元符号加大括号
        4. {{nested.value}} - 支持嵌套访问对象属性
        
        Args:
            content: 包含变量占位符的内容
            data: 变量数据
            
        Returns:
            str: 替换变量后的内容
        """
        result = content
        
        # 扁平化嵌套数据
        flat_data = self._flatten_data(data)
        
        # 替换双大括号格式的变量 {{variable}}
        for key, value in flat_data.items():
            pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
            result = re.sub(pattern, str(value) if value is not None else "", result)
        
        # 替换单大括号格式的变量 {variable}
        for key, value in flat_data.items():
            pattern = r"\{\s*" + re.escape(key) + r"\s*\}"
            result = re.sub(pattern, str(value) if value is not None else "", result)
        
        # 替换美元符号加大括号格式的变量 ${variable}
        for key, value in flat_data.items():
            pattern = r"\$\{\s*" + re.escape(key) + r"\s*\}"
            result = re.sub(pattern, str(value) if value is not None else "", result)
        
        return result
    
    def _flatten_data(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """
        扁平化嵌套数据
        
        将嵌套的字典扁平化为单层字典，使用点号连接键名。
        例如：{"a": {"b": 1}} -> {"a.b": 1}
        
        Args:
            data: 嵌套字典
            prefix: 键前缀
            
        Returns:
            Dict[str, Any]: 扁平化的字典
        """
        result = {}
        
        for key, value in data.items():
            new_key = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # 递归扁平化嵌套字典
                nested_result = self._flatten_data(value, f"{new_key}.")
                result.update(nested_result)
            elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                # 处理字典列表
                for i, item in enumerate(value):
                    nested_result = self._flatten_data(item, f"{new_key}.{i}.")
                    result.update(nested_result)
            else:
                # 普通值
                result[new_key] = value
        
        return result

    def get_report_by_id(self, report_id: int) -> Optional[Report]:
        return self.db.query(Report).filter(Report.id == report_id).first()

    def delete_report(self, report_id: int, user_id: int) -> Optional[Report]:
        """
        删除指定ID的报告
        """
        report = self.db.query(Report).filter(Report.id == report_id, Report.owner_id == user_id).first()
        if not report:
            return None
        
        # 可选：如果报告有关联的文件，也在这里处理删除逻辑
        # import os
        # if report.file_path and os.path.exists(report.file_path):
        #     os.remove(report.file_path)

        self.db.delete(report)
        self.db.commit()
        return report

    def update_report_status(self, report_id: int, status: ReportStatusEnum) -> Optional[Report]:
        """
        更新报告状态
        """
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return None
        
        report.status = status
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report(self, report_id: int, user_id: int) -> Optional[Report]:
        """根据ID和用户ID获取报告"""
        report = self.db.query(Report).filter(Report.id == report_id, Report.user_id == user_id).first()
        return report

    async def generate_and_get_pdf_path(self, report_id: int) -> str:
        """为指定报告生成PDF并返回文件路径"""
        
        # 假设我们能通过 report_id 获取到报告的所有必需信息
        # 在实际应用中，这里需要从数据库中获取报告、模板和数据
        db_report = self.db.query(Report).filter(Report.id == report_id).first()
        if not db_report:
            raise ReportGenerationException(f"ID为 {report_id} 的报告未找到")

        # 1. 获取模板
        # 假设 template_name 存储在 db_report.template_name 或类似字段
        template = self.get_template_by_name(db_report.template_name)

        # 2. 准备数据
        # 实际情况会更复杂，需要聚合多个数据源
        competition_data = self.db.query(Competition).filter(Competition.id == db_report.competition_id).first()
        user_data = self.db.query(User).filter(User.id == db_report.user_id).first()
        
        report_data = {
            "project_name": competition_data.name if competition_data else "N/A",
            "team_name": "示例团队", # 示例数据
            "student_name": user_data.username if user_data else "N/A",
            "student_id": "0000001", # 示例数据
            "date": datetime.now().strftime("%Y-%m-%d"),
            "competition": competition_data.to_dict() if competition_data else {},
        }

        # 3. 调用核心生成方法
        pdf_path = self.generate_report(
            template=template,
            data=report_data,
            format=ReportFormat.PDF
        )
        return pdf_path 