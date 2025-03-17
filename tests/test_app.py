from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.notes import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteWithHistory,
    NoteSummary,
    AnalyticsResponse,
)
from app.services import notes, ai, analytics

# Create a test app that uses sync versions of service functions
test_app = FastAPI()

# Notes endpoints


@test_app.post("/notes/", response_model=NoteResponse, status_code=201)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    return notes.create_note(db, note)


@test_app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    return notes.get_note(db, note_id)


@test_app.get("/notes/", response_model=List[NoteResponse])
def get_all_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return notes.get_all_notes(db, skip, limit)


@test_app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int, note_update: NoteUpdate, db: Session = Depends(get_db)
):
    return notes.update_note(db, note_id, note_update)


@test_app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    notes.delete_note(db, note_id)
    return None


@test_app.get("/notes/{note_id}/history", response_model=NoteWithHistory)
def get_note_with_history(note_id: int, db: Session = Depends(get_db)):
    note = notes.get_note(db, note_id)
    history = notes.get_note_history(db, note_id)

    # Convert SQLAlchemy model to Pydantic model
    note_dict = {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "history": history,
    }

    return note_dict


# AI endpoints


@test_app.get("/ai/notes/{note_id}/summary", response_model=NoteSummary)
def summarize_note(note_id: int, db: Session = Depends(get_db)):
    note = notes.get_note(db, note_id)
    summary = ai.summarize_text(note.content, note.title)

    return {"note_id": note.id, "summary": summary}


# Analytics endpoints


@test_app.get("/analytics/notes", response_model=AnalyticsResponse)
def get_notes_analytics(db: Session = Depends(get_db)):
    return analytics.analyze_notes(db)
