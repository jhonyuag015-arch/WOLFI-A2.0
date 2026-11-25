# Capa de inteligencia artificial en la nube mediante Groq.
# Mantiene la misma interfaz que conversacion.py espera del antiguo Ollama.

import json
import re

import requests

import configuracion as cfg


SISTEMA = (
    "Eres TláhuacBot, el asistente virtual del Tecnológico de Tláhuac II "
    "(TecNM). Resuelves dudas de aspirantes y estudiantes sobre carreras, "
    "materias, campo laboral, modalidad, duración y admisión.\n"
    "Reglas:\n"
    "1. Los datos propios del Tec (duración, modalidad, créditos, título, "
    "objetivo, perfiles y carreras) salen SOLO del CONTEXTO. No los inventes.\n"
    "2. Puedes complementar con conocimiento general de la disciplina, "
    "aclarando que el plan oficial debe confirmarse en el Tec.\n"
    "3. Nunca inventes costos, becas, fechas, teléfonos, direcciones, "
    "requisitos ni materias oficiales. Si no está en el CONTEXTO, di que "
    "no tienes el dato y recomienda consultarlo con el Tecnológico.\n"
    "4. Recuerda la conversación: 'esa carrera' o 'y cuánto dura' se refiere "
    "a la carrera de la que venían hablando.\n"
    "5. Si la pregunta no tiene relación con el Tec o elegir carrera, "
    "explica amablemente que tu función es orientar sobre el Tecnológico.\n"
    "6. Responde en español cercano y amable, máximo 4 oraciones. Texto "
    "claro y natural, sin encabezados innecesarios ni emojis."
)

_sesion = requests.Session()


class ErrorLlama(Exception):
    """La API de IA no está disponible o falló durante la respuesta."""
    pass


def generar(pregunta, contexto, historial):
    """Genera texto progresivamente usando el endpoint compatible de Groq."""
    if not cfg.GROQ_API_KEY:
        raise ErrorLlama("Falta configurar GROQ_API_KEY en el servidor")

    mensajes = [{"role": "system", "content": SISTEMA}]
    mensajes += historial[-cfg.MAX_HISTORIAL:]
    mensajes.append({
        "role": "user",
        "content": f"CONTEXTO OFICIAL:\n{contexto}\n\nPREGUNTA: {pregunta}",
    })

    carga = {
        "model": cfg.MODELO_IA,
        "messages": mensajes,
        "stream": True,
        **cfg.OPCIONES,
    }
    cabeceras = {
        "Authorization": f"Bearer {cfg.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with _sesion.post(
            cfg.GROQ_URL,
            headers=cabeceras,
            json=carga,
            stream=True,
            timeout=(cfg.TIMEOUT_CONEXION, cfg.TIMEOUT_RESPUESTA),
        ) as respuesta:
            if respuesta.status_code == 401:
                raise ErrorLlama("La clave de Groq no es válida")
            if respuesta.status_code == 429:
                raise ErrorLlama("Se alcanzó el límite temporal de solicitudes")
            respuesta.raise_for_status()
            for linea in respuesta.iter_lines(decode_unicode=False):
                if not linea:
                    continue

                if isinstance(linea, bytes):
                    linea = linea.decode("utf-8")

                if not linea.startswith(b"data:") and not linea.startswith("data:"):
                    continue

                contenido = linea[5:].strip()
                if contenido == "[DONE]":
                    return
                try:
                    dato = json.loads(contenido)
                except json.JSONDecodeError:
                    continue
                elecciones = dato.get("choices", [])
                if not elecciones:
                    continue
                delta = elecciones[0].get("delta", {})
                trozo = delta.get("content") or ""
                if trozo:
                    yield trozo
    except ErrorLlama:
        raise
    except (requests.RequestException, ValueError) as error:
        raise ErrorLlama(str(error)) from error


def limpiar_trozo(trozo):
    return re.sub(r"[*_`#]+", "", trozo)


def limpiar(texto):
    texto = limpiar_trozo(texto)
    texto = re.sub(r"^\s*[-•]\s+", "", texto, flags=re.MULTILINE).strip()
    if texto and texto[-1] not in ".!?…":
        corte = max(texto.rfind(c) for c in ".!?")
        if corte > len(texto) // 2:
            texto = texto[:corte + 1]
    return texto


def calentar():
    # Groq aloja el modelo: no es necesario descargarlo ni calentarlo en Render.
    return None
