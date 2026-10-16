from typing import Literal, Optional

from pydantic import BaseModel, Field

Peso = int | float
# {"A": [["B", 15], ["C", 22]]}  o  {"A": {"B": 15, "C": 22}}
ListaAdyacencia = dict[str, list[tuple[str, Peso]] | dict[str, Peso]]

AlgoritmoBusqueda = Literal["bfs", "dfs", "dijkstra", "greedy", "a_estrella", "hill_climbing"]

_GRAFO_EJEMPLO = {
    "A": [["B", 4], ["C", 2]], "B": [["D", 5]], "C": [["B", 1], ["D", 8], ["E", 10]],
    "D": [["E", 2]], "E": [],
}


class GrafoBase(BaseModel):
    grafo: ListaAdyacencia = Field(..., description="Lista de adyacencia: nodo -> [[vecino, peso], ...]")
    dirigido: bool = Field(True, description="Si es false, cada arista se puede recorrer en ambos sentidos.")
    coordenadas: Optional[dict[str, tuple[float, float]]] = Field(
        None, description="Posición (x, y) de cada nodo; si están todas, la heurística es la distancia euclidiana."
    )


class CompararRequest(GrafoBase):
    origen: str
    destino: str
    algoritmos: list[AlgoritmoBusqueda] = Field(
        default_factory=lambda: ["bfs", "dfs", "dijkstra", "hill_climbing"], min_length=1
    )

    model_config = {"json_schema_extra": {"examples": [{
        "grafo": _GRAFO_EJEMPLO, "dirigido": True, "origen": "A", "destino": "E",
        "algoritmos": ["bfs", "dfs", "dijkstra", "greedy", "a_estrella", "hill_climbing"],
    }]}}


class AlcanceRequest(GrafoBase):
    origen: str
    costo_maximo: Optional[float] = Field(None, ge=0, description="Solo nodos con costo mínimo ≤ este valor.")
    saltos_maximos: Optional[int] = Field(None, ge=0, description="Solo nodos a lo más a este número de aristas.")

    model_config = {"json_schema_extra": {"examples": [{
        "grafo": _GRAFO_EJEMPLO, "origen": "A", "costo_maximo": 8,
    }]}}


class GenerarGrafoRequest(BaseModel):
    n: int = Field(8, ge=2, le=30, description="Número de nodos.")
    densidad: float = Field(0.3, ge=0, le=1, description="Probabilidad de cada arista extra (1 = grafo completo).")
    semilla: int = Field(42, description="La misma semilla siempre genera el mismo grafo.")
