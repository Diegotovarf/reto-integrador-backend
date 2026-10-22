// Dibuja en un <svg> el "diagrama" que regresa el backend (autómatas y grafos usan el mismo formato):
//   { dirigido?, nodos: [{id, x?, y?, inicial?, final?}], aristas: [{origen, destino, peso? | simbolos?}] }
// Las opciones claseNodo y claseArista permiten resaltar rutas, estados activos, etc. con CSS.

const NS = "http://www.w3.org/2000/svg";
const ANCHO = 720;
const ALTO = 440;
const MARGEN = 55;
const TIPOS_ARISTA = ["base", "ruta", "activa", "apagada"];

function crear(etiqueta, atributos, padre) {
  const elemento = document.createElementNS(NS, etiqueta);
  for (const [clave, valor] of Object.entries(atributos)) elemento.setAttribute(clave, valor);
  padre?.appendChild(elemento);
  return elemento;
}

// Si los nodos traen coordenadas (grafos generados) se escalan al lienzo; si no, se acomodan en círculo.
function posiciones(nodos) {
  const posicion = {};
  if (nodos.length && nodos.every(n => n.x != null && n.y != null)) {
    const xs = nodos.map(n => n.x), ys = nodos.map(n => n.y);
    const minX = Math.min(...xs), minY = Math.min(...ys);
    const escalaX = (ANCHO - 2 * MARGEN) / (Math.max(...xs) - minX || 1);
    const escalaY = (ALTO - 2 * MARGEN) / (Math.max(...ys) - minY || 1);
    nodos.forEach(n => { posicion[n.id] = { x: MARGEN + (n.x - minX) * escalaX, y: MARGEN + (n.y - minY) * escalaY }; });
  } else {
    // Elipse que aprovecha todo el ancho del lienzo; con pocos nodos se queda casi circular.
    const radioY = ALTO / 2 - MARGEN;
    const radioX = nodos.length <= 6 ? radioY * 1.3 : ANCHO / 2 - MARGEN;
    const inicio = nodos.length === 2 ? Math.PI : -Math.PI / 2; // con 2 nodos: izquierda y derecha
    nodos.forEach((n, i) => {
      const angulo = inicio + (2 * Math.PI * i) / nodos.length;
      posicion[n.id] = { x: ANCHO / 2 + radioX * Math.cos(angulo), y: ALTO / 2 + radioY * Math.sin(angulo) };
    });
  }
  return posicion;
}

const unitario = (dx, dy) => { const largo = Math.hypot(dx, dy) || 1; return [dx / largo, dy / largo]; };

export function dibujarDiagrama(svg, diagrama, opciones = {}) {
  const { claseNodo = () => "", claseArista = () => "", etiquetaArista, mostrarPesos = true } = opciones;
  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${ANCHO} ${ALTO}`);
  const prefijo = svg.id || "svg";
  const dirigido = diagrama.dirigido !== false; // los autómatas siempre son dirigidos
  const total = diagrama.nodos.length;
  const R = total <= 12 ? 20 : total <= 30 ? 14 : 10;
  const pos = posiciones(diagrama.nodos);

  // Puntas de flecha, una por color de arista.
  const defs = crear("defs", {}, svg);
  for (const tipo of TIPOS_ARISTA) {
    const marcador = crear("marker", {
      id: `${prefijo}-${tipo}`, viewBox: "0 0 10 10", refX: 9, refY: 5,
      markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse",
    }, defs);
    crear("path", { d: "M0,0 L10,5 L0,10 z", class: `punta ${tipo}` }, marcador);
  }

  const capaAristas = crear("g", {}, svg);
  const capaNodos = crear("g", {}, svg);
  const existe = new Set(diagrama.aristas.map(a => `${a.origen}->${a.destino}`));

  for (const arista of diagrama.aristas) {
    const clase = claseArista(arista) || "";
    const tipo = TIPOS_ARISTA.find(t => clase.split(" ").includes(t)) || "base";
    const texto = etiquetaArista ? etiquetaArista(arista)
      : arista.simbolos ? arista.simbolos.join(", ")
      : mostrarPesos ? arista.peso : "";
    const grupo = crear("g", { class: `arista ${clase}` }, capaAristas);
    const p = pos[arista.origen], q = pos[arista.destino];
    let trazo, etiquetaX, etiquetaY;

    if (arista.origen === arista.destino) {
      // Lazo: transición de un estado a sí mismo.
      trazo = `M ${p.x - R * 0.6} ${p.y - R * 0.8} C ${p.x - R * 1.8} ${p.y - R * 3.2}, ${p.x + R * 1.8} ${p.y - R * 3.2}, ${p.x + R * 0.6} ${p.y - R * 0.8}`;
      etiquetaX = p.x;
      etiquetaY = p.y - R * 2.75;
    } else {
      // Si existe la arista contraria (A→B y B→A) se curvan para no encimarse.
      const [ux, uy] = unitario(q.x - p.x, q.y - p.y);
      const curva = dirigido && existe.has(`${arista.destino}->${arista.origen}`) ? 28 : 0;
      const c = { x: (p.x + q.x) / 2 - uy * curva * 2, y: (p.y + q.y) / 2 + ux * curva * 2 };
      const [sx, sy] = unitario(c.x - p.x, c.y - p.y);
      const [ex, ey] = unitario(c.x - q.x, c.y - q.y);
      const inicio = { x: p.x + sx * R, y: p.y + sy * R };
      const fin = { x: q.x + ex * (R + 1), y: q.y + ey * (R + 1) };
      trazo = `M ${inicio.x} ${inicio.y} Q ${c.x} ${c.y} ${fin.x} ${fin.y}`;
      etiquetaX = 0.25 * inicio.x + 0.5 * c.x + 0.25 * fin.x;
      etiquetaY = 0.25 * inicio.y + 0.5 * c.y + 0.25 * fin.y;
    }

    crear("path", { d: trazo, ...(dirigido ? { "marker-end": `url(#${prefijo}-${tipo})` } : {}) }, grupo);
    if (texto !== "" && texto != null) {
      crear("text", { x: etiquetaX, y: etiquetaY, "text-anchor": "middle", "dominant-baseline": "central" }, grupo)
        .textContent = texto;
    }
  }

  for (const nodo of diagrama.nodos) {
    const { x, y } = pos[nodo.id];
    const grupo = crear("g", { class: `nodo ${claseNodo(nodo.id) || ""}` }, capaNodos);
    crear("title", {}, grupo).textContent = nodo.id;
    if (nodo.inicial) {
      crear("path", { d: `M ${x - R - 30} ${y} L ${x - R - 2} ${y}`, class: "flecha-inicial", "marker-end": `url(#${prefijo}-base)` }, grupo);
    }
    crear("circle", { cx: x, cy: y, r: R }, grupo);
    if (nodo.final) crear("circle", { cx: x, cy: y, r: R - 4, class: "anillo" }, grupo);
    crear("text", { x, y, "text-anchor": "middle", "dominant-baseline": "central", "font-size": R < 14 ? 9 : 13 }, grupo)
      .textContent = nodo.id;
  }
}

// Conjunto "A->B" de las aristas que recorre un camino; en grafos no dirigidos cuenta en ambos sentidos.
export function aristasDeCamino(camino, dirigido) {
  const pares = new Set();
  for (let i = 0; i + 1 < (camino?.length ?? 0); i++) {
    pares.add(`${camino[i]}->${camino[i + 1]}`);
    if (!dirigido) pares.add(`${camino[i + 1]}->${camino[i]}`);
  }
  return pares;
}
