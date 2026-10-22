// Módulo 1 · Traductor de lenguajes y verificador de reglas
// Endpoints: POST /cadenas/operar, POST /lenguajes/operar, GET /automatas/ejemplos, POST /automatas/{afd|afnd|afnd-e}
import { get, post } from "./api.js";
import { dibujarDiagrama } from "./diagrama.js";
import {
  $, $$, aviso, casillasHTML, comoLeerHTML, conjuntoHTML, ejecutar, enlazarRangos, esc, explicacionHTML,
  guiaHTML, insignia, jsonHTML, lista, marcadas, subpestanas, tablaHTML,
} from "./ui.js";

// [clave, nombre, explicación sencilla]
const OPS_CADENA = [
  ["longitud", "Longitud |w|", "¿cuántas letras tiene?"],
  ["inversa", "Inversa wᴿ", "la palabra escrita al revés"],
  ["concatenacion", "Concatenación w·v", "pegar w y v una tras otra"],
  ["potencia", "Potencia wⁿ", "repetir w n veces seguidas"],
  ["prefijos", "Prefijos", "todas las formas en que puede empezar"],
  ["sufijos", "Sufijos", "todas las formas en que puede terminar"],
  ["subcadenas", "Subcadenas", "todos los pedazos seguidos"],
  ["palindromo", "¿Palíndromo?", "¿se lee igual al derecho y al revés?"],
  ["conteo", "Conteo de símbolos", "cuántas veces aparece cada letra"],
  ["alfabeto", "¿w ∈ Σ*?", "¿usa solo letras permitidas?"],
];
const NOMBRES_CADENA = Object.fromEntries(OPS_CADENA.map(([clave, nombre, sencillo]) => [clave, `${nombre} · ${sencillo}`]));

const OPS_LENGUAJE = [
  ["union", "Unión L ∪ M", "juntar las palabras de L y de M"],
  ["interseccion", "Intersección L ∩ M", "las palabras que están en los dos"],
  ["diferencia", "Diferencia L − M", "las de L que no están en M"],
  ["diferencia_simetrica", "Dif. simétrica L △ M", "las que están en solo uno de los dos"],
  ["concatenacion", "Concatenación L·M", "pegar cada palabra de L con cada una de M"],
  ["potencia", "Potencia Lⁿ", "concatenar L consigo mismo n veces"],
  ["kleene", "Cerradura de Kleene L*", "todas las combinaciones, incluida la vacía ε"],
  ["positiva", "Cerradura positiva L⁺", "todas las combinaciones de al menos una palabra"],
  ["inversa", "Inversa Lᴿ", "cada palabra escrita al revés"],
  ["complemento", "Complemento L̄", "las palabras posibles que NO están en L"],
];

const PRUEBAS_LOTE = {
  afd: ["01", "1101", "110", "ε", "0001"],
  afnd: ["ab", "aab", "ba", "b", "abab"],
  "afnd-e": ["aabb", "ab", "ba", "ε", "bba"],
};

