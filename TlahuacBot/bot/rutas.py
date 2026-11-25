# PROYECTO: TLAHUACBOT
# Rutas de la pagina web. Solo reciben, validan y entregan; la logica
# vive en conversacion.py.

import json

from flask import Blueprint, Response, jsonify, render_template, request, stream_with_context

import configuracion as cfg
from bot.conversacion import conversar


bp = Blueprint("chat", __name__)


def leer_peticion():
    # Devuelve (pregunta, historial, error). Si hay error, es una respuesta lista.
    datos = request.get_json(silent=True) or {}
    pregunta = datos.get("mensaje", "")

    if not isinstance(pregunta, str):
        return None, None, (jsonify({"respuesta": "La pregunta no es válida."}), 400)

    if len(pregunta) > cfg.MAX_CARACTERES_PREGUNTA:
        return None, None, (jsonify({
            "respuesta": "Tu mensaje es muy largo. Intenta con una pregunta más corta."
        }), 400)

    return pregunta, datos.get("historial"), None


@bp.route("/")
def inicio():
    return render_template("index.html")


@bp.route("/chat", methods=["POST"])
def chat():
    # Respuesta completa de una vez (la pagina usa /chat/stream; esta ruta
    # queda por compatibilidad y para pruebas).
    pregunta, historial, error = leer_peticion()
    if error:
        return error

    final = {}
    for tipo, dato in conversar(pregunta, historial):
        if tipo == "fin":
            final = dato
    return jsonify(final)


@bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    # Respuesta por partes: una linea JSON por evento.
    #   {"t": "texto..."}                      -> pedazo de la respuesta
    #   {"fin": true, "respuesta": "...", ...} -> respuesta final y limpia
    pregunta, historial, error = leer_peticion()
    if error:
        return error

    def eventos():
        for tipo, dato in conversar(pregunta, historial):
            linea = {"t": dato} if tipo == "texto" else {"fin": True, **dato}
            yield json.dumps(linea, ensure_ascii=False) + "\n"

    return Response(
        stream_with_context(eventos()),
        mimetype="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
