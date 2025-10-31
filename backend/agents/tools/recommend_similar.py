"""
Recommend similar books tool.
"""
from langchain_core.tools import tool
from typing import List, Dict, Any
from db.models import SessionLocal
from db.repository import BookRepository
from sentence_transformers import SentenceTransformer
from langchain_anthropic import ChatAnthropic
import settings

# Load models once (singleton pattern)
_model = None
_llm_model = None


def get_model():
    """Get or create sentence transformer model."""
    global _model
    if _model is None:
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model


def get_llm_model():
    """Get or initialize LLM model for genre inference."""
    global _llm_model
    if _llm_model is None:
        _llm_model = ChatAnthropic(
            model="claude-haiku-4-5",
            api_key=settings.ANTHROPIC_API_KEY
        )
    return _llm_model


@tool
def recommend_similar_books(reference: str) -> List[Dict[str, Any]]:
    """
    Recommend books similar to a given title or description.

    Uses hybrid search:
    1. Vector similarity search to find reference book
    2. Gets genre from that book
    3. If book not found, uses LLM to infer genre based on world knowledge
    4. Searches for similar books ONLY within the same genre(s)

    Returns top 3 most similar books.

    Args:
        reference: Book title or description to base recommendations on

    Returns:
        List of up to 3 similar books
        Format: [{"titulo": str, "autor": str, "genero": str, "synopsis": str, "disponibilidad": bool, "estante": str}]
    """
    model = get_model()
    llm_model = get_llm_model()

    with SessionLocal() as session:
        repo = BookRepository(session)
        results = repo.recommend_similar(reference, model, limit=3, llm_model=llm_model)
        return results
