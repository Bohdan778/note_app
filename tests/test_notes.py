import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_note(client):
    """Test creating a new note"""
    response = client.post(
        "/notes/",
        json={"title": "Test Note", "content": "This is a test note content."}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note content."
    assert "id" in data

def test_get_note(client):
    """Test getting a note by ID"""
    # First create a note
    create_response = client.post(
        "/notes/",
        json={"title": "Test Note", "content": "This is a test note content."}
    )
    note_id = create_response.json()["id"]
    
    # Then get the note
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note content."

def test_get_nonexistent_note(client):
    """Test getting a note that doesn't exist"""
    response = client.get("/notes/999")
    assert response.status_code == 404

def test_update_note(client):
    """Test updating a note"""
    # First create a note
    create_response = client.post(
        "/notes/",
        json={"title": "Original Title", "content": "Original content."}
    )
    note_id = create_response.json()["id"]
    
    # Then update the note
    response = client.put(
        f"/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated content."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content."

def test_delete_note(client):
    """Test deleting a note"""
    # First create a note
    create_response = client.post(
        "/notes/",
        json={"title": "Test Note", "content": "This is a test note content."}
    )
    note_id = create_response.json()["id"]
    
    # Then delete the note
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204
    
    # Verify the note is deleted
    get_response = client.get(f"/notes/{note_id}")
    assert get_response.status_code == 404

def test_get_note_history(client):
    """Test getting a note with its history"""
    # First create a note
    create_response = client.post(
        "/notes/",
        json={"title": "Original Title", "content": "Original content."}
    )
    note_id = create_response.json()["id"]
    
    # Update the note multiple times
    client.put(
        f"/notes/{note_id}",
        json={"title": "Updated Title 1", "content": "Updated content 1."}
    )
    client.put(
        f"/notes/{note_id}",
        json={"title": "Updated Title 2", "content": "Updated content 2."}
    )
    
    # Get the note with history
    response = client.get(f"/notes/{note_id}/history")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Updated Title 2"
    assert data["content"] == "Updated content 2."
    assert len(data["history"]) == 2
    assert data["history"][0]["title"] == "Original Title"
    assert data["history"][1]["title"] == "Updated Title 1"