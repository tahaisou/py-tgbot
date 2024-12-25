from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TagRead(BaseModel):
    """
    标签信息响应模型
    """
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserRead(BaseModel):
    """
    用户信息响应模型
    """
    id: int
    username: Optional[str] = None
    nickname: Optional[str] = None
    platform_user_id: str
    avatar_url: Optional[str] = None
    status: bool
    tg_first_name: Optional[str] = None
    tg_last_name: Optional[str] = None
    tg_language_code: Optional[str] = None
    tg_is_bot: bool = False
    last_interaction: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    note: Optional[str] = None
    tags: List[TagRead] = []  # 添加标签列表字段

    class Config:
        from_attributes = True 