# Backend-Frontend Integration Guide

## Arquitectura General

El sistema waifu está compuesto por múltiples servicios que trabajan en conjunto para proveer una experiencia de avatar interactivo con voz, animaciones y expresiones faciales.

## Servicios del Sistema

### 1. Backend Principal (WebSocket)
**Descripción**: Servidor principal que maneja la lógica del agente conversacional, coordina todos los servicios y mantiene conexiones WebSocket con clientes.

**Puerto**: `8765` (configurable en `settings.py`)

**Cómo iniciar**:
```bash
cd backend/
source .venv/bin/activate
python main.py
```

**Funcionalidades**:
- Procesamiento de mensajes del usuario
- Integración con LangChain y Claude Haiku
- Coordinación de servicios TTS, visemas, expresiones y animaciones
- Almacenamiento de conversaciones en SQLite
- Respuestas rápidas con `ToolFastOutput`

---

### 2. Speech-to-Text Service (TTS)
**Descripción**: Servicio HTTP que genera audio usando XTTS-v2 con clonación de voz. Convierte texto a speech usando samples de voz preentrenados.

**Puerto**: `5002`

**Cómo iniciar**:
```bash
cd speech_to_text_service/
source .venv/bin/activate  # (reutiliza .venv de n8n con TTS instalado)
python app.py
```

**Endpoints**:
- `POST /generate` - Genera audio desde texto
- `GET /voice/<filename>` - Sirve archivos de audio generados
- `GET /health` - Health check

**Ejemplo**:
```json
POST /generate
{
  "text": "Hola, soy Hana",
  "entonacion": "neutral"
}

Response:
{
  "audio_url": "/voice/tts_20250824T143022.wav"
}
```

---

### 3. Visemas Service 
**Descripción**: Servicio HTTP que procesa archivos de audio para generar movimientos de labios sincronizados usando librosa. Mapea fonemas españoles a visemas VRoid.

**Puerto**: `5001`

**Cómo iniciar**:
```bash
cd visemas_service/
source .venv/bin/activate
python app.py
```

**Endpoints**:
- `POST /generate` - Genera visemas desde audio y texto
- `GET /health` - Health check

**Ejemplo**:
```json
POST /generate
{
  "audio_url": "http://localhost:5002/voice/tts_20250824T143022.wav",
  "text": "Hola, soy Hana"
}

Response:
{
  "visemas": [
    {"tiempo": 0.0, "visema": "aa"},
    {"tiempo": 0.12, "visema": "oh"},
    {"tiempo": 0.25, "visema": "ih"}
  ]
}
```

---

### 4. Animation Service
**Descripción**: Servicio HTTP que maneja secuencias de animaciones y sirve archivos de poses (.vrma) y modelos de avatar (.vrm). Incluye sistema de selección inteligente de animaciones.

**Puerto**: `5003`

**Cómo iniciar**:
```bash
cd animation_service/
source .venv/bin/activate
python app.py
```

**Endpoints**:
- `GET /sequence/<name>` - Obtiene datos de secuencia de animación
- `GET /sequences` - Lista todas las secuencias disponibles con descripciones
- `GET /poses/<filename>` - Sirve archivos .vrma de poses
- `GET /models/<filename>` - Sirve archivos .vrm de modelos
- `GET /health` - Health check

**Secuencias disponibles**:
- `idle` - Animación de reposo natural
- `hello` - Saludo amigable con gestos de mano
- `v` - Gesto de victoria/paz
- `sexy_look` - Poses seductoras y elegantes
- `inclined` - Inclinación respetuosa

**Ejemplo**:
```json
GET /sequence/hello

Response:
{
  "sequence": "hello",
  "description": "Saludo amigable y energético...",
  "keyframes": [
    {
      "vrma": "http://localhost:5003/poses/hello_key_00.vrma",
      "duration": 0.8,
      "crossfade": 0.15
    }
  ],
  "breathing": false,
  "delay": 0.0
}
```

---

## Flujo de Comunicación

### WebSocket Protocol (Backend Principal)

**Conexión**: `ws://localhost:8765`

**Mensajes del Cliente**:

1. **Heartbeat** (debe enviarse cada 30-60 segundos):
```
"alive"
```
Respuesta: `"alive"`

2. **Mensaje de conversación**:
```json
{
  "message": "Hola, ¿cómo estás?",
  "id": "uuid-random-string"
}
```

**Respuestas del Servidor**:

### Tipo 1: Respuestas Rápidas (Fast Output)
**Sin `message_id`** - Ejecutar inmediatamente:
```json
{
  "audio_url": "/voice/tts_fast_xyz.wav",
  "visemas": [
    {"tiempo": 0.0, "visema": "neutral"},
    {"tiempo": 0.2, "visema": "aa"}
  ],
  "text": "dame un momento mientras lo checo"
}
```
**Acción del cliente**: Reproducir audio y visemas inmediatamente (ASAP).

### Tipo 2: Respuestas Completas (Con ID)
**Con `message_id`** - Esperar a recibir los 3 JSONs:

1. **Audio + Visemas**:
```json
{
  "audio_url": "/voice/tts_20250824T143022.wav",
  "visemas": [
    {"tiempo": 0.0, "visema": "aa"},
    {"tiempo": 0.12, "visema": "oh"}
  ],
  "message_id": "uuid-random-string"
}
```

2. **Expresiones**:
```json
{
  "expresiones": [
    {"expresion": "neutral", "tiempo": 0, "intensidad": 1},
    {"expresion": "happy", "tiempo": 1, "intensidad": 1}
  ],
  "message_id": "uuid-random-string"
}
```

3. **Animaciones**:
```json
{
  "sequence": "hello",
  "keyframes": [
    {"vrma": "http://localhost:5003/poses/hello_key_00.vrma", "duration": 0.8, "crossfade": 0.15}
  ],
  "breathing": false,
  "delay": 0.0,
  "message_id": "uuid-random-string"
}
```

**Acción del cliente**: Una vez recibidos los 3 JSONs con el mismo `message_id`, procesarlos todos juntos de forma sincronizada.

---

## Orden de Inicialización

Para levantar el sistema completo:

1. **TTS Service** (puerto 5002)
2. **Visemas Service** (puerto 5001) 
3. **Animation Service** (puerto 5003)
4. **Backend Principal** (puerto 8765)

## Dependencias

- **Backend Principal**: Requiere que todos los servicios HTTP estén corriendo
- **Visemas Service**: Requiere TTS Service para obtener archivos de audio
- **TTS y Animation**: Independientes entre sí
- **Frontend**: Requiere Backend Principal (WebSocket) y Animation Service (archivos estáticos)

## Configuración

Todos los puertos y URLs son configurables en los archivos respectivos:
- `backend/settings.py` - WebSocket
- `*_service/app.py` - Servicios HTTP