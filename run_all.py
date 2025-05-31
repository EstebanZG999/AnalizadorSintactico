# run_all.py

import sys
import os
import argparse
import traceback
import importlib.util

# ------------------------------------------------------------------
# Ajustar ruta para que Python encuentre los paquetes “lexer” y “sintaxer”
# ------------------------------------------------------------------
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# ------------------------------------------------------------------
# Función de ayuda para importar módulos desde una ruta .py
# ------------------------------------------------------------------
def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ------------------------------------------------------------------
# 1) Regenerar el lexer (ejecuta lexer/run_lexer.py)
# ------------------------------------------------------------------
def regenerate_lexer():
    # Ruta al script run_lexer.py
    run_lexer_path = os.path.join(project_root, "lexer", "run_lexer.py")
    if not os.path.isfile(run_lexer_path):
        print(f"Error: no encontré run_lexer.py en {run_lexer_path}")
        sys.exit(1)

    print("→ Regenerando lexer…")
    # Cambiamos el cd para entrar en la carpeta lexer/ antes de invocar run_lexer.py
    lexer_dir = os.path.join(project_root, "lexer")
    exit_code = os.system(f"cd \"{lexer_dir}\" && python3 run_lexer.py")
    if exit_code != 0:
        print(f"Error al regenerar el lexer (exit code {exit_code}).")
        sys.exit(1)
    print("   Lexer regenerado correctamente.\n")

# ------------------------------------------------------------------
# 2) Regenerar el parser (ejecuta sintaxer/run_parser.py con flags)
# ------------------------------------------------------------------
def regenerate_parser(grammar_file, show_grammar, show_first_follow, show_automaton, show_tables, show_parse):
    run_parser_path = os.path.join(project_root, "sintaxer", "run_parser.py")
    if not os.path.isfile(run_parser_path):
        print(f"Error: no encontré run_parser.py en {run_parser_path}")
        sys.exit(1)

    cmd = f"python3 \"{run_parser_path}\" \"{grammar_file}\""
    if show_grammar:
        cmd += " --show-grammar"
    if show_first_follow:
        cmd += " --show-first-follow"
    if show_automaton:
        cmd += " --show-automaton"
    if show_tables:
        cmd += " --show-tables"
    if show_parse:
        cmd += " --show-parse"

    print("→ Regenerando parser con comando:")
    print("   " + cmd)
    exit_code = os.system(cmd)
    if exit_code != 0:
        print(f"Error al regenerar el parser (exit code {exit_code}).")
        sys.exit(1)
    print("   Parser regenerado correctamente.\n")

# ------------------------------------------------------------------
# 3) Tokenizar el archivo fuente usando lexer/thelexer.py
# ------------------------------------------------------------------
def tokenize_source(source_path):
    thelexer_path = os.path.join(project_root, "lexer", "thelexer.py")
    if not os.path.isfile(thelexer_path):
        print(f"Error: no encontré thelexer.py en {thelexer_path}")
        sys.exit(1)

    lexer_mod = import_module_from_file("thelexer", thelexer_path)
    if not hasattr(lexer_mod, "Lexer"):
        print("Error: thelexer.py no define la clase Lexer")
        sys.exit(1)
    Lexer = lexer_mod.Lexer

    with open(source_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    print(f"→ Tokenizando el archivo fuente: {source_path}")
    try:
        # asumimos que Lexer constructor
        # recibe sólo el texto (no ya la lista de tokens) y luego get_tokens() devuelve
        # una lista de tuplas (token_type, lexema).
        lexer = Lexer(source_code)
        token_tuples = lexer.get_tokens()
    except Exception as e:
        print("[Lexical Error]")
        traceback.print_exc()
        sys.exit(2)

    print("\n[DEBUG-LEXER] Tokens generados por el lexer (incluye WS/EOF):")
    for idx, (ttype, lexeme) in enumerate(token_tuples):
        print(f"  {idx:3}: (\"{ttype}\", \"{lexeme}\")")
    print("[/DEBUG-LEXER]\n")

    # Filtrar tokens IGNORE (p.ej. WS) si los produce el lexer
    filtered = []
    for ttype, lexeme in token_tuples:
        if ttype == "WS":
            continue
        filtered.append((ttype, lexeme))

    print(f"   Tokens obtenidos ({len(filtered)}): {filtered}\n")
    return filtered

# ------------------------------------------------------------------
# 4) Parsear la lista de tokens usando sintaxer/theparser.py
# ------------------------------------------------------------------
def parse_tokens(token_tuples):
    """
    Carga el módulo ‘theparser.py’ y usa Parser.parse() sobre la lista de tuplas (token_type, lexema).
    """
    theparser_path = os.path.join(project_root, "sintaxer", "theparser.py")
    if not os.path.isfile(theparser_path):
        print(f"Error: no encontré theparser.py en {theparser_path}")
        sys.exit(1)

    parser_mod = import_module_from_file("theparser", theparser_path)
    if not hasattr(parser_mod, "Parser"):
        print("Error: theparser.py no define la clase Parser")
        sys.exit(1)
    Parser = parser_mod.Parser

    # Asegurarnos de terminar con ("EOF", "")
    if not token_tuples or token_tuples[-1][0] != "EOF":
        token_tuples.append(("EOF", ""))

    print("→ Iniciando análisis sintáctico con Parser.parse()")
    try:
        # NOTA: Aquí pasamos la lista de tuplas (term, lexema) directamente
        Parser.parse(token_tuples)
    except Exception as e:
        print("[Syntax Error]")
        traceback.print_exc()
        sys.exit(3)

    print("   ¡Parseo correcto! El archivo fuente cumple la gramática.\n")

# ------------------------------------------------------------------
# 5) Flujo principal: combina todo
# ------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Flujo completo: regenera lexer&parser, tokeniza y parsea el código fuente."
    )
    parser.add_argument("grammar_file",
                        help="Ruta al archivo YAPar (.yalp) con la gramática")
    parser.add_argument("source_file",
                        help="Ruta al archivo fuente a compilar (por ejemplo, .txt o .src)")
    parser.add_argument("--show-grammar", action="store_true",
                        help="Muestra la gramática extendida")
    parser.add_argument("--show-first-follow", action="store_true",
                        help="Muestra los conjuntos FIRST y FOLLOW")
    parser.add_argument("--show-automaton", action="store_true",
                        help="Muestra el autómata LR(0)")
    parser.add_argument("--show-tables", action="store_true",
                        help="Muestra las tablas ACTION | GOTO")
    parser.add_argument("--show-parse", action="store_true",
                        help="Muestra la traza de parseo de ejemplo")

    args = parser.parse_args()
    grammar_file = args.grammar_file
    source_file  = args.source_file

    if not os.path.isfile(grammar_file):
        print(f"Error: no existe el archivo de gramática {grammar_file}")
        sys.exit(1)
    if not os.path.isfile(source_file):
        print(f"Error: no existe el archivo fuente {source_file}")
        sys.exit(1)

    # 1) Regenerar el lexer
    regenerate_lexer()

    # 2) Regenerar el parser con las opciones deseadas
    regenerate_parser(
        grammar_file,
        show_grammar      = args.show_grammar,
        show_first_follow = args.show_first_follow,
        show_automaton    = args.show_automaton,
        show_tables       = args.show_tables,
        show_parse        = args.show_parse
    )

    # 3) Tokenizar el código fuente
    token_list = tokenize_source(source_file)

    # 4) Parsear la lista de tokens
    parse_tokens(token_list)

if __name__ == "__main__":
    main()
