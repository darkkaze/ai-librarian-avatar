import websockets
import asyncio
import json

import settings
from agents.agent import Agent
from db.models import DatabaseManager
from vox.xtts_client import XTTSClient
from visemas.librosa_client import LibrosaClient
from animations.expressions_client import ExpressionsClient
from animations.animations_client import AnimationsClient
from langchain_community.tools import TavilySearchResults  # Herramienta de búsqueda web
import os
import re

class WebSocketHandler:
    def __init__(self, agent: Agent, db_manager: DatabaseManager, websocket):
        """
        Inicializa el manejador de WebSocket.
        
        Args:
            agent: Instancia del agente LangChain
            db_manager: Manager de la base de datos
            websocket: Conexión WebSocket del cliente
        """
        self.agent = agent
        self.db_manager = db_manager
        self.websocket = websocket
        self.tts_model = XTTSClient()
        self.visemas_model = LibrosaClient()
        self.expressions_model = ExpressionsClient()
        self.animations_model = AnimationsClient(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    async def handler(self):
        """Handler principal que rutea mensajes según su tipo"""
        async for message in self.websocket:
            try:
                print(f"Mensaje recibido: {message}")
                
                # Parsear mensaje
                if message == "alive":
                    await self.alive()
                else:
                    try:
                        msg_data = json.loads(message)
                        if "message" in msg_data and "id" in msg_data:
                            await self.main(msg_data["message"], msg_data["id"])
                        else:
                            await self.websocket.send(json.dumps({
                                "error": "Formato de mensaje inválido. Se requiere: {\"message\":\"...\", \"id\":\"...\"}", 
                                "type": "error"
                            }))
                    except json.JSONDecodeError:
                        await self.websocket.send(json.dumps({
                            "error": "JSON inválido", 
                            "type": "error"
                        }))
                        
            except Exception as e:
                print(f"Error procesando mensaje: {e}")
                await self.websocket.send(json.dumps({"error": str(e), "type": "error"}))
    
    async def alive(self):
        """Responde al heartbeat para mantener conexión activa"""
        await self.websocket.send("alive")
    
    async def main(self, message: str, message_id: str):
        """Función principal que maneja el flujo de procesamiento"""
        agent_response = await self.agent.process_message(message, [])  # El agente maneja su propia memoria
        agent_response = agent_response[0]['text'] if isinstance(agent_response, list) else agent_response
        print(f"Respuesta del agente: {agent_response}")
        # remove all text inside []
        agent_response = re.sub(r'\[.*?\]', '', agent_response).strip()
        # remove Sonrío con *:
        agent_response = re.sub(r'Sonr[ií]o(?: con)? \w+:?', '', agent_response).strip()
        # remove y? le? respondo con *
        agent_response = re.sub(r'(?:y\s*)?(?:le\s*)?respondo(?: con)? \w+:?', '', agent_response, flags=re.IGNORECASE).strip()
        await asyncio.gather(
            self._parallel1(message, agent_response, message_id),
            self._parallel2(agent_response, message_id), 
            self._parallel3(agent_response, message_id)
        )
    
    async def _parallel1(self, message: str, agent_response: str, message_id: str):
        """Primera rama de procesamiento paralelo: audio y visemas"""
        await self.db_manager.save_conversation(message, agent_response)
        audio_url = await self.tts_model.speech_to_text(agent_response)
        #await self.websocket.send(json.dumps({"audio_url": audio_url, "message_id": message_id}))
        visemas = await self.visemas_model.generate_visemes(agent_response, audio_url) 
        await self.websocket.send(json.dumps(
            {"audio_url": audio_url, "message_id": message_id, "visemas": visemas.get("visemas", [])})
            )
    
    async def _parallel2(self, agent_response: str, message_id: str):
        """Segunda rama de procesamiento paralelo: expresiones"""
        expressions = await self.expressions_model.generate_expressions(agent_response) 
        expressions["message_id"] = message_id
        await self.websocket.send(json.dumps(expressions))
    
    async def _parallel3(self, agent_response: str, message_id: str):
        """Tercera rama de procesamiento paralelo: animaciones"""
        animations = await self.animations_model.generate_animations(agent_response)
        animations["message_id"] = message_id
        await self.websocket.send(json.dumps(animations))



async def start_server():
    """Inicializa el servidor WebSocket"""
    # Inicializar dependencias
    db_manager = DatabaseManager()
    
    async def handler_factory(websocket):
        """Factory para crear instancias de WebSocketHandler por cliente"""
        # Crear modelos para fast output
        from vox.xtts_client import XTTSClient
        from visemas.librosa_client import LibrosaClient
        tts_model = XTTSClient()
        visemas_model = LibrosaClient()
        
        tools = []
        
        # Agregar herramienta de búsqueda si hay API key
        if os.getenv("TAVILY_API_KEY"):
            search_tool = TavilySearchResults(max_results=3)  # Herramienta de búsqueda web
            tools.append(search_tool)
            print("✅ Herramienta de búsqueda Tavily agregada")
        else:
            print("⚠️ TAVILY_API_KEY no encontrada. Búsqueda web deshabilitada.")
        
        # Crear agente con las herramientas disponibles
        agent = Agent(tools=tools)
        
        websocket_handler = WebSocketHandler(agent, db_manager, websocket)
        await websocket_handler.handler()
    
    print(f"Iniciando servidor WebSocket en {settings.WEBSOCKET_HOST}:{settings.WEBSOCKET_PORT}")
    server = await websockets.serve(
        handler_factory, 
        settings.WEBSOCKET_HOST, 
        settings.WEBSOCKET_PORT
    )
    print("Servidor iniciado. Esperando conexiones...")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(start_server())