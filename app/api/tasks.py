from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..core.deps import get_current_admin
from ..core.database import get_db
from ..models.task import TaskConfig
from ..schemas.task import TaskConfigCreate, TaskConfigUpdate, TaskConfigRead
from ..services.scheduler import SchedulerService
from sqlalchemy import select
from datetime import datetime

router = APIRouter(prefix="/api/v1/tasks", tags=["定时任务"])

@router.get("/", response_model=List[TaskConfigRead], summary="获取任务配置列表")
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """获取所有定时任务配置"""
    query = select(TaskConfig)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=TaskConfigRead, summary="添加任务配置")
async def create_task(
    task: TaskConfigCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """添加新的定时任务配置"""
    db_task = TaskConfig(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.post("/{task_id}/run", response_model=dict, summary="手动执行任务")
async def run_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_admin)
):
    """手动执行指定的定时任务"""
    query = select(TaskConfig).where(TaskConfig.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    scheduler = SchedulerService(None)
    
    if task.task_name == "update_server_status":
        await scheduler.update_server_status()
    elif task.task_name == "send_expiration_notices":
        await scheduler.send_expiration_notices()
    else:
        raise HTTPException(status_code=400, detail="不支持的任务类型")
    
    # 更新执行时间
    task.last_run_time = datetime.now()
    await db.commit()
    
    return {"status": "success", "message": f"任务 {task.task_name} 执行完成"} 