import pytest
from app.models.models import AuditLog, Task

def test_create_task_generates_audit_log(client, auth_headers, db):
    payload = {
        "title": "Audit log task test"
    }
    response = client.post("/api/v1/tasks/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    
    # Assert audit log entry created in db
    logs = db.query(AuditLog).all()
    assert len(logs) == 1
    assert logs[0].action == "CREATE_TASK"
    assert "Audit log task test" in logs[0].new_value

def test_update_task_generates_audit_log(client, auth_headers, db, test_user):
    task = Task(user_id=test_user.id, title="Initial Task", priority="Medium", status="Pending")
    db.add(task)
    db.commit()
    db.refresh(task)

    payload = {
        "priority": "High"
    }
    response = client.put(f"/api/v1/tasks/{task.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200

    # There might be 1 audit log for CREATE_TASK if created via API, but here we created direct in db,
    # so there should be exactly 1 audit log for UPDATE_TASK.
    logs = db.query(AuditLog).filter(AuditLog.action == "UPDATE_TASK").all()
    assert len(logs) == 1
    assert "Status: Pending, Priority: Medium" in logs[0].old_value
    assert "Status: Pending, Priority: High" in logs[0].new_value
