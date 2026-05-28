from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from aplicacion.base_de_datos import get_db
from aplicacion.esquemas import TaskCreate, TaskResponse, TaskUpdate
from aplicacion.modelos import Task, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_existing_task(
    task_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.get("/", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task: Task = Depends(get_existing_task)):
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
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
    # Bug: comprueba el estado del payload en lugar del estado actual de la tarea;
    # una tarea ya completada puede modificarse sin ningún error
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
