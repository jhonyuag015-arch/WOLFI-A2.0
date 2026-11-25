# PROYECTO: TLAHUACBOT
# Consultas generales del Tec que NO dependen de una carrera: admision,
# costos, becas, servicios escolares y tramites academicos.
#
# Funciona por SIMILITUD: compara la pregunta del usuario contra todas las
# preguntas de esas intenciones en dataset_preguntas.json (TF-IDF + coseno).
# Si ninguna se parece lo suficiente, no responde y el motor sigue su camino.
#
# Para agregar un tema nuevo basta con agregar un registro al dataset cuya
# "intencion" empiece con alguno de los PREFIJOS de abajo. No hay que tocar
# mas codigo.

from difflib import get_close_matches

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from bot.datos import REGISTROS
from bot.temas import limpiar_para_tema


# Intenciones que atiende este modulo ("admision" exacta o con sufijo).
PREFIJOS = ("admision_", "costos_", "becas_", "servicios_", "tramites_")

# Similitud minima para contestar. Mas alto = mas estricto (contesta menos
# pero se equivoca menos). Se ajusta con evaluacion.py.
UMBRAL_CONSULTA = 0.50

# Si la similitud es MUY alta, contestamos aunque la pregunta mencione una
# carrera ("cuanto dura el servicio social en sistemas").
UMBRAL_CONSULTA_ALTO = 0.80


def es_consulta(intencion):
    # True si la intencion es una consulta general de este modulo.
    return intencion == "admision" or intencion.startswith(PREFIJOS)


# Intenciones que sirven de "freno": si la pregunta se parece mas a estas
# (por ejemplo "necesito ayuda de una persona" o "que carreras hay"), este
# modulo no contesta y el motor sigue con su flujo normal.
FRENOS = {"sin_respuesta", "oferta_educativa", "modalidades", "duracion"}

# Palabras que aparecen en casi cualquier pregunta sobre la escuela y no
# ayudan a distinguir un tema de otro.
PALABRAS_INSTITUCION = {"tec", "tecnologico", "tecnm", "campus", "escuela",
                        "plantel"}


def limpiar(texto):
    # Mismo limpiado que el clasificador de temas, sin el nombre de la escuela.
    limpio = limpiar_para_tema(texto)
    return " ".join(p for p in limpio.split() if p not in PALABRAS_INSTITUCION)

# Palabras de pregunta que no dicen "de que" se esta preguntando.
PALABRAS_GENERICAS = {"cuanto", "cuesta", "como", "donde", "cual", "cuales",
                      "cuando", "puedo", "puede", "tengo", "hacer", "quiero",
                      "necesito", "dime", "saber", "pueden"}


def _contenido(texto):
    # Palabras con significado propio (de 4 letras o mas, no genericas).
    return [p for p in texto.split()
            if len(p) >= 4 and p not in PALABRAS_GENERICAS]


# Preparamos los ejemplos: una fila por cada pregunta del dataset.
_frases = []
_intenciones = []
_vocabulario = {}   # intencion -> palabras con significado de sus preguntas
for _registro in REGISTROS:
    if not (es_consulta(_registro["intencion"])
            or _registro["intencion"] in FRENOS):
        continue
    for _pregunta in _registro["preguntas"]:
        _limpia = limpiar(_pregunta)
        if _limpia:
            _frases.append(_limpia)
            _intenciones.append(_registro["intencion"])
            _vocabulario.setdefault(_registro["intencion"], set()).update(
                _contenido(_limpia))

# Grupos de letras (n-gramas): tolera errores de dedo y variantes.
_VECTORIZADOR = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
_MATRIZ = _VECTORIZADOR.fit_transform(_frases)


def buscar_consulta(texto):
    # Devuelve (intencion, similitud) de la pregunta mas parecida del
    # dataset, o (None, similitud) si ninguna alcanza el umbral.
    limpio = limpiar(texto)
    if not limpio:
        return None, 0.0

    similitudes = cosine_similarity(_VECTORIZADOR.transform([limpio]), _MATRIZ)[0]
    mejor = int(similitudes.argmax())
    puntaje = float(similitudes[mejor])

    if puntaje < UMBRAL_CONSULTA or _intenciones[mejor] in FRENOS:
        return None, puntaje

    # Una sola palabra suelta ("estudia") se parece a demasiadas cosas:
    # solo contestamos si la coincidencia es casi exacta.
    if len(limpio.split()) < 2 and puntaje < UMBRAL_CONSULTA_ALTO:
        return None, puntaje

    # Seguro contra preguntas fuera de tema ("cuanto cuesta un taco"): al
    # menos una palabra con significado debe parecerse a las del tema elegido.
    vocabulario = list(_vocabulario.get(_intenciones[mejor], ()))
    if not any(get_close_matches(p, vocabulario, n=1, cutoff=0.8)
               for p in _contenido(limpio)):
        return None, puntaje

    return _intenciones[mejor], puntaje
