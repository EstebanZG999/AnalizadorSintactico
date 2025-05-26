import os
import sys
import importlib.util
import tempfile

# Permitir importar src como paquete
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

import pytest
from src.generators.parser_generator import generate_parser_file

@pytest.fixture
def simple_slr_tables():
    # Caso trivial: una gramática S → a
    states = []           # No se usan aquí
    transitions = {}      # Idem
    productions = {"S": [["a"]]}
    # Acción de ejemplo: shift en 0 sobre 'a' a 1; accept en 1
    action = {(0, 'a'): ('shift', 1), (1, '$'): ('accept', None)}
    goto   = {(0, 'S'): 1}
    return action, goto, productions, 'S'

def test_generate_parser_file_executes(simple_slr_tables, tmp_path):
    action, goto, productions, start = simple_slr_tables
    output = tmp_path / "theparser.py"

    # Genera el parser
    generate_parser_file(action, goto, productions, start, str(output))
    assert output.exists()

    # Comprueba que el archivo contenga las cabeceras esperadas
    text = output.read_text()
    assert "class Parser" in text
    assert "ACTION" in text and "GOTO" in text
    assert f"START = '{start}'" in text

    # Intentar importar el módulo generado para verificar sintaxis
    spec = importlib.util.spec_from_file_location("theparser", str(output))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)   # debería no lanzar errores

    # Verificar que la clase Parser tenga los atributos
    Parser = getattr(module, "Parser")
    # Inicializar tablas y comprobar que contienen nuestras entradas
    Parser._init_tables()
    assert Parser.ACTION[(0, 'a')] == ('shift', 1)
    assert Parser.ACTION[(1, '$')] == ('accept', None)
    assert Parser.GOTO[(0, 'S')] == 1
