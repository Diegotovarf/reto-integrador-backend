from app.respuesta import crear_explicacion

TEORIA = {
    "afd": (
        "Un Autómata Finito Determinista es una 5-tupla (Q, Σ, δ, q₀, F): estados, alfabeto, función de transición, "
        "estado inicial y estados finales. 'Determinista' significa que para cada estado y símbolo hay a lo sumo un "
        "estado siguiente, así que el autómata sigue un único camino. La cadena se acepta si al terminar de leerla "
        "el autómata está en un estado de F."
    ),
    "afnd": (
        "Un Autómata Finito No Determinista permite que δ(q, a) sea un conjunto de estados: el autómata puede "
        "'adivinar' y seguir varias ramas a la vez. Se simula llevando el conjunto de todos los estados activos. "
        "La cadena se acepta si al menos una rama termina en un estado final. Todo AFND tiene un AFD equivalente "
        "(construcción de subconjuntos), así que reconocen los mismos lenguajes: los regulares."
    ),
    "afnd-e": (
        "Un AFND-ε además permite transiciones ε, que cambian de estado sin consumir ningún símbolo. La cerradura-ε "
        "de un estado es el conjunto de estados alcanzables desde él usando solo transiciones ε. En cada paso se "
        "mueve con el símbolo leído y luego se aplica la cerradura-ε. Siguen reconociendo exactamente los lenguajes "
        "regulares."
    ),
}

COMPLEJIDAD = {
    "afd": "O(|w|): se hace una sola transición por cada símbolo de la cadena.",
    "afnd": "O(|w|·|Q|²) en el peor caso: por cada símbolo se revisan las transiciones de todos los estados activos.",
    "afnd-e": "O(|w|·|Q|²): igual que el AFND, más el cálculo de la cerradura-ε en cada paso.",
}


def _trayectoria_afd(resultado: dict, pasos: list) -> str:
    texto = resultado["recorrido"][0]
    for paso in pasos:
        texto += f" —{paso['simbolo']}→ {paso['siguiente']}"
    return texto


def _trayectoria_afn(resultado: dict, pasos: list) -> str:
    texto = "{" + ", ".join(resultado["recorrido"][0]) + "}"
    for paso in pasos:
        texto += f" —{paso['simbolo']}→ {{" + ", ".join(paso["hacia"]) + "}"
    return texto


def explicar(tipo: str, resultado: dict, pasos: list) -> dict:
    trayectoria = _trayectoria_afd(resultado, pasos) if tipo == "afd" else _trayectoria_afn(resultado, pasos)
    veredicto = "ACEPTADA" if resultado["aceptada"] else "RECHAZADA"
    resumen = f"La cadena '{resultado['cadena']}' es {veredicto}. {resultado['motivo']} Recorrido: {trayectoria}."
    if tipo == "afd" and not resultado["afd_completo"]:
        resumen += (" Nota: a este AFD le faltan transiciones; cuando no hay transición se considera que va a un "
                    "estado de rechazo implícito.")
    return crear_explicacion(resumen, TEORIA[tipo], COMPLEJIDAD[tipo])
