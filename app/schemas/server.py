from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class ServerStatus(str, Enum):
    NORMAL = "normal"
    PENDING = "pending"
    EXPIRING = "expiring"
    EXPIRED = "expired"

class ServerInfoCreate(BaseModel):
    """创建服务器信息的请求模型"""
    # 基础信息
    product_type: str = "100M+10M"
    system: str = "centos7"
    configs: List[str] = []
    
    # 服务器访问信息
    server_ips: List[str]
    server_port: str
    server_username: str
    server_password: str
    
    # 时间管理（可选）
    start_date: Optional[datetime] = None  # 不提供则使用当前时间
    
    # 其他信息
    extra_info: Dict[str, str] = {}

class ServerRenewalCreate(BaseModel):
    """续期请求模型"""
    admin_password: str  # 管理员密码验证

class ServerInfoUpdate(BaseModel):
    """更新服务器信息的请求模型"""
    start_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None

class ServerRenewalRead(BaseModel):
    """续期记录响应模型"""
    id: int
    renew_date: datetime
    old_expire_date: datetime
    new_expire_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ServerInfoRead(BaseModel):
    """服务器信息响应模型"""
    id: int
    server_ips: List[str]
    server_port: str
    server_username: str
    server_password: str
    product_type: str
    system: str
    configs: List[str]
    start_date: datetime
    expire_date: datetime
    status: ServerStatus
    created_at: datetime
    updated_at: datetime
    renewals: List[ServerRenewalRead] = []

    class Config:
        from_attributes = True 