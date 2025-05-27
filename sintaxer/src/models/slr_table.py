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

    # Detectar símbolo aumentado (termina en apostrofe)
    augmented = next(lhs for lhs in productions if lhs.endswith("'"))

    # Listar producciones de usuario (excluyendo la aumentada) para índices
    all_productions: List[Tuple[str, List[str]]] = []
    for lhs, rhss in productions.items():
        if lhs == augmented:
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
                    # REDUCE: buscar índice en all_productions
                    prod_index = all_productions.index((item.lhs, list(item.rhs)))
                    for lookahead in follow_sets.get(item.lhs, []):
                        action[(state.id, lookahead)] = ('reduce', prod_index)

    return action, goto
