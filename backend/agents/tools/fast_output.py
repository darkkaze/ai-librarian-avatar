from langchain.tools import BaseTool
from typing import Any, Dict, Type
from pydantic import BaseModel, Field
import random
import json
import asyncio


class FastOutputInput(BaseModel):
    message: str = Field(description="Mensaje rápido a enviar al usuario")


class ToolFastOutput(BaseTool):
    """
    Herramienta para enviar respuestas rápidas al usuario mientras se procesan otras tareas.
    """
    
    name: str = "fast_output"
    description: str = """Usa esta herramienta PRIMERO cuando una tarea requiera usar múltiples herramientas o procesamiento complejo. 
    Envía un mensaje de acknowledgment rápido al usuario mientras procesas la respuesta completa en paralelo."""
    
    args_schema: Type[BaseModel] = FastOutputInput
    
    # Declarar atributos para Pydantic v2
    websocket: Any = None
    tts_model: Any = None
    visemas_model: Any = None
    
    def __init__(self, websocket, tts_model=None, visemas_model=None):
        super().__init__()
        self.websocket = websocket
        self.tts_model = tts_model
        self.visemas_model = visemas_model
    
    async def _arun(self, message: str) -> str:
        """Versión asíncrona de la herramienta"""
        # Elegir frase aleatoria
        selected_text = self._get_random_phrase()
        print(f"🎭 Fast output selected text: {selected_text}")
        
        # Generar audio y visemas si los modelos están disponibles
        print(f"🎭 TTS model available: {self.tts_model is not None}")
        print(f"🎭 Visemas model available: {self.visemas_model is not None}")
        
        if self.tts_model and self.visemas_model:
            try:
                print("🎭 Generating TTS audio...")
                # Generar audio
                audio_url = await self.tts_model.speech_to_text(selected_text)
                print(f"🎭 TTS audio URL: {audio_url}")
                
                print("🎭 Generating visemas...")
                # Generar visemas
                visemas_data = await self.visemas_model.generate_visemes(selected_text, audio_url)
                print(f"🎭 Visemas generated: {len(visemas_data.get('visemas', []))} items")
                
                # Enviar respuesta con audio y visemas generados
                response = {
                    "audio_url": audio_url,
                    "visemas": visemas_data.get("visemas", []),
                    "text": selected_text
                }
                print(f"🎭 Sending complete fast output: {response}")
            except Exception as e:
                print(f"❌ Error generando audio/visemas rápidos: {e}")
                # Fallback sin audio
                response = {
                    "text": selected_text
                }
                print(f"🎭 Sending fallback fast output: {response}")
        else:
            print("🎭 No models available, sending text-only")
            # Fallback sin audio
            response = {
                "text": selected_text
            }
            print(f"🎭 Sending text-only fast output: {response}")
        
        await self.websocket.send(json.dumps(response))
        return f"Enviado mensaje rápido: '{selected_text}'"
    
    def _run(self, message: str) -> str:
        """Versión síncrona"""
        selected_text = self._get_random_phrase()
        return f"Mensaje rápido: {selected_text}"
    
    def _get_random_phrase(self) -> str:
        """Retorna una frase rápida aleatoria"""
        phrases = [
            "dame un momento mientras lo checo",
            "ok, espera, lo reviso",
            "agh, espera que lo busco", 
            "vale, déjame revisar",
            "mmm, dame un segundo",
            "espera, voy a ver",
            "oki, un momentito",
            "ah, espérame tantito",
            "sure, lo busco ahora",
            "perfecto, checando..."
        ]
        return random.choice(phrases)