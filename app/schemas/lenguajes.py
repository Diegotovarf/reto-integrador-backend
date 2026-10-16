from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.services.cadenas import normalizar

OperacionCadena = Literal[
    "longitud", "inversa", "concatenacion", "potencia", "prefijos",
    "sufijos", "subcadenas", "palindromo", "conteo", "alfabeto",
]

OperacionLenguaje = Literal[
    "union", "interseccion", "diferencia", "diferencia_simetrica", "concatenacion",
    "potencia", "kleene", "positiva", "inversa", "complemento",
]


class CadenasRequest(BaseModel):
    w: str = Field(..., max_length=200, description="Cadena principal. Usa 'ε' o '' para la cadena vacía.")
    v: Optional[str] = Field(None, max_length=200, description="Segunda cadena (para concatenación).")
    n: Optional[int] = Field(None, ge=0, le=50, description="Exponente (para potencia).")
    sigma: Optional[list[str]] = Field(None, description="Alfabeto (para verificar w ∈ Σ*).")
    operaciones: list[OperacionCadena] = Field(..., min_length=1)

    model_config = {"json_schema_extra": {"examples": [{
        "w": "abba", "v": "ca", "n": 2, "sigma": ["a", "b"],
        "operaciones": ["longitud", "inversa", "concatenacion", "potencia", "palindromo", "alfabeto"],
    }]}}

    @field_validator("w", "v")
    @classmethod
    def _cadena_vacia(cls, valor):
        return normalizar(valor) if valor is not None else None


class LenguajesRequest(BaseModel):
    L: list[str] = Field(default_factory=list, max_length=500)
    M: list[str] = Field(default_factory=list, max_length=500)
    sigma: list[str] = Field(default_factory=list, max_length=20, description="Alfabeto (para el complemento).")
    k: int = Field(3, ge=0, le=10, description="Cota para L*, L⁺ y Σ^≤k.")
    n: int = Field(2, ge=0, le=10, description="Exponente para Lⁿ.")
    operaciones: list[OperacionLenguaje] = Field(..., min_length=1)

    model_config = {"json_schema_extra": {"examples": [{
        "L": ["a", "ab"], "M": ["ab", "b"], "sigma": ["a", "b"], "k": 2, "n": 2,
        "operaciones": ["union", "interseccion", "concatenacion", "kleene", "complemento"],
    }]}}

    @field_validator("L", "M")
    @classmethod
    def _cadenas_vacias(cls, valores):
        return [normalizar(c) for c in valores]

    @field_validator("sigma")
    @classmethod
    def _alfabeto(cls, valores):
        return sorted(set(valores))
