from fastapi import APIRouter

from app.explicaciones.lenguajes import (
    TEORIA_GENERAL_CADENAS, TEORIA_GENERAL_LENGUAJES, NOMBRES_LENGUAJES,
    explicar_cadena, explicar_lenguaje,
)
from app.respuesta import crear_explicacion, respuesta
from app.schemas.lenguajes import CadenasRequest, LenguajesRequest
from app.services import cadenas, lenguajes
from app.services.cadenas import mostrar, mostrar_lista

router = APIRouter(tags=["Módulo 1 · Cadenas y lenguajes"])


@router.post("/cadenas/operar")
def operar_cadenas(datos: CadenasRequest):
    """Aplica una o varias operaciones a la cadena w."""
    resultados = []
    for operacion in datos.operaciones:
        valor = cadenas.operar(operacion, datos.w, datos.v, datos.n, datos.sigma)
        resultados.append({
            "operacion": operacion,
            "resultado": valor,
            "explicacion": explicar_cadena(operacion, datos.w, datos.v, datos.n, valor),
        })
    resumen = f"Se aplicaron {len(resultados)} operación(es) a w = '{mostrar(datos.w)}'."
    return respuesta("lenguajes", "operaciones con cadenas", resultados,
                     crear_explicacion(resumen, TEORIA_GENERAL_CADENAS))


@router.post("/lenguajes/operar")
def operar_lenguajes(datos: LenguajesRequest):
    """Aplica una o varias operaciones a los lenguajes L y M."""
    L, M = set(datos.L), set(datos.M)
    resultados = []
    for operacion in datos.operaciones:
        conjunto = lenguajes.operar(operacion, L, M, datos.sigma, datos.k, datos.n)
        universo = lenguajes.tamano_universo(datos.sigma, datos.k) if operacion == "complemento" else None
        resultados.append({
            "operacion": operacion,
            "nombre": NOMBRES_LENGUAJES[operacion],
            "resultado": mostrar_lista(conjunto),
            "cardinalidad": len(conjunto),
            "explicacion": explicar_lenguaje(operacion, L, M, datos.k, datos.n, conjunto, universo),
        })
    resumen = (f"Se aplicaron {len(resultados)} operación(es) a L = {{{', '.join(mostrar_lista(L))}}}"
               f" y M = {{{', '.join(mostrar_lista(M))}}}.")
    return respuesta("lenguajes", "operaciones con lenguajes", resultados,
                     crear_explicacion(resumen, TEORIA_GENERAL_LENGUAJES))
