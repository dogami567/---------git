from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from backend.app.db.database import Base


# 订阅与竞赛的多对多关系表
class CompetitionSubscription(Base):
    """
    竞赛订阅关联表
    """
    __tablename__ = "competition_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    subscription = relationship("Subscription", back_populates="competitions")
    competition = relationship("Competition", back_populates="subscriptions")


class Subscription(Base):
    """
    订阅模型
    存储用户订阅信息
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=True)
    keywords = Column(Text, nullable=True)  # 存储为JSON字符串
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="subscriptions")
    competitions = relationship("CompetitionSubscription", back_populates="subscription", cascade="all, delete-orphan") 