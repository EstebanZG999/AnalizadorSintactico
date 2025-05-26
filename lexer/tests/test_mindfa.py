# tests/test_mindfa.py
import pytest
from src.models.regex_parser import RegexParser
from src.models.syntax_tree import SyntaxTree
from src.models.dfa import DFA
from src.models.mindfa import minimize_dfa

@pytest.fixture
def make_dfa():
    def _mk(regex):
        parser = RegexParser(regex)
        postfix = parser.parse()
        tree = SyntaxTree(postfix)
        return DFA(tree)
    return _mk

def test_minimize_reduces_states(make_dfa):
    """Verifica que el DFA mínimo no tenga más estados que el original."""
    regex = "(a|b)*abb#"
    original = make_dfa(regex)
    minimized = minimize_dfa(original)
    assert len(minimized.states) <= len(original.states)

def test_minimize_preserves_language(make_dfa):
    """Comprueba que ambos DFA (original y mínimo) aceptan/rechazan las mismas cadenas."""
    regex = "(a|b)*abb#"
    dfa = make_dfa(regex)
    min_dfa = minimize_dfa(dfa)

    # Cadenas que deberían aceptarse (sin el marcador final)
    accepted = ["abb", "aabb", "abababb"]
    # Cadenas que deberían rechazarse
    rejected = ["ab", "aab", "bba", "aba", "ba"]

    for s in accepted:
        assert dfa.simulate(s), f"Original debe aceptar '{s}'"
        assert min_dfa.simulate(s), f"Mínimo debe aceptar '{s}'"
    for s in rejected:
        assert not dfa.simulate(s), f"Original no debe aceptar '{s}'"
        assert not min_dfa.simulate(s), f"Mínimo no debe aceptar '{s}'"
