from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import delete, update
from app.models.notes import Note, NoteHistory
from app.schemas.notes import NoteCreate, NoteUpdate
from typing import List, Optional
from fastapi import HTTPException

# Async versions

async def create_note_async(db: AsyncSession, note: NoteCreate) -> Note:
    """Create a new note (async)"""
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


async def get_note_async(db: AsyncSession, note_id: int) -> Note:
    """Get a note by ID (async)"""
    result = await db.execute(select(Note).filter(Note.id == note_id))
    note = result.scalars().first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


async def get_all_notes_async(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Note]:
    """Get all notes with pagination (async)"""
    result = await db.execute(select(Note).offset(skip).limit(limit))
    return result.scalars().all()


async def update_note_async(
    db: AsyncSession, note_id: int, note_update: NoteUpdate
) -> Note:
    """Update a note and save the previous version to history (async)"""
    db_note = await get_note_async(db, note_id)

    # Create history record before updating
    note_history = NoteHistory(
        note_id=db_note.id, title=db_note.title, content=db_note.content
    )
    db.add(note_history)

    # Update note with new values
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.content is not None:
        db_note.content = note_update.content

    await db.commit()
    await db.refresh(db_note)
    return db_note


async def delete_note_async(db: AsyncSession, note_id: int) -> bool:
    """Delete a note (async)"""
    db_note = await get_note_async(db, note_id)
    await db.delete(db_note)
    await db.commit()
    return True


async def get_note_history_async(
    db: AsyncSession, note_id: int
) -> List[NoteHistory]:
    """Get the history of a note (async)"""
    note = await get_note_async(db, note_id)
    result = await db.execute(
        select(NoteHistory)
        .filter(NoteHistory.note_id == note_id)
        .order_by(NoteHistory.created_at)
    )
    return result.scalars().all()


# Sync versions for testing


def create_note(db: Session, note: NoteCreate) -> Note:
    """Create a new note (sync)"""
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_note(db: Session, note_id: int) -> Note:
    """Get a note by ID (sync)"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


def get_all_notes(db: Session, skip: int = 0, limit: int = 100) -> List[Note]:
    """Get all notes with pagination (sync)"""
    return db.query(Note).offset(skip).limit(limit).all()


def update_note(db: Session, note_id: int, note_update: NoteUpdate) -> Note:
    """Update a note and save the previous version to history (sync)"""
    db_note = get_note(db, note_id)

    # Create history record before updating
    note_history = NoteHistory(
        note_id=db_note.id, title=db_note.title, content=db_note.content
    )
    db.add(note_history)

    # Update note with new values
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.content is not None:
        db_note.content = note_update.content

    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int) -> bool:
    """Delete a note (sync)"""
    db_note = get_note(db, note_id)
    db.delete(db_note)
    db.commit()
    return True


def get_note_history(db: Session, note_id: int) -> List[NoteHistory]:
    """Get the history of a note (sync)"""
    note = get_note(db, note_id)
    return (
        db.query(NoteHistory)
        .filter(NoteHistory.note_id == note_id)
        .order_by(NoteHistory.created_at)
        .all()
    )
