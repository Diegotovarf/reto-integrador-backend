"""Simulación de AFD, AFND y AFND-ε sobre una cadena."""
from app.errores import ErrorEntrada
from app.services.cadenas import mostrar, normalizar

EPSILON = "ε"
_SIMBOLOS_EPSILON = {"ε", "λ", "", "eps", "epsilon"}


def _normalizar_transiciones(transiciones: dict) -> dict:
    """Unifica las distintas formas de escribir ε como "ε"."""
    return {
        origen: {(EPSILON if simbolo in _SIMBOLOS_EPSILON else simbolo): destinos
                 for simbolo, destinos in por_simbolo.items()}
        for origen, por_simbolo in transiciones.items()
    }


def _como_lista(destinos) -> list[str]:
    return [destinos] if isinstance(destinos, str) else list(destinos)


def _validar(estados: list[str], alfabeto: list[str], inicial: str, finales: list[str],
             transiciones: dict, permite_epsilon: bool) -> None:
    conjunto = set(estados)
    if not conjunto:
        raise ErrorEntrada("El autómata debe tener al menos un estado.")
    if inicial not in conjunto:
        raise ErrorEntrada(f"El estado inicial '{inicial}' no está en el conjunto de estados Q.")
    sobrantes = sorted(set(finales) - conjunto)
    if sobrantes:
        raise ErrorEntrada(f"Los estados finales {sobrantes} no están en el conjunto de estados Q.")
    if any(simbolo in _SIMBOLOS_EPSILON for simbolo in alfabeto):
        raise ErrorEntrada("ε no puede formar parte del alfabeto Σ: representa la cadena vacía.")

    for origen, por_simbolo in transiciones.items():
        if origen not in conjunto:
            raise ErrorEntrada(f"Hay transiciones desde '{origen}', que no está en Q.")
        for simbolo, destinos in por_simbolo.items():
            if simbolo == EPSILON:
                if not permite_epsilon:
                    raise ErrorEntrada("El autómata tiene transiciones ε; evalúalo como AFND-ε.")
            elif simbolo not in alfabeto:
                raise ErrorEntrada(f"La transición δ({origen}, {simbolo}) usa un símbolo que no está en Σ.")
            invalidos = [d for d in _como_lista(destinos) if d not in conjunto]
            if invalidos:
                raise ErrorEntrada(f"La transición δ({origen}, {simbolo}) lleva a estados que no están en Q: {invalidos}.")


def diagrama(estados: list[str], inicial: str, finales: list[str], transiciones: dict) -> dict:
    """Nodos y aristas para dibujar el autómata. Las aristas paralelas se agrupan."""
    etiquetas: dict[tuple[str, str], list[str]] = {}
    for origen, por_simbolo in transiciones.items():
        for simbolo, destinos in por_simbolo.items():
            for destino in _como_lista(destinos):
                etiquetas.setdefault((origen, destino), []).append(simbolo)
    return {
        "nodos": [{"id": e, "inicial": e == inicial, "final": e in finales} for e in estados],
        "aristas": [{"origen": o, "destino": d, "simbolos": sorted(s)} for (o, d), s in etiquetas.items()],
    }


def evaluar_afd(estados, alfabeto, transiciones, inicial, finales, cadena):
    transiciones = _normalizar_transiciones(transiciones)
    _validar(estados, alfabeto, inicial, finales, transiciones, permite_epsilon=False)
    w = normalizar(cadena)

    actual = inicial
    recorrido = [actual]
    pasos = []
    motivo = None
    for posicion, simbolo in enumerate(w, start=1):
        if simbolo not in alfabeto:
            motivo = f"El símbolo '{simbolo}' (posición {posicion}) no pertenece al alfabeto Σ, por lo que la cadena se rechaza."
            break
        siguiente = transiciones.get(actual, {}).get(simbolo)
        if siguiente is None:
            motivo = f"No existe la transición δ({actual}, {simbolo}): el autómata se bloquea y la cadena se rechaza."
            break
        pasos.append({"paso": posicion, "estado": actual, "simbolo": simbolo, "siguiente": siguiente})
        actual = siguiente
        recorrido.append(actual)

    aceptada = motivo is None and actual in finales
    if motivo is None:
        motivo = (f"Se leyó toda la cadena y el autómata terminó en {actual}, "
                  f"que {'sí' if aceptada else 'no'} es un estado final.")

    resultado = {
        "cadena": mostrar(w),
        "aceptada": aceptada,
        "estado_final": actual,
        "recorrido": recorrido,
        "motivo": motivo,
        "afd_completo": all(s in transiciones.get(e, {}) for e in estados for s in alfabeto),
        "diagrama": diagrama(estados, inicial, finales, transiciones),
    }
    return resultado, pasos


