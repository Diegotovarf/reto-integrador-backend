from fastapi import APIRouter

from app.errores import ErrorEntrada
from app.explicaciones.benchmark import explicar_escalabilidad_tsp, explicar_ordenamiento, explicar_tsp
from app.respuesta import respuesta
from app.schemas.benchmark import OrdenamientoRequest, TSPEscalabilidadRequest, TSPRequest
from app.services import grafos
from app.services.medicion import medir
from app.services.ordenamientos import CATALOGO, catalogo_publico, generar_datos
from app.services.tsp import tsp_exacto, tsp_voraz

router = APIRouter(prefix="/benchmark", tags=["Módulo 3 · Escalabilidad y benchmark"])


def _brecha(exacto: float, voraz: float | None) -> float | None:
    if voraz is None or not exacto:
        return None
    return round((voraz - exacto) / exacto * 100, 2)


@router.get("/ordenamiento/catalogo")
def catalogo():
    """Algoritmos de ordenamiento disponibles con su complejidad teórica."""
    return catalogo_publico()


@router.post("/ordenamiento")
def comparar_ordenamientos(datos: OrdenamientoRequest):
    """Ordena el mismo conjunto de datos con cada algoritmo seleccionado y compara su desempeño."""
    propios = datos.datos is not None
    entrada = datos.datos if propios else generar_datos(datos.tamano, datos.tipo, datos.semilla)
    tipo = None if propios else datos.tipo
    referencia = sorted(entrada)
    repeticiones = 3 if len(entrada) <= 500 else 1

    filas = []
    for clave in datos.algoritmos:
        info = CATALOGO[clave]
        (ordenada, contadores), metricas = medir(info["funcion"], entrada, repeticiones=repeticiones)
        filas.append({
            "clave": clave,
            "nombre": info["nombre"],
            **metricas,
            **contadores,
            "correcto": ordenada == referencia,
            "estable": info["estable"],
            "complejidad": {k: info[k] for k in ("mejor", "promedio", "peor", "espacio")},
        })

    resultado = {
        "n": len(entrada),
        "tipo": tipo,
        "algoritmos": filas,
        "ranking": [f["clave"] for f in sorted(filas, key=lambda f: f["tiempo_ms"])],
        "grafica": {
            "etiquetas": [f["nombre"] for f in filas],
            "tiempo_ms": [f["tiempo_ms"] for f in filas],
            "memoria_pico_kb": [f["memoria_pico_kb"] for f in filas],
            "comparaciones": [f["comparaciones"] for f in filas],
        },
    }
    if datos.incluir_datos:
        resultado["datos_entrada"] = entrada
        resultado["datos_ordenados"] = referencia

    if datos.tamanos:
        series = {clave: [] for clave in datos.algoritmos}
        for tamano in datos.tamanos:
            muestra = generar_datos(tamano, datos.tipo, datos.semilla)
            for clave in datos.algoritmos:
                _, metricas = medir(CATALOGO[clave]["funcion"], muestra, medir_memoria=False)
                series[clave].append(metricas["tiempo_ms"])
        resultado["escalabilidad"] = {"tamanos": datos.tamanos, "tiempo_ms": series}

    return respuesta("benchmark", "comparar ordenamientos", resultado,
                     explicar_ordenamiento(filas, len(entrada), tipo))


@router.post("/tsp")
def comparar_tsp(datos: TSPRequest):
    """Agente Viajero: compara la solución exacta (NP-difícil) contra la heurística voraz."""
    if datos.grafo is not None:
        grafo, coordenadas, dirigido = grafos.normalizar(datos.grafo, datos.dirigido), None, datos.dirigido
    else:
        (grafo, coordenadas), dirigido = grafos.generar(datos.n, 1.0, datos.semilla), False

    exacto, metricas = medir(tsp_exacto, grafo, datos.inicio)
    exacto.update(metricas)
    try:
        voraz, metricas = medir(tsp_voraz, grafo, datos.inicio, repeticiones=3)
        voraz.update(metricas)
    except ErrorEntrada as error:
        voraz = {"algoritmo": "Vecino más cercano (voraz)", "camino": [], "costo": None, "error": str(error)}

    resultado = {
        "n": len(grafo),
        "exacto": exacto,
        "voraz": voraz,
        "brecha_porcentaje": _brecha(exacto["costo"], voraz["costo"]),
        "grafo": grafo,
        "diagrama": grafos.diagrama(grafo, dirigido, coordenadas),
    }
    return respuesta("benchmark", "TSP exacto vs voraz", resultado, explicar_tsp(exacto, voraz, len(grafo)))


@router.post("/tsp/escalabilidad")
def escalabilidad_tsp(datos: TSPEscalabilidadRequest):
    """Mide cómo crecen tiempo y memoria del TSP exacto y del voraz al aumentar el número de nodos."""
    filas = []
    for n in datos.tamanos:
        grafo, _ = grafos.generar(n, 1.0, datos.semilla)
        exacto, me = medir(tsp_exacto, grafo)
        voraz, mv = medir(tsp_voraz, grafo, repeticiones=3)
        filas.append({
            "n": n,
            "exacto_tiempo_ms": me["tiempo_ms"],
            "exacto_memoria_kb": me["memoria_pico_kb"],
            "exacto_costo": exacto["costo"],
            "exacto_estados": exacto["estados_evaluados"],
            "voraz_tiempo_ms": mv["tiempo_ms"],
            "voraz_memoria_kb": mv["memoria_pico_kb"],
            "voraz_costo": voraz["costo"],
            "brecha_porcentaje": _brecha(exacto["costo"], voraz["costo"]),
        })

    columnas = ("exacto_tiempo_ms", "voraz_tiempo_ms", "exacto_memoria_kb", "voraz_memoria_kb")
    resultado = {
        "tabla": filas,
        "grafica": {"n": [f["n"] for f in filas], **{c: [f[c] for f in filas] for c in columnas}},
    }
    return respuesta("benchmark", "escalabilidad TSP", resultado, explicar_escalabilidad_tsp(filas))
