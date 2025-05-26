import os
import sys

# Permitir importar src como paquete
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

import pytest
from sintaxer.src.models.lr0 import Item, State, closure, goto, items
from sintaxer.src.models.slr_table import construct_slr_table

@pytest.fixture
def simple_production():
    # Gramática mínima:
    #   S' → S
    #   S  → a
    return {
        "S'": [["S"]],
        "S":  [["a"]],
    }

def test_slr_shift_and_accept(simple_production):
    # Construir estados LR(0)
    states, transitions = items(simple_production, start_symbol="S")
    # FIRST/FOLLOW sencillos: FOLLOW(S) = {'$'}
    follow_sets = {"S": {"$"}, "S'": set()}

    action, goto_table = construct_slr_table(
        states, transitions, simple_production, follow_sets
    )

    # Estado 0 tiene ítem S' → · S ; goto(0,'S') = estado 1
    assert (0, 'S') in goto_table
    # En estado 0 con terminal 'a' no hay acción shift (se usa goto), así acción debe ser error
    assert (0, 'a') not in action

    # Estado 1: closure de S' → S·  y S → · a  y A? no, revisar ítems...
    # Más importante: en estado que contenga S → a·, sobre '$' debe ser accept (término aumentado)
    # Detectamos qué estado es el del ítem S' → S·
    accept_state = next(
        i for i, st in enumerate(states)
        if Item("S'", ("S",), 1) in st.items
    )
    assert action[(accept_state, '$')] == ('accept', None)

def test_slr_reduce(simple_production):
    # Construir estados y transiciones
    states, transitions = items(simple_production, start_symbol="S")
    # FOLLOW(S) = {'$'}
    follow_sets = {"S": {"$"}, "S'": set()}

    action, goto_table = construct_slr_table(
        states, transitions, simple_production, follow_sets
    )

    # Encuentra el estado que tenga el ítem S → a· (dot al final)
    reduce_state = next(
        i for i, st in enumerate(states)
        if Item("S", ("a",), 1) in st.items
    )
    # La producción S→a es la primera (índice 0 en el listado simple)
    assert action[(reduce_state, '$')] == ('reduce', 0)
