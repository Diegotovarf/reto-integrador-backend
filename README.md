# Reto Integrador — Laboratorio de Autómatas, Rutas y Complejidad

Aplicación web para que estudiantes de nuevo ingreso experimenten con autómatas, optimización de rutas y complejidad algorítmica.

| Entrega | Contenido |
|---|---|
| Checkpoint 1 · Backend | API en FastAPI (`app/`, `tests/`) |
| Checkpoint 2 · Frontend | Interfaz gráfica en HTML, CSS y JavaScript ([`frontend/`](frontend/README.md)) |

## Cómo correrlo

Se necesitan dos terminales abiertas en la raíz del repositorio:

```bash
# Terminal 1 · backend (http://localhost:8000)
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 · frontend (http://localhost:5500)
cd frontend
python -m http.server 5500
```

Abre **http://localhost:5500** en el navegador. Los detalles de la interfaz están en [`frontend/README.md`](frontend/README.md).

- Documentación interactiva de la API: http://localhost:8000/docs (cada endpoint trae un ejemplo listo para probar)
- Pruebas: `python -m pytest`

## Arquitectura

Las tres capas del reto quedan separadas en carpetas:

| Capa | Carpeta | Qué hace |
|---|---|---|
| Cómputo determinista | `app/services/` | Los algoritmos, sin dependencias de FastAPI |
| Interpretación y explicabilidad | `app/explicaciones/` | Convierte cada resultado en un resumen y su base teórica |
| API (la consume el frontend) | `app/routers/`, `app/schemas/` | Endpoints y validación de entradas |
| Interfaz gráfica (GUI) | `frontend/` | Formularios, diagramas, tablas y gráficas que consumen la API |

## Formato de respuesta

Todos los endpoints `POST` responden con la misma forma:

```json
{
  "modulo": "automatas",
  "operacion": "AFND",
  "resultado": { "aceptada": true, "diagrama": { "nodos": [], "aristas": [] } },
  "pasos": [ { "paso": 1, "simbolo": "a", "desde": ["q0"], "hacia": ["q0", "q1"] } ],
  "explicacion": { "resumen": "La cadena 'ab' es ACEPTADA…", "teoria": "Un AFND…", "complejidad": "O(|w|·|Q|²)…" },
  "metricas": { "tiempo_ms": 0.01, "memoria_pico_kb": 1.2 }
}
```

Errores en los datos de entrada → `400 {"error": "mensaje"}`. Errores de forma (falta un campo, tipo incorrecto) → `422`, el formato estándar de FastAPI.

## Endpoints

### Módulo 1 · Traductor de lenguajes y verificador de reglas

| Endpoint | Entrada | Operaciones |
|---|---|---|
| `POST /cadenas/operar` | `w`, `v`, `n`, `sigma`, `operaciones` | longitud, inversa, concatenacion, potencia, prefijos, sufijos, subcadenas, palindromo, conteo, alfabeto |
| `POST /lenguajes/operar` | `L`, `M`, `sigma`, `k`, `n`, `operaciones` | union, interseccion, diferencia, diferencia_simetrica, concatenacion, potencia, kleene, positiva, inversa, complemento |
| `GET /automatas/ejemplos` | — | Un AFD, un AFND y un AFND-ε de ejemplo |
| `POST /automatas/afd` | `estados`, `alfabeto`, `transiciones`, `inicial`, `finales`, `cadena` | `transiciones: {"q0": {"a": "q1"}}` |
| `POST /automatas/afnd` | igual | `transiciones: {"q0": {"a": ["q0", "q1"]}}` |
| `POST /automatas/afnd-e` | igual | además la clave `"ε"` para transiciones vacías |

- La cadena vacía se escribe `"ε"` o `""` en la entrada y se devuelve como `"ε"`.
- L*, L⁺ y el complemento son infinitos, por eso se calculan hasta `k` (L* hasta Lᵏ, complemento dentro de Σ^≤k).
- Cada símbolo es un carácter.

### Módulo 2 · Asistente de logística y optimización

| Endpoint | Qué hace |
|---|---|
| `GET /grafos/ejemplos` | Grafos del profesor (10, 25 y 50 nodos) |
| `POST /grafos/generar` | Grafo aleatorio conexo con coordenadas (`n`, `densidad`, `semilla`) |
| `POST /grafos/comparar` | Ejecuta los `algoritmos` elegidos con el mismo grafo, `origen` y `destino`: `bfs`, `dfs`, `dijkstra`, `greedy`, `a_estrella`, `hill_climbing` |
| `POST /grafos/alcance` | Nodos alcanzables desde `origen`, con `costo_maximo` y `saltos_maximos` opcionales |

- Formato del grafo (el mismo de los archivos del profesor): `{"A": [["B", 15], ["C", 22]], ...}`. También se acepta `{"A": {"B": 15}}`.
- `dirigido: false` hace que cada arista se pueda recorrer en ambos sentidos.
- `coordenadas` (opcional) permite usar la distancia euclidiana como heurística. Sin coordenadas se usa el número mínimo de aristas hasta el destino.
- `resultado.tabla` trae camino, costo, nodos expandidos, tiempo y memoria de cada algoritmo. `resultado.diagrama` trae los nodos y aristas para dibujar el grafo y resaltar la ruta.

### Módulo 3 · Auditoría de escalabilidad y benchmark

| Endpoint | Qué hace |
|---|---|
| `GET /benchmark/ordenamiento/catalogo` | Algoritmos disponibles con su complejidad teórica |
| `POST /benchmark/ordenamiento` | Ordena los mismos datos con ≥ 2 `algoritmos` y compara tiempo, memoria, comparaciones y movimientos |
| `POST /benchmark/tsp` | Agente Viajero: exacto (Held-Karp) contra voraz (vecino más cercano) |
| `POST /benchmark/tsp/escalabilidad` | Curva de tiempo y memoria del exacto contra el voraz al crecer `n` (P vs NP, espacio) |

- Algoritmos de ordenamiento: `burbuja`, `seleccion`, `insercion`, `shell`, `mergesort`, `quicksort`, `heapsort`, `timsort`.
- Datos: los tuyos en `datos`, o generados con `tamano` (máx. 2000), `tipo` (`aleatorio`, `ordenado`, `inverso`, `casi_ordenado`, `pocos_unicos`) y `semilla`.
- `tamanos: [100, 500, 1000]` agrega una curva de escalabilidad (`resultado.escalabilidad`). `resultado.grafica` viene lista para la gráfica comparativa.
- El límite de 2000 elementos existe porque medir la memoria con `tracemalloc` hace unas 30 veces más lentos a los algoritmos O(n²). Con los 8 algoritmos y 2000 elementos la respuesta tarda unos 18 s; con 1000 elementos y 4 algoritmos, unos 3 s.
- El TSP exacto acepta hasta 12 nodos, porque su costo crece como 2ⁿ.