const PLANTILLA = `
  <div class="subtabs">
    <button type="button" data-sub="cadenas">Cadenas</button>
    <button type="button" data-sub="lenguajes">Lenguajes</button>
    <button type="button" data-sub="automatas">Autómatas</button>
  </div>

  <div data-panel="cadenas">
    ${guiaHTML({
      texto: "Una <b>cadena</b> (o palabra) es una fila de letras, como <code>abba</code>. Aquí le aplicas operaciones: voltearla, repetirla, pegarle otra palabra, ver si se lee igual al revés, etc.",
      ejemplo: "si w = <code>roma</code>, su inversa es <code>amor</code>; y <code>anilina</code> es un palíndromo porque se lee igual al revés.",
      pasos: ["Escribe una palabra en <b>w</b> (ya viene <code>abba</code> de ejemplo).", "Marca las operaciones que quieras ver.", "Presiona <b>Aplicar operaciones</b> y revisa cada tarjeta de resultado."],
    })}
    <form class="tarjeta" id="form-cadenas">
      <h3>Operaciones con cadenas</h3>
      <div class="campos">
        <label>Palabra w <small>la palabra principal</small><input name="w" value="abba"></label>
        <label>Palabra v <small>solo para pegarla (concatenación)</small><input name="v" value="ca"></label>
        <label>Número n <small>cuántas veces repetir (potencia)</small><input name="n" type="number" min="0" max="50" value="2"></label>
        <label>Letras permitidas Σ <small>separadas por comas</small><input name="sigma" value="a, b"></label>
      </div>
      <p class="ayuda">💡 Para la palabra vacía (sin letras) escribe <code>ε</code>.</p>
      <fieldset><legend>¿Qué quieres calcular?</legend>${casillasHTML("op", OPS_CADENA)}</fieldset>
      <div class="acciones"><button class="primario">Aplicar operaciones</button></div>
    </form>
    <div class="salida"></div>
  </div>

  <div data-panel="lenguajes">
    ${guiaHTML({
      texto: "Un <b>lenguaje</b> es simplemente un conjunto de palabras, por ejemplo L = {a, ab}. Como son conjuntos, puedes juntarlos, ver qué tienen en común o qué les falta, y también combinar sus palabras.",
      ejemplo: "si L son las palabras de tu lista de compras y M las de tu amigo, la <b>unión</b> es todo lo que compran entre los dos y la <b>intersección</b> lo que ambos compran.",
      pasos: ["Escribe las palabras de <b>L</b> y de <b>M</b> separadas por comas.", "Marca las operaciones que quieras.", "Presiona <b>Aplicar operaciones</b>: verás cada conjunto resultado y cuántas palabras tiene."],
    })}
    <form class="tarjeta" id="form-lenguajes">
      <h3>Operaciones con lenguajes</h3>
      <div class="campos">
        <label>Lenguaje L <small>palabras separadas por comas</small><input name="L" value="a, ab"></label>
        <label>Lenguaje M <small>palabras separadas por comas</small><input name="M" value="ab, b"></label>
        <label>Letras permitidas Σ <small>se usan para el complemento</small><input name="sigma" value="a, b"></label>
        <label>Número n <small>para la potencia Lⁿ</small><input name="n" type="number" min="0" max="10" value="2"></label>
        <label>Largo máximo k = <output></output>
          <small>L* y el complemento tienen infinitas palabras; solo se muestran las de hasta k letras</small>
          <input name="k" type="range" min="0" max="6" value="2"></label>
      </div>
      <fieldset><legend>¿Qué quieres calcular?</legend>
        ${casillasHTML("op", OPS_LENGUAJE, ["union", "interseccion", "diferencia", "concatenacion", "kleene", "complemento"])}
      </fieldset>
      <div class="acciones"><button class="primario">Aplicar operaciones</button></div>
    </form>
    <div class="salida"></div>
  </div>

  <div data-panel="automatas">
    ${guiaHTML({
      texto: "Un <b>autómata</b> es una máquina que lee una palabra <b>letra por letra</b>. Los <b>círculos</b> son estados y las <b>flechas</b> dicen a dónde moverse con cada letra. Empieza donde apunta la flechita de entrada y, si al terminar de leer queda en un <b>círculo doble</b> (estado final), la palabra se <b>acepta</b>; si no, se <b>rechaza</b>.",
      ejemplo: "es como un torniquete del metro: según lo que hagas (meter tarjeta, empujar) cambia de estado, y solo te deja pasar si sigues la secuencia correcta.",
      pasos: [
        "Elige el tipo de autómata. Se carga un ejemplo listo para probar.",
        "Presiona <b>Evaluar cadena</b> y luego <b>▶ Reproducir</b> para ver cómo avanza letra por letra.",
        "Cambia la palabra en <b>Palabra a evaluar</b> o prueba muchas a la vez en la parte de abajo.",
      ],
    })}
    <details class="tarjeta tipos-automata">
      <summary>¿Cuál es la diferencia entre AFD, AFND y AFND-ε?</summary>
      <ul>
        <li><b>AFD (determinista):</b> con cada letra hay <b>un solo</b> camino posible. La máquina nunca duda.</li>
        <li><b>AFND (no determinista):</b> con una letra puede haber <b>varios</b> caminos a la vez; la máquina los prueba todos al mismo tiempo. Acepta si <b>alguno</b> termina en un estado final.</li>
        <li><b>AFND-ε:</b> además tiene flechas <b>ε</b> que la dejan moverse <b>sin leer ninguna letra</b>, como un atajo gratis.</li>
      </ul>
    </details>
    <div class="rejilla-2">
      <form class="tarjeta" id="form-automata">
        <h3>Simulador de autómatas</h3>
        <div class="campos">
          <label>Tipo de autómata
            <select name="tipo">
              <option value="afd">AFD · un solo camino</option>
              <option value="afnd">AFND · varios caminos a la vez</option>
              <option value="afnd-e">AFND-ε · con atajos ε</option>
            </select>
          </label>
          <label>Estados Q <small>los círculos</small><input name="estados"></label>
          <label>Letras permitidas Σ <small>el alfabeto</small><input name="alfabeto"></label>
          <label>Estado inicial q₀ <small>donde empieza</small><input name="inicial"></label>
          <label>Estados finales F <small>círculos dobles: aceptan</small><input name="finales"></label>
        </div>
        <label>Reglas de movimiento δ (transiciones)
          <small>una por línea: <code>q0 a -> q1</code> significa "si estoy en q0 y leo una a, me muevo a q1". Para un atajo sin letra escribe <code>ε</code> o <code>eps</code>.</small>
          <textarea name="transiciones" rows="7" spellcheck="false"></textarea>
        </label>
        <label>Palabra a evaluar <input name="cadena"></label>
        <p class="descripcion-ejemplo ayuda"></p>
        <div class="acciones">
          <button class="primario">Evaluar cadena</button>
          <button type="button" data-ejemplo>Restaurar ejemplo</button>
          <button type="button" data-previa>Redibujar diagrama</button>
        </div>
      </form>
      <div class="tarjeta">
        <h3>Diagrama de estados</h3>
        <div class="reproductor"><svg id="svg-automata" class="diagrama"></svg></div>
        <div class="leyenda">
          <span><i class="muestra activa"></i>donde está ahora</span>
          <span><i class="muestra acepta"></i>terminó y aceptó</span>
          <span><i class="muestra rechaza"></i>terminó y rechazó</span>
          <span>◎ estado final · → inicio</span>
        </div>
        <p class="ayuda">La flecha naranja es el movimiento que acaba de hacer; la letra resaltada arriba es la que leyó.</p>
      </div>
    </div>
    <div class="salida"></div>
    <form class="tarjeta" id="form-lote">
      <h3>Probar varias palabras a la vez</h3>
      <p class="ayuda">Usa el mismo autómata de arriba. Escribe una palabra por renglón (<code>ε</code> = palabra vacía) y descubre qué reglas sigue: ¿qué tienen en común las que acepta?</p>
      <textarea name="cadenas" rows="5" spellcheck="false"></textarea>
      <div class="acciones"><button class="primario">Probar todas</button></div>
      <div class="salida-lote"></div>
    </form>
  </div>`;

