"""Formato común de respuesta para todos los endpoints.

Cada respuesta tiene la misma forma para que el frontend pueda renderizarla igual:

    {
        "modulo":      módulo del producto,
        "operacion":   operación ejecutada,
        "resultado":   datos calculados (cómputo determinista),
        "pasos":       traza paso a paso (para animaciones o tablas),
        "explicacion": {"resumen", "teoria", "complejidad"} (capa de interpretación),
        "metricas":    tiempo, memoria u otros contadores
    }
"""
from typing import Any, Optional


def crear_explicacion(resumen: str, teoria: str, complejidad: Optional[str] = None) -> dict:
    explicacion = {"resumen": resumen, "teoria": teoria}
    if complejidad:
        explicacion["complejidad"] = complejidad
    return explicacion


def respuesta(modulo: str, operacion: str, resultado: Any, explicacion: dict,
              pasos: Optional[list] = None, metricas: Optional[dict] = None) -> dict:
    return {
        "modulo": modulo,
        "operacion": operacion,
        "resultado": resultado,
        "pasos": pasos or [],
        "explicacion": explicacion,
        "metricas": metricas or {},
    }
