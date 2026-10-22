// Módulo 3 · Auditoría de escalabilidad y benchmark
// Endpoints: GET /benchmark/ordenamiento/catalogo, POST /benchmark/ordenamiento,
//            POST /benchmark/tsp, POST /benchmark/tsp/escalabilidad
import { get, post } from "./api.js";
import { aristasDeCamino, dibujarDiagrama } from "./diagrama.js";
import {
  $, COLORES, casillasHTML, comoLeerHTML, ejecutar, enlazarRangos, enlazarSelector, esc, explicacionHTML, flecha,
  grafica, guiaHTML, insignia, jsonHTML, lista, marcadas, numero, selectorHTML, subpestanas, tablaHTML,
} from "./ui.js";

const PLANTILLA = `
  <div class="subtabs">
    <button type="button" data-sub="ordenamiento">🔢 Ordenar números</button>
    <button type="button" data-sub="tsp">🚚 Agente viajero</button>
    <button type="button" data-sub="escalabilidad">📈 ¿Qué pasa si crece?</button>
  </div>

  <div data-panel="ordenamiento">
    ${guiaHTML({
      texto: "Hay muchas recetas (algoritmos) para <b>ordenar números de menor a mayor</b>. Con pocos números todas son rápidas, pero con muchos la diferencia es enorme. Aquí pones a <b>competir</b> varias recetas con <b>exactamente los mismos números</b> y mides cuánto tarda cada una y cuánta memoria usa.",
      ejemplo: "ordenar un mazo de cartas. Puedes comparar cada carta con todas las demás (lento, como Burbuja) o partir el mazo en montones pequeños y luego juntarlos (rápido, como Merge sort).",
      pasos: ["Marca al menos 2 algoritmos (pasa el cursor sobre uno para ver cómo funciona).", "Elige cuántos números ordenar y cómo vienen acomodados.", "Presiona <b>Ejecutar benchmark</b> y mira quién gana."],
    })}
    <form class="tarjeta" id="form-orden">
      <h3>Competencia de algoritmos de ordenamiento</h3>
      <fieldset><legend>Participantes (elige al menos 2)</legend><div class="catalogo"><span class="ayuda">Cargando catálogo…</span></div></fieldset>
      <div class="campos">
        <label>¿Cuántos números? n = <output></output><input type="range" name="tamano" min="10" max="2000" step="10" value="500"></label>
        <label>¿Cómo vienen los números?
          <select name="tipo">
            <option value="aleatorio">Revueltos al azar</option>
            <option value="ordenado">Ya ordenados (el caso más fácil)</option>
            <option value="inverso">Al revés, de mayor a menor (el más difícil)</option>
            <option value="casi_ordenado">Casi ordenados</option>
            <option value="pocos_unicos">Con muchos repetidos</option>
          </select>
        </label>
        <label>Semilla <small>el mismo número genera los mismos datos</small><input type="number" name="semilla" value="42"></label>
        <label>Probar también con <small>otras cantidades, para ver cómo crece el tiempo</small><input name="tamanos" value="100, 250, 500, 1000"></label>
      </div>
      <details>
        <summary>Usar mis propios números</summary>
        <textarea name="datos" rows="3" placeholder="Ej. 5, 3, 9, 1, 7"></textarea>
      </details>
      <p class="ayuda">⏳ Con muchos números y algoritmos lentos puede tardar unos segundos. Es normal.</p>
      <div class="acciones"><button class="primario">Ejecutar benchmark</button></div>
    </form>
    <div class="salida"></div>
  </div>

  <div data-panel="tsp">
    ${guiaHTML({
      texto: "El <b>problema del agente viajero</b>: un repartidor debe visitar <b>todas las ciudades una sola vez</b> y volver al inicio recorriendo la menor distancia. Se compara un método <b>exacto</b>, que siempre encuentra la mejor ruta pero revisa muchísimas combinaciones, contra uno <b>voraz</b>, que siempre va a la ciudad más cercana: es rapidísimo pero puede equivocarse.",
      ejemplo: "planear la ruta de un camión de paquetería. Con 5 entregas puedes probar todas las rutas; con 50 ni una supercomputadora alcanzaría.",
      pasos: ["Elige cuántas ciudades (de 3 a 12).", "Presiona <b>Resolver</b>.", "Compara los dos mapas: costo de la ruta y tiempo que tardó cada método."],
    })}
    <form class="tarjeta" id="form-tsp">
      <h3>Agente viajero: exacto contra voraz</h3>
      <div class="campos">
        <label>Número de ciudades = <output></output><input type="range" name="n" min="3" max="12" value="8"></label>
        <label>Semilla <small>cambia el número para otro mapa</small><input type="number" name="semilla" value="42"></label>
      </div>
      <div class="acciones"><button class="primario">Resolver</button></div>
    </form>
    <div class="salida"></div>
  </div>

  <div data-panel="escalabilidad">
    ${guiaHTML({
      texto: "Aquí se resuelve el agente viajero con <b>cada vez más ciudades</b> para ver cómo crece el trabajo. El método exacto crece de forma <b>exponencial</b>: cada ciudad extra casi duplica el tiempo. El voraz crece <b>poco</b>. Esa es la idea de <b>P contra NP</b>: hay problemas fáciles de revisar pero que nadie sabe resolver rápido cuando crecen.",
      ejemplo: "doblar una hoja de papel: cada doblez duplica el grosor. A los pocos dobleces ya es imposible. Así crece el método exacto.",
      pasos: ["Deja los tamaños de ejemplo o escribe otros entre 3 y 12.", "Presiona <b>Medir escalabilidad</b>.", "Observa cómo la línea roja (exacto) se dispara y la azul (voraz) casi no sube."],
    })}
    <form class="tarjeta" id="form-escala">
      <h3>¿Cómo crece el trabajo al agregar ciudades? (P vs NP)</h3>
      <div class="campos">
        <label>Cantidades de ciudades a probar <small>separadas por comas, de 3 a 12</small><input name="tamanos" value="4, 6, 8, 10, 11, 12"></label>
        <label>Semilla <input type="number" name="semilla" value="42"></label>
      </div>
      <div class="acciones"><button class="primario">Medir escalabilidad</button></div>
    </form>
    <div class="salida"></div>
  </div>`;

