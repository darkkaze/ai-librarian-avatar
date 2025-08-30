#!/usr/bin/env python3
"""
Motor TTS usando XTTS-v2
"""

import os
import torch
import tempfile
from datetime import datetime

# Fix PyTorch compatibility para XTTS
original_load = torch.load
def patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = patched_load

from TTS.api import TTS


class XTTSEngine:
    """Motor TTS usando XTTS-v2"""
    
    def __init__(self):
        print("📱 Inicializando XTTS-v2...")
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self.speaker_wav = "model_tts/voices/demo_nino.mp3"
        self._temp_dir = tempfile.mkdtemp()
        print("✅ XTTS-v2 inicializado y listo")
        
        # Verificar que el sample de voz existe
        if not os.path.exists(self.speaker_wav):
            raise FileNotFoundError(f"Sample de voz no encontrado: {self.speaker_wav}")
    
    def generate_speech(self, text: str) -> str:
        """Genera audio con XTTS-v2"""
        try:
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            output_file = os.path.join(self._temp_dir, f"xtts_{timestamp}.wav")
            
            self.tts.tts_to_file(
                text=text,
                file_path=output_file,
                speaker_wav=self.speaker_wav,
                language="es"
            )
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Error generando TTS con XTTS: {e}")
    
    def cleanup(self):
        """Limpiar recursos de XTTS"""
        # XTTS maneja su propia limpieza
        pass