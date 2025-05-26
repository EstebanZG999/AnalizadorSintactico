# tests/test_lexer_integration.py
import pytest
from thelexer import Lexer

def test_lexer_simple_expression():
    """
    Usa la clase generada en thelexer.py para tokenizar una cadena
    y compara el resultado con la salida esperada según lexer.yal.
    """
    # Cadena de prueba: letra, +, número, salto de línea
    src = "A+3\n"
    lexer = Lexer(src)
    tokens = lexer.get_tokens()

    # Según las reglas de inputs/lexer.yal, esperamos:
    #   LETTER  "A"
    #   PLUS    "+"
    #   NUMBER  3
    #   EOL     None
    expected = [
        ("ID", "A"),    # gettoken mapea LETTER (o WORD) → depende de tu regla ORDER
        ("PLUS", "+"),
        ("NUMBER", 3),
        ("EOL",    "\n"),
    ]
    assert tokens == expected