const DEFECTO = ["burbuja", "insercion", "mergesort", "quicksort"];

export function iniciarModulo3(raiz) {
  raiz.innerHTML = PLANTILLA;
  subpestanas(raiz);
  enlazarRangos(raiz);
  iniciarOrdenamiento(raiz.querySelector('[data-panel="ordenamiento"]'));
  iniciarTSP(raiz.querySelector('[data-panel="tsp"]'));
  iniciarEscalabilidad(raiz.querySelector('[data-panel="escalabilidad"]'));
}

const enteros = texto => lista(texto).map(Number);

// ---------------- Ordenamiento ----------------

function iniciarOrdenamiento(panel) {
  const form = $("form", panel), salida = $(".salida", panel), catalogo = $(".catalogo", form);

  const cargarCatalogo = async () => {
    const algoritmos = await get("/benchmark/ordenamiento/catalogo");
    catalogo.innerHTML = casillasHTML("alg", algoritmos.map(a => [
      a.clave, a.nombre, `promedio ${a.promedio} · espacio ${a.espacio}${a.estable ? " · estable" : ""}`, a.descripcion,
    ]), DEFECTO);
  };
  cargarCatalogo().catch(() => {
    catalogo.innerHTML = `<span class="ayuda">No se pudo cargar el catálogo. Revisa la conexión con el backend y recarga la página.</span>`;
  });

  form.addEventListener("submit", evento => {
    evento.preventDefault();
    const f = form.elements;
    ejecutar($("button.primario", form), salida, async () => {
      const cuerpo = {
        algoritmos: marcadas(form, "alg"), tamano: Number(f.tamano.value), tipo: f.tipo.value, semilla: Number(f.semilla.value),
      };
      const tamanos = enteros(f.tamanos.value);
      if (tamanos.length) cuerpo.tamanos = tamanos;
      if (f.datos.value.trim()) {
        cuerpo.datos = f.datos.value.split(/[\s,]+/).filter(Boolean).map(Number);
        if (cuerpo.datos.some(Number.isNaN)) throw new Error("Tus datos deben ser números separados por comas.");
      }
      mostrarOrdenamiento(await post("/benchmark/ordenamiento", cuerpo), salida);
    });
  });
}

