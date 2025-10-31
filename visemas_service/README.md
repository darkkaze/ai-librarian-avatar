# Visemas Service

Lip-sync generation service using Librosa for phoneme extraction and viseme mapping.

## Description

This service provides:
- Phoneme extraction from audio files using Librosa
- Phoneme-to-viseme mapping for VRM avatar lip-sync
- Timestamped viseme sequences for precise mouth animation
- REST API for viseme generation from audio and text

## Environment Variables

This service does **not require** any API keys or environment variables.

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

## Execution

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the service
python app.py
```

The service will start on **port 5001**.

## API Endpoints

- `POST /generate` - Generate viseme sequence
  - Request body: `{"audio_url": "http://...", "text": "Spoken text"}`
  - Returns: JSON with timestamped viseme array

## Viseme Mapping

Maps Spanish phonemes to VRM expressions:
- `aa` - Wide open mouth (a)
- `ee` - Smile, semi-open (e)
- `ih` - Smile, closed mouth (i)
- `oh` - Round mouth (o)
- `ou` - Very round, pursed lips (u)
- `neutral` - Rest position

## How It Works

1. Receives audio URL and transcript text
2. Downloads audio file
3. Extracts phonemes using Librosa
4. Maps phonemes to VRM visemes
5. Generates timestamped sequence with duration
6. Returns JSON for frontend animation

## Output Format

```json
{
  "visemas": [
    {"visema": "aa", "timestamp": 0.0},
    {"visema": "neutral", "timestamp": 0.15}
  ]
}
```
