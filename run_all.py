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
def regenerate_parser(
    grammar_file,
    show_grammar,
    show_first_follow,
    show_automaton,
    show_tables,
    show_parse
):
    run_parser_path = os.path.join(project_root, "sintaxer", "run_parser.py")
    if not os.path.isfile(run_parser_path):
        print(f"Error: no encontré run_parser.py en {run_parser_path}")
        sys.exit(1)

    # Importamos run_parser.py como módulo
    parser_mod = import_module_from_file("run_parser", run_parser_path)

    # Llamamos a la función que devolvía todos los artefactos
    artifacts = parser_mod.build_parser_artifacts(
        grammar_file,
        show_grammar      = show_grammar,
        show_first_follow = show_first_follow,
        show_automaton    = show_automaton,
        show_tables       = show_tables,
        show_parse        = show_parse
    )

    print("   Parser regenerado correctamente.\n")
    return artifacts
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
        lexer = Lexer(source_code)
        token_tuples = lexer.get_tokens()
    except Exception:
        print("[Lexical Error]")
        traceback.print_exc()
        sys.exit(2)

    print("\n[DEBUG-LEXER] Tokens generados por el lexer (incluye WS/EOF):")
    for idx, (ttype, lexeme) in enumerate(token_tuples):
        print(f"  {idx:3}: (\"{ttype}\", \"{lexeme}\")")
    print("[/DEBUG-LEXER]\n")

    # Filtrar tokens IGNORE (por ejemplo, WS)
    filtered = [(t, l) for (t, l) in token_tuples if t != "WS"]
    print(f"   Tokens filtrados ({len(filtered)}): {filtered}\n")
    return filtered


# ------------------------------------------------------------------
# 4) Traza genérica shift/reduce usando los artefactos del parser
# ------------------------------------------------------------------
def trace_parse(token_types, action, goto, productions_aug_list):
    """
    token_types: lista de strings, p. ej. ["ID", "PLUS", "ID", "SEMICOLON", "$"]
    action:       { (estado, terminal) → ("shift", j) / ("reduce", idx) / ("accept", None) }
    goto:         { (estado, no_terminal) → estado_destino }
    productions_aug_list: [
         (lhs, rhs_list),   # índice 0,  S' → [S]
         (lhs, rhs_list),   # índice 1,  S  → S ∧ P
         ...
    ]
    """
    try:
        from tabulate import tabulate
    except ImportError:
        print("Instala 'tabulate' para visualizar la traza de parseo.")
        return

    print("\n=== Traza de parseo (Shift/Reduce) ===")
    headers = ["Paso", "Pila", "Lectura", "Acción"]
    rows = []
    stack = [0]
    pos = 0
    step = 1

    # Añadir "$" al final si no está
    if not token_types or token_types[-1] != "$":
        token_types = token_types + ["$"]

    # Detectar estado de aceptación para comparar con inst[0] == "accept"
    accept_state = None
    for (st, sym), inst in action.items():
        if sym == "$" and inst == ("accept", None):
            accept_state = st
            break

    while True:
        cur_state = stack[-1]
        cur_token = token_types[pos]

        # Caso “accept”:
        if cur_state == accept_state and cur_token == "$":
            rows.append([step, list(stack), " ".join(token_types[pos:]), "accept"])
            break

        inst = action.get((cur_state, cur_token))
        if not inst:
            # No hay acción definida: abrimos la traza con error
            rows.append([
                step,
                list(stack),
                " ".join(token_types[pos:]),
                f"ERROR: no action para estado {cur_state} y token '{cur_token}'"
            ])
            break

        kind, arg = inst
        if kind == "shift":
            rows.append([step, list(stack), " ".join(token_types[pos:]), f"shift → {arg}"])
            stack.append(arg)
            pos += 1

        elif kind == "reduce":
            # Recuperar (lhs, rhs) de productions_aug_list[arg]
            lhs, rhs = productions_aug_list[arg]
            rows.append([step, list(stack), " ".join(token_types[pos:]), f"reduce {lhs} → {' '.join(rhs)}"])
            # Desapilar |rhs| elementos
            for _ in rhs:
                stack.pop()

            top = stack[-1]
            next_state = goto.get((top, lhs))
            if next_state is None:
                rows.append([step, list(stack), " ".join(token_types[pos:]), f"ERROR: no GOTO para ({top}, {lhs})"])
                break
            stack.append(next_state)

        else:  # "accept"
            rows.append([step, list(stack), " ".join(token_types[pos:]), "accept"])
            break

        step += 1

    # Imprimir la traza completa
    print(tabulate(rows, headers, tablefmt="github"))
    print()

# ------------------------------------------------------------------
# 5) Parsear la lista de tokens usando sintaxer/theparser.py
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
# 6) Flujo principal: combina todo
# ------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Flujo completo: regenera lexer&parser, tokeniza, traza y parsea."
    )
    parser.add_argument("grammar_file", help="Ruta al archivo YAPar (.yalp)")
    parser.add_argument("source_file",  help="Ruta al archivo fuente a procesar")
    parser.add_argument("--show-grammar",      action="store_true", help="Muestra gramática extendida")
    parser.add_argument("--show-first-follow", action="store_true", help="Muestra FIRST/FOLLOW")
    parser.add_argument("--show-automaton",    action="store_true", help="Muestra autómata LR(0)")
    parser.add_argument("--show-tables",       action="store_true", help="Muestra ACTION/GOTO")
    parser.add_argument("--show-parse",        action="store_true", help="Muestra traza shift/reduce")

    args = parser.parse_args()
    grammar_file = args.grammar_file
    source_file  = args.source_file

    if not os.path.isfile(grammar_file):
        print(f"Error: no existe el archivo de gramática {grammar_file}")
        sys.exit(1)
    if not os.path.isfile(source_file):
        print(f"Error: no existe el archivo fuente {source_file}")
        sys.exit(1)

    # 1) Regenerar lexer
    regenerate_lexer()

    # 2) Regenerar parser *en memoria*, obteniendo artefactos
    artifacts = regenerate_parser(
        grammar_file,
            show_grammar      = args.show_grammar,
            show_first_follow = args.show_first_follow,
            show_automaton    = args.show_automaton,
            show_tables       = args.show_tables,
            show_parse        = args.show_parse
    )
    action             = artifacts["action"]
    goto               = artifacts["goto"]
    productions_aug_list = artifacts["productions_aug_list"]

    # 3) Tokenizar el código fuente
    token_list = tokenize_source(source_file)

    # 4) Si piden traza, generarla con los tokens obtenidos
    if args.show_parse:
        token_types = [tipo for (tipo, _) in token_list]
        trace_parse(token_types, action, goto, productions_aug_list)

    # 5) Parseo definitivo
    parse_tokens(token_list)

if __name__ == "__main__":
    main()
