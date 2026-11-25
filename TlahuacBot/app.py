# PROYECTO: TLAHUACBOT
# Asistente virtual del Tecnologico de Tlahuac II.
#
# Ejecuta:  python app.py
#
# Estructura:
#   configuracion.py     ajustes (modelo, limites, cache...)
#   bot/carreras.py      carreras y alias
#   bot/temas.py         charla basica y clasificador de temas (TF-IDF)
#   bot/motor.py         respuestas del dataset (respaldo sin Llama)
#   bot/contexto.py      datos que se le pasan a Llama
#   bot/llm.py           llamada a Ollama (streaming)
#   bot/conversacion.py  une todo: motor -> contexto -> Llama
#   bot/rutas.py         rutas web

from flask import Flask

import configuracion as cfg
from bot.llm import calentar
from bot.rutas import bp


def crear_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


app = crear_app()


if __name__ == "__main__":
    # Carga Llama en memoria desde el arranque (la primera pregunta ya no espera).
    calentar()

    # use_reloader=False: con el reloader Flask arranca todo dos veces.
    app.run(debug=cfg.DEBUG, use_reloader=False)
