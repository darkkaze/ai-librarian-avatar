#!/usr/bin/env python3
"""
Servicio de Text-to-Speech refactorizado
Soporta Gemini TTS, Piper TTS y XTTS-v2
"""

import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Importar motores TTS
from model_gemini.gemini_engine import GeminiEngine
from model_piper.piper_engine import PiperEngine
from model_tts.xtts_engine import XTTSEngine

app = Flask(__name__)
CORS(app)

# Inicializar motor TTS con Gemini por defecto
print("🔧 Inicializando servicio TTS con Gemini TTS...")
try:
    tts_engine = GeminiEngine()
    print("✅ Servicio TTS inicializado con Gemini")
except Exception as e:
    print(f"⚠️ Error inicializando Gemini, fallback a Piper: {e}")
    try:
        tts_engine = PiperEngine()
        print("✅ Servicio TTS inicializado con Piper (fallback)")
    except Exception as e2:
        print(f"⚠️ Error inicializando Piper, fallback a XTTS: {e2}")
        tts_engine = XTTSEngine()
        print("✅ Servicio TTS inicializado con XTTS (fallback final)")

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    engine_name = type(tts_engine).__name__.replace('Engine', '').lower()
    return jsonify({
        "status": "healthy", 
        "service": "speech_to_text_service",
        "engine": engine_name
    })

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
        "audio_url": "/voice/filename.wav",
        "engine": "gemini|piper|xtts"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON requerido"}), 400
        
        text = data.get('text')
        
        if not text:
            return jsonify({"error": "text requerido"}), 400
        
        print(f"🎤 Generando TTS: '{text}' con {type(tts_engine).__name__}")
        
        # Generar audio usando el motor configurado
        audio_file = tts_engine.generate_speech(text)
        
        # Crear URL para el archivo generado
        filename = os.path.basename(audio_file)
        server_url = request.host_url.rstrip('/')
        audio_url = f"{server_url}/voice/{filename}"
        
        engine_name = type(tts_engine).__name__.replace('Engine', '').lower()
        
        return jsonify({
            "audio_url": audio_url,
            "engine": engine_name
        })
        
    except Exception as e:
        print(f"❌ Error in generate_speech endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/voice/<filename>', methods=['GET'])
def serve_audio(filename):
    """Sirve archivos de audio generados"""
    try:
        file_path = os.path.join(tts_engine._temp_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "Archivo no encontrado"}), 404
        
        return send_file(file_path, mimetype='audio/wav')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎤 Iniciando servicio de TTS refactorizado en puerto 5002...")
    try:
        app.run(host='0.0.0.0', port=5002, debug=True)
    finally:
        tts_engine.cleanup()