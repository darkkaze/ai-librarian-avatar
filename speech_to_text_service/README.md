# Speech-to-Text Service

Text-to-Speech (TTS) service supporting multiple synthesis engines: Gemini TTS, Piper TTS, and XTTS-v2.

## Description

This service provides:
- **Gemini TTS**: Google's Gemini 2.5 Pro Preview TTS (Mexican Spanish accent)
- **Piper TTS**: Lightweight neural TTS
- **XTTS-v2**: Coqui TTS for high-quality voice synthesis
- Flask REST API for audio generation
- WAV format audio output

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

This service requires the following API key:

| Variable | Purpose | Used For |
|----------|---------|----------|
| `GEMINI_API_KEY` | **Required** | Gemini 2.5 Pro Preview TTS for speech synthesis |

Set this environment variable before running:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

**Where to get API key:**
- Google AI Studio: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

**Note:** Piper TTS and XTTS-v2 engines don't require API keys (run locally).

## Execution

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the service
python app.py
```

The service will start on **port 5002**.

## API Endpoints

- `POST /generate` - Generate speech from text
  - Request body: `{"text": "Your text here"}`
  - Returns: JSON with audio file URL

## TTS Engines

### Gemini TTS
- Model: `gemini-2.5-pro-preview-tts`
- Voice: Despina (Mexican Spanish accent)
- Style: Neutral voice, low emotion, informative tone

### Piper TTS
- Voice model: `es_MX-claude-high.onnx`
- Fast, lightweight synthesis

### XTTS-v2
- High-quality neural TTS
- Configurable voice characteristics

## Voice Characteristics

Default configuration optimized for:
- Mexican Spanish accent
- Neutral voice tone
- Professional and informative delivery
- Low emotional expression
