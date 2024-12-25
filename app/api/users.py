from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..core.deps import get_current_admin
from ..core.database import get_db
from ..models.user import User
from ..schemas.user import UserRead
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from ..services.telegram import TelegramService
from sqlalchemy import or_
from ..models.tag import Tag, user_tags
from sqlalchemy import update
from sqlalchemy import and_
from sqlalchemy import Table
from ..schemas.tag import TagCreate
from ..schemas.message import MessageCreate, ParseMode
import json

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])

@router.get("/", response_model=List[UserRead], summary="获取用户列表")
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """获取所有用户的列表，支持分页"""
    query = (
        select(User)
        .options(selectinload(User.tags))
        .offset(skip)
        .limit(limit)
        .order_by(User.last_interaction.desc())
    )
    result = await db.execute(query)
    users = result.scalars().all()
    return users

@router.get("/sync", response_model=dict, summary="同步 Telegram 用户")
async def sync_users_from_telegram(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """从 Telegram 同步最新的用户数据"""
    # 获取 Telegram 更新
    updates = await TelegramService.get_updates(db=db)
    
    new_users = 0
    updated_users = 0
    
    for update in updates:
        if "message" in update and "from" in update["message"]:
            user_data = update["message"]["from"]
            
            # 检查用户是否存在
            query = select(User).where(
                User.platform == "telegram",
                User.platform_user_id == str(user_data["id"])
            )
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            
            if user is None:
                # 创建新用户
                user = User(
                    platform_user_id=str(user_data["id"]),
                    username=user_data.get("username"),
                    tg_first_name=user_data.get("first_name"),
                    tg_last_name=user_data.get("last_name"),
                    tg_language_code=user_data.get("language_code"),
                    tg_is_bot=user_data.get("is_bot", False),
                    last_interaction=datetime.utcnow()
                )
                db.add(user)
                new_users += 1
            else:
                # 更新现有用户
                user.username = user_data.get("username", user.username)
                user.tg_first_name = user_data.get("first_name", user.tg_first_name)
                user.tg_last_name = user_data.get("last_name", user.tg_last_name)
                user.tg_language_code = user_data.get("language_code", user.tg_language_code)
                user.last_interaction = datetime.utcnow()
                updated_users += 1
    
    await db.commit()
    
    return {
        "new_users": new_users,
        "updated_users": updated_users,
        "total_updates": len(updates)
    }

@router.get("/stats", response_model=dict, summary="获取用户统计")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """获取用户总数和活跃用户统计信息"""
    # 总用户数
    total_query = select(func.count(User.id))
    total_result = await db.execute(total_query)
    total_users = total_result.scalar()
    
    # 今日活跃用户
    today = datetime.now().date()
    active_query = select(func.count(User.id)).where(
        func.date(User.last_interaction) == today
    )
    active_result = await db.execute(active_query)
    active_users = active_result.scalar()
    
    return {
        "total_users": total_users,
        "active_users_today": active_users
    }

@router.get("/search", response_model=List[UserRead], summary="搜索用户")
async def search_users(
    keyword: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """根据关键词搜索用户"""
    query = select(User).where(
        or_(
            User.username.ilike(f"%{keyword}%"),
            User.tg_first_name.ilike(f"%{keyword}%"),
            User.tg_last_name.ilike(f"%{keyword}%")
        )
    )
    result = await db.execute(query)
    return result.scalars().all() 

@router.get("/stats/chart", response_model=dict, summary="获取用户增长图表")
async def get_user_chart_data(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """获取用户增长趋势图表数据"""
    today = datetime.now().date()
    data = []
    
    for i in range(days):
        date = today - timedelta(days=i)
        query = select(func.count(User.id)).where(
            func.date(User.created_at) == date
        )
        result = await db.execute(query)
        count = result.scalar()
        data.append({"date": date.isoformat(), "count": count})
    
    return {"data": data} 

@router.put("/{user_id}/note", response_model=UserRead, summary="更新用户备注")
async def update_user_note(
    user_id: int,
    note: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """更新指定用户的备注信息"""
    # 先查询用户是否存在
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新备注
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(note=note)
    )
    await db.execute(stmt)
    await db.commit()
    
    # 重新查询用户信息
    result = await db.execute(query)
    updated_user = result.scalar_one()
    return updated_user

@router.post("/{user_id}/tags", response_model=UserRead, summary="添加用户标签")
async def add_user_tags(
    user_id: int,
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """为指定用户添加标签"""
    # 获取用户
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 先删除用户的所有现有标签关联
    delete_stmt = user_tags.delete().where(user_tags.c.user_id == user_id)
    await db.execute(delete_stmt)
    
    # 获取或创建新标签
    for tag_name in tag_data.tags:
        # 先查询标签是否存在
        tag_query = select(Tag).where(Tag.name == tag_name)
        result = await db.execute(tag_query)
        tag = result.scalar_one_or_none()
        
        if not tag:
            # 创建新标签
            tag = Tag(name=tag_name)
            db.add(tag)
            await db.flush()  # 立即创建标签获取ID
        
        # 添加新的关联
        await db.execute(
            user_tags.insert().values(
                user_id=user_id,
                tag_id=tag.id
            )
        )
    
    await db.commit()
    
    # 重新查询用户（包含标签）
    query = select(User).options(selectinload(User.tags)).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one()

@router.post("/{user_id}/message", summary="发送消息给用户")
async def send_message_to_user(
    user_id: int,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """向指定用户发送 Telegram 消息"""
    # 获取用户
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not user.platform_user_id:
        raise HTTPException(status_code=400, detail="用户没有关联的 Telegram ID")
    
    # 检查机器人配置
    bot = await TelegramService.get_active_bot(db)
    if not bot:
        raise HTTPException(status_code=400, detail="没有可用的机器人配置")
    
    parse_mode = None if message.parse_mode == ParseMode.TEXT else message.parse_mode.value
    
    try:
        # 发送文本消息
        if message.text:
            response = await TelegramService.send_message(
                int(user.platform_user_id),
                message.text,
                parse_mode=parse_mode,
                db=db
            )
            if not response.get("ok"):
                raise HTTPException(
                    status_code=400,
                    detail=f"消息发送失败: {response.get('description')}"
                )
        
        # 发送图片
        if message.photo_url:
            response = await TelegramService.send_photo(
                int(user.platform_user_id),
                str(message.photo_url),
                caption=message.caption,
                parse_mode=parse_mode,
                db=db
            )
            if not response.get("ok"):
                raise HTTPException(
                    status_code=400,
                    detail=f"图片发送失败: {response.get('description')}"
                )
        
        return {"status": "success", "message": "消息已发送"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"消息发送失败: {str(e)}"
        ) 