from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from aplicacion.modelos import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    categoria: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    categoria: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    categoria: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime

    model_config = {"from_attributes": True}
