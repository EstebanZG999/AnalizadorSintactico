# sintaxer/tests/test_parser_integration.py

# sintaxer/tests/test_parser_integration.py
import os
import sys
import subprocess
import pytest
import textwrap
from lexer.thelexer import Lexer

@pytest.fixture(autouse=True)
def generate_parser(tmp_path):
    # Calcula la raíz del repo a partir de este archivo
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    run_parser = os.path.join(repo_root, "sintaxer", "run_parser.py")

    # Directorio temporal para la gramática
    grammar_dir = tmp_path / "inputs"
    grammar_dir.mkdir()
    grammar = grammar_dir / "simple.yalp"

    # Escribimos la gramática sin sangrías
    grammar.write_text(textwrap.dedent("""\
        %token NUMBER \\d+
        %token PLUS   \\+
        %token SEMICOLON ;
        %%
        expr :
            NUMBER PLUS NUMBER SEMICOLON
        ;
        """),
        encoding="utf-8"
    )

    # Ejecuta run_parser.py para generar theparser.py
    result = subprocess.run(
        [sys.executable, run_parser, str(grammar)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repo_root
    )
    assert result.returncode == 0, f"Parser generation failed:\n{result.stderr.decode()}"

# Importa la clase Parser del parser recién generado
from sintaxer.theparser import Parser

def test_end_to_end_simple_expression():
    source = "1 + 2 * (3 - 4);\n"
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