# PROYECTO: TLAHUACBOT
# Configuracion central: todo lo que quieras ajustar esta aqui.

import os
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
CARPETA_DATOS = CARPETA / "Datos"


# ----------------------------------------------------------------------
# IA EN LA NUBE (Groq)
# ----------------------------------------------------------------------

# La clave se configura en Render > Environment como GROQ_API_KEY.
# Nunca escribas la clave directamente en este archivo ni la subas a GitHub.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO_IA = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

# Si no hay clave, WOLFI-A/TláhuacBot sigue funcionando con el motor local.
USAR_IA = bool(GROQ_API_KEY)

TIMEOUT_CONEXION = 15
TIMEOUT_RESPUESTA = 90

OPCIONES = {
    "temperature": 0.5,
    "max_completion_tokens": 280,
}


# ----------------------------------------------------------------------
# CONVERSACION
# ----------------------------------------------------------------------

MAX_CARACTERES_PREGUNTA = 500

# Memoria: cuantos mensajes recuerda Llama y de que largo maximo.
MAX_HISTORIAL = 4
MAX_CARACTERES_HISTORIAL = 350

# Datos de carrera que se le pasan a Llama (menos datos = respuesta mas rapida).
MAX_CARRERAS_CONTEXTO = 3
MAX_CARACTERES_CONTEXTO = 2200

# Respuestas guardadas para preguntas repetidas (botones, tarjetas, demos).
TAMANO_CACHE = 64


# ----------------------------------------------------------------------
# SERVIDOR
# ----------------------------------------------------------------------

# Pon TLAHUACBOT_DEBUG=1 en el entorno para modo desarrollo.
DEBUG = os.environ.get("TLAHUACBOT_DEBUG", "0") == "1"
