#!/usr/bin/env python3
"""
Servicio de Text-to-Speech usando XTTS-v2 con Flask
"""

import os
import torch
import tempfile
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Fix PyTorch compatibility 
original_load = torch.load
def patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = patched_load

from TTS.api import TTS

app = Flask(__name__)
CORS(app)

# XTTS no soporta MPS nativamente, solo CUDA
# Usar CPU optimizado para M4 (que en realidad es bastante rápido)
device = "mps"
use_gpu = False

class TTSGenerator:
    """Generador TTS inicializado una sola vez para evitar cold starts"""
    
    def __init__(self):
        print("📱 Inicializando XTTS-v2 en CPU (evitando cold start)...")
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")#, gpu=False)
        self.speaker_wav = "voice_cloning/samples/demo_nino.mp3"  # El sample más grande
        self._temp_dir = tempfile.mkdtemp()
        print("✅ XTTS-v2 inicializado y listo")
        
        # Verificar que el sample de voz existe
        if not os.path.exists(self.speaker_wav):
            raise FileNotFoundError(f"Sample de voz no encontrado: {self.speaker_wav}")
    
    def generate_speech(self, text, entonacion="neutral"):
        """Genera audio TTS y retorna el path del archivo generado"""
        try:
            # Crear nombre único basado en timestamp
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            output_file = os.path.join(self._temp_dir, f"tts_{timestamp}.wav")
            
            # Generar speech con XTTS
            self.tts.tts_to_file(
                text=text,
                file_path=output_file,
                speaker_wav=self.speaker_wav,
                language="es"  # Spanish
            )
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Error generando TTS: {e}")

# Inicializar generador una sola vez (evita cold starts)
print("🔧 Usando CPU optimizado para Apple Silicon")
tts_generator = TTSGenerator()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({"status": "healthy", "service": "speech_to_text_service"})

@app.route('/generate', methods=['POST'])
def generate_speech():
    """
    Endpoint principal para generar speech
    
    Body JSON:
    {
        "text": "Hola mundo",
        "entonacion": "neutral"  // opcional
    }
    
    Response:
    {
        "audio_url": "/voice/tts_abc123.wav"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON requerido"}), 400
        
        text = data.get('text')
        entonacion = data.get('entonacion', 'neutral')
        
        if not text:
            return jsonify({"error": "text requerido"}), 400
        
        # Generar audio usando el generador inicializado
        audio_file = tts_generator.generate_speech(text, entonacion)
        
        # Crear URL para el archivo generado
        filename = os.path.basename(audio_file)
        # Obtener la URL base del servidor desde la request
        server_url = request.host_url.rstrip('/')
        audio_url = f"{server_url}/voice/{filename}"
        
        return jsonify({"audio_url": audio_url})
        
    except Exception as e:
        print(f"❌ Error in generate_speech endpoint: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/voice/<filename>', methods=['GET'])
def serve_audio(filename):
    """Sirve archivos de audio generados"""
    try:
        file_path = os.path.join(tts_generator._temp_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "Archivo no encontrado"}), 404
        
        return send_file(file_path, mimetype='audio/wav')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎤 Iniciando servicio de TTS en puerto 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)