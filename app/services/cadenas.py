"""Operaciones con cadenas (palabras) sobre un alfabeto Σ.

La cadena vacía se representa internamente como "" y se muestra como "ε".
Cada símbolo de una cadena es un carácter.
"""
from collections import Counter
from typing import Iterable, Optional

from app.errores import ErrorEntrada

EPSILON = "ε"
_REPRESENTACIONES_VACIA = {"ε", "λ"}


def normalizar(cadena: str) -> str:
    """Convierte "ε" o "λ" en la cadena vacía."""
    return "" if cadena in _REPRESENTACIONES_VACIA else cadena


def mostrar(cadena: str) -> str:
    """Representación legible: la cadena vacía se muestra como ε."""
    return cadena if cadena else EPSILON


def ordenar(cadenas: Iterable[str]) -> list[str]:
    """Orden canónico: primero por longitud y luego alfabéticamente."""
    return sorted(set(cadenas), key=lambda c: (len(c), c))


def mostrar_lista(cadenas: Iterable[str]) -> list[str]:
    return [mostrar(c) for c in ordenar(cadenas)]


def prefijos(w: str) -> list[str]:
    return ordenar(w[:i] for i in range(len(w) + 1))


def sufijos(w: str) -> list[str]:
    return ordenar(w[i:] for i in range(len(w) + 1))


def subcadenas(w: str) -> list[str]:
    return ordenar(w[i:j] for i in range(len(w) + 1) for j in range(i, len(w) + 1))


def simbolos_invalidos(w: str, sigma: Iterable[str]) -> list[str]:
    alfabeto = set(sigma)
    return sorted({simbolo for simbolo in w if simbolo not in alfabeto})


def operar(operacion: str, w: str, v: Optional[str] = None,
           n: Optional[int] = None, sigma: Optional[list[str]] = None):
    if operacion == "longitud":
        return len(w)
    if operacion == "inversa":
        return mostrar(w[::-1])
    if operacion == "concatenacion":
        if v is None:
            raise ErrorEntrada("La concatenación necesita una segunda cadena v.")
        return mostrar(w + v)
    if operacion == "potencia":
        if n is None:
            raise ErrorEntrada("La potencia necesita el exponente n.")
        return mostrar(w * n)
    if operacion == "prefijos":
        return [mostrar(p) for p in prefijos(w)]
    if operacion == "sufijos":
        return [mostrar(s) for s in sufijos(w)]
    if operacion == "subcadenas":
        return [mostrar(s) for s in subcadenas(w)]
    if operacion == "palindromo":
        return w == w[::-1]
    if operacion == "conteo":
        return dict(sorted(Counter(w).items()))
    if operacion == "alfabeto":
        if not sigma:
            raise ErrorEntrada("Para verificar si w ∈ Σ* necesitas indicar el alfabeto sigma.")
        invalidos = simbolos_invalidos(w, sigma)
        return {"pertenece": not invalidos, "simbolos_invalidos": invalidos}
    raise ErrorEntrada(f"Operación con cadenas desconocida: {operacion}")
