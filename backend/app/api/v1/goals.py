from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, Goal, GoalMilestone
from app.schemas.schemas import GoalCreate, GoalResponse, GoalMilestoneCreate, GoalMilestoneResponse

router = APIRouter(prefix="/goals", tags=["goals"])

@router.get("/", response_model=List[GoalResponse])
def list_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Goal).filter(Goal.user_id == current_user.id).all()

@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(goal_in: GoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_goal = Goal(
        user_id=current_user.id,
        title=goal_in.title,
        category=goal_in.category,
        target_value=goal_in.target_value,
        deadline=goal_in.deadline,
        status="Pending"
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.post("/{goal_id}/milestones", response_model=GoalMilestoneResponse)
def add_milestone(
    goal_id: int,
    milestone_in: GoalMilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db_milestone = GoalMilestone(
        goal_id=goal_id,
        title=milestone_in.title,
        progress=milestone_in.progress,
        is_completed=milestone_in.is_completed
    )
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    
    all_milestones = db.query(GoalMilestone).filter(GoalMilestone.goal_id == goal_id).all()
    completed = [m for m in all_milestones if m.is_completed]
    goal.current_value = (len(completed) / len(all_milestones)) * 100 if all_milestones else 0.0
    if goal.current_value >= 100.0:
        goal.status = "Completed"
    else:
        goal.status = "In Progress"
    db.commit()
    
    return db_milestone
