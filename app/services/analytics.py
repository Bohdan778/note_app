from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.notes import Note
import pandas as pd
import nltk
from collections import Counter
from typing import List, Dict, Any, Tuple
import re

# Download NLTK data
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)


def clean_text(text: str) -> str:
    """Clean text by removing special characters and converting to lowercase"""
    text = re.sub(r"[^\w\s]", "", text.lower())
    return text


def remove_stopwords(words: List[str]) -> List[str]:
    """Remove common stopwords from a list of words"""
    stopwords = set(nltk.corpus.stopwords.words("english"))
    return [word for word in words if word not in stopwords and len(word) > 1]


async def analyze_notes_async(db: AsyncSession) -> Dict[str, Any]:
    """Analyze all notes in the database (async)"""
    result = await db.execute(select(Note))
    notes = result.scalars().all()
    return _analyze_notes_helper(notes)


def analyze_notes(db: Session) -> Dict[str, Any]:
    """Analyze all notes in the database (sync)"""
    notes = db.query(Note).all()
    return _analyze_notes_helper(notes)


def _analyze_notes_helper(notes) -> Dict[str, Any]:
    if not notes:
        return {
            "total_notes": 0,
            "total_words": 0,
            "average_note_length": 0,
            "most_common_words": [],
            "top_3_shortest_notes": [],
            "top_3_longest_notes": [],
        }

    # Create a DataFrame for easier analysis
    df = pd.DataFrame(
        [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "word_count": len(nltk.word_tokenize(note.content)),
            }
            for note in notes
        ]
    )

    # Calculate total words
    total_words = df["word_count"].sum()

    # Calculate average note length
    avg_length = df["word_count"].mean()

    # Find most common words (excluding stopwords)
    all_text = " ".join([clean_text(note.content) for note in notes])
    words = nltk.word_tokenize(all_text)
    filtered_words = remove_stopwords(words)
    most_common_words = Counter(filtered_words).most_common(5)

    # Find shortest and longest notes
    df_sorted = df.sort_values("word_count")
    shortest_notes = df_sorted.head(3)["id"].tolist()
    longest_notes = df_sorted.tail(3)["id"].tolist()

    return {
        "total_notes": len(notes),
        "total_words": int(total_words),
        "average_note_length": float(avg_length),
        "most_common_words": most_common_words,
        "top_3_shortest_notes": shortest_notes,
        "top_3_longest_notes": longest_notes,
    }
