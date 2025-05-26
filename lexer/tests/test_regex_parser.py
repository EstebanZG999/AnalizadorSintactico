# tests/test_regex_parser.py
import pytest
from src.models.regex_parser import RegexParser, Symbol

@pytest.mark.parametrize("pattern, expected_tokens, expected_postfix", [
    ("a|b#", ["a", "|", "b", ".", "#"],      ["a", "b", "#", ".", "|"]),
    ("ab#",  ["a", ".", "b", ".", "#"],      ["a", "b", ".", "#", "."]),
    ("a*#",  ["a", "*", ".", "#"],           ["a", "*", "#", "."]),
    ("[0-1]#", ["(", "0", "|", "1", ")", ".", "#"], ["0", "1", "|", "#", "."]),
 ])
def test_tokenize_and_postfix(pattern, expected_tokens, expected_postfix):
    parser = RegexParser(pattern)
    tokens = parser.parse()  # parse() hace tokenize+to_postfix
    # Comparamos sólo valores
    token_vals = [str(t) for t in parser.tokens]
    postfix_vals = [str(t) for t in tokens]
    # Ignorar el marcador final en la comprobación de postfix
    assert token_vals[:len(expected_tokens)] == expected_tokens
    assert postfix_vals[:len(expected_postfix)] == expected_postfix
