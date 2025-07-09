"""
绠€鍖栨姤鍛婄敓鎴怉PI绔偣

鎻愪緵绠€鍖栫殑鎶ュ憡鐢熸垚API鎺ュ彛锛屾洿瀹规槗涓庡閮ㄧ郴缁熼泦鎴愩€?
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.app.api.deps import get_db
from backend.app.core.exceptions import handle_exceptions, ReportGenerationException
from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat
from backend.app.schemas.report import ReportFormatEnum, GenerateReportResponse


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
    title: str
    sections: List[ReportContentSection]

class SimpleReportResponse(BaseModel):
    report_id: int
    file_path: Optional[str] = None
    message: str


# 瑙ｅ喅寰幆寮曠敤
ReportContentSection.update_forward_refs()


router = APIRouter()


@router.post("/generate", response_model=GenerateReportResponse)
@handle_exceptions
async def generate_simple_report(
    request: SimpleReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    鐢熸垚绠€鍖栨姤鍛?
    
    浣跨敤绠€鍖栫殑璇锋眰鏍煎紡鐢熸垚鎶ュ憡銆傛敮鎸丮arkdown鍜孌OCX鏍煎紡銆?
    """
    # 鍒涘缓鎶ュ憡鏈嶅姟
    report_service = ReportService(db)
    
    # 鍒涘缓妯℃澘
    template = ReportTemplate(
        title=request.title,
        description=request.description
    )
    
    # 娣诲姞閮ㄥ垎
    for section_data in request.sections:
        section = ReportSection(
            title=section_data.title,
            content=section_data.content,
            level=section_data.level
        )
        template.add_section(section)
    
    # 纭畾鎶ュ憡鏍煎紡
    report_format = ReportFormat.MARKDOWN
    if request.format.lower() == "docx":
        report_format = ReportFormat.DOCX
    
    # 鑾峰彇鏍煎紡鍖栭€夐」
    formatting_options = request.formatting_options
    include_toc = formatting_options.get("include_toc", True)
    include_code_highlighting = formatting_options.get("include_code_highlighting", True)
    include_styles = formatting_options.get("include_styles", True)
    include_charts = formatting_options.get("include_charts", False)
    
    # 鐢熸垚鎶ュ憡
    try:
        output_path = report_service.generate_report(
            template=template,
            data=request.data,
            format=report_format,
            include_toc=include_toc,
            include_code_highlighting=include_code_highlighting,
            include_styles=include_styles,
            include_charts=include_charts
        )
        
        # 鑾峰彇鏂囦欢鍚?
        file_name = os.path.basename(output_path)
        
        # 杩斿洖缁撴灉
        return GenerateReportResponse(
            success=True,
            message="鎶ュ憡鐢熸垚鎴愬姛",
            file_path=output_path,
            file_name=file_name,
            format=ReportFormatEnum.MARKDOWN if report_format == ReportFormat.MARKDOWN else ReportFormatEnum.DOCX
        )
    except ReportGenerationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"鎶ュ憡鐢熸垚澶辫触: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"鏈嶅姟鍣ㄩ敊璇? {str(e)}"
        ) 