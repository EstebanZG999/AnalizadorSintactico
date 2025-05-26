import pytest
from lexer.thelexer import Lexer
from sintaxer.src.runtime.parser_interface import parse

# Caso de prueba sencillo: expresión aritmética
def test_end_to_end_simple_expression():
    source = "1 + 2 * (3 - 4);\n"
    lexer = Lexer(source)
    tokens = lexer.get_tokens()
    parser = parse()
    ast = parser.parse(tokens)
    assert ast is not None

# Detección de error de sintaxis
def test_syntax_error_detected():
    source = "1 + * 3;"
    lexer = Lexer(source)
    tokens = lexer.get_tokens()
    parser = parse()
    with pytest.raises(Exception) as excinfo:
        parser.parse(tokens)
    msg = str(excinfo.value).lower()
    assert "unexpected token" in msg or "error" in msg
