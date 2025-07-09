"""
Pydantic模型模块
包含所有用于API请求和响应的Pydantic模型
"""

from backend.app.schemas.component import (
    ComponentBase,
    ComponentCreate,
    ComponentUpdate,
    ComponentResponse,
    ComponentVersionBase,
    ComponentVersionResponse,
    ComponentList
)

from backend.app.schemas.ai_engine import (
    AIModelBase,
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelList,
    TemplateBase,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateList,
    PersonalizeCodeRequest,
    PersonalizeCodeResponse,
    LogResponse
)

from backend.app.schemas.report import (
    ReportFormatEnum,
    ReportSectionCreate,
    ReportSectionResponse,
    ReportTemplateCreate,
    ReportTemplateResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    ProjectReportRequest
) 

from backend.app.schemas.competition import (
    CompetitionBase,
    CompetitionCreate,
    CompetitionUpdate,
    Competition
) 