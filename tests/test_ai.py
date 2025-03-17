import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock the Gemini API response
@pytest.fixture
def mock_gemini_response():
    with patch("app.services.ai.GEMINI_API_KEY", "mock_api_key"), \
         patch("app.services.ai.genai.GenerativeModel") as mock_model:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a mock summary of the note."
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance
        yield

def test_summarize_note(client, mock_gemini_response):
    """Test summarizing a note with AI"""
    # First create a note
    create_response = client.post(
        "/notes/",
        json={"title": "Test Note", "content": "This is a test note content that needs to be summarized."}
    )
    note_id = create_response.json()["id"]
    
    # Then get the summary
    response = client.get(f"/ai/notes/{note_id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["note_id"] == note_id
    assert data["summary"] == "This is a mock summary of the note."

def test_summarize_nonexistent_note(client, mock_gemini_response):
    """Test summarizing a note that doesn't exist"""
    response = client.get("/ai/notes/999/summary")
    assert response.status_code == 404