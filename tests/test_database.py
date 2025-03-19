import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine, SessionLocal

# Test for lines 36-40
def test_get_db():
    db = next(get_db())
    try:
        assert db is not None
        assert isinstance(db, Session)
    finally:
        db.close()

# Test for lines 47-51
@patch('app.database.SessionLocal')
def test_session_local_creation(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    db = next(get_db())
    assert db == mock_session
    mock_session.close.assert_called_once()

def test_database_connection():
    # Test that we can connect to the database
    db = SessionLocal()
    try:
        # Try to execute a simple query
        result = db.execute("SELECT 1").scalar()
        assert result == 1
    finally:
        db.close()

def test_create_tables():
    # Test that tables can be created
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Check if tables exist by querying information_schema
    db = SessionLocal()
    try:
        # For SQLite, we can check if the table exists in sqlite_master
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [row[0] for row in result]

        # Check if our tables are in the list
        # This assumes you have a 'notes' table
        assert 'notes' in table_names
    finally:
        db.close()
