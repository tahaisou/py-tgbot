from aiohttp import ClientSession
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.bot import BotConfig
from fastapi import HTTPException

class TelegramService:
    """Telegram 服务"""
    
    @staticmethod
    async def get_active_bot(db: AsyncSession) -> Optional[BotConfig]:
        """获取当前激活的机器人配置"""
        query = select(BotConfig).where(
            BotConfig.is_active == True,
            BotConfig.status == "active"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def test_bot(token: str) -> Dict[str, Any]:
        """测试机器人 token"""
        async with ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{token}/getMe"
            ) as response:
                return await response.json()
    
    @staticmethod
    async def send_message(
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """发送消息"""
        if not db:
            raise ValueError("数据库会话是必需的")
            
        bot = await TelegramService.get_active_bot(db)
        if not bot:
            raise ValueError("没有可用的机器人配置")
        
        try:
            async with ClientSession() as session:
                url = f"https://api.telegram.org/bot{bot.bot_token}/sendMessage"
                # 构建基本 payload
                payload = {
                    "chat_id": chat_id,
                    "text": text
                }
                
                # 只有当 parse_mode 不为 None 时才添加到 payload
                if parse_mode:
                    payload["parse_mode"] = parse_mode
                    
                print(f"Sending message to Telegram: URL={url}, Payload={payload}")  # 调试日志
                
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    print(f"Telegram API response: {result}")  # 调试日志
                    
                    if not result.get("ok"):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Telegram API error: {result.get('description')}"
                        )
                    return result
        except Exception as e:
            print(f"Error sending message: {str(e)}")  # 调试日志
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send message: {str(e)}"
            )
    
    @staticmethod
    async def send_photo(
        chat_id: int,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """发送图片"""
        if not db:
            raise ValueError("数据库会话是必需的")
            
        bot = await TelegramService.get_active_bot(db)
        if not bot:
            raise ValueError("没有可用的机器人配置")
        
        async with ClientSession() as session:
            async with session.post(
                f"https://api.telegram.org/bot{bot.bot_token}/sendPhoto",
                json={
                    "chat_id": chat_id,
                    "photo": photo_url,
                    "caption": caption,
                    "parse_mode": parse_mode
                }
            ) as response:
                return await response.json()
    
    @staticmethod
    async def get_updates(
        db: AsyncSession = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取更新"""
        if not db:
            raise ValueError("数据库会话是必需的")
            
        bot = await TelegramService.get_active_bot(db)
        if not bot:
            raise ValueError("没有可用的机器人配置")
        
        params = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        
        async with ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{bot.bot_token}/getUpdates",
                params=params
            ) as response:
                return await response.json()
    
    @staticmethod
    async def get_webhook_info(
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """获取 webhook 信息"""
        if not db:
            raise ValueError("数据库会话是必需的")
            
        bot = await TelegramService.get_active_bot(db)
        if not bot:
            raise ValueError("没有可用的机器人配置")
        
        async with ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{bot.bot_token}/getWebhookInfo"
            ) as response:
                return await response.json() 