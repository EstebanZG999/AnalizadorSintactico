# sintaxer/src/runtime/parser_interface.py

from typing import List, Tuple, Dict, Any

def parse(
    tokens: List[Tuple[str, Any]],
    action: Dict[Tuple[int, str], Tuple[str, int]],
    goto: Dict[Tuple[int, str], int],
    productions: List[Tuple[str, List[str]]],
    start_symbol: Any
) -> None:
    """
    Ejecuta el parsing shift-reduce SLR(1). Añade EOF '$' si no está presente.

    tokens: lista de (terminal, valor).
    action: tabla ACTION[(estado, terminal)] -> (inst, arg).
    goto:   tabla GOTO[(estado, no_terminal)] -> estado.
    productions: lista indexada de tuplas (lhs, rhs).
    start_symbol: símbolo inicial (no se usa en la lógica interna).
    """
    # Añadir EOF si falta
    if not tokens or tokens[-1][0] != '$':
        tokens = tokens + [('$', None)]

    stack: List[int] = [0]
    pos: int = 0

    while True:
        state = stack[-1]
        term, _ = tokens[pos]
        inst, arg = action.get((state, term), (None, None))

        if inst is None:
            expected = [t for (s, t), _ in action.items() if s == state]
            raise SyntaxError(
                f"Syntax error at position {pos}: unexpected token '{term}'. "
                f"Expected one of: {expected}"
            )

        if inst == 'shift':
            stack.append(arg)
            pos += 1

        elif inst == 'reduce':
            lhs, rhs = productions[arg]
            for _ in rhs:
                stack.pop()
            state2 = stack[-1]
            next_state = goto.get((state2, lhs))
            if next_state is None:
                raise SyntaxError(f"Missing GOTO for state {state2} and symbol '{lhs}'")
            stack.append(next_state)

        elif inst == 'accept':
            return

        else:
            raise SyntaxError(f"Invalid action '{inst}' in state {state}")


class ParserInterface:
    """
    Wrapper para el parser shift-reduce SLR(1).
    """
    def __init__(
        self,
        action: Dict[Tuple[int, str], Tuple[str, int]],
        goto: Dict[Tuple[int, str], int],
        productions: List[Tuple[str, List[str]]],
        start_symbol: Any
    ):
        self.action = action
        self.goto = goto
        self.productions = productions
        self.start_symbol = start_symbol

    def run(self, tokens: List[Tuple[str, Any]]) -> None:
        """
        Ejecuta el parser sobre la lista de tokens.
        tokens debe incluir ('$', None) al final (se añadirá si falta).
        """
        parse(tokens, self.action, self.goto, self.productions, self.start_symbol)
