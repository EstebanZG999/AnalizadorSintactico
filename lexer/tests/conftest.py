# tests/conftest.py

import os
import sys
import pytest

# 1) Asegúrate de que src/ esté en el path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 2) Fixture que genera thelexer.py y extiende el DFA, antes de cualquier test
from controllers.main_controller import generate_lexer

@pytest.fixture(scope="session", autouse=True)
def build_thelexer():
    # Genera o actualiza thelexer.py a partir de inputs/lexer.yal
    generate_lexer()
    # no return; es solo setup
