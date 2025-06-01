# sintaxer/run_parser.py

import sys
import os
import argparse

# Aseguramos que el paquete sintaxer esté en el path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from sintaxer.src.models.yalp_parser import YalpParser
from sintaxer.src.models.grammar_analysis import compute_first, compute_follow
from sintaxer.src.models.lr0 import items as build_states
from sintaxer.src.models.slr_table import construct_slr_table
from sintaxer.src.generators.parser_generator import generate_parser_file


def print_grammar(prod_list):
    print("\n=== Gramática extendida ===")
    for idx, (lhs, rhs) in enumerate(prod_list):
        print(f"{idx}. {lhs} → {' '.join(rhs)}")


def print_first_follow(productions_aug, first, follow):
    print("\n=== Conjuntos FIRST y FOLLOW ===")
    for nt in productions_aug:
        # Omitir la producción aumentada (propia) si termina en "'"
        if nt.endswith("'"):
            continue
        fset = ", ".join(sorted(first.get(nt, [])))
        fol  = ", ".join(sorted(follow.get(nt, [])))
        print(f"FIRST({nt}) = {{ {fset} }}")
        print(f"FOLLOW({nt}) = {{ {fol} }}")


def print_automaton(states, transitions):
    print("\n=== Autómata LR(0) ===")
    for sid, state in enumerate(states):
        print(f"I{sid}:")
        # Intentar iterar items en State o en atributo 'items'
        state_items = None
        if hasattr(state, '__iter__'):
            state_items = state
        elif hasattr(state, 'items'):
            state_items = state.items
        else:
            state_items = [state]
        for item in state_items:
            print(f"  {format_item(item)}")
        for symbol, dest in transitions.get(sid, {}).items():
            print(f"  (I{sid}, {symbol!r}) → I{dest}")


def print_tables(action, goto):
    try:
        from tabulate import tabulate
    except ImportError:
        print("Instala 'tabulate' para mejor visualización de tablas.")
        return
    # Determinar alfabetos
    terminals = sorted({sym for (s, sym) in action.keys()})
    nonterms = sorted({nt for (s, nt) in goto.keys()})
    headers = ["Estado"] + terminals + nonterms
    max_state = max(
        max((s for (s, _) in action.keys()), default=0),
        max((s for (s, _) in goto.keys()), default=0)
    )
    table = []
    for s in range(max_state + 1):
        row = [s]
        for t in terminals:
            row.append(action.get((s, t), ""))
        for A in nonterms:
            row.append(goto.get((s, A), ""))
        table.append(row)
    print("\n=== Tabla SLR(1) (ACTION | GOTO) ===")
    print(tabulate(table, headers=headers, tablefmt="github"))
    

def format_item(item):
    # item.lhs  = 'Q'
    # item.rhs  = ('[', 'S', ']')
    # item.dot  = posición del punto
    parts = []
    for i, sym in enumerate(item.rhs):
        if i == item.dot:
            parts.append('·')
        parts.append(sym)
    # si el punto va al final
    if item.dot == len(item.rhs):
        parts.append('·')
    return f"{item.lhs} → {' '.join(parts)}"


