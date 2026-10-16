from pydantic import BaseModel, Field


class AutomataBase(BaseModel):
    estados: list[str] = Field(..., min_length=1, description="Conjunto de estados Q.")
    alfabeto: list[str] = Field(..., description="Alfabeto Σ (un carácter por símbolo).")
    inicial: str = Field(..., description="Estado inicial q₀.")
    finales: list[str] = Field(..., description="Estados finales F.")
    cadena: str = Field("", max_length=500, description="Cadena a evaluar. Usa 'ε' o '' para la cadena vacía.")


class AFDRequest(AutomataBase):
    transiciones: dict[str, dict[str, str]] = Field(..., description="δ(estado, símbolo) = estado")

    model_config = {"json_schema_extra": {"examples": [{
        "estados": ["q0", "q1", "q2"], "alfabeto": ["0", "1"], "inicial": "q0", "finales": ["q2"],
        "transiciones": {"q0": {"0": "q1", "1": "q0"}, "q1": {"0": "q1", "1": "q2"}, "q2": {"0": "q1", "1": "q0"}},
        "cadena": "1101",
    }]}}


class AFNDRequest(AutomataBase):
    transiciones: dict[str, dict[str, list[str]]] = Field(
        ..., description="δ(estado, símbolo) = [estados]. En AFND-ε usa la clave 'ε' para transiciones vacías."
    )

    model_config = {"json_schema_extra": {"examples": [{
        "estados": ["q0", "q1", "q2"], "alfabeto": ["a", "b"], "inicial": "q0", "finales": ["q2"],
        "transiciones": {"q0": {"a": ["q0", "q1"], "b": ["q0"]}, "q1": {"b": ["q2"]}},
        "cadena": "aab",
    }]}}
