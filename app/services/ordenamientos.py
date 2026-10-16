"""Catálogo de algoritmos de ordenamiento con contadores de operaciones.

Cada función recibe una lista, no la modifica, y devuelve (lista_ordenada, contadores).
"""
import random


def _contadores(comparaciones, movimientos):
    return {"comparaciones": comparaciones, "movimientos": movimientos}


def burbuja(datos):
    a = list(datos)
    n = len(a)
    comparaciones = movimientos = 0
    for i in range(n - 1):
        hubo_intercambio = False
        for j in range(n - 1 - i):
            comparaciones += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                movimientos += 1
                hubo_intercambio = True
        if not hubo_intercambio:
            break
    return a, _contadores(comparaciones, movimientos)


def seleccion(datos):
    a = list(datos)
    n = len(a)
    comparaciones = movimientos = 0
    for i in range(n - 1):
        minimo = i
        for j in range(i + 1, n):
            comparaciones += 1
            if a[j] < a[minimo]:
                minimo = j
        if minimo != i:
            a[i], a[minimo] = a[minimo], a[i]
            movimientos += 1
    return a, _contadores(comparaciones, movimientos)


def insercion(datos):
    a = list(datos)
    comparaciones = movimientos = 0
    for i in range(1, len(a)):
        valor = a[i]
        j = i - 1
        while j >= 0:
            comparaciones += 1
            if a[j] <= valor:
                break
            a[j + 1] = a[j]
            movimientos += 1
            j -= 1
        a[j + 1] = valor
    return a, _contadores(comparaciones, movimientos)


def shell(datos):
    a = list(datos)
    n = len(a)
    comparaciones = movimientos = 0
    salto = n // 2
    while salto > 0:
        for i in range(salto, n):
            valor = a[i]
            j = i
            while j >= salto:
                comparaciones += 1
                if a[j - salto] <= valor:
                    break
                a[j] = a[j - salto]
                movimientos += 1
                j -= salto
            a[j] = valor
        salto //= 2
    return a, _contadores(comparaciones, movimientos)


def mergesort(datos):
    """Merge sort ascendente (iterativo): mezcla bloques de tamaño 1, 2, 4, …"""
    a = list(datos)
    n = len(a)
    comparaciones = movimientos = 0
    ancho = 1
    while ancho < n:
        for inicio in range(0, n, 2 * ancho):
            medio = min(inicio + ancho, n)
            fin = min(inicio + 2 * ancho, n)
            i, j = inicio, medio
            mezcla = []
            while i < medio and j < fin:
                comparaciones += 1
                if a[i] <= a[j]:
                    mezcla.append(a[i])
                    i += 1
                else:
                    mezcla.append(a[j])
                    j += 1
            mezcla.extend(a[i:medio])
            mezcla.extend(a[j:fin])
            a[inicio:fin] = mezcla
            movimientos += fin - inicio
        ancho *= 2
    return a, _contadores(comparaciones, movimientos)


