import pytest
from unittest.mock import patch, MagicMock
from fastapi.exceptions import HTTPException
from app.services.ai import (
    summarize_text,
    summarize_text_async,
    list_available_models,
)

# Фікстури для мока API


@pytest.fixture
def mock_gemini_api_key():
    with patch("app.services.ai.GEMINI_API_KEY", "mock_api_key"):
        yield "mock_api_key"


@pytest.fixture
def mock_available_models():
    with patch("app.services.ai.genai.list_models") as mock_list_models:
        mock_list_models.return_value = [
            MagicMock(name="gemini-1.0-pro"),
            MagicMock(name="gemini-pro"),
            MagicMock(name="gemini-1.5-pro"),
        ]
        yield


# Тест для успішного самаризування тексту


def test_summarize_text(mock_gemini_api_key, mock_available_models):
    """Перевіряє самарізацію тексту через Gemini API"""
    with patch("app.services.ai.genai.GenerativeModel") as mock_model:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a mock summary of the note."
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance

        summary = summarize_text("This is a test note content.")
        assert summary == "This is a mock summary of the note."


# Тест для обробки помилки при самаризації


def test_summarize_text_with_error(mock_gemini_api_key, mock_available_models):
    with patch("app.services.ai.genai.GenerativeModel") as mock_model:
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = Exception("API error")
        mock_model.return_value = mock_instance

        # Перевіряємо, чи правильно обробляється помилка
        try:
            summarize_text("Test content", "Test Note")
        except HTTPException as exc:
            assert exc.status_code == 500
            assert "AI summarization failed" in exc.detail


# Тест для асинхронного самаризування тексту


@pytest.mark.asyncio
async def test_summarize_text_async(
    mock_gemini_api_key, mock_available_models
):
    """Перевіряє асинхронну самарізацію тексту через Gemini API"""
    with patch("app.services.ai.genai.GenerativeModel") as mock_model:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a mock summary of the note."
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance

        summary = await summarize_text_async("This is a test note content.")
        assert summary == "This is a mock summary of the note."


# Тест для обробки помилки при асинхронній самаризації


@pytest.mark.asyncio
async def test_summarize_text_async_with_error(
    mock_gemini_api_key, mock_available_models
):
    with patch("app.services.ai.genai.GenerativeModel") as mock_model:
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = Exception("API error")
        mock_model.return_value = mock_instance

        # Перевіряємо, чи правильно обробляється помилка
        try:
            await summarize_text_async("Test content", "Test Note")
        except HTTPException as exc:
            assert exc.status_code == 500
            assert "AI summarization failed" in exc.detail


# Тест для отримання списку доступних моделей


def test_list_available_models(mock_gemini_api_key):
    """Перевіряє список доступних моделей через Gemini API"""
    with patch("app.services.ai.genai.list_models") as mock_list_models:
        # Створюємо фіктивні моделі з атрибутом .name
        mock_model_1 = MagicMock()
        mock_model_1.name = "models/gemini-1.0-pro"
        mock_model_2 = MagicMock()
        mock_model_2.name = "models/gemini-pro"
        mock_model_3 = MagicMock()
        mock_model_3.name = "models/gemini-1.5-pro"

        # Повертаємо список моделей
        mock_list_models.return_value = [
            mock_model_1,
            mock_model_2,
            mock_model_3,
        ]

        # Викликаємо функцію для отримання списку моделей
        models = list_available_models()

        # Перевіряємо, чи є хоча б одна модель, що містить "gemini" в її назві
        assert any(
            "gemini" in model.lower() for model in models
        ), f"Models found: {models}"


# Тест для обробки помилки, якщо API ключ не налаштований


def test_list_available_models_with_no_api_key():
    """Перевіряє обробку ситуації, коли API ключ не налаштований"""
    with patch("app.services.ai.GEMINI_API_KEY", None):
        models = list_available_models()
        assert models == "API key not set"
