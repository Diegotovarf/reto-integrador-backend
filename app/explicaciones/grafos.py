from app.respuesta import crear_explicacion

TEORIA = {
    "bfs": "Búsqueda en anchura (BFS): explora por niveles usando una cola (FIFO). Primero visita todos los vecinos del origen, luego los vecinos de esos, etc. Encuentra el camino con menos aristas, pero ignora los pesos, así que no garantiza el de menor costo.",
    "dfs": "Búsqueda en profundidad (DFS): usa una pila (LIFO) y avanza por un camino hasta que no puede más; entonces retrocede. Gasta poca memoria, pero el camino que encuentra puede ser largo y caro.",
    "dijkstra": "Dijkstra: expande siempre el nodo con menor costo acumulado g(n) desde el origen, usando una cola de prioridad. Con pesos no negativos garantiza el camino de costo mínimo.",
    "greedy": "Greedy Best-First: expande siempre el nodo que 'parece' más cercano al destino según la heurística h(n), sin mirar lo que ya costó llegar. Suele ser rápido, pero no garantiza el camino óptimo.",
    "a_estrella": "A*: expande el nodo con menor f(n) = g(n) + h(n), es decir, costo ya recorrido más una estimación de lo que falta. Si h nunca sobreestima el costo real (heurística admisible), A* encuentra el camino óptimo explorando menos nodos que Dijkstra.",
    "hill_climbing": "Hill-Climbing (escalada): búsqueda local que desde el nodo actual se mueve al vecino con mejor heurística, solo si mejora. No guarda alternativas ni retrocede, así que puede quedarse atorado en un óptimo local o una meseta sin llegar al destino.",
}

COMPLEJIDAD = {
    "bfs": "Tiempo O(V + E), espacio O(V).",
    "dfs": "Tiempo O(V + E), espacio O(V).",
    "dijkstra": "Tiempo O((V + E) log V) con montículo binario, espacio O(V).",
    "greedy": "Tiempo O((V + E) log V) en el peor caso, espacio O(V).",
    "a_estrella": "Tiempo O((V + E) log V) en el peor caso; con una buena heurística explora mucho menos. Espacio O(V).",
    "hill_climbing": "Tiempo O(V · grado máximo) como máximo, espacio O(1) además del camino: no guarda frontera.",
}

TEORIA_COMPARACION = (
    "Todos los algoritmos reciben el mismo grafo, origen y destino. Los no informados (BFS, DFS) solo usan la "
    "estructura del grafo; Dijkstra usa los pesos; los informados (Greedy, A*, Hill-Climbing) usan además una "
    "heurística h(n) que estima la distancia al destino. Comparar costo, nodos expandidos y tiempo muestra el "
    "equilibrio entre calidad de la solución y esfuerzo de búsqueda."
)


def explicar_algoritmo(clave: str, resultado: dict) -> dict:
    nombre = resultado["algoritmo"]
    if resultado["encontrado"]:
        resumen = (f"{nombre} encontró {' → '.join(resultado['camino'])} con costo {resultado['costo']:g} "
                   f"en {resultado['saltos']} salto(s), expandiendo {resultado['nodos_expandidos']} nodo(s).")
    else:
        resumen = f"{nombre} no encontró un camino tras expandir {resultado['nodos_expandidos']} nodo(s)."
    if "motivo_parada" in resultado and not resultado["encontrado"]:
        resumen += " " + resultado["motivo_parada"]
    if "heuristica" in resultado:
        resumen += f" Heurística usada: {resultado['heuristica']}."
    return crear_explicacion(resumen, TEORIA[clave], COMPLEJIDAD[clave])


def explicar_comparacion(filas: list[dict], origen: str, destino: str) -> dict:
    exitosos = [f for f in filas if f["encontrado"]]
    if not exitosos:
        return crear_explicacion(f"Ningún algoritmo encontró un camino de {origen} a {destino}: "
                                 "el destino no es alcanzable o los algoritmos locales se atoraron.",
                                 TEORIA_COMPARACION)
    mejor_costo = min(f["costo"] for f in exitosos)
    optimos = [f["algoritmo"] for f in exitosos if f["costo"] == mejor_costo]
    mas_rapido = min(filas, key=lambda f: f["tiempo_ms"])
    menos_expansiones = min(exitosos, key=lambda f: f["nodos_expandidos"])
    partes = [
        f"El menor costo de {origen} a {destino} es {mejor_costo:g}, logrado por: {', '.join(optimos)}.",
        f"El más rápido fue {mas_rapido['algoritmo']} ({mas_rapido['tiempo_ms']} ms).",
        f"{menos_expansiones['algoritmo']} fue el que menos nodos expandió ({menos_expansiones['nodos_expandidos']}).",
    ]
    no_optimos = [f["algoritmo"] for f in exitosos if f["costo"] > mejor_costo]
    if no_optimos:
        partes.append(f"{', '.join(no_optimos)} encontraron un camino más caro: no garantizan el óptimo.")
    fallidos = [f["algoritmo"] for f in filas if not f["encontrado"]]
    if fallidos:
        partes.append(f"{', '.join(fallidos)} no llegaron al destino.")
    return crear_explicacion(" ".join(partes), TEORIA_COMPARACION)


def explicar_alcance(resultado: dict, costo_maximo, saltos_maximos) -> dict:
    limites = []
    if costo_maximo is not None:
        limites.append(f"costo ≤ {costo_maximo:g}")
    if saltos_maximos is not None:
        limites.append(f"a lo más {saltos_maximos} salto(s)")
    condicion = f" con {' y '.join(limites)}" if limites else ""
    total = len(resultado["alcanzables"])
    resumen = f"Desde {resultado['origen']} se alcanzan {total} nodo(s){condicion} (incluido el origen)."
    if resultado["mas_lejano"]:
        lejano = resultado["mas_lejano"]
        resumen += f" El más lejano es {lejano['nodo']} con costo mínimo {lejano['costo_minimo']:g}."
    if resultado["no_alcanzables"]:
        resumen += f" Quedan fuera: {', '.join(resultado['no_alcanzables'])}."
    teoria = ("El alcance se calcula con Dijkstra desde el origen, que da el costo mínimo a cada nodo, y con BFS, "
              "que da el mínimo número de aristas. Un nodo es alcanzable si existe un camino dirigido hasta él.")
    return crear_explicacion(resumen, teoria, "O((V + E) log V)")
