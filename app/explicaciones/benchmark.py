from app.respuesta import crear_explicacion

DESCRIPCION_TIPOS = {
    "aleatorio": "datos en orden aleatorio",
    "ordenado": "datos ya ordenados",
    "inverso": "datos en orden inverso",
    "casi_ordenado": "datos casi ordenados (≈5% fuera de lugar)",
    "pocos_unicos": "datos con muchos valores repetidos",
}

TEORIA_ORDENAMIENTO = (
    "La complejidad temporal T(n) describe cómo crece el número de operaciones al crecer el tamaño n de la entrada. "
    "Los algoritmos O(n²) (burbuja, selección, inserción) comparan casi todos los pares, por lo que duplicar n "
    "cuadruplica su tiempo; los O(n log n) (mezcla, quicksort, montículo) dividen el problema y escalan mucho mejor. "
    "Ningún ordenamiento basado en comparaciones puede ser mejor que O(n log n) en el peor caso. Ordenar es un "
    "problema de la clase P: se resuelve en tiempo polinómico. La memoria consumida mide la complejidad espacial S(n)."
)

TEORIA_TSP = (
    "P es la clase de problemas que se resuelven en tiempo polinómico, como ordenar o encontrar el camino más corto "
    "con Dijkstra. NP es la clase de problemas cuya solución se puede verificar en tiempo polinómico. La versión de "
    "decisión del Agente Viajero ('¿existe un circuito de costo ≤ K?') es NP-completa: no se conoce ningún algoritmo "
    "polinómico que la resuelva, y encontrarlo probaría que P = NP. Held-Karp da el óptimo con programación dinámica "
    "en O(n²·2ⁿ) tiempo y O(n·2ⁿ) memoria; la heurística del vecino más cercano tarda O(n²) pero no garantiza el "
    "óptimo. Respecto al espacio, NSPACE(f(n)) es la clase de problemas que una máquina no determinista resuelve "
    "usando O(f(n)) memoria. Por el teorema de Savitch, NSPACE(f) ⊆ DSPACE(f²). El TSP está en PSPACE: probando "
    "las permutaciones una por una basta memoria polinómica, aunque el tiempo sea exponencial. Held-Karp hace lo "
    "contrario y cambia memoria exponencial por menos tiempo."
)


def explicar_ordenamiento(filas: list[dict], tamano: int, tipo: str | None) -> dict:
    por_tiempo = sorted(filas, key=lambda f: f["tiempo_ms"])
    rapido, lento = por_tiempo[0], por_tiempo[-1]
    descripcion = f" con {DESCRIPCION_TIPOS[tipo]}" if tipo else ""
    partes = [f"Se ordenaron {tamano} elementos{descripcion} con {len(filas)} algoritmos."]
    if rapido["tiempo_ms"] > 0 and lento is not rapido:
        partes.append(f"El más rápido fue {rapido['nombre']} ({rapido['tiempo_ms']} ms) y el más lento "
                      f"{lento['nombre']} ({lento['tiempo_ms']} ms), unas {lento['tiempo_ms'] / rapido['tiempo_ms']:.1f} veces más.")
    con_contadores = [f for f in filas if f["comparaciones"] is not None]
    if con_contadores:
        menos = min(con_contadores, key=lambda f: f["comparaciones"])
        partes.append(f"{menos['nombre']} hizo menos comparaciones ({menos['comparaciones']}).")
    menos_memoria = min(filas, key=lambda f: f["memoria_pico_kb"])
    partes.append(f"{menos_memoria['nombre']} usó menos memoria ({menos_memoria['memoria_pico_kb']} KB).")
    if tipo in {"ordenado", "casi_ordenado"}:
        partes.append("Con datos ordenados o casi ordenados, inserción y burbuja se acercan a su mejor caso O(n).")
    elif tipo == "inverso":
        partes.append("El orden inverso es el peor caso de inserción y burbuja: cada elemento debe recorrer toda la lista.")
    if any(not f["correcto"] for f in filas):
        partes.append("Atención: algún algoritmo no produjo la lista correctamente ordenada.")
    return crear_explicacion(" ".join(partes), TEORIA_ORDENAMIENTO)


def explicar_tsp(exacto: dict, voraz: dict, n: int) -> dict:
    partes = [f"Grafo de {n} nodos. El óptimo (Held-Karp) cuesta {exacto['costo']:g}: {' → '.join(exacto['camino'])}."]
    if voraz["costo"] is None:
        partes.append(f"El voraz no logró cerrar un circuito ({voraz['error']}), aunque sí existe uno: "
                      "una heurística puede fallar donde el método exacto encuentra solución.")
    else:
        partes.append(f"El voraz obtuvo {voraz['costo']:g}: {' → '.join(voraz['camino'])}.")
        if voraz["costo"] == exacto["costo"]:
            partes.append("En este caso la heurística encontró también el óptimo.")
        else:
            brecha = (voraz["costo"] - exacto["costo"]) / exacto["costo"] * 100 if exacto["costo"] else 0
            partes.append(f"La heurística quedó {brecha:.1f}% por encima del óptimo.")
    partes.append(f"Held-Karp evaluó {exacto['estados_evaluados']} estados en {exacto['tiempo_ms']} ms.")
    if "tiempo_ms" in voraz:
        partes.append(f"El voraz tomó {voraz['tiempo_ms']} ms.")
    return crear_explicacion(" ".join(partes), TEORIA_TSP,
                             "Held-Karp: tiempo O(n²·2ⁿ), espacio O(n·2ⁿ). Voraz: tiempo O(n²), espacio O(n).")


def explicar_escalabilidad_tsp(filas: list[dict]) -> dict:
    primero, ultimo = filas[0], filas[-1]
    partes = [f"Se midieron grafos de {primero['n']} a {ultimo['n']} nodos."]
    if primero["exacto_tiempo_ms"] > 0 and len(filas) > 1:
        factor = ultimo["exacto_tiempo_ms"] / primero["exacto_tiempo_ms"]
        partes.append(f"El tiempo de Held-Karp creció unas {factor:.0f} veces y su memoria pasó de "
                      f"{primero['exacto_memoria_kb']} KB a {ultimo['exacto_memoria_kb']} KB: crecimiento exponencial.")
        partes.append(f"El voraz pasó de {primero['voraz_tiempo_ms']} ms a {ultimo['voraz_tiempo_ms']} ms: crecimiento polinómico.")
    return crear_explicacion(" ".join(partes), TEORIA_TSP,
                             "Held-Karp: tiempo O(n²·2ⁿ), espacio O(n·2ⁿ). Voraz: tiempo O(n²), espacio O(n).")
