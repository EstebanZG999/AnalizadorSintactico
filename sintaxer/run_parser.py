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


def print_grammar(productions):
    print("\n=== Gramática extendida ===")
    for idx, (lhs, rhs_list) in enumerate(productions):
        rhss = [" ".join(rhs) for rhs in rhs_list]
        print(f"{idx}. {lhs} → {' | '.join(rhss)}")


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

def main():
    parser = argparse.ArgumentParser(
        description="Genera y muestra artefactos de un parser SLR(1) desde un archivo .yalp"
    )
    parser.add_argument("grammar_file")
    parser.add_argument("--show-grammar", action="store_true")
    parser.add_argument("--show-automaton", action="store_true")
    parser.add_argument("--show-tables", action="store_true")
    args = parser.parse_args()

    grammar_file = args.grammar_file

    # Mostrar y leer archivo
    print(f"--- Leyendo gramática desde: {os.path.abspath(grammar_file)} ---")
    with open(grammar_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            print(f"{i:3}: {line.rstrip()}")

    # Parsear la gramática
    yalp = YalpParser()
    yalp.parse_file(grammar_file)
    productions = yalp.productions
    if not productions:
        print("No se encontraron producciones")
        sys.exit(1)
    print("→ Producciones parseadas:", productions)

    # Determinar símbolo inicial *desde* las claves de productions
    start_symbol = next(iter(productions))  # p.ej. 's' en tu grammar
    # Extender gramática con S' → S
    productions_aug = {f"{start_symbol}'": [[start_symbol]], **productions}
    if args.show_grammar:
        print_grammar(list(productions_aug.items()))

    # FIRST / FOLLOW
    first = compute_first(productions_aug)
    follow = compute_follow(productions_aug, start_symbol, first)

    # Construir LR(0)
    states, transitions = build_states(productions, start_symbol)
    if args.show_automaton:
        print_automaton(states, transitions)

    # Tablas SLR(1)
    action, goto = construct_slr_table(states, transitions, productions_aug, follow)
    if args.show_tables:
        print_tables(action, goto)

    # DEBUG: volcar ACTION
    print("\n=== DEBUG: ACTION TABLE ===")
    for (st, sym), inst in sorted(action.items()):
        print(f"  (state={st!r}, sym={sym!r}) -> {inst!r}")
    print("============================\n")

    # Generar theparser.py
    output_path = os.path.join(os.path.dirname(__file__), "theparser.py")
    generate_parser_file(action, goto, productions, start_symbol, output_path)
    print(f"Parser generado exitosamente en: {output_path}")


if __name__ == "__main__":
    main()
