"""Algoritmos de búsqueda de rutas: BFS, DFS, Dijkstra, Greedy, A* y Hill-Climbing.

Todos reciben (grafo, origen, destino, coordenadas) y devuelven un diccionario
con la misma forma para poder compararlos en una tabla.
"""
import heapq
import math
from collections import deque

from app.services.grafos import Grafo, costo_camino


def _reconstruir(padres: dict[str, str], destino: str) -> list[str]:
    camino = [destino]
    while camino[-1] in padres:
        camino.append(padres[camino[-1]])
    return camino[::-1]


def _resultado(algoritmo: str, grafo: Grafo, camino: list[str], orden_visita: list[str],
               frontera_maxima: int, **extra) -> dict:
    encontrado = bool(camino)
    return {
        "algoritmo": algoritmo,
        "encontrado": encontrado,
        "camino": camino,
        "costo": costo_camino(grafo, camino) if encontrado else None,
        "saltos": len(camino) - 1 if encontrado else None,
        "nodos_expandidos": len(orden_visita),
        "orden_visita": orden_visita,
        "frontera_maxima": frontera_maxima,
        **extra,
    }


def saltos_hasta(grafo: Grafo, destino: str) -> dict[str, int]:
    """Mínimo número de aristas desde cada nodo hasta el destino (BFS sobre el grafo invertido)."""
    inverso: dict[str, list[str]] = {nodo: [] for nodo in grafo}
    for nodo, vecinos in grafo.items():
        for vecino, _ in vecinos:
            inverso[vecino].append(nodo)
    distancias = {destino: 0}
    cola = deque([destino])
    while cola:
        actual = cola.popleft()
        for anterior in inverso[actual]:
            if anterior not in distancias:
                distancias[anterior] = distancias[actual] + 1
                cola.append(anterior)
    return distancias


def construir_heuristica(grafo: Grafo, destino: str, coordenadas: dict | None, admisible: bool = False):
    """Devuelve (h, descripción).

    Con coordenadas de todos los nodos se usa la distancia euclidiana. Sin ellas se usa
    el número mínimo de aristas hasta el destino; si se pide una heurística admisible
    (para A*), ese número se multiplica por el peso mínimo del grafo para no sobreestimar.
    """
    if coordenadas and all(nodo in coordenadas for nodo in grafo):
        meta = coordenadas[destino]
        return (lambda nodo: math.dist(coordenadas[nodo], meta)), "distancia euclidiana al destino"

    saltos = saltos_hasta(grafo, destino)
    if admisible:
        pesos = [peso for vecinos in grafo.values() for _, peso in vecinos]
        minimo = min(pesos) if pesos else 0
        return (lambda nodo: saltos.get(nodo, math.inf) * minimo), \
            f"aristas mínimas hasta el destino × peso mínimo del grafo ({minimo})"
    return (lambda nodo: saltos.get(nodo, math.inf)), "número mínimo de aristas hasta el destino"


def bfs(grafo: Grafo, origen: str, destino: str, coordenadas=None) -> dict:
    cola = deque([origen])
    padres: dict[str, str] = {}
    descubiertos = {origen}
    orden = []
    frontera_maxima = 1
    while cola:
        actual = cola.popleft()
        orden.append(actual)
        if actual == destino:
            return _resultado("BFS", grafo, _reconstruir(padres, destino), orden, frontera_maxima)
        for vecino, _ in grafo[actual]:
            if vecino not in descubiertos:
                descubiertos.add(vecino)
                padres[vecino] = actual
                cola.append(vecino)
        frontera_maxima = max(frontera_maxima, len(cola))
    return _resultado("BFS", grafo, [], orden, frontera_maxima)


def dfs(grafo: Grafo, origen: str, destino: str, coordenadas=None) -> dict:
    pila = [origen]
    padres: dict[str, str] = {}
    visitados = set()
    orden = []
    frontera_maxima = 1
    while pila:
        actual = pila.pop()
        if actual in visitados:
            continue
        visitados.add(actual)
        orden.append(actual)
        if actual == destino:
            return _resultado("DFS", grafo, _reconstruir(padres, destino), orden, frontera_maxima)
        # Se apilan en orden inverso para explorar los vecinos en el orden en que se escribieron.
        for vecino, _ in reversed(grafo[actual]):
            if vecino not in visitados:
                padres[vecino] = actual
                pila.append(vecino)
        frontera_maxima = max(frontera_maxima, len(pila))
    return _resultado("DFS", grafo, [], orden, frontera_maxima)


def _mejor_primero(nombre: str, grafo: Grafo, origen: str, destino: str, h, descripcion_h: str) -> dict:
    """Búsqueda por costo acumulado g(n) + h(n). Con h = 0 es Dijkstra; con h admisible es A*."""
    g = {origen: 0}
    padres: dict[str, str] = {}
    frontera = [(h(origen), 0, origen)]
    contador = 1
    cerrados = set()
    orden = []
    frontera_maxima = 1
    while frontera:
        _, _, actual = heapq.heappop(frontera)
        if actual in cerrados:
            continue
        cerrados.add(actual)
        orden.append(actual)
        if actual == destino:
            return _resultado(nombre, grafo, _reconstruir(padres, destino), orden, frontera_maxima,
                              heuristica=descripcion_h)
        for vecino, peso in grafo[actual]:
            nuevo_costo = g[actual] + peso
            if nuevo_costo < g.get(vecino, math.inf):
                g[vecino] = nuevo_costo
                padres[vecino] = actual
                heapq.heappush(frontera, (nuevo_costo + h(vecino), contador, vecino))
                contador += 1
        frontera_maxima = max(frontera_maxima, len(frontera))
    return _resultado(nombre, grafo, [], orden, frontera_maxima, heuristica=descripcion_h)


