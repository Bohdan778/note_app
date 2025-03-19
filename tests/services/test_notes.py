import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notes import Note, NoteHistory
from app.schemas.notes import NoteCreate, NoteUpdate
from app.services.notes import (
    # Sync functions
    create_note, get_note, get_all_notes,
    update_note, delete_note, get_note_history,
    # Async functions
    create_note_async, get_note_async, get_all_notes_async,
    update_note_async, delete_note_async, get_note_history_async
)

# ============= SYNC TESTS =============

def test_create_note(db):
    # Create test data
    note_data = NoteCreate(title="Test Note", content="Test Content")

    # Call the function directly
    result = create_note(db, note_data)

    # Assertions
    assert result is not None
    assert result.title == "Test Note"
    assert result.content == "Test Content"

def test_get_note(db):
    # First create a note
    note_data = NoteCreate(title="Test Note", content="Test Content")
    db_note = create_note(db, note_data)

    # Call the function directly
    result = get_note(db, db_note.id)

    # Assertions
    assert result is not None
    assert result.id == db_note.id
    assert result.title == "Test Note"

def test_get_note_not_found(db):
    # Call with non-existent ID
    with pytest.raises(HTTPException) as excinfo:
        get_note(db, 99999)

    assert excinfo.value.status_code == 404
    assert "Note not found" in excinfo.value.detail

def test_get_all_notes(db):
    # Create multiple notes
    create_note(db, NoteCreate(title="Note 1", content="Content 1"))
    create_note(db, NoteCreate(title="Note 2", content="Content 2"))

    # Call the function directly
    results = get_all_notes(db)

    # Assertions
    assert len(results) >= 2
    titles = [note.title for note in results]
    assert "Note 1" in titles
    assert "Note 2" in titles

def test_update_note(db):
    # First create a note
    note_data = NoteCreate(title="Original Title", content="Original Content")
    db_note = create_note(db, note_data)

    # Call the function directly
    update_data = NoteUpdate(title="Updated Title", content="Updated Content")
    result = update_note(db, db_note.id, update_data)

    # Assertions
    assert result is not None
    assert result.id == db_note.id
    assert result.title == "Updated Title"
    assert result.content == "Updated Content"

    # Check history was created
    history = db.query(NoteHistory).filter(NoteHistory.note_id == db_note.id).all()
    assert len(history) == 1
    assert history[0].title == "Original Title"
    assert history[0].content == "Original Content"

def test_update_note_partial(db):
    # First create a note
    note_data = NoteCreate(title="Original Title", content="Original Content")
    db_note = create_note(db, note_data)

    # Call with only title update
    update_data = NoteUpdate(title="Updated Title", content=None)
    result = update_note(db, db_note.id, update_data)

    # Assertions
    assert result.title == "Updated Title"
    assert result.content == "Original Content"  # Should not change

def test_delete_note(db):
    # First create a note
    note_data = NoteCreate(title="Test Note", content="Test Content")
    db_note = create_note(db, note_data)

    # Call the function directly
    result = delete_note(db, db_note.id)

    # Assertions
    assert result is True

    # Verify note is deleted
    deleted_note = db.query(Note).filter(Note.id == db_note.id).first()
    assert deleted_note is None

def test_get_note_history(db):
    # First create a note
    note_data = NoteCreate(title="Original Title", content="Original Content")
    db_note = create_note(db, note_data)

    # Update it to create history
    update_data = NoteUpdate(title="Updated Title", content="Updated Content")
    update_note(db, db_note.id, update_data)

    # Call the function directly
    history = get_note_history(db, db_note.id)

    # Assertions
    assert len(history) == 1
    assert history[0].title == "Original Title"
    assert history[0].content == "Original Content"

# ============= ASYNC TESTS =============

@pytest.mark.asyncio
async def test_create_note_async():
    # Create a mock AsyncSession
    mock_db = AsyncMock(spec=AsyncSession)

    # Create test data
    note_data = NoteCreate(title="Test Note", content="Test Content")

    # Call the function
    result = await create_note_async(mock_db, note_data)

    # Assertions
    assert result is not None
    assert result.title == "Test Note"
    assert result.content == "Test Content"
    assert mock_db.add.called
    await mock_db.commit()  # Make sure to await the coroutine
    await mock_db.refresh(result)  # Make sure to await the coroutine

