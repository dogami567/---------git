"""
报告生成API端点

提供报告生成和模板管理的API端点。
"""

from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from backend.app.api import deps
from backend.app.core.exceptions import handle_exceptions
from backend.app.models.user import User
from backend.app.schemas.report import (
    CompetitionReportCreate,
    Report,
    ReportTemplateResponse,
)
from backend.app.services import report_service


router = APIRouter()


@router.post("/", response_model=Report, status_code=status.HTTP_201_CREATED)
@handle_exceptions
def create_competition_report(
    report_in: CompetitionReportCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    为指定竞赛创建新的报告。
    """
    report_service_instance = report_service.ReportService(db)
    db_report = report_service_instance.create_competition_report(
        report_in=report_in, user_id=current_user.id
    )
    return db_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
def delete_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    删除一个报告
    """
    report_service_instance = report_service.ReportService(db)
    deleted_report = report_service_instance.delete_report(report_id=report_id, user_id=current_user.id)
    if not deleted_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告未找到或您没有权限删除",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/templates", response_model=List[ReportTemplateResponse])
@handle_exceptions
def get_report_templates(db: Session = Depends(deps.get_db)):
    """
    获取可用的报告模板列表
    """
    return report_service.get_all_templates(db)


@router.get("/download/{report_id}", response_class=FileResponse)
@handle_exceptions
async def download_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    下载指定ID的报告（PDF格式）
    """
    report_service_instance = report_service.ReportService(db)
    
    # 1. 获取报告
    db_report = report_service_instance.get_report(report_id=report_id, user_id=current_user.id)
    if not db_report:
        raise HTTPException(status_code=404, detail="报告未找到或您没有权限访问")

    # 2. 生成PDF报告
    try:
        # 假设报告服务有一个方法可以生成PDF并返回路径
        pdf_path = await report_service_instance.generate_and_get_pdf_path(report_id=report_id)
        
        # 3. 返回文件响应
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="生成的PDF文件未找到")
        
        report_filename = f"report_{db_report.competition.name}_{report_id}.pdf"
        
        return FileResponse(
            path=pdf_path,
            filename=report_filename,
            media_type='application/pdf'
        )
    except Exception as e:
        # 这里的异常处理可以更精细
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}") 