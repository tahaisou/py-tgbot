from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    """
    用户模型
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    nickname = Column(String(50))
    avatar_url = Column(String(255))
    platform = Column(String(20), default="telegram")
    platform_user_id = Column(String(50), nullable=False)
    status = Column(Boolean, default=True)
    
    # Telegram 特有字段
    tg_first_name = Column(String(64))
    tg_last_name = Column(String(64))
    tg_language_code = Column(String(10))
    tg_is_bot = Column(Boolean, default=False)
    last_interaction = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 添加备注字段
    note = Column(String(1000))
    
    # 添加标签关联
    tags = relationship("Tag", secondary="user_tags", back_populates="users")
    server_infos = relationship("ServerInfo", back_populates="user") 