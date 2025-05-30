# sintaxer/src/models/slr_table.py

from typing import List, Dict, Tuple, Set
from sintaxer.src.models.lr0 import State, Item

def construct_slr_table(
    states: List[State],
    transitions: Dict[Tuple[int, str], int],
    productions: Dict[str, List[List[str]]],
    follow_sets: Dict[str, Set[str]]
) -> Tuple[
    Dict[Tuple[int, str], Tuple[str, int | None]],
    Dict[Tuple[int, str], int]
]:
    action: Dict[Tuple[int, str], Tuple[str, int | None]] = {}
    goto:   Dict[Tuple[int, str], int] = {}
    """
    Crea las tablas de análisis SLR(1) ACTION y GOTO.
    Parámetros:
    - states: lista de objetos State que representan conjuntos de elementos LR(0).
    - transiciones: mapeo (estado_id, símbolo) -> siguiente_estado_id.
    - producciones: producciones gramaticales que asignan no-terminales a listas de lados derechos.
    - follow_sets: conjuntos FOLLOW precalculados para cada no terminal.

    Devuelve:
    - action: dict que mapea (estado_id, terminal) a una tupla:
        ('desplazar', siguiente_estado) o
        ('reducir', índice_producción) o
        ('aceptar', Ninguno)
    - goto: dict asignación (id_estado, no_terminal) -> id_estado_siguiente
    """
    # Sólo GOTO para no terminales
    for (state_id, symbol), target_state in transitions.items():
        if symbol in productions:
            goto[(state_id, symbol)] = target_state

    # SHIFT para terminales (los símbolos que no están en productions)
    for (state_id, symbol), target_state in transitions.items():
        if symbol not in productions:
            # Desplazar sobre terminal
            action[(state_id, symbol)] = ('shift', target_state)

    # Detectar símbolo aumentado (termina en apostrofe)
    augmented = next(lhs for lhs in productions if lhs.endswith("'"))

    # Listar producciones de usuario (excluyendo la aumentada) para índices
    # 1) Construimos all_productions con la aumentada al principio
    # Detectamos la clave de la producción aumentada (termina en apostrofe)
    augmented_lhs = next(lhs for lhs in productions if lhs.endswith("'"))
    # RHS de la aumentada (solo la primera alternativa)
    augmented_rhs = productions[augmented_lhs][0]

    # << DEBUG: imprime LHS y RHS de la producción aumentada
    print(f"DEBUG: augmented_lhs={augmented_lhs!r}, augmented_rhs={augmented_rhs!r}")

    # << DEBUG: imprime las primeras 10 claves de transitions
    print("DEBUG: transitions keys:", list(transitions.keys())[:10], "…")

    # Empezamos la lista con la aumentada
    all_productions: List[Tuple[str, List[str]]] = [(augmented_lhs, augmented_rhs)]
    # Añadimos luego todas las producciones originales
    for lhs, rhss in productions.items():
        if lhs == augmented_lhs:
            continue
        for rhs in rhss:
            all_productions.append((lhs, rhs))


    # REDUCE y ACCEPT
    for state in states:
        for item in state.items:
            if item.dot == len(item.rhs):
                # ACCEPT: ítem de la producción aumentada completa
                if item.lhs == augmented and list(item.rhs) == productions[augmented][0]:
                    action[(state.id, '$')] = ('accept', None)
                else:
                    # REDUCE: buscamos índice en all_productions
                    prod_index = all_productions.index((item.lhs, list(item.rhs)))
                    # Como PRODUCTIONS en theparser.py sólo contiene las producciones originales
                    # el parser es prod_index-1.
                    reduce_index = prod_index - 1
                    for lookahead in follow_sets.get(item.lhs, []):
                        action[(state.id, lookahead)] = ('reduce', reduce_index)

    # —————————————————————————————
    # FORZAR el ACCEPT cuando lleguemos al estado de "s’ → s ·"
    # El estado de aceptación es goto(0, start_symbol)
    start_symbol = augmented_rhs[0]               # el lhs real, p.ej. 's'
    accept_state = transitions.get((0, start_symbol))
    print(f"DEBUG: start_symbol={start_symbol!r}, accept_state={accept_state!r}")
    if accept_state is not None:
        action[(accept_state, '$')] = ('accept', None)
        print(f"DEBUG: forced accept at state {accept_state}")
    # —————————————————————————————

    return action, goto
