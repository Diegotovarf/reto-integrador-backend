// Módulo 2 · Asistente de logística y optimización
// Endpoints: GET /grafos/ejemplos, POST /grafos/generar, POST /grafos/comparar, POST /grafos/alcance
import { get, post } from "./api.js";
import { aristasDeCamino, dibujarDiagrama } from "./diagrama.js";
import {
  $, $$, COLORES, aviso, casillasHTML, comoLeerHTML, ejecutar, enlazarRangos, enlazarSelector, esc, explicacionHTML,
  flecha, grafica, guiaHTML, insignia, jsonHTML, marcadas, metricasHTML, numero, selectorHTML, subpestanas, tablaHTML,
} from "./ui.js";

// [clave, nombre, idea en pocas palabras, explicación al pasar el cursor]
const ALGORITMOS = [
  ["bfs", "BFS", "revisa por capas, como ondas en el agua",
    "Búsqueda en anchura: primero visita todos los vecinos, luego los vecinos de los vecinos... Encuentra el camino con menos paradas, aunque no siempre el más barato."],
  ["dfs", "DFS", "sigue un camino hasta el fondo y regresa",
    "Búsqueda en profundidad: avanza lo más lejos posible por un camino y, si no llega, regresa a probar otro. Gasta poca memoria pero puede dar rodeos."],
  ["dijkstra", "Dijkstra", "siempre sigue lo más barato; da el mejor",
    "Expande siempre el lugar al que es más barato llegar desde el origen. Garantiza el camino de menor costo."],
  ["greedy", "Greedy", "va hacia lo que parece más cerca",
    "Voraz: elige siempre el lugar que parece más cerca del destino (heurística). Es rápido pero puede equivocarse."],
  ["a_estrella", "A*", "lo recorrido + lo que falta; da el mejor",
    "Combina lo que ya costó llegar con una estimación de lo que falta. Encuentra el mejor camino revisando menos lugares que Dijkstra."],
  ["hill_climbing", "Hill-Climbing", "solo da pasos que mejoran",
    "Escalada: siempre da el paso que más lo acerca al destino y nunca retrocede. Es muy rápido pero se puede atorar."],
];

const GRAFO_PEQUENO = {
  A: [["B", 4], ["C", 2]], B: [["D", 5]], C: [["B", 1], ["D", 8], ["E", 10]], D: [["E", 2]], E: [],
};

