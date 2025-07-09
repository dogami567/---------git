from typing import Generator, Dict, Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于FastAPI的Depends
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 在真实应用中，这里会解码JWT Token并验证用户
# 目前，我们使用一个模拟函数来返回一个固定的用户对象
def get_current_active_user() -> Dict[str, Any]:
    """
    获取当前活跃用户。
    
    这是一个模拟实现，总是返回ID为1的用户。
    """
    # 模拟从数据库或缓存中获取的用户模型
    # 实际应用中会是 User ORM Model
    class MockUser:
        def __init__(self, id, email, username):
            self.id = id
            self.email = email
            self.username = username
            
    return MockUser(id=1, email="student1@example.com", username="student1") 