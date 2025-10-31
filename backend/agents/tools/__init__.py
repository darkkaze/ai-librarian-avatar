"""
Librera Agent Tools.

Available tools:
- search_book_by_title: Search for a specific book by title
- search_books_by_criteria: Search books by author, genre, or query
- recommend_similar_books: Get recommendations similar to a reference book
- recommend_by_author: Get recommendations from similar authors (same genre)
"""
from agents.tools.search_book import search_book_by_title
from agents.tools.search_criteria import search_books_by_criteria
from agents.tools.recommend_similar import recommend_similar_books
from agents.tools.recommend_author import recommend_by_author

ALL_TOOLS = [
    search_book_by_title,
    search_books_by_criteria,
    recommend_similar_books,
    recommend_by_author
]

__all__ = [
    "search_book_by_title",
    "search_books_by_criteria",
    "recommend_similar_books",
    "recommend_by_author",
    "ALL_TOOLS"
]