def dijkstra(grafo: Grafo, origen: str, destino: str, coordenadas=None) -> dict:
    return _mejor_primero("Dijkstra", grafo, origen, destino, lambda _: 0, "sin heurística (h = 0)")


def a_estrella(grafo: Grafo, origen: str, destino: str, coordenadas=None) -> dict:
    h, descripcion = construir_heuristica(grafo, destino, coordenadas, admisible=True)
    return _mejor_primero("A*", grafo, origen, destino, h, descripcion)


def greedy(grafo: Grafo, origen: str, destino: str, coordenadas=None) -> dict:
    h, descripcion = construir_heuristica(grafo, destino, coordenadas)
    padres: dict[str, str] = {}
    descubiertos = {origen}
    frontera = [(h(origen), 0, origen)]
    contador = 1
    orden = []
    frontera_maxima = 1
    while frontera:
        _, _, actual = heapq.heappop(frontera)
        orden.append(actual)
        if actual == destino:
            return _resultado("Greedy Best-First", grafo, _reconstruir(padres, destino), orden,
                              frontera_maxima, heuristica=descripcion)
        for vecino, _ in grafo[actual]:
            if vecino not in descubiertos:
                descubiertos.add(vecino)
                padres[vecino] = actual
                heapq.heappush(frontera, (h(vecino), contador, vecino))
                contador += 1
        frontera_maxima = max(frontera_maxima, len(frontera))
    return _resultado("Greedy Best-First", grafo, [], orden, frontera_maxima, heuristica=descripcion)


def hill_climbing(grafo: Grafo, origen: str, destino: str, coordenadas=None) -> dict:
    """Hill-Climbing de máximo descenso: siempre se mueve al vecino con menor h(n).

    Se detiene si ningún vecino mejora a h del nodo actual (óptimo local o meseta)
    o si no quedan vecinos sin visitar (callejón sin salida). No retrocede.
    """
    h, descripcion = construir_heuristica(grafo, destino, coordenadas)
    camino = [origen]
    visitados = {origen}
    actual = origen
    frontera_maxima = 0
    motivo = "Se alcanzó el destino."
    while actual != destino:
        candidatos = [(h(vecino), vecino) for vecino, _ in grafo[actual] if vecino not in visitados]
        frontera_maxima = max(frontera_maxima, len(candidatos))
        if not candidatos:
            motivo = f"Callejón sin salida en {actual}: no tiene vecinos sin visitar."
            break
        if any(vecino == destino for _, vecino in candidatos):
            mejor_h, mejor = h(destino), destino
        else:
            mejor_h, mejor = min(candidatos)
        if mejor_h >= h(actual):
            motivo = (f"Óptimo local en {actual}: h({actual}) = {h(actual):g} y ningún vecino tiene una h menor, "
                      "así que el algoritmo se detiene sin llegar al destino.")
            break
        camino.append(mejor)
        visitados.add(mejor)
        actual = mejor

    encontrado = actual == destino
    return _resultado("Hill-Climbing", grafo, camino if encontrado else [], camino, frontera_maxima,
                      heuristica=descripcion, motivo_parada=motivo)


ALGORITMOS = {
    "bfs": bfs,
    "dfs": dfs,
    "dijkstra": dijkstra,
    "greedy": greedy,
    "a_estrella": a_estrella,
    "hill_climbing": hill_climbing,
}


def alcance(grafo: Grafo, origen: str, costo_maximo: float | None = None,
            saltos_maximos: int | None = None) -> dict:
    """Nodos alcanzables desde `origen`, con su costo mínimo (Dijkstra) y su mínimo de saltos (BFS)."""
    costos = {origen: 0}
    padres: dict[str, str] = {}
    cola = [(0, 0, origen)]
    contador = 1
    cerrados = set()
    while cola:
        costo, _, actual = heapq.heappop(cola)
        if actual in cerrados:
            continue
        cerrados.add(actual)
        for vecino, peso in grafo[actual]:
            if costo + peso < costos.get(vecino, math.inf):
                costos[vecino] = costo + peso
                padres[vecino] = actual
                heapq.heappush(cola, (costos[vecino], contador, vecino))
                contador += 1

    saltos = {origen: 0}
    cola_bfs = deque([origen])
    while cola_bfs:
        actual = cola_bfs.popleft()
        for vecino, _ in grafo[actual]:
            if vecino not in saltos:
                saltos[vecino] = saltos[actual] + 1
                cola_bfs.append(vecino)

    alcanzables = []
    for nodo in sorted(costos, key=lambda n: (costos[n], n)):
        if costo_maximo is not None and costos[nodo] > costo_maximo:
            continue
        if saltos_maximos is not None and saltos[nodo] > saltos_maximos:
            continue
        alcanzables.append({
            "nodo": nodo,
            "costo_minimo": costos[nodo],
            "saltos_minimos": saltos[nodo],
            "camino": _reconstruir(padres, nodo),
        })

    fuera = sorted(set(grafo) - {a["nodo"] for a in alcanzables})
    return {
        "origen": origen,
        "alcanzables": alcanzables,
        "no_alcanzables": fuera,
        "mas_lejano": alcanzables[-1] if len(alcanzables) > 1 else None,
    }
