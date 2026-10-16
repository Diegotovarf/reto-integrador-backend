import json
from pathlib import Path

from fastapi import APIRouter

from app.explicaciones.grafos import explicar_algoritmo, explicar_alcance, explicar_comparacion
from app.respuesta import crear_explicacion, respuesta
from app.schemas.grafos import AlcanceRequest, CompararRequest, GenerarGrafoRequest
from app.services import grafos
from app.services.busquedas import ALGORITMOS, alcance
from app.services.medicion import medir

router = APIRouter(prefix="/grafos", tags=["Módulo 2 · Logística y optimización"])

_EJEMPLOS = Path(__file__).resolve().parent.parent / "datos" / "grafos_profesor.json"

_COLUMNAS_TABLA = ("algoritmo", "encontrado", "camino", "costo", "saltos", "nodos_expandidos",
                   "tiempo_ms", "memoria_pico_kb")


@router.get("/ejemplos")
def ejemplos():
    """Grafos de prueba del profesor (dirigidos y ponderados)."""
    datos = json.loads(_EJEMPLOS.read_text(encoding="utf-8"))
    return {nombre: {"nodos": len(grafo), "dirigido": True, "grafo": grafo} for nombre, grafo in datos.items()}


@router.post("/generar")
def generar(datos: GenerarGrafoRequest):
    """Genera un grafo no dirigido, conexo y con coordenadas para dibujarlo."""
    grafo, coordenadas = grafos.generar(datos.n, datos.densidad, datos.semilla)
    aristas = sum(len(v) for v in grafo.values()) // 2
    resultado = {"grafo": grafo, "dirigido": False, "coordenadas": coordenadas,
                 "diagrama": grafos.diagrama(grafo, False, coordenadas)}
    explicacion = crear_explicacion(
        f"Se generó un grafo de {datos.n} nodos y {aristas} aristas con la semilla {datos.semilla}.",
        "Los nodos se colocan en un plano y el peso de cada arista es su distancia euclidiana redondeada hacia arriba. "
        "Primero se construye un árbol aleatorio, lo que garantiza que el grafo sea conexo, y luego se agregan aristas "
        "según la densidad. Con la misma semilla se obtiene siempre el mismo grafo.",
    )
    return respuesta("grafos", "generar grafo", resultado, explicacion)


@router.post("/comparar")
def comparar(datos: CompararRequest):
    """Ejecuta los algoritmos seleccionados con el mismo grafo, origen y destino."""
    grafo = grafos.normalizar(datos.grafo, datos.dirigido)
    grafos.verificar_nodo(grafo, datos.origen, "origen")
    grafos.verificar_nodo(grafo, datos.destino, "destino")

    filas = []
    for clave in dict.fromkeys(datos.algoritmos):
        resultado, metricas = medir(ALGORITMOS[clave], grafo, datos.origen, datos.destino, datos.coordenadas,
                                    repeticiones=5)
        fila = {"clave": clave, **resultado, **metricas}
        fila["explicacion"] = explicar_algoritmo(clave, resultado)
        filas.append(fila)

    resultado = {
        "algoritmos": filas,
        "tabla": [{columna: fila[columna] for columna in _COLUMNAS_TABLA} for fila in filas],
        "diagrama": grafos.diagrama(grafo, datos.dirigido, datos.coordenadas),
    }
    return respuesta("grafos", "comparar búsquedas", resultado,
                     explicar_comparacion(filas, datos.origen, datos.destino))


@router.post("/alcance")
def calcular_alcance(datos: AlcanceRequest):
    """Nodos alcanzables desde un punto de referencia, opcionalmente limitados por costo o saltos."""
    grafo = grafos.normalizar(datos.grafo, datos.dirigido)
    grafos.verificar_nodo(grafo, datos.origen, "origen")
    resultado, metricas = medir(alcance, grafo, datos.origen, datos.costo_maximo, datos.saltos_maximos)
    resultado["diagrama"] = grafos.diagrama(grafo, datos.dirigido, datos.coordenadas)
    return respuesta("grafos", "alcance", resultado,
                     explicar_alcance(resultado, datos.costo_maximo, datos.saltos_maximos), metricas=metricas)
