#!/usr/bin/env python3
"""
Motor TTS usando Piper con configuración claude_slow_11
Usando subprocess (API directa tiene problemas)
"""

import os
import subprocess
import tempfile
from datetime import datetime


class PiperEngine:
    """Motor TTS usando Piper con configuración claude_slow_11"""
    
    def __init__(self):
        print("🎤 Inicializando Piper TTS...")
        
        # Configuración claude_slow_11 
        self.model_path = "model_piper/voices/es_MX-claude-high.onnx"
        self.length_scale = 1.1        # 10% más lenta
        self.noise_scale = 0.6         # Configuración estándar para claridad  
        self.noise_w_scale = 0.6       # Configuración estándar
        self.sentence_silence = 0.2    # Sin pausas adicionales
        self.pitch = 3  # 1.0 es normal, >1.0 más aguda, <1.0 más grave
        
        self._temp_dir = tempfile.mkdtemp()
        
        # Verificar que el modelo existe
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo Piper no encontrado: {self.model_path}")
        
        print(f"✅ Piper TTS inicializado (claude_slow_11 config)")
        print(f"   Modelo: {self.model_path}")
        print(f"   Velocidad: {self.length_scale}x")
    
    def generate_speech(self, text: str) -> str:
        """Genera audio con Piper TTS usando API directa"""
        try:
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            output_file = os.path.join(self._temp_dir, f"piper_{timestamp}.wav")
            
            # Comando Piper con configuración claude_slow_11
            cmd = [
                "python", "-m", "piper",
                "--model", self.model_path,
                "--output_file", output_file,
                "--length-scale", str(self.length_scale),
                "--noise-scale", str(self.noise_scale),
                "--noise-w-scale", str(self.noise_w_scale),
                "--sentence-silence", str(self.sentence_silence)
            ]
            
            # Ejecutar Piper
            subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                check=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../"))
            )
            
            if not os.path.exists(output_file):
                raise Exception("Piper no generó el archivo de audio")
            
            return output_file
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error ejecutando Piper: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error generando TTS con Piper: {e}")
    
    def cleanup(self):
        """Limpiar archivos temporales de Piper"""
        import shutil
        if os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)