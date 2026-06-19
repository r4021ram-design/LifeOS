from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, Habit, HabitLog
from app.schemas.schemas import HabitCreate, HabitResponse, HabitLogCreate, HabitLogResponse

router = APIRouter(prefix="/habits", tags=["habits"])

@router.get("/", response_model=List[HabitResponse])
def list_habits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Habit).filter(Habit.user_id == current_user.id).all()

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(habit_in: HabitCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_habit = Habit(
        user_id=current_user.id,
        name=habit_in.name,
        category=habit_in.category,
        frequency=habit_in.frequency,
        goal=habit_in.goal
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@router.post("/{habit_id}/logs", response_model=HabitLogResponse)
def log_habit(
    habit_id: int,
    log_in: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    existing_log = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date == log_in.date
    ).first()
    
    if existing_log:
        existing_log.status = log_in.status
        db.commit()
        db.refresh(existing_log)
        return existing_log

    db_log = HabitLog(
        habit_id=habit_id,
        date=log_in.date,
        status=log_in.status
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
