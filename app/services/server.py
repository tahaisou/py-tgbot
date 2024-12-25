from datetime import datetime, timedelta
from typing import Tuple
from ..models.server import ServerStatus, ServerInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

class ServerService:
    """服务器管理服务"""
    
    @staticmethod
    def calculate_expire_date(start_date: datetime) -> datetime:
        """计算到期时间（一个自然月）"""
        next_month = start_date.replace(day=1) + timedelta(days=32)
        return next_month.replace(day=start_date.day)
    
    @staticmethod
    def calculate_server_status(expire_date: datetime) -> ServerStatus:
        """计算服务器状态"""
        now = datetime.now()
        days_remaining = (expire_date - now).days
        
        if days_remaining <= 0:
            return ServerStatus.EXPIRED
        elif days_remaining <= 5:
            return ServerStatus.EXPIRING
        elif days_remaining <= 7:
            return ServerStatus.PENDING
        else:
            return ServerStatus.NORMAL
    
    @staticmethod
    async def update_server_status(server: ServerInfo, db: AsyncSession) -> None:
        """更新服务器状态"""
        new_status = ServerService.calculate_server_status(server.expire_date)
        if new_status != server.status:
            server.status = new_status
            await db.commit()
    
    @staticmethod
    async def renew_server(
        server: ServerInfo,
        admin_password: str,
        db: AsyncSession
    ) -> Tuple[datetime, datetime]:
        """
        续期服务器
        返回：(原到期时间, 新到期时间)
        """
        from ..models.admin import Admin
        
        # 验证管理员密码
        if not Admin.verify_password(admin_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="管理员密码错误"
            )
        
        # 记录原到期时间
        old_expire_date = server.expire_date
        
        # 计算新的到期时间
        now = datetime.now()
        if now > old_expire_date:
            # 如果已过期，从当前时间开始计算
            new_expire_date = ServerService.calculate_expire_date(now)
        else:
            # 如果未过期，从原到期时间开始计算
            new_expire_date = ServerService.calculate_expire_date(old_expire_date)
        
        # 更新服务器到期时间和状态
        server.expire_date = new_expire_date
        server.status = ServerService.calculate_server_status(new_expire_date)
        
        await db.commit()
        return old_expire_date, new_expire_date
    
    @staticmethod
    async def delete_server(server_id: int, admin_password: str, db: AsyncSession) -> None:
        """删除服务器信息"""
        from ..models.admin import Admin
        
        # 验证管理员密码
        if not Admin.verify_password(admin_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="管理员密码错误"
            )
        
        # 查询服务器
        query = select(ServerInfo).where(ServerInfo.id == server_id)
        result = await db.execute(query)
        server = result.scalar_one_or_none()
        
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务器不存在"
            )
        
        # 删除服务器信息
        await db.delete(server)
        await db.commit() 