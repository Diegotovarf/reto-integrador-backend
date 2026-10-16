"""Problema del Agente Viajero (TSP): solución exacta (Held-Karp) y heurística voraz."""
from itertools import combinations

from app.errores import ErrorEntrada
from app.services.grafos import Grafo

LIMITE_EXACTO = 12


def _pesos(grafo: Grafo) -> dict[str, dict[str, float]]:
    return {origen: dict(vecinos) for origen, vecinos in grafo.items()}


def _inicio_valido(grafo: Grafo, inicio: str | None) -> str:
    if inicio is None:
        return next(iter(grafo))
    if inicio not in grafo:
        raise ErrorEntrada(f"El nodo inicial '{inicio}' no pertenece al grafo.")
    return inicio


def tsp_exacto(grafo: Grafo, inicio: str | None = None) -> dict:
    """Held-Karp: dp[(S, j)] = costo mínimo de salir del inicio, visitar el subconjunto S y terminar en j."""
    if len(grafo) > LIMITE_EXACTO:
        raise ErrorEntrada(f"El TSP exacto acepta como máximo {LIMITE_EXACTO} nodos (su costo crece como 2ⁿ).")
    pesos = _pesos(grafo)
    inicio = _inicio_valido(grafo, inicio)
    restantes = [nodo for nodo in grafo if nodo != inicio]
    n = len(restantes)
    if n == 0:
        return {"algoritmo": "Held-Karp (exacto)", "camino": [inicio, inicio], "costo": 0, "estados_evaluados": 1}

    dp: dict[tuple[int, int], float] = {}
    padres: dict[tuple[int, int], int | None] = {}
    for j, nodo in enumerate(restantes):
        if nodo in pesos[inicio]:
            dp[(1 << j, j)] = pesos[inicio][nodo]
            padres[(1 << j, j)] = None
    estados = len(dp)

    for tamano in range(2, n + 1):
        for grupo in combinations(range(n), tamano):
            mascara = sum(1 << j for j in grupo)
            for j in grupo:
                previa = mascara ^ (1 << j)
                mejor_costo, mejor_anterior = float("inf"), None
                for i in grupo:
                    if i == j or (previa, i) not in dp:
                        continue
                    peso = pesos[restantes[i]].get(restantes[j])
                    if peso is None:
                        continue
                    costo = dp[(previa, i)] + peso
                    if costo < mejor_costo:
                        mejor_costo, mejor_anterior = costo, i
                if mejor_anterior is not None:
                    dp[(mascara, j)] = mejor_costo
                    padres[(mascara, j)] = mejor_anterior
                    estados += 1

    completa = (1 << n) - 1
    mejor_costo, ultimo = float("inf"), None
    for j, nodo in enumerate(restantes):
        regreso = pesos[nodo].get(inicio)
        if (completa, j) in dp and regreso is not None and dp[(completa, j)] + regreso < mejor_costo:
            mejor_costo, ultimo = dp[(completa, j)] + regreso, j
    if ultimo is None:
        raise ErrorEntrada("No existe un circuito que visite todos los nodos y regrese al inicio.")

    ruta_inversa = []
    mascara, actual = completa, ultimo
    while actual is not None:
        ruta_inversa.append(restantes[actual])
        anterior = padres[(mascara, actual)]
        mascara ^= 1 << actual
        actual = anterior

    return {
        "algoritmo": "Held-Karp (exacto)",
        "camino": [inicio] + ruta_inversa[::-1] + [inicio],
        "costo": mejor_costo,
        "estados_evaluados": estados,
    }


def tsp_voraz(grafo: Grafo, inicio: str | None = None) -> dict:
    """Vecino más cercano: desde el nodo actual, ir siempre al no visitado más barato."""
    pesos = _pesos(grafo)
    inicio = _inicio_valido(grafo, inicio)
    pendientes = set(grafo) - {inicio}
    camino = [inicio]
    actual = inicio
    costo = 0
    while pendientes:
        candidatos = [(peso, vecino) for vecino, peso in pesos[actual].items() if vecino in pendientes]
        if not candidatos:
            raise ErrorEntrada(f"El voraz quedó atrapado en {actual}: no tiene aristas a nodos sin visitar.")
        peso, siguiente = min(candidatos)
        costo += peso
        camino.append(siguiente)
        pendientes.remove(siguiente)
        actual = siguiente
    regreso = pesos[actual].get(inicio)
    if regreso is None:
        raise ErrorEntrada(f"No hay arista de {actual} de regreso a {inicio} para cerrar el circuito.")
    return {
        "algoritmo": "Vecino más cercano (voraz)",
        "camino": camino + [inicio],
        "costo": costo + regreso,
        "estados_evaluados": len(camino),
    }