export function iniciarModulo1(raiz) {
  raiz.innerHTML = PLANTILLA;
  subpestanas(raiz);
  enlazarRangos(raiz);
  iniciarCadenas(raiz.querySelector('[data-panel="cadenas"]'));
  iniciarLenguajes(raiz.querySelector('[data-panel="lenguajes"]'));
  iniciarAutomatas(raiz.querySelector('[data-panel="automatas"]'));
}

// ---------------- Cadenas ----------------

function valorCadena(valor) {
  if (typeof valor === "boolean") return insignia(valor);
  if (Array.isArray(valor)) return conjuntoHTML(valor);
  if (valor && typeof valor === "object") {
    if ("pertenece" in valor) {
      return insignia(valor.pertenece, "w ∈ Σ*", "w ∉ Σ*")
        + (valor.simbolos_invalidos.length ? ` <span class="ayuda">Símbolos fuera de Σ: ${esc(valor.simbolos_invalidos.join(", "))}</span>` : "");
    }
    return Object.entries(valor).map(([s, c]) => `<span class="chip">${esc(s)}: <b>${c}</b></span>`).join(" ");
  }
  return `<code class="valor">${esc(valor)}</code>`;
}

function iniciarCadenas(panel) {
  const form = $("form", panel), salida = $(".salida", panel);
  form.addEventListener("submit", evento => {
    evento.preventDefault();
    const f = form.elements;
    const cuerpo = {
      w: f.w.value.trim(),
      v: f.v.value.trim() || null,
      n: f.n.value === "" ? null : Number(f.n.value),
      sigma: lista(f.sigma.value).length ? lista(f.sigma.value) : null,
      operaciones: marcadas(form, "op"),
    };
    ejecutar($("button.primario", form), salida, async () => {
      const respuesta = await post("/cadenas/operar", cuerpo);
      salida.innerHTML = `
        ${explicacionHTML(respuesta.explicacion, "Resumen")}
        <div class="rejilla-tarjetas">${respuesta.resultado.map(r => `
          <article class="tarjeta resultado">
            <h4>${NOMBRES_CADENA[r.operacion]}</h4>
            <div class="valor-resultado">${valorCadena(r.resultado)}</div>
            <p>${esc(r.explicacion.resumen)}</p>
            <details><summary>Teoría</summary><p>${esc(r.explicacion.teoria)}</p></details>
          </article>`).join("")}
        </div>
        ${jsonHTML(respuesta)}`;
    });
  });
}

