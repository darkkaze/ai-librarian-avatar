# Waifu Librera - Interactive 3D Avatar with Conversational AI

Personal study project exploring the integration of a LangGraph/LangChain conversational agent with a 3D VRoid avatar.

## Project Overview

This project connects a ReAct-based AI agent (powered by Claude Haiku 4.5) with an interactive 3D VRM avatar that can:
- Listen to voice input
- Process natural language queries about a book library
- Respond with synchronized speech, lip-sync, facial expressions, and body animations

**Why VRoid?** VRoid/VRM was chosen for its ease of use - you can quickly create or find existing 3D avatars, and they come with built-in viseme (lip-sync) and facial expression support, making avatar animation straightforward.

## Demo

🎥 **[Watch Video Demo](https://youtube.com/shorts/4K3GIW9ZUZc?feature=share)**

[![AI Librarian Avatar Demo](https://img.youtube.com/vi/4K3GIW9ZUZc/maxresdefault.jpg)](https://youtube.com/shorts/4K3GIW9ZUZc?feature=share)

## Key Features

### Vector Search for Book Recommendations
- Uses **SQLite with vector extensions** (`sqlite-vec`) for book inventory context
- Implements vector-based book recommendations using semantic similarity
- Model: `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)

**Note:** A sales-based recommendation algorithm would be more effective in production, but this project uses vector similarity as a proof of concept due to lack of sales data.

### Conversational AI Agent
- Built with **LangGraph** and **LangChain**
- Powered by **Claude Haiku 4.5**
- Three specialized tools: search by title, search by criteria, and similarity recommendations
- Maintains conversation history (last 3 minutes)

### Real-time Multimedia Coordination
- Parallel processing of TTS, visemes, expressions, and animations
- WebSocket-based communication
- Voice feedback prevention (pauses voice capture during avatar speech)

## Architecture

The project follows a **microservices architecture**:

```
┌─────────────────┐
│   Vue Frontend  │  (3D Avatar + Voice Interface)
│   Port: 5173    │
└────────┬────────┘
         │ WebSocket
┌────────▼────────┐
│  Backend WS     │  (Agent Coordinator)
│  Port: 8765     │
└─┬───┬───┬───┬───┘
  │   │   │   │
  │   │   │   └──► Animation Service (Port 5003)
  │   │   └──────► Visemas Service (Port 5001)
  │   └──────────► TTS Service (Port 5002)
  └──────────────► SQLite Vector DB
```

## Installation

Each service has its own README with detailed installation instructions:

- **Frontend**: [`vue-project/README.md`](vue-project/README.md) - Node.js 20.19.0+
- **Backend**: [`backend/README.md`](backend/README.md) - Python 3.11+
- **TTS Service**: [`speech_to_text_service/README.md`](speech_to_text_service/README.md) - Python 3.11+
- **Visemas Service**: [`visemas_service/README.md`](visemas_service/README.md) - Python 3.11+
- **Animation Service**: [`animation_service/README.md`](animation_service/README.md) - Python 3.11+

## Environment Variables

The project requires the following API keys:

| Variable | Required By | Purpose |
|----------|------------|---------|
| `ANTHROPIC_API_KEY` | Backend | Claude Haiku 4.5 for conversational agent |
| `OPENAI_API_KEY` | Backend | GPT-4o-mini for animation selection |
| `GEMINI_API_KEY` | TTS Service | Gemini 2.5 Pro TTS for speech synthesis |

Create these environment variables before starting the services:

```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
```

Or create a `.env` file in each service directory (see `.env.example` if available).

## Quick Start

### 1. Set Environment Variables

See the **Environment Variables** section above.

### 2. Start Services (in order)

```bash
# Terminal 1 - TTS Service
cd speech_to_text_service
source venv/bin/activate
python app.py

# Terminal 2 - Visemas Service
cd visemas_service
source venv/bin/activate
python app.py

# Terminal 3 - Animation Service
cd animation_service
source venv/bin/activate
python app.py

# Terminal 4 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 5 - Frontend
cd vue-project
npm run dev
```

Open `http://localhost:5173` in your browser and interact with the avatar!

## Tech Stack

- **Frontend**: Vue 3, TypeScript, Three.js, @pixiv/three-vrm, Vuetify
- **Backend**: Python, WebSockets, LangGraph, LangChain
- **AI Models**: Claude Haiku 4.5, GPT-4o-mini, Gemini 2.5 Pro TTS
- **Database**: SQLite with vector extensions (sqlite-vec)
- **TTS Engines**: Gemini TTS, Piper TTS, XTTS-v2

## Apology for Architecture

Yes, I went with a microservices architecture thinking it would be easier to debug (and it was!), but I got lazy and didn't implement a one-click execution script. You'll need to manually start all 5 services in separate terminals. My apologies for the inconvenience! 😅

Feel free to create a `docker-compose.yml` or startup script if you want to improve this.

## License

This project is licensed under the **Beerware License** (Revision 42).

You can do whatever you want with this code. If we meet some day, and you think this stuff is worth it, you can buy me a beer (or a coffee) in return.

☕ Support via Ko-fi: [ko-fi.com/darkkaze](https://ko-fi.com/darkkaze)

See [LICENSE](LICENSE) for the full license text.
