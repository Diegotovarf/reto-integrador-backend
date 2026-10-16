"""Operaciones con lenguajes finitos, representados como conjuntos de cadenas.

Las operaciones que producen lenguajes infinitos (L*, L⁺, complemento) se
acotan: L* y L⁺ hasta k concatenaciones, y el complemento dentro de Σ^≤k.
"""
from itertools import product

from app.errores import ErrorEntrada

LIMITE_CADENAS = 20_000

OPERACIONES_BINARIAS = {"union", "interseccion", "diferencia", "diferencia_simetrica", "concatenacion"}


def _acotar(lenguaje: set[str]) -> set[str]:
    if len(lenguaje) > LIMITE_CADENAS:
        raise ErrorEntrada(
            f"El resultado supera {LIMITE_CADENAS} cadenas. Reduce k, n o el tamaño de los lenguajes."
        )
    return lenguaje


def concatenar(L: set[str], M: set[str]) -> set[str]:
    if len(L) * len(M) > LIMITE_CADENAS * 10:
        raise ErrorEntrada(
            f"La concatenación generaría {len(L) * len(M)} combinaciones. Reduce k, n o el tamaño de los lenguajes."
        )
    return _acotar({x + y for x in L for y in M})


def potencia(L: set[str], n: int) -> set[str]:
    resultado = {""}
    for _ in range(n):
        resultado = concatenar(resultado, L)
    return resultado


def kleene(L: set[str], k: int) -> set[str]:
    """L* acotada: L⁰ ∪ L¹ ∪ … ∪ Lᵏ."""
    resultado = {""}
    actual = {""}
    for _ in range(k):
        actual = concatenar(actual, L)
        resultado |= actual
    return _acotar(resultado)


def positiva(L: set[str], k: int) -> set[str]:
    """L⁺ acotada: L¹ ∪ … ∪ Lᵏ."""
    resultado = set()
    actual = {""}
    for _ in range(k):
        actual = concatenar(actual, L)
        resultado |= actual
    return _acotar(resultado)


def tamano_universo(sigma: list[str], k: int) -> int:
    return sum(len(sigma) ** i for i in range(k + 1))


def universo(sigma: list[str], k: int) -> set[str]:
    """Σ^≤k: todas las cadenas sobre Σ de longitud 0 a k."""
    if tamano_universo(sigma, k) > LIMITE_CADENAS:
        raise ErrorEntrada(
            f"Σ^≤{k} tiene {tamano_universo(sigma, k)} cadenas (límite {LIMITE_CADENAS}). Reduce k o el alfabeto."
        )
    return {"".join(simbolos) for i in range(k + 1) for simbolos in product(sigma, repeat=i)}


def operar(operacion: str, L: set[str], M: set[str], sigma: list[str], k: int, n: int) -> set[str]:
    if operacion == "union":
        return L | M
    if operacion == "interseccion":
        return L & M
    if operacion == "diferencia":
        return L - M
    if operacion == "diferencia_simetrica":
        return L ^ M
    if operacion == "concatenacion":
        return concatenar(L, M)
    if operacion == "potencia":
        return potencia(L, n)
    if operacion == "kleene":
        return kleene(L, k)
    if operacion == "positiva":
        return positiva(L, k)
    if operacion == "inversa":
        return {w[::-1] for w in L}
    if operacion == "complemento":
        if not sigma:
            raise ErrorEntrada("El complemento necesita el alfabeto sigma.")
        return universo(sigma, k) - L
    raise ErrorEntrada(f"Operación con lenguajes desconocida: {operacion}")