// ---------------- Lenguajes ----------------

function iniciarLenguajes(panel) {
  const form = $("form", panel), salida = $(".salida", panel);
  form.addEventListener("submit", evento => {
    evento.preventDefault();
    const f = form.elements;
    const cuerpo = {
      L: lista(f.L.value), M: lista(f.M.value), sigma: lista(f.sigma.value),
      k: Number(f.k.value), n: Number(f.n.value || 0), operaciones: marcadas(form, "op"),
    };
    ejecutar($("button.primario", form), salida, async () => {
      const respuesta = await post("/lenguajes/operar", cuerpo);
      salida.innerHTML = `
        ${explicacionHTML(respuesta.explicacion, "Resumen")}
        <div class="rejilla-tarjetas">${respuesta.resultado.map(r => `
          <article class="tarjeta resultado">
            <h4>${esc(r.nombre)} <span class="chip">|resultado| = ${r.cardinalidad}</span></h4>
            <div class="valor-resultado">${conjuntoHTML(r.resultado)}</div>
            <p>${esc(r.explicacion.resumen)}</p>
            <details><summary>Teoría</summary><p>${esc(r.explicacion.teoria)}</p></details>
          </article>`).join("")}
        </div>
        ${jsonHTML(respuesta)}`;
    });
  });
}

// ---------------- Autómatas ----------------

const normalizarSimbolo = s => (["eps", "epsilon", "ε", "λ"].includes(s.toLowerCase()) ? "ε" : s);

function transicionesATexto(transiciones) {
  return Object.entries(transiciones)
    .flatMap(([origen, porSimbolo]) => Object.entries(porSimbolo)
      .map(([simbolo, destino]) => `${origen} ${simbolo} -> ${[].concat(destino).join(" ")}`))
    .join("\n");
}

