from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class BotConfig(Base):
    """机器人配置模型"""
    __tablename__ = "bot_config"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String(100), nullable=False)
    bot_token = Column(String(255), nullable=False)
    bot_username = Column(String(100))
    webhook_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_check_time = Column(DateTime)
    status = Column(String(50), default="pending")
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 