const PLANTILLA = `
  ${guiaHTML({
    texto: "Un <b>grafo</b> es como un mapa: los <b>círculos (nodos)</b> son lugares, las <b>líneas (aristas)</b> son caminos y el <b>número</b> sobre cada línea es lo que cuesta recorrerlo (kilómetros, minutos o pesos). Un <b>algoritmo de búsqueda</b> es una estrategia para encontrar cómo ir de un lugar a otro.",
    ejemplo: "es lo que hace una app de mapas o de repartidores: hay muchas formas de buscar la ruta y no todas encuentran la más barata.",
    pasos: [
      "Elige un mapa (grafo) y presiona <b>Cargar grafo</b>. Ya hay uno pequeño cargado.",
      "En <b>Comparar rutas</b> elige el origen y el destino, y presiona <b>Comparar algoritmos</b>.",
      "Revisa la tabla y haz clic en cada algoritmo para ver su ruta pintada en el mapa.",
    ],
  })}
  <div class="rejilla-lateral">
    <div class="columna-controles">
      <form class="tarjeta" id="form-grafo">
        <h3>Paso 1 · Elige el mapa (grafo)</h3>
        <label>¿Qué mapa quieres usar?
          <select name="fuente">
            <option value="pequeno">Mapa pequeño de ejemplo (5 lugares)</option>
            <option value="grafo-10">Grafo del profesor · 10 lugares</option>
            <option value="grafo-25">Grafo del profesor · 25 lugares</option>
            <option value="grafo-50">Grafo del profesor · 50 lugares</option>
            <option value="aleatorio">Generar uno al azar</option>
          </select>
        </label>
        <div class="campos" data-aleatorio hidden>
          <label>Lugares (nodos) = <output></output><input type="range" name="n" min="2" max="30" value="10"></label>
          <label>Cantidad de caminos = <output></output><small>0 = pocos caminos, 1 = todos conectados</small><input type="range" name="densidad" min="0" max="1" step="0.05" value="0.25"></label>
          <label>Semilla <small>el mismo número da el mismo mapa</small><input type="number" name="semilla" value="42"></label>
        </div>
        <div class="acciones"><button class="primario">Cargar grafo</button></div>
        <details>
          <summary>Avanzado: ver o editar el mapa en texto (JSON)</summary>
          <p class="ayuda"><code>{"A": [["B", 15]]}</code> significa: de A sale un camino a B que cuesta 15.</p>
          <textarea name="json" rows="8" spellcheck="false"></textarea>
          <label class="check"><input type="checkbox" name="dirigido"> Calles de un solo sentido (grafo dirigido)</label>
          <button type="button" data-aplicar>Aplicar cambios</button>
        </details>
        <p class="info-grafo ayuda"></p>
      </form>

      <div class="tarjeta">
        <h3>Paso 2 · ¿Qué quieres hacer?</h3>
        <div class="subtabs">
          <button type="button" data-sub="rutas">🧭 Buscar ruta</button>
          <button type="button" data-sub="alcance">📍 ¿Hasta dónde llego?</button>
        </div>
        <form data-panel="rutas" id="form-rutas">
          <p class="ayuda">Busca cómo ir de un lugar a otro con varias estrategias y compáralas.</p>
          <div class="campos">
            <label>Salgo de (origen) <select name="origen" class="nodos"></select></label>
            <label>Quiero llegar a (destino) <select name="destino" class="nodos"></select></label>
          </div>
          <fieldset><legend>Estrategias a comparar (pasa el cursor para saber más)</legend>${casillasHTML("alg", ALGORITMOS)}</fieldset>
          <div class="acciones"><button class="primario">Comparar algoritmos</button></div>
        </form>
        <form data-panel="alcance" id="form-alcance">
          <p class="ayuda">¿A qué lugares puedo llegar desde un punto? Por ejemplo: "si solo tengo 100 de presupuesto" o "si solo puedo hacer 2 transbordos".</p>
          <div class="campos">
            <label>Salgo de (origen) <select name="origen" class="nodos"></select></label>
            <label>Presupuesto máximo <small>costo máximo, opcional</small><input type="number" name="costo_maximo" min="0" placeholder="sin límite"></label>
            <label>Máximo de paradas <small>saltos, opcional</small><input type="number" name="saltos_maximos" min="0" placeholder="sin límite"></label>
          </div>
          <div class="acciones"><button class="primario">Calcular alcance</button></div>
        </form>
      </div>
    </div>

    <div class="tarjeta columna-diagrama">
      <h3>El mapa</h3>
      <svg id="svg-grafo" class="diagrama"></svg>
      <div class="leyenda">
        <span><i class="muestra origen"></i>salida</span>
        <span><i class="muestra destino"></i>llegada</span>
        <span><i class="muestra ruta"></i>ruta encontrada / alcanzable</span>
        <label class="check"><input type="checkbox" data-pesos checked> mostrar costos</label>
      </div>
      <p class="ayuda">Las flechas indican el sentido del camino y el número es su costo.</p>
      <p class="titulo-resaltado ayuda"></p>
    </div>
  </div>
  <div class="salida"></div>`;

// Acepta {"A": [["B", 4]]} o {"A": {"B": 4}} y regresa siempre la primera forma.
function adyacencia(grafo) {
  return Object.fromEntries(Object.entries(grafo).map(([u, vecinos]) => [u, Array.isArray(vecinos) ? vecinos : Object.entries(vecinos)]));
}

function diagramaLocal({ grafo, dirigido, coordenadas }) {
  const ady = adyacencia(grafo);
  const ids = new Set(Object.keys(ady));
  Object.values(ady).forEach(vecinos => vecinos.forEach(([v]) => ids.add(v)));
  const vistas = new Set();
  const aristas = [];
  for (const [u, vecinos] of Object.entries(ady)) {
    for (const [v, peso] of vecinos) {
      const clave = dirigido ? `${u}->${v}` : [u, v].sort().join("|");
      if (vistas.has(clave)) continue;
      vistas.add(clave);
      aristas.push({ origen: u, destino: v, peso });
    }
  }
  const nodos = [...ids].map(id => (coordenadas?.[id] ? { id, x: coordenadas[id][0], y: coordenadas[id][1] } : { id }));
  return { dirigido, nodos, aristas };
}

