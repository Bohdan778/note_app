import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.api.ai import router, summarize_note, get_available_models
from app.models.notes import Note
from app.schemas.notes import NoteSummary


@pytest.mark.asyncio
async def test_summarize_note_direct():
    """Test the summarize_note function directly"""
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock note
    mock_note = MagicMock(spec=Note)
    mock_note.id = 1
    mock_note.title = "Test Title"
    mock_note.content = "Test content for summarization"

    # Mock service functions
    with patch("app.api.ai.notes_service.get_note_async", return_value=mock_note) as mock_get_note, \
         patch("app.api.ai.ai_service.summarize_text_async", return_value="Brief note summary") as mock_summarize:

        # Call the function directly
        result = await summarize_note(note_id=1, db=mock_db)

        # Verify function calls
        mock_get_note.assert_called_once_with(mock_db, 1)
        mock_summarize.assert_called_once_with(mock_note.content, mock_note.title)

        # Check result
        assert result["note_id"] == 1
        assert result["summary"] == "Brief note summary"


@pytest.mark.asyncio
async def test_summarize_note_not_found_direct():
    """Test the summarize_note function with note not found"""
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock service function to raise exception
    with patch("app.api.ai.notes_service.get_note_async",
               side_effect=HTTPException(status_code=404, detail="Note not found")) as mock_get_note:

        # Call the function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await summarize_note(note_id=999, db=mock_db)

        # Verify exception details
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Note not found"

        # Verify function call
        mock_get_note.assert_called_once_with(mock_db, 999)


@pytest.mark.asyncio
async def test_summarize_note_ai_error_direct():
    """Test the summarize_note function with AI service error"""
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock note
    mock_note = MagicMock(spec=Note)
    mock_note.id = 1
    mock_note.title = "Test Title"
    mock_note.content = "Test content for summarization"

    # Mock service functions
    with patch("app.api.ai.notes_service.get_note_async", return_value=mock_note) as mock_get_note, \
         patch("app.api.ai.ai_service.summarize_text_async",
               side_effect=Exception("AI service error")) as mock_summarize:

        # Call the function and expect exception
        with pytest.raises(Exception) as exc_info:
            await summarize_note(note_id=1, db=mock_db)

        # Verify exception details
        assert str(exc_info.value) == "AI service error"

        # Verify function calls
        mock_get_note.assert_called_once_with(mock_db, 1)
        mock_summarize.assert_called_once_with(mock_note.content, mock_note.title)


@pytest.mark.asyncio
async def test_get_available_models_direct():
    """Test the get_available_models function directly"""
    # Mock models
    mock_models = ["gpt-3.5-turbo", "gemini-pro", "claude-2"]

    # Mock service function
    with patch("app.api.ai.ai_service.list_available_models", return_value=mock_models) as mock_list_models:

        # Call the function directly
        result = await get_available_models()

        # Verify function call
        mock_list_models.assert_called_once()

        # Check result
        assert result["models"] == mock_models


@pytest.mark.asyncio
async def test_get_available_models_empty_direct():
    """Test the get_available_models function with empty list"""
    # Mock service function
    with patch("app.api.ai.ai_service.list_available_models", return_value=[]) as mock_list_models:

        # Call the function directly
        result = await get_available_models()

        # Verify function call
        mock_list_models.assert_called_once()

        # Check result
        assert result["models"] == []


# Fixed HTTP client tests
def test_summarize_note_http(client):
    """Test the summarize_note endpoint via HTTP"""
    # Mock note
    mock_note = MagicMock(spec=Note)
    mock_note.id = 1
    mock_note.title = "Test Title"
    mock_note.content = "Test content for summarization"

    # Mock service functions
    with patch("app.api.ai.notes_service.get_note_async", return_value=mock_note), \
         patch("app.api.ai.ai_service.summarize_text_async", return_value="Brief note summary"), \
         patch("app.api.ai.get_async_db"):  # Mock the dependency

        # Make HTTP request
        response = client.get("/ai/notes/1/summary")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["note_id"] == 1
        assert data["summary"] == "Brief note summary"


def test_get_available_models_http(client):
    """Test the get_available_models endpoint via HTTP"""
    # Mock models
    mock_models = ["gpt-3.5-turbo", "gemini-pro", "claude-2"]

    # Mock service function
    with patch("app.api.ai.ai_service.list_available_models", return_value=mock_models):

        # Make HTTP request
        response = client.get("/ai/models")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["models"] == mock_models
