// Componentes de la GUI que comparten los tres módulos: tablas, explicaciones, gráficas, avisos, etc.

export const $ = (selector, raiz = document) => raiz.querySelector(selector);
export const $$ = (selector, raiz = document) => [...raiz.querySelectorAll(selector)];

// Escapa el texto antes de meterlo en HTML (evita que una cadena como "<b>" rompa la página).
export function esc(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/** "a, b , c" → ["a", "b", "c"] */
export function lista(texto) {
  return texto.split(",").map(s => s.trim()).filter(s => s !== "");
}

export const flecha = camino => (camino?.length ? camino.join(" → ") : "—");
export const numero = (valor, decimales = 4) =>
  valor == null ? "—" : Number(valor).toLocaleString("es-MX", { maximumFractionDigits: decimales });

// ---------- Formularios ----------

/** opciones: [[valor, texto, detalle?], ...] */
export function casillasHTML(nombre, opciones, marcadas = opciones.map(o => o[0])) {
  return `<div class="casillas">${opciones.map(([valor, texto, detalle, ayuda]) => `
    <label class="casilla" ${ayuda ? `title="${esc(ayuda)}"` : ""}>
      <input type="checkbox" name="${nombre}" value="${valor}" ${marcadas.includes(valor) ? "checked" : ""}>
      <span>${texto}${detalle ? `<small>${detalle}</small>` : ""}</span>
    </label>`).join("")}</div>`;
}

export const marcadas = (raiz, nombre) => $$(`input[name="${nombre}"]:checked`, raiz).map(i => i.value);

// Muestra junto a cada <input type="range"> el valor que tiene seleccionado.
export function enlazarRangos(raiz) {
  for (const rango of $$('input[type="range"]', raiz)) {
    const salida = rango.closest("label").querySelector("output");
    const actualizar = () => { salida.textContent = rango.value; };
    rango.addEventListener("input", actualizar);
    actualizar();
  }
}

// ---------- Ayuda para usuarios sin experiencia ----------

/** Recuadro "¿Qué es esto?": explicación sencilla, un ejemplo de la vida diaria y los pasos a seguir. */
export function guiaHTML({ titulo = "¿Qué es esto?", texto, ejemplo, pasos = [] }) {
  return `<details class="guia" open>
    <summary>📘 ${titulo}</summary>
    <p>${texto}</p>
    ${ejemplo ? `<p class="ejemplo-vida">🧩 <b>Piénsalo así:</b> ${ejemplo}</p>` : ""}
    ${pasos.length ? `<p class="titulo-pasos"><b>Cómo usarlo:</b></p><ol class="pasos">${pasos.map(p => `<li>${p}</li>`).join("")}</ol>` : ""}
  </details>`;
}

/** Notas cortas para interpretar una tabla o gráfica. */
export function comoLeerHTML(notas) {
  return `<div class="como-leer"><b>📖 Cómo leer esto:</b><ul>${notas.map(n => `<li>${n}</li>`).join("")}</ul></div>`;
}

// ---------- Bloques de resultado ----------

export function explicacionHTML(explicacion, titulo = "¿Qué pasó?") {
  if (!explicacion) return "";
  return `<div class="explicacion">
    <h4>💡 ${titulo}</h4>
    <p class="resumen">${esc(explicacion.resumen)}</p>
    ${explicacion.complejidad ? `<p class="complejidad"><b>¿Qué tan rápido es? (complejidad):</b> ${esc(explicacion.complejidad)}</p>` : ""}
    ${explicacion.teoria ? `<details><summary>Base teórica (para saber más)</summary><p>${esc(explicacion.teoria)}</p></details>` : ""}
  </div>`;
}

export function metricasHTML(metricas) {
  if (!metricas || metricas.tiempo_ms == null) return "";
  return `<div class="metricas">
    <span class="chip">⏱ ${numero(metricas.tiempo_ms)} ms</span>
    <span class="chip">💾 ${numero(metricas.memoria_pico_kb, 2)} KB</span>
  </div>`;
}

/** columnas: [{titulo, valor: (fila, i) => html}] */
export function tablaHTML(columnas, filas, claseFila = () => "") {
  return `<div class="tabla-scroll"><table>
    <thead><tr>${columnas.map(c => `<th>${c.titulo}</th>`).join("")}</tr></thead>
    <tbody>${filas.map((fila, i) => `<tr data-i="${i}" class="${claseFila(fila, i)}">
      ${columnas.map(c => `<td>${c.valor(fila, i)}</td>`).join("")}</tr>`).join("")}</tbody>
  </table></div>`;
}

export function conjuntoHTML(elementos, limite = 300) {
  if (!elementos.length) return `<span class="conjunto vacio">∅ (conjunto vacío)</span>`;
  const visibles = elementos.slice(0, limite).map(e => `<span class="chip">${esc(e)}</span>`).join("");
  const resto = elementos.length > limite ? `<span class="chip">… y ${elementos.length - limite} más</span>` : "";
  return `<div class="conjunto">{ ${visibles}${resto} }</div>`;
}

export const insignia = (ok, si = "Sí", no = "No") => `<span class="insignia ${ok ? "ok" : "mal"}">${ok ? si : no}</span>`;

export const jsonHTML = datos => `<details class="json">
  <summary>Ver la respuesta JSON del backend</summary>
  <pre>${esc(JSON.stringify(datos, null, 2))}</pre>
</details>`;

export const errorHTML = mensaje => `<div class="alerta error"><b>No se pudo completar la operación.</b> ${esc(mensaje)}</div>`;

// ---------- Interacción ----------

// Ejecuta una petición mostrando un indicador de carga en el botón y el error en la salida si algo falla.
export async function ejecutar(boton, salida, tarea) {
  const contenido = boton.innerHTML;
  boton.disabled = true;
  boton.innerHTML = `<span class="spinner"></span> Procesando…`;
  try {
    await tarea();
  } catch (error) {
    salida.innerHTML = errorHTML(error.message);
    aviso(error.message, "error");
  } finally {
    boton.disabled = false;
    boton.innerHTML = contenido;
  }
}

export function aviso(mensaje, tipo = "info") {
  const elemento = document.createElement("div");
  elemento.className = `aviso ${tipo}`;
  elemento.textContent = mensaje;
  $("#avisos").appendChild(elemento);
  setTimeout(() => elemento.remove(), 5000);
}

// Sub-pestañas: cada .subtabs controla los [data-panel] que son sus hermanos.
export function subpestanas(raiz) {
  for (const barra of $$(".subtabs", raiz)) {
    const paneles = $$(":scope > [data-panel]", barra.parentElement);
    const botones = $$("button", barra);
    const activar = nombre => {
      botones.forEach(b => b.classList.toggle("activa", b.dataset.sub === nombre));
      paneles.forEach(p => { p.hidden = p.dataset.panel !== nombre; });
    };
    botones.forEach(b => b.addEventListener("click", () => activar(b.dataset.sub)));
    activar(botones[0].dataset.sub);
  }
}

// Botones segmentados para elegir qué métrica graficar.
export function selectorHTML(opciones) {
  return `<div class="segmentado">${opciones.map(([valor, texto], i) =>
    `<button type="button" data-m="${valor}" class="${i === 0 ? "activa" : ""}">${texto}</button>`).join("")}</div>`;
}

export function enlazarSelector(contenedor, alCambiar) {
  const botones = $$("button[data-m]", contenedor);
  botones.forEach(b => b.addEventListener("click", () => {
    botones.forEach(x => x.classList.toggle("activa", x === b));
    alCambiar(b.dataset.m);
  }));
  alCambiar(botones[0].dataset.m);
}

// ---------- Gráficas (Chart.js) ----------

export const COLORES = ["#4f46e5", "#0ea5e9", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#ec4899", "#64748b"];

export function grafica(canvas, configuracion) {
  if (typeof Chart === "undefined") {
    canvas.replaceWith(Object.assign(document.createElement("p"), {
      className: "ayuda", textContent: "No se pudo cargar Chart.js (¿sin internet?). Los datos siguen en la tabla.",
    }));
    return;
  }
  canvas._grafica?.destroy();
  canvas._grafica = new Chart(canvas, {
    ...configuracion,
    options: { responsive: true, maintainAspectRatio: false, ...configuracion.options },
  });
}
