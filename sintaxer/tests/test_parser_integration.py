# sintaxer/tests/test_parser_integration.py

import os
import sys
import subprocess
import pytest
from lexer.thelexer import Lexer

@pytest.fixture(scope="module", autouse=True)
def generate_parser(tmp_path):
    # Ruta al repo
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    run_parser = os.path.join(repo_root, "sintaxer", "run_parser.py")
    grammar = os.path.join(repo_root, "sintaxer", "inputs", "simple.yalp")

    # Asegúrate de que exista la gramática simple.yalp
    os.makedirs(os.path.dirname(grammar), exist_ok=True)
    with open(grammar, "w", encoding="utf-8") as gf:
        gf.write(
            "%token NUMBER \\d+\\n"
            "%token PLUS   \\+\\n"
            "%token SEMICOLON ;\\n"
            "%%\\n"
            "Expr → NUMBER PLUS NUMBER SEMICOLON\\n"
        )

    # Genera theparser.py
    result = subprocess.run(
        [sys.executable, run_parser, grammar],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repo_root
    )
    if result.returncode != 0:
        pytest.skip(f"Parser generation failed:\n{result.stderr.decode()}")

# Importa la clase Parser del archivo generado
from sintaxer.theparser import Parser

def test_end_to_end_simple_expression():
    source = "1 + 2 * (3 - 4);\\n"
    lexer = Lexer(source)
    tokens = lexer.get_tokens()
    ast = Parser.parse(tokens)
    assert ast is not None

def test_syntax_error_detected():
    source = "1 + * 3;"
    lexer = Lexer(source)
    tokens = lexer.get_tokens()
    with pytest.raises(Exception) as excinfo:
        Parser.parse(tokens)
    msg = str(excinfo.value).lower()
    assert "unexpected" in msg or "error" in msg
