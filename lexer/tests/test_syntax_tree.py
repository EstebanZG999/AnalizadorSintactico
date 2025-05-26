# tests/test_syntax_tree.py
import pytest
from src.models.regex_parser import RegexParser
from src.models.syntax_tree import SyntaxTree

@pytest.mark.parametrize("pattern, nullable, firstpos, lastpos", [
    ("a#",   False, {1},    {2}),       # 'a' luego '#'
    ("a*#",  False, {1,2},  {2}),       # 'a*' luego '#'
    ("ab#",  False, {1},    {3}),       # 'a'·'b'·'#'
    ("a|b#", False, {1,2}, {1,3}),      # (a|b) luego '#', lastpos incluye pos de 'a' y '#'
])
def test_syntax_tree_properties(pattern, nullable, firstpos, lastpos):
    # parseo y construcción
    parser = RegexParser(pattern)
    postfix = parser.parse()
    tree = SyntaxTree(postfix)
    root = tree.raiz

    # Chequeos básicos
    assert root.nullable == nullable
    assert root.firstpos == firstpos
    assert root.lastpos  == lastpos
