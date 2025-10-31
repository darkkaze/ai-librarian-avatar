"""
Repository for database operations (conversations and books).
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np

from db.models import Conversation, MessageRole, Book


class ConversationRepository:
    """
    Repository for conversation persistence operations.

    Available methods:
    - save_message(message: str, role: str): Save a single message
    - get_recent(minutes: int): Retrieve messages from last N minutes
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def save_message(self, message: str, role: str) -> None:
        """
        Save a single message to the database.

        Args:
            message: Message text
            role: Message role ('human' or 'agent')
        """
        message_role = MessageRole.HUMAN if role == "human" else MessageRole.AGENT
        conversation = Conversation(
            message=message,
            role=message_role
        )
        self.session.add(conversation)
        self.session.commit()

    def get_recent(self, minutes: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation messages.

        Args:
            minutes: Number of minutes to look back (default: 3)

        Returns:
            List of message dictionaries ordered chronologically
            Format: [{"id": 1, "message": "...", "role": "human", "timestamp": "..."}]
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

        messages = self.session.query(Conversation)\
            .filter(Conversation.timestamp >= cutoff_time)\
            .order_by(Conversation.timestamp.asc())\
            .all()

        return [msg.to_dict() for msg in messages]


class BookRepository:
    """
    Repository for book search operations.

    Available methods:
    - search_by_title(query, model, limit): Search books by title similarity
    - search_by_criteria(author, genre, query, model, limit): Search by filters + text
    - recommend_similar(query, model, limit): Get similar book recommendations
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def search_by_title(
        self,
        query: str,
        model,
        limit: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a book by title using exact match first, then vector similarity.

        Args:
            query: Search query (book title)
            model: SentenceTransformer model for embeddings
            limit: Maximum results (default: 3)

        Returns:
            Book dictionary if found, None otherwise
        """
        # First try exact match (case-insensitive)
        print(f"🔍 Buscando título exacto: {query}")
        exact_match = self.session.query(Book)\
            .filter(Book.titulo.ilike(f"%{query}%"))\
            .first()

        if exact_match:
            print(f"✅ Encontrado por búsqueda exacta: {exact_match.titulo}")
            return exact_match.to_dict()

        print(f"❌ No encontrado por búsqueda exacta, usando búsqueda vectorial...")

        # Fall back to vector search
        from db.models import get_db_connection_with_vec

        # Generate embedding for query
        query_embedding = model.encode(query)

        # Use raw connection with vector extensions
        conn = get_db_connection_with_vec()
        cursor = conn.cursor()

        try:
            # Test if vss_distance is available
            try:
                cursor.execute("SELECT vss_version()")
                vss_version = cursor.fetchone()
                print(f"🔍 VSS Version: {vss_version}")
            except Exception as test_e:
                print(f"❌ Error probando vss_version: {test_e}")

            print(f"🔍 Ejecutando query vectorial con embedding de tamaño: {len(query_embedding.tobytes())} bytes")

            # sqlite-vss v0.1.2 syntax: query vss table directly
            query = f"""
                SELECT
                    rowid,
                    distance
                FROM vss_books
                WHERE vss_search(embedding, ?)
                LIMIT {limit}
            """
            cursor.execute(query, (query_embedding.tobytes(),))
            vss_results = cursor.fetchall()

            if not vss_results:
                print("🔍 No se encontraron resultados en búsqueda vectorial")
                return None

            # Get book details from books table
            book_id = vss_results[0][0]
            cursor.execute("""
                SELECT id, titulo, autor, genero, sinopsis, isbn, disponibilidad, estante
                FROM books
                WHERE id = ?
            """, (book_id,))

            print("✅ Query vectorial ejecutado sin errores")

            result = cursor.fetchone()

            print(f"🔍 Resultado del libro: {result}")

            if result:
                return {
                    "titulo": result[1],
                    "autor": result[2],
                    "genero": result[3],
                    "synopsis": result[4],
                    "disponibilidad": bool(result[6]),
                    "estante": result[7]
                }

            return None
        except Exception as e:
            print(f"❌ ERROR en search_by_title: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            conn.close()

    def search_by_criteria(
        self,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        query: Optional[str] = None,
        model=None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search books by author, genre, or text query.

        Args:
            author: Author name filter (optional)
            genre: Genre filter (optional)
            query: Free-text search (optional, uses vector search)
            model: SentenceTransformer model (required if query provided)
            limit: Maximum results (default: 3)

        Returns:
            List of book dictionaries
        """
        if query and model:
            # Vector search
            from db.models import get_db_connection_with_vec

            query_embedding = model.encode(query)

            conn = get_db_connection_with_vec()
            cursor = conn.cursor()

            try:
                # Query vss table directly
                query = f"""
                    SELECT rowid, distance
                    FROM vss_books
                    WHERE vss_search(embedding, ?)
                    LIMIT {limit}
                """
                cursor.execute(query, (query_embedding.tobytes(),))
                vss_results = cursor.fetchall()

                if not vss_results:
                    return []

                # Get book details for all results
                book_ids = [row[0] for row in vss_results]
                placeholders = ','.join('?' * len(book_ids))

                cursor.execute(f"""
                    SELECT id, titulo, autor, genero, sinopsis, isbn, disponibilidad, estante
                    FROM books
                    WHERE id IN ({placeholders})
                """, book_ids)

                books = cursor.fetchall()

                return [
                    {
                        "titulo": row[1],
                        "autor": row[2],
                        "genero": row[3],
                        "synopsis": row[4],
                        "disponibilidad": bool(row[6]),
                        "estante": row[7]
                    }
                    for row in books
                ]
            finally:
                conn.close()

        # SQL filter search with vector fallback for author
        if author and model:
            # Use vector search for author to handle name variations
            # (e.g., "Isabel Allende" vs "ALLENDE, ISABEL")
            from db.models import get_db_connection_with_vec

            author_embedding = model.encode(f"{author} autor")
            conn = get_db_connection_with_vec()
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT rowid, distance
                    FROM vss_books
                    WHERE vss_search(embedding, ?)
                    LIMIT 10
                """, (author_embedding.tobytes(),))

                candidates = cursor.fetchall()
                if candidates:
                    candidate_ids = [row[0] for row in candidates]
                    placeholders = ','.join('?' * len(candidate_ids))

                    # Split author query into words for flexible matching
                    author_words = author.split()
                    author_conditions = ' AND '.join([f"autor LIKE ?" for _ in author_words])
                    author_params = [f"%{word}%" for word in author_words]

                    cursor.execute(f"""
                        SELECT id, titulo, autor, genero, sinopsis, isbn, disponibilidad, estante
                        FROM books
                        WHERE id IN ({placeholders}) AND ({author_conditions})
                        LIMIT {limit}
                    """, (*candidate_ids, *author_params))

                    books = cursor.fetchall()

                    if books:
                        return [
                            {
                                "titulo": row[1],
                                "autor": row[2],
                                "genero": row[3],
                                "synopsis": row[4],
                                "disponibilidad": bool(row[6]),
                                "estante": row[7]
                            }
                            for row in books
                        ]
            finally:
                conn.close()

        # Fallback to SQL-only filter search
        query_obj = self.session.query(Book)

        if author and not model:
            # SQL-only fallback: split author into words
            author_words = author.split()
            for word in author_words:
                query_obj = query_obj.filter(Book.autor.ilike(f"%{word}%"))

        if genre:
            query_obj = query_obj.filter(Book.genero.ilike(f"%{genre}%"))

        books = query_obj.limit(limit).all()
        return [book.to_dict() for book in books]

    def recommend_similar(
        self,
        reference: str,
        model,
        limit: int = 3,
        llm_model=None
    ) -> List[Dict[str, Any]]:
        """
        Recommend books similar to a reference using hybrid search.

        Strategy:
        1. Vector search to find reference book (tolerates voice input variations)
        2. Get genre(s) from that book
        3. If book not found, use LLM to infer genre(s)
        4. Vector search ONLY within those genres
        5. Return top results from same genre

        Args:
            reference: Reference text (book title or description)
            model: SentenceTransformer model for embeddings
            limit: Maximum recommendations (default: 3)
            llm_model: Optional LLM model for genre inference (LangChain model)

        Returns:
            List of similar book dictionaries
        """
        from db.models import get_db_connection_with_vec

        print(f"🔍 Buscando libros similares a: {reference}")

        # Step 1: Find reference book using vector search
        ref_embedding = model.encode(reference)
        conn = get_db_connection_with_vec()
        cursor = conn.cursor()

        try:
            # Find reference book
            cursor.execute("""
                SELECT rowid, distance
                FROM vss_books
                WHERE vss_search(embedding, ?)
                LIMIT 1
            """, (ref_embedding.tobytes(),))

            ref_result = cursor.fetchone()

            ref_genre = None
            ref_book_id = None

            if ref_result:
                ref_book_id = ref_result[0]

                # Step 2: Get genre from reference book
                cursor.execute("""
                    SELECT id, titulo, autor, genero
                    FROM books
                    WHERE id = ?
                """, (ref_book_id,))

                ref_book = cursor.fetchone()
                if ref_book:
                    ref_genre = ref_book[3]
                    print(f"✅ Libro de referencia encontrado en DB: {ref_book[1]} (género: {ref_genre})")

            # Step 2b: If book not found in DB, use LLM to infer genre
            if not ref_genre and llm_model:
                print(f"⚠️ Libro no encontrado en DB, usando LLM para inferir género...")
                from langchain_core.messages import HumanMessage

                prompt = f"""El libro "{reference}" no está en nuestra base de datos.

Basándote en tu conocimiento, ¿de qué género(s) es este libro?

Responde SOLO con los géneros separados por comas, sin explicaciones adicionales.
Formato: Género1, Género2, Género3

Ejemplos:
- Harry Potter: Fantasía juvenil, Aventura, Literatura infantil
- Cien años de soledad: Realismo mágico, Novela histórica, Literatura latinoamericana
- El código Da Vinci: Thriller, Misterio, Ficción histórica

Libro: {reference}
Géneros:"""

                response = llm_model.invoke([HumanMessage(content=prompt)])
                inferred_genres = response.content.strip()
                print(f"🤖 Géneros inferidos por LLM: {inferred_genres}")

                # Use the full inferred string as compound genre
                ref_genre = inferred_genres

            if not ref_genre:
                print("❌ No se pudo determinar el género del libro")
                return []

            print(f"📚 Género(s) a buscar: {ref_genre}")

            # Step 3: Get all books of the same/similar genre(s)
            # Split genres and search with LIKE for partial matching
            genres = [g.strip() for g in ref_genre.split(',')]
            genre_conditions = ' OR '.join(['genero LIKE ?' for _ in genres])
            genre_params = [f"%{g}%" for g in genres]

            cursor.execute(f"""
                SELECT id FROM books WHERE {genre_conditions}
            """, tuple(genre_params))

            genre_book_ids = [row[0] for row in cursor.fetchall()]
            print(f"📚 Libros en género '{ref_genre}': {len(genre_book_ids)}")

            if len(genre_book_ids) < 2 and ref_book_id:
                print("⚠️ Muy pocos libros en este género, usando búsqueda general")
                # Fallback to general search
                cursor.execute(f"""
                    SELECT rowid, distance
                    FROM vss_books
                    WHERE vss_search(embedding, ?)
                    LIMIT {limit}
                """, (ref_embedding.tobytes(),))
                vss_results = cursor.fetchall()
                book_ids = [row[0] for row in vss_results if row[0] != ref_book_id]
            elif len(genre_book_ids) < 1:
                print("⚠️ No hay libros en estos géneros")
                return []
            else:
                # Step 4: Vector search and filter by genre
                # SQLite-vss doesn't support WHERE rowid IN with vss_search well
                # So we search broadly and filter by genre afterward
                cursor.execute(f"""
                    SELECT rowid, distance
                    FROM vss_books
                    WHERE vss_search(embedding, ?)
                    LIMIT 50
                """, (ref_embedding.tobytes(),))

                vss_results = cursor.fetchall()

                # Filter to only books in the target genre
                genre_set = set(genre_book_ids)
                filtered = [row for row in vss_results if row[0] in genre_set]

                # Exclude reference book itself (if it exists in DB)
                if ref_book_id:
                    book_ids = [row[0] for row in filtered if row[0] != ref_book_id][:limit]
                else:
                    book_ids = [row[0] for row in filtered][:limit]

            if not book_ids:
                return []

            # Get book details
            placeholders = ','.join('?' * len(book_ids))
            cursor.execute(f"""
                SELECT id, titulo, autor, genero, sinopsis, isbn, disponibilidad, estante
                FROM books
                WHERE id IN ({placeholders})
            """, book_ids)

            books = cursor.fetchall()

            results = [
                {
                    "titulo": row[1],
                    "autor": row[2],
                    "genero": row[3],
                    "synopsis": row[4],
                    "disponibilidad": bool(row[6]),
                    "estante": row[7]
                }
                for row in books
            ]

            print(f"✅ {len(results)} recomendaciones encontradas del mismo género")
            return results

        finally:
            conn.close()

    def recommend_by_author(
        self,
        author_query: str,
        model,
        limit: int = 3,
        llm_model=None
    ) -> List[Dict[str, Any]]:
        """
        Recommend books by finding similar authors based on genre.

        Strategy:
        1. Vector search to find a book by the author (tolerates voice input)
        2. Get genre(s) from that author's books
        3. If author not found, use LLM to infer genre(s)
        4. Vector search for books in same genre(s) by OTHER authors
        5. Return recommendations from different authors

        Args:
            author_query: Author name (may have voice input variations)
            model: SentenceTransformer model for embeddings
            limit: Maximum recommendations (default: 3)
            llm_model: Optional LLM model for genre inference (LangChain model)

        Returns:
            List of book dictionaries from similar authors
        """
        from db.models import get_db_connection_with_vec

        print(f"🔍 Buscando autores similares a: {author_query}")

        # Step 1: Find a book by this author using vector search
        query_embedding = model.encode(f"{author_query} autor")
        conn = get_db_connection_with_vec()
        cursor = conn.cursor()

        try:
            # Vector search to find author's book
            cursor.execute("""
                SELECT rowid, distance
                FROM vss_books
                WHERE vss_search(embedding, ?)
                LIMIT 5
            """, (query_embedding.tobytes(),))

            candidates = cursor.fetchall()

            genres = []
            actual_author = None

            if candidates:
                # Step 2: Get author and genres from their books
                candidate_ids = [row[0] for row in candidates]
                placeholders = ','.join('?' * len(candidate_ids))

                cursor.execute(f"""
                    SELECT DISTINCT autor, genero
                    FROM books
                    WHERE id IN ({placeholders}) AND autor LIKE ?
                """, (*candidate_ids, f"%{author_query.split()[0]}%"))

                author_genres = cursor.fetchall()

                if author_genres:
                    actual_author = author_genres[0][0]
                    genres = list(set([row[1] for row in author_genres]))
                    print(f"✅ Autor encontrado en DB: {actual_author}")
                    print(f"📚 Géneros del autor: {', '.join(genres)}")

            # Step 2b: If author not found in DB, use LLM to infer genres
            if not genres and llm_model:
                print(f"⚠️ Autor no encontrado en DB, usando LLM para inferir género...")
                from langchain_core.messages import HumanMessage

                prompt = f"""El autor "{author_query}" no está en nuestra base de datos.

Basándote en tu conocimiento, ¿qué géneros literarios escribe este autor?

Responde SOLO con los géneros separados por comas, sin explicaciones adicionales.
Formato: Género1, Género2, Género3

Ejemplos:
- Isabel Allende: Realismo mágico, Novela histórica, Literatura latinoamericana
- Stephen King: Terror psicológico, Horror sobrenatural, Thriller
- J.K. Rowling: Fantasía juvenil, Aventura, Literatura infantil

Autor: {author_query}
Géneros:"""

                response = llm_model.invoke([HumanMessage(content=prompt)])
                inferred_genres = response.content.strip()
                print(f"🤖 Géneros inferidos por LLM: {inferred_genres}")

                # Split genres and clean
                genres = [g.strip() for g in inferred_genres.split(',')]

            if not genres:
                print("❌ No se pudo determinar el género del autor")
                return []

            # Step 3: Find books in same genres
            # Use LIKE for partial matching since genres might be compound
            genre_conditions = ' OR '.join(['genero LIKE ?' for _ in genres])
            genre_params = [f"%{g}%" for g in genres]

            # Exclude actual_author only if we found them in DB
            if actual_author:
                query = f"""
                    SELECT id FROM books
                    WHERE ({genre_conditions})
                    AND autor != ?
                """
                cursor.execute(query, (*genre_params, actual_author))
            else:
                query = f"""
                    SELECT id FROM books
                    WHERE {genre_conditions}
                """
                cursor.execute(query, tuple(genre_params))

            genre_book_ids = [row[0] for row in cursor.fetchall()]
            print(f"📖 Libros de otros autores en estos géneros: {len(genre_book_ids)}")

            if len(genre_book_ids) < 1:
                print("⚠️ No hay otros autores en estos géneros")
                return []

            # Step 4: Vector search and filter by genre
            # SQLite-vss doesn't support WHERE rowid IN with vss_search well
            cursor.execute(f"""
                SELECT rowid, distance
                FROM vss_books
                WHERE vss_search(embedding, ?)
                LIMIT 50
            """, (query_embedding.tobytes(),))

            vss_results = cursor.fetchall()

            # Filter to only books in target genres
            genre_set = set(genre_book_ids)
            filtered = [row for row in vss_results if row[0] in genre_set]
            book_ids = [row[0] for row in filtered][:limit]

            if not book_ids:
                return []

            # Get book details
            placeholders = ','.join('?' * len(book_ids))
            cursor.execute(f"""
                SELECT id, titulo, autor, genero, sinopsis, isbn, disponibilidad, estante
                FROM books
                WHERE id IN ({placeholders})
            """, book_ids)

            books = cursor.fetchall()

            results = [
                {
                    "titulo": row[1],
                    "autor": row[2],
                    "genero": row[3],
                    "synopsis": row[4],
                    "disponibilidad": bool(row[6]),
                    "estante": row[7]
                }
                for row in books
            ]

            print(f"✅ {len(results)} recomendaciones de autores similares")
            return results

        finally:
            conn.close()

