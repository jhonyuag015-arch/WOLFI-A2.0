# PROYECTO: TLAHUACBOT
# Carga de los archivos JSON. Se lee UNA sola vez, al arrancar.

import json

from bot.carreras import CARRERAS
from bot.texto import normalizar
from configuracion import CARPETA_DATOS


def _leer(nombre):
    with (CARPETA_DATOS / nombre).open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


# Preguntas y respuestas, indexadas por intencion (por ejemplo "mecanica_trabajo").
REGISTROS = _leer("dataset_preguntas.json")["registros"]
INDICE = {registro["intencion"]: registro for registro in REGISTROS}

# carreras.json, indexado por nombre normalizado.
_CARRERAS_JSON = {normalizar(c["nombre"]): c for c in _leer("carreras.json")}

# dataset_institucional.json, indexado por clave de carrera (mecanica, ti...).
INSTITUCIONAL = {c["id"]: c for c in _leer("dataset_institucional.json")["carreras"]}


def texto_de(intencion):
    # Devuelve la respuesta de un registro del dataset, o None si no existe.
    registro = INDICE.get(intencion)
    return registro["respuesta"] if registro else None


def datos_json(clave):
    # Datos de la carrera en carreras.json, o None si no esta.
    return _CARRERAS_JSON.get(normalizar(CARRERAS[clave]["nombre"]))
