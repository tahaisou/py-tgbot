from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from datetime import datetime, timedelta
from ..models.server import ServerInfo, ServerStatus
from ..core.database import async_session_maker
from ..services.server import ServerService
from ..services.telegram import TelegramService

class SchedulerService:
    def __init__(self, app: FastAPI):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        
    async def update_server_status(self):
        """更新所有服务器状态"""
        async with async_session_maker() as db:
            # 查询所有服务器
            query = select(ServerInfo)
            result = await db.execute(query)
            servers = result.scalars().all()
            
            for server in servers:
                await ServerService.update_server_status(server, db)
    
    async def send_expiration_notices(self):
        """发送到期提醒"""
        async with async_session_maker() as db:
            # 查询所有服务器及其用户信息
            query = (
                select(ServerInfo)
                .join(ServerInfo.user)
                .where(ServerInfo.status.in_([
                    ServerStatus.PENDING,
                    ServerStatus.EXPIRING,
                    ServerStatus.EXPIRED
                ]))
            )
            result = await db.execute(query)
            servers = result.scalars().all()
            
            for server in servers:
                days_remaining = (server.expire_date - datetime.now()).days
                
                if server.status == ServerStatus.EXPIRED:
                    message = (
                        f"⚠️ 服务器已过期\n\n"
                        f"IP: {', '.join(json.loads(server.server_ips))}\n"
                        f"过期时间: {server.expire_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"请尽快续期！"
                    )
                elif server.status == ServerStatus.EXPIRING:
                    message = (
                        f"⚠️ 服务器即将到期\n\n"
                        f"IP: {', '.join(json.loads(server.server_ips))}\n"
                        f"剩余天数: {days_remaining}天\n"
                        f"到期时间: {server.expire_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"请及时续期！"
                    )
                else:  # PENDING
                    message = (
                        f"📅 服务器到期提醒\n\n"
                        f"IP: {', '.join(json.loads(server.server_ips))}\n"
                        f"剩余天数: {days_remaining}天\n"
                        f"到期时间: {server.expire_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"请注意续期时间。"
                    )
                
                # 发送消息给用户
                await TelegramService.send_message(
                    int(server.user.platform_user_id),
                    message,
                    parse_mode="HTML",
                    db=db
                )
    
    def start(self):
        """启动定时任务"""
        # 每小时更新一次服务器状态
        self.scheduler.add_job(
            self.update_server_status,
            CronTrigger(hour="*")
        )
        
        # 每天早上9点发送到期提醒
        self.scheduler.add_job(
            self.send_expiration_notices,
            CronTrigger(hour=9, minute=0)
        )
        
        self.scheduler.start() 