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
    
    try:
        # 调用服务层方法，该方法会处理查找、生成和路径返回
        file_path, media_type, filename = await report_service_instance.generate_and_get_pdf_path(
            report_id=report_id, user_id=current_user.id
        )
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="生成的报告文件未找到")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type
        )
    except HTTPException as http_exc:
        raise http_exc # 重新抛出已知的HTTP异常
    except Exception as e:
        # 捕获其他未知异常
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}") 