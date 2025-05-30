import sys
import os

# Permitir importar el módulo src desde la raíz del proyecto
test_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, test_root)

import pytest
from sintaxer.src.models.yalp_parser import YalpParser

@pytest.fixture
def yalp_file(tmp_path):
    """Crea un archivo temporal .yalp con una gramática de prueba"""
    content = '''
        /* Definición de parser */
        
        /* INICIA Sección de TOKENS */
        %token TOKEN_1
        %token TOKEN_2
        %token TOKEN_3 TOKEN_4
        %token WS
        IGNORE WS
        /* FINALIZA Sección de TOKENS */
        
        %%
        
        /* INICIA Sección de PRODUCCIONES */
        production1:
              production1 TOKEN_2 production2
            | production2
        ;
        production2:
              production2 TOKEN_2 production3
            | production3
        ;
        production3:
              TOKEN_3 production1 TOKEN_4
            | TOKEN_1
        ;
        /* FINALIZA Sección de PRODUCCIONES */
        '''
    file_path = tmp_path / "parser_test.yalp"
    file_path.write_text(content)
    return str(file_path)


def test_tokens_and_ignores(yalp_file):
    parser = YalpParser()
    parser.parse_file(yalp_file)

    # Verifica tokens declarados
    assert parser.tokens == ['TOKEN_1', 'TOKEN_2', 'TOKEN_3', 'TOKEN_4', 'WS']
    # Verifica tokens ignorados
    assert parser.ignores == {'WS'}


def test_productions(yalp_file):
    parser = YalpParser()
    parser.parse_file(yalp_file)

    expected_productions = {
        'production1': [
            ['production1', 'TOKEN_2', 'production2'],
            ['production2'],
        ],
        'production2': [
            ['production2', 'TOKEN_2', 'production3'],
            ['production3'],
        ],
        'production3': [
            ['TOKEN_3', 'production1', 'TOKEN_4'],
            ['TOKEN_1'],
        ],
    }
    assert parser.productions == expected_productions
