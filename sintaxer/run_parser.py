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

def main():
    parser = argparse.ArgumentParser(
        description="Genera y muestra artefactos de un parser SLR(1) desde un archivo .yalp"
    )
    parser.add_argument("grammar_file", help="Ruta al archivo YAPar (.yalp) con la gramática")
    parser.add_argument("--show-grammar", action="store_true", help="Muestra la gramática extendida numerada")
    parser.add_argument("--show-first-follow", action="store_true", help="Muestra los conjuntos FIRST y FOLLOW")
    parser.add_argument("--show-automaton", action="store_true", help="Muestra el autómata LR(0) completo")
    parser.add_argument("--show-tables", action="store_true", help="Muestra las tablas ACTION y GOTO")
    parser.add_argument("--show-parse", action="store_true", help="Muestra la traza de parseo")
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
    if args.show_first_follow:
        print_first_follow(productions_aug, first, follow)

    # Construir LR(0)
    states, transitions = build_states(productions, start_symbol)
    if args.show_automaton:
        print_automaton(states, transitions)

    # Tablas SLR(1)
    action, goto = construct_slr_table(states, transitions, productions_aug, follow)
    if args.show_tables:
        print_tables(action, goto)
    
    if args.show_parse:
        print("\n=== Traza de parseo de ejemplo ===")
        # Para arithmetic.yalp, la cadena de ejemplo es: 1 + 2 ;
        # Los tokens relevantes (solo tipos) serán:
        sample = ["NUMBER", "PLUS", "NUMBER", "SEMICOLON", "$"]
        stack = [0]
        idx = 0
        print(f"Pila\t| Lectura\t\t| Acción")
        while True:
            st = stack[-1]
            tok = sample[idx]
            inst = action.get((st, tok))
            if not inst:
                print(f"Error en estado {st} con token {tok!r}")
                break

            if inst[0] == "shift":
                # Mostramos el estado actual de la pila, la lectura restante
                print(f"{stack}\t| {' '.join(sample[idx:])}\t| shift → estado {inst[1]}")
                stack.append(inst[1])
                idx += 1

            elif inst[0] == "reduce":
                # inst[1] es el índice de la producción en productions_aug
                prod_items = list(productions_aug.items())
                lhs, rhs_list = prod_items[inst[1]]
                # Asumimos que cada producción en productions_aug tiene exactamente una RHS
                rhs = rhs_list[0]

                # Al reducir, desapilamos tantos símbolos como long(rhss)
                for _ in range(len(rhs)):
                    stack.pop()

                st2 = stack[-1]                  # Estado anterior tras desapilar
                dest = goto.get((st2, lhs))      # GOTO(estado anterior, lhs)
                stack.append(dest)

                # Imprimimos la acción reduce
                print(f"{stack}\t| {' '.join(sample[idx:])}\t| reduce {lhs} → {' '.join(rhs)}")

            else:  # accept
                print(f"{stack}\t| {' '.join(sample[idx:])}\t| accept")
                break

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
