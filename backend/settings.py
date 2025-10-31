import os

WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8765

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PHONEME_TO_VISEME = {
    # Vocales principales
    'a': 'aa',      # Boca abierta amplia
    'e': 'ee',      # Sonrisa, boca semi-abierta
    'i': 'ih',      # Sonrisa, boca cerrada
    'o': 'oh',      # Boca redonda
    'u': 'ou',      # Boca muy redonda, labios fruncidos

    # Consonantes -> mapear a la vocal más cercana o neutral
    'p': 'neutral', 'b': 'neutral', 'm': 'neutral',  # Labiales
    'f': 'ee', 'v': 'ee',                            # Fricativas -> sonrisa
    't': 'ih', 'd': 'ih', 'n': 'ih', 'l': 'ih',      # Alveolares -> ih
    's': 'ih', 'z': 'ih',                            # Fricativas -> ih
    'k': 'aa', 'g': 'aa',                            # Velares -> aa
    'r': 'aa',                                       # Vibrante -> aa
    'ch': 'ih', 'y': 'ih',                           # Palatales -> ih
    'h': 'aa',                                       # Aspirada -> aa
    'j': 'aa',                                       # J española -> aa
    'ñ': 'ih',                                       # Ñ -> ih

    # Silencio
    'sil': 'neutral'  # Posición neutral/descanso
}