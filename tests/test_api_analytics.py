def test_analytics(client):
    """Перевіряє аналітику нотаток"""
    client.post("/notes/", json={"title": "Short", "content": "Short note."})
    client.post(
        "/notes/",
        json={
            "title": "Longer",
            "content": "This is a longer note with more words.",
        },
    )

    response = client.get("/analytics/notes")
    assert response.status_code == 200
    data = response.json()

    assert data["total_notes"] == 2
    assert data["total_words"] > 0
    assert "most_common_words" in data
