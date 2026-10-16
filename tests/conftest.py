import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def cliente():
    return TestClient(app)


def verificar_formato(cuerpo: dict) -> None:
    """Toda respuesta exitosa debe tener el formato común y una explicación."""
    assert set(cuerpo) == {"modulo", "operacion", "resultado", "pasos", "explicacion", "metricas"}
    assert cuerpo["explicacion"]["resumen"]
    assert cuerpo["explicacion"]["teoria"]
