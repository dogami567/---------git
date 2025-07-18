"""
报告生成服务

提供报告模板管理和报告生成功能。支持多种格式输出，包括Markdown、DOCX和PDF。
"""

import os
import re
import json
import logging
import hashlib
import jinja2
import markdown
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
from backend.app.models.report import Report, ReportStatusEnum, ReportFormatEnum, ReportTemplate as ReportTemplateModel
from backend.app.schemas.report import CompetitionReportCreate
from backend.app.models.competition import Competition
from backend.app.models.user import User


# 配置日志
logger = logging.getLogger(__name__)


class StructureSection:
    """
    报告结构中的一个部分
    """
    
    def __init__(self, title: str, content: str = "", level: int = 1):
        self.title = title
        self.content = content
        self.level = max(1, min(6, level))
        self.subsections: List['StructureSection'] = []
    
    def add_subsection(self, subsection: 'StructureSection') -> None:
        self.subsections.append(subsection)
    
    def to_markdown(self) -> str:
        md = f"{'#' * self.level} {self.title}\\n\\n"
        if self.content:
            md += f"{self.content}\\n\\n"
        for subsection in self.subsections:
            md += subsection.to_markdown()
        return md
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "level": self.level,
            "subsections": [subsection.to_dict() for subsection in self.subsections]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StructureSection':
        section = cls(
            title=data["title"],
            content=data.get("content", ""),
            level=data.get("level", 1)
        )
        for subsection_data in data.get("subsections", []):
            section.add_subsection(cls.from_dict(subsection_data))
        return section


