from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..core.deps import get_current_admin
from ..core.database import get_db
from ..models.server import ServerInfo, ServerRenewal
from ..models.user import User
from ..schemas.server import ServerInfoCreate, ServerInfoRead, ServerRenewalCreate
from ..services.server import ServerService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json
from datetime import datetime

router = APIRouter(prefix="/api/v1/servers", tags=["服务器管理"])

@router.post("/{user_id}", response_model=ServerInfoRead, summary="添加服务器信息")
async def add_server_info(
    user_id: int,
    server_info: ServerInfoCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """为用户添加服务器信息，包含到期时间管理"""
    # 检查用户是否存在
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 计算起始时间和到期时间
    start_date = server_info.start_date or datetime.now()
    expire_date = ServerService.calculate_expire_date(start_date)
    status = ServerService.calculate_server_status(expire_date)
    
    # 构建原始内容
    raw_content = (
        f"产品类型:{server_info.product_type}\n"
        f"系统:{server_info.system}\n"
    )
    
    for config in server_info.configs:
        raw_content += f"{config}\n"
    
    raw_content += "机器信息:\n"
    for ip in server_info.server_ips:
        raw_content += f"{ip}\n"
    
    raw_content += f"远程账号:{server_info.server_username}\n"
    raw_content += f"密码:{server_info.server_password}\n"
    raw_content += f"远程端口:{server_info.server_port}"
    
    # 创建服务器信息记录
    server = ServerInfo(
        user_id=user_id,
        raw_content=raw_content,
        server_ips=json.dumps(server_info.server_ips),
        server_port=server_info.server_port,
        server_username=server_info.server_username,
        server_password=server_info.server_password,
        start_date=start_date,
        expire_date=expire_date,
        status=status,
        extra_info={
            "product_type": server_info.product_type,
            "system": server_info.system,
            "configs": server_info.configs,
            **server_info.extra_info
        }
    )
    
    db.add(server)
    await db.commit()
    await db.refresh(server)
    
    return server

@router.post("/{user_id}/{server_id}/renew", response_model=dict, summary="续期服务器")
async def renew_server(
    user_id: int,
    server_id: int,
    renewal: ServerRenewalCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """续期服务器一个月，需要管理员密码验证"""
    # 检查服务器是否存在
    query = select(ServerInfo).where(
        ServerInfo.id == server_id,
        ServerInfo.user_id == user_id
    )
    result = await db.execute(query)
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(status_code=404, detail="服务器不存在")
    
    # 执行续期
    old_expire_date, new_expire_date = await ServerService.renew_server(
        server,
        renewal.admin_password,
        db
    )
    
    # 创建续期记录
    renewal_record = ServerRenewal(
        server_id=server_id,
        old_expire_date=old_expire_date,
        new_expire_date=new_expire_date
    )
    
    db.add(renewal_record)
    await db.commit()
    
    return {
        "status": "success",
        "message": "续期成功",
        "old_expire_date": old_expire_date,
        "new_expire_date": new_expire_date
    }

@router.delete("/{user_id}/{server_id}", response_model=dict, summary="删除服务器")
async def delete_server(
    user_id: int,
    server_id: int,
    admin_password: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """删除服务器信息，需要管理员密码验证"""
    # 检查服务器是否属于该用户
    query = select(ServerInfo).where(
        ServerInfo.id == server_id,
        ServerInfo.user_id == user_id
    )
    result = await db.execute(query)
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(status_code=404, detail="服务器不存在")
    
    # 执行删除
    await ServerService.delete_server(server_id, admin_password, db)
    
    return {
        "status": "success",
        "message": "服务器已删除"
    }

@router.get("/summary", response_model=dict, summary="获取服务器信息汇总")
async def get_servers_summary(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """获取所有服务器信息的汇总"""
    # 查询所有服务器信息，包含用户信息
    query = (
        select(ServerInfo, User)
        .join(User, ServerInfo.user_id == User.id)
        .options(selectinload(ServerInfo.user))
    )
    result = await db.execute(query)
    servers = result.all()
    
    # 初始化统计数据
    summary = {
        "total_servers": len(servers),
        "users": {},
        "systems": {},
        "configs": {}
    }
    
    # 处理每个服务器信息
    for server, user in servers:
        user_id = str(user.id)
        
        # 用户维度统计
        if user_id not in summary["users"]:
            summary["users"][user_id] = {
                "user_id": user.id,
                "username": user.username,
                "server_count": 0,
                "servers": []
            }
        
        # 添加服务器信息
        server_info = {
            "id": server.id,
            "ips": json.loads(server.server_ips),
            "port": server.server_port,
            "username": server.server_username,
            "product_type": server.extra_info.get("product_type", "未知"),
            "system": server.extra_info.get("system", "未知"),
            "configs": server.extra_info.get("configs", []),
            "created_at": server.created_at.isoformat()
        }
        summary["users"][user_id]["servers"].append(server_info)
        summary["users"][user_id]["server_count"] += 1
        
        # 系统维度统计
        system = server.extra_info.get("system", "未知")
        summary["systems"][system] = summary["systems"].get(system, 0) + 1
        
        # 配置维度统计
        for config in server.extra_info.get("configs", []):
            summary["configs"][config] = summary["configs"].get(config, 0) + 1
    
    # 转换用户数据为列表
    summary["users"] = list(summary["users"].values())
    
    return summary 