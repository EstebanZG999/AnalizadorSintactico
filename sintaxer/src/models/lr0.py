from dataclasses import dataclass
from typing import Tuple, FrozenSet, Dict, List, Set

@dataclass(frozen=True)
class Item:
    lhs: str          # p.ej. "E'"
    rhs: tuple[str]   # p.ej. ("+", "T", "E'")
    dot: int          # posición del punto

@dataclass
class State:
    id: int
    items: frozenset[Item]

def closure(items: Set[Item], productions: Dict[str, List[List[str]]]) -> Set[Item]:
    """
    Dado un conjunto de ítems LR(0), expande cerradura:
    Para cada ítem A → α · B β, añade B → · γ para cada producción B → γ.
    """
    closure_set = set(items)
    added = True
    while added:
        added = False
        for item in list(closure_set):
            # si el punto está antes de un símbolo
            if item.dot < len(item.rhs):
                B = item.rhs[item.dot]
                # Si B es un no terminal, añadir sus producciones con punto al inicio
                if B in productions:
                    for prod in productions[B]:
                        new_item = Item(lhs=B, rhs=tuple(prod), dot=0)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            added = True
    return closure_set

def goto(items: Set[Item], symbol: str, productions: Dict[str, List[List[str]]]) -> Set[Item]:
    """
    Mueve el punto sobre `symbol`: para cada ítem A → α · symbol β en `items`,
    genera A → α symbol · β y luego toma closure().
    """
    # Mover el punto sobre `symbol`
    moved = set()
    for item in items:
        if item.dot < len(item.rhs) and item.rhs[item.dot] == symbol:
            # crea un nuevo ítem con dot+1
            moved_item = Item(lhs=item.lhs, rhs=item.rhs, dot=item.dot + 1)
            moved.add(moved_item)
    # devuelve la cerradura de ese conjunto
    return closure(moved, productions)

def items(productions: dict, start_symbol: str) -> (list[State], dict):
    """
    Genera todos los estados del autómata LR(0):
     1. Estado 0 = closure({ S' → · S })
     2. Para cada estado I y cada símbolo X, compute J = goto(I, X).
     3. Si J no es vacío ni está en la lista, lo añades como nuevo estado.
    Devuelve la lista de estados y un map de transiciones {(i, X): j}.
    """
