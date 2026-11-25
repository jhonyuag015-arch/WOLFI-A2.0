# PROYECTO: TLAHUACBOT
# Carreras del Tec, sus alias y deteccion de la carrera en un texto.

from difflib import get_close_matches

from bot.texto import contiene


# CARRERAS Y SUS ALIAS
# ----------------------------------------------------------------------
# Para agregar un apodo nuevo de una carrera, basta con escribirlo en
# su lista de alias (sin acentos y en minusculas).

CARRERAS = {
    "mecanica": {
        "nombre": "Ingeniería Mecánica",
        "alias": ["ingenieria mecanica", "mecanica", "mecanico", "mecanicos"],
    },
    "logistica": {
        "nombre": "Ingeniería en Logística",
        "alias": ["ingenieria en logistica", "logistica"],
    },
    "ti": {
        "nombre": "Ingeniería en Tecnologías de la Información",
        "alias": [
            "tecnologias de la informacion y comunicaciones",
            "tecnologias de la informacion",
            "tecnologias de informacion",
            "itic", "tics", "tic", "ti",
        ],
    },
    "sistemas": {
        "nombre": "Ingeniería en Sistemas Computacionales",
        "alias": ["sistemas computacionales", "ingenieria en sistemas",
                  "sistemas", "isc"],
    },
    "gestion": {
        "nombre": "Ingeniería en Gestión Empresarial",
        "alias": ["gestion empresarial", "gestion", "empresarial"],
    },
    "turismo": {
        "nombre": "Licenciatura en Turismo",
        "alias": ["licenciatura en turismo", "turismo", "turistico"],
    },
}

# Palabras de una sola palabra que usamos para corregir errores de dedo.
ALIAS_SIMPLES = {}
for _clave, _datos in CARRERAS.items():
    for _alias in _datos["alias"]:
        if " " not in _alias and len(_alias) >= 6:
            ALIAS_SIMPLES[_alias] = _clave

# Todos los alias, del mas largo al mas corto (se usa al limpiar preguntas).
ALIAS_TODOS = sorted(
    [alias for datos in CARRERAS.values() for alias in datos["alias"]],
    key=len,
    reverse=True,
)

# Palabras antes de "ti" que indican que es el pronombre ("para ti"),
# no la carrera de Tecnologias de la Informacion.
ANTES_DE_TI_NO_CARRERA = {"para", "por", "a", "sin", "contigo"}


def detectar_carreras(texto):
    # Devuelve la lista de claves de carrera mencionadas en el texto.
    tokens = texto.split()
    encontradas = []

    for clave, datos in CARRERAS.items():
        for alias in datos["alias"]:

            if not contiene(texto, alias):
                continue

            # Caso especial: "ti" puede ser el pronombre.
            if alias == "ti":
                posiciones = [i for i, t in enumerate(tokens) if t == "ti"]
                es_carrera = any(
                    i == 0 or tokens[i - 1] not in ANTES_DE_TI_NO_CARRERA
                    for i in posiciones
                )
                if not es_carrera:
                    continue

            encontradas.append(clave)
            break

    # Si no encontramos nada, intentamos corregir errores de dedo
    # (por ejemplo "logistca" en lugar de "logistica").
    if not encontradas:
        for token in tokens:
            if len(token) < 6:
                continue
            parecido = get_close_matches(
                token, list(ALIAS_SIMPLES), n=1, cutoff=0.82
            )
            if parecido and ALIAS_SIMPLES[parecido[0]] not in encontradas:
                encontradas.append(ALIAS_SIMPLES[parecido[0]])

    return encontradas