function mostrarOrdenamiento(respuesta, salida) {
  const r = respuesta.resultado;
  const porClave = Object.fromEntries(r.algoritmos.map(a => [a.clave, a]));
  const medallas = ["🥇", "🥈", "🥉"];

  salida.innerHTML = `
    ${explicacionHTML(respuesta.explicacion, "Conclusión del benchmark")}
    <div class="rejilla-2">
      <div class="tarjeta">
        <h4>🏆 ¿Quién ordenó más rápido? (${r.n} números)</h4>
        <ol class="ranking">${r.ranking.map((clave, i) => `
          <li><span>${medallas[i] ?? `${i + 1}.`}</span> <b>${esc(porClave[clave].nombre)}</b>
            <span class="chip">${numero(porClave[clave].tiempo_ms)} ms</span></li>`).join("")}
        </ol>
      </div>
      <div class="tarjeta">
        <h4>Gráfica comparativa</h4>
        <p class="ayuda">Elige qué comparar. En todas, la barra más baja es la mejor.</p>
        ${selectorHTML([["tiempo_ms", "Tiempo (ms)"], ["comparaciones", "Comparaciones"], ["movimientos", "Movimientos"], ["memoria_pico_kb", "Memoria (KB)"]])}
        <div class="lienzo"><canvas data-barras></canvas></div>
      </div>
    </div>
    ${r.datos_entrada ? `
      <div class="tarjeta">
        <h4>Los datos: antes y después de ordenar ${r.datos_entrada.length > 40 ? "<small>se muestran los primeros 40</small>" : ""}</h4>
        <p><b>Antes:</b> <code>${esc(r.datos_entrada.slice(0, 40).join(", "))}${r.datos_entrada.length > 40 ? " …" : ""}</code></p>
        <p><b>Después:</b> <code>${esc(r.datos_ordenados.slice(0, 40).join(", "))}${r.datos_ordenados.length > 40 ? " …" : ""}</code></p>
      </div>` : ""}
    ${r.escalabilidad ? `
      <div class="tarjeta">
        <h4>¿Qué pasa cuando hay más números?</h4>
        ${comoLeerHTML([
          "Abajo está la cantidad de números y a la izquierda el tiempo que tardó.",
          "Las líneas que se <b>disparan hacia arriba</b> son algoritmos lentos, O(n²): si duplicas los datos, el tiempo se multiplica por 4.",
          "Las líneas que se quedan <b>casi planas</b> son algoritmos rápidos, O(n log n).",
        ])}
        <div class="lienzo alto"><canvas data-lineas></canvas></div>
      </div>` : ""}
    <div class="tarjeta">
      <h4>Tabla de resultados</h4>
      ${tablaHTML([
        { titulo: "Algoritmo", valor: a => `<b>${esc(a.nombre)}</b>` },
        { titulo: "Tiempo (ms)", valor: a => numero(a.tiempo_ms) },
        { titulo: "Memoria (KB)", valor: a => numero(a.memoria_pico_kb, 2) },
        { titulo: "Comparaciones", valor: a => numero(a.comparaciones, 0) },
        { titulo: "Movimientos", valor: a => numero(a.movimientos, 0) },
        { titulo: "¿Ordenó bien?", valor: a => insignia(a.correcto) },
        { titulo: "Estable", valor: a => (a.estable ? "Sí" : "No") },
        { titulo: "Velocidad teórica (mejor / normal / peor)", valor: a => `${a.complejidad.mejor} / ${a.complejidad.promedio} / ${a.complejidad.peor}` },
        { titulo: "Memoria extra", valor: a => a.complejidad.espacio },
      ], r.algoritmos)}
      ${comoLeerHTML([
        "<b>Tiempo:</b> milésimas de segundo (ms) que tardó. <b>Memoria:</b> kilobytes (KB) que necesitó.",
        "<b>Comparaciones:</b> cuántas veces revisó si un número era mayor que otro. <b>Movimientos:</b> cuántas veces cambió números de lugar.",
        "<b>Estable:</b> si dos números son iguales, conserva el orden en que venían.",
        "<b>O(n²)</b> es lento con muchos datos; <b>O(n log n)</b> es rápido.",
      ])}
    </div>
    ${jsonHTML(respuesta)}`;

  const barras = $("[data-barras]", salida);
  enlazarSelector(salida, metrica => grafica(barras, {
    type: "bar",
    data: {
      labels: r.algoritmos.map(a => a.nombre),
      datasets: [{ label: metrica, data: r.algoritmos.map(a => a[metrica]), backgroundColor: r.algoritmos.map((_, i) => COLORES[i % COLORES.length]) }],
    },
    options: { plugins: { legend: { display: false } } },
  }));

  if (r.escalabilidad) {
    grafica($("[data-lineas]", salida), {
      type: "line",
      data: {
        labels: r.escalabilidad.tamanos,
        datasets: Object.entries(r.escalabilidad.tiempo_ms).map(([clave, tiempos], i) => ({
          label: porClave[clave].nombre, data: tiempos, borderColor: COLORES[i % COLORES.length],
          backgroundColor: COLORES[i % COLORES.length], tension: 0.25,
        })),
      },
      options: { scales: { x: { title: { display: true, text: "n (elementos)" } }, y: { title: { display: true, text: "tiempo (ms)" } } } },
    });
  }
}

