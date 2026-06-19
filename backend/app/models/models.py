import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Float, ForeignKey, Text, Index, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="USER")  # ADMIN, USER, PREMIUM, TEAM_OWNER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), onupdate=lambda: datetime.datetime.now(datetime.UTC))

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    trading_journal = relationship("TradingJournal", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    ai_usage_logs = relationship("AIUsageLog", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, default="#000000")
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, default="Medium")  # Critical, High, Medium, Low
    status = Column(String, default="Pending")    # Pending, In Progress, Waiting, Completed, Cancelled
    due_date = Column(Date, nullable=True)
    due_time = Column(Time, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # in minutes
    repeat_rule = Column(String, nullable=True)
    reminder_rule = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), onupdate=lambda: datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    labels = relationship("TaskLabel", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")

    # Composite Index for Tasks query optimization
    __table_args__ = (
        Index("idx_tasks_user_due", "user_id", "due_date"),
    )

class TaskLabel(Base):
    __tablename__ = "task_labels"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    label = Column(String, nullable=False)

    task = relationship("Task", back_populates="labels")

class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    task = relationship("Task", back_populates="comments")

class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    task = relationship("Task", back_populates="attachments")

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    type = Column(String, default="One Time")  # One Time, Daily, Weekly, Monthly, Yearly
    time = Column(DateTime, nullable=False)
    status = Column(String, default="Pending")  # Pending, Sent, Failed
    timing_offset_minutes = Column(Integer, default=0)

    task = relationship("Task", back_populates="reminders")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel = Column(String, nullable=False)  # Push, Email, SMS, WhatsApp
    content = Column(Text, nullable=False)
    status = Column(String, default="Pending", index=True)  # Pending, Sent, Failed
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    attempts = relationship("NotificationAttempt", back_populates="notification", cascade="all, delete-orphan")

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    frequency = Column(String, default="Daily")
    goal = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, default="Completed")  # Completed, Skipped, Failed

    habit = relationship("Habit", back_populates="logs")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=True)  # Personal, Business, Trading, Fitness, Learning
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, default=0.0)
    deadline = Column(Date, nullable=True)
    status = Column(String, default="Pending")

    user = relationship("User", back_populates="goals")
    milestones = relationship("GoalMilestone", back_populates="goal", cascade="all, delete-orphan")

class GoalMilestone(Base):
    __tablename__ = "goal_milestones"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    progress = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)

    goal = relationship("Goal", back_populates="milestones")

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # Comma separated
    parent_note_id = Column(Integer, ForeignKey("notes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="notes")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    calendar_id = Column(String, default="Primary")

    user = relationship("User", back_populates="events")

    # Composite Index for Event searches
    __table_args__ = (
        Index("idx_events_user_start", "user_id", "start_time"),
    )

class TradingJournal(Base):
    __tablename__ = "trading_journal"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entry_time = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    exit_time = Column(DateTime, nullable=True)
    ticker = Column(String, nullable=False)
    type = Column(String, default="Long")  # Long, Short
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    strategy = Column(String, nullable=True)
    psychology_notes = Column(Text, nullable=True)
    pnl = Column(Float, default=0.0)

    user = relationship("User", back_populates="trading_journal")


# --- SaaS Billing / Subscription Architecture (Future-Proofing) ---

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Free, Premium, Enterprise
    price = Column(Float, nullable=False)
    interval = Column(String, default="monthly")  # monthly, yearly
    features = Column(JSON, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String, default="active")  # active, trialing, past_due, canceled
    current_period_start = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    current_period_end = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="succeeded")  # succeeded, failed, pending
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))


# --- Enterprise Audit Trail Logging ---

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)  # e.g., UPDATE_TASK, DELETE_NOTE, LOGIN
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="audit_logs")


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="ai_usage_logs")


class NotificationAttempt(Base):
    __tablename__ = "notification_attempts"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    status = Column(String, nullable=False)  # Sent, Failed
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    notification = relationship("Notification", back_populates="attempts")


# --- PostgreSQL GIN full-text index creation using SQLAlchemy Event Listeners ---
from sqlalchemy import event, DDL

event.listen(
    Task.__table__,
    "after_create",
    DDL("CREATE INDEX IF NOT EXISTS idx_tasks_search_gin ON tasks USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || coalesce(notes, '')))")
    .execute_if(dialect="postgresql")
)

event.listen(
    Note.__table__,
    "after_create",
    DDL("CREATE INDEX IF NOT EXISTS idx_notes_search_gin ON notes USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, '') || ' ' || coalesce(tags, '')))")
    .execute_if(dialect="postgresql")
)

event.listen(
    Goal.__table__,
    "after_create",
    DDL("CREATE INDEX IF NOT EXISTS idx_goals_search_gin ON goals USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(category, '')))")
    .execute_if(dialect="postgresql")
)

event.listen(
    Habit.__table__,
    "after_create",
    DDL("CREATE INDEX IF NOT EXISTS idx_habits_search_gin ON habits USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(category, '')))")
    .execute_if(dialect="postgresql")
)

event.listen(
    Event.__table__,
    "after_create",
    DDL("CREATE INDEX IF NOT EXISTS idx_events_search_gin ON events USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || coalesce(location, '')))")
    .execute_if(dialect="postgresql")
)

event.listen(
    TradingJournal.__table__,
    "after_create",
    DDL("CREATE INDEX IF NOT EXISTS idx_trading_search_gin ON trading_journal USING gin(to_tsvector('english', coalesce(ticker, '') || ' ' || coalesce(strategy, '') || ' ' || coalesce(psychology_notes, '')))")
    .execute_if(dialect="postgresql")
)
