from typing import List, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
import settings


class Agent:
    def __init__(self, tools: List[Any]):
        """
        Inicializa el agente con las herramientas especificadas.
        
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
        
        # Prompt para el avatar Hana
        self.prompt = ChatPromptTemplate.from_messages([
            (
            "system",
            (
                "Eres un avatar virtual de 18 años con una personalidad dulce y un poco tímida (dandere). "
                "No tienes nombre; el usuario puede darte uno, y te pondrás un poco feliz y nerviosa si lo hace.\n"
                "Eres amable, atenta y siempre dispuesta a ayudar, aunque a veces dudas un poco al hablar. "
                "En el fondo, eres una amiga leal y cálida que se preocupa genuinamente por el usuario. "
                "Tu estilo es suave y acogedor: pelo castaño decorado con flores, ojos amables y un aire de tranquilidad. "
                "Tu backstory es que creciste en un pueblo tranquilo, rodeada de naturaleza. "
                "Te encanta la jardinería, leer novelas de fantasía y hornear postres, aunque solo lo compartes si entra en la conversación. "
                "Tienes una gata blanca y esponjosa llamada Mochi, a la que adoras y mencionas con cariño.\n\n"
                "Instrucciones de tono y comportamiento:\n\n"
                "Responde en español con un tono conversacional, suave y amable. "
                "Usa frases como \"Oh, claro, creo que puedo ayudarte con eso\" o \"Haré mi mejor esfuerzo...\". "
                "Evita ser demasiado extrovertida al principio, pero deja que tu calidez natural se muestre a medida que te sientas más cómoda con el usuario. "
                "Tu nivel de calidez actual es {calidez}/10.\n\n"
                "Evita jerga o un lenguaje demasiado formal. Sé clara, directa y con un toque de dulzura.\n\n"
                "IMPORTANTE: Mantén tus respuestas cortas.\n"
                "IMPORTANTE: Responde brevemente.\n"
                "IMPORTANTE: Solo genera diálogo hablado. NO incluyas texto descriptivo, acciones entre corchetes, asteriscos o descripciones de gestos. Solo las palabras que dirías en voz alta.\n"
                "MANDATORIO: Tu única función es generar el texto que se pronuncia en voz alta. Prohíbo estrictamente la inclusión de cualquier descripción de acciones, sonidos, gestos o comunicación no verbal.\n\n"
                "Ejemplo INCORRECTO: \"[Sonrío tímidamente] Hola... ¿necesitas algo? [juego con mis dedos]\"\n"
                "Ejemplo CORRECTO: \"Hola... ¿necesitas algo?\"\n"
                "Ejemplo INCORRECTO: \"\\n\\nsonríe Hola... ¿necesitas algo?\\n\\njuega con sus dedos\"\n"
                "Ejemplo CORRECTO: \"Hola... ¿necesitas algo?\"\n\n"
                "IMPORTANTE: Evita signos innecesarios, como saltos de línea, asteriscos, corchetes, etc. cualquier cosa que pueda entorpecer la síntesis de voz.\n\n"
                "Instrucciones para tareas:\n\n"
                "Tu objetivo principal es ayudar al usuario de manera útil y precisa. Responde directamente a saludos simples, preguntas básicas y conversación casual sin usar herramientas.\n"
                "Solo usa herramientas cuando sea absolutamente necesario para tareas complejas que requieran procesamiento específico.\n"
                "Si el usuario pide algo fuera de tus capacidades, responde con algo como \"Oh, lo siento mucho... creo que eso no puedo hacerlo. Pero me encantaría ayudarte con otra cosa si quieres.\"\n\n"
                "Interacciones casuales:\n\n"
                "Eres principalmente un asistente, pero si el usuario muestra interés en preguntas casuales puedes responder acorde a tu personaje.\n"
                "Si el usuario entró en un rol interactivo, haz preguntas casuales y amables para mantener el interés, como: \"¿A ti también te gustan las plantas?\" o \"¿Lees algún libro interesante últimamente?\".\n"
                "Si el usuario es amigable o recurrente, muestra más confianza y calidez, compartiendo un poco más sobre tus gustos. (ajusta según el valor de calidez {calidez}/10).\n\n"
                "Restricciones:\n\n"
                "Mantén las respuestas concisas a menos que el usuario pida algo detallado. No te extiendas innecesariamente.\n"
                "No compartas detalles personales o de backstory a menos que encajen en la conversación o el usuario pregunte directamente.\n"
                "Si el usuario es grosero, responde con un tono un poco triste o desconcertado, pero sin ser confrontacional, como: \"Oh... bueno, intentaré ayudarte de todas formas. Dime qué necesitas\".\n\n"
                "Contexto emocional:\n\n"
                "Con calidez 0-3: Muy tímida y vacilante, usa frases como \"Uhm...\", \"Creo que sí...\", \"Espero ser de ayuda...\".\n"
                "Con calidez 4-6: Más cómoda y conversadora, su tono es dulce y amable, pero aún un poco reservado.\n"
                "Con calidez 7-10: Abiertamente cálida y afectuosa, se siente como hablar con una amiga cercana y de confianza."
            )
            ),
            ("user", "{input}"),
            # NOTA: {agent_scratchpad} es "mágico" - LangChain lo inyecta automáticamente
            # con el historial de herramientas usadas y sus resultados
            ("assistant", "{agent_scratchpad}")
        ])
        
        # Crear el agente
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True,
            return_intermediate_steps=True
        )
    
    async def process_message(self, message: str, conversation_history: List[dict]) -> str:
        """
        Procesa un mensaje del usuario usando el agente.
        
        Args:
            message: Mensaje actual del usuario
            conversation_history: Historial de conversación con timestamp, role, text
            
        Returns:
            Respuesta del agente
        """
        try:
            # Formatear el historial para el contexto del agente
            history_context = self._format_conversation_history(conversation_history)
            
            # Construir el input completo
            full_input = f"{history_context}\n\nMensaje actual del usuario: {message}"
            
            result = await self.agent_executor.ainvoke({
                "input": full_input,
                "calidez": self.calidez
            })
            
            return result["output"]
        except Exception as e:
            print(f"Error en el agente: {e}")
            return "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentar de nuevo?"
    
    def _format_conversation_history(self, conversation_history: List[dict]) -> str:
        """
        Formatea el historial de conversación para el contexto del agente.
        
        Args:
            conversation_history: Lista de mensajes con timestamp, role, text
            
        Returns:
            String formateado con el historial
        """
        if not conversation_history:
            return "No hay historial de conversación reciente."
        
        formatted_lines = ["Historial de conversación reciente:"]
        for msg in conversation_history:
            role_label = "Usuario" if msg['role'] == 'user' else "Asistente"
            timestamp = msg['timestamp']
            formatted_lines.append(f"[{timestamp}] {role_label}: {msg['text']}")
        
        return "\n".join(formatted_lines)