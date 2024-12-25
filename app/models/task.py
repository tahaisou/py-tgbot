from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class TaskConfig(Base):
    """定时任务配置模型"""
    __tablename__ = "task_config"
    
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    task_type = Column(String(50), nullable=False)
    cron_expression = Column(String(100))
    interval_seconds = Column(Integer)
    is_active = Column(Boolean, default=True)
    last_run_time = Column(DateTime)
    next_run_time = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 