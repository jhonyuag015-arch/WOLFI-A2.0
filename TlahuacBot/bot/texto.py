# PROYECTO: TLAHUACBOT
# Utilidades de texto compartidas por todos los modulos.

import unicodedata


def normalizar(texto):
    # Minusculas y separamos las letras de sus acentos.
    texto = unicodedata.normalize("NFKD", texto.lower())

    # Quitamos los acentos.
    texto = "".join(
        letra for letra in texto if not unicodedata.combining(letra)
    )

    # Dejamos solo letras y numeros; todo lo demas pasa a ser espacio.
    texto = "".join(
        letra if letra.isalnum() else " " for letra in texto
    )

    # Quitamos espacios repetidos.
    return " ".join(texto.split())


def contiene(texto, frase):
    # Revisa si una frase aparece como palabra completa (no a la mitad de otra).
    return f" {frase} " in f" {texto} "

