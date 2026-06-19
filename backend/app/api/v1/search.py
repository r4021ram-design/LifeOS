from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.core.db import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, Task, Note, Goal, Habit, Event, TradingJournal
from app.schemas.schemas import SearchResponse

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_model=SearchResponse, status_code=status.HTTP_200_OK)
def search_all(
    q: str = Query(..., min_length=1, description="Search term query"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search endpoint returning matching tasks, notes, goals, habits, events, and trading logs.
    Utilizes PostgreSQL GIN Full-Text-Search in production, fallback to SQLite LIKE on development.
    """
    is_postgres = db.bind.dialect.name == "postgresql"

    if is_postgres:
        # PostgreSQL plainto_tsquery search against GIN indices
        tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            func.to_tsvector('english', 
                func.coalesce(Task.title, '') + ' ' + 
                func.coalesce(Task.description, '') + ' ' + 
                func.coalesce(Task.notes, '')
            ).op('@@')(func.plainto_tsquery('english', q))
        ).all()

        notes = db.query(Note).filter(
            Note.user_id == current_user.id,
            func.to_tsvector('english', 
                func.coalesce(Note.title, '') + ' ' + 
                func.coalesce(Note.content, '') + ' ' + 
                func.coalesce(Note.tags, '')
            ).op('@@')(func.plainto_tsquery('english', q))
        ).all()

        goals = db.query(Goal).filter(
            Goal.user_id == current_user.id,
            func.to_tsvector('english', 
                func.coalesce(Goal.title, '') + ' ' + 
                func.coalesce(Goal.category, '')
            ).op('@@')(func.plainto_tsquery('english', q))
        ).all()

        habits = db.query(Habit).filter(
            Habit.user_id == current_user.id,
            func.to_tsvector('english', 
                func.coalesce(Habit.name, '') + ' ' + 
                func.coalesce(Habit.category, '')
            ).op('@@')(func.plainto_tsquery('english', q))
        ).all()

        events = db.query(Event).filter(
            Event.user_id == current_user.id,
            func.to_tsvector('english', 
                func.coalesce(Event.title, '') + ' ' + 
                func.coalesce(Event.description, '') + ' ' + 
                func.coalesce(Event.location, '')
            ).op('@@')(func.plainto_tsquery('english', q))
        ).all()

        trading_journal = db.query(TradingJournal).filter(
            TradingJournal.user_id == current_user.id,
            func.to_tsvector('english', 
                func.coalesce(TradingJournal.ticker, '') + ' ' + 
                func.coalesce(TradingJournal.strategy, '') + ' ' + 
                func.coalesce(TradingJournal.psychology_notes, '')
            ).op('@@')(func.plainto_tsquery('english', q))
        ).all()
    else:
        # Fallback for SQLite / Development using standard wildcards
        search_pattern = f"%{q}%"

        tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            (Task.title.ilike(search_pattern)) |
            (Task.description.ilike(search_pattern)) |
            (Task.notes.ilike(search_pattern))
        ).all()

        notes = db.query(Note).filter(
            Note.user_id == current_user.id,
            (Note.title.ilike(search_pattern)) |
            (Note.content.ilike(search_pattern)) |
            (Note.tags.ilike(search_pattern))
        ).all()

        goals = db.query(Goal).filter(
            Goal.user_id == current_user.id,
            (Goal.title.ilike(search_pattern)) |
            (Goal.category.ilike(search_pattern))
        ).all()

        habits = db.query(Habit).filter(
            Habit.user_id == current_user.id,
            (Habit.name.ilike(search_pattern)) |
            (Habit.category.ilike(search_pattern))
        ).all()

        events = db.query(Event).filter(
            Event.user_id == current_user.id,
            (Event.title.ilike(search_pattern)) |
            (Event.description.ilike(search_pattern)) |
            (Event.location.ilike(search_pattern))
        ).all()

        trading_journal = db.query(TradingJournal).filter(
            TradingJournal.user_id == current_user.id,
            (TradingJournal.ticker.ilike(search_pattern)) |
            (TradingJournal.strategy.ilike(search_pattern)) |
            (TradingJournal.psychology_notes.ilike(search_pattern))
        ).all()

    return {
        "tasks": tasks,
        "notes": notes,
        "goals": goals,
        "habits": habits,
        "events": events,
        "trading_journal": trading_journal
    }
