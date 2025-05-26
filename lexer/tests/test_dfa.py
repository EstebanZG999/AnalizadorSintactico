# tests/test_dfa.py
import pytest
from src.models.regex_parser import RegexParser
from src.models.syntax_tree import SyntaxTree
from src.models.dfa import DFA

@pytest.fixture
def make_dfa():
    def _mk(regex):
        parser = RegexParser(regex)
        postfix = parser.parse()
        tree = SyntaxTree(postfix)
        return DFA(tree)
    return _mk

def test_dfa_simple_acceptance(make_dfa):
    dfa = make_dfa("a#")
    assert dfa.simulate("a") is True
    assert dfa.simulate("")  is False
    assert dfa.simulate("b") is False

def test_dfa_concat(make_dfa):
    dfa = make_dfa("ab#")
    assert dfa.simulate("ab")
    assert not dfa.simulate("a")
    assert not dfa.simulate("b")

def test_dfa_kleene(make_dfa):
    dfa = make_dfa("a*#")
    assert dfa.simulate("")    
    assert dfa.simulate("aaaa")
    assert not dfa.simulate("b")

def test_dfa_union(make_dfa):
    dfa = make_dfa("(a|b)#")
    assert dfa.simulate("a")
    assert dfa.simulate("b")
    assert not dfa.simulate("ab")
