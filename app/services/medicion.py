"""Medición de tiempo de ejecución y memoria pico."""
import time
import tracemalloc


def medir(funcion, *args, repeticiones: int = 1, medir_memoria: bool = True):
    """Ejecuta `funcion(*args)` y devuelve (resultado, metricas).

    El tiempo es el mejor de `repeticiones` corridas y se mide sin tracemalloc,
    porque rastrear la memoria hace más lento el código. La memoria pico se mide
    en una corrida aparte.
    """
    mejor_tiempo = float("inf")
    resultado = None
    for _ in range(max(1, repeticiones)):
        inicio = time.perf_counter()
        resultado = funcion(*args)
        mejor_tiempo = min(mejor_tiempo, time.perf_counter() - inicio)

    metricas = {"tiempo_ms": round(mejor_tiempo * 1000, 4)}

    if medir_memoria:
        tracemalloc.start()
        try:
            funcion(*args)
            _, pico = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        metricas["memoria_pico_kb"] = round(pico / 1024, 2)

    return resultado, metricas
