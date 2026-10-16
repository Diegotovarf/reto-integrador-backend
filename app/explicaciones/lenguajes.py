from app.respuesta import crear_explicacion
from app.services.cadenas import mostrar

TEORIA_GENERAL_CADENAS = (
    "Una cadena (o palabra) es una secuencia finita de símbolos de un alfabeto Σ. "
    "La cadena vacía ε no tiene símbolos y es el elemento neutro de la concatenación."
)

TEORIA_CADENAS = {
    "longitud": "La longitud |w| es el número de símbolos de la cadena. La cadena vacía ε tiene longitud 0.",
    "inversa": "La inversa wᴿ escribe los símbolos de w en orden contrario: si w = a₁a₂…aₙ, entonces wᴿ = aₙ…a₂a₁.",
    "concatenacion": "La concatenación w·v pega v al final de w. Es asociativa, ε es su elemento neutro (w·ε = w) y no es conmutativa: en general w·v ≠ v·w.",
    "potencia": "La potencia wⁿ concatena w consigo misma n veces. Por definición w⁰ = ε y wⁿ = w·wⁿ⁻¹, así que |wⁿ| = n·|w|.",
    "prefijos": "Un prefijo de w es cualquier cadena x tal que w = x·y. Una cadena de longitud n tiene n + 1 prefijos, incluidos ε y w.",
    "sufijos": "Un sufijo de w es cualquier cadena y tal que w = x·y. Una cadena de longitud n tiene n + 1 sufijos, incluidos ε y w.",
    "subcadenas": "Una subcadena de w es cualquier y tal que w = x·y·z. Todo prefijo y todo sufijo es subcadena; ε es subcadena de cualquier cadena.",
    "palindromo": "Una cadena es palíndromo cuando es igual a su inversa (w = wᴿ), por ejemplo 'abba' o 'aba'.",
    "conteo": "|w|ₐ denota cuántas veces aparece el símbolo a en w. La suma de todos los conteos es |w|.",
    "alfabeto": "Un alfabeto Σ es un conjunto finito de símbolos y Σ* es el conjunto de todas las cadenas que se pueden formar con ellos. w ∈ Σ* si y solo si cada símbolo de w pertenece a Σ.",
}


def explicar_cadena(operacion: str, w: str, v: str | None, n: int | None, resultado) -> dict:
    W = mostrar(w)
    resumenes = {
        "longitud": lambda: f"|{W}| = {resultado}: la cadena tiene {resultado} símbolo(s).",
        "inversa": lambda: f"Al leer '{W}' de derecha a izquierda se obtiene '{resultado}'.",
        "concatenacion": lambda: f"'{W}' · '{mostrar(v or '')}' = '{resultado}'.",
        "potencia": lambda: f"'{W}' elevada a {n} es '{resultado}': se escribe '{W}' {n} vez/veces seguidas.",
        "prefijos": lambda: f"'{W}' tiene {len(resultado)} prefijos distintos: {', '.join(resultado)}.",
        "sufijos": lambda: f"'{W}' tiene {len(resultado)} sufijos distintos: {', '.join(resultado)}.",
        "subcadenas": lambda: f"'{W}' tiene {len(resultado)} subcadenas distintas (contando ε).",
        "palindromo": lambda: (f"'{W}' {'sí' if resultado else 'no'} es palíndromo: "
                               f"su inversa es '{mostrar(w[::-1])}'."),
        "conteo": lambda: ("Conteo de símbolos: " + ", ".join(f"|{W}|_{s} = {c}" for s, c in resultado.items())
                           if resultado else "La cadena vacía no contiene símbolos."),
        "alfabeto": lambda: (f"'{W}' pertenece a Σ*: todos sus símbolos están en el alfabeto." if resultado["pertenece"]
                             else f"'{W}' no pertenece a Σ*: los símbolos {resultado['simbolos_invalidos']} no están en el alfabeto."),
    }
    return crear_explicacion(resumenes[operacion](), TEORIA_CADENAS[operacion])


TEORIA_GENERAL_LENGUAJES = (
    "Un lenguaje es un conjunto de cadenas sobre un alfabeto Σ, es decir, un subconjunto de Σ*. "
    "Como son conjuntos, admiten las operaciones de conjuntos (unión, intersección, diferencia) "
    "y además operaciones propias de las cadenas (concatenación, potencia, cerraduras)."
)

NOMBRES_LENGUAJES = {
    "union": "Unión L ∪ M",
    "interseccion": "Intersección L ∩ M",
    "diferencia": "Diferencia L − M",
    "diferencia_simetrica": "Diferencia simétrica L △ M",
    "concatenacion": "Concatenación L·M",
    "potencia": "Potencia Lⁿ",
    "kleene": "Cerradura de Kleene L*",
    "positiva": "Cerradura positiva L⁺",
    "inversa": "Inversa Lᴿ",
    "complemento": "Complemento L̄",
}

TEORIA_LENGUAJES = {
    "union": "L ∪ M contiene las cadenas que están en L, en M o en ambos.",
    "interseccion": "L ∩ M contiene solo las cadenas que están en ambos lenguajes a la vez.",
    "diferencia": "L − M contiene las cadenas de L que no están en M.",
    "diferencia_simetrica": "L △ M = (L − M) ∪ (M − L): las cadenas que están en uno solo de los dos lenguajes.",
    "concatenacion": "L·M = {xy | x ∈ L, y ∈ M}: se pega cada cadena de L con cada cadena de M. Puede tener hasta |L|·|M| cadenas (menos si algunas combinaciones coinciden).",
    "potencia": "Lⁿ es L concatenado consigo mismo n veces. L⁰ = {ε} para cualquier L.",
    "kleene": "L* = L⁰ ∪ L¹ ∪ L² ∪ … reúne todas las concatenaciones de cero o más cadenas de L. Siempre contiene ε y es infinito si L tiene alguna cadena no vacía, por eso aquí se calcula hasta Lᵏ.",
    "positiva": "L⁺ = L¹ ∪ L² ∪ … reúne las concatenaciones de una o más cadenas de L. Contiene ε solo si ε ∈ L. Aquí se calcula hasta Lᵏ.",
    "inversa": "Lᴿ = {wᴿ | w ∈ L}: se invierte cada cadena del lenguaje.",
    "complemento": "L̄ = Σ* − L contiene todas las cadenas sobre Σ que no están en L. Como Σ* es infinito, aquí se calcula dentro de Σ^≤k (cadenas de longitud 0 a k).",
}


def explicar_lenguaje(operacion: str, L: set, M: set, k: int, n: int, resultado: set,
                      tamano_universo: int | None = None) -> dict:
    nombre = NOMBRES_LENGUAJES[operacion]
    resumen = f"{nombre}: el resultado tiene {len(resultado)} cadena(s)"
    if operacion in {"union", "interseccion", "diferencia", "diferencia_simetrica", "concatenacion"}:
        resumen += f" a partir de |L| = {len(L)} y |M| = {len(M)}."
    elif operacion == "potencia":
        resumen += f", formadas concatenando {n} cadena(s) de L."
    elif operacion in {"kleene", "positiva"}:
        resumen += f", considerando hasta {k} concatenaciones de cadenas de L."
    elif operacion == "complemento":
        resumen += f": son las cadenas de Σ^≤{k} ({tamano_universo} en total) que no están en L."
    else:
        resumen += "."
    return crear_explicacion(resumen, TEORIA_LENGUAJES[operacion])
