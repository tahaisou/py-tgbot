from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum

class ServerStatus(str, Enum):
    """
    服务器状态枚举
    """
    NORMAL = "normal"      # 正常
    PENDING = "pending"    # 待续费（7天内到期）
    EXPIRING = "expiring"  # 即将到期（5天内到期）
    EXPIRED = "expired"    # 已过期

class ServerInfo(Base):
    """
    服务器信息模型
    """
    __tablename__ = "server_info"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    raw_content = Column(Text, nullable=False)
    
    # 四要素
    server_ips = Column(Text, nullable=False)  # JSON 格式存储 IP 列表
    server_port = Column(String(10), nullable=False)
    server_username = Column(String(50), nullable=False)
    server_password = Column(String(255), nullable=False)
    
    # 额外信息
    extra_info = Column(JSON)
    
    # 时间管理
    start_date = Column(DateTime, nullable=False, server_default=func.now())
    expire_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ServerStatus), nullable=False, default=ServerStatus.NORMAL)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="server_infos")
    renewals = relationship("ServerRenewal", back_populates="server", cascade="all, delete-orphan")

class ServerRenewal(Base):
    """
    服务器续期记录模型
    """
    __tablename__ = "server_renewals"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey('server_info.id', ondelete='CASCADE'))
    renew_date = Column(DateTime, nullable=False, server_default=func.now())
    old_expire_date = Column(DateTime, nullable=False)
    new_expire_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    server = relationship("ServerInfo", back_populates="renewals") 