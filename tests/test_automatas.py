import pytest

from tests.conftest import verificar_formato

AFD = {
    "estados": ["q0", "q1", "q2"], "alfabeto": ["0", "1"], "inicial": "q0", "finales": ["q2"],
    "transiciones": {"q0": {"0": "q1", "1": "q0"}, "q1": {"0": "q1", "1": "q2"}, "q2": {"0": "q1", "1": "q0"}},
}
AFND = {
    "estados": ["q0", "q1", "q2"], "alfabeto": ["a", "b"], "inicial": "q0", "finales": ["q2"],
    "transiciones": {"q0": {"a": ["q0", "q1"], "b": ["q0"]}, "q1": {"b": ["q2"]}},
}
AFND_E = {
    "estados": ["q0", "q1"], "alfabeto": ["a", "b"], "inicial": "q0", "finales": ["q1"],
    "transiciones": {"q0": {"a": ["q0"], "ε": ["q1"]}, "q1": {"b": ["q1"]}},
}


@pytest.mark.parametrize("cadena, aceptada", [("1101", True), ("01", True), ("110", False), ("", False)])
def test_afd(cliente, cadena, aceptada):
    cuerpo = cliente.post("/automatas/afd", json={**AFD, "cadena": cadena}).json()
    verificar_formato(cuerpo)
    assert cuerpo["resultado"]["aceptada"] is aceptada
    assert len(cuerpo["pasos"]) == len(cadena)


def test_afd_recorrido(cliente):
    cuerpo = cliente.post("/automatas/afd", json={**AFD, "cadena": "1101"}).json()
    assert cuerpo["resultado"]["recorrido"] == ["q0", "q0", "q0", "q1", "q2"]
    assert "q0 —1→ q0" in cuerpo["explicacion"]["resumen"]


def test_afd_sin_transicion_rechaza(cliente):
    incompleto = {**AFD, "transiciones": {"q0": {"0": "q1"}}, "cadena": "01"}
    cuerpo = cliente.post("/automatas/afd", json=incompleto).json()
    assert cuerpo["resultado"]["aceptada"] is False
    assert "δ(q1, 1)" in cuerpo["resultado"]["motivo"]
    assert cuerpo["resultado"]["afd_completo"] is False


def test_afd_simbolo_fuera_del_alfabeto(cliente):
    cuerpo = cliente.post("/automatas/afd", json={**AFD, "cadena": "102"}).json()
    assert cuerpo["resultado"]["aceptada"] is False
    assert "'2'" in cuerpo["resultado"]["motivo"]


def test_afd_estado_inicial_invalido_responde_400(cliente):
    respuesta = cliente.post("/automatas/afd", json={**AFD, "inicial": "qx", "cadena": "1"})
    assert respuesta.status_code == 400


@pytest.mark.parametrize("cadena, aceptada", [("aab", True), ("ab", True), ("aba", False), ("", False)])
def test_afnd(cliente, cadena, aceptada):
    cuerpo = cliente.post("/automatas/afnd", json={**AFND, "cadena": cadena}).json()
    verificar_formato(cuerpo)
    assert cuerpo["resultado"]["aceptada"] is aceptada


def test_afnd_conjuntos_activos(cliente):
    cuerpo = cliente.post("/automatas/afnd", json={**AFND, "cadena": "ab"}).json()
    assert cuerpo["resultado"]["recorrido"] == [["q0"], ["q0", "q1"], ["q0", "q2"]]


def test_afnd_rechaza_transiciones_epsilon(cliente):
    respuesta = cliente.post("/automatas/afnd", json={**AFND_E, "cadena": "a"})
    assert respuesta.status_code == 400
    assert "AFND-ε" in respuesta.json()["error"]


@pytest.mark.parametrize("cadena, aceptada", [("aabb", True), ("", True), ("b", True), ("ε", True), ("aba", False)])
def test_afnd_epsilon(cliente, cadena, aceptada):
    cuerpo = cliente.post("/automatas/afnd-e", json={**AFND_E, "cadena": cadena}).json()
    verificar_formato(cuerpo)
    assert cuerpo["resultado"]["aceptada"] is aceptada


def test_afnd_epsilon_clausuras(cliente):
    cuerpo = cliente.post("/automatas/afnd-e", json={**AFND_E, "cadena": "a"}).json()
    assert cuerpo["resultado"]["clausuras"] == {"q0": ["q0", "q1"], "q1": ["q1"]}
    assert cuerpo["pasos"][0]["clausura"] == ["q0", "q1"]


def test_ejemplos_de_automatas_funcionan(cliente):
    ejemplos = cliente.get("/automatas/ejemplos").json()
    for tipo, ejemplo in ejemplos.items():
        datos = {k: v for k, v in ejemplo.items() if k != "descripcion"}
        cuerpo = cliente.post(f"/automatas/{tipo}", json=datos).json()
        assert cuerpo["resultado"]["aceptada"] is True
