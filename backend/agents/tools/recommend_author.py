"""
Tool for recommending books by finding similar authors based on genre.
"""
from typing import List, Dict, Any
from langchain.tools import tool
from sentence_transformers import SentenceTransformer
from langchain_anthropic import ChatAnthropic
import settings

from db.models import SessionLocal
from db.repository import BookRepository

# Global model instances (lazy loaded)
_model = None
_llm_model = None


def get_model():
    """Get or initialize sentence transformer model."""
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
def recommend_by_author(author_name: str) -> List[Dict[str, Any]]:
    """
    Recommend books by finding similar authors based on genre.

    This tool:
    1. Finds books by the specified author (using vector search to tolerate voice input)
    2. Gets the genre(s) of that author's books
    3. If author not found, uses LLM to infer genre based on world knowledge
    4. Searches for books in the same genre(s) by OTHER authors
    5. Returns top 3 recommendations from similar authors

    Use this when user asks for:
    - "algo similar a [autor]"
    - "autores como [autor]"
    - "libros parecidos a los de [autor]"

    Args:
        author_name: Name of the author (tolerates voice input variations)

    Returns:
        List of up to 3 book dictionaries from similar authors
    """
    model = get_model()
    llm_model = get_llm_model()

    with SessionLocal() as session:
        repo = BookRepository(session)
        results = repo.recommend_by_author(author_name, model, limit=3, llm_model=llm_model)
        return results
