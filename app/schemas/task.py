from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskConfigBase(BaseModel):
    task_name: str
    task_type: str
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True

class TaskConfigCreate(TaskConfigBase):
    pass

class TaskConfigUpdate(TaskConfigBase):
    task_name: Optional[str] = None
    task_type: Optional[str] = None
    is_active: Optional[bool] = None

class TaskConfigRead(TaskConfigBase):
    id: int
    last_run_time: Optional[datetime]
    next_run_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 