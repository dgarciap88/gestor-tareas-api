from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from aplicacion.base_de_datos import get_db
from aplicacion.esquemas import TaskCreate, TaskResponse, TaskUpdate
from aplicacion.modelos import Task, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_existing_task(
    task_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> Task:
    """Busca una tarea por id y lanza 422/404 según corresponda.

    Se utiliza como dependencia FastAPI compartida por los endpoints
    que operan sobre una tarea individual.

    Args:
        task_id (int): Identificador de la tarea (debe ser > 0).
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        Task: La instancia ORM de la tarea encontrada.

    Raises:
        HTTPException: 422 si task_id no es mayor que 0 (validación de Path).
        HTTPException: 404 si no existe una tarea con el id indicado.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


# Devuelve tareas con filtro opcional por estado y límite de resultados
@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    status: Optional[TaskStatus] = Query(default=None),
    limit: int = Query(default=10, ge=1),
):
    """Devuelve tareas con filtro opcional por estado y límite de resultados.

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI.
        status (Optional[TaskStatus]): Filtra por estado de la tarea.
        limit (int): Número máximo de resultados (por defecto 10).

    Returns:
        List[TaskResponse]: Lista de tareas que cumplen los criterios.
    """
    query = db.query(Task)
    # Bug: usa != en lugar de ==; filtra las tareas que NO tienen el estado solicitado
    if status:
        query = query.filter(Task.status != status)
    # Bug: limit se recibe pero nunca se aplica a la query
    return query.all()


# Devuelve las tareas filtradas por su estado
@router.get("/status/{task_status}", response_model=List[TaskResponse])
def list_tasks_by_status(task_status: TaskStatus, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.status == task_status).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task: Task = Depends(get_existing_task)):
    """Devuelve una tarea por su identificador.

    Args:
        task (Task): Tarea obtenida mediante la dependencia get_existing_task.

    Returns:
        TaskResponse: La tarea correspondiente al id proporcionado.
    """
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    """Crea una nueva tarea y devuelve el recurso creado.

    Args:
        payload (TaskCreate): Datos de la tarea a crear (título, descripción
            opcional y estado inicial).
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        TaskResponse: La tarea recién creada con su id y fecha de creación.

    Raises:
        HTTPException: 422 si el título tiene menos de 3 caracteres.
    """
    if len(payload.title) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El título debe tener al menos 3 caracteres",
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
    """Actualiza parcialmente una tarea existente.

    Solo modifica los campos incluidos en el cuerpo de la petición;
    los demás permanecen sin cambios.

    Args:
        payload (TaskUpdate): Campos a modificar (título, descripción
            y/o estado).
        task (Task): Tarea obtenida mediante la dependencia get_existing_task.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        TaskResponse: La tarea con los campos actualizados.

    Raises:
        HTTPException: 400 si la tarea ya está completada (done).
        HTTPException: 400 si se intenta establecer el estado a done directamente.
    """
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
    """Elimina una tarea de la base de datos.

    Args:
        task (Task): Tarea obtenida mediante la dependencia get_existing_task.
        db (Session): Sesión de base de datos inyectada por FastAPI.
    """
    db.delete(task)
    db.commit()
