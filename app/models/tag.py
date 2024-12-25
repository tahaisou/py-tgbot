from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

# 用户-标签关联表
user_tags = Table(
    'user_tags',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE')),
    Column('created_at', DateTime, server_default=func.now())
)

class Tag(Base):
    """
    标签模型
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    users = relationship("User", secondary=user_tags, back_populates="tags") 