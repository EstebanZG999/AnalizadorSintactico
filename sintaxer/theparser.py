#!/usr/bin/env python3
# Auto-generated parser SLR(1)

import sys
from typing import List, Tuple, Any

class Parser:
    ACTION = {(0, 'NUMBER'): ('shift', 2), (2, 'PLUS'): ('shift', 4), (3, 'SEMICOLON'): ('shift', 5), (4, 'NUMBER'): ('shift', 6), (1, '$'): ('accept', None), (5, '$'): ('reduce', 0), (6, 'SEMICOLON'): ('reduce', 1)}
    GOTO = {(0, 's'): 1, (0, 'p'): 3}
    PRODUCTIONS = [('s', ['p', 'SEMICOLON']), ('p', ['NUMBER', 'PLUS', 'NUMBER'])]
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