// ---------------- TSP ----------------

function tarjetaRuta(titulo, solucion, id) {
  return `<div class="tarjeta">
    <h4>${titulo}</h4>
    ${solucion.error ? `<div class="alerta error">${esc(solucion.error)}</div>` : `
    <div class="metricas">
      <span class="chip">Distancia total <b>${numero(solucion.costo)}</b></span>
      <span class="chip">Combinaciones revisadas <b>${numero(solucion.estados_evaluados, 0)}</b></span>
      <span class="chip">⏱ ${numero(solucion.tiempo_ms)} ms</span>
      <span class="chip">💾 ${numero(solucion.memoria_pico_kb, 2)} KB</span>
    </div>
    <p class="ayuda">${esc(flecha(solucion.camino))}</p>`}
    <svg id="${id}" class="diagrama"></svg>
  </div>`;
}

function dibujarRuta(svg, diagrama, camino) {
  const pares = aristasDeCamino(camino, false);
  dibujarDiagrama(svg, diagrama, {
    claseNodo: id => (id === camino?.[0] ? "origen" : "ruta"),
    claseArista: a => (pares.has(`${a.origen}->${a.destino}`) ? "ruta" : "apagada"),
    etiquetaArista: a => (pares.has(`${a.origen}->${a.destino}`) ? a.peso : ""),
  });
}

function iniciarTSP(panel) {
  const form = $("form", panel), salida = $(".salida", panel);
  form.addEventListener("submit", evento => {
    evento.preventDefault();
    ejecutar($("button.primario", form), salida, async () => {
      const respuesta = await post("/benchmark/tsp", { n: Number(form.elements.n.value), semilla: Number(form.elements.semilla.value) });
      const r = respuesta.resultado;
      const brecha = r.brecha_porcentaje;
      salida.innerHTML = `
        <div class="veredicto ${brecha === 0 ? "ok" : "aviso"}">
          <b>${brecha === 0 ? "¡Esta vez el voraz también encontró la mejor ruta! ✅" : brecha == null ? "El voraz no encontró una ruta completa" : `La ruta del voraz salió ${numero(brecha, 2)}% más larga que la mejor`}</b>
          <span>Exacto: ${numero(r.exacto.costo)} · Voraz: ${numero(r.voraz.costo)} · ${r.n} ciudades</span>
        </div>
        <div class="rejilla-2">
          ${tarjetaRuta("🎯 Método exacto (Held-Karp) · siempre la mejor ruta", r.exacto, "svg-tsp-exacto")}
          ${tarjetaRuta("⚡ Método voraz (vecino más cercano) · rápido, pero no siempre la mejor", r.voraz, "svg-tsp-voraz")}
        </div>
        ${comoLeerHTML([
          "La ruta morada empieza y termina en la ciudad morada fuerte, y pasa una vez por cada ciudad.",
          "<b>Combinaciones revisadas:</b> cuánto trabajo hizo cada método. El exacto revisa muchas más, por eso tarda más.",
        ])}
        ${explicacionHTML(respuesta.explicacion, "Interpretación")}
        ${jsonHTML(respuesta)}`;
      dibujarRuta($("#svg-tsp-exacto", salida), r.diagrama, r.exacto.camino);
      dibujarRuta($("#svg-tsp-voraz", salida), r.diagrama, r.voraz.camino);
    });
  });
}

