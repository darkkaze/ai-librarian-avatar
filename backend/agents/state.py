"""
State definition for Librera ReAct Agent.
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class InputUserState(TypedDict):
    """
    State schema for Librera ReAct Agent workflow.

    Attributes:
        messages: Sequence of LangChain messages (HumanMessage, AIMessage, SystemMessage, ToolMessage)
        input_user: User's input message text
        conversation_history: Optional formatted conversation history from last 3 minutes
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    input_user: str
    conversation_history: str
