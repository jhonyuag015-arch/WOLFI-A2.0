# PROYECTO: TLAHUACBOT
# Arma el CONTEXTO que se le manda a Llama.
#
# Entre menos texto reciba Llama, mas rapido contesta. Por eso solo se
# incluye lo que pide la pregunta: el tema detectado (estudios, trabajo,
# modalidad...) de las carreras detectadas, sin repetir datos.

from bot.carreras import CARRERAS
from bot.datos import INSTITUCIONAL, datos_json
from bot.motor import TEMAS_POR_CARRERA, respuesta_carrera
from configuracion import MAX_CARACTERES_CONTEXTO, MAX_CARRERAS_CONTEXTO


# Nombre con el que se presenta cada tema dentro del contexto.
ETIQUETAS = {
    "estudios": "Qué se estudia",
    "trabajo": "Campo laboral",
    "modalidad": "Modalidad y duración",
    "duracion": "Modalidad y duración",
    "perfil_ingreso": "Perfil de ingreso",
    "perfil_egreso": "Perfil de egreso",
    "objetivo": "Objetivo",
}

# Un dato corto extra que complementa a algunos temas: (etiqueta, campo, origen).
EXTRAS = {
    "estudios": ("Áreas de formación", "areas_de_formacion_resumen", "inst"),
    "trabajo": ("Qué hace un egresado", "que_hace", "fila"),
}

# Si la pregunta es de una carrera pero sin tema claro, damos la ficha basica.
TEMAS_FICHA = ("estudios", "trabajo", "modalidad")

# Intenciones generales del Tec: su respuesta oficial tambien va al contexto.
INTENCIONES_GENERALES = {"oferta_educativa", "modalidades", "duracion", "admision"}


def como_texto(valor):
    # Convierte listas en texto separado por comas.
    if isinstance(valor, list):
        return ", ".join(str(v) for v in valor)
    return str(valor)


def bloque_carrera(clave, tema):
    # Lo que sabemos de UNA carrera para el tema que se pregunta.
    inst = INSTITUCIONAL.get(clave, {})
    fila = datos_json(clave) or {}

    basicos = [
        ("Título", inst.get("titulo_otorgado")),
        ("Modalidad", inst.get("modalidad") or fila.get("modalidad")),
        ("Semestres", inst.get("duracion_semestres") or fila.get("duracion_semestres")),
        ("Créditos", inst.get("creditos")),
    ]
    cabecera = " | ".join(f"{e}: {como_texto(v)}" for e, v in basicos if v)
    lineas = [f"CARRERA: {CARRERAS[clave]['nombre']}" + (f" | {cabecera}" if cabecera else "")]

    temas = (tema,) if tema in TEMAS_POR_CARRERA else TEMAS_FICHA
    for t in temas:
        texto, _ = respuesta_carrera(clave, t)
        if texto:
            lineas.append(f"{ETIQUETAS[t]}: {texto}")

        if t in EXTRAS:
            etiqueta, campo, origen = EXTRAS[t]
            valor = (inst if origen == "inst" else fila).get(campo)
            if valor:
                lineas.append(f"{etiqueta}: {como_texto(valor)}")

    return "\n".join(lineas)


def resumen_carreras():
    # Lista corta de carreras (para cuando no se menciona ninguna).
    lineas = ["CARRERAS DEL TECNOLÓGICO:"]
    for clave, datos in CARRERAS.items():
        inst = INSTITUCIONAL.get(clave, {})
        extra = [str(inst[c]) for c in ("modalidad", "duracion_semestres") if inst.get(c)]
        lineas.append("- " + datos["nombre"] + (f" ({', '.join(extra)})" if extra else ""))
    return "\n".join(lineas)


def construir_contexto(resultado):
    # Recibe lo que devolvio el motor (ya con la carrera heredada, si aplica).
    carreras = resultado.get("carreras", [])
    tema = resultado.get("tema", "")
    bloques = []

    if carreras:
        bloques += [bloque_carrera(c, tema) for c in carreras[:MAX_CARRERAS_CONTEXTO]]
    elif resultado["intencion"] not in INTENCIONES_GENERALES:
        bloques.append(resumen_carreras())

    if resultado["intencion"] in INTENCIONES_GENERALES:
        bloques.append("INFORMACIÓN OFICIAL DEL TEC: " + resultado["respuesta"])

    # Corte de seguridad: si el contexto se pasa del limite, Ollama
    # recortaria el inicio del mensaje (incluido el prompt de sistema).
    return "\n\n".join(bloques)[:MAX_CARACTERES_CONTEXTO]
