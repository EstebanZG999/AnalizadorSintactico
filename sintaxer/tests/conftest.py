import os
import sys
import pytest

# __file__ apunta a sintaxer/tests/conftest.py
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Inserta sintaxer/ en sys.path para que 'src' sea importable
sys.path.insert(0, root)
