from typing import List, Optional, Union, Dict, Any

from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, EmailStr, root_validator
from sqlalchemy.orm import Session

from backend.app.core.exceptions import BadRequestException, NotFoundException, handle_exceptions
from backend.app.schemas.report import Report
from backend.app.api import deps
from backend.app.services import report_service
from backend.app.schemas.params import Params, Page
from backend.app.utils import paginate

# 创建路由器
router = APIRouter()


# --- 新增：登录请求模型 (支持用户名或邮箱登录) ---
class UserLogin(BaseModel):
    login_identifier: str  # 可以是用户名或邮箱
    password: str


# --- 新增：Token响应模型 ---
class Token(BaseModel):
    access_token: str
    token_type: str


# 模型定义
class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str


class User(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool = True
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserInDB(User):
    """数据库中的用户模型"""
    hashed_password: str


# 示例数据（实际应用中会从数据库获取）
USERS = [
    {
        "id": 1,
        "email": "student1@example.com",
        "username": "student1",
        "full_name": "张三",
        "university": "北京大学",
        "major": "计算机科学",
        "grade": "大三",
        "is_active": True,
        "is_verified": True,
        "hashed_password": "hashed_password_here"
    },
    {
        "id": 2,
        "email": "student2@example.com",
        "username": "student2",
        "full_name": "李四",
        "university": "清华大学",
        "major": "电子工程",
        "grade": "大二",
        "is_active": True,
        "is_verified": False,
        "hashed_password": "hashed_password_here"
    }
]

# 创建一个模拟的报告数据库
REPORTS_DB = [
    Report(id=1, title='关于"蓝桥杯"的初步分析报告', owner_id=1, status="已生成", file_path="/reports/report_1.pdf", extra_info={"competition_ids": [1]}),
    Report(id=2, title='数学建模竞赛回顾与分析', owner_id=1, status="生成中", file_path=None, extra_info={"competition_ids": [2]}),
]


@router.get("/", response_model=List[User])
@handle_exceptions
async def get_users(skip: int = 0, limit: int = 100):
    """
    获取用户列表，支持分页
    """
    return USERS[skip : skip + limit]


@router.get("/me", response_model=User)
@handle_exceptions
async def get_current_user():
    """
    获取当前登录用户信息
    """
    # 在实际应用中，这里会从认证中间件获取当前用户
    # 这里仅作示例
    return USERS[0]


@router.get("/{user_id}", response_model=User)
@handle_exceptions
async def get_user(user_id: int):
    """
    根据ID获取特定用户详情
    """
    for user in USERS:
        if user["id"] == user_id:
            return user
    raise NotFoundException(detail=f"用户ID {user_id} 不存在")


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_user(user: UserCreate):
    """
    创建新用户
    """
    # 检查邮箱是否已被使用
    for existing_user in USERS:
        if existing_user["email"] == user.email:
            raise BadRequestException(detail="该邮箱已被注册")
    
    # 检查用户名是否已被使用
    for existing_user in USERS:
        if existing_user["username"] == user.username:
            raise BadRequestException(detail="该用户名已被使用")
    
    # 模拟数据库操作
    new_id = max(u["id"] for u in USERS) + 1
    
    # 在实际应用中，这里会对密码进行哈希处理
    hashed_password = f"hashed_{user.password}"
    
    # 创建新用户
    new_user = {
        "id": new_id,
        **user.dict(exclude={"password"}),
        "is_active": True,
        "is_verified": False,
        "hashed_password": hashed_password
    }
    
    # 在实际应用中，这里会将数据保存到数据库
    # 这里仅作示例
    USERS.append(new_user)
    return new_user


@router.post("/login", response_model=Token)
@handle_exceptions
async def login_for_access_token(form_data: UserLogin):
    """
    用户登录以获取访问令牌 (支持用户名或邮箱)
    """
    # 1. 判断 login_identifier 是邮箱还是用户名
    is_email = "@" in form_data.login_identifier
    
    # 2. 根据类型查找用户
    user = None
    for u in USERS:
        if is_email and u["email"] == form_data.login_identifier:
            user = u
            break
        elif not is_email and u["username"] == form_data.login_identifier:
            user = u
            break
            
    # 3. 验证用户是否存在以及密码是否正确
    # 注意：这里的密码验证是极度简化的，实际应用必须使用安全的哈希比较
    if not user or f"hashed_{form_data.password}" != user["hashed_password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. 创建并返回JWT Token (这里用一个假token代替)
    # 在实际应用中，这里会使用 jose 或 pyjwt 库来创建真实的JWT
    access_token = f"fake-jwt-token-for-user-{user['id']}"
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/{user_id}", response_model=User)
@handle_exceptions
async def update_user(user_id: int, user: UserBase):
    """
    更新用户信息
    """
    for u in USERS:
        if u["id"] == user_id:
            # 在实际应用中，这里会更新数据库中的记录
            # 这里仅作示例
            updated_user = {
                **u,
                **user.dict(),
            }
            return updated_user
    
    raise NotFoundException(detail=f"用户ID {user_id} 不存在")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_user(user_id: int):
    """
    删除用户
    """
    for i, user in enumerate(USERS):
        if user["id"] == user_id:
            # 在实际应用中，这里会从数据库中删除记录
            # 这里仅作示例
            return
    
    raise NotFoundException(detail=f"用户ID {user_id} 不存在")


@router.get("/me/reports", response_model=Page[Report])
@handle_exceptions
def get_my_reports(
    params: Params = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取当前用户的所有报告(分页)
    """
    report_service_instance = report_service.ReportService(db)
    user_reports = report_service_instance.get_reports_by_user(user_id=current_user.id)
    return paginate(user_reports, params)


# 模拟的报告数据(这部分可以删除或保留用于其他测试)
mock_reports = [
    Report(id=1, title='关于"蓝桥杯"的初步分析报告', owner_id=1, status="已生成", file_path="/reports/report_1.pdf", extra_info={"competition_ids": [1]}),
    Report(id=2, title='数学建模竞赛回顾与分析', owner_id=1, status="生成中", file_path=None, extra_info={"competition_ids": [2]}),
] 