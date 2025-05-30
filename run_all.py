# run_all.py

import sys
import os

from lexer.thelexer import Lexer
from sintaxer.theparser import Parser  

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <source_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    try:
        text = open(source_file, encoding="utf-8").read()
    except OSError as e:
        print(f"[IO Error] Cannot read '{source_file}': {e}")
        sys.exit(1)

    # 1) Análisis léxico
    try:
        lexer  = Lexer(text)
        tokens = lexer.get_tokens()
    except Exception as e:
        print(f"[Lexical Error] {e}")
        sys.exit(2)

    # 2) Análisis sintáctico
    try:
        Parser.parse(tokens)
        print("Parsing completed successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"[Syntax Error] {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
