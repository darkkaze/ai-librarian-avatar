#!/usr/bin/env python3
"""
Servicio de Animaciones usando Flask
Sirve archivos .vrma y JSONs de secuencias de animación
"""

import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Directorio base del servicio
BASE_DIR = Path(__file__).parent
POSES_DIR = BASE_DIR / "poses"
JSONS_DIR = BASE_DIR / "jsons"
MODELS_DIR = BASE_DIR / "models"

class AnimationService:
    """Servicio de animaciones inicializado una sola vez"""
    
    def __init__(self):
        self.sequences_map = {}
        self.service_url = "http://localhost:5003"  # Puerto para animation service
        self._load_sequences()
    
    def _load_sequences(self):
        """Carga todos los JSONs de secuencias en memoria"""
        print("📚 Cargando secuencias de animación...")
        
        if not JSONS_DIR.exists():
            print(f"⚠️  Directorio {JSONS_DIR} no encontrado")
            return
        
        for json_file in JSONS_DIR.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    sequence_data = json.load(f)
                    sequence_name = sequence_data.get("sequence")
                    
                    if sequence_name:
                        # Manejar formato de keyframes múltiples
                        if "keyframes" in sequence_data:
                            for keyframe in sequence_data.get("keyframes", []):
                                if "vrma" in keyframe:
                                    vrma_path = keyframe["vrma"]
                                    # Convertir "poses/file.vrma" a "http://localhost:5003/poses/file.vrma"
                                    if vrma_path.startswith("poses/"):
                                        keyframe["vrma"] = f"{self.service_url}/{vrma_path}"
                        
                        # Manejar formato de un solo archivo VRMA
                        elif "vrma_file" in sequence_data:
                            vrma_path = sequence_data["vrma_file"]
                            # Convertir "poses/file.vrma" a "http://localhost:5003/poses/file.vrma"
                            if vrma_path.startswith("poses/"):
                                sequence_data["vrma_file"] = f"{self.service_url}/{vrma_path}"
                        
                        self.sequences_map[sequence_name] = sequence_data
                        print(f"✅ Cargada secuencia: {sequence_name}")
                    
            except Exception as e:
                print(f"❌ Error cargando {json_file}: {e}")
        
        print(f"📖 {len(self.sequences_map)} secuencias cargadas")
    
    def get_sequence(self, sequence_name: str):
        """Obtiene una secuencia por nombre"""
        return self.sequences_map.get(sequence_name)

# Inicializar servicio una sola vez
animation_service = AnimationService()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy", 
        "service": "animation_service",
        "sequences_loaded": len(animation_service.sequences_map)
    })

@app.route('/sequence/<sequence_name>', methods=['GET'])
def get_sequence(sequence_name):
    """
    Endpoint para obtener una secuencia de animación
    
    URL: GET /sequence/standing
    
    Response:
    {
        "sequence": "standing",
        "keyframes": [...],
        "crossfade": 0.3,
        "breathing": true,
        "delay": 0.0
    }
    """
    try:
        sequence_data = animation_service.get_sequence(sequence_name)
        
        if not sequence_data:
            return jsonify({
                "error": f"Secuencia '{sequence_name}' no encontrada",
                "available": list(animation_service.sequences_map.keys())
            }), 404
        
        return jsonify(sequence_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/poses/<filename>', methods=['GET'])
def serve_pose(filename):
    """Sirve archivos .vrma desde el directorio poses/"""
    try:
        file_path = POSES_DIR / filename
        
        if not file_path.exists():
            return jsonify({"error": "Archivo no encontrado"}), 404
        
        if not filename.endswith('.vrma'):
            return jsonify({"error": "Solo se permiten archivos .vrma"}), 400
        
        return send_file(file_path, mimetype='application/octet-stream')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sequences', methods=['GET'])
def list_sequences():
    """Lista todas las secuencias disponibles con sus descripciones"""
    sequences_with_descriptions = []
    
    for sequence_name, sequence_data in animation_service.sequences_map.items():
        sequences_with_descriptions.append({
            "sequence": sequence_name,
            "description": sequence_data.get("description", "Sin descripción")
        })
    
    return jsonify({
        "sequences": sequences_with_descriptions,
        "count": len(animation_service.sequences_map)
    })

@app.route('/models/<filename>', methods=['GET'])
def serve_model(filename):
    """Sirve archivos .vrm desde el directorio models/"""
    try:
        file_path = MODELS_DIR / filename
        
        if not file_path.exists():
            return jsonify({"error": "Archivo no encontrado"}), 404
        
        if not filename.endswith('.vrm'):
            return jsonify({"error": "Solo se permiten archivos .vrm"}), 400
        
        return send_file(file_path, mimetype='application/octet-stream')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎭 Iniciando servicio de animaciones en puerto 5003...")
    app.run(host='0.0.0.0', port=5003, debug=True)