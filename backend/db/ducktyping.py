from typing import Protocol, List, Dict, Any


class DatabaseManagerProtocol(Protocol):
    """
    Protocol defining the interface expected for a DatabaseManager.

    Any class implementing this protocol must have:
    - save_conversation(user_message: str, agent_response: str) -> None: Persist conversation
    - retrieve_conversation(hours: int, limit: int) -> List[Dict[str, Any]]: Retrieve conversation history
    """

    async def save_conversation(self, user_message: str, agent_response: str) -> None:
        """
        Save a conversation exchange to persistent storage.

        Args:
            user_message: User's message
            agent_response: Agent's response
        """
        ...

    async def retrieve_conversation(self, hours: int = 12, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation history.

        Args:
            hours: Number of hours to look back
            limit: Maximum number of messages to retrieve

        Returns:
            List of conversation messages (chronologically ordered)
        """
        ...
