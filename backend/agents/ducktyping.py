from typing import Protocol


class AgentProtocol(Protocol):
    """
    Protocol defining the interface expected for an Agent.

    Any class implementing this protocol must have:
    - process_message(message: str) -> str: Process user input and return response
    """

    async def process_message(self, message: str) -> str:
        """
        Process a user message and return agent's response.

        Args:
            message: User's input message

        Returns:
            Agent's text response
        """
        ...
