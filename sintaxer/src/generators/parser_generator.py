import sys
from typing import Dict, List, Tuple, Any


def generate_parser_file(
    action: Dict[Tuple[int, str], Tuple[str, Any]],
    goto: Dict[Tuple[int, str], int],
    productions: Dict[str, List[List[str]]],
    start_symbol: str,
    output_path: str
) -> None:
    """
    Genera un archivo Python con la clase Parser para un analizador SLR(1).
    """
    # Aplanar producciones en lista indexada
    prod_list: List[Tuple[str, List[str]]] = []
    for lhs, rhss in productions.items():
        for rhs in rhss:
            prod_list.append((lhs, rhs))

    # Representaciones literales de tablas y producciones
    action_repr = repr(action)
    goto_repr   = repr(goto)
    prods_repr  = repr(prod_list)

    # Construir contenido de theparser.py
    lines: List[str] = []
    lines.append("#!/usr/bin/env python3")
    lines.append("# Auto-generated parser SLR(1)")
    lines.append("")
    lines.append("import sys")
    lines.append("from typing import List, Tuple, Any")
    lines.append("")
    lines.append("class Parser:")
    lines.append(f"    ACTION = {action_repr}")
    lines.append(f"    GOTO = {goto_repr}")
    lines.append(f"    PRODUCTIONS = {prods_repr}")
    lines.append(f"    START = '{start_symbol}'")
    lines.append("")
    lines.append("    @classmethod")
    lines.append("    def _init_tables(cls):")
    lines.append("        # No-op: las tablas ya están inicializadas en variables de clase")
    lines.append("        pass")
    lines.append("")
    lines.append("    @classmethod")
    lines.append("    def parse(cls, tokens: List[Tuple[str, Any]]) -> None:")
    lines.append("        \"\"\"Ejecuta el parsing shift-reduce. tokens: lista de (terminal, valor), sin EOF.\"\"\"")
    lines.append("        cls._init_tables()")
    lines.append("        stack: List[int] = [0]")
    lines.append("        tokens = tokens + [('$', None)]  # EOF")
    lines.append("        pos = 0")
    lines.append("        while True:")
    lines.append("            state = stack[-1]")
    lines.append("            term, _ = tokens[pos]")
    lines.append("            action = cls.ACTION.get((state, term))")
    lines.append("            if action is None:")
    lines.append("                raise SyntaxError(f'Syntax error at position {pos}, unexpected token {term}')")
    lines.append("            inst, arg = action")
    lines.append("            if inst == 'shift':")
    lines.append("                stack.append(arg)")
    lines.append("                pos += 1")
    lines.append("            elif inst == 'reduce':")
    lines.append("                lhs, rhs = cls.PRODUCTIONS[arg]")
    lines.append("                for _ in rhs:")
    lines.append("                    stack.pop()")
    lines.append("                state2 = stack[-1]")
    lines.append("                goto_state = cls.GOTO.get((state2, lhs))")
    lines.append("                if goto_state is None:")
    lines.append("                    raise SyntaxError(f'Missing GOTO for state {state2} and symbol {lhs}')")
    lines.append("                stack.append(goto_state)")
    lines.append("            elif inst == 'accept':")
    lines.append("                return")
    lines.append("            else:")
    lines.append("                raise SyntaxError(f'Invalid action {inst} in state {state}')")
    lines.append("")
    lines.append("def main():")
    lines.append("    \"\"\"Invoca el parser generado desde línea de comandos.\"\"\"")
    lines.append("    if len(sys.argv) != 2:")
    lines.append("        print(f'Usage: {sys.argv[0]} <input_file>')")
    lines.append("        sys.exit(1)")
    lines.append("    filename = sys.argv[1]")
    lines.append("    from src.runtime.parser_interface import LexerInterface")
    lines.append("    text = open(filename).read()")
    lines.append("    tokens = LexerInterface.tokenize(text)")
    lines.append("    Parser.parse(tokens)")
    lines.append("    print('Input parsed successfully.')")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    main()")

    content = "\n".join(lines) + "\n"
    # Escribir archivo generado
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
