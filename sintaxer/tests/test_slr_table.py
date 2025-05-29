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
    # FOLLOW(S) = {'$'}
    follow_sets = {"S": {"$"}, "S'": set()}

    action, goto_table = construct_slr_table(
        states, transitions, simple_production, follow_sets
    )

    # Estado 0 tiene ítem S' → · S
    assert (0, 'S') in goto_table

    # Estado 0 debe hacer shift sobre el terminal 'a'
    assert (0, 'a') in action
    inst, target = action[(0, 'a')]
    assert inst == 'shift'
    # Y que ese shift vaya al mismo estado que transitions[(0,'a')]
    assert target == transitions[(0, 'a')]

    # Estado de aceptación: el que contiene S' → S·
    accept_state = next(
        i for i, st in enumerate(states)
        if Item("S'", ("S",), 1) in st.items
    )
    assert action[(accept_state, '$')] == ('accept', None)

def test_slr_reduce(simple_production):
    states, transitions = items(simple_production, start_symbol="S")
    follow_sets = {"S": {"$"}, "S'": set()}

    action, goto_table = construct_slr_table(
        states, transitions, simple_production, follow_sets
    )

    # Estado que contiene el ítem S → a·
    reduce_state = next(
        i for i, st in enumerate(states)
        if Item("S", ("a",), 1) in st.items
    )
    # La producción S→a es la única original: índice 0
    assert action[(reduce_state, '$')] == ('reduce', 0)