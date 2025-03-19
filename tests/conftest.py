import pytest
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import the main application
from app.main import app as test_app
from app.database import Base, get_db, get_async_db

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# Set a mock API key for testing if not already set
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "mock_api_key_for_testing"

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create engines
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
async_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factories
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
AsyncTestingSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=async_engine
)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    """
    # Create the database tables
    Base.metadata.create_all(bind=engine)

    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def async_db():
    """
    Create a fresh async database for each test.
    """
    # Create the database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a new async session for each test
    async_db = AsyncTestingSessionLocal()
    try:
        yield async_db
    finally:
        await async_db.close()

    # Drop all tables after the test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client for synchronous endpoints.
    """
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db
        finally:
            pass

    # Override the DB dependency
    test_app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(test_app) as c:
        yield c

    # Reset the dependency override
    test_app.dependency_overrides = {}


@pytest.fixture(scope="function")
async def async_client(async_db):
    """
    Create a test client for asynchronous endpoints.
    """
    # Override the get_async_db dependency to use the test database
    async def override_get_async_db():
        try:
            yield async_db
        finally:
            pass

    # Override the DB dependency
    test_app.dependency_overrides[get_async_db] = override_get_async_db

    # Create async test client
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac

    # Reset the dependency override
    test_app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_note_data():
    """
    Provide test data for notes.
    """
    return {
        "title": "Test Note",
        "content": "This is a test note content."
    }


@pytest.fixture(scope="function")
def test_note_update_data():
    """
    Provide test data for note updates.
    """
    return {
        "title": "Updated Test Note",
        "content": "This is updated test note content."
    }
