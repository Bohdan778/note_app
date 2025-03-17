from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_main_running():
    """Перевіряє, чи працює головний API"""
    response = client.get("/")
    assert (
        response.status_code == 200
    )  # Головна сторінка має повертати статус 200
    assert response.json() == {
        "message": "Welcome to the AI-Enhanced Notes Management System"
    }


def test_main_not_found():
    response = client.get("/nonexistent-route")
    assert (
        response.status_code == 404
    )  # Неіснуючий маршрут має повертати статус 404
    assert response.json() == {"detail": "Not Found"}


def test_create_note():
    """Перевіряє, чи працює створення нотатки"""
    data = {
        "title": "Test Note",
        "content": "This is a test note content",
    }
    response = client.post("/notes/", json=data)
    assert (
        response.status_code == 201
    )  # Створення нотатки має повертати статус 201
    assert response.json()["title"] == "Test Note"  # Перевірка назви нотатки
    # Перевірка контенту
    assert response.json()["content"] == "This is a test note content"