def build_parser_artifacts(
    grammar_file: str,
    show_grammar: bool,
    show_first_follow: bool,
    show_automaton: bool,
    show_tables: bool,
    show_parse: bool
):
    """
    1. Parsea la gramática YAPar (.yalp)
    2. Extiende con S' → start_symbol
    3. Calcula FIRST / FOLLOW
    4. Construye LR(0) (states, transitions)
    5. Construye tablas ACTION y GOTO
    6. Si los flags están activos, imprime gramática, FIRST/FOLLOW, autómata y tablas.
    7. Devuelve un dict con action, goto, productions_aug_list, start_symbol, etc.
    """

    # 1) Leer e imprimir archivo .yalp
    print(f"--- Leyendo gramática desde: {os.path.abspath(grammar_file)} ---")
    with open(grammar_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            print(f"{i:3}: {line.rstrip()}")

    # 2) Parsear la gramática en objetos internos
    yalp = YalpParser()
    yalp.parse_file(grammar_file)
    productions = yalp.productions
    if not productions:
        print("No se encontraron producciones en la gramática.")
        sys.exit(1)

    # 3) Determinar símbolo inicial (e.g., 'S')
    start_symbol = next(iter(productions.keys()))

    # 4) Construir gramática aumentada: S' → S
    productions_aug = { f"{start_symbol}'": [[start_symbol]] }
    for lhs, rhss in productions.items():
        productions_aug[lhs] = rhss

    # 5) Si piden, imprimir la gramática extendida
    # Para imprimirla numéricamente, necesitamos una lista indexada [ (lhs, [rhs1,rhs2,…]), … ]
    # Pero print_grammar recibe exactamente esa forma, así que:
    if show_grammar:
        # Aplanamos productions_aug en [(lhs, rhs), …] para que print_grammar funcione correctamente
        flat = [(lhs, rhs) for lhs, rhss in productions_aug.items() for rhs in rhss]
        print_grammar(flat)

    # 6) Calcular FIRST y FOLLOW
    first  = compute_first(productions_aug)
    follow = compute_follow(productions_aug, start_symbol, first)
    if show_first_follow:
        print_first_follow(productions_aug, first, follow)

    # 7) Construir autómata LR(0)
    states, transitions = build_states(productions_aug, start_symbol)
    if show_automaton:
        print_automaton(states, transitions)

    # 8) Construir tablas SLR(1): action y goto
    action, goto = construct_slr_table(states, transitions, productions_aug, follow)
    if show_tables:
        print_tables(action, goto)

    # 9) Generar de inmediato theparser.py con la tabla recién calculada
    #     Para ello necesitamos:
    #      - action
    #      - goto
    #      - productions_aug_list
    #      - start_symbol
    #     Calculamos productions_aug_list de forma idéntica a como lo usará el parser.
    productions_aug_list = [
        (lhs, rhs)
        for lhs, rhss in productions_aug.items()
        for rhs in rhss
    ]
    #   output_path = carpeta/sintaxer/theparser.py
    output_path = os.path.join(os.path.dirname(__file__), "theparser.py")
    generate_parser_file(
        action,
        goto,
        productions_aug_list,
        start_symbol,
        output_path
    )
    # Generar theparser.py en sintaxer/theparser.py
    print(f"\nParser generado exitosamente en: {output_path}")

    # 10) Preparar lista indexada de producciones, en el MISMO orden que usó construct_slr_table
    return {
        "productions": productions,
        "action": action,
        "goto": goto,
        "productions_aug_list": productions_aug_list,
        "start_symbol": start_symbol,
        "states": states,
        "transitions": transitions,
        "first": first,
        "follow": follow
    }

def main():
    parser = argparse.ArgumentParser(
        description="Genera artefactos de un parser SLR(1) desde un archivo .yalp"
    )
    parser.add_argument("grammar_file", help="Ruta al archivo YAPar (.yalp) con la gramática")
    parser.add_argument("--show-grammar",      action="store_true", help="Muestra gramática extendida numerada")
    parser.add_argument("--show-first-follow", action="store_true", help="Muestra FIRST y FOLLOW")
    parser.add_argument("--show-automaton",    action="store_true", help="Muestra el autómata LR(0)")
    parser.add_argument("--show-tables",       action="store_true", help="Muestra tablas ACTION y GOTO")
    parser.add_argument("--show-parse",        action="store_true", help="Muestra traza de parseo genérico (ejemplo)")

    args = parser.parse_args()
    # Simplemente invocamos build_parser_artifacts para imprimir por pantalla
    build_parser_artifacts(
        args.grammar_file,
        args.show_grammar,
        args.show_first_follow,
        args.show_automaton,
        args.show_tables,
        args.show_parse
    )

    '''
    # Mostrar y leer archivo
    print(f"--- Leyendo gramática desde: {os.path.abspath(grammar_file)} ---")
    with open(grammar_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            print(f"{i:3}: {line.rstrip()}")

    # DEBUG: volcar ACTION
    print("\n=== DEBUG: ACTION TABLE ===")
    for (st, sym), inst in sorted(action.items()):
        print(f"  (state={st!r}, sym={sym!r}) -> {inst!r}")
    print("============================\n")
    '''

if __name__ == "__main__":
    main()