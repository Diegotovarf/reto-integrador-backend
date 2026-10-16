from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.errores import ErrorEntrada
from app.routers import automatas, benchmark, grafos, lenguajes

app = FastAPI(
    title="Reto Integrador · Laboratorio de autómatas, rutas y complejidad",
    description=(
        "Backend del producto para que estudiantes de nuevo ingreso experimenten con lenguajes, autómatas, "
        "optimización de rutas y complejidad algorítmica. Toda respuesta incluye una explicación del proceso "
        "y su base teórica."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ErrorEntrada)
async def manejar_error_entrada(_: Request, error: ErrorEntrada):
    return JSONResponse(status_code=400, content={"error": str(error)})


app.include_router(lenguajes.router)
app.include_router(automatas.router)
app.include_router(grafos.router)
app.include_router(benchmark.router)


@app.get("/", tags=["General"])
def inicio():
    return {
        "producto": app.title,
        "documentacion": "/docs",
        "modulos": {
            "1. Traductor de lenguajes y verificador de reglas": [
                "POST /cadenas/operar", "POST /lenguajes/operar",
                "GET /automatas/ejemplos", "POST /automatas/afd", "POST /automatas/afnd", "POST /automatas/afnd-e",
            ],
            "2. Asistente de logística y optimización": [
                "GET /grafos/ejemplos", "POST /grafos/generar", "POST /grafos/comparar", "POST /grafos/alcance",
            ],
            "3. Auditoría de escalabilidad y benchmark": [
                "GET /benchmark/ordenamiento/catalogo", "POST /benchmark/ordenamiento",
                "POST /benchmark/tsp", "POST /benchmark/tsp/escalabilidad",
            ],
        },
    }
