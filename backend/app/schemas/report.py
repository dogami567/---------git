"""
报告相关的Pydantic模型

定义报告生成和管理相关的数据模型。
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ReportFormatEnum(str, Enum):
    """报告格式枚举"""
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"


class ChartData(BaseModel):
    """图表数据模型"""
    title: str = Field(..., description="图表标题")
    type: str = Field(..., description="图表类型，如'bar', 'line', 'pie'等")
    data: Dict[str, Any] = Field(..., description="图表数据")


class ReportFormattingOptions(BaseModel):
    """报告格式化选项"""
    include_toc: bool = Field(True, description="是否包含目录")
    include_code_highlighting: bool = Field(True, description="是否包含代码高亮")
    include_styles: bool = Field(True, description="是否包含样式")
    include_charts: bool = Field(False, description="是否包含图表")
    charts: Optional[List[ChartData]] = Field(None, description="图表数据列表")


class ReportSectionCreate(BaseModel):
    """报告部分创建模型"""
    title: str = Field(..., description="部分标题")
    content: str = Field("", description="部分内容")
    level: int = Field(1, description="标题级别（1-6）")


class ReportSectionResponse(BaseModel):
    """报告部分响应模型"""
    title: str = Field(..., description="部分标题")
    content: str = Field(..., description="部分内容")
    level: int = Field(..., description="标题级别（1-6）")


class ReportTemplateCreate(BaseModel):
    """报告模板创建模型"""
    title: str = Field(..., description="模板标题")
    description: str = Field("", description="模板描述")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="模板元数据")
    sections: List[ReportSectionCreate] = Field(default_factory=list, description="报告部分列表")


class ReportTemplateResponse(BaseModel):
    """报告模板响应模型"""
    id: int
    title: str = Field(..., description="模板标题")
    description: str = Field(..., description="模板描述")
    structure: Dict[str, Any] = Field(..., description="模板结构")
    extra_info: Optional[Dict[str, Any]] = Field(None, description="模板元数据")

    class Config:
        from_attributes = True


class GenerateReportRequest(BaseModel):
    """生成报告请求模型"""
    template: ReportTemplateCreate = Field(..., description="报告模板")
    data: Dict[str, Any] = Field(default_factory=dict, description="报告数据")
    format: ReportFormatEnum = Field(ReportFormatEnum.MARKDOWN, description="报告格式")
    include_toc: bool = Field(True, description="是否包含目录")
    include_code_highlighting: bool = Field(True, description="是否包含代码高亮")
    include_styles: bool = Field(True, description="是否包含样式")
    include_charts: bool = Field(False, description="是否包含图表")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="图表数据")


class ProjectReportRequest(BaseModel):
    """项目报告请求模型"""
    data: Dict[str, Any] = Field(default_factory=dict, description="项目数据")
    format: ReportFormatEnum = Field(ReportFormatEnum.MARKDOWN, description="报告格式")
    include_toc: bool = Field(True, description="是否包含目录")
    include_code_highlighting: bool = Field(True, description="是否包含代码高亮")
    include_styles: bool = Field(True, description="是否包含样式")
    include_charts: bool = Field(False, description="是否包含图表")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="图表数据")


class GenerateReportResponse(BaseModel):
    """生成报告响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    file_path: str = Field(..., description="文件路径")
    file_name: str = Field(..., description="文件名")
    format: ReportFormatEnum = Field(..., description="报告格式")


# --- 新增：专门用于从前端接收竞赛报告生成请求的模型 ---
class CompetitionReportCreate(BaseModel):
    """竞赛报告创建请求模型"""
    title: str = Field(..., description="报告标题")
    competition_ids: List[int] = Field(..., description="关联的竞赛ID列表")
    template_id: int = Field(..., description="使用的模板ID")
    format: ReportFormatEnum = Field(..., description="报告格式")
    included_sections: List[str] = Field(default_factory=list, description="包含的部分列表")


# --- 新增：用于表示报告本身的模型 ---
class Report(BaseModel):
    """报告基础模型"""
    id: int
    title: str
    owner_id: int
    status: str
    file_path: Optional[str] = None
    extra_info: Optional[Dict[str, Any]] = None
    created_at: Optional[Any] = None # 在实际应用中应为 datetime
    updated_at: Optional[Any] = None # 在实际应用中应为 datetime

    class Config:
        from_attributes = True


# --- 新增：用于API响应的报告模型 ---
class ReportResponse(BaseModel):
    """报告响应模型，用于API返回"""
    id: int
    title: str
    status: str
    file_path: Optional[str] = None
    created_at: Any # 实际应为 datetime
    updated_at: Any # 实际应为 datetime

    class Config:
        from_attributes = True


# 解决循环引用
ReportSectionCreate.update_forward_refs()
ReportSectionResponse.update_forward_refs() 