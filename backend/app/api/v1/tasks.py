from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.db import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, Task, TaskLabel
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.core.audit import log_audit

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.user_id == current_user.id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if due_date:
        query = query.filter(Task.due_date == due_date)
    return query.all()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    duplicate = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.title == task_in.title,
        Task.due_date == task_in.due_date
    ).first()
    
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A task with the same title and due date already exists."
        )

    db_task = Task(
        user_id=current_user.id,
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        status=task_in.status,
        due_date=task_in.due_date,
        due_time=task_in.due_time,
        estimated_time=task_in.estimated_time,
        repeat_rule=task_in.repeat_rule,
        reminder_rule=task_in.reminder_rule,
        notes=task_in.notes
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    if task_in.labels:
        for label_text in task_in.labels:
            label = TaskLabel(task_id=db_task.id, label=label_text)
            db.add(label)
        db.commit()
        db.refresh(db_task)

    log_audit(db, current_user.id, "CREATE_TASK", None, f"Task Title: {db_task.title}", request.client.host if request.client else None)
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_val = f"Status: {db_task.status}, Priority: {db_task.priority}"
    update_data = task_in.model_dump(exclude_unset=True)
    
    if "labels" in update_data:
        labels_list = update_data.pop("labels")
        if labels_list is not None:
            db.query(TaskLabel).filter(TaskLabel.task_id == task_id).delete()
            for label_text in labels_list:
                label = TaskLabel(task_id=task_id, label=label_text)
                db.add(label)

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    
    new_val = f"Status: {db_task.status}, Priority: {db_task.priority}"
    log_audit(db, current_user.id, "UPDATE_TASK", old_val, new_val, request.client.host if request.client else None)
    
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_title = db_task.title
    db.delete(db_task)
    db.commit()
    
    log_audit(db, current_user.id, "DELETE_TASK", f"Title: {task_title}", None, request.client.host if request.client else None)
    return None
