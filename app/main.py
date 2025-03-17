from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import engine, Base
from app.api import notes, ai, analytics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Enhanced Notes Management System",
    description="A RESTful API for managing notes with AI capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes.router)
app.include_router(ai.router)
app.include_router(analytics.router)

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the AI-Enhanced Notes Management System"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)