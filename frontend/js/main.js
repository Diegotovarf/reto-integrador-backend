// Punto de entrada: pestañas de los 3 módulos, indicador de conexión y arranque de cada módulo.
import { API_URL, get, guardarApi } from "./api.js";
import { $, $$ } from "./ui.js";
import { iniciarModulo1 } from "./modulo1.js";
import { iniciarModulo2 } from "./modulo2.js";
import { iniciarModulo3 } from "./modulo3.js";

function activarPestana(nombre) {
  $$(".pestanas button").forEach(b => b.classList.toggle("activa", b.dataset.tab === nombre));
  $$(".modulo").forEach(s => { s.hidden = s.id !== nombre; });
  history.replaceState(null, "", `#${nombre}`);
}

async function revisarConexion() {
  const indicador = $("#estado-api");
  try {
    await get("/");
    indicador.textContent = "Backend conectado";
    indicador.className = "punto-estado ok";
  } catch {
    indicador.textContent = "Backend sin conexión";
    indicador.className = "punto-estado mal";
  }
}

$$(".pestanas button").forEach(b => b.addEventListener("click", () => activarPestana(b.dataset.tab)));
$$("[data-ir]").forEach(b => b.addEventListener("click", () => { activarPestana(b.dataset.ir); scrollTo(0, 0); }));
activarPestana(["inicio", "modulo1", "modulo2", "modulo3"].includes(location.hash.slice(1)) ? location.hash.slice(1) : "inicio");

const formApi = $("#form-api");
formApi.elements.url.value = API_URL;
formApi.addEventListener("submit", evento => {
  evento.preventDefault();
  guardarApi(formApi.elements.url.value);
  location.reload();
});

revisarConexion();
setInterval(revisarConexion, 15000);

iniciarModulo1($("#modulo1 .contenido"));
iniciarModulo2($("#modulo2 .contenido"));
iniciarModulo3($("#modulo3 .contenido"));
