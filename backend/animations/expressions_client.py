import openai

class ExpressionsClient:
    def __init__(self, openai_api_key: str = None):
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
    
    async def generate_expressions(self, agent_response: str) -> dict:
        """Genera expresiones usando GPT para crear secuencia JSON"""
        if not self.openai_client:
            return {
                "expresiones": [
                    {"expresion": "neutral", "tiempo": 0.0, "intensidad": 1.0}
                ]
            }
        
        try:
            # Calcular duración aproximada basada en longitud del texto
            duration = max(2, len(agent_response) // 20)  # ~20 chars por segundo
            
            expressions_list = [
                'neutral', 'blink', 'happy', 'angry', 'sad', 'relaxed', 
                'lookUp', 'lookDown', 'lookLeft', 'lookRight', 'blinkLeft', 
                'blinkRight', 'blush', 'surprised'
            ]
            
            prompt = (
                f"Genera expresiones faciales para esta respuesta del agente: \"{agent_response}\"\n\n"
                f"Duración aproximada: {duration} segundos\n"
                f"Expresiones disponibles: {expressions_list}\n\n"
                f"Reglas:\n"
                f"- Comenzar con 'neutral' en tiempo 0\n"
                f"- Elegir 1 o 2 expresiones apropiadas durante la respuesta\n"
                f"- Terminar con 'neutral'\n"
                f"- Tiempo en segundos, intensidad siempre 1\n\n"
                f"MANDATORIO: Responde únicamente el JSON en este formato:\n"
                f'{{"expresiones": [\n'
                f'  {{"expresion": "neutral", "tiempo": 0, "intensidad": 1}},\n'
                f'  {{"expresion": "happy", "tiempo": 1, "intensidad": 1}},\n'
                f'  {{"expresion": "blink", "tiempo": 2.5, "intensidad": 1}},\n'
                f'  {{"expresion": "neutral", "tiempo": 3, "intensidad": 1}}\n'
                f']}}'
            )
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.4
            )
            
            # Parsear respuesta JSON
            import json
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            print(f"Error en generate_expressions: {e}")
            return {
                "expresiones": [
                    {"expresion": "neutral", "tiempo": 0, "intensidad": 1},
                    {"expresion": "blink", "tiempo": 1, "intensidad": 1},
                    {"expresion": "neutral", "tiempo": 2, "intensidad": 1}
                ]
            }