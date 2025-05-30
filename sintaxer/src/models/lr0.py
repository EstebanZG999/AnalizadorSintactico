# sintaxer/src/models/lr0.py

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

def items(productions: Dict[str, List[List[str]]],
          start_symbol: str
         ) -> Tuple[List[State], Dict[Tuple[int, str], int]]:
    """
    Genera todos los estados del autómata LR(0):
     1. Estado 0 = closure({ S' → · S })
     2. Para cada estado I y cada símbolo X, compute J = goto(I, X).
     3. Si J no es vacío ni está en la lista, lo añades como nuevo estado.
    Devuelve la lista de estados y un map de transiciones {(i, X): j}.
    """
    # Preparar producción aumentada S' → start_symbol
    augmented_start = f"{start_symbol}'"
    prods = {augmented_start: [[start_symbol]], **productions}

    # Estado inicial: closure({ Item(augmented_start, (start_symbol,), 0) })
    init_item = Item(lhs=augmented_start, rhs=(start_symbol,), dot=0)
    init_closure = closure({init_item}, prods)
    states = [State(id=0, items=frozenset(init_closure))]
    transitions = {}

    # Iterar sobre estados y todos los símbolos
    changed = True
    while changed:
        changed = False
        for state in list(states):
            for symbol in set(
                sym for item in state.items
                for sym in (item.rhs[item.dot:item.dot+1] if item.dot < len(item.rhs) else [])
            ):
                target = goto(state.items, symbol, prods)
                if not target:
                    continue
                # comprobar si ya existe un estado con esos ítems
                existing = next((s for s in states if s.items == frozenset(target)), None)
                if existing is None:
                    new_id = len(states)
                    states.append(State(id=new_id, items=frozenset(target)))
                    transitions[(state.id, symbol)] = new_id
                    changed = True
                else:
                    transitions[(state.id, symbol)] = existing.id

    return states, transitions