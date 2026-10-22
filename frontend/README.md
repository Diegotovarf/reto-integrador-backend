# Reto Integrador · Frontend

Interfaz gráfica del laboratorio de autómatas, rutas y complejidad. Consume la API de FastAPI del Checkpoint 1.

Está hecha con **HTML, CSS y JavaScript puro**: no hay que instalar nada ni compilar. Las gráficas usan [Chart.js 4.4.1](https://www.chartjs.org/) desde un CDN y los diagramas de autómatas y grafos se dibujan en SVG con código propio.

## Cómo correrlo

Se necesitan dos terminales.

```bash
# Terminal 1 · backend (puerto 8000), desde la carpeta donde está requirements.txt
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 · frontend (puerto 5500)
cd frontend
python -m http.server 5500
```

Abre **http://localhost:5500**. Arriba a la derecha aparece **Backend conectado** en verde. Si el backend corre en otra dirección, haz clic en ese indicador y cambia la URL.

> El frontend se sirve con `http.server` porque los navegadores no cargan módulos de JavaScript (`type="module"`) cuando abres el archivo con doble clic (`file://`).

## Estructura

```
frontend/
├── index.html        Estructura de la página: encabezado, pestañas y las 3 secciones
├── css/estilos.css   Diseño visual (colores, tarjetas, tablas, diagramas)
└── js/
    ├── main.js       Arranque: pestañas, indicador de conexión, inicia los 3 módulos
    ├── api.js        get() y post() hacia el backend y traducción de errores 400/422
    ├── ui.js         Componentes reutilizables: tablas, explicaciones, gráficas, avisos
    ├── diagrama.js   Dibuja autómatas y grafos en SVG y resalta rutas y estados
    ├── modulo1.js    Cadenas, lenguajes y simulador de autómatas
    ├── modulo2.js    Grafos: comparar algoritmos de búsqueda y alcance
    └── modulo3.js    Benchmark de ordenamiento, TSP y su escalabilidad
```

### Cómo se conecta con el backend

Todas las respuestas del backend tienen la misma forma (`modulo`, `operacion`, `resultado`, `pasos`, `explicacion`, `metricas`). Por eso el frontend reutiliza los mismos componentes en los tres módulos:

| Parte de la respuesta | Componente que la muestra |
|---|---|
| `resultado` | Tablas, tarjetas, conjuntos y diagramas propios de cada operación |
| `resultado.diagrama` | `dibujarDiagrama()` en SVG (autómatas y grafos usan el mismo formato) |
| `pasos` | Tabla de traza y reproductor paso a paso del autómata |
| `explicacion` | Recuadro azul "¿Qué pasó?" con resumen, complejidad y base teórica |
| `metricas` | Indicadores de tiempo (ms) y memoria (KB) |
| Errores 400 / 422 | Recuadro rojo y aviso flotante con el mensaje del backend |

## Pensado para principiantes

El producto está dirigido a estudiantes de nuevo ingreso, así que la interfaz explica todo en lenguaje sencillo:

- **Pestaña Inicio**: qué hace cada módulo con un ejemplo de la vida diaria, cómo usar la página, las 3 capas de la arquitectura y un glosario.
- **Recuadro amarillo "¿Qué es esto?"** en cada sección: explicación sencilla, analogía ("piénsalo así") y pasos a seguir.
- **Etiquetas en español sencillo**: por ejemplo "Letras permitidas Σ", "Reglas de movimiento δ" o "Presupuesto máximo", y debajo de cada operación o algoritmo una frase que dice qué hace.
- **"📖 Cómo leer esto"** junto a cada tabla y gráfica.
- **Recuadro azul "💡 ¿Qué pasó?"** con la explicación que genera el backend y su base teórica.

## Los 3 apartados y sus componentes

### Módulo 1 · Lenguajes y autómatas

| Pestaña | Endpoint | Componentes de la GUI |
|---|---|---|
| Cadenas | `POST /cadenas/operar` | Campos w, v, n, Σ · casillas de operaciones · una tarjeta por resultado con su teoría |
| Lenguajes | `POST /lenguajes/operar` | Campos L, M, Σ · deslizador de la cota k · conjuntos resultado con su cardinalidad |
| Autómatas | `GET /automatas/ejemplos`, `POST /automatas/{afd,afnd,afnd-e}` | Editor de la 5-tupla · diagrama de estados · cinta de entrada · reproductor ⏮ ◀ ▶ ⏭ · tabla de traza · veredicto · prueba de varias cadenas a la vez |

Las transiciones se escriben una por línea: `q0 a -> q1` (en AFND: `q0 a -> q0 q1`, y en AFND-ε: `q0 ε -> q1`).

### Módulo 2 · Logística y rutas

| Sección | Endpoint | Componentes de la GUI |
|---|---|---|
| Elegir grafo | `GET /grafos/ejemplos`, `POST /grafos/generar` | Selector (grafo pequeño, grafos del profesor de 10/25/50 nodos, aleatorio) · deslizadores n y densidad · editor JSON |
| Comparar rutas | `POST /grafos/comparar` | Origen/destino · casillas de 6 algoritmos · tabla comparativa con el óptimo marcado (⭐) · clic en una fila para dibujar su ruta · gráfica de barras por métrica · detalle del algoritmo |
| Alcance | `POST /grafos/alcance` | Costo y saltos máximos · árbol de caminos mínimos resaltado · tabla de nodos alcanzables y lista de los que quedan fuera |

### Módulo 3 · Escalabilidad y benchmark

| Pestaña | Endpoint | Componentes de la GUI |
|---|---|---|
| Ordenamiento | `GET /benchmark/ordenamiento/catalogo`, `POST /benchmark/ordenamiento` | Catálogo con complejidades · tamaño n · tipo de datos · ranking 🥇🥈🥉 · barras de tiempo, comparaciones, movimientos y memoria · curva de escalabilidad · tabla con verificación de que ordenó bien |
| Agente viajero | `POST /benchmark/tsp` | Número de ciudades · dos diagramas lado a lado (exacto contra voraz) · brecha porcentual |
| Escalabilidad TSP | `POST /benchmark/tsp/escalabilidad` | Curvas de tiempo y memoria · escala logarítmica · tabla de mediciones |

En todos los resultados se puede abrir **Ver la respuesta JSON del backend** para mostrar exactamente lo que respondió la API.

## Guion sugerido para la demostración (≈ 8 min)

1. **Arranque**: muestra las dos terminales corriendo y el indicador verde **Backend conectado**.
2. **Módulo 1 · Autómatas**: con el AFD de ejemplo evalúa `1101`, presiona **Reproducir** y explica cómo avanza la cinta. Luego usa **Probar todas** para ver qué acepta y qué rechaza. Cambia a AFND-ε para mostrar las cerraduras-ε.
3. **Módulo 1 · Cadenas y lenguajes**: aplica todas las operaciones a `abba` y muestra una tarjeta con su teoría.
4. **Módulo 2**: carga el grafo del profesor de 25 nodos y compara los 6 algoritmos de A a Y. Haz clic en BFS y luego en Dijkstra para mostrar que el camino con menos saltos no siempre es el más barato. Después calcula el alcance con un costo máximo.
5. **Módulo 3**: corre el benchmark con n = 1000 y señala cómo se curva hacia arriba la línea de burbuja. Luego resuelve el TSP con 10 ciudades y abre la escalabilidad en escala logarítmica para explicar P vs NP.
6. **Errores**: escribe un estado inicial que no exista para mostrar que la interfaz explica el error en lugar de fallar.