def clausura_epsilon(estados: set[str], transiciones: dict) -> set[str]:
    """Estados alcanzables desde `estados` usando solo transiciones ε."""
    clausura = set(estados)
    pendientes = list(estados)
    while pendientes:
        estado = pendientes.pop()
        for destino in transiciones.get(estado, {}).get(EPSILON, []):
            if destino not in clausura:
                clausura.add(destino)
                pendientes.append(destino)
    return clausura


def _evaluar_no_determinista(estados, alfabeto, transiciones, inicial, finales, cadena, con_epsilon):
    transiciones = _normalizar_transiciones(transiciones)
    _validar(estados, alfabeto, inicial, finales, transiciones, permite_epsilon=con_epsilon)
    cerrar = (lambda conjunto: clausura_epsilon(conjunto, transiciones)) if con_epsilon else set
    w = normalizar(cadena)

    actuales = cerrar({inicial})
    recorrido = [sorted(actuales)]
    pasos = []
    motivo = None
    for posicion, simbolo in enumerate(w, start=1):
        if simbolo not in alfabeto:
            motivo = f"El símbolo '{simbolo}' (posición {posicion}) no pertenece al alfabeto Σ, por lo que la cadena se rechaza."
            actuales = set()
            break
        movidos = {d for e in actuales for d in transiciones.get(e, {}).get(simbolo, [])}
        siguientes = cerrar(movidos)
        paso = {"paso": posicion, "simbolo": simbolo, "desde": sorted(actuales), "mover": sorted(movidos)}
        if con_epsilon:
            paso["clausura"] = sorted(siguientes)
        paso["hacia"] = sorted(siguientes)
        pasos.append(paso)
        actuales = siguientes
        recorrido.append(sorted(actuales))
        if not actuales:
            motivo = (f"Después de leer '{simbolo}' (posición {posicion}) no queda ningún estado activo: "
                      "todas las ramas se bloquearon y la cadena se rechaza.")
            break

    alcanzados = sorted(actuales & set(finales))
    aceptada = bool(alcanzados)
    if motivo is None:
        if aceptada:
            motivo = f"Se leyó toda la cadena y entre los estados activos {sorted(actuales)} hay estados finales: {alcanzados}."
        else:
            motivo = f"Se leyó toda la cadena, pero ninguno de los estados activos {sorted(actuales)} es final."

    resultado = {
        "cadena": mostrar(w),
        "aceptada": aceptada,
        "estados_activos_finales": sorted(actuales),
        "estados_finales_alcanzados": alcanzados,
        "recorrido": recorrido,
        "motivo": motivo,
        "diagrama": diagrama(estados, inicial, finales, transiciones),
    }
    if con_epsilon:
        resultado["clausuras"] = {e: sorted(clausura_epsilon({e}, transiciones)) for e in estados}
    return resultado, pasos


def evaluar_afnd(estados, alfabeto, transiciones, inicial, finales, cadena):
    return _evaluar_no_determinista(estados, alfabeto, transiciones, inicial, finales, cadena, con_epsilon=False)


def evaluar_afnd_epsilon(estados, alfabeto, transiciones, inicial, finales, cadena):
    return _evaluar_no_determinista(estados, alfabeto, transiciones, inicial, finales, cadena, con_epsilon=True)
