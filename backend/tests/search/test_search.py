import pytest
from app.models.models import Task, Note, Goal, Habit, Event, TradingJournal

def test_search_no_query_parameter(client, auth_headers):
    response = client.get("/api/v1/search/", headers=auth_headers)
    # Fastapi returns 422 if required query parameter is missing
    assert response.status_code == 422

def test_search_empty_results(client, auth_headers):
    response = client.get("/api/v1/search/?q=nonexistentkeyword", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"] == []
    assert data["notes"] == []
    assert data["goals"] == []
    assert data["habits"] == []
    assert data["events"] == []
    assert data["trading_journal"] == []

def test_search_success_with_matches(client, auth_headers, db, test_user):
    # Setup test records across multiple tables
    task = Task(user_id=test_user.id, title="Refactor index tests", priority="Low")
    note = Note(user_id=test_user.id, title="Index notes", content="Details on GIN indices")
    goal = Goal(user_id=test_user.id, title="Target Goal", category="Trading")
    habit = Habit(user_id=test_user.id, name="Daily review index", category="Routine")
    
    db.add_all([task, note, goal, habit])
    db.commit()

    # Query search for keyword "index"
    response = client.get("/api/v1/search/?q=index", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Assert SQLite LIKE fallback returns matching items
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Refactor index tests"
    
    assert len(data["notes"]) == 1
    assert data["notes"][0]["title"] == "Index notes"
    
    assert len(data["habits"]) == 1
    assert data["habits"][0]["name"] == "Daily review index"

    # Goal should not match "index"
    assert len(data["goals"]) == 0