// "q0 a -> q0 q1" (una línea por transición) → {"q0": {"a": ["q0", "q1"]}}  (en AFD: {"q0": {"a": "q0"}})
function textoATransiciones(texto, tipo) {
  const transiciones = {};
  texto.split("\n").map(l => l.trim()).filter(Boolean).forEach((linea, i) => {
    const [izquierda, derecha] = linea.split("->");
    const [origen, simbolo] = izquierda.trim().split(/\s+/);
    const destinos = (derecha ?? "").trim().split(/[\s,]+/).filter(Boolean);
    if (!origen || !simbolo || !destinos.length) {
      throw new Error(`Transición ${i + 1} ("${linea}"): usa el formato "q0 a -> q1".`);
    }
    transiciones[origen] ??= {};
    const clave = normalizarSimbolo(simbolo);
    if (tipo === "afd") {
      if (destinos.length > 1) throw new Error(`Transición ${i + 1}: en un AFD cada (estado, símbolo) va a un solo estado.`);
      transiciones[origen][clave] = destinos[0];
    } else {
      transiciones[origen][clave] = [...new Set([...(transiciones[origen][clave] ?? []), ...destinos])];
    }
  });
  return transiciones;
}

function leerAutomata(form) {
  const f = form.elements;
  const tipo = f.tipo.value;
  return {
    tipo,
    cuerpo: {
      estados: lista(f.estados.value), alfabeto: lista(f.alfabeto.value), inicial: f.inicial.value.trim(),
      finales: lista(f.finales.value), transiciones: textoATransiciones(f.transiciones.value, tipo),
      cadena: f.cadena.value.trim(),
    },
  };
}

// Diagrama armado en el navegador para ver el autómata antes de evaluarlo.
function diagramaLocal({ estados, inicial, finales, transiciones }) {
  const agrupadas = {};
  for (const [origen, porSimbolo] of Object.entries(transiciones)) {
    for (const [simbolo, destinos] of Object.entries(porSimbolo)) {
      for (const destino of [].concat(destinos)) (agrupadas[`${origen}|${destino}`] ??= []).push(simbolo);
    }
  }
  return {
    nodos: estados.map(id => ({ id, inicial: id === inicial, final: finales.includes(id) })),
    aristas: Object.entries(agrupadas).map(([clave, simbolos]) => {
      const [origen, destino] = clave.split("|");
      return { origen, destino, simbolos };
    }),
  };
}

function iniciarAutomatas(panel) {
  const form = $("#form-automata", panel);
  const salida = $(":scope > .salida", panel);
  const reproductor = $(".reproductor", panel);
  const formLote = $("#form-lote", panel);
  let ejemplos = null;
  let detener = () => {};

  const dibujarPrevia = () => {
    detener();
    try {
      const { cuerpo } = leerAutomata(form);
      reproductor.innerHTML = `<svg id="svg-automata" class="diagrama"></svg>`;
      dibujarDiagrama($("svg", reproductor), diagramaLocal(cuerpo));
    } catch (error) {
      aviso(error.message, "error");
    }
  };

  const cargarEjemplo = async () => {
    try {
      ejemplos ??= await get("/automatas/ejemplos");
    } catch (error) {
      aviso(error.message, "error");
      return;
    }
    const tipo = form.elements.tipo.value;
    const ejemplo = ejemplos[tipo];
    const f = form.elements;
    f.estados.value = ejemplo.estados.join(", ");
    f.alfabeto.value = ejemplo.alfabeto.join(", ");
    f.inicial.value = ejemplo.inicial;
    f.finales.value = ejemplo.finales.join(", ");
    f.transiciones.value = transicionesATexto(ejemplo.transiciones);
    f.cadena.value = ejemplo.cadena;
    $(".descripcion-ejemplo", form).textContent = `Ejemplo: ${ejemplo.descripcion}.`;
    formLote.elements.cadenas.value = PRUEBAS_LOTE[tipo].join("\n");
    salida.innerHTML = "";
    $(".salida-lote", formLote).innerHTML = "";
    dibujarPrevia();
  };

  form.elements.tipo.addEventListener("change", cargarEjemplo);
  $("[data-ejemplo]", form).addEventListener("click", cargarEjemplo);
  $("[data-previa]", form).addEventListener("click", dibujarPrevia);

  form.addEventListener("submit", evento => {
    evento.preventDefault();
    ejecutar($("button.primario", form), salida, async () => {
      const { tipo, cuerpo } = leerAutomata(form);
      const respuesta = await post(`/automatas/${tipo}`, cuerpo);
      detener();
      detener = mostrarEvaluacion(respuesta, tipo, reproductor, salida);
    });
  });

  formLote.addEventListener("submit", evento => {
    evento.preventDefault();
    const destino = $(".salida-lote", formLote);
    ejecutar($("button.primario", formLote), destino, async () => {
      const { tipo, cuerpo } = leerAutomata(form);
      const cadenas = formLote.elements.cadenas.value.split("\n").map(c => c.trim()).filter(c => c !== "");
      const respuestas = await Promise.all(cadenas.map(cadena => post(`/automatas/${tipo}`, { ...cuerpo, cadena })));
      const aceptadas = respuestas.filter(r => r.resultado.aceptada).length;
      destino.innerHTML = `
        <p><b>${aceptadas}</b> de ${respuestas.length} cadenas aceptadas.</p>
        ${tablaHTML([
          { titulo: "Cadena", valor: r => `<code>${esc(r.resultado.cadena)}</code>` },
          { titulo: "Resultado", valor: r => insignia(r.resultado.aceptada, "ACEPTADA", "RECHAZADA") },
          { titulo: "Motivo", valor: r => esc(r.resultado.motivo) },
        ], respuestas)}`;
    });
  });

  cargarEjemplo();
}

