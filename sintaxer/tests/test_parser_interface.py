import pytest
from sintaxer.src.runtime.parser_interface import parse

# Gramática simple: S -> 'a'
action = {(0,'a'): ('shift',1), (1,'$'):('accept',None)}
goto   = {(0,'S'):1}
# PRODUCTIONS list indexada: [(lhs, rhs_list), ...]
productions = [('S',['a'])]

tokens_correct = [('a','a')]
tokens_bad     = [('b','b')]

def test_parse_accepts_with_explicit_eof():
    """El parser acepta 'a' cuando se le pasa el EOF explícitamente."""
    tokens = [('a', 'a'), ('$', None)]
    # No debe lanzar excepción
    parse(tokens, action, goto, productions, start_symbol='S')

def test_parse_accepts_without_explicit_eof():
    """El parser añade el EOF internamente y acepta 'a'."""
    tokens = [('a', 'a')]
    # No debe lanzar excepción
    parse(tokens, action, goto, productions, start_symbol='S')

def test_parse_rejects_unexpected_token_with_eof():
    """Con EOF explícito, el parser rechaza token desconocido b."""
    tokens = [('b', 'b'), ('$', None)]
    with pytest.raises(SyntaxError) as excinfo:
        parse(tokens, action, goto, productions, start_symbol='S')
    assert 'unexpected token' in str(excinfo.value).lower()

def test_parse_rejects_unexpected_token_without_eof():
    """Sin EOF explícito, el parser rechaza token desconocido b."""
    tokens = [('b', 'b')]
    with pytest.raises(SyntaxError) as excinfo:
        parse(tokens, action, goto, productions, start_symbol='S')
    assert 'unexpected token' in str(excinfo.value).lower()
