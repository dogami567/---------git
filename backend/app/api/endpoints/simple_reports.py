"""
绠€鍖栨姤鍛婄敓鎴怉PI绔偣

鎻愪緵绠€鍖栫殑鎶ュ憡鐢熸垚API鎺ュ彛锛屾洿瀹规槗涓庡閮ㄧ郴缁熼泦鎴愩€?
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.app.api import deps
from backend.app.core.exceptions import handle_exceptions, ReportGenerationException
from backend.app.services.report_service import ReportService, ReportStructure, StructureSection
from backend.app.models.report import ReportFormatEnum
from backend.app.schemas.report import GenerateReportResponse
from datetime import datetime


class TextBlock(BaseModel):
    """文本块"""
    type: str = "text"
    content: str

class ImageBlock(BaseModel):
    """图片块"""
    type: str = "image"
    url: str
    caption: Optional[str] = None

class ListBlock(BaseModel):
    """列表块"""
    type: str = "list"
    items: List[str]

class Heading(BaseModel):
    text: str
    level: int = Field(1, description="标题级别：1-6")

class Paragraph(BaseModel):
    text: str

class ReportContentSection(BaseModel):
    title: str
    elements: List[Dict[str, Any]] # 可以是TextBlock, ImageBlock, ListBlock等

class SimpleReportRequest(BaseModel):
    title: str = Field(..., example="我的简单报告")
    content: str = Field(..., example="这是报告的主要内容。")

class SimpleReportResponse(BaseModel):
    message: str
    report_path: str


# 瑙ｅ喅寰幆寮曠敤
ReportContentSection.update_forward_refs()


router = APIRouter()


@router.post("/simple-report", response_model=GenerateReportResponse)
@handle_exceptions
async def create_simple_report(
    request: SimpleReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
):
    """
    一个简单的端点，用于快速生成包含标题和内容的PDF报告。
    """
    report_service = ReportService(db)
    
    # 1. 创建一个临时的报告结构
    template = ReportStructure(title=request.title)
    template.add_section(StructureSection(title="主要内容", content=request.content))
    
    # 2. 定义报告元数据
    report_data = {
        "report_title": request.title,
        "generation_date": datetime.now().strftime("%Y-%m-%d"),
    }
    
    # 3. 使用后台任务生成报告
    background_tasks.add_task(
        report_service.generate_report,
        template=template,
        data=report_data,
        format=ReportFormatEnum.PDF, # 强制PDF格式
        output_dir_name="simple_reports" # 指定单独的输出目录
    )

    return {"message": "简单报告生成任务已启动，请稍后查看'reports/simple_reports'目录。"}

# ... (保留其他可能存在的路由) 