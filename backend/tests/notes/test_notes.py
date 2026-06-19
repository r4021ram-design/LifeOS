import pytest
from app.models.models import Note

def test_list_notes_empty(client, auth_headers):
    response = client.get("/api/v1/notes/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_note_success(client, auth_headers):
    payload = {
        "title": "Hardening Notes",
        "content": "Make sure tests run at 80% coverage.",
        "tags": "dev,testing"
    }
    response = client.post("/api/v1/notes/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hardening Notes"
    assert data["content"] == "Make sure tests run at 80% coverage."
    assert data["tags"] == "dev,testing"

def test_delete_note_success(client, auth_headers, db, test_user):
    note = Note(user_id=test_user.id, title="Stale Notes", content="This notes is old.")
    db.add(note)
    db.commit()
    db.refresh(note)

    response = client.delete(f"/api/v1/notes/{note.id}", headers=auth_headers)
    assert response.status_code == 204
    assert db.query(Note).filter(Note.id == note.id).first() is None
