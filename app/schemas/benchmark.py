from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.grafos import ListaAdyacencia

AlgoritmoOrdenamiento = Literal[
    "burbuja", "seleccion", "insercion", "shell", "mergesort", "quicksort", "heapsort", "timsort",
]
TipoDatos = Literal["aleatorio", "ordenado", "inverso", "casi_ordenado", "pocos_unicos"]

# Medir la memoria con tracemalloc hace ~30 veces más lentos a los algoritmos O(n²);
# con 2000 elementos el peor caso (burbuja + selección + inserción) sigue en segundos.
MAX_ELEMENTOS = 2000


class OrdenamientoRequest(BaseModel):
    algoritmos: list[AlgoritmoOrdenamiento] = Field(..., min_length=2, description="Al menos 2 algoritmos.")
    datos: Optional[list[int | float]] = Field(
        None, min_length=1, max_length=MAX_ELEMENTOS, description="Datos propios. Si se omiten, se generan."
    )
    tamano: int = Field(1000, ge=1, le=MAX_ELEMENTOS, description="Cantidad de datos a generar.")
    tipo: TipoDatos = "aleatorio"
    semilla: int = 42
    tamanos: Optional[list[int]] = Field(
        None, max_length=6, description="Tamaños extra para la curva de escalabilidad, ej. [100, 500, 1000]."
    )
    incluir_datos: bool = Field(True, description="Devolver los datos de entrada y la lista ordenada.")

    model_config = {"json_schema_extra": {"examples": [{
        "algoritmos": ["burbuja", "insercion", "mergesort", "quicksort"],
        "tamano": 1000, "tipo": "aleatorio", "tamanos": [100, 500, 1000],
    }]}}

    @field_validator("algoritmos")
    @classmethod
    def _distintos(cls, valores):
        unicos = list(dict.fromkeys(valores))
        if len(unicos) < 2:
            raise ValueError("Selecciona al menos 2 algoritmos distintos.")
        return unicos

    @field_validator("tamanos")
    @classmethod
    def _tamanos(cls, valores):
        if valores is None:
            return None
        if any(t < 1 or t > MAX_ELEMENTOS for t in valores):
            raise ValueError(f"Cada tamaño debe estar entre 1 y {MAX_ELEMENTOS}.")
        return sorted(set(valores))


class TSPRequest(BaseModel):
    grafo: Optional[ListaAdyacencia] = Field(None, description="Grafo propio. Si se omite, se genera uno completo.")
    dirigido: bool = False
    n: int = Field(6, ge=3, le=12, description="Nodos del grafo generado.")
    semilla: int = 42
    inicio: Optional[str] = None


class TSPEscalabilidadRequest(BaseModel):
    tamanos: list[int] = Field(default_factory=lambda: [4, 6, 8, 10], min_length=1, max_length=8)
    semilla: int = 42

    @field_validator("tamanos")
    @classmethod
    def _tamanos(cls, valores):
        if any(t < 3 or t > 12 for t in valores):
            raise ValueError("Cada tamaño debe estar entre 3 y 12 nodos.")
        return sorted(set(valores))
