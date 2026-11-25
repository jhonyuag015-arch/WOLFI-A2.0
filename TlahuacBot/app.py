
# PROYECTO: TLAHUACBOT
# Asistente virtual del Tecnológico de Tláhuac II.

from flask import Flask

import configuracion as cfg
from bot.llm import calentar
from bot.rutas import bp


def crear_app():
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.register_blueprint(bp)
    return app


app = crear_app()


if __name__ == "__main__":
    calentar()
    app.run(debug=cfg.DEBUG, use_reloader=False)

