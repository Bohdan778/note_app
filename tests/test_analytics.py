import pytest
from fastapi.testclient import TestClient

def test_empty_analytics(client):
    """Test analytics with no notes"""
    response = client.get("/analytics/notes")
    assert response.status_code == 200
    data = response.json()
    assert data["total_notes"] == 0
    assert data["total_words"] == 0
    assert data["average_note_length"] == 0
    assert data["most_common_words"] == []
    assert data["top_3_shortest_notes"] == []
    assert data["top_3_longest_notes"] == []

def test_analytics_with_notes(client):
    """Test analytics with multiple notes"""
    # Create several notes with different lengths
    client.post("/notes/", json={"title": "Short Note", "content": "Short."})
    client.post("/notes/", json={"title": "Medium Note", "content": "This is a medium length note with several words."})
    client.post("/notes/", json={"title": "Long Note", "content": "This is a much longer note with many more words. It should have the highest word count among all the notes we've created for this test. We need to make sure it has significantly more words than the others."})
    
    # Get analytics
    response = client.get("/analytics/notes")
    assert response.status_code == 200
    data = response.json()
    
    # Basic assertions
    assert data["total_notes"] == 3
    assert data["total_words"] > 0
    assert data["average_note_length"] > 0
    assert len(data["most_common_words"]) > 0
    assert len(data["top_3_shortest_notes"]) == 3
    assert len(data["top_3_longest_notes"]) == 3
    
    # The shortest note should be first in the shortest list
    shortest_id = data["top_3_shortest_notes"][0]
    shortest_response = client.get(f"/notes/{shortest_id}")
    assert shortest_response.json()["title"] == "Short Note"
    
    # The longest note should be first in the longest list
    longest_id = data["top_3_longest_notes"][-1]
    longest_response = client.get(f"/notes/{longest_id}")
    assert longest_response.json()["title"] == "Long Note"