#!/usr/bin/env python3
import sys
import os

# Aseguramos que el paquete sintaxer esté en el path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from sintaxer.src.models.yalp_parser import YalpParser
from sintaxer.src.models.grammar_analysis import compute_first, compute_follow
from sintaxer.src.models.lr0 import items as build_states
from sintaxer.src.models.slr_table import construct_slr_table
from sintaxer.src.generators.parser_generator import generate_parser_file

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <grammar_file.yalp>")
        sys.exit(1)

    grammar_file = sys.argv[1]
    # Debug: mostrar el fichero
    print(f"--- Leyendo gramática desde: {os.path.abspath(grammar_file)} ---")
    with open(grammar_file, 'r', encoding='utf-8') as f:
        for i, l in enumerate(f, 1):
            print(f"{i:3}: {l.rstrip()}")

    # 1) Parsear la gramática
    yalp = YalpParser()
    yalp.parse_file(grammar_file)
    productions = yalp.productions
    print("→ Producciones parseadas:", productions)
    if not productions:
        print("No productions found")
        sys.exit(1)

    # 2) Preparamos la producción aumentada
    start_symbol = next(iter(productions))
    augmented_start = f"{start_symbol}'"
    # productions_aug incluye la producción aumentada S' -> S
    productions_aug = {augmented_start: [[start_symbol]], **productions}

    # 3) Calcular FIRST y FOLLOW sobre productions_aug
    first = compute_first(productions_aug)
    follow = compute_follow(productions_aug, start_symbol, first)

    # 4) Construir estados LR(0)
    states, transitions = build_states(productions, start_symbol)

    # 5) Construir tablas SLR(1) con productions_aug (para detectar accept)
    action, goto = construct_slr_table(states, transitions, productions_aug, follow)

    # 6) Generar theparser.py usando solo productions originales
    base_dir = os.path.dirname(__file__)
    output_path = os.path.join(base_dir, "theparser.py")
    generate_parser_file(action, goto, productions, start_symbol, output_path)
    print(f"Parser generado exitosamente en: {output_path}")

if __name__ == "__main__":
    main()