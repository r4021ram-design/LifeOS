import pytest
from app.models.models import Habit, HabitLog

def test_list_habits_empty(client, auth_headers):
    response = client.get("/api/v1/habits/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_habit_success(client, auth_headers):
    payload = {
        "name": "Meditation",
        "category": "Mindfulness",
        "frequency": "Daily",
        "goal": "15 mins daily"
    }
    response = client.post("/api/v1/habits/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Meditation"
    assert data["category"] == "Mindfulness"
    assert data["frequency"] == "Daily"

def test_log_habit_success(client, auth_headers, db, test_user):
    habit = Habit(user_id=test_user.id, name="Drink Water", frequency="Daily")
    db.add(habit)
    db.commit()
    db.refresh(habit)

    payload = {
        "date": "2026-06-18",
        "status": "Completed"
    }
    response = client.post(f"/api/v1/habits/{habit.id}/logs", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Completed"
    assert data["date"] == "2026-06-18"
