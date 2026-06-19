import pytest
from app.models.models import Task

def test_list_tasks_empty(client, auth_headers):
    response = client.get("/api/v1/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_task_success(client, auth_headers):
    payload = {
        "title": "Finish production hardening",
        "description": "Ensure 80%+ coverage and OTel setup",
        "priority": "Critical",
        "status": "Pending",
        "due_date": "2026-06-20",
        "estimated_time": 120,
        "reminder_rule": "15m_before",
        "labels": ["hardening", "ci-cd"]
    }
    response = client.post("/api/v1/tasks/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Finish production hardening"
    assert data["priority"] == "Critical"
    assert data["status"] == "Pending"
    assert len(data["labels"]) == 2
    assert data["labels"][0]["label"] == "hardening"

def test_create_task_duplicate(client, auth_headers):
    payload = {
        "title": "Duplicate task",
        "due_date": "2026-06-20"
    }
    # First creation
    response = client.post("/api/v1/tasks/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    
    # Second creation (fails with 400)
    response = client.post("/api/v1/tasks/", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "A task with the same title and due date already exists."

def test_update_task_success(client, auth_headers, db, test_user):
    # Setup initial task in db
    task = Task(user_id=test_user.id, title="Refactor codebase", priority="Medium", status="Pending")
    db.add(task)
    db.commit()
    db.refresh(task)

    payload = {
        "status": "Completed",
        "priority": "High"
    }
    response = client.put(f"/api/v1/tasks/{task.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Completed"
    assert data["priority"] == "High"

def test_delete_task_success(client, auth_headers, db, test_user):
    task = Task(user_id=test_user.id, title="Stale Task", priority="Low", status="Pending")
    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.delete(f"/api/v1/tasks/{task.id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Assert deleted from database
    assert db.query(Task).filter(Task.id == task.id).first() is None
