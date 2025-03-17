from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List

from app.database import get_async_db, get_db
from app.schemas.notes import NoteCreate, NoteUpdate, NoteResponse, NoteWithHistory
from app.services import notes as notes_service

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/", response_model=NoteResponse, status_code=201)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new note"""
    return await notes_service.create_note_async(db, note)

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get a note by ID"""
    return await notes_service.get_note_async(db, note_id)

@router.get("/", response_model=List[NoteResponse])
async def get_all_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all notes with pagination"""
    return await notes_service.get_all_notes_async(db, skip, limit)

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note_update: NoteUpdate, db: AsyncSession = Depends(get_async_db)):
    """Update a note"""
    return await notes_service.update_note_async(db, note_id, note_update)

@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_async_db)):
    """Delete a note"""
    await notes_service.delete_note_async(db, note_id)
    return None

@router.get("/{note_id}/history", response_model=NoteWithHistory)
async def get_note_with_history(note_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get a note with its version history"""
    note = await notes_service.get_note_async(db, note_id)
    history = await notes_service.get_note_history_async(db, note_id)
    
    # Convert SQLAlchemy model to Pydantic model
    note_dict = {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "history": history
    }
    
    return note_dict