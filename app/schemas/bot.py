from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class BotConfigCreate(BaseModel):
    """创建机器人配置"""
    bot_name: str
    bot_token: str
    webhook_url: Optional[HttpUrl] = None

class BotConfigUpdate(BaseModel):
    """更新机器人配置"""
    bot_name: Optional[str] = None
    bot_token: Optional[str] = None
    webhook_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None

class BotConfigRead(BaseModel):
    """机器人配置响应"""
    id: int
    bot_name: str
    bot_username: Optional[str]
    webhook_url: Optional[str]
    is_active: bool
    status: str
    last_check_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 