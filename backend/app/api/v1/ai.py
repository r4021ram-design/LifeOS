from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.api.v1.auth import get_current_user
from app.models.models import User
from app.services.ai_assistant import generate_daily_schedule, breakdown_large_task

router = APIRouter(prefix="/ai", tags=["ai"])

class TaskSummaryIn(BaseModel):
    title: str
    priority: str
    due_date: Optional[str] = None
    estimated_time: Optional[int] = None

class AIScheduleRequest(BaseModel):
    tasks: List[TaskSummaryIn]

class AIBreakdownRequest(BaseModel):
    title: str
    description: Optional[str] = None

@router.post("/schedule")
async def optimize_schedule(req: AIScheduleRequest, current_user: User = Depends(get_current_user)):
    tasks_dicts = [task.model_dump() for task in req.tasks]
    schedule_data = await generate_daily_schedule(tasks_dicts)
    return schedule_data

@router.post("/breakdown")
async def breakdown_task(req: AIBreakdownRequest, current_user: User = Depends(get_current_user)):
    breakdown_data = await breakdown_large_task(req.title, req.description)
    return breakdown_data
