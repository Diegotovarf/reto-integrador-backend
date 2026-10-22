// Comunicación con el backend (FastAPI). Todos los módulos piden datos a través de get() y post().

const CLAVE = "reto-integrador-api";

function leerGuardada() {
  try { return localStorage.getItem(CLAVE); } catch { return null; }
}

export const API_URL = (leerGuardada() || "http://localhost:8000").replace(/\/$/, "");

export function guardarApi(url) {
  try { localStorage.setItem(CLAVE, url.trim()); } catch { /* sin almacenamiento: se usa el valor por defecto */ }
}

// El backend responde 400 {"error": "..."} cuando los datos no tienen sentido
// y 422 {"detail": [...]} cuando falta un campo o tiene el tipo incorrecto.
function mensajeError(status, datos) {
  if (datos.error) return datos.error;
  if (Array.isArray(datos.detail)) {
    return datos.detail.map(d => `${d.loc.filter(p => p !== "body").join(" → ")}: ${d.msg}`).join(" · ");
  }
  return `El backend respondió con el código ${status}.`;
}

async function pedir(ruta, opciones) {
  let respuesta;
  try {
    respuesta = await fetch(API_URL + ruta, opciones);
  } catch {
    throw new Error(`No hay conexión con el backend en ${API_URL}. Revisa que uvicorn esté corriendo.`);
  }
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) throw new Error(mensajeError(respuesta.status, datos));
  return datos;
}

export const get = ruta => pedir(ruta);

export const post = (ruta, cuerpo) => pedir(ruta, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(cuerpo),
});
