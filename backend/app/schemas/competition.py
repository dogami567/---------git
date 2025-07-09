from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# 基础模型，包含所有模型共享的字段
class CompetitionBase(BaseModel):
    title: str
    description: Optional[str] = None
    organizer: str
    category: str
    registration_deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    website: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# 创建时所需的模型，继承自基础模型
class CompetitionCreate(CompetitionBase):
    pass


# 更新时所需的模型，所有字段都是可选的
class CompetitionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    organizer: Optional[str] = None
    category: Optional[str] = None
    registration_deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


# 用于API响应的模型，包含数据库中的完整信息
class Competition(CompetitionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 