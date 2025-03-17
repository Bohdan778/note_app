from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Base Note Schema
class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

# Schema for creating a note
class NoteCreate(NoteBase):
    pass

# Schema for updating a note
class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)

# Schema for note history
class NoteHistoryBase(BaseModel):
    title: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

# Schema for note response
class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Schema for note with history
class NoteWithHistory(NoteResponse):
    history: List[NoteHistoryBase] = []

# Schema for note summary
class NoteSummary(BaseModel):
    note_id: int
    summary: str

# Schema for analytics response
class AnalyticsResponse(BaseModel):
    total_notes: int
    total_words: int
    average_note_length: float
    most_common_words: List[tuple]
    top_3_shortest_notes: List[int]
    top_3_longest_notes: List[int]