// ---------------- Escalabilidad TSP ----------------

function iniciarEscalabilidad(panel) {
  const form = $("form", panel), salida = $(".salida", panel);
  form.addEventListener("submit", evento => {
    evento.preventDefault();
    ejecutar($("button.primario", form), salida, async () => {
      const respuesta = await post("/benchmark/tsp/escalabilidad", {
        tamanos: enteros(form.elements.tamanos.value), semilla: Number(form.elements.semilla.value),
      });
      const r = respuesta.resultado;
      salida.innerHTML = `
        ${explicacionHTML(respuesta.explicacion, "Interpretación")}
        <div class="tarjeta">
          <h4>Exacto contra voraz al agregar ciudades</h4>
          ${selectorHTML([["tiempo", "Tiempo (ms)"], ["memoria", "Memoria (KB)"]])}
          <label class="check"><input type="checkbox" data-log> Escala logarítmica: con ella, un crecimiento exponencial se ve como una línea recta</label>
          <div class="lienzo alto"><canvas></canvas></div>
          ${comoLeerHTML([
            "Abajo está el número de ciudades; a la izquierda, el tiempo o la memoria.",
            "La línea <b>roja</b> (exacto) se dispara: crecimiento exponencial, típico de los problemas NP-difíciles.",
            "La línea <b>azul</b> (voraz) casi no sube: crecimiento polinómico, de la clase P.",
          ])}
        </div>
        <div class="tarjeta">
          <h4>Tabla de mediciones</h4>
          ${tablaHTML([
            { titulo: "Ciudades", valor: t => `<b>${t.n}</b>` },
            { titulo: "Tiempo exacto (ms)", valor: t => numero(t.exacto_tiempo_ms) },
            { titulo: "Tiempo voraz (ms)", valor: t => numero(t.voraz_tiempo_ms) },
            { titulo: "Memoria exacto (KB)", valor: t => numero(t.exacto_memoria_kb, 2) },
            { titulo: "Memoria voraz (KB)", valor: t => numero(t.voraz_memoria_kb, 2) },
            { titulo: "Combinaciones (exacto)", valor: t => numero(t.exacto_estados, 0) },
            { titulo: "Distancia exacta", valor: t => numero(t.exacto_costo) },
            { titulo: "Distancia voraz", valor: t => numero(t.voraz_costo) },
            { titulo: "¿Cuánto peor fue el voraz?", valor: t => (t.brecha_porcentaje == null ? "—" : `${numero(t.brecha_porcentaje, 2)}%`) },
          ], r.tabla)}
        </div>
        ${jsonHTML(respuesta)}`;

      const canvas = $("canvas", salida), casillaLog = $("[data-log]", salida);
      let metrica = "tiempo";
      const pintar = () => {
        const sufijo = metrica === "tiempo" ? "tiempo_ms" : "memoria_kb";
        grafica(canvas, {
          type: "line",
          data: {
            labels: r.grafica.n,
            datasets: [
              { label: "Held-Karp (exacto)", data: r.grafica[`exacto_${sufijo}`], borderColor: COLORES[4], backgroundColor: COLORES[4], tension: 0.25 },
              { label: "Vecino más cercano (voraz)", data: r.grafica[`voraz_${sufijo}`], borderColor: COLORES[0], backgroundColor: COLORES[0], tension: 0.25 },
            ],
          },
          options: {
            scales: {
              x: { title: { display: true, text: "n (ciudades)" } },
              y: { type: casillaLog.checked ? "logarithmic" : "linear", title: { display: true, text: metrica === "tiempo" ? "tiempo (ms)" : "memoria (KB)" } },
            },
          },
        });
      };
      enlazarSelector(salida, m => { metrica = m; pintar(); });
      casillaLog.addEventListener("change", pintar);
    });
  });
}
