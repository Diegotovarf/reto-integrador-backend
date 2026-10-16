from app.services import cadenas, lenguajes
from tests.conftest import verificar_formato


def test_prefijos_sufijos_y_subcadenas():
    assert cadenas.prefijos("ab") == ["", "a", "ab"]
    assert cadenas.sufijos("ab") == ["", "b", "ab"]
    assert cadenas.subcadenas("aba") == ["", "a", "b", "ab", "ba", "aba"]


def test_operaciones_basicas_de_cadenas():
    assert cadenas.operar("longitud", "") == 0
    assert cadenas.operar("inversa", "abc") == "cba"
    assert cadenas.operar("potencia", "ab", n=0) == "ε"
    assert cadenas.operar("potencia", "ab", n=3) == "ababab"
    assert cadenas.operar("palindromo", "abba") is True
    assert cadenas.operar("alfabeto", "abc", sigma=["a", "b"]) == {"pertenece": False, "simbolos_invalidos": ["c"]}


def test_endpoint_cadenas(cliente):
    cuerpo = cliente.post("/cadenas/operar", json={
        "w": "abba", "v": "c", "n": 2, "sigma": ["a", "b"],
        "operaciones": ["longitud", "concatenacion", "potencia", "palindromo", "alfabeto"],
    }).json()
    verificar_formato(cuerpo)
    valores = {r["operacion"]: r["resultado"] for r in cuerpo["resultado"]}
    assert valores == {"longitud": 4, "concatenacion": "abbac", "potencia": "abbaabba",
                       "palindromo": True, "alfabeto": {"pertenece": True, "simbolos_invalidos": []}}
    assert all(r["explicacion"]["resumen"] for r in cuerpo["resultado"])


def test_concatenacion_sin_v_responde_400(cliente):
    respuesta = cliente.post("/cadenas/operar", json={"w": "a", "operaciones": ["concatenacion"]})
    assert respuesta.status_code == 400
    assert "segunda cadena" in respuesta.json()["error"]


def test_cerraduras_y_potencia():
    assert lenguajes.kleene({"a"}, 2) == {"", "a", "aa"}
    assert lenguajes.positiva({"a"}, 2) == {"a", "aa"}
    assert lenguajes.potencia({"a", "b"}, 2) == {"aa", "ab", "ba", "bb"}
    assert lenguajes.potencia({"a"}, 0) == {""}


def test_complemento_dentro_de_sigma_k():
    resultado = lenguajes.operar("complemento", {"", "a"}, set(), ["a", "b"], k=1, n=0)
    assert resultado == {"b"}


def test_endpoint_lenguajes_con_epsilon(cliente):
    cuerpo = cliente.post("/lenguajes/operar", json={
        "L": ["ε", "a"], "M": ["b"], "sigma": ["a", "b"], "k": 1,
        "operaciones": ["union", "concatenacion", "complemento"],
    }).json()
    verificar_formato(cuerpo)
    valores = {r["operacion"]: r["resultado"] for r in cuerpo["resultado"]}
    assert valores["union"] == ["ε", "a", "b"]
    assert valores["concatenacion"] == ["b", "ab"]
    assert valores["complemento"] == ["b"]


def test_complemento_sin_alfabeto_responde_400(cliente):
    respuesta = cliente.post("/lenguajes/operar", json={"L": ["a"], "operaciones": ["complemento"]})
    assert respuesta.status_code == 400


def test_universo_demasiado_grande_responde_400(cliente):
    respuesta = cliente.post("/lenguajes/operar", json={
        "L": ["a"], "sigma": list("abcdefghij"), "k": 10, "operaciones": ["complemento"],
    })
    assert respuesta.status_code == 400
