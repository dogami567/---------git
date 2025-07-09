import os
import sys
import unittest
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db.database import Base, engine, SessionLocal
from backend.app.models.user import User
from backend.app.models.competition import Competition
from backend.app.models.subscription import Subscription, CompetitionSubscription


class TestDatabase(unittest.TestCase):
    """
    数据库测试类
    """
    
    @classmethod
    def setUpClass(cls):
        """
        在所有测试前执行一次
        创建所有表
        """
        # 创建所有表
        Base.metadata.create_all(bind=engine)
    
    @classmethod
    def tearDownClass(cls):
        """
        在所有测试后执行一次
        删除所有表
        """
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
    
    def setUp(self):
        """
        每个测试前的设置
        """
        # 创建会话
        self.db = SessionLocal()
    
    def tearDown(self):
        """
        每个测试后的清理
        """
        # 关闭会话
        self.db.close()
    
    def test_connection(self):
        """
        测试数据库连接
        """
        # 执行简单查询
        result = self.db.execute(text("SELECT 1")).scalar()
        self.assertEqual(result, 1)
    
    def test_user_model(self):
        """
        测试用户模型
        """
        # 创建测试用户
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User",
            university="Test University",
            major="Computer Science",
            grade="大三"
        )
        
        # 添加到会话
        self.db.add(test_user)
        self.db.commit()
        self.db.refresh(test_user)
        
        # 验证用户ID
        self.assertIsNotNone(test_user.id)
        
        # 查询用户
        queried_user = self.db.query(User).filter(User.email == "test@example.com").first()
        self.assertEqual(queried_user.username, "testuser")
        
        # 清理
        self.db.delete(test_user)
        self.db.commit()
    
    def test_competition_model(self):
        """
        测试竞赛模型
        """
        # 创建测试竞赛
        test_competition = Competition(
            title="测试竞赛",
            description="这是一个测试竞赛",
            organizer="测试组织者",
            category="数学"
        )
        
        # 添加到会话
        self.db.add(test_competition)
        self.db.commit()
        self.db.refresh(test_competition)
        
        # 验证竞赛ID
        self.assertIsNotNone(test_competition.id)
        
        # 查询竞赛
        queried_competition = self.db.query(Competition).filter(Competition.title == "测试竞赛").first()
        self.assertEqual(queried_competition.organizer, "测试组织者")
        
        # 清理
        self.db.delete(test_competition)
        self.db.commit()


if __name__ == "__main__":
    unittest.main() 