@pytest.mark.asyncio
async def test_get_note_async():
    # Create a mock AsyncSession
    mock_db = AsyncMock(spec=AsyncSession)

    # Create a mock note
    mock_note = Note(id=1, title="Test Note", content="Test Content")

    # Setup mock for execute
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_note
    mock_result.scalars.return_value = mock_scalars

    # Set up the execute method to return the mock_result
    mock_db.execute.return_value = mock_result

    # Call the function
    result = await get_note_async(mock_db, 1)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.title == "Test Note"
    assert result.content == "Test Content"
    assert mock_db.execute.called

@pytest.mark.asyncio
async def test_get_note_async_not_found():
    # Create a mock AsyncSession
    mock_db = AsyncMock(spec=AsyncSession)

    # Setup mock for execute with None result
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars

    # Set up the execute method to return the mock_result
    mock_db.execute.return_value = mock_result

    # Call the function and check for exception
    with pytest.raises(HTTPException) as excinfo:
        await get_note_async(mock_db, 1)

    # Assertions
    assert excinfo.value.status_code == 404
    assert "Note not found" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_all_notes_async():
    # Create a mock AsyncSession
    mock_db = AsyncMock(spec=AsyncSession)

    # Create mock notes
    mock_notes = [
        Note(id=1, title="Test Note 1", content="Test Content 1"),
        Note(id=2, title="Test Note 2", content="Test Content 2")
    ]

    # Setup mock for execute
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = mock_notes
    mock_result.scalars.return_value = mock_scalars

    # Set up the execute method to return the mock_result
    mock_db.execute.return_value = mock_result

    # Call the function
    results = await get_all_notes_async(mock_db)

    # Assertions
    assert results is not None
    assert len(results) == 2
    assert results[0].title == "Test Note 1"
    assert results[1].title == "Test Note 2"
    assert mock_db.execute.called

@pytest.mark.asyncio
async def test_update_note_async():
    # Create a mock AsyncSession
    mock_db = AsyncMock(spec=AsyncSession)

    # Create a mock note
    mock_note = Note(id=1, title="Original Title", content="Original Content")

    # Mock get_note_async to return the note directly
    with patch('app.services.notes.get_note_async', autospec=True) as mock_get:
        mock_get.return_value = mock_note

        # Prepare update data
        update_data = NoteUpdate(title="Updated Title", content="Updated Content")

        # Call the function
        result = await update_note_async(mock_db, 1, update_data)

        # Assertions
        assert result is not None
        assert result.id == 1
        assert result.title == "Updated Title"
        assert result.content == "Updated Content"
        assert mock_db.add.called  # For history record
        await mock_db.commit()  # Make sure to await the coroutine
        await mock_db.refresh(result)  # Make sure to await the coroutine

@pytest.mark.asyncio
async def test_delete_note_async():
    # Create a mock AsyncSession
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.delete = AsyncMock()  # Explicitly make delete an AsyncMock

    # Create a mock note
    mock_note = Note(id=1, title="Test Note", content="Test Content")

    # Mock get_note_async to return the note directly
    with patch('app.services.notes.get_note_async', autospec=True) as mock_get:
        mock_get.return_value = mock_note

        # Call the function
        result = await delete_note_async(mock_db, 1)

        # Assertions
        assert result is True
        assert mock_db.delete.called
        await mock_db.commit()  # Make sure to await the coroutine

@pytest.mark.asyncio
async def test_get_note_history_async():
    # Create a mock AsyncSession
    mock_db = AsyncMock(spec=AsyncSession)

    # Create a mock note and history
    mock_note = Note(id=1, title="Current Title", content="Current Content")
    mock_history = [
        NoteHistory(id=1, note_id=1, title="Original Title", content="Original Content"),
        NoteHistory(id=2, note_id=1, title="Updated Title 1", content="Updated Content 1")
    ]

    # Mock get_note_async to return the note directly
    with patch('app.services.notes.get_note_async', autospec=True) as mock_get:
        mock_get.return_value = mock_note

        # Setup mock for execute
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_history
        mock_result.scalars.return_value = mock_scalars

        # Set up the execute method to return the mock_result
        mock_db.execute.return_value = mock_result

        # Call the function
        history = await get_note_history_async(mock_db, 1)

        # Assertions
        assert history is not None
        assert len(history) == 2
        assert history[0].title == "Original Title"
        assert history[1].title == "Updated Title 1"
        assert mock_db.execute.called
