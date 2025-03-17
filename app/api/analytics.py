from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.notes import AnalyticsResponse
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/notes", response_model=AnalyticsResponse)
async def get_notes_analytics(db: AsyncSession = Depends(get_async_db)):
    """Get analytics for all notes"""
    return await analytics_service.analyze_notes_async(db)