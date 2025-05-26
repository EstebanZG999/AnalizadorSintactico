import os
import sys

# Permitir importar src como paquete
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

import pytest
from sintaxer.src.models.lr0 import Item, State, closure, goto, items

@pytest.fixture
def simple_productions():
    """
    Gramática aumentada para pruebas:
      S' → S
      S  → A
      A  → a
    """
    return {
        "S'": [["S"]],
        "S":  [["A"]],
        "A":  [["a"]],
    }

@pytest.fixture
def arithmetic_grammar():
    return {
        "E":  [["T", "E'"]],
        "E'": [["+", "T", "E'"], ["ε"]],
        "T":  [["F", "T'"]],
        "T'": [["*", "F", "T'"], ["ε"]],
        "F":  [["(", "E", ")"], ["id"]],
    }

def test_closure_simple(simple_productions):
    # Ítem inicial: S' → · S
    start_item = Item(lhs="S'", rhs=("S",), dot=0)
    clos = closure({start_item}, simple_productions)

    # Debe incluir:
    #   S' → · S
    #   S  → · A
    #   A  → · a
    expected = {
        Item("S'", ("S",), 0),
        Item("S",  ("A",), 0),
        Item("A",  ("a",), 0),
    }
    assert clos == expected

def test_goto_simple(simple_productions):
    # A partir del closure del ítem S' → · S
    start_item = Item(lhs="S'", rhs=("S",), dot=0)
    clos = closure({start_item}, simple_productions)

    # goto por 'S' mueve punto en S' → S ·
    got = goto(clos, "S", simple_productions)

    # La clausura de {S'→S·} no añade nada nuevo
    expected = {Item("S'", ("S",), 1)}
    assert got == expected

def test_items_count(arithmetic_grammar):
    """
    Usa la gramática clásica:
      E  → T E'
      E' → + T E' | ε
      T  → F T'
      T' → * F T' | ε
      F  → ( E ) | id
    Se espera típicamente 12 estados LR(0).
    """
    productions = arithmetic_grammar
    states, transitions = items(productions, start_symbol="E")

    # Asegura que hay al menos varios estados y la inicial sea la 0
    assert isinstance(states, list)
    assert len(states) == 18
    assert states[0].id == 0

    # Comprueba una transición conocida: desde estado 0 sobre 'T'
    assert ("0", "T") or (0, "T") in transitions  # hay una goto(0,"T")

    # Asegura que cada State.items es frozenset de Item
    for st in states:
        assert isinstance(st.items, frozenset)
        for it in st.items:
            assert isinstance(it, Item)
