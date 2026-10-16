import json
from pathlib import Path

from fastapi import APIRouter

from app.explicaciones.automatas import explicar
from app.respuesta import respuesta
from app.schemas.automatas import AFDRequest, AFNDRequest
from app.services import automatas

router = APIRouter(prefix="/automatas", tags=["Módulo 1 · Autómatas"])

_EJEMPLOS = Path(__file__).resolve().parent.parent / "datos" / "automatas_ejemplo.json"


def _parametros(datos):
    return (datos.estados, datos.alfabeto, datos.transiciones, datos.inicial, datos.finales, datos.cadena)


@router.get("/ejemplos")
def ejemplos():
    """Autómatas de ejemplo listos para enviar a cada endpoint."""
    return json.loads(_EJEMPLOS.read_text(encoding="utf-8"))


@router.post("/afd")
def evaluar_afd(datos: AFDRequest):
    resultado, pasos = automatas.evaluar_afd(*_parametros(datos))
    return respuesta("automatas", "AFD", resultado, explicar("afd", resultado, pasos), pasos)


@router.post("/afnd")
def evaluar_afnd(datos: AFNDRequest):
    resultado, pasos = automatas.evaluar_afnd(*_parametros(datos))
    return respuesta("automatas", "AFND", resultado, explicar("afnd", resultado, pasos), pasos)


@router.post("/afnd-e")
def evaluar_afnd_epsilon(datos: AFNDRequest):
    resultado, pasos = automatas.evaluar_afnd_epsilon(*_parametros(datos))
    return respuesta("automatas", "AFND-ε", resultado, explicar("afnd-e", resultado, pasos), pasos)
