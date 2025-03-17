def test_create_note(client):
    """Перевіряє створення нотатки через API"""
    response = client.post(
        "/notes/", json={"title": "Test Note", "content": "Test content."}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test content."
    assert "id" in data


def test_get_note(client):
    """Перевіряє отримання нотатки"""
    create_response = client.post(
        "/notes/", json={"title": "Test", "content": "Test content."}
    )
    note_id = create_response.json()["id"]

    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id


def test_update_note(client):
    """Перевіряє оновлення нотатки"""
    create_response = client.post(
        "/notes/", json={"title": "Original", "content": "Content"}
    )
    note_id = create_response.json()["id"]

    response = client.put(
        f"/notes/{note_id}",
        json={"title": "Updated", "content": "Updated content"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_delete_note(client):
    """Перевіряє видалення нотатки"""
    create_response = client.post(
        "/notes/", json={"title": "To delete", "content": "Content"}
    )
    note_id = create_response.json()["id"]

    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204

    get_response = client.get(f"/notes/{note_id}")
    assert get_response.status_code == 404
