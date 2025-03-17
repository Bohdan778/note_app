from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for simplicity, but can be changed to any other database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")
# Convert the URL to async format for SQLAlchemy 2.0
ASYNC_DATABASE_URL = DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=True,
    future=True
)

# Create sync engine for creating tables and testing
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    future=True
)

# Session factories
AsyncSessionLocal = sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get async DB session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Dependency to get sync DB session (for testing)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()