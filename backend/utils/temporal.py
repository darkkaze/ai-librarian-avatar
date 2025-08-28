from typing import Any, Dict
from db.models import DatabaseManager, MessageRole


async def recuperar_conversacion(db_manager: DatabaseManager, message: str) -> list:
    """Recupera la conversación previa de las últimas 12 horas"""
    return db_manager.get_recent_conversation(hours=12, limit=10)


async def guardar_conversacion(db_manager: DatabaseManager, message: str, response: str):
    """Guarda tanto el mensaje del usuario como la respuesta del agente"""
    db_manager.save_message(message, MessageRole.USER)
    db_manager.save_message(response, MessageRole.AGENT)


async def text_to_speech(agent_response: str) -> Dict[str, Any]:
    """Genera el audio TTS (placeholder)"""
    # TODO: Implementar TTS real
    return {
        "audio_url": "/voice/output.wav",
        "type": "audio"
    }


async def visemas_choice(agent_response: str, speech_data: Dict[str, Any]) -> Dict[str, Any]:
    """Genera visemas basados en el audio (placeholder)"""
    # TODO: Implementar generación real de visemas con Librosa
    return {
        "visemas": [
            {"visema": "neutral", "tiempo": 0.0},
            {"visema": "aa", "tiempo": 0.5},
            {"visema": "neutral", "tiempo": 1.0}
        ],
        "type": "visemas"
    }


async def expression_choice(agent_response: str) -> Dict[str, Any]:
    """Selecciona expresiones basadas en la respuesta del agente (placeholder)"""
    # TODO: Implementar selección con IA
    return {
        "expresiones": [
            {"expresion": "neutral", "tiempo": 0.0, "intensidad": 1.0}
        ],
        "type": "expressions"
    }


async def animation_choice(agent_response: str) -> Dict[str, Any]:
    """Selecciona animaciones basadas en la respuesta del agente (placeholder)"""
    # TODO: Implementar selección con IA
    return {
        "animaciones": [
            {"animation": "idle", "tiempo": 0.0}
        ],
        "type": "animations"
    }