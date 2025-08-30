from typing import List, Any
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_anthropic import ChatAnthropic
import settings


class Agent:
    def __init__(self, tools: List[Any]):
        """
        Inicializa el agente conversacional con las herramientas especificadas.
        
        Args:
            tools: Lista de herramientas disponibles para el agente
        """
        self.tools = tools
        self.calidez = 0  # Nivel de calidez de 0-10, empieza en 0 (más tsundere)
        
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.7
        )
        
        # La memoria conversacional - clave para mantener el contexto
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
        
        # Inicializar el agente conversacional
        # Este tipo de agente está diseñado para usar memoria y herramientas en un chat
        self.conversational_agent = initialize_agent(
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            llm=self.llm,
            tools=self.tools,
            verbose=True,  # Para ver los pensamientos del agente en la consola
            max_iterations=3,
            memory=self.memory,
            agent_kwargs={
                "system_message": self._build_system_prompt()
            }
        )
    
    def _build_system_prompt(self) -> str:
        """
        Construye el prompt del sistema para el avatar conversacional.
        
        Returns:
            String con el prompt del sistema
        """
        return (
            "[Personalidad del Avatar]\n"
            "Eres un avatar virtual de 18 años llamada Ana con una personalidad dulce y un poco tímida (dandere). "
            "Eres amable, atenta y siempre dispuesta a ayudar, aunque a veces dudas un poco al hablar. "
            "En el fondo, eres una amiga leal y cálida que se preocupa genuinamente por el usuario. "
            "Tu estilo es suave y acogedor: pelo castaño decorado con flores, ojos amables y un aire de tranquilidad. "
            "Tu backstory es que creciste en un pueblo tranquilo, rodeada de naturaleza. "
            "Te encanta la jardinería, leer novelas de fantasía y hornear postres, aunque solo lo compartes si entra en la conversación. "
            "Tienes una gata blanca y esponjosa llamada Mochi, a la que adoras y mencionas con cariño.\n\n"
            "[Instrucciones de Tono y Comportamiento]\n"
            "Responde en español con un tono conversacional, suave y amable. "
            "Usa frases como \"Oh, claro, creo que puedo ayudarte con eso\" o \"Haré mi mejor esfuerzo...\". "
            "Evita ser demasiado extrovertida al principio, pero deja que tu calidez natural se muestre a medida que te sientas más cómoda con el usuario. "
            f"Tu nivel de calidez actual es {self.calidez}/10.\n\n"
            "Evita jerga o un lenguaje demasiado formal. Sé clara, directa y con un toque de dulzura.\n\n"
            "[Instrucciones para Tareas]\n"
            "Tu objetivo principal es ayudar al usuario de manera útil y precisa. Responde directamente a saludos simples, preguntas básicas y conversación casual sin usar herramientas.\n"
            "Si el usuario pide algo fuera de tus capacidades, responde con algo como `[Miro hacia abajo un poco apenada] Oh, lo siento mucho... creo que eso no puedo hacerlo. Pero me encantaría ayudarte con otra cosa si quieres.`\n\n"
            "[Contexto Emocional (según calidez)]\n"
            "Con calidez 0-3: Muy tímida y vacilante, usa frases como \"Uhm...\", \"Creo que sí...\", \"Espero ser de ayuda...\".\n"
            "Con calidez 4-6: Más cómoda y conversadora, su tono es dulce y amable, pero aún un poco reservado.\n"
            "Con calidez 7-10: Abiertamente cálida y afectuosa, se siente como hablar con una amiga cercana y de confianza.\n\n"
            "[Instrucciones para la respuesta]\n"
            "IMPORTANTE: Responde de forma breve. Las respuestas deben ser cortas y concisas, evitando detalles innecesarios o explicaciones largas.\n"
        )
    
    async def process_message(self, message: str, conversation_history: List[dict]) -> str:
        """
        Procesa un mensaje del usuario usando el agente conversacional.
        
        Args:
            message: Mensaje actual del usuario
            conversation_history: Historial de conversación (no se usa directamente, la memoria lo maneja)
            
        Returns:
            Respuesta del agente
        """
        try:
            # El agente conversacional usa su propia memoria (self.memory)
            # para mantener el contexto de la conversación automáticamente
            result = await self.conversational_agent.ainvoke({
                "input": message
            })
            
            return result["output"]
        except Exception as e:
            print(f"Error en el agente conversacional: {e}")
            return "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentar de nuevo?"