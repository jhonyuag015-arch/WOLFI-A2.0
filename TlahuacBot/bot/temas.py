# PROYECTO: TLAHUACBOT
# Charla basica (hola, gracias...) y clasificador de TEMAS con Machine
# Learning: TF-IDF + similitud de coseno.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from bot.carreras import ALIAS_TODOS
from bot.texto import contiene, normalizar


# ----------------------------------------------------------------------
# CHARLA BASICA (saludos, gracias, despedidas)
# ----------------------------------------------------------------------

CHARLA = {
    "saludo": {
        "frases": ["buenos dias", "buenas tardes", "buenas noches", "buenas",
                   "hola", "holi", "hey", "saludos", "que tal"],
        "respuesta": (
            "¡Hola! Soy TláhuacBot, el asistente virtual del Tecnológico de "
            "Tláhuac II. Puedo ayudarte con las carreras, su campo laboral, "
            "modalidades, duración y el proceso de admisión."
        ),
    },
    "gracias": {
        "frases": ["muchas gracias", "mil gracias", "te agradezco", "gracias"],
        "respuesta": "¡De nada! Si tienes otra duda sobre el Tec, aquí estoy.",
    },
    "despedida": {
        "frases": ["hasta luego", "hasta pronto", "nos vemos", "adios",
                   "bye", "chao"],
        "respuesta": "¡Hasta luego! Mucho éxito.",
    },
}

# Frases de charla ordenadas de la mas larga a la mas corta, para que
# "buenas tardes" se quite antes que "buenas".
FRASES_CHARLA = sorted(
    [(frase, tipo) for tipo, d in CHARLA.items() for frase in d["frases"]],
    key=lambda x: len(x[0]),
    reverse=True,
)

# Palabras de relleno que no cuentan como una pregunta real.
RELLENO = {"ok", "vale", "va", "bueno", "pues", "por", "favor", "oye"}


def quitar_charla(texto):
    # Quita saludos/gracias/despedidas del texto.
    # Devuelve (texto sin charla, tipos de charla encontrados).
    encontrados = []

    for frase, tipo in FRASES_CHARLA:
        if contiene(texto, frase):
            texto = " ".join(f" {texto} ".replace(f" {frase} ", " ").split())
            if tipo not in encontrados:
                encontrados.append(tipo)

    return texto, encontrados


# ----------------------------------------------------------------------
# CLASIFICADOR DE TEMAS (Machine Learning con TF-IDF)
# ----------------------------------------------------------------------
# Cada tema tiene ejemplos de como lo preguntaria la gente.
# Entre mas ejemplos agregues, mejor entiende el bot.

EJEMPLOS_TEMA = {
    "estudios": [
        "que se estudia", "que materias se estudian", "que materias llevan",
        "de que trata", "que voy a aprender", "que aprendere",
        "que temas estudia", "que estudian", "que se ve en la carrera",
        "plan de estudios", "que llevan", "cuales son las materias",
        "que hace alguien que estudia", "en que consiste",
    ],
    "trabajo": [
        "donde puedo trabajar", "en que puedo trabajar", "campo laboral",
        "en que empresas puedo trabajar", "oportunidades de trabajo",
        "salida laboral", "de que trabajan los egresados", "empleo",
        "que puestos hay", "mercado laboral", "a que se dedica un egresado",
        "a que se dedica un ingeniero", "que hace un egresado",
        "que hace un ingeniero", "que actividades realiza un profesional",
        "donde trabaja un egresado",
        "campo de trabajo", "area de trabajo", "donde laboran",
        "en que se trabaja", "en que laboran los egresados",
    ],
    "modalidad": [
        "es presencial o en linea", "que modalidad tiene", "es presencial",
        "es en linea", "se puede estudiar en linea", "hay carreras en linea",
        "que carreras hay en linea", "carreras a distancia",
        "que puedo estudiar a distancia", "hay carreras virtuales",
        "modalidad", "es escolarizada", "es virtual", "es a distancia",
    ],
    "duracion": [
        "cuanto dura", "cuantos semestres", "cuantos semestres dura",
        "cuantos anos son", "cuantos anos dura", "duracion", "cuanto tiempo",
        "en cuanto tiempo termino", "cuantos semestres duran las carreras",
        "cuanto tarda", "en cuanto tiempo me recibo",
    ],
    "perfil_ingreso": [
        "perfil de ingreso", "que conocimientos necesito para entrar",
        "que habilidades se recomiendan", "que necesito para estudiar",
        "requisitos de ingreso", "requisitos para entrar",
        "que debo saber para entrar", "que perfil debo tener",
        "que se necesita para estudiar",
    ],
    "perfil_egreso": [
        "perfil de egreso", "que habilidades tendre al terminar",
        "que sabre hacer cuando termine", "que capacidades desarrolla",
        "que conocimientos obtiene un egresado", "como sale un egresado",
        "que competencias desarrolla",
    ],
    "objetivo": [
        "cual es el objetivo", "cual es la meta", "para que sirve estudiar",
        "que busca formar", "objetivo general", "cual es la finalidad",
        "para que sirve la carrera", "que busca la carrera",
    ],
    "admision": [
        "como me inscribo", "proceso de admision", "donde solicito ficha",
        "como entro al tec", "como ingreso", "inscripcion", "ficha de examen",
        "examen de admision", "convocatoria", "como puedo entrar",
        "fechas de inscripcion", "como me registro", "quiero inscribirme",
    ],
    "oferta": [
        "que carreras hay", "que carreras ofrece", "oferta educativa",
        "que puedo estudiar en el tec", "cuales son las carreras",
        "que ingenierias ofrece", "que licenciaturas hay",
        "que opciones de estudio tiene", "lista de carreras",
        "carreras disponibles", "que carreras tienen",
    ],
    # Piden "informacion" en general de una carrera.
    "general": [
        "informacion", "dame informacion", "quiero informacion",
        "quiero saber", "quiero saber de", "ahora quiero saber de",
        "cuentame de", "hablame de", "dime sobre", "que es",
        "info", "datos", "mas informacion", "me puedes decir sobre",
        "me interesa", "quiero conocer",
    ],
    # Cosas que el bot NO sabe todavia (no estan en el dataset).
    "fuera_alcance": [
        "cuanto cuesta", "costo de la inscripcion", "colegiatura",
        "donde queda", "direccion del tec", "como llego", "telefono",
        "horarios", "horario de clases", "becas", "hay becas",
        "cuanto se paga", "correo de contacto", "ubicacion",
        "necesito ayuda de una persona", "no encuentro mi pregunta",
        "quiero hablar con alguien", "que dia empiezan las clases",
    ],
}

