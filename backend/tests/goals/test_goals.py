import pytest
from app.models.models import Goal, GoalMilestone

def test_list_goals_empty(client, auth_headers):
    response = client.get("/api/v1/goals/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_goal_success(client, auth_headers):
    payload = {
        "title": "Learn Rust",
        "category": "Learning",
        "target_value": 100.0,
        "deadline": "2026-12-31"
    }
    response = client.post("/api/v1/goals/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learn Rust"
    assert data["category"] == "Learning"
    assert data["status"] == "Pending"

def test_add_milestone_and_progress_recalculation(client, auth_headers, db, test_user):
    goal = Goal(user_id=test_user.id, title="Learn Rust", target_value=100.0, current_value=0.0)
    db.add(goal)
    db.commit()
    db.refresh(goal)

    payload = {
        "title": "Read Chapter 1",
        "progress": 50.0,
        "is_completed": True
    }
    response = client.post(f"/api/v1/goals/{goal.id}/milestones", json=payload, headers=auth_headers)
    assert response.status_code == 200
    
    # Verify goal progress updated to 100% since 1/1 milestone is completed
    db.refresh(goal)
    assert goal.current_value == 100.0
    assert goal.status == "Completed"
