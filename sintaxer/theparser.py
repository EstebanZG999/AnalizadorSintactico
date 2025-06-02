#!/usr/bin/env python3
# Auto-generated parser SLR(1)

import sys
from typing import List, Tuple, Any

class Parser:
    ACTION = {(0, 'LBRACKET'): ('shift', 3), (0, 'ID'): ('shift', 4), (2, 'GT'): ('shift', 6), (3, 'LBRACKET'): ('shift', 3), (3, 'ID'): ('shift', 4), (5, 'LT'): ('shift', 8), (6, 'LBRACKET'): ('shift', 3), (6, 'ID'): ('shift', 4), (7, 'RBRACKET'): ('shift', 10), (7, 'LT'): ('shift', 8), (8, 'LBRACKET'): ('shift', 3), (8, 'ID'): ('shift', 4), (11, 'GT'): ('shift', 6), (1, 'RBRACKET'): ('reduce', 4), (1, '$'): ('reduce', 4), (1, 'LT'): ('reduce', 4), (1, 'GT'): ('reduce', 4), (2, 'RBRACKET'): ('reduce', 2), (2, 'LT'): ('reduce', 2), (2, '$'): ('reduce', 2), (4, 'RBRACKET'): ('reduce', 6), (4, 'GT'): ('reduce', 6), (4, 'LT'): ('reduce', 6), (4, '$'): ('reduce', 6), (5, '$'): ('accept', None), (9, 'RBRACKET'): ('reduce', 3), (9, '$'): ('reduce', 3), (9, 'LT'): ('reduce', 3), (9, 'GT'): ('reduce', 3), (10, 'RBRACKET'): ('reduce', 5), (10, 'GT'): ('reduce', 5), (10, 'LT'): ('reduce', 5), (10, '$'): ('reduce', 5), (11, 'RBRACKET'): ('reduce', 1), (11, 'LT'): ('reduce', 1), (11, '$'): ('reduce', 1)}
    GOTO = {(0, 'q'): 1, (0, 'p'): 2, (0, 's'): 5, (3, 'q'): 1, (3, 'p'): 2, (3, 's'): 7, (6, 'q'): 9, (8, 'q'): 1, (8, 'p'): 11}
    PRODUCTIONS = [("s'", ['s']), ('s', ['s', 'LT', 'p']), ('s', ['p']), ('p', ['p', 'GT', 'q']), ('p', ['q']), ('q', ['LBRACKET', 's', 'RBRACKET']), ('q', ['ID'])]
    START = 's'

    @classmethod
    def _init_tables(cls):
        # No-op: las tablas ya están inicializadas en variables de clase
        pass

    @classmethod
    def parse(cls, tokens: List[Tuple[str, Any]]) -> None:
        """Ejecuta el parsing shift-reduce. tokens: lista de (terminal, valor), sin EOF."""
        cls._init_tables()
        stack: List[int] = [0]
        # Mapear el EOF que venga del lexer al marcador '$'
        tokens = [( '$', None) if term == 'EOF' else (term, val) for term, val in tokens]
        tokens = tokens + [('$', None)]  # EOF
        pos = 0
        # Detectar estado de aceptación dinámicamente
        ACCEPT_STATE = None
        for (st, sym), inst in cls.ACTION.items():
            if sym == '$' and inst[0] == 'accept':
                ACCEPT_STATE = st
                break

        while True:
            state = stack[-1]
            term, _ = tokens[pos]
            # Si el parser ve literal 'EOF', lo trata como fin de input
            if term == 'EOF':
                term = '$'
            # Si estamos en EOF y en el estado de aceptación, terminamos
            if term == '$' and state == ACCEPT_STATE:
                return

            print(f"DEBUG-PARSE → state={state}, term={term!r}, ACCEPT_STATE={ACCEPT_STATE}")
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
