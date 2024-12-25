from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..core.deps import get_current_admin
from ..core.database import get_db
from ..models.bot import BotConfig
from ..schemas.bot import BotConfigCreate, BotConfigUpdate, BotConfigRead
from ..services.telegram import TelegramService
from sqlalchemy import select, update
from datetime import datetime

router = APIRouter(prefix="/api/v1/bot", tags=["机器人配置"])

@router.get("/config", response_model=List[BotConfigRead], summary="获取机器人配置列表")
async def list_bot_configs(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """获取所有机器人配置"""
    query = select(BotConfig)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/config", response_model=BotConfigRead, summary="添加机器人配置")
async def create_bot_config(
    config: BotConfigCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """添加新的机器人配置"""
    # 测试机器人 token
    test_result = await TelegramService.test_bot(config.bot_token)
    if not test_result["ok"]:
        raise HTTPException(
            status_code=400,
            detail=f"机器人 token 验证失败: {test_result.get('description', '未知错误')}"
        )
    
    # 创建配置
    bot_config = BotConfig(
        bot_name=config.bot_name,
        bot_token=config.bot_token,
        bot_username=test_result["result"]["username"],
        webhook_url=str(config.webhook_url) if config.webhook_url else None,
        status="active",
        last_check_time=datetime.now()
    )
    
    db.add(bot_config)
    await db.commit()
    await db.refresh(bot_config)
    
    return bot_config

@router.post("/config/{config_id}/test", response_model=dict, summary="测试机器人配置")
async def test_bot_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """测试指定的机器人配置"""
    # 获取配置
    query = select(BotConfig).where(BotConfig.id == config_id)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 测试机器人
    test_result = await TelegramService.test_bot(config.bot_token)
    
    # 更新状态
    config.last_check_time = datetime.now()
    if test_result["ok"]:
        config.status = "active"
        config.error_message = None
    else:
        config.status = "error"
        config.error_message = test_result.get("description", "未知错误")
    
    await db.commit()
    
    return test_result 