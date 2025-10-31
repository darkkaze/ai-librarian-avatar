"""
Database models for conversation persistence and book catalog.
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Boolean, Text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum
import os

Base = declarative_base()


class MessageRole(enum.Enum):
    """Message role enum."""
    HUMAN = "human"
    AGENT = "agent"


class Conversation(Base):
    """
    Conversation message model.

    Each row represents a single message in the conversation history.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "message": self.message,
            "role": self.role.value,
            "timestamp": self.timestamp.isoformat()
        }


class Book(Base):
    """
    Book catalog model.

    Stores book information with vector embeddings for semantic search.
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    genero = Column(String, nullable=False)
    sinopsis = Column(Text, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    disponibilidad = Column(Boolean, default=True, nullable=False)
    estante = Column(String, nullable=False)  # Sección: General, Infantil, Novedad, Bestsellers, Ficción

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "synopsis": self.sinopsis,
            "disponibilidad": self.disponibilidad,
            "estante": self.estante
        }


# Database setup
DATABASE_URL = "sqlite:///db/conversation.db"
engine = create_engine(DATABASE_URL, echo=False)


def load_sqlite_vec(dbapi_conn, connection_record):
    """Load sqlite-vec extensions."""
    try:
        dbapi_conn.enable_load_extension(True)
        db_dir = os.path.dirname(os.path.abspath(__file__))

        vector_path = os.path.join(db_dir, "vector0")
        vss_path = os.path.join(db_dir, "vss0")

        print(f"Loading vector0 from: {vector_path}")
        dbapi_conn.load_extension(vector_path)

        print(f"Loading vss0 from: {vss_path}")
        dbapi_conn.load_extension(vss_path)

        dbapi_conn.enable_load_extension(False)
        print("✅ sqlite-vec extensions loaded successfully")
    except Exception as e:
        print(f"❌ Error loading sqlite-vec extensions: {e}")
        raise


# Register event listener to load extensions on connect
event.listen(engine, "connect", load_sqlite_vec)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Get database session context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_connection_with_vec():
    """
    Get raw SQLite connection with vector extensions loaded.

    Use this for vector search operations instead of SessionLocal.
    """
    import sqlite3

    db_path = "db/conversation.db"
    print(f"📁 Conectando a DB: {db_path}")
    conn = sqlite3.connect(db_path)

    # Enable and load extensions
    conn.enable_load_extension(True)
    db_dir = os.path.dirname(os.path.abspath(__file__))

    vector_path = os.path.join(db_dir, "vector0")
    vss_path = os.path.join(db_dir, "vss0")

    print(f"📦 Cargando vector0 desde: {vector_path}")
    print(f"📦 Cargando vss0 desde: {vss_path}")

    try:
        conn.load_extension(vector_path)
        print("✅ vector0 cargado")

        conn.load_extension(vss_path)
        print("✅ vss0 cargado")
    except Exception as e:
        print(f"❌ ERROR cargando extensiones: {e}")
        print(f"❌ Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.enable_load_extension(False)

    print("✅ Conexión lista con extensiones vectoriales")
    return conn


class DatabaseManager:
    """
    Database manager implementing DatabaseManagerProtocol.

    Handles conversation persistence using ConversationRepository.
    """

    async def save_conversation(self, user_message: str, agent_response: str) -> None:
        """
        Save a conversation exchange to persistent storage.

        Saves two separate messages: one for user (human role) and one for agent.

        Args:
            user_message: User's message
            agent_response: Agent's response
        """
        from db.repository import ConversationRepository

        with SessionLocal() as session:
            repo = ConversationRepository(session)
            repo.save_message(user_message, "human")
            repo.save_message(agent_response, "agent")

    async def retrieve_conversation(self, hours: int = 12, limit: int = 10):
        """
        Retrieve recent conversation history.

        Args:
            hours: Number of hours to look back
            limit: Maximum number of messages to retrieve

        Returns:
            List of conversation messages (chronologically ordered)
        """
        from db.repository import ConversationRepository

        with SessionLocal() as session:
            repo = ConversationRepository(session)
            return repo.get_recent(minutes=hours * 60)[:limit]
