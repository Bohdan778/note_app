import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
from fastapi import HTTPException

from app.services.ai import (
    list_available_models,
    summarize_text,
    summarize_text_async
)

# Test data
TEST_TEXT = "This is a test text that needs to be summarized."
TEST_TITLE = "Test Title"
TEST_SUMMARY = "Summary of the test text."

# ============= TESTS FOR list_available_models =============

def test_list_available_models_no_api_key():
    """Test list_available_models when API key is not set"""
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        with patch('app.services.ai.GEMINI_API_KEY', None):
            result = list_available_models()
            assert result == "API key not set"

def test_list_available_models_success():
    """Test list_available_models when successful"""
    # Create mock models
    mock_model1 = MagicMock()
    mock_model1.name = "gemini-pro"
    mock_model2 = MagicMock()
    mock_model2.name = "gemini-1.5-pro"
    mock_models = [mock_model1, mock_model2]

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.genai.list_models', return_value=mock_models):
                result = list_available_models()
                assert result == ["gemini-pro", "gemini-1.5-pro"]

def test_list_available_models_error():
    """Test list_available_models when an error occurs"""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.genai.list_models', side_effect=Exception("API error")):
                result = list_available_models()
                assert "Error listing models: API error" in result

# ============= TESTS FOR summarize_text_async =============

@pytest.mark.asyncio
async def test_summarize_text_async():
    """Test summarize_text_async function"""
    with patch('app.services.ai.summarize_text', return_value=TEST_SUMMARY):
        result = await summarize_text_async(TEST_TEXT, TEST_TITLE)
        assert result == TEST_SUMMARY

# ============= TESTS FOR summarize_text =============

def test_summarize_text_no_api_key():
    """Test summarize_text when API key is not set"""
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        with patch('app.services.ai.GEMINI_API_KEY', None):
            with pytest.raises(HTTPException) as excinfo:
                summarize_text(TEST_TEXT, TEST_TITLE)

            assert excinfo.value.status_code == 500
            assert "GEMINI_API_KEY not set" in excinfo.value.detail

def test_summarize_text_with_available_models_in_list():
    """Test summarize_text when models are available in the list"""
    # Mock response
    mock_response = MagicMock()
    mock_response.text = TEST_SUMMARY

    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.list_available_models', return_value=["gemini-pro", "other-model"]):
                with patch('app.services.ai.genai.GenerativeModel', return_value=mock_model):
                    result = summarize_text(TEST_TEXT, TEST_TITLE)

                    # Assertions
                    assert result == TEST_SUMMARY
                    mock_model.generate_content.assert_called_once()
                    # Check that the prompt contains the title and text
                    call_args = mock_model.generate_content.call_args[0][0]
                    assert TEST_TITLE in call_args
                    assert TEST_TEXT in call_args

def test_summarize_text_with_model_not_in_list():
    """Test summarize_text when preferred models are not in the list"""
    # Mock response
    mock_response = MagicMock()
    mock_response.text = TEST_SUMMARY

    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.list_available_models', return_value=["custom-gemini-pro", "other-model"]):
                with patch('app.services.ai.genai.GenerativeModel', return_value=mock_model):
                    result = summarize_text(TEST_TEXT, TEST_TITLE)

                    # Assertions
                    assert result == TEST_SUMMARY
                    mock_model.generate_content.assert_called_once()

def test_summarize_text_with_empty_model_list():
    """Test summarize_text when model list is empty"""
    # Mock response
    mock_response = MagicMock()
    mock_response.text = TEST_SUMMARY

    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.list_available_models', return_value=[]):
                with patch('app.services.ai.genai.GenerativeModel', return_value=mock_model):
                    result = summarize_text(TEST_TEXT, TEST_TITLE)

                    # Assertions
                    assert result == TEST_SUMMARY
                    mock_model.generate_content.assert_called_once()
                    # Check that it used the default model
                    assert mock_model.generate_content.call_args[0][0].startswith(f"Title: {TEST_TITLE}")

def test_summarize_text_with_non_list_models():
    """Test summarize_text when list_available_models returns a string (error)"""
    # Mock response
    mock_response = MagicMock()
    mock_response.text = TEST_SUMMARY

    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.list_available_models', return_value="Error listing models"):
                with patch('app.services.ai.genai.GenerativeModel', return_value=mock_model):
                    result = summarize_text(TEST_TEXT, TEST_TITLE)

                    # Assertions
                    assert result == TEST_SUMMARY
                    mock_model.generate_content.assert_called_once()

def test_summarize_text_with_fallback_model():
    """Test summarize_text when it needs to use a fallback model"""
    # Mock response
    mock_response = MagicMock()
    mock_response.text = TEST_SUMMARY

    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.list_available_models', return_value=["random-model", "gemini-something-pro"]):
                with patch('app.services.ai.genai.GenerativeModel', return_value=mock_model):
                    result = summarize_text(TEST_TEXT, TEST_TITLE)

                    # Assertions
                    assert result == TEST_SUMMARY
                    mock_model.generate_content.assert_called_once()

def test_summarize_text_error():
    """Test summarize_text when an error occurs"""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.list_available_models', return_value=["gemini-pro"]):
                with patch('app.services.ai.genai.GenerativeModel', side_effect=Exception("API error")):
                    with pytest.raises(HTTPException) as excinfo:
                        summarize_text(TEST_TEXT, TEST_TITLE)

                    assert excinfo.value.status_code == 500
                    assert "AI summarization failed" in excinfo.value.detail
                    assert "API error" in excinfo.value.detail

def test_summarize_text_generate_content_error():
    """Test summarize_text when generate_content raises an error"""
    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("Generation error")

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch('app.services.ai.GEMINI_API_KEY', "fake-key"):
            with patch('app.services.ai.list_available_models', return_value=["gemini-pro"]):
                with patch('app.services.ai.genai.GenerativeModel', return_value=mock_model):
                    with pytest.raises(HTTPException) as excinfo:
                        summarize_text(TEST_TEXT, TEST_TITLE)

                    assert excinfo.value.status_code == 500
                    assert "AI summarization failed" in excinfo.value.detail
                    assert "Generation error" in excinfo.value.detail
