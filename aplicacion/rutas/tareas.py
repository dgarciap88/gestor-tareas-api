from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from aplicacion.base_de_datos import get_db
from aplicacion.esquemas import TaskCreate, TaskResponse, TaskUpdate
from aplicacion.modelos import Task, TaskPriority, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_existing_task(
    task_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    return task


@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    status: Optional[TaskStatus] = Query(default=None),
    limit: int = Query(default=10, ge=1),
):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status != status)
    return query.all()


@router.get("/status/{task_status}", response_model=List[TaskResponse])
def list_tasks_by_status(task_status: TaskStatus, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.status == task_status).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task: Task = Depends(get_existing_task)):
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    if len(payload.title) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El titulo debe tener al menos 3 caracteres",
        )
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    payload: TaskUpdate, task: Task = Depends(get_existing_task),
    db: Session = Depends(get_db),
):
    if task.status == TaskStatus.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a task that is already done",
        )
    if payload.status == TaskStatus.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede establecer el estado a done directamente",
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task: Task = Depends(get_existing_task), db: Session = Depends(get_db)
):
    db.delete(task)
    db.commit()