export function iniciarModulo2(raiz) {
  raiz.innerHTML = PLANTILLA;
  subpestanas(raiz);
  enlazarRangos(raiz);

  const formGrafo = $("#form-grafo", raiz);
  const svg = $("#svg-grafo", raiz);
  const salida = $(":scope > .salida", raiz);
  const casillaPesos = $("[data-pesos]", raiz);
  let actual = null;           // { grafo, dirigido, coordenadas, diagrama }
  let resaltado = {};          // { claseNodo, claseArista, titulo }
  let ejemplos = null;

  const redibujar = () => {
    if (!actual) return;
    dibujarDiagrama(svg, actual.diagrama, { ...resaltado, mostrarPesos: casillaPesos.checked });
    $(".titulo-resaltado", raiz).textContent = resaltado.titulo ?? "";
  };
  const resaltar = nuevo => { resaltado = nuevo; redibujar(); };

  const usarGrafo = (grafo, dirigido, coordenadas = null) => {
    actual = { grafo, dirigido, coordenadas, diagrama: diagramaLocal({ grafo, dirigido, coordenadas }) };
    formGrafo.elements.json.value = JSON.stringify(grafo);
    formGrafo.elements.dirigido.checked = dirigido;
    const ids = actual.diagrama.nodos.map(n => n.id);
    casillaPesos.checked = actual.diagrama.aristas.length <= 60;
    for (const select of $$("select.nodos", raiz)) {
      select.innerHTML = ids.map(id => `<option>${esc(id)}</option>`).join("");
    }
    $$('select[name="destino"]', raiz).forEach(s => { s.value = ids[ids.length - 1]; });
    $(".info-grafo", formGrafo).textContent =
      `Mapa cargado: ${ids.length} lugares (nodos) · ${actual.diagrama.aristas.length} caminos (aristas) · ${dirigido ? "calles de un solo sentido (dirigido)" : "caminos de doble sentido (no dirigido)"}${coordenadas ? " · con posiciones reales, así que la heurística usa la distancia en línea recta" : ""}`;
    salida.innerHTML = "";
    resaltar({});
  };

  formGrafo.elements.fuente.addEventListener("change", () => {
    $("[data-aleatorio]", formGrafo).hidden = formGrafo.elements.fuente.value !== "aleatorio";
  });

  formGrafo.addEventListener("submit", evento => {
    evento.preventDefault();
    const f = formGrafo.elements;
    ejecutar($("button.primario", formGrafo), salida, async () => {
      const fuente = f.fuente.value;
      if (fuente === "pequeno") return usarGrafo(GRAFO_PEQUENO, true);
      if (fuente === "aleatorio") {
        const respuesta = await post("/grafos/generar", { n: Number(f.n.value), densidad: Number(f.densidad.value), semilla: Number(f.semilla.value) });
        const { grafo, dirigido, coordenadas } = respuesta.resultado;
        usarGrafo(grafo, dirigido, coordenadas);
        salida.innerHTML = explicacionHTML(respuesta.explicacion, "Grafo generado");
        return;
      }
      ejemplos ??= await get("/grafos/ejemplos");
      usarGrafo(ejemplos[fuente].grafo, ejemplos[fuente].dirigido);
    });
  });

  $("[data-aplicar]", formGrafo).addEventListener("click", () => {
    try {
      const grafo = JSON.parse(formGrafo.elements.json.value);
      const nodos = Object.keys(grafo);
      const coordenadas = actual?.coordenadas && nodos.every(n => actual.coordenadas[n]) ? actual.coordenadas : null;
      usarGrafo(grafo, formGrafo.elements.dirigido.checked, coordenadas);
      aviso("Grafo actualizado.");
    } catch (error) {
      aviso(`El JSON no es válido: ${error.message}`, "error");
    }
  });

  casillaPesos.addEventListener("change", redibujar);

  const base = () => ({
    grafo: actual.grafo, dirigido: actual.dirigido, ...(actual.coordenadas ? { coordenadas: actual.coordenadas } : {}),
  });

  // ---------- Comparar rutas ----------
  const formRutas = $("#form-rutas", raiz);
  formRutas.addEventListener("submit", evento => {
    evento.preventDefault();
    const f = formRutas.elements;
    ejecutar($("button.primario", formRutas), salida, async () => {
      const respuesta = await post("/grafos/comparar", {
        ...base(), origen: f.origen.value, destino: f.destino.value, algoritmos: marcadas(formRutas, "alg"),
      });
      mostrarComparacion(respuesta, f.origen.value, f.destino.value);
    });
  });

  function mostrarComparacion(respuesta, origen, destino) {
    const filas = respuesta.resultado.algoritmos;
    const costos = filas.filter(f => f.encontrado).map(f => f.costo);
    const optimo = costos.length ? Math.min(...costos) : null;

    salida.innerHTML = `
      ${explicacionHTML(respuesta.explicacion, "Conclusión de la comparación")}
      <div class="tarjeta">
        <h4>Tabla comparativa <small>haz clic en una fila para pintar su ruta en el mapa</small></h4>
        ${tablaHTML([
          { titulo: "Estrategia", valor: f => `<b>${esc(f.algoritmo)}</b>` },
          { titulo: "¿Llegó?", valor: f => insignia(f.encontrado) },
          { titulo: "Camino encontrado", valor: f => esc(flecha(f.camino)) },
          { titulo: "Costo total", valor: f => (f.costo == null ? "—" : `${numero(f.costo)}${f.costo === optimo ? " ⭐" : ""}`) },
          { titulo: "Paradas", valor: f => f.saltos ?? "—" },
          { titulo: "Lugares revisados", valor: f => f.nodos_expandidos },
          { titulo: "Tiempo (ms)", valor: f => numero(f.tiempo_ms) },
          { titulo: "Memoria (KB)", valor: f => numero(f.memoria_pico_kb, 2) },
        ], filas, f => (f.costo === optimo ? "optima" : ""))}
        ${comoLeerHTML([
          "<b>Costo total:</b> lo que cuesta el camino. Menos es mejor. La ⭐ marca el más barato.",
          "<b>Paradas:</b> cuántos tramos tiene el camino.",
          "<b>Lugares revisados:</b> cuánto tuvo que explorar la estrategia antes de decidir. Menos = trabajó menos.",
          "<b>Tiempo:</b> cuánto tardó la computadora, en milésimas de segundo (ms).",
        ])}
      </div>
      <div class="rejilla-2">
        <div class="tarjeta">
          <h4>Gráfica comparativa</h4>
          <p class="ayuda">Elige qué comparar. En todas, la barra más baja es la mejor.</p>
          ${selectorHTML([["costo", "Costo total"], ["nodos_expandidos", "Lugares revisados"], ["tiempo_ms", "Tiempo (ms)"], ["memoria_pico_kb", "Memoria (KB)"]])}
          <div class="lienzo"><canvas></canvas></div>
        </div>
        <div class="tarjeta detalle-algoritmo"></div>
      </div>
      ${jsonHTML(respuesta)}`;

    const canvas = $("canvas", salida);
    enlazarSelector(salida, metrica => grafica(canvas, {
      type: "bar",
      data: {
        labels: filas.map(f => f.algoritmo),
        datasets: [{ label: metrica, data: filas.map(f => f[metrica] ?? 0), backgroundColor: filas.map((_, i) => COLORES[i % COLORES.length]) }],
      },
      options: { plugins: { legend: { display: false } } },
    }));

    const seleccionar = indice => {
      const fila = filas[indice];
      const enRuta = new Set(fila.camino ?? []);
      const pares = aristasDeCamino(fila.camino, actual.dirigido);
      $$("tr[data-i]", salida).forEach(tr => tr.classList.toggle("seleccionada", Number(tr.dataset.i) === indice));
      resaltar({
        titulo: `Ruta de ${fila.algoritmo}: ${flecha(fila.camino)} (costo ${fila.costo ?? "—"})`,
        claseNodo: id => (id === origen ? "origen" : id === destino ? "destino" : enRuta.has(id) ? "ruta" : ""),
        claseArista: a => (pares.has(`${a.origen}->${a.destino}`) ? "ruta" : ""),
      });
      $(".detalle-algoritmo", salida).innerHTML = `
        ${explicacionHTML(fila.explicacion, `Así trabajó ${fila.algoritmo}`)}
        <p class="ayuda"><b>Orden en que revisó los lugares:</b> ${esc((fila.orden_visita ?? []).join(", "))}</p>
        ${fila.frontera_maxima != null ? `<p class="ayuda"><b>Máximo de lugares pendientes por revisar a la vez:</b> ${fila.frontera_maxima}</p>` : ""}
        ${fila.heuristica ? `<p class="ayuda"><b>Estimación usada (heurística):</b> ${esc(fila.heuristica)}</p>` : ""}`;
    };
    $$("tr[data-i]", salida).forEach(tr => tr.addEventListener("click", () => seleccionar(Number(tr.dataset.i))));
    const mejor = filas.findIndex(f => f.costo === optimo);
    seleccionar(mejor >= 0 ? mejor : 0);
  }

  // ---------- Alcance ----------
  const formAlcance = $("#form-alcance", raiz);
  formAlcance.addEventListener("submit", evento => {
    evento.preventDefault();
    const f = formAlcance.elements;
    ejecutar($("button.primario", formAlcance), salida, async () => {
      const respuesta = await post("/grafos/alcance", {
        ...base(), origen: f.origen.value,
        costo_maximo: f.costo_maximo.value === "" ? null : Number(f.costo_maximo.value),
        saltos_maximos: f.saltos_maximos.value === "" ? null : Number(f.saltos_maximos.value),
      });
      const r = respuesta.resultado;
      const alcanzables = new Set(r.alcanzables.map(a => a.nodo));
      // Aristas del árbol de caminos mínimos: el último tramo de cada camino.
      const arbol = new Set(r.alcanzables.filter(a => a.camino.length > 1)
        .map(a => `${a.camino[a.camino.length - 2]}->${a.camino[a.camino.length - 1]}`));
      resaltar({
        titulo: `Desde ${r.origen} se alcanzan ${r.alcanzables.length} nodos`,
        claseNodo: id => (id === r.origen ? "origen" : alcanzables.has(id) ? "ruta" : "apagado"),
        claseArista: a => (arbol.has(`${a.origen}->${a.destino}`) || (!actual.dirigido && arbol.has(`${a.destino}->${a.origen}`)) ? "ruta" : "apagada"),
      });
      salida.innerHTML = `
        ${explicacionHTML(respuesta.explicacion, "Resultado del alcance")}
        ${metricasHTML(respuesta.metricas)}
        <div class="rejilla-2">
          <div class="tarjeta">
            <h4>✅ Lugares a los que sí llegas (${r.alcanzables.length})</h4>
            ${tablaHTML([
              { titulo: "Lugar", valor: a => `<b>${esc(a.nodo)}</b>` },
              { titulo: "Costo más barato", valor: a => numero(a.costo_minimo) },
              { titulo: "Mínimo de paradas", valor: a => a.saltos_minimos },
              { titulo: "Camino más barato", valor: a => esc(flecha(a.camino)) },
            ], r.alcanzables)}
          </div>
          <div class="tarjeta">
            <h4>🚫 Lugares a los que no llegas (${r.no_alcanzables.length})</h4>
            <p>${r.no_alcanzables.length ? r.no_alcanzables.map(n => `<span class="chip">${esc(n)}</span>`).join(" ") : "Puedes llegar a todos los lugares."}</p>
            ${r.mas_lejano ? `<p><b>El más lejano al que llegas:</b> ${esc(r.mas_lejano.nodo)} (costo ${numero(r.mas_lejano.costo_minimo)})</p>` : ""}
            ${comoLeerHTML(["En el mapa, los lugares grises quedan fuera de tu alcance.", "Las líneas moradas forman la ruta más barata para llegar a cada lugar."])}
          </div>
        </div>
        ${jsonHTML(respuesta)}`;
    });
  });

  usarGrafo(GRAFO_PEQUENO, true);
}
