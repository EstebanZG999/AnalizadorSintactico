#!/usr/bin/env python3
import sys
from lexer.thelexer import Lexer
from sintaxer.src.runtime.parser_interface import Parser
from sintaxer.src.runtime.error_reporting import format_error

def main():
    if len(sys.argv) != 2:
        print("Uso: run_all.py <archivo_fuente>")
        sys.exit(1)

    fuente = sys.argv[1]
    try:
        text = open(fuente, encoding="utf-8").read()
    except IOError as e:
        print(f"Error al leer '{fuente}': {e}")
        sys.exit(1)

    # 1. Léxico
    try:
        lexer = Lexer(text)
        tokens = lexer.get_tokens()
    except Exception as e:
        print("Error en el lexer:", e)
        sys.exit(1)

    print("→ Tokens generados:")
    for tok in tokens:
        print("   ", tok)

    # 2. Sintaxis
    parser = Parser()
    try:
        ast = parser.parse(tokens)
        print("\n✓ AST generado con éxito:")
        print(ast)
    except Exception as e:
        print("\n✗ Error en el parser:")
        print(format_error(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
