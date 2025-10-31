# Backend - WebSocket Coordination Server

## Overview
WebSocket server that coordinates parallel processing of TTS, visemas, expressions, and animations for the Waifu Avatar System.

Now includes **LibreraAgent**: a ReAct-based conversational agent for library book assistance using LangGraph + Claude Haiku 4.5.

## Architecture

### Core Components

**WebSocketHandler** (`main.py`)
- Receives agent and db_manager implementing their respective protocols
- Routes messages: heartbeat (`"alive"`) or full messages (`{"message": "...", "id": "..."}`)
- Parallel processing via `asyncio.gather()`:
  - `_parallel1`: TTS + Visemas (lip-sync) + DB save
  - `_parallel2`: Facial expressions
  - `_parallel3`: Body animations

### Dependencies

**Microservices:**
- `vox/xtts_client.py`: TTS generation (port 5002)
- `visemas/librosa_client.py`: Lip-sync generation (port 5001)
- `animations/expressions_client.py`: Facial expression analysis
- `animations/animations_client.py`: Body animation selection (OpenAI)

## Protocol Interfaces (Duck Typing)

### AgentProtocol (`agents/ducktyping.py`)
Expected interface for conversational agent implementations.

**Required method:**
- `async def process_message(message: str) -> str`

**Implementation:** `LibreraAgent` (`agents/agent.py`)

### DatabaseManagerProtocol (`db/ducktyping.py`)
Expected interface for conversation persistence.

**Required methods:**
- `async def save_conversation(user_message: str, agent_response: str) -> None`
- `async def retrieve_conversation(hours: int, limit: int) -> List[Dict[str, Any]]`

**Implementation:** `DatabaseManager` (`db/models.py`)

## LibreraAgent - Simplified Workflow

**Model:** Claude Haiku 4.5 (`claude-haiku-4-5`)

**Workflow (Linear, no loops):**
```
start → plan_and_search → [execute_search] → check_results → [execute_recommend?] → format_voice → END
```

**Nodes:**
- `start`: Load last 3 minutes of conversation history from DB
- `plan_and_search`: Analyze query and call appropriate search tool
- `execute_search`: Execute book search tool
- `check_results`: Check if book found, recommend similar if not
- `execute_recommend`: Execute recommendation tool (if needed)
- `format_voice`: Format response for voice interface (1-20 words)

**Tools (3):**
1. `search_book_by_title`: Vector search for specific book by title
2. `search_books_by_criteria`: Search by author, genre, or free-text query (top 3)
3. `recommend_similar_books`: Vector-based recommendations (top 3)

**Voice Interface Constraint:** All responses MUST be extremely short (1-20 words, max 30) since users will HEAR them.

**Vector Search Implementation:**
- Uses `sqlite-vec` (v0.1.2) with `vss0.dylib` and `vector0.dylib`
- Model: `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)
- Two-phase query: Query `vss_books` for rowid, then `books` table for details

## Database Schema

**Table:** `conversations`
- `id`: Integer (PK)
- `message`: String
- `role`: Enum('human', 'agent')
- `timestamp`: DateTime

**Repository:** `ConversationRepository` (`db/repository.py`)
- `save_message(message: str, role: str)`: Save single message
- `get_recent(minutes: int)`: Retrieve messages from last N minutes

## Database Schema (Books)

**Table:** `books`
- `id`: Integer (PK)
- `titulo`: String
- `autor`: String
- `genero`: String
- `sinopsis`: Text
- `isbn`: String (unique)
- `disponibilidad`: Boolean
- `estante`: String (General, Infantil, Novedad, Bestsellers, Ficción)

**Virtual Table:** `vss_books`
- `rowid`: Integer (references books.id)
- `embedding`: Blob (384-dimension vector)

**Repository:** `BookRepository` (`db/repository.py`)
- `search_by_title(query, model, limit)`: Vector search by title
- `search_by_criteria(author, genre, query, model, limit)`: Filtered search
- `recommend_similar(reference, model, limit)`: Similarity recommendations

## Current Status

- ✅ WebSocket infrastructure ready
- ✅ Parallel processing pipeline functional
- ✅ LibreraAgent implemented (simplified workflow with LangGraph)
- ✅ DatabaseManager implemented (SQLite conversation persistence)
- ✅ Book database with vector search implemented
- ✅ All 3 tools using real vector search
- ✅ Spanish prompts optimized for voice interface
- ⚠️ Tool selection needs improvement for general queries

## Known Issues

**Tool Selection:** The `plan_and_search` node may not call tools for general recommendation queries like "me recomiendas algo para mi hijo". The prompt has been updated to be more forceful and provide clearer examples.
