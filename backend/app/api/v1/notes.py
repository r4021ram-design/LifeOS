from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, Note
from app.schemas.schemas import NoteCreate, NoteResponse
from app.core.audit import log_audit

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/", response_model=List[NoteResponse])
def list_notes(
    tag: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Note).filter(Note.user_id == current_user.id)
    if tag:
        query = query.filter(Note.tags.like(f"%{tag}%"))
    return query.all()

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note_in: NoteCreate, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_note = Note(
        user_id=current_user.id,
        title=note_in.title,
        content=note_in.content,
        tags=note_in.tags,
        parent_note_id=note_in.parent_note_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    log_audit(db, current_user.id, "CREATE_NOTE", None, f"Note Title: {db_note.title}", request.client.host if request.client else None)
    return db_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_title = db_note.title
    db.delete(db_note)
    db.commit()
    
    log_audit(db, current_user.id, "DELETE_NOTE", f"Title: {note_title}", None, request.client.host if request.client else None)
    return None
