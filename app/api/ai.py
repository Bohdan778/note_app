from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.notes import NoteSummary
from app.services import notes as notes_service
from app.services import ai as ai_service

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/notes/{note_id}/summary", response_model=NoteSummary)
async def summarize_note(note_id: int, db: AsyncSession = Depends(get_async_db)):
    """Generate a summary for a note using AI"""
    note = await notes_service.get_note_async(db, note_id)
    summary = await ai_service.summarize_text_async(note.content, note.title)
    
    return {
        "note_id": note.id,
        "summary": summary
    }

@router.get("/models")
async def get_available_models():
    """Get list of available AI models"""
    return {"models": ai_service.list_available_models()}