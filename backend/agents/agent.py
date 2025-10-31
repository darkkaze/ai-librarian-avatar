"""
Librera ReAct Agent - Main agent implementation.

Orchestrates the complete ReAct workflow for library book assistance.
Uses LangGraph to manage the reasoning and acting cycle.
"""
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from agents.state import InputUserState
from agents.prompts import (
    SYSTEM_PROMPT,
    REFLECT_PROMPT,
    ACT_PROMPT,
    DECISION_PROMPT,
    HUMANIZE_PROMPT
)
from agents.tools import ALL_TOOLS


class LibreraAgent:
    """
    Librera AI ReAct Agent.

    Main agent class that orchestrates the complete workflow for
    assisting users in finding books. Model-agnostic: works with any
    LangChain-compatible model that supports tool calling.

    The workflow follows this pattern:
    start → reflect → act → [decision] → tools → reflect (loop)
                              ↓
                            final → END
    """

    def __init__(self, model, tools=None):
        """
        Initialize Librera ReAct Agent.

        Args:
            model: LangChain model instance with tool calling support.
                   Must be compatible with LangChain's bind_tools() method.
                   Example: ChatAnthropic(model='claude-haiku-4-5-20250929')
            tools: Optional list of tools. If not provided, uses ALL_TOOLS (3 tools)

        Raises:
            ValueError: If model is None
        """
        if model is None:
            raise ValueError(
                "Model is required. Please provide a LangChain-compatible model.\n"
                "Example: ChatAnthropic(model='claude-haiku-4-5-20250929')"
            )

        self.model = model

        # Initialize tools (use ALL_TOOLS by default)
        if tools is None:
            tools = ALL_TOOLS

        self.tools = tools
        self.model_with_tools = self.model.bind_tools(tools) if tools else self.model

        self.tool_node = ToolNode(tools) if tools else None

        self.workflow = self._build_workflow()
        self.workflow.name = "librera_react_agent"

    @property
    def agent(self):
        """Get compiled workflow graph."""
        return self.workflow

    def _start_node(self, state: InputUserState):
        """
        Start node - Initialize with system prompt and user input.

        Loads conversation history from last 3 minutes from database.
        """
        print("\n[ 🚀 INICIANDO LIBRERA AGENT ]")

        from db.models import SessionLocal
        from db.repository import ConversationRepository

        # Load recent conversation history (last 3 minutes)
        conversation_history = ""
        with SessionLocal() as session:
            repo = ConversationRepository(session)
            recent_messages = repo.get_recent(minutes=3)

            print(f"DEBUG - Mensajes recientes cargados: {len(recent_messages)}")
            if recent_messages:
                conversation_history = "\n📜 RECENT CONVERSATION HISTORY:\n"
                for msg in recent_messages:
                    role_emoji = "👤" if msg["role"] == "human" else "🤖"
                    conversation_history += f"{role_emoji} {msg['role'].upper()}: {msg['message']}\n"
                    print(f"  - {msg['role']}: {msg['message'][:100]}")
            else:
                conversation_history = "\n📜 No recent conversation history."

            print(f"DEBUG - Historial formateado: {conversation_history[:300]}...")

        system_message = SystemMessage(content=SYSTEM_PROMPT.format(
            conversation_history=conversation_history
        ))
        user_message = HumanMessage(content=state["input_user"])

        return {
            "messages": [system_message, user_message],
        }

    def _plan_and_search_node(self, state: InputUserState):
        """Plan and execute initial search based on user query."""
        print("\n[ 🔍 PLANIFICANDO Y BUSCANDO ]")

        # Get user query
        user_query = state.get("input_user", "")

        # Debug: Check messages in state
        print(f"DEBUG - Número de mensajes en state: {len(state['messages'])}")
        if state['messages']:
            first_msg = state['messages'][0]
            print(f"DEBUG - Primer mensaje (system): {first_msg.content[:300] if hasattr(first_msg, 'content') else 'NO CONTENT'}...")

        prompt = f"""La pregunta del usuario es: "{user_query}"

CRÍTICO: DEBES llamar a UNA herramienta. NO puedes responder sin llamar una herramienta primero.

Analiza la pregunta:

0. REFERENCIAS CONTEXTUALES: Si usa palabras como "ese libro", "ese autor", "el que dijiste", "de qué trata":
   → PRIMERO mira el HISTORIAL DE CONVERSACIÓN arriba
   → Identifica el libro/autor específico mencionado recientemente
   → Luego USA: search_book_by_title con el nombre exacto del libro identificado
   → Ejemplo: Si mencionaste "American Assassin" y pregunta "de qué trata ese libro" → search_book_by_title(title="American Assassin")

1. Si menciona un TÍTULO ESPECÍFICO de libro (ej: "tienes Harry Potter", "busco Cien años de soledad"):
   → USA: search_book_by_title

2. Si pide RECOMENDACIONES o describe una NECESIDAD (ej: "algo para mi hijo", "quiero algo de aventuras", "libros para niños"):
   → USA: search_books_by_criteria con el query apropiado

3. Si menciona AUTOR o GÉNERO (ej: "libros de García Márquez", "algo de ciencia ficción"):
   → USA: search_books_by_criteria

EJEMPLOS:
- "de qué trata ese libro" + historial muestra "American Assassin" → search_book_by_title(title="American Assassin")
- "me recomiendas algo para mi hijo" → search_books_by_criteria(query="libros infantiles para niños")
- "quiero algo de aventuras" → search_books_by_criteria(query="libros de aventuras")
- "tienes libros de Stephen King" → search_books_by_criteria(author="Stephen King")
- "tienes algo similar a Isabel Allende" → recommend_by_author(author_name="Isabel Allende")
- "algo parecido a Harry Potter" → recommend_similar_books(reference="Harry Potter")

IMPORTANTE sobre recomendaciones:
- Si pide "similar a [AUTOR]" → usa recommend_by_author
- Si pide "similar a [LIBRO]" → usa recommend_similar_books

NO RESPONDAS CON TEXTO. LLAMA LA HERRAMIENTA AHORA."""

        mode_message = HumanMessage(content=prompt)
        messages = state['messages']
        response = self.model_with_tools.invoke(messages + [mode_message])

        print(f"DEBUG - Response type: {type(response)}")
        print(f"DEBUG - Has tool_calls: {hasattr(response, 'tool_calls')}")
        if hasattr(response, 'tool_calls'):
            print(f"DEBUG - Tool calls: {response.tool_calls}")
            if response.tool_calls:
                tool_names = [tc['name'] for tc in response.tool_calls]
                print(f"🔧 Ejecutando: {', '.join(tool_names)}")

        return {"messages": [response]}

    def _check_and_recommend_node(self, state: InputUserState):
        """Check if we found results. If not, recommend similar books."""
        print("\n[ 🎯 VERIFICANDO RESULTADOS ]")

        # Check if we have tool results in messages
        tool_messages = [msg for msg in state["messages"] if hasattr(msg, 'type') and msg.type == 'tool']

        if not tool_messages:
            print("→ Sin resultados de herramientas")
            return {"messages": []}

        # Debug: Print all tool results
        print(f"DEBUG - Total de resultados de herramientas: {len(tool_messages)}")
        for i, msg in enumerate(tool_messages):
            print(f"DEBUG - Tool result {i+1}: {msg.content[:200] if hasattr(msg, 'content') else 'NO CONTENT'}")

        # Get last tool result
        last_tool_result = tool_messages[-1]

        # Check if result is None or empty
        result_content = str(last_tool_result.content) if hasattr(last_tool_result, 'content') else ""

        if "None" in result_content or not result_content or result_content == "[]":
            print("→ No se encontró el libro, buscando recomendaciones...")

            # Get original user query
            user_query = state.get("input_user", "")

            # Call appropriate recommendation tool
            # Check if query is about an author or a book
            if any(word in user_query.lower() for word in ["autor", "autora", "escribió", "escribe"]):
                prompt = f"""El libro/autor buscado no se encontró. Usa recommend_by_author con el nombre del autor de la consulta: "{user_query}"

IMPORTANTE: Solo llama a recommend_by_author, no hagas nada más."""
            else:
                prompt = f"""El libro buscado no se encontró. Usa recommend_similar_books con la consulta original del usuario: "{user_query}"

IMPORTANTE: Solo llama a recommend_similar_books, no hagas nada más."""

            response = self.model_with_tools.invoke(state["messages"] + [HumanMessage(content=prompt)])

            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Llamando a recommend_similar_books")

            return {"messages": [response]}

        print("→ Libro encontrado, continuando...")
        return {"messages": []}

    def _format_voice_node(self, state: InputUserState):
        """Format final response for voice interface (very short)."""
        print("\n[ 🎙️ FORMATEANDO PARA VOZ ]")

        # Get all tool results
        tool_results = [msg for msg in state["messages"] if hasattr(msg, 'type') and msg.type == 'tool']

        if not tool_results:
            return {"messages": [AIMessage(content="No encontré información sobre ese libro.")]}

        # Create summary of all tool results
        results_summary = "\n".join([f"Resultado: {msg.content}" for msg in tool_results])

        print(f"🔍 DEBUG - Tool results:\n{results_summary}")

        prompt = f"""{HUMANIZE_PROMPT}

Información EXACTA de la base de datos:
{results_summary}

Pregunta original del usuario: {state.get('input_user', '')}

⚠️ REGLA CRÍTICA:
- Menciona SOLO los títulos y autores EXACTOS que aparecen arriba
- NO combines información de diferentes libros
- NO inventes autores o títulos
- Si un libro no tiene sinopsis (synopsis: ""), di "No tengo más detalles"

Crea una respuesta de VOZ CORTA (máximo 20 palabras) usando SOLO la información exacta de arriba."""

        response = self.model.invoke([HumanMessage(content=prompt)])

        print(f"📢 Respuesta final: {response.content}")

        return {"messages": [response]}

    def _route_after_plan(self, state: InputUserState) -> str:
        """Route after plan_and_search: execute tools or skip."""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "execute_search"
        return "check_results"

    def _route_after_check(self, state: InputUserState) -> str:
        """Route after check: execute recommend tools or format."""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "execute_recommend"
        return "format"

    def _build_workflow(self):
        """
        Build simplified workflow for book search.

        Flow: start → plan_and_search → [tools] → check_and_recommend → [tools?] → format_voice → END

        Returns:
            Compiled StateGraph workflow
        """
        workflow = StateGraph(InputUserState)

        # Add nodes
        workflow.add_node("start", self._start_node)
        workflow.add_node("plan_and_search", self._plan_and_search_node)
        workflow.add_node("execute_search", self.tool_node)
        workflow.add_node("check_results", self._check_and_recommend_node)
        workflow.add_node("execute_recommend", self.tool_node)
        workflow.add_node("format", self._format_voice_node)

        # Set entry
        workflow.set_entry_point("start")

        # Define edges
        workflow.add_edge("start", "plan_and_search")

        workflow.add_conditional_edges(
            "plan_and_search",
            self._route_after_plan,
            {
                "execute_search": "execute_search",
                "check_results": "check_results"
            }
        )

        workflow.add_edge("execute_search", "check_results")

        workflow.add_conditional_edges(
            "check_results",
            self._route_after_check,
            {
                "execute_recommend": "execute_recommend",
                "format": "format"
            }
        )

        workflow.add_edge("execute_recommend", "format")
        workflow.add_edge("format", END)

        return workflow.compile()

    async def process_message(self, message: str) -> str:
        """
        Process a user message and return agent's response.

        Implements AgentProtocol interface.

        Args:
            message: User's input message

        Returns:
            Agent's text response
        """
        result = await self.workflow.ainvoke({"input_user": message})
        final_message = result["messages"][-1]
        return final_message.content
