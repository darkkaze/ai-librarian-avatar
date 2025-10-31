# Animation Service

Flask service that serves VRMA animation files and animation sequence definitions for the Waifu Avatar System.

## Description

This service provides:
- Serving `.vrma` animation files for 3D VRM avatars
- Animation sequence definitions with timing and transitions
- REST API for querying available animations

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

The service will start on **port 5003**.

## API Endpoints

- `GET /sequences` - List all available animation sequences
- `GET /sequence/<name>` - Get specific animation sequence data
- `GET /animations/<filename>` - Serve VRMA animation files

## Animation Files

- Animation files (`.vrma`) are stored in `animations/`
- Sequence definitions (JSON) are stored in `jsons/`
