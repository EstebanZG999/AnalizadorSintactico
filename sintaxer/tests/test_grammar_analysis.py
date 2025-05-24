# tests/test_grammar_analysis.py

import os
import sys

# Permitir importar src
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

import pytest
from src.models.grammar_analysis import compute_first, compute_follow

@pytest.fixture
def arithmetic_grammar():
    """
    Grammar:
      E  → T E'
      E' → + T E' | ε
      T  → F T'
      T' → * F T' | ε
      F  → ( E ) | id
    """
    return {
        "E":  [["T", "E'"]],
        "E'": [["+", "T", "E'"], ["ε"]],
        "T":  [["F", "T'"]],
        "T'": [["*", "F", "T'"], ["ε"]],
        "F":  [["(", "E", ")"], ["id"]],
    }

def test_first_sets(arithmetic_grammar):
    first = compute_first(arithmetic_grammar)

    assert first["E"]  == {"(", "id"}
    assert first["E'"] == {"+", "ε"}
    assert first["T"]  == {"(", "id"}
    assert first["T'"] == {"*", "ε"}
    assert first["F"]  == {"(", "id"}

def test_follow_sets(arithmetic_grammar):
    first = compute_first(arithmetic_grammar)
    follow = compute_follow(arithmetic_grammar, start_symbol="E", first=first)

    # FOLLOW(E) contains ')' and '$'
    assert follow["E"]  >= {")", "$"}
    # FOLLOW(E') contains ')' and '$'
    assert follow["E'"] >= {")", "$"}
    # FOLLOW(T) contains '+' , ')' and '$'
    assert follow["T"]  >= {"+", ")", "$"}
    # FOLLOW(T') contains '+' , ')' and '$'
    assert follow["T'"] >= {"+", ")", "$"}
    # FOLLOW(F) contains '*' , '+' , ')' and '$'
    assert follow["F"]  >= {"*", "+", ")", "$"}
