import random
from itertools import permutations

import pytest

from app.errores import ErrorEntrada
from app.services import grafos
from app.services.ordenamientos import CATALOGO
from app.services.tsp import tsp_exacto, tsp_voraz
from tests.conftest import verificar_formato

_rng = random.Random(0)
CASOS = [
    [], [1], [2, 1], [3, 3, 3], list(range(20)), list(range(20, 0, -1)),
    [5, -2, 0, 9.5, -2, 3.25],
    [_rng.randint(-50, 50) for _ in range(200)],
]


@pytest.mark.parametrize("clave", list(CATALOGO))
@pytest.mark.parametrize("datos", CASOS)
def test_cada_algoritmo_ordena_correctamente(clave, datos):
    copia = list(datos)
    ordenada, _ = CATALOGO[clave]["funcion"](datos)
    assert ordenada == sorted(datos)
    assert datos == copia, "no debe modificar la entrada"


def test_endpoint_ordenamiento(cliente):
    cuerpo = cliente.post("/benchmark/ordenamiento", json={
        "algoritmos": ["burbuja", "mergesort", "quicksort"], "tamano": 300, "tipo": "inverso",
        "tamanos": [50, 100],
    }).json()
    verificar_formato(cuerpo)
    resultado = cuerpo["resultado"]
    assert all(fila["correcto"] for fila in resultado["algoritmos"])
    assert resultado["datos_ordenados"] == sorted(resultado["datos_entrada"])
    assert len(resultado["grafica"]["tiempo_ms"]) == 3
    assert resultado["escalabilidad"]["tamanos"] == [50, 100]
    assert len(resultado["escalabilidad"]["tiempo_ms"]["burbuja"]) == 2


def test_contadores_en_peor_caso(cliente):
    # Con valores distintos en orden inverso, burbuja hace n(n-1)/2 intercambios.
    cuerpo = cliente.post("/benchmark/ordenamiento", json={
        "algoritmos": ["burbuja", "seleccion"], "datos": list(range(300, 0, -1)),
    }).json()
    filas = {f["clave"]: f for f in cuerpo["resultado"]["algoritmos"]}
    assert filas["burbuja"]["movimientos"] == 300 * 299 // 2
    assert filas["seleccion"]["comparaciones"] == 300 * 299 // 2


def test_ordenamiento_con_datos_propios(cliente):
    cuerpo = cliente.post("/benchmark/ordenamiento", json={
        "algoritmos": ["insercion", "heapsort"], "datos": [3, 1, 2],
    }).json()
    assert cuerpo["resultado"]["datos_ordenados"] == [1, 2, 3]
    assert cuerpo["resultado"]["tipo"] is None


def test_ordenamiento_requiere_dos_algoritmos_distintos(cliente):
    respuesta = cliente.post("/benchmark/ordenamiento", json={"algoritmos": ["burbuja", "burbuja"]})
    assert respuesta.status_code == 422


def _fuerza_bruta(grafo, inicio):
    pesos = {o: dict(v) for o, v in grafo.items()}
    resto = [n for n in grafo if n != inicio]
    return min(
        sum(pesos[a][b] for a, b in zip((inicio, *orden), (*orden, inicio)))
        for orden in permutations(resto)
    )


@pytest.mark.parametrize("semilla", [1, 2, 3])
def test_tsp_exacto_coincide_con_fuerza_bruta(semilla):
    grafo, _ = grafos.generar(7, 1.0, semilla)
    exacto = tsp_exacto(grafo)
    assert exacto["costo"] == _fuerza_bruta(grafo, "A")
    assert sorted(exacto["camino"][:-1]) == sorted(grafo)
    assert tsp_voraz(grafo)["costo"] >= exacto["costo"]


def test_tsp_exacto_limita_nodos():
    grafo, _ = grafos.generar(13, 1.0, 1)
    with pytest.raises(ErrorEntrada):
        tsp_exacto(grafo)


def test_endpoint_tsp(cliente):
    cuerpo = cliente.post("/benchmark/tsp", json={"n": 6, "semilla": 5}).json()
    verificar_formato(cuerpo)
    resultado = cuerpo["resultado"]
    assert resultado["voraz"]["costo"] >= resultado["exacto"]["costo"]
    assert resultado["brecha_porcentaje"] >= 0
    assert "tiempo_ms" in resultado["exacto"] and "memoria_pico_kb" in resultado["exacto"]


def test_endpoint_tsp_cuando_el_voraz_falla(cliente):
    # Desde A el voraz va a B (más barato) y queda sin salida; el circuito A→C→B→A sí existe.
    grafo = {"A": [["B", 1], ["C", 5]], "B": [["A", 1]], "C": [["B", 1]]}
    cuerpo = cliente.post("/benchmark/tsp", json={"grafo": grafo, "dirigido": True, "inicio": "A"}).json()
    assert cuerpo["resultado"]["exacto"]["costo"] == 7
    assert cuerpo["resultado"]["voraz"]["costo"] is None
    assert "no logró" in cuerpo["explicacion"]["resumen"]


def test_endpoint_escalabilidad_tsp(cliente):
    cuerpo = cliente.post("/benchmark/tsp/escalabilidad", json={"tamanos": [4, 6, 8]}).json()
    verificar_formato(cuerpo)
    tabla = cuerpo["resultado"]["tabla"]
    assert [f["n"] for f in tabla] == [4, 6, 8]
    assert tabla[-1]["exacto_estados"] > tabla[0]["exacto_estados"]
    assert cuerpo["resultado"]["grafica"]["n"] == [4, 6, 8]