// Muestra el veredicto, la tabla de pasos y un reproductor que anima el recorrido del autómata.
// Regresa una función para detener la animación.
function mostrarEvaluacion(respuesta, tipo, contenedor, salida) {
  const r = respuesta.resultado;
  const pasos = respuesta.pasos;
  const recorrido = r.recorrido.map(x => [].concat(x ?? []));
  const simbolos = r.cadena === "ε" ? [] : [...r.cadena];
  let i = 0;
  let temporizador = null;

  // Un elemento nuevo en cada evaluación para que no se acumulen los eventos de la anterior.
  const reproductor = document.createElement("div");
  contenedor.replaceChildren(reproductor);
  reproductor.innerHTML = `
    <div class="cinta">${simbolos.map((s, j) => `<span data-j="${j}">${esc(s)}</span>`).join("") || "<span>ε</span>"}</div>
    <svg id="svg-automata" class="diagrama"></svg>
    <div class="controles">
      <button type="button" data-a="inicio" title="Inicio">⏮</button>
      <button type="button" data-a="atras" title="Paso anterior">◀</button>
      <button type="button" data-a="play" class="primario">▶ Reproducir</button>
      <button type="button" data-a="adelante" title="Paso siguiente">▶</button>
      <button type="button" data-a="fin" title="Final">⏭</button>
    </div>
    <p class="estado-paso"></p>`;
  const svg = $("svg", reproductor);
  const botonPlay = $('[data-a="play"]', reproductor);

  const pintar = () => {
    const activos = new Set(recorrido[i]);
    const anteriores = i > 0 ? new Set(recorrido[i - 1]) : null;
    const simbolo = i > 0 ? pasos[i - 1]?.simbolo : null;
    const ultimo = i === recorrido.length - 1;
    dibujarDiagrama(svg, r.diagrama, {
      claseNodo: id => (!activos.has(id) ? "" : ultimo ? (r.aceptada ? "acepta" : "rechaza") : "activa"),
      claseArista: a => {
        const usada = anteriores?.has(a.origen) && activos.has(a.destino) && a.simbolos.includes(simbolo);
        const vacia = tipo === "afnd-e" && a.simbolos.includes("ε") && activos.has(a.origen) && activos.has(a.destino);
        return usada || vacia ? "activa" : "";
      },
    });
    $$(".cinta span[data-j]", reproductor).forEach(celda => {
      const j = Number(celda.dataset.j);
      celda.className = j < i - 1 ? "leida" : j === i - 1 ? "actual" : "";
    });
    const conjunto = `{${[...activos].join(", ")}}`;
    let texto = i === 0 ? `Empieza en ${conjunto}` : `Paso ${i}: lee la letra '${simbolo}' y queda en ${conjunto}`;
    if (ultimo) texto += ` · ${r.aceptada ? "✅ terminó en un estado final: ACEPTADA" : "❌ no terminó en un estado final: RECHAZADA"}`;
    $(".estado-paso", reproductor).textContent = texto;
    $$("tr[data-i]", salida).forEach(fila => fila.classList.toggle("seleccionada", Number(fila.dataset.i) === i - 1));
  };

  const pausar = () => { clearInterval(temporizador); temporizador = null; botonPlay.textContent = "▶ Reproducir"; };
  const ir = nuevo => { i = Math.max(0, Math.min(recorrido.length - 1, nuevo)); pintar(); };

  reproductor.addEventListener("click", evento => {
    const accion = evento.target.closest("button")?.dataset.a;
    if (!accion) return;
    if (accion !== "play") pausar();
    if (accion === "inicio") ir(0);
    if (accion === "atras") ir(i - 1);
    if (accion === "adelante") ir(i + 1);
    if (accion === "fin") ir(recorrido.length - 1);
    if (accion === "play") {
      if (temporizador) return pausar();
      if (i === recorrido.length - 1) ir(0);
      botonPlay.textContent = "⏸ Pausa";
      temporizador = setInterval(() => (i < recorrido.length - 1 ? ir(i + 1) : pausar()), 900);
    }
  });

  const formato = v => (Array.isArray(v) ? `{${v.join(", ")}}` : v ?? "—");
  const TITULOS = {
    paso: "Paso", estado: "Estaba en", simbolo: "Leyó la letra", siguiente: "Se movió a",
    desde: "Estaba en", mover: "Al leer llegó a", clausura: "Con atajos ε", hacia: "Quedó en",
  };
  const columnas = pasos.length ? Object.keys(pasos[0]).map(clave => ({
    titulo: TITULOS[clave] ?? clave,
    valor: paso => esc(formato(paso[clave])),
  })) : [];
  const clausuras = r.clausuras
    ? `<p class="ayuda"><b>Cerraduras-ε</b> (a dónde se llega desde cada estado usando solo atajos ε): ${Object.entries(r.clausuras)
      .map(([q, c]) => `<span class="chip">ε-cierre(${esc(q)}) = {${esc(c.join(", "))}}</span>`).join(" ")}</p>`
    : "";

  salida.innerHTML = `
    <div class="veredicto ${r.aceptada ? "ok" : "mal"}">
      <b>La cadena '${esc(r.cadena)}' fue ${r.aceptada ? "ACEPTADA ✅" : "RECHAZADA ❌"}</b>
      <span>${esc(r.motivo)}</span>
      ${r.afd_completo === false ? `<span class="ayuda">Nota: el AFD no es completo (faltan transiciones).</span>` : ""}
    </div>
    <div class="rejilla-2">
      <div class="tarjeta">
        <h4>Recorrido paso a paso <small>haz clic en una fila para verla en el diagrama</small></h4>
        ${pasos.length ? tablaHTML(columnas, pasos) : "<p class='ayuda'>La palabra vacía no tiene letras, así que la máquina no se mueve.</p>"}
        ${comoLeerHTML(tipo === "afd"
          ? ["Cada renglón es una letra leída: dónde estaba la máquina, qué letra leyó y a dónde se movió."]
          : ["Las llaves { } agrupan <b>todos</b> los estados en los que la máquina puede estar al mismo tiempo.",
             "Si al final alguno de ellos es un estado final, la palabra se acepta."])}
        ${clausuras}
      </div>
      <div>${explicacionHTML(respuesta.explicacion)}</div>
    </div>
    ${jsonHTML(respuesta)}`;
  $$("tr[data-i]", salida).forEach(fila => fila.addEventListener("click", () => { pausar(); ir(Number(fila.dataset.i) + 1); }));

  pintar();
  return pausar;
}