def quicksort(datos):
    """Quicksort con partición de Hoare y pivote central; usa una pila explícita en lugar de recursión."""
    a = list(datos)
    comparaciones = movimientos = 0
    pendientes = [(0, len(a) - 1)]
    while pendientes:
        bajo, alto = pendientes.pop()
        if bajo >= alto:
            continue
        pivote = a[(bajo + alto) // 2]
        i, j = bajo - 1, alto + 1
        while True:
            i += 1
            comparaciones += 1
            while a[i] < pivote:
                i += 1
                comparaciones += 1
            j -= 1
            comparaciones += 1
            while a[j] > pivote:
                j -= 1
                comparaciones += 1
            if i >= j:
                break
            a[i], a[j] = a[j], a[i]
            movimientos += 1
        pendientes.append((bajo, j))
        pendientes.append((j + 1, alto))
    return a, _contadores(comparaciones, movimientos)


def heapsort(datos):
    a = list(datos)
    n = len(a)
    comparaciones = movimientos = 0

    def hundir(raiz, fin):
        nonlocal comparaciones, movimientos
        while True:
            hijo = 2 * raiz + 1
            if hijo >= fin:
                return
            if hijo + 1 < fin:
                comparaciones += 1
                if a[hijo] < a[hijo + 1]:
                    hijo += 1
            comparaciones += 1
            if a[raiz] >= a[hijo]:
                return
            a[raiz], a[hijo] = a[hijo], a[raiz]
            movimientos += 1
            raiz = hijo

    for i in range(n // 2 - 1, -1, -1):
        hundir(i, n)
    for fin in range(n - 1, 0, -1):
        a[0], a[fin] = a[fin], a[0]
        movimientos += 1
        hundir(0, fin)
    return a, _contadores(comparaciones, movimientos)


def timsort(datos):
    """sorted() de Python (Timsort, implementado en C). Sirve como referencia; no expone contadores."""
    return sorted(datos), _contadores(None, None)


CATALOGO = {
    "burbuja": {
        "nombre": "Burbuja (Bubble sort)", "funcion": burbuja,
        "mejor": "O(n)", "promedio": "O(n²)", "peor": "O(n²)", "espacio": "O(1)", "estable": True,
        "descripcion": "Compara pares vecinos y los intercambia si están en desorden; en cada pasada el mayor 'flota' al final. Se detiene si una pasada no hizo intercambios.",
    },
    "seleccion": {
        "nombre": "Selección (Selection sort)", "funcion": seleccion,
        "mejor": "O(n²)", "promedio": "O(n²)", "peor": "O(n²)", "espacio": "O(1)", "estable": False,
        "descripcion": "Busca el mínimo de la parte sin ordenar y lo coloca al inicio. Siempre hace n(n-1)/2 comparaciones, aunque los datos ya estén ordenados.",
    },
    "insercion": {
        "nombre": "Inserción (Insertion sort)", "funcion": insercion,
        "mejor": "O(n)", "promedio": "O(n²)", "peor": "O(n²)", "espacio": "O(1)", "estable": True,
        "descripcion": "Toma cada elemento y lo inserta en su lugar dentro de la parte ya ordenada, como al acomodar cartas en la mano. Muy rápido con datos casi ordenados.",
    },
    "shell": {
        "nombre": "Shell sort", "funcion": shell,
        "mejor": "O(n log n)", "promedio": "≈ O(n^1.5) (depende de los saltos)", "peor": "O(n²)", "espacio": "O(1)", "estable": False,
        "descripcion": "Generaliza la inserción: primero ordena elementos separados por un salto grande y luego reduce el salto hasta 1.",
    },
    "mergesort": {
        "nombre": "Mezcla (Merge sort)", "funcion": mergesort,
        "mejor": "O(n log n)", "promedio": "O(n log n)", "peor": "O(n log n)", "espacio": "O(n)", "estable": True,
        "descripcion": "Divide y vencerás: parte la lista en mitades, las ordena y las mezcla. Su tiempo no depende del orden inicial, pero necesita memoria extra.",
    },
    "quicksort": {
        "nombre": "Rápido (Quicksort)", "funcion": quicksort,
        "mejor": "O(n log n)", "promedio": "O(n log n)", "peor": "O(n²)", "espacio": "O(log n)", "estable": False,
        "descripcion": "Elige un pivote y reparte los elementos en menores y mayores; repite en cada parte. Suele ser el más rápido en la práctica.",
    },
    "heapsort": {
        "nombre": "Montículo (Heapsort)", "funcion": heapsort,
        "mejor": "O(n log n)", "promedio": "O(n log n)", "peor": "O(n log n)", "espacio": "O(1)", "estable": False,
        "descripcion": "Construye un montículo máximo y extrae repetidamente el mayor, colocándolo al final.",
    },
    "timsort": {
        "nombre": "Timsort (sorted de Python)", "funcion": timsort,
        "mejor": "O(n)", "promedio": "O(n log n)", "peor": "O(n log n)", "espacio": "O(n)", "estable": True,
        "descripcion": "Híbrido de mezcla e inserción que aprovecha los tramos ya ordenados. Está escrito en C, por eso sirve como referencia de velocidad.",
    },
}


def catalogo_publico() -> list[dict]:
    return [{"clave": clave, **{k: v for k, v in info.items() if k != "funcion"}}
            for clave, info in CATALOGO.items()]


def generar_datos(tamano: int, tipo: str, semilla: int) -> list[int]:
    rng = random.Random(semilla)
    if tipo == "pocos_unicos":
        return [rng.randint(0, 9) for _ in range(tamano)]
    datos = [rng.randint(0, max(100, tamano * 10)) for _ in range(tamano)]
    if tipo == "ordenado":
        datos.sort()
    elif tipo == "inverso":
        datos.sort(reverse=True)
    elif tipo == "casi_ordenado":
        datos.sort()
        for _ in range(max(1, tamano // 20)):
            i, j = rng.randrange(tamano), rng.randrange(tamano)
            datos[i], datos[j] = datos[j], datos[i]
    return datos
