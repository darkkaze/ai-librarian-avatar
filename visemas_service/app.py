#!/usr/bin/env python3
"""
Servicio de generación de visemas usando Flask
"""

import os
import json
import librosa
import numpy as np
import torch
import requests
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile

app = Flask(__name__)
CORS(app)

# Configurar MPS para operaciones de audio con GPU si está disponible
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("🚀 Usando MPS para análisis de audio acelerado")
else:
    device = torch.device("cpu")
    print("⚠️ Usando CPU para análisis de audio")

# Mapeo mejorado de fonemas españoles a visemas VRoid
PHONEME_TO_VISEME = {
    # Vocales principales (más precisas)
    'a': 'aa',      # Boca abierta amplia
    'e': 'ee',      # Sonrisa, boca semi-abierta
    'i': 'ih',      # Sonrisa, boca cerrada
    'o': 'oh',      # Boca redonda
    'u': 'ou',      # Boca muy redonda, labios fruncidos
    
    # Consonantes labiales (requieren cierre labial)
    'p': 'neutral', 'b': 'neutral', 'm': 'neutral',  # Labiales -> cierre
    'f': 'ee', 'v': 'ee',                            # Labio-dentales -> sonrisa ligera
    'w': 'ou',                                       # Semi-vocal labial -> redonda
    
    # Consonantes alveolares (lengua al alveolo)
    't': 'ih', 'd': 'ih', 'n': 'ih', 'l': 'ih',      # Alveolares -> ih
    's': 'ih', 'z': 'ih',                            # Fricativas alveolares -> ih
    'r': 'aa', 'rr': 'aa',                           # Vibrantes -> aa (boca abierta)
    
    # Consonantes palatales (lengua al paladar)
    'ch': 'ih', 'y': 'ih', 'ñ': 'ih',                # Palatales -> ih
    'll': 'ih',                                      # Ll -> ih
    
    # Consonantes velares (parte posterior lengua)
    'k': 'aa', 'g': 'aa', 'j': 'aa',                 # Velares -> aa
    'c': 'aa', 'q': 'aa',                            # Velares adicionales -> aa
    'x': 'ih',                                       # X -> ih
    
    # Consonantes especiales
    'h': 'aa',      # Aspirada -> aa (boca abierta)
    
    # Diptongos comunes en español
    'ai': 'aa', 'ay': 'aa',  # ai/ay -> aa
    'au': 'ou',              # au -> ou
    'ei': 'ee', 'ey': 'ee',  # ei/ey -> ee
    'eu': 'ou',              # eu -> ou
    'oi': 'oh', 'oy': 'oh',  # oi/oy -> oh
    'ou': 'ou',              # ou -> ou
    'ia': 'ih', 'ie': 'ih', 'io': 'ih', 'iu': 'ih',  # i + vocal -> ih predominante
    'ua': 'ou', 'ue': 'ou', 'ui': 'ou', 'uo': 'ou',  # u + vocal -> ou predominante
    
    # Silencio y pausas
    'sil': 'neutral', 'pau': 'neutral'  # Posición neutral/descanso
}

# Patrones de dígrafos y combinaciones españolas
SPANISH_DIGRAPHS = {
    'ch': 'ch',     # che -> ch
    'll': 'll',     # elle -> ll  
    'rr': 'rr',     # erre -> rr
    'qu': 'k',      # que -> k
    'gu': 'g',      # gue -> g (sin u)
    'gü': 'gu',     # güe -> gu
}

# Mapeo de intensidad por tipo de visema (para variaciones naturales)
VISEME_INTENSITY = {
    'aa': 1.0,      # Máxima apertura
    'oh': 0.9,      # Redonda prominente
    'ou': 0.85,     # Redonda pero menos que oh
    'ee': 0.75,     # Sonrisa moderada
    'ih': 0.65,     # Sonrisa sutil
    'neutral': 0.0  # Sin movimiento
}

