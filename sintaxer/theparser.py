#!/usr/bin/env python3
# Auto-generated parser SLR(1)

import sys
from typing import List, Tuple, Any

class Parser:
    ACTION = {(1, '$'): ('accept', None), (3, 'TOKEN_4'): ('reduce', 5), (3, '$'): ('reduce', 5), (3, 'TOKEN_2'): ('reduce', 5), (4, 'TOKEN_4'): ('reduce', 3), (4, '$'): ('reduce', 3), (4, 'TOKEN_2'): ('reduce', 3), (5, '$'): ('reduce', 1), (5, 'TOKEN_2'): ('reduce', 1), (5, 'TOKEN_4'): ('reduce', 1), (9, '$'): ('reduce', 0), (9, 'TOKEN_2'): ('reduce', 0), (9, 'TOKEN_4'): ('reduce', 0), (10, 'TOKEN_4'): ('reduce', 4), (10, '$'): ('reduce', 4), (10, 'TOKEN_2'): ('reduce', 4), (11, 'TOKEN_4'): ('reduce', 2), (11, '$'): ('reduce', 2), (11, 'TOKEN_2'): ('reduce', 2)}
    GOTO = {(0, 'production1'): 1, (0, 'production3'): 4, (0, 'production2'): 5, (2, 'production1'): 7, (2, 'production3'): 4, (2, 'production2'): 5, (6, 'production3'): 4, (6, 'production2'): 9, (8, 'production3'): 11}
    PRODUCTIONS = [('production1', ['production1', 'TOKEN_2', 'production2']), ('production1', ['production2']), ('production2', ['production2', 'TOKEN_2', 'production3']), ('production2', ['production3']), ('production3', ['TOKEN_3', 'production1', 'TOKEN_4']), ('production3', ['TOKEN_1'])]
    START = 'production1'

    @classmethod
    def _init_tables(cls):
        # No-op: las tablas ya están inicializadas en variables de clase
        pass

    @classmethod
    def parse(cls, tokens: List[Tuple[str, Any]]) -> None:
        """Ejecuta el parsing shift-reduce. tokens: lista de (terminal, valor), sin EOF."""
        cls._init_tables()
        stack: List[int] = [0]
        tokens = tokens + [('$', None)]  # EOF
        pos = 0
        while True:
            state = stack[-1]
            term, _ = tokens[pos]
            action = cls.ACTION.get((state, term))
            if action is None:
                raise SyntaxError(f'Syntax error at position {pos}, unexpected token {term}')
            inst, arg = action
            if inst == 'shift':
                stack.append(arg)
                pos += 1
            elif inst == 'reduce':
                lhs, rhs = cls.PRODUCTIONS[arg]
                for _ in rhs:
                    stack.pop()
                state2 = stack[-1]
                goto_state = cls.GOTO.get((state2, lhs))
                if goto_state is None:
                    raise SyntaxError(f'Missing GOTO for state {state2} and symbol {lhs}')
                stack.append(goto_state)
            elif inst == 'accept':
                return
            else:
                raise SyntaxError(f'Invalid action {inst} in state {state}')

def main():
    """Invoca el parser generado desde línea de comandos."""
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <input_file>')
        sys.exit(1)
    filename = sys.argv[1]
    from sintaxer.src.runtime.parser_interface import LexerInterface
    text = open(filename).read()
    tokens = LexerInterface.tokenize(text)
    Parser.parse(tokens)
    print('Input parsed successfully.')

if __name__ == '__main__':
    main()
