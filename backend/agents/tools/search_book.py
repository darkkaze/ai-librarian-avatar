"""
Search book by title tool.
"""
from langchain_core.tools import tool
from typing import Optional, Dict, Any
from db.models import SessionLocal
from db.repository import BookRepository
from sentence_transformers import SentenceTransformer

# Load model once (singleton pattern)
_model = None


def get_model():
    """Get or create sentence transformer model."""
    global _model
    if _model is None:
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model


@tool
def search_book_by_title(title: str) -> Optional[Dict[str, Any]]:
    """
    Search for a specific book by title.

    Performs vector similarity matching on book titles in the database.

    Args:
        title: Book title to search for

    Returns:
        Book information if found, None if not found
        Format: {"titulo": str, "autor": str, "genero": str, "synopsis": str, "disponibilidad": bool, "estante": str}
    """
    model = get_model()

    with SessionLocal() as session:
        repo = BookRepository(session)
        result = repo.search_by_title(title, model, limit=1)
        return result