class VisemeGenerator:
    """Generador de visemas inicializado una sola vez para evitar cold starts"""
    
    def __init__(self):
        print("📦 Inicializando generador de visemas...")
        # Inicializar cualquier modelo o configuración pesada aquí
        self._temp_dir = tempfile.mkdtemp()
        print("✅ Generador de visemas inicializado")
    
    def download_audio(self, audio_url):
        """Descarga audio desde URL"""
        try:
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            
            # Crear archivo temporal
            temp_file = os.path.join(self._temp_dir, "audio.wav")
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            return temp_file
        except Exception as e:
            raise Exception(f"Error descargando audio: {e}")
    
    def text_to_advanced_phonemes(self, text):
        """Conversión mejorada de texto a fonemas españoles con patrones avanzados"""
        text = text.lower().strip()
        if not text:
            return ['neutral']
        
        # Limpiar y normalizar texto
        import re
        text = re.sub(r'[¿¡.,!?;:\-\(\)\[\]\"\'…]', ' ', text)  # Remover puntuación
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios
        
        phonemes = []
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Manejar espacios -> silencio
            if char == ' ':
                if not phonemes or phonemes[-1] != 'sil':  # Evitar silencios duplicados
                    phonemes.append('sil')
                i += 1
                continue
            
            # Detectar dígrafos españoles (2 caracteres)
            if i + 1 < len(text):
                digraph = text[i:i+2]
                if digraph in SPANISH_DIGRAPHS:
                    phonemes.append(SPANISH_DIGRAPHS[digraph])
                    i += 2
                    continue
                
                # Detectar diptongos
                if digraph in PHONEME_TO_VISEME:
                    phonemes.append(digraph)
                    i += 2
                    continue
            
            # Detectar combinaciones especiales de 3 caracteres
            if i + 2 < len(text):
                trigraph = text[i:i+3]
                # Casos como "gue", "gui", "güe", "güi"
                if trigraph in ['gue', 'gui']:
                    phonemes.append('g')
                    phonemes.append(trigraph[2])  # e o i
                    i += 3
                    continue
                elif trigraph in ['güe', 'güi']:
                    phonemes.append('gu')
                    phonemes.append(trigraph[2])  # e o i
                    i += 3
                    continue
            
            # Caracteres individuales
            if char in 'aeiouáéíóúü':
                # Normalizar acentos
                char_map = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u'}
                phonemes.append(char_map.get(char, char))
            elif char in 'bcdfghjklmnpqrstvwxyzñç':
                phonemes.append(char)
            
            i += 1
        
        # Post-procesamiento: optimizar secuencias
        return self._optimize_phoneme_sequence(phonemes)
    
    def _optimize_phoneme_sequence(self, phonemes):
        """Optimiza secuencia de fonemas para mejor flujo de visemas"""
        if not phonemes:
            return ['neutral']
        
        optimized = []
        
        for i, phoneme in enumerate(phonemes):
            # Evitar demasiados silencios seguidos
            if phoneme == 'sil':
                if not optimized or optimized[-1] != 'sil':
                    optimized.append(phoneme)
                continue
            
            # Mejorar transiciones entre consonantes similares
            if optimized and i < len(phonemes) - 1:
                prev_phoneme = optimized[-1]
                next_phoneme = phonemes[i + 1] if i + 1 < len(phonemes) else None
                
                # Si tenemos consonantes similares consecutivas, insertar vocal de apoyo
                if (prev_phoneme in 'bcdfghjklmnpqrstvwxyzñ' and 
                    phoneme in 'bcdfghjklmnpqrstvwxyzñ' and 
                    prev_phoneme != phoneme):
                    # Insertar vocal de apoyo corta
                    optimized.append('e')  # Vocal neutra para transición
            
            optimized.append(phoneme)
        
        return optimized if optimized else ['neutral']
    
    def estimate_phonemes_from_audio(self, audio_file, text_reference=None):
        """Estimación mejorada de visemas con análisis de audio avanzado y anti-duplicación inteligente"""
        # Cargar audio con mejor resolución
        y, sr = librosa.load(audio_file, sr=22050)  # Frecuencia estándar para análisis de habla
        
        # Análisis de audio más sofisticado
        # 1. Detectar segmentos de voz con mejor sensibilidad
        intervals = librosa.effects.split(y, top_db=15, frame_length=2048, hop_length=512)
        
        # 2. Análisis de energía para detectar énfasis
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        
        # 3. Usar texto mejorado para fonemas
        if text_reference:
            phonemes = self.text_to_advanced_phonemes(text_reference)
            print(f"📝 Fonemas detectados: {phonemes}")
        else:
            # Patrón más natural para español
            phonemes = ['h', 'o', 'l', 'a', 'sil', 'm', 'u', 'n', 'd', 'o']
        
        visemes = []
        total_duration = len(y) / sr
        
        # Sistema anti-duplicación mejorado
        last_viseme = None
        viseme_history = []  # Historial de últimos 3 visemas
        emphasis_threshold = np.percentile(rms, 75)  # Umbral de énfasis (75% percentil)
        
        print(f"🎵 Duración total: {total_duration:.2f}s, Intervalos: {len(intervals)}")

        if len(intervals) == 0:
            # Caso sin intervalos detectados - usar duración completa
            phoneme_duration = total_duration / max(len(phonemes), 1)
            
            for i, phoneme in enumerate(phonemes):
                tiempo = round(i * phoneme_duration, 2)
                
                # Calcular énfasis en este momento
                frame_idx = int(tiempo * sr / 512)  # Convertir a índice de frame
                energy = rms[min(frame_idx, len(rms)-1)] if len(rms) > 0 else 0.5
                is_emphasized = energy > emphasis_threshold
                
                # Generar visema con anti-duplicación inteligente
                viseme = self._generate_smart_viseme(
                    phoneme, last_viseme, viseme_history, is_emphasized
                )
                
                visemes.append({
                    "visema": viseme,
                    "tiempo": tiempo
                })
                
                # Actualizar historial
                self._update_viseme_history(viseme_history, viseme)
                last_viseme = viseme
        else:
            # Distribuir fonemas en intervalos detectados
            phoneme_idx = 0
            
            for interval_idx, (start, end) in enumerate(intervals):
                start_time = start / sr
                end_time = end / sr
                interval_duration = end_time - start_time
                
                # Determinar cuántos fonemas asignar a este intervalo
                phonemes_per_interval = max(1, min(4, int(interval_duration * 3)))  # ~3 fonemas por segundo
                current_phonemes = phonemes[phoneme_idx:phoneme_idx + phonemes_per_interval]
                
                if not current_phonemes:  # Si se acabaron los fonemas, usar vocales
                    current_phonemes = ['a']
                
                phoneme_duration = interval_duration / len(current_phonemes)
                
                for i, phoneme in enumerate(current_phonemes):
                    tiempo = round(start_time + (i * phoneme_duration), 2)
                    
                    # Análisis de énfasis para este frame
                    frame_idx = int(tiempo * sr / 512)
                    energy = rms[min(frame_idx, len(rms)-1)] if frame_idx < len(rms) else 0.5
                    is_emphasized = energy > emphasis_threshold
                    
                    # Generar visema inteligente
                    viseme = self._generate_smart_viseme(
                        phoneme, last_viseme, viseme_history, is_emphasized
                    )
                    
                    visemes.append({
                        "visema": viseme,
                        "tiempo": tiempo
                    })
                    
                    # Actualizar historial
                    self._update_viseme_history(viseme_history, viseme)
                    last_viseme = viseme
                
                phoneme_idx += phonemes_per_interval
                
                # Agregar pausa entre intervalos si es significativa
                if interval_idx < len(intervals) - 1:
                    next_start = intervals[interval_idx + 1][0] / sr
                    silence_duration = next_start - end_time
                    
                    if silence_duration > 0.15:  # Pausa de más de 150ms
                        silence_time = round(end_time + silence_duration/2, 2)
                        visemes.append({
                            "visema": "neutral",
                            "tiempo": silence_time
                        })
                        # Resetear historial después de pausa larga
                        viseme_history.clear()
                        last_viseme = "neutral"
        
        # Post-procesamiento final
        visemes = self._post_process_visemes(visemes)
        print(f"✅ Generados {len(visemes)} visemas")
        return visemes
    
    def _generate_smart_viseme(self, phoneme, last_viseme, history, is_emphasized=False):
        """Genera visema con algoritmo anti-duplicación inteligente"""
        base_viseme = PHONEME_TO_VISEME.get(phoneme, 'neutral')
        
        # Si no hay conflicto, usar el visema base
        if base_viseme != last_viseme:
            return base_viseme
        
        # Algoritmo anti-duplicación mejorado
        viseme_groups = {
            'open': ['aa', 'oh', 'ou'],      # Boca abierta/redonda
            'smile': ['ee', 'ih'],           # Sonrisa
            'closed': ['neutral']            # Cerrada
        }
        
        # Encontrar grupo del visema base
        current_group = None
        for group, visemes in viseme_groups.items():
            if base_viseme in visemes:
                current_group = group
                break
        
        if not current_group:
            return base_viseme
        
        # Obtener alternativas del mismo grupo, excluyendo recientes
        alternatives = [v for v in viseme_groups[current_group] 
                       if v != last_viseme and v not in history[-2:]]
        
        # Si no hay alternativas en el grupo, probar grupos relacionados
        if not alternatives:
            if current_group == 'open':
                alternatives = [v for v in viseme_groups['smile'] if v not in history[-1:]]
            elif current_group == 'smile':
                alternatives = [v for v in viseme_groups['open'] if v not in history[-1:]]
            else:
                alternatives = ['aa', 'ee']  # Fallback
        
        if not alternatives:
            return base_viseme  # No hay alternativas, mantener original
        
        # Seleccionar alternativa, considerando énfasis
        if is_emphasized and 'aa' in alternatives:
            return 'aa'  # Énfasis -> boca más abierta
        elif len(alternatives) == 1:
            return alternatives[0]
        else:
            # Selección ponderada (preferir variedad)
            return np.random.choice(alternatives)
    
    def _update_viseme_history(self, history, viseme):
        """Actualiza historial de visemas para anti-duplicación"""
        history.append(viseme)
        if len(history) > 3:  # Mantener solo últimos 3
            history.pop(0)
    
    def _post_process_visemes(self, visemes):
        """Post-procesamiento final para optimizar secuencia de visemas"""
        if len(visemes) < 2:
            return visemes
        
        processed = []
        
        for viseme_data in visemes:
            viseme = viseme_data["visema"]
            tiempo = viseme_data["tiempo"]
            
            # Eliminar visemas duplicados consecutivos con timing muy cercano
            if (processed and 
                processed[-1]["visema"] == viseme and 
                abs(processed[-1]["tiempo"] - tiempo) < 0.1):
                continue  # Skip this duplicate
            
            processed.append({
                "visema": viseme,
                "tiempo": tiempo
            })
        
        return processed
    
    def generate_visemes(self, audio_url, text):
        """Genera visemas desde URL de audio y texto"""
        try:
            # Descargar audio
            audio_file = self.download_audio(audio_url)
            
            # Generar visemas
            visemes = self.estimate_phonemes_from_audio(audio_file, text)
            
            # Limpiar archivo temporal
            try:
                os.remove(audio_file)
            except:
                pass
            
            return {"visemas": visemes}
            
        except Exception as e:
            raise Exception(f"Error generando visemas: {e}")

# Inicializar generador una sola vez (evita cold starts)
viseme_generator = VisemeGenerator()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({"status": "healthy", "service": "visemas_service"})

@app.route('/generate', methods=['POST'])
def generate_visemes():
    """
    Endpoint principal para generar visemas
    
    Body JSON:
    {
        "audio_url": "http://example.com/audio.wav",
        "text": "Hola mundo"
    }
    
    Response:
    {
        "visemas": [
            {"visema": "aa", "tiempo": 0.0},
            {"visema": "neutral", "tiempo": 0.5}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON requerido"}), 400
        
        audio_url = data.get('audio_url')
        text = data.get('text', '')
        
        if not audio_url:
            return jsonify({"error": "audio_url requerido"}), 400
        
        # Generar visemas usando el generador inicializado
        result = viseme_generator.generate_visemes(audio_url, text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎭 Iniciando servicio de visemas en puerto 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)