# Palabras de relleno que se quitan antes de clasificar el tema.
PALABRAS_VACIAS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en",
    "y", "o", "a", "al", "que", "es", "son", "se", "si", "me", "mi", "mis",
    "tu", "tus", "por", "para", "con", "lo", "les", "le", "ingenieria",
    "licenciatura",
}

# Si la similitud es menor a esto, no clasificamos el tema.
# (Con 0.30 una pregunta sobre Francia se confundia con "modalidad".)
UMBRAL_TEMA = 0.45

# Palabras que indican una pregunta que el bot todavia no puede contestar.
# Es una regla de seguridad: gana sobre el clasificador.
PALABRAS_FUERA_ALCANCE = {
    "cuesta", "costo", "costos", "precio", "precios", "colegiatura",
    "cuota", "cuotas", "beca", "becas", "telefono", "direccion",
    "ubicacion", "horario", "horarios",
}


def limpiar_para_tema(texto, carreras_detectadas=()):
    # Quita nombres de carrera y palabras vacias, para que el clasificador
    # se fije solo en lo que realmente se esta preguntando.
    texto = normalizar(texto)

    # Quitamos los alias de TODAS las carreras (los mas largos primero).
    for alias in ALIAS_TODOS:
        if alias == "ti" and "ti" not in texto.split():
            continue
        texto = " ".join(f" {texto} ".replace(f" {alias} ", " ").split())

    # Quitamos palabras vacias.
    return " ".join(t for t in texto.split() if t not in PALABRAS_VACIAS)


# Preparamos los ejemplos de entrenamiento.
_frases = []
_temas = []
for _tema, _lista in EJEMPLOS_TEMA.items():
    for _frase in _lista:
        _limpia = limpiar_para_tema(_frase)
        if _limpia:
            _frases.append(_limpia)
            _temas.append(_tema)

# TF-IDF sobre grupos de letras (n-gramas): tolera errores de dedo
# y variantes como "estudia", "estudiar" y "estudian".
VECTORIZADOR = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
MATRIZ = VECTORIZADOR.fit_transform(_frases)


def clasificar_tema(texto):
    # Devuelve (tema, similitud). Si no se parece a nada, tema = "desconocido".
    limpio = limpiar_para_tema(texto)
    if not limpio:
        return "desconocido", 0.0

    # Regla de seguridad: costos, becas, telefonos, etc.
    if PALABRAS_FUERA_ALCANCE & set(limpio.split()):
        return "fuera_alcance", 1.0

    similitudes = cosine_similarity(VECTORIZADOR.transform([limpio]), MATRIZ)[0]
    mejor = int(similitudes.argmax())
    puntaje = float(similitudes[mejor])

    if puntaje < UMBRAL_TEMA:
        return "desconocido", puntaje

    return _temas[mejor], puntaje


