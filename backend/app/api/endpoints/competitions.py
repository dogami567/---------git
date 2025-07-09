from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.core.exceptions import NotFoundException, handle_exceptions
from backend.app.api import deps
from backend.app.models.competition import Competition as CompetitionModel
from backend.app.schemas.competition import Competition, CompetitionCreate, CompetitionUpdate

# 创建路由器
router = APIRouter()


@router.get("", response_model=List[Competition])
@handle_exceptions
async def get_competitions(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    keyword: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    level_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """
    从数据库获取竞赛列表，支持分页和多种过滤条件
    """
    query = db.query(CompetitionModel)

    if keyword:
        query = query.filter(CompetitionModel.title.ilike(f"%{keyword}%"))

    if category_id and category_id.isdigit():
        query = query.filter(CompetitionModel.category_id == int(category_id))

    if level_id and level_id.isdigit():
        query = query.filter(CompetitionModel.level_id == int(level_id))

    # # 可以在这里根据 status 添加更多关于日期的过滤逻辑
    # from datetime import date
    # today = date.today()
    # if status == "upcoming":
    #     query = query.filter(CompetitionModel.start_date > today)
    # elif status == "ongoing":
    #      query = query.filter(CompetitionModel.start_date <= today, CompetitionModel.end_date >= today)
    # elif status == "ended":
    #      query = query.filter(CompetitionModel.end_date < today)

    competitions = query.offset(skip).limit(limit).all()
    return competitions


class HotCompetition(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


@router.get("/hot", response_model=List[HotCompetition])
@handle_exceptions
async def get_hot_competitions(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(deps.get_db)
):
    """
    获取热门竞赛列表
    """
    # 这里的"热门"逻辑是简化的，实际可以根据浏览量、订阅数等排序
    hot_competitions = db.query(CompetitionModel).order_by(CompetitionModel.id.desc()).limit(limit).all()
    return hot_competitions


@router.get("/categories", response_model=List[str])
@handle_exceptions
async def get_competition_categories(db: Session = Depends(deps.get_db)):
    """
    获取所有竞赛类别
    """
    # 假设类别存储在某个地方或可以从现有竞赛中提取
    # 这里为了演示，返回硬编码的列表
    return ["科技创新", "学科竞赛", "创业实践", "人文社科"]


@router.get("/levels", response_model=List[str])
@handle_exceptions
async def get_competition_levels(db: Session = Depends(deps.get_db)):
    """
    获取所有竞赛级别
    """
    # 假设级别是固定的
    return ["校级", "省级", "国家级", "国际级"]


@router.get("/{competition_id}", response_model=Competition)
@handle_exceptions
async def get_competition(
    competition_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    根据ID从数据库获取特定竞赛详情
    """
    db_competition = db.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
    if db_competition is None:
        raise NotFoundException(detail=f"竞赛ID {competition_id} 不存在")
    return db_competition


@router.post("/", response_model=Competition, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_competition(
    *,
    db: Session = Depends(deps.get_db),
    competition_in: CompetitionCreate
):
    """
    创建新竞赛并保存到数据库
    """
    db_competition = CompetitionModel(**competition_in.dict())
    db.add(db_competition)
    db.commit()
    db.refresh(db_competition)
    return db_competition


@router.put("/{competition_id}", response_model=Competition)
@handle_exceptions
async def update_competition(
    *,
    db: Session = Depends(deps.get_db),
    competition_id: int,
    competition_in: CompetitionUpdate
):
    """
    更新数据库中的竞赛信息
    """
    db_competition = db.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
    if not db_competition:
        raise NotFoundException(detail=f"竞赛ID {competition_id} 不存在")
    
    update_data = competition_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_competition, field, value)
        
    db.add(db_competition)
    db.commit()
    db.refresh(db_competition)
    return db_competition


@router.delete("/{competition_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_competition(
    *,
    db: Session = Depends(deps.get_db),
    competition_id: int
):
    """
    从数据库中删除竞赛
    """
    db_competition = db.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
    if not db_competition:
        raise NotFoundException(detail=f"竞赛ID {competition_id} 不存在")
        
    db.delete(db_competition)
    db.commit()
    
    return 