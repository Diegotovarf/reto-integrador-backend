"""Representación de grafos ponderados y utilidades comunes.

Formato interno (el mismo de los grafos del profesor):
    {"A": [("B", 15), ("C", 22)], "B": [...], ...}
También se acepta la forma {"A": {"B": 15, "C": 22}}.
"""
import math
import random
import string

from app.errores import ErrorEntrada

Grafo = dict[str, list[tuple[str, float]]]


def _agregar(pesos: dict, origen: str, destino: str, peso: float) -> None:
    actual = pesos[origen].get(destino)
    if actual is None or peso < actual:
        pesos[origen][destino] = peso


def normalizar(grafo: dict, dirigido: bool = True) -> Grafo:
    """Valida el grafo, registra todos los nodos y, si no es dirigido, agrega las aristas inversas."""
    pesos: dict[str, dict[str, float]] = {}
    for origen, vecinos in grafo.items():
        pesos.setdefault(origen, {})
        pares = vecinos.items() if isinstance(vecinos, dict) else vecinos
        for destino, peso in pares:
            if peso < 0:
                raise ErrorEntrada(
                    f"La arista {origen}→{destino} tiene peso negativo ({peso}). "
                    "Los algoritmos de este módulo requieren pesos ≥ 0."
                )
            pesos.setdefault(destino, {})
            _agregar(pesos, origen, destino, peso)
            if not dirigido:
                _agregar(pesos, destino, origen, peso)
    if not pesos:
        raise ErrorEntrada("El grafo está vacío.")
    return {nodo: list(vecinos.items()) for nodo, vecinos in pesos.items()}


def verificar_nodo(grafo: Grafo, nodo: str, rol: str) -> None:
    if nodo not in grafo:
        raise ErrorEntrada(f"El {rol} '{nodo}' no pertenece al grafo.")


def costo_camino(grafo: Grafo, camino: list[str]) -> float:
    total = 0
    for a, b in zip(camino, camino[1:]):
        total += dict(grafo[a])[b]
    return total


def diagrama(grafo: Grafo, dirigido: bool, coordenadas: dict | None = None) -> dict:
    """Nodos y aristas para dibujar el grafo. En grafos no dirigidos cada arista aparece una vez."""
    aristas = []
    vistas = set()
    for origen, vecinos in grafo.items():
        for destino, peso in vecinos:
            clave = (origen, destino) if dirigido else tuple(sorted((origen, destino)))
            if clave in vistas:
                continue
            vistas.add(clave)
            aristas.append({"origen": origen, "destino": destino, "peso": peso})
    nodos = []
    for nodo in grafo:
        datos = {"id": nodo}
        if coordenadas and nodo in coordenadas:
            datos["x"], datos["y"] = coordenadas[nodo]
        nodos.append(datos)
    return {"dirigido": dirigido, "nodos": nodos, "aristas": aristas}


def _nombres(n: int) -> list[str]:
    if n <= len(string.ascii_uppercase):
        return list(string.ascii_uppercase[:n])
    return [f"N{i}" for i in range(n)]


def generar(n: int, densidad: float, semilla: int) -> tuple[Grafo, dict]:
    """Genera un grafo no dirigido, conexo y con coordenadas.

    El peso de cada arista es la distancia euclidiana redondeada hacia arriba, así
    la distancia en línea recta nunca sobreestima el costo real (heurística admisible para A*).
    Con densidad 1 el grafo es completo.
    """
    rng = random.Random(semilla)
    nombres = _nombres(n)
    coordenadas = {nombre: (rng.randint(0, 100), rng.randint(0, 100)) for nombre in nombres}

    def peso(a: str, b: str) -> int:
        return max(1, math.ceil(math.dist(coordenadas[a], coordenadas[b])))

    pares = set()
    # Árbol aleatorio para garantizar que el grafo sea conexo.
    orden = nombres[:]
    rng.shuffle(orden)
    for i in range(1, n):
        pares.add(tuple(sorted((orden[i], rng.choice(orden[:i])))))
    # Aristas adicionales según la densidad.
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < densidad:
                pares.add((nombres[i], nombres[j]))

    grafo: Grafo = {nombre: [] for nombre in nombres}
    for a, b in sorted(pares):
        p = peso(a, b)
        grafo[a].append((b, p))
        grafo[b].append((a, p))
    return grafo, coordenadas
