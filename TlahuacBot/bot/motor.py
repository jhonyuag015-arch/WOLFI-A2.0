# PROYECTO: TLAHUACBOT
# Motor del chatbot: con la carrera y el tema busca la respuesta exacta
# en el dataset. Es el respaldo cuando Llama no esta disponible.

from bot.carreras import CARRERAS, detectar_carreras
from bot.consultas import UMBRAL_CONSULTA_ALTO, buscar_consulta
from bot.datos import datos_json, texto_de
from bot.temas import CHARLA, RELLENO, clasificar_tema, quitar_charla
from bot.texto import normalizar


# ----------------------------------------------------------------------
# BUSQUEDA DE RESPUESTAS
# ----------------------------------------------------------------------

AYUDA = (
    "No encontré una respuesta confiable a eso. Puedes preguntarme sobre "
    "las carreras del Tec (qué se estudia, campo laboral, modalidad, "
    "duración, perfil de ingreso) o sobre el proceso de admisión."
)


def respuesta_carrera(clave, tema):
    # Devuelve (texto, intencion) para una carrera y un tema.
    # Primero busca en el dataset; si no esta, usa carreras.json.
    nombre = CARRERAS[clave]["nombre"]
    fila = datos_json(clave)

    # Temas que el dataset resuelve directamente con "<carrera>_<tema>".
    directos = {
        "estudios": f"{clave}_estudios",
        "trabajo": f"{clave}_trabajo",
        "modalidad": f"{clave}_modalidad",
        "duracion": f"{clave}_modalidad",   # esa respuesta ya incluye la duracion
        "perfil_ingreso": f"{clave}_perfil_ingreso",
        "objetivo": f"objetivo_{clave}",
        "perfil_egreso": f"perfil_egreso_{clave}",
    }

    intencion = directos[tema]
    texto = texto_de(intencion)
    if texto:
        return texto, intencion

    # Respaldo con carreras.json.
    if fila:
        if tema == "objetivo":
            return f"Objetivo de {nombre}: {fila['objetivo']}", intencion + "*"
        if tema == "perfil_egreso":
            return f"Un egresado de {nombre}: {fila['que_hace']}", intencion + "*"

    return None, intencion


def ficha(clave):
    # Resumen general de una carrera: que se estudia, donde se trabaja y modalidad.
    partes = [CARRERAS[clave]["nombre"]]
    for tema in ("estudios", "trabajo", "modalidad"):
        texto, _ = respuesta_carrera(clave, tema)
        if texto:
            partes.append(texto)
    return "\n\n".join(partes), f"ficha_{clave}"


def lista_de_carreras():
    return ", ".join(d["nombre"] for d in CARRERAS.values())


def resultado(respuesta, intencion, carreras=(), tema="", confianza=0.0):
    # Formato de salida del motor (lo usan la web y la evaluacion).
    return {
        "respuesta": respuesta,
        "intencion": intencion,
        "carreras": list(carreras),
        "tema": tema,
        "confianza": round(confianza, 2),
    }


# Temas que necesitan una carrera para poder contestarse.
TEMAS_POR_CARRERA = {
    "estudios", "trabajo", "modalidad", "duracion",
    "perfil_ingreso", "perfil_egreso", "objetivo",
}

# Maximo de carreras que contestamos en un mismo mensaje.
MAX_CARRERAS = 3


def responder(pregunta):
    # Funcion principal: recibe el texto del usuario y devuelve un diccionario.
    texto = normalizar(pregunta)

    if not texto:
        return resultado(AYUDA, "vacio")

    # Paso 1: quitamos la charla (hola, gracias...).
    texto, charla = quitar_charla(texto)
    texto = " ".join(t for t in texto.split() if t not in RELLENO)

    # Si solo era charla, contestamos la charla.
    if not texto:
        tipo = charla[0] if charla else "saludo"
        return resultado(CHARLA[tipo]["respuesta"], tipo)

    # Paso 2: detectamos carrera(s) y tema.
    carreras = detectar_carreras(texto)
    tema, confianza = clasificar_tema(texto)

    # Consulta general del Tec (admision, costos, becas, servicios, tramites).
    # Si la coincidencia es casi exacta gana incluso con una carrera mencionada.
    consulta, similitud = buscar_consulta(texto)
    if consulta and similitud >= UMBRAL_CONSULTA_ALTO:
        return resultado(texto_de(consulta), consulta, carreras, "consulta", similitud)

    # Caso A: hay carrera(s) y el tema depende de la carrera.
    if carreras and tema in TEMAS_POR_CARRERA:
        partes = []
        intenciones = []
        for clave in carreras[:MAX_CARRERAS]:
            respuesta, intencion = respuesta_carrera(clave, tema)
            if respuesta:
                if len(carreras) > 1:
                    respuesta = CARRERAS[clave]["nombre"] + ":\n" + respuesta
                partes.append(respuesta)
                intenciones.append(intencion)
        if partes:
            return resultado(
                "\n\n".join(partes), "+".join(intenciones),
                carreras, tema, confianza,
            )

    # Caso A2: consulta general que NO depende de la carrera.
    if consulta:
        return resultado(texto_de(consulta), consulta, carreras, "consulta", similitud)

    # Caso B: hay carrera pero no entendimos el tema -> ficha general.
    if carreras and tema in ("desconocido", "oferta", "general"):
        if len(carreras) == 1:
            texto_ficha, intencion = ficha(carreras[0])
            return resultado(texto_ficha, intencion, carreras, tema, confianza)
        return resultado(
            "Mencionas varias carreras. Pregúntame por una a la vez, o dime "
            "qué quieres saber de ellas: qué se estudia, campo laboral, "
            "modalidad o duración.",
            "varias_carreras", carreras, tema, confianza,
        )

    # Caso C: temas generales (no dependen de una carrera).
    if tema == "admision":
        return resultado(texto_de("admision"), "admision", carreras, tema, confianza)

    if tema == "oferta":
        return resultado(texto_de("oferta_educativa"), "oferta_educativa",
                         carreras, tema, confianza)

    if tema == "modalidad":
        return resultado(texto_de("modalidades"), "modalidades",
                         carreras, tema, confianza)

    if tema == "duracion":
        return resultado(texto_de("duracion"), "duracion",
                         carreras, tema, confianza)

    if tema == "fuera_alcance":
        return resultado(texto_de("sin_respuesta"), "sin_respuesta",
                         carreras, tema, confianza)

    # Caso D: el tema necesita carrera y no la mencionaron.
    if tema in TEMAS_POR_CARRERA:
        return resultado(
            "¿De cuál carrera quieres saber? Tengo información de: "
            + lista_de_carreras() + ".",
            "pedir_carrera", carreras, tema, confianza,
        )

    # Caso E: no entendimos la pregunta. Si venia con charla
    # ("muchas gracias por todo"), contestamos la charla.
    if charla:
        return resultado(CHARLA[charla[0]]["respuesta"], charla[0])

    return resultado(AYUDA, "no_entendido", carreras, tema, confianza)
