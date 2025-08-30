# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Waifu Avatar System** - an interactive 3D avatar that responds to voice input with synchronized speech, expressions, and animations. The system consists of a Vue.js frontend and multiple Python microservices working together.

### Core Architecture

The system follows a **microservices architecture** with WebSocket coordination:

- **Frontend**: Vue 3 + TypeScript + Three.js for 3D VRM avatar rendering
- **Backend**: Python WebSocket server coordinating all services
- **TTS Service**: XTTS-v2 voice synthesis (port 5002)
- **Visemas Service**: Librosa-based lip-sync generation (port 5001) 
- **Animation Service**: VRMA animation file server (port 5003)

### Communication Flow

1. **User speaks** → Frontend captures voice → WebSocket sends to backend
2. **Backend processes** with LangChain + Claude Haiku agent
3. **Parallel processing**: TTS, expressions, and animations generated simultaneously
4. **Frontend receives** coordinated responses and renders avatar

## Development Commands

### Frontend (Vue.js)
```bash
cd vue-project/
npm install
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint + oxlint
npm run type-check   # Vue TypeScript checking
```

### Backend Services
```bash
# Main backend (WebSocket coordinator)
cd backend/
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py       # Starts on port 8765

# TTS Service 
cd speech_to_text_service/
python app.py        # Starts on port 5002

# Visemas Service
cd visemas_service/
python app.py        # Starts on port 5001

# Animation Service
cd animation_service/
python app.py        # Starts on port 5003
```

### Service Startup Order
1. TTS Service (5002)
2. Visemas Service (5001) 
3. Animation Service (5003)
4. Main Backend (8765)
5. Frontend dev server

## Key Technical Concepts

### WebSocket Protocol

The system uses a **dual response pattern**:

1. **Fast Output** (no `message_id`): Immediate responses like "let me check that"
2. **Complete Response** (with `message_id`): Full coordinated response requiring 3 parts:
   - Audio + Visemas
   - Expressions 
   - Animations

### Animation System

**Critical Implementation Detail**: The frontend uses a **clean idle rotation system**:
- Idle animations (`idle`, `idle2`) loop continuously with natural duration-based transitions
- Specific animations (from webhooks) play **once** and automatically return to idle
- Uses `LoopRepeat` for idles, `LoopOnce` for specific animations

### Voice Feedback Prevention

**Essential Feature**: The system automatically pauses voice capture when the avatar speaks to prevent audio feedback loops:
- Voice capture stops when audio playback begins
- Auto-resumes 500ms after audio ends
- Manual interrupt available via UI button

### VRM Avatar Standards

- Uses **@pixiv/three-vrm** and **@pixiv/three-vrm-animation** libraries
- Expressions follow VRoid naming: `aa`, `ih`, `ou`, `ee`, `oh`, `neutral`
- Animations use VRMA format with crossfading support
- Bone manipulation follows strict hierarchy rules (see `bones-rules.md`)

## File Structure Highlights

```
waifu/
├── vue-project/               # Frontend
│   ├── src/composables/       # Vue composables for core logic
│   │   ├── useAvatarRenderer.ts    # 3D rendering & animation
│   │   ├── useVoiceCapture.ts      # Speech recognition
│   │   ├── useWebSocket.ts         # WebSocket communication
│   │   ├── useAudioPlayback.ts     # Audio playback
│   │   └── useResponseCoordinator.ts # Response synchronization
│   └── src/types/waifu-protocol.ts # Shared type definitions
├── backend/                   # Main WebSocket server
│   ├── agents/agent.py        # LangChain conversational agent
│   └── main.py               # WebSocket handler
├── animation_service/         # VRMA animation server
│   ├── animations/           # .vrma files
│   ├── jsons/               # Animation sequence definitions
│   └── app.py               # Flask server
└── docs/                    # Architecture documentation
```

## Animation JSON Format

Animations are defined in JSON files with this structure:
```json
{
  "sequence": "hello",
  "description": "Friendly greeting animation",
  "vrma_file": "animations/hello.vrma",
  "breathing": false,
  "delay": 0.0,
  "temporary": true
}
```

## Debugging Notes

- **Voice timeout**: Currently set to 1500ms (1.5 seconds) in `HomeView.vue`
- **Animation issues**: Check console for Three.js clip loading and crossfade timing
- **WebSocket problems**: Monitor connection state and message coordination
- **Feedback loops**: Verify voice capture pauses during avatar speech

## Integration Points

- **Backend ↔ TTS**: HTTP POST to `/generate` endpoint
- **Backend ↔ Visemas**: HTTP POST with audio URL and text  
- **Backend ↔ Animations**: HTTP GET to `/sequence/<name>`
- **Frontend ↔ Backend**: WebSocket with dual response protocol
- **Frontend ↔ Animation Service**: Direct HTTP for VRMA file serving

This architecture prioritizes real-time interaction and natural conversation flow while maintaining clean separation of concerns across services.