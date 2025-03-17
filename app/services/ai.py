import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

# Get Gemini API key, but don't fail if not set
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Only configure if key is available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def list_available_models():
    """List all available models for debugging"""
    if not GEMINI_API_KEY:
        return "API key not set"

    try:
        models = genai.list_models()
        return [model.name for model in models]
    except Exception as e:
        return f"Error listing models: {str(e)}"


async def summarize_text_async(text: str, title: str = "") -> str:
    """
    Summarize text using Gemini API (async)
    """
    return summarize_text(text, title)


def summarize_text(text: str, title: str = "") -> str:
    """
    Summarize text using Gemini API (sync)
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "GEMINI_API_KEY not set. Configure it to use AI."
                ),
        )

    try:
        # Спробуємо отримати список доступних моделей
        available_models = list_available_models()

        # Виберемо відповідну модель
        model_name = None

        # Перевіряємо різні варіанти назв моделей
        possible_models = [
            "gemini-pro",
            "models/gemini-pro",
            "gemini-1.5-pro",
            "models/gemini-1.5-pro",
            "gemini-1.0-pro",
        ]

        # Якщо ми змогли отримати список моделей, перевіримо, які з них
        # доступні
        if isinstance(available_models, list):
            for model in possible_models:
                if model in available_models or any(
                    m.endswith(model) for m in available_models
                ):
                    model_name = model
                    break

        # Якщо не знайшли жодної моделі в списку, спробуємо використати першу
        # зі списку можливих
        if (
            not model_name
            and isinstance(available_models, list)
            and available_models
        ):
            # Використовуємо першу доступну модель
            for model in available_models:
                if "gemini" in model.lower() and "pro" in model.lower():
                    model_name = model
                    break

        # Якщо все ще немає моделі, використовуємо стандартну
        if not model_name:
            model_name = "gemini-pro"

        # Створюємо модель і генеруємо вміст
        model = genai.GenerativeModel(model_name)
        prompt = f"Title: {title}\nContent: {text}\nSummarize briefly."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Якщо виникла помилка, повертаємо фіктивний підсумок
        fallback_summary = f"Підсумок для '{title}': Основні ідеї."

        # return fallback_summary
        raise HTTPException(
            status_code=500,
            detail=f"AI summarization failed: {
                str(e)}",
        )
