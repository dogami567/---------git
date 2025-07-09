from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel

from backend.app.core.exceptions import handle_exceptions, NotFoundException, ConflictException
# 假设我们有一个可以从Token获取当前用户的依赖项
# from backend.app.api.deps import get_current_user_from_token
# from backend.app.models.user import User

# --- 模型定义 ---

class SubscriptionBase(BaseModel):
    """订阅基础模型"""
    competition_id: int


class SubscriptionCreate(SubscriptionBase):
    """创建订阅请求模型"""
    pass # user_id 将从token中获取


class Subscription(SubscriptionBase):
    """订阅响应模型"""
    id: int
    user_id: int

    class Config:
        from_attributes = True


class SubscriptionStatus(BaseModel):
    """订阅状态响应模型"""
    is_subscribed: bool
    subscription_id: Optional[int] = None


# --- 路由器设置 ---
router = APIRouter()

# --- 模拟数据库 ---
# 使用一个列表来模拟订阅表
SUBSCRIPTIONS: List[Dict[str, Any]] = []
next_subscription_id = 1

# --- 模拟依赖项 ---
# 在实际应用中，这将是一个复杂的函数，用于解码JWT并从数据库获取用户
def get_current_user_from_token_mock() -> Dict[str, Any]:
    # 为测试目的，我们硬编码返回一个用户
    # 假设这是从登录后返回的token中解码出来的用户信息
    return {"id": 1, "email": "student1@example.com", "username": "student1"}

# --- API 端点 ---

@router.get("/", response_model=List[Subscription])
@handle_exceptions
async def get_user_subscriptions(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_mock)
):
    """
    获取当前登录用户的所有订阅。
    """
    current_user_id = current_user["id"]
    user_subs = [sub for sub in SUBSCRIPTIONS if sub["user_id"] == current_user_id]
    return user_subs


@router.post("/", response_model=Subscription, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_mock)
):
    """
    为当前登录用户创建一个新的竞赛订阅。
    """
    global next_subscription_id
    current_user_id = current_user["id"]

    # 检查是否已经订阅
    for sub in SUBSCRIPTIONS:
        if sub["user_id"] == current_user_id and sub["competition_id"] == subscription.competition_id:
            raise ConflictException(detail="您已经订阅了此竞赛")
            
    # 创建新的订阅记录
    new_subscription = {
        "id": next_subscription_id,
        "user_id": current_user_id,
        "competition_id": subscription.competition_id,
    }
    SUBSCRIPTIONS.append(new_subscription)
    next_subscription_id += 1
    
    return new_subscription


@router.get("/check/{competition_id}", response_model=SubscriptionStatus)
@handle_exceptions
async def check_subscription_status(
    competition_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_mock)
):
    """
    检查当前用户是否订阅了特定的竞赛。
    """
    current_user_id = current_user["id"]

    for sub in SUBSCRIPTIONS:
        if sub["user_id"] == current_user_id and sub["competition_id"] == competition_id:
            return {"is_subscribed": True, "subscription_id": sub["id"]}
            
    return {"is_subscribed": False}


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_subscription(
    subscription_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_mock)
):
    """
    删除一个订阅。
    """
    current_user_id = current_user["id"]
    
    global SUBSCRIPTIONS
    
    sub_to_delete = None
    for sub in SUBSCRIPTIONS:
        if sub["id"] == subscription_id:
            sub_to_delete = sub
            break
            
    if not sub_to_delete:
        raise NotFoundException(detail="订阅记录未找到")
        
    # 验证该订阅是否属于当前用户
    if sub_to_delete["user_id"] != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限删除此订阅"
        )
        
    SUBSCRIPTIONS = [s for s in SUBSCRIPTIONS if s["id"] != subscription_id]
    return 