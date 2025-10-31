#!/usr/bin/env python3
"""
Motor TTS usando Gemini 2.5 Pro Preview TTS
Configuración: Acento mexicano, voz neutral, poca emoción, informativo
"""

import os
import mimetypes
import struct
import tempfile
from datetime import datetime
from google import genai
from google.genai import types


class GeminiEngine:
    """Motor TTS usando Gemini 2.5 Pro Preview TTS"""

    def __init__(self):
        print("🤖 Inicializando Gemini TTS...")

        # Obtener API key del entorno
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno")

        # Inicializar cliente Gemini
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-pro-preview-tts"
        self.voice_name = "Despina"

        self._temp_dir = tempfile.mkdtemp()

        print("✅ Gemini TTS inicializado")
        print(f"   Modelo: {self.model}")
        print(f"   Voz: {self.voice_name}")

    def generate_speech(self, text: str) -> str:
        """
        Genera audio con Gemini TTS

        Args:
            text: Texto a sintetizar

        Returns:
            Ruta del archivo de audio generado
        """
        try:
            # Agregar instrucciones de estilo al texto
            text_with_style = f"""Habla con acento mexicano, voz neutral, poca emoción, tono informativo y profesional:
{text}"""

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=text_with_style),
                    ],
                ),
            ]

            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voice_name
                        )
                    )
                ),
            )

            # Generar audio en streaming
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            file_index = 0

            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue

                if (
                    chunk.candidates[0].content.parts[0].inline_data
                    and chunk.candidates[0].content.parts[0].inline_data.data
                ):
                    output_file = os.path.join(
                        self._temp_dir, f"gemini_{timestamp}_{file_index}.wav"
                    )
                    file_index += 1

                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)

                    if file_extension is None:
                        file_extension = ".wav"
                        data_buffer = self._convert_to_wav(
                            inline_data.data, inline_data.mime_type
                        )

                    with open(output_file, "wb") as f:
                        f.write(data_buffer)

                    # Retornar el primer archivo generado
                    return output_file

            raise Exception("No se generó ningún archivo de audio")

        except Exception as e:
            raise Exception(f"Error generando TTS con Gemini: {e}")

    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """
        Convierte datos de audio raw a formato WAV

        Args:
            audio_data: Datos de audio raw
            mime_type: Tipo MIME del audio

        Returns:
            Datos de audio en formato WAV
        """
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            chunk_size,
            b"WAVE",
            b"fmt ",
            16,
            1,
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_size,
        )
        return header + audio_data

    def _parse_audio_mime_type(self, mime_type: str) -> dict:
        """
        Extrae parámetros de audio del MIME type

        Args:
            mime_type: Tipo MIME (ej: "audio/L16;rate=24000")

        Returns:
            Diccionario con bits_per_sample y rate
        """
        bits_per_sample = 16
        rate = 24000

        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass

        return {"bits_per_sample": bits_per_sample, "rate": rate}

    def cleanup(self):
        """Limpiar archivos temporales de Gemini"""
        import shutil

        if os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
