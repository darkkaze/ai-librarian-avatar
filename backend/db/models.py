import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
import os


class MessageRole(Enum):
    USER = "user"
    AGENT = "agent"


class DatabaseManager:
    def __init__(self, db_path: str = "db/conversation.db"):
        """
        Inicializa el manager de la base de datos.
        
        Args:
            db_path: Ruta al archivo de la base de datos SQLite
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Asegura que el directorio de la base de datos existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    text TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'agent')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índice para optimizar consultas por timestamp
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_mensajes_timestamp 
                ON mensajes(timestamp)
            """)
            
            # Preparación para SQLiteVec futuro
            # Esta estructura permitirá agregar columnas de vectores más adelante
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mensaje_metadata (
                    mensaje_id INTEGER PRIMARY KEY,
                    vector_embedding BLOB,
                    vector_version TEXT,
                    FOREIGN KEY (mensaje_id) REFERENCES mensajes (id)
                )
            """)
            
            conn.commit()
    
    def save_message(self, text: str, role: MessageRole) -> int:
        """
        Guarda un mensaje en la base de datos.
        
        Args:
            text: Contenido del mensaje
            role: Rol del remitente (USER o AGENT)
            
        Returns:
            ID del mensaje guardado
        """
        # Asegurarse de que text es un string
        if isinstance(text, list):
            text = " ".join(str(t) for t in text)
        elif not isinstance(text, str):
            text = str(text)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO mensajes (text, role) VALUES (?, ?)",
                (text, role.value)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_recent_conversation(self, hours: int = 12, limit: int = 10) -> List[Dict]:
        """
        Recupera los mensajes más recientes de las últimas N horas.
        
        Args:
            hours: Número de horas hacia atrás para buscar
            limit: Máximo número de mensajes a recuperar
            
        Returns:
            Lista de mensajes ordenados cronológicamente (más antiguos primero)
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, timestamp, text, role
                FROM mensajes 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff_time.isoformat(), limit))
            
            messages = cursor.fetchall()
            
            # Convertir a lista de diccionarios y revertir para orden cronológico
            return [dict(msg) for msg in reversed(messages)]
    
    async def retrieve_conversation(self, hours: int = 12, limit: int = 10) -> List[Dict]:
        """
        Recupera los mensajes más recientes de las últimas N horas.
        
        Args:
            hours: Número de horas hacia atrás para buscar
            limit: Máximo número de mensajes a recuperar
            
        Returns:
            Lista de mensajes ordenados cronológicamente (más antiguos primero)
        """
        return self.get_recent_conversation(hours, limit)
    
    async def save_conversation(self, user_message: str, agent_response: str):
        """
        Guarda tanto el mensaje del usuario como la respuesta del agente.
        
        Args:
            user_message: Mensaje del usuario
            agent_response: Respuesta del agente
        """
        print("🎭 Saving conversation to DB...")
        self.save_message(user_message, MessageRole.USER)
        print("🎭 User message saved.")
        self.save_message(agent_response, MessageRole.AGENT)
    
    def cleanup_old_messages(self, days: int = 30):
        """
        Elimina mensajes más antiguos que N días.
        
        Args:
            days: Número de días de retención
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM mensajes WHERE timestamp < ?",
                (cutoff_time.isoformat(),)
            )
            deleted_count = cursor.rowcount
            conn.commit()
            
        return deleted_count