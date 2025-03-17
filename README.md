# AI-Enhanced Notes Management System

A RESTful API service for managing notes with AI capabilities, built with FastAPI and SQLAlchemy.

## Features

- **Notes Management**: Create, read, update, and delete notes with version history
- **AI Integration**: Summarize notes using Google's Gemini AI
- **Analytics**: Analyze notes to get insights like word count, average length, and common words
- **Comprehensive Testing**: Unit and integration tests with high coverage

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Google Gemini AI**: For note summarization
- **Pandas & NLTK**: For data analysis and text processing
- **Pytest**: For testing

## Installation

### Prerequisites

- Python 3.8+
- Gemini API key (get one from [Google AI Studio](https://aistudio.google.com/))

### Setup

1. Clone the repository:
git clone [https://github.com/yourusername/notes-ai-system.git](https://github.com/yourusername/notes-ai-system.git)
cd notes-ai-system


2. Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install dependencies:
pip install -r requirements.txt


4. Create a `.env` file in the root directory with your Gemini API key:
DATABASE_URL=sqlite:///./notes.db
GEMINI_API_KEY=your_gemini_api_key_here


## Running the Application

1. Start the FastAPI server:
uvicorn app.main:app --reload


2. The API will be available at `http://localhost:8000`
3. Access the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Notes

- `POST /notes/` - Create a new note
- `GET /notes/{note_id}` - Get a note by ID
- `GET /notes/` - Get all notes (with pagination)
- `PUT /notes/{note_id}` - Update a note
- `DELETE /notes/{note_id}` - Delete a note
- `GET /notes/{note_id}/history` - Get a note with its version history

### AI

- `GET /ai/notes/{note_id}/summary` - Generate a summary for a note using AI
- `GET /ai/models` - List available AI models

### Analytics

- `GET /analytics/notes` - Get analytics for all notes

## Testing

Run the tests with pytest:
pytest


For test coverage report:
pytest --cov=app tests/


## Project Structure
notes_app/
├── app/
│   ├── **init**.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── .env                     # Environment variables (not in git)
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation

## Implementation Details

### Notes Management

The system allows for complete management of notes with CRUD operations. Each note has a title, content, and timestamps. When a note is updated, the previous version is automatically saved to the history.

### AI Integration

The system uses Google's Gemini AI to generate summaries of notes. This helps users quickly understand the content of long notes without having to read the entire text.

### Analytics

The analytics feature provides insights into the notes database, including:
- Total number of notes
- Total word count across all notes
- Average note length
- Most common words
- Top 3 shortest and longest notes

## License

This project is licensed under the MIT License - see the LICENSE file for details.