class ReportStructure:
    """
    报告的整体结构，用于构建和序列化。
    """
    
    def __init__(self, title: str, description: str = "", metadata: Dict[str, Any] = None):
        self.title = title
        self.description = description
        self.metadata = metadata or {}
        self.sections: List[StructureSection] = []
        self.version = "1.1.0"
        self.created_at = datetime.now().isoformat()
    
    def add_section(self, section: StructureSection) -> None:
        self.sections.append(section)
    
    def to_markdown(self) -> str:
        md = f"# {self.title}\\n\\n"
        if self.description:
            md += f"{self.description}\\n\\n"
        if self.metadata:
            md += "## 元数据\\n\\n"
            for key, value in self.metadata.items():
                md += f"- **{key}**: {value}\\n"
            md += "\\n"
        for section in self.sections:
            md += section.to_markdown()
        return md
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
            "sections": [section.to_dict() for section in self.sections],
            "version": self.version,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportStructure':
        # 从 "structure" 键（如果存在）或数据本身获取结构信息
        structure_data = data.get("structure", data)
        if not isinstance(structure_data, dict):
             raise ValueError("用于创建报告结构的数据格式无效。")

        template = cls(
            title=structure_data.get("title", ""),  # 优先使用结构内的标题
            description=structure_data.get("description", ""),
            metadata=structure_data.get("metadata", {})
        )

        # 如果顶层数据中有 'title'，用它来覆盖
        if 'title' in data and isinstance(data['title'], str):
            template.title = data['title']
        
        template.version = structure_data.get("version", "1.0.0")
        template.created_at = structure_data.get("created_at", datetime.now().isoformat())
        
        for section_data in structure_data.get("sections", []):
            template.add_section(StructureSection.from_dict(section_data))
        return template
    
    def save_to_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ReportStructure':
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"加载报告结构文件失败: {file_path}, error: {e}")
            raise


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
        self.logger = logger
        self.formatter = ReportFormatterService()
        self.reports_dir = Path(settings.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir = Path(settings.REPORTS_TEMPLATES_DIR)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.reports_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def create_competition_report(self, report_in: CompetitionReportCreate, user_id: int) -> Report:
        """为指定竞赛创建新的报告"""
        
        # 验证竞赛ID是否存在
        competitions = self.db.query(Competition).filter(Competition.id.in_(report_in.competition_ids)).all()
        if len(competitions) != len(set(report_in.competition_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="一个或多个竞赛ID未找到"
            )

        extra_data = {
            "competition_ids": report_in.competition_ids,
            "included_sections": report_in.included_sections
        }
        
        db_report = Report(
            title=report_in.title,
            owner_id=user_id,
            template_id=report_in.template_id,
            status=ReportStatusEnum.PENDING,
            format=report_in.format.value,
            extra_info=extra_data
        )
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        
        return db_report

    def get_reports_by_user(self, user_id: int) -> List[Report]:
        """获取用户的所有报告"""
        return self.db.query(Report).filter(Report.owner_id == user_id).order_by(Report.created_at.desc()).all()

    @lru_cache(maxsize=32)
    def get_template_by_name(self, name: str) -> ReportStructure:
        """
        根据名称获取模板
        
        Args:
            name: 模板名称
            
        Returns:
            ReportStructure: 模板对象
            
        Raises:
            ValueError: 如果模板不存在
        """
        template_file = self.templates_dir / f"{name}.json"
        
        if not template_file.exists():
            db_template = self.db.query(ReportTemplateModel).filter(ReportTemplateModel.title == name).first()
            if not db_template:
                raise FileNotFoundError(f"模板 '{name}' 在文件或数据库中均未找到。")
            
            template_data = db_template.structure
            # 确保将数据库中的title字段也包含进去
            if isinstance(template_data, dict):
                template_data['title'] = db_template.title

            return ReportStructure.from_dict(template_data)

        return ReportStructure.load_from_file(str(template_file))
    
    def save_template(self, template: ReportStructure, name: str) -> str:
        """
        保存模板
        
        Args:
            template: 模板对象
            name: 模板名称
            
        Returns:
            str: 模板文件路径
        """
        file_path = self.templates_dir / f"{name}.json"
        template.save_to_file(str(file_path))
        
        # 清除缓存
        self.get_template_by_name.cache_clear()
        
        return str(file_path)
    
    def create_project_report_template(self) -> ReportStructure:
        """
        创建项目报告模板
        
        Returns:
            ReportStructure: 项目报告模板
        """
        template = ReportStructure(
            title="项目周报",
            description="一个标准的项目周报模板，用于跟踪项目进度。",
            metadata={"version": "1.0", "author": "系统内置"}
        )
        
        # 添加项目概述部分
        overview_section = StructureSection(
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
        tech_stack_section = StructureSection(
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
        architecture_section = StructureSection(
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
        features_section = StructureSection(
            title="功能特性",
            content="{{features_description}}"
        )
        template.add_section(features_section)
        
        # 添加实现细节部分
        implementation_section = StructureSection(
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
        testing_section = StructureSection(
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
        conclusion_section = StructureSection(
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
        references_section = StructureSection(
            title="参考文献",
            content="{{references}}"
        )
        template.add_section(references_section)
        
        # 添加附录部分
        appendix_section = StructureSection(
            title="附录",
            content="{{appendix}}"
        )
        template.add_section(appendix_section)
        
        return template
    
    def generate_report(self, template: ReportStructure, data: dict, format: ReportFormatEnum, output_path: str):
        """
        根据模板和数据生成报告内容。
        这是一个简化的实现。
        """
        try:
            # 1. 使用Jinja2渲染模板
            md_template_str = template.to_markdown()
            jinja_template = jinja2.Template(md_template_str)
            md_content = jinja_template.render(data)
            
            # 2. 根据格式进行转换和保存
            if format == ReportFormatEnum.MARKDOWN:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                return output_path

            # 对于PDF和DOCX，我们先将Markdown转为HTML
            html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
            
            # 添加一些基础样式
            html_with_style = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'SimSun', sans-serif; line-height: 1.6; }}
                    h1, h2, h3 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f2f2f2; }}
                    code {{ font-family: 'Courier New', monospace; background-color: #eee; padding: 2px 4px; border-radius: 4px; }}
                    pre > code {{ display: block; padding: 10px; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            if format == ReportFormatEnum.PDF:
                from weasyprint import HTML
                # 直接将带样式的HTML字符串传递给weasyprint
                HTML(string=html_with_style).write_pdf(output_path)
                
            elif format == ReportFormatEnum.DOCX:
                try:
                    import pypandoc
                    # 使用pypandoc将HTML转换为docx
                    pypandoc.convert_text(html_with_style, 'docx', format='html', outputfile=output_path)
                except (ImportError, OSError) as e:
                    self.logger.warning(f"pypandoc 或其依赖未找到。DOCX 导出功能受限: {e}")
                    raise ReportGenerationException("无法生成DOCX，缺少pypandoc或其系统依赖。")
                except Exception as e:
                    # 捕获 pypandoc 可能抛出的其他所有异常
                    # 检查是否为 PandocNotFoundError
                    if 'PandocNotFoundError' in str(type(e)):
                         self.logger.warning(f"Pandoc 未安装或未在 PATH 中。DOCX 导出功能受限: {e}")
                         raise ReportGenerationException("无法生成DOCX，缺少Pandoc程序。")
                    self.logger.error(f"使用pypandoc生成DOCX时发生未知错误: {e}", exc_info=True)
                    raise ReportGenerationException(f"生成DOCX时发生未知错误: {e}")
            
            return output_path

        except Exception as e:
            self.logger.error(f"生成报告时发生未知错误: {e}", exc_info=True)
            raise ReportGenerationException(f"生成报告失败：生成{format.value}时发生未知错误: {e}")
    def _generate_cache_key(self, template: ReportStructure, data: Dict[str, Any], 
                           format: ReportFormatEnum, include_toc: bool, 
                           include_code_highlighting: bool, include_styles: bool,
                           include_charts: bool, chart_data: Optional[Dict[str, Any]]) -> str:
        """
        为报告生成缓存键
        
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
        # 使用模板、数据和所有格式化选项的哈希值作为缓存键
        # 确保数据字典是可预测的顺序
        # 对非字符串类型进行稳健的序列化
        try:
            # 尝试使用可排序的json dump来标准化数据
            data_str = json.dumps(data, sort_keys=True)
        except TypeError:
            # 如果失败，回退到简单的str表示
            data_str = str(data)
            
        key_string = (
            template.to_markdown() + 
            data_str + 
            f"{format.value}{include_toc}{include_code_highlighting}{include_styles}{include_charts}" +
            json.dumps(chart_data, sort_keys=True) if chart_data else ""
        )
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
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
        """删除一个报告，并确保只有所有者才能删除"""
        report_to_delete = self.db.query(Report).filter(
            Report.id == report_id, Report.owner_id == user_id
        ).first()

        if report_to_delete:
            self.db.delete(report_to_delete)
            self.db.commit()
        return report_to_delete

    def update_report_status(self, report_id: int, status: ReportStatusEnum) -> Optional[Report]:
        """更新报告状态"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return None
        
        report.status = status
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report(self, report_id: int, user_id: int) -> Optional[Report]:
        """获取指定ID的报告，并验证用户权限"""
        report = self.db.query(Report).filter(Report.id == report_id, Report.owner_id == user_id).first()
        return report

    async def generate_and_get_report_path(self, report_id: int, user_id: int) -> tuple[str, str, str]:
        """
        为指定报告生成文件并返回其路径、MIME类型和文件名。
        此方法现在是通用的，可以处理所有支持的报告格式。
        """
        db_report = self.get_report(report_id, user_id)
        if not db_report:
            raise HTTPException(status_code=404, detail="报告未找到")

        # 从数据库记录中获取报告格式
        report_format = ReportFormatEnum(db_report.format)
        
        # 定义MIME类型映射
        mime_types = {
            ReportFormatEnum.PDF: "application/pdf",
            ReportFormatEnum.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ReportFormatEnum.MARKDOWN: "text/markdown"
        }
        media_type = mime_types.get(report_format, "application/octet-stream")

        # 动态生成文件名
        file_extension = report_format.value.lower()
        filename = f"{db_report.title or 'report'}_{db_report.id}.{file_extension}"

        # 检查报告模板是否存在
        template = self.db.query(ReportTemplateModel).filter(ReportTemplateModel.id == db_report.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail=f"ID为 {db_report.template_id} 的模板未找到")
        
        template_structure = ReportStructure.from_dict(template.structure)

        # 准备模板数据
        context = {
            "report": db_report,
            "user": db_report.owner,
            "competitions": self.db.query(Competition).filter(Competition.id.in_(db_report.extra_info.get("competition_ids", []))).all()
        }

        # --- 新增：确保所有模板变量都存在于上下文中 ---
        md_template_str = template_structure.to_markdown()
        # 使用正则表达式查找所有 {{...}} 格式的变量
        template_variables = set(re.findall(r"\\{\\{\\s*([^\\}]+?)\\s*\\}\\}", md_template_str))
        
        for var in template_variables:
            # 对于嵌套变量如 "user.name"，我们只检查根变量 "user"
            root_var = var.split('.')[0]
            if root_var not in context:
                self.logger.warning(f"模板变量 '{var}' 在上下文中缺失，将使用空字符串填充。")
                context[root_var] = ""
        # --- 修复结束 ---

        # 定义缓存文件路径
        cache_key = self._generate_cache_key(
            template=template_structure,
            data=context,
            format=report_format,
            # 为缺失的参数提供默认值
            include_toc=False,
            include_code_highlighting=False,
            include_styles=True, # 默认启用样式
            include_charts=False,
            chart_data=None
        )
        cache_file_path = self.cache_dir / f"{cache_key}.{file_extension}"

        # 如果缓存文件已存在，直接返回路径
        if cache_file_path.exists():
            return str(cache_file_path), media_type, filename

        # 调用核心生成方法
        generated_path = self.generate_report(
            template=template_structure,
            data=context,
            format=report_format,
            output_path=str(cache_file_path)
        )
        
        if not generated_path:
             raise ReportGenerationException("报告文件生成失败，未返回有效路径。")

        return generated_path, media_type, filename

    def get_user_reports_paginated(self, user_id: int, page: int, page_size: int):
        """
        分页获取指定用户的报告列表。
        """
        # 这里需要实现分页逻辑，例如：
        # total_reports = self.db.query(Report).filter(Report.owner_id == user_id).count()
        # reports = self.db.query(Report).filter(Report.owner_id == user_id).offset((page - 1) * page_size).limit(page_size).all()
        # return total_reports, reports 