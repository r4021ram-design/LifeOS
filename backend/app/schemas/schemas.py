from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import date, time, datetime

# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# --- Tasks ---
class TaskLabelBase(BaseModel):
    label: str

class TaskLabelResponse(TaskLabelBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    priority: Optional[str] = "Medium"
    status: Optional[str] = "Pending"
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_time: Optional[int] = None
    repeat_rule: Optional[str] = None
    reminder_rule: Optional[str] = None
    notes: Optional[str] = None
    labels: Optional[List[str]] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_time: Optional[int] = None
    repeat_rule: Optional[str] = None
    reminder_rule: Optional[str] = None
    notes: Optional[str] = None
    labels: Optional[List[str]] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    due_date: Optional[date]
    due_time: Optional[time]
    estimated_time: Optional[int]
    repeat_rule: Optional[str]
    reminder_rule: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    labels: List[TaskLabelResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Habits ---
class HabitLogCreate(BaseModel):
    date: date
    status: str = "Completed"

class HabitLogResponse(BaseModel):
    id: int
    date: date
    status: str

    model_config = ConfigDict(from_attributes=True)

class HabitCreate(BaseModel):
    name: str
    category: Optional[str] = None
    frequency: Optional[str] = "Daily"
    goal: Optional[str] = None

class HabitResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    frequency: str
    goal: Optional[str]
    created_at: datetime
    logs: List[HabitLogResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Goals ---
class GoalMilestoneCreate(BaseModel):
    title: str
    progress: Optional[float] = 0.0
    is_completed: Optional[bool] = False

class GoalMilestoneResponse(GoalMilestoneCreate):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class GoalCreate(BaseModel):
    title: str
    category: Optional[str] = None
    target_value: Optional[float] = None
    deadline: Optional[date] = None

class GoalResponse(BaseModel):
    id: int
    title: str
    category: Optional[str]
    target_value: Optional[float]
    current_value: float
    deadline: Optional[date]
    status: str
    milestones: List[GoalMilestoneResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Notes ---
class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    tags: Optional[str] = None
    parent_note_id: Optional[int] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    tags: Optional[str]
    parent_note_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Trading Journal ---
class TradingJournalCreate(BaseModel):
    ticker: str
    type: str = "Long"
    quantity: int
    entry_price: float
    strategy: Optional[str] = None
    psychology_notes: Optional[str] = None

class TradingJournalUpdate(BaseModel):
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    psychology_notes: Optional[str] = None

class TradingJournalResponse(BaseModel):
    id: int
    entry_time: datetime
    exit_time: Optional[datetime]
    ticker: str
    type: str
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    strategy: Optional[str]
    psychology_notes: Optional[str]
    pnl: float

    model_config = ConfigDict(from_attributes=True)

# --- Panchang ---
class PanchangResponse(BaseModel):
    date: str
    tithi: str
    nakshatra: str
    yoga: str
    karana: str
    sunrise: str
    sunset: str
    muhurats: List[str]

# --- Events ---
class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    calendar_id: str

    model_config = ConfigDict(from_attributes=True)

# --- Search ---
class SearchResponse(BaseModel):
    tasks: List[TaskResponse]
    notes: List[NoteResponse]
    goals: List[GoalResponse]
    habits: List[HabitResponse]
    events: List[EventResponse]
    trading_journal: List[TradingJournalResponse]

# --- Device Tokens ---
class DeviceTokenCreate(BaseModel):
    token: str
    platform: str
    device_name: Optional[str] = None

class DeviceTokenResponse(BaseModel):
    id: int
    user_id: int
    token: str
    platform: str
    device_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
