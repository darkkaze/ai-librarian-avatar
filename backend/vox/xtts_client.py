import aiohttp
import asyncio

class XTTSClient:
    def __init__(self, service_url: str = "http://localhost:5002"):
        self.service_url = service_url
    
    async def speech_to_text(self, text: str, entonacion: str = 'neutral') -> str:
        """Genera speech usando el servicio HTTP TTS"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "text": text,
                "entonacion": entonacion
            }
            
            async with session.post(f"{self.service_url}/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["audio_url"]
                else:
                    error_data = await response.json()
                    raise Exception(f"Error TTS: {error_data.get('error', 'Unknown error')}")