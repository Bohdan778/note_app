from unittest.mock import patch, MagicMock

def test_summarize_note(client):
    """Перевіряє, чи працює AI-самарізація нотаток"""
    create_response = client.post("/notes/", json={"title": "AI Note", "content": "This is a test note."})
    note_id = create_response.json()["id"]

    with patch("app.services.ai.summarize_text", return_value="Mock summary"):
        response = client.get(f"/ai/notes/{note_id}/summary")
    
    assert response.status_code == 200
    assert response.json()["summary"] == "Mock summary"
