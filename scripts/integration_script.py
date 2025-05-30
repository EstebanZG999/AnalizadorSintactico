#!/usr/bin/env python3
import os
import sys

# 1) Añade la carpeta raíz del proyecto al PYTHONPATH dinámicamente
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# 2) Importar paquetes
from lexer.thelexer import Lexer
from sintaxer.theparser import Parser

def main():
    source = "TOKEN_1 TOKEN_2 TOKEN_3 TOKEN_4\n"

    # 1. Tokenización
    lexer = Lexer(source)
    raw_tokens = lexer.get_tokens()
    print("Raw tokens:", raw_tokens)

    # 2. Mapear y filtrar tokens
    terminals = {"TOKEN_1", "TOKEN_2", "TOKEN_3", "TOKEN_4"}
    tokens = []
    for tok_type, lex in raw_tokens:
        # Mapea IDs válidos a terminales
        if tok_type == "ID" and lex in terminals:
            tokens.append((lex, lex))
        # Ignora espacio, newline u otros IDs
        elif tok_type in ("EOL", "WS"):
            continue
        # Conserva EOF
        elif tok_type == "EOF":
            tokens.append((tok_type, lex))
        else:
            # Descarta cualquier otro
            continue

    print("Mapped tokens:", tokens)

    # 3. Parsing
    try:
        Parser.parse(tokens)
        print("✅ Integración OK: la cadena es válida.")
    except Exception as e:
        print("❌ Error en la integración:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
