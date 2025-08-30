import aiohttp
import openai

class AnimationsClient:
    def __init__(self, service_url: str = "http://localhost:5003", openai_api_key: str = None):
        self.service_url = service_url
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
    
    async def generate_animations(self, agent_response: str) -> dict:
        """Genera animaciones usando GPT para selección y servicio HTTP para obtener datos"""
        try:
            # Usar métodos privados según buenas prácticas
            selected_animation = await self._select_animation(agent_response)
            animation_data = await self._retrieve_animation_from_server(selected_animation)
            
            return animation_data
        except Exception:
            # Fallback a idle si hay error
            return await self._retrieve_animation_from_server("idle")
    
    async def _select_animation(self, agent_response: str) -> str:
        """Usa GPT-4o-mini para seleccionar la animación más apropiada"""
        if not self.openai_client:
            print("❌ OpenAI API key not configured, defaulting to 'idle' animation")
            return "idle"  # Fallback si no hay API key
        
        try:
            # Obtener lista de animaciones disponibles
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/sequences") as response:
                    if response.status == 200:
                        sequences_data = await response.json()
                        sequences = sequences_data.get("sequences", [])
                    else:
                        return "idle"
            
            # Crear prompt para GPT
            sequences_text = "\n".join([
                f"- {seq['sequence']}: {seq['description']}" 
                for seq in sequences
            ])
            
            prompt = (
                f"Dada la siguiente respuesta del agente, "
                f"selecciona la animación más apropiada.\n\n"
                f"Respuesta del agente: \"{agent_response}\"\n\n"
                f"Animaciones disponibles:\n{sequences_text}\n\n"
                f"Mandatorio: Responde únicamente con el nombre de la animación (ejemplo: \"hello\", \"idle\", \"v\", etc.). "
                "Mandatorio: responder solo con el nombre exacto de la animación.\n"
                f"Si no hay una animación clara para el contexto, usa \"idle\"."
            )

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Usando gpt-4o-mini (más disponible que gpt-4.1-nano)
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.3
            )
            
            selected = response.choices[0].message.content.strip().lower()
            print(f"🎭 Animation selected by GPT: {selected}, debug: {response.choices[0].message}")
            # Validar que la animación existe
            available_sequences = [seq['sequence'] for seq in sequences]
            if selected in available_sequences:
                return selected
            else:
                return "idle"
                
        except Exception as e:
            print(f"Error en _select_animation: {e}")
            return "idle"
    
    async def _retrieve_animation_from_server(self, sequence_name: str) -> dict:
        """Obtiene los datos completos de animación desde el servidor"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/sequence/{sequence_name}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        # Fallback a idle si la secuencia no existe
                        async with session.get(f"{self.service_url}/sequence/idle") as fallback_response:
                            if fallback_response.status == 200:
                                return await fallback_response.json()
                            else:
                                # Último fallback hardcodeado
                                return {
                                    "sequence": "idle",
                                    "keyframes": [{"vrma": "http://localhost:5003/animations/waiting-animation.vrma", "duration": 2.0, "crossfade": 0.25}],
                                    "breathing": True,
                                    "delay": 0.0
                                }
        except Exception as e:
            print(f"Error en _retrieve_animation_from_server: {e}")
            return {
                "sequence": "idle",
                "keyframes": [{"vrma": "http://localhost:5003/animations/waiting-animation.vrma", "duration": 2.0, "crossfade": 0.25}],
                "breathing": True,
                "delay": 0.0
            }