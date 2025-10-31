# Backend - WebSocket Coordination Server

Main WebSocket server that coordinates all microservices and handles conversational AI agent for the Waifu Avatar System.

## Description

This service provides:
- WebSocket server for real-time communication with frontend
- **LibreraAgent**: ReAct-based conversational agent using LangGraph + Claude Haiku 4.5
- Parallel processing coordination for TTS, visemas, expressions, and animations
- SQLite database with vector search for book recommendations
- Conversation history persistence

## Installation

**Requirements:** Python 3.11+

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

This service requires the following API keys:

| Variable | Purpose | Used For |
|----------|---------|----------|
| `ANTHROPIC_API_KEY` | **Required** | Claude Haiku 4.5 conversational agent + tool calls |
| `OPENAI_API_KEY` | **Required** | GPT-4o-mini for intelligent animation selection |

Set these environment variables before running:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

**Where to get API keys:**
- Anthropic Claude: [console.anthropic.com](https://console.anthropic.com)
- OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## SQLite Vector Extensions

This project uses `sqlite-vec` for vector similarity search. The required extensions are **NOT included** in the repository (platform-specific binaries).

**Install extensions:**

```bash
pip install sqlite-vec
```

The extensions (`vector0.dylib` and `vss0.dylib` on macOS, `.so` on Linux, `.dll` on Windows) will be downloaded automatically when you install the package. Copy them to `backend/db/` directory:

```bash
# macOS/Linux example
cp $(python -c "import sqlite_vec; print(sqlite_vec.__path__[0])")/vec0.* backend/db/
```

Or the code will attempt to load them from the sqlite-vec package location.

## Database Setup

Import books data (optional):

```bash
python import_books.py
```

## Execution

**Prerequisites:** Make sure the following services are running first:
1. TTS Service (port 5002)
2. Visemas Service (port 5001)
3. Animation Service (port 5003)

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the WebSocket server
python main.py
```

The service will start on **port 8765**.

## Features

- **LibreraAgent**: Conversational AI for library book assistance
- **Vector Search**: Book recommendations using `sqlite-vec`
- **Tools**: Book search by title, author, genre, and similarity recommendations
- **Voice-Optimized**: Responses limited to 1-20 words for natural speech
- **Conversation Memory**: Retrieves last 3 minutes of chat history

## Architecture

- WebSocket handler routes messages to agent
- Parallel processing pipeline for multimedia responses
- Duck typing protocols for agent and database interfaces
