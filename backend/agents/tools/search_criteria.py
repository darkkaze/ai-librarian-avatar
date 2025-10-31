"""
Search books by criteria tool.
"""
from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
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
def search_books_by_criteria(
    author: Optional[str] = None,
    genre: Optional[str] = None,
    query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search books by author, genre, or free-text query.

    Returns top 3 matching books.

    Args:
        author: Author name (optional)
        genre: Book genre (optional)
        query: Free-text search query (optional, uses vector search on synopsis)

    Returns:
        List of up to 3 books matching criteria
        Format: [{"titulo": str, "autor": str, "genero": str, "synopsis": str, "disponibilidad": bool, "estante": str}]
    """
    # Always use model for author search (to handle name variations)
    model = get_model() if (query or author) else None

    with SessionLocal() as session:
        repo = BookRepository(session)
        results = repo.search_by_criteria(
            author=author,
            genre=genre,
            query=query,
            model=model,
            limit=3
        )
        return results
