# PROYECTO: TLAHUACBOT
# Une todas las capas: motor (carrera y tema) -> contexto -> Llama.
# Es un generador de eventos, asi la misma logica sirve para la respuesta
# por partes (/chat/stream) y para la respuesta completa (/chat).

from collections import OrderedDict
from threading import Lock

import configuracion as cfg
from bot import llm
from bot.carreras import detectar_carreras
from bot.consultas import es_consulta
from bot.contexto import construir_contexto
from bot.motor import responder
from bot.texto import normalizar


# Respuestas que NO necesitan a Llama (son fijas y mejor dejarlas asi).
# Ademas, TODA consulta general (admision, costos, becas, servicios y
# tramites, ver bot/consultas.py) se contesta solo con el motor: asi Llama
# no puede inventar ni cambiar costos, fechas, telefonos o requisitos.
SOLO_MOTOR = {
    "saludo", "gracias", "despedida", "vacio", "pedir_carrera", "sin_respuesta",
}

# Si la pregunta es de este tipo, NO heredamos la carrera de la charla anterior.
NO_HEREDAN_CARRERA = {
    "saludo", "gracias", "despedida", "vacio", "sin_respuesta",
    "oferta_educativa", "admision",
}


# ----------------------------------------------------------------------
# HISTORIAL (memoria de la conversacion)
# ----------------------------------------------------------------------

def limpiar_historial(valor):
    # La pagina manda los mensajes anteriores; revisamos que sean validos.
    if not isinstance(valor, list):
        return []

    limpio = []
    for item in valor[-cfg.MAX_HISTORIAL:]:
        if not isinstance(item, dict):
            continue
        rol = item.get("role")
        texto = item.get("content")
        if rol in ("user", "assistant") and isinstance(texto, str) and texto.strip():
            limpio.append({"role": rol, "content": texto[:cfg.MAX_CARACTERES_HISTORIAL]})
    return limpio


def con_carrera_heredada(resultado, historial):
    # Si no mencionaron carrera pero venian hablando de una, la heredamos
    # (asi funciona "y cuanto dura?" despues de preguntar por una carrera).
    if (resultado.get("carreras")
            or resultado["intencion"] in NO_HEREDAN_CARRERA
            or es_consulta(resultado["intencion"])):
        return resultado

    for mensaje in reversed(historial):
        if mensaje["role"] != "user":
            continue
        encontradas = detectar_carreras(normalizar(mensaje["content"]))
        if encontradas:
            return dict(resultado, carreras=encontradas, intencion="seguimiento")
    return resultado


# ----------------------------------------------------------------------
# CACHE de respuestas (solo preguntas sin historial)
# ----------------------------------------------------------------------

_cache = OrderedDict()
_candado = Lock()


def _cache_leer(clave):
    with _candado:
        if clave in _cache:
            _cache.move_to_end(clave)
            return _cache[clave]
    return None


def _cache_guardar(clave, texto):
    with _candado:
        _cache[clave] = texto
        _cache.move_to_end(clave)
        while len(_cache) > cfg.TAMANO_CACHE:
            _cache.popitem(last=False)


# ----------------------------------------------------------------------
# CONVERSACION
# ----------------------------------------------------------------------

def conversar(pregunta, historial):
    # Genera eventos: ("texto", pedazo) las veces que haga falta y, al final,
    # ("fin", {"respuesta", "intencion", "origen"}).
    historial = limpiar_historial(historial)
    resultado = con_carrera_heredada(responder(pregunta), historial)
    intencion = resultado["intencion"]
    base = resultado["respuesta"]

    def fin(texto, origen):
        return "fin", {"respuesta": texto, "intencion": intencion, "origen": origen}

    if not cfg.USAR_IA or intencion in SOLO_MOTOR or es_consulta(intencion):
        yield fin(base, "motor")
        return

    # Pregunta repetida y sin historial: no hace falta volver a preguntarle a Llama.
    clave = None if historial else normalizar(pregunta)
    guardada = _cache_leer(clave) if clave else None
    if guardada:
        yield fin(guardada, "cache")
        return

    partes = []
    try:
        for trozo in llm.generar(pregunta, construir_contexto(resultado), historial):
            partes.append(trozo)
            yield "texto", llm.limpiar_trozo(trozo)
    except llm.ErrorLlama:
        yield fin(base, "motor")
        return

    texto = llm.limpiar("".join(partes))
    if not texto:
        yield fin(base, "motor")
        return

    if clave:
        _cache_guardar(clave, texto)
    yield fin(texto, "llama")