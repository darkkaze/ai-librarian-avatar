# Vue Frontend - Waifu Avatar Interface

Interactive 3D VRM avatar interface built with Vue 3, TypeScript, and Three.js.

## Description

This is the frontend application providing:
- 3D VRM avatar rendering using Three.js and @pixiv/three-vrm
- Real-time lip-sync animation with visemes
- Facial expressions synchronized with dialogue
- Body animations with smooth crossfading
- Voice capture and speech recognition
- WebSocket communication with backend
- Audio playback with automatic voice capture pause

## Environment Variables

This frontend application does **not require** any API keys or environment variables.

All AI processing happens in the backend services.

## Installation

**Requirements:** Node.js 20.19.0+ or 22.12.0+

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start development server with hot-reload
npm run dev
```

The application will be available at `http://localhost:5173` (or the port shown in terminal).

## Production Build

```bash
# Type-check and build for production
npm run build

# Preview production build locally
npm run preview
```

## Code Quality

```bash
# Run linters (ESLint + oxlint)
npm run lint

# Type-check with Vue TSC
npm run type-check

# Format code with Prettier
npm run format
```

## Key Features

### 3D Avatar System
- VRM model loading and rendering
- Expression morphing (aa, ih, ou, ee, oh, neutral)
- VRMA animation playback with looping control
- Idle rotation system with natural transitions

### Voice Interaction
- Speech recognition with configurable timeout
- Automatic voice capture pause during avatar speech
- Manual interrupt capability
- 1.5-second silence detection

### Animation System
- **Idle animations**: Loop continuously (`idle`, `idle2`)
- **Specific animations**: Play once and return to idle
- Smooth crossfading between animations
- Duration-based transition timing

### WebSocket Protocol
- Dual response pattern (fast output + complete response)
- Message coordination requiring 3 parts: Audio+Visemas, Expressions, Animations
- Heartbeat support
- Automatic feedback loop prevention

## Architecture

The application uses Vue 3 Composition API with specialized composables:
- `useAvatarRenderer.ts` - 3D rendering & animation
- `useVoiceCapture.ts` - Speech recognition
- `useWebSocket.ts` - Backend communication
- `useAudioPlayback.ts` - Audio playback
- `useResponseCoordinator.ts` - Response synchronization

## Configuration

Backend WebSocket connection is configured to:
- `ws://localhost:8765` (default)

Adjust in `src/composables/useWebSocket.ts` if needed.

## Tech Stack

- **Vue 3.5** with Composition API
- **TypeScript 5.8**
- **Vuetify 3.9** for UI components
- **Three.js 0.179** for 3D rendering
- **@pixiv/three-vrm** for VRM avatar support
- **Vite 7** for build tooling
