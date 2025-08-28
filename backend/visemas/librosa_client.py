import aiohttp

class LibrosaClient:
    def __init__(self, service_url: str = "http://localhost:5001"):
        self.service_url = service_url
    
    async def generate_visemes(self, text: str, audio_url: str) -> dict:
        """Genera visemas usando el servicio HTTP de librosa"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "text": text,
                "audio_url": audio_url
            }
            
            async with session.post(f"{self.service_url}/generate", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise Exception(f"Error visemas: {error_data.get('error', 'Unknown error')}")