import pytest

from app.services import busquedas, grafos
from tests.conftest import verificar_formato

# Caminos A→E: A-C-B-D-E = 10 (óptimo), A-B-D-E = 11, A-C-E = 12 (menos saltos), A-C-D-E = 12.
GRAFO = {
    "A": [["B", 4], ["C", 2]], "B": [["D", 5]], "C": [["B", 1], ["D", 8], ["E", 10]],
    "D": [["E", 2]], "E": [],
}


def _normalizado():
    return grafos.normalizar(GRAFO)


def test_dijkstra_y_a_estrella_encuentran_el_optimo():
    g = _normalizado()
    for algoritmo in (busquedas.dijkstra, busquedas.a_estrella):
        resultado = algoritmo(g, "A", "E")
        assert resultado["camino"] == ["A", "C", "B", "D", "E"]
        assert resultado["costo"] == 10


def test_bfs_minimiza_saltos_no_costo():
    resultado = busquedas.bfs(_normalizado(), "A", "E")
    assert resultado["camino"] == ["A", "C", "E"]
    assert resultado["costo"] == 12


def test_dfs_sigue_el_primer_vecino():
    resultado = busquedas.dfs(_normalizado(), "A", "E")
    assert resultado["camino"] == ["A", "B", "D", "E"]


def test_origen_igual_a_destino():
    for algoritmo in busquedas.ALGORITMOS.values():
        resultado = algoritmo(_normalizado(), "B", "B")
        assert resultado["camino"] == ["B"] and resultado["costo"] == 0


def test_hill_climbing_se_atora_en_callejon():
    # B está cerca del destino D pero no tiene salida; el camino real es A→C→D.
    g = grafos.normalizar({"A": [["B", 1], ["C", 1]], "B": [], "C": [["D", 1]], "D": []})
    coordenadas = {"A": (0, 0), "B": (9, 0), "C": (0, 5), "D": (10, 0)}
    resultado = busquedas.hill_climbing(g, "A", "D", coordenadas)
    assert resultado["encontrado"] is False
    assert "Callejón" in resultado["motivo_parada"]
    assert busquedas.bfs(g, "A", "D")["camino"] == ["A", "C", "D"]


def test_grafo_no_dirigido_agrega_aristas_inversas():
    g = grafos.normalizar({"A": [["B", 3]]}, dirigido=False)
    assert g == {"A": [("B", 3)], "B": [("A", 3)]}


def test_comparar_endpoint(cliente):
    cuerpo = cliente.post("/grafos/comparar", json={
        "grafo": GRAFO, "origen": "A", "destino": "E",
        "algoritmos": ["bfs", "dfs", "dijkstra", "greedy", "a_estrella", "hill_climbing"],
    }).json()
    verificar_formato(cuerpo)
    tabla = {fila["algoritmo"]: fila for fila in cuerpo["resultado"]["tabla"]}
    assert tabla["Dijkstra"]["costo"] == 10
    assert all("tiempo_ms" in fila and "memoria_pico_kb" in fila for fila in tabla.values())
    assert len(cuerpo["resultado"]["diagrama"]["aristas"]) == 7
    assert "10" in cuerpo["explicacion"]["resumen"]


def test_comparar_con_grafos_del_profesor(cliente):
    ejemplos = cliente.get("/grafos/ejemplos").json()
    for nombre, ejemplo in ejemplos.items():
        nodos = list(ejemplo["grafo"])
        cuerpo = cliente.post("/grafos/comparar", json={
            "grafo": ejemplo["grafo"], "origen": nodos[0], "destino": nodos[-1],
            "algoritmos": list(busquedas.ALGORITMOS),
        }).json()
        filas = {f["clave"]: f for f in cuerpo["resultado"]["algoritmos"]}
        optimo = filas["dijkstra"]["costo"]
        assert optimo is not None, nombre
        assert filas["a_estrella"]["costo"] == optimo, nombre
        assert all(f["costo"] >= optimo for f in filas.values() if f["encontrado"]), nombre


def test_alcance_con_costo_maximo(cliente):
    cuerpo = cliente.post("/grafos/alcance", json={"grafo": GRAFO, "origen": "A", "costo_maximo": 8}).json()
    verificar_formato(cuerpo)
    resultado = cuerpo["resultado"]
    assert [a["nodo"] for a in resultado["alcanzables"]] == ["A", "C", "B", "D"]
    assert resultado["no_alcanzables"] == ["E"]
    assert resultado["mas_lejano"]["nodo"] == "D"


@pytest.mark.parametrize("datos", [
    {"grafo": {"A": [["B", -1]]}, "origen": "A", "destino": "B"},
    {"grafo": GRAFO, "origen": "Z", "destino": "E"},
])
def test_entradas_invalidas_responden_400(cliente, datos):
    assert cliente.post("/grafos/comparar", json=datos).status_code == 400


def test_generar_grafo_completo_y_reproducible(cliente):
    peticion = {"n": 6, "densidad": 1, "semilla": 7}
    primero = cliente.post("/grafos/generar", json=peticion).json()["resultado"]
    segundo = cliente.post("/grafos/generar", json=peticion).json()["resultado"]
    assert primero == segundo
    assert all(len(vecinos) == 5 for vecinos in primero["grafo"].values())
    assert len(primero["diagrama"]["aristas"]) == 15


def test_generar_grafo_disperso_es_conexo():
    g, _ = grafos.generar(20, 0, semilla=3)
    assert len(busquedas.alcance(g, "A")["alcanzables"]) == 20
