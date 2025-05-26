# src/controllers/main_controller.py

import os
import re
import contextlib, io
import textwrap
from src.models.regex_parser import RegexParser
from src.models.syntax_tree import SyntaxTree
from src.models.dfa import DFA
from src.models.yalex_parser import YALexParser
from src.models.mindfa import minimize_dfa


def generate_global_dfa():
    """
    Genera un DFA global a partir de la especificación en 'inputs/lexer.yal',
    asignando un marcador único a cada regla y combinándolas en una única expresión regular.
    """
    spec_filename = "inputs/lexer.yal"
    yalex_parser = YALexParser(spec_filename)
    yalex_parser.parse()
    
    global_rules = []
    marker_to_rule = {}
    
    special = {
        '#': r'\#',
        '.': r'\.',
        '{': r'\{',
        '}': r'\}',
    }

    for i, (regex_str, action_code) in enumerate(yalex_parser.rules):
        regex_clean = regex_str.lstrip("| ").strip()
        if not regex_clean:
            continue

        if regex_clean == "ws":
            # expandimos la definición y la metemos tal cual:
            expanded = yalex_parser.expand_definitions("ws").replace("\n", "").strip()
            # No la escapamos ni tocamos más, porque es algo como "(([' ' '\t'])+)"
            escaped = expanded
            # Y seguimos con el flujo normal de marcado…
        else:
            expanded = yalex_parser.expand_definitions(regex_clean).replace("\n", "").strip()

        # Depuración extra para ver qué estamos recibiendo
        print(f"[RAW   ] Regla {i+1}: regex_str={regex_str!r}, expanded={expanded!r}")

        # Caso A: literal entre comillas
        if expanded == "'":
            # un solo apóstrofo: lo representamos como carácter escapado \'
            escaped = r"\'"
            # print(f"[SPECIAL] Regla {i+1}: literal suelto {expanded!r} → escaped={escaped!r}")
        elif expanded == '"':
            # una sola comilla doble → \"
            escaped = r'\"'
            # print(f"[SPECIAL] Regla {i+1}: literal suelto {expanded!r} → escaped={escaped!r}")
            lit = expanded[1:-1]
            if lit == r"\n":
                escaped = r"\n"
            else:
                escaped = special.get(lit, re.escape(lit))

        # Caso B: cualquier carácter único no alfanumérico
        elif len(expanded) == 1 and not expanded.isalnum():
            escaped = special.get(expanded, re.escape(expanded))

        # Caso C: expresiones más complejas
        else:
            escaped = re.sub(r'"([^"]*)"', lambda m: re.escape(m.group(1)), expanded)
            escaped = re.sub(r"'([^']*)'", lambda m: re.escape(m.group(1)), escaped)

        # Vuelta de depuración para verificar
        # print(f"[ESCAPED] Regla {i+1}: escaped={escaped!r}")

        # Marcador y resto idéntico al tuyo…
        marker = chr(128 + i)
        marker_to_rule[marker] = {'order': i, 'action': action_code}
        '''
        # ——— DEPURACIÓN: tokenización del trozo completo ———
        debug_regex = escaped + "#"
        print(f"[DEBUG] Regla {i+1}: expresion a tokenizar → {debug_regex!r}")
        try:
            tokens = RegexParser(debug_regex).tokenize()
            print(f"[DEBUG] Tokens: {[str(t) for t in tokens]}")
        except ValueError as e:
            print(f"[ERROR] fallo tokenizando regla {i+1}: {e}")
            raise
        # ——— fin depuración ———
        '''
        global_rules.append(f"{escaped}{marker}")

    
    # Combina todas las expresiones en una única expresión global con alternancia
    global_regex = "|".join(f"({r})" for r in global_rules)
    print("Expresión global generada:", global_regex)
    
    
    # Remueve cualquier salto de línea que pueda quedar en la expresión global —> Comentado para no romper literales \n, \t dentro de []
    # global_regex = global_regex.replace("\n", "").replace("\r", "").strip()
    print("Expresión global generada (repr):", repr(global_regex))
    
    # Procesar la expresión global: tokenizar, convertir a postfix, construir árbol y DFA
    r_parser = RegexParser(global_regex)
    r_parser.tokenize()
    postfix = r_parser.to_postfix()
    syntax_tree = SyntaxTree(postfix)
    global_dfa = DFA(syntax_tree)
    
    # Asigna el mapeo de marcadores al DFA
    global_dfa.marker_to_rule = marker_to_rule
    # Crea una estructura para mapear cada ID de estado a su conjunto de posiciones
    global_dfa.state_sets = {state_id: state_set for state_set, state_id in global_dfa.states.items()}
    
    # Genera la imagen del DFA global en la carpeta 'imagenes' con Graphviz
    # global_dfa.render_dfa("global_dfa")
    
    return global_dfa


def generate_lexer():
    """
    Genera el archivo 'thelexer.py' a partir de la especificación YALex.
    Combina el header, la generación de DFAs para cada regla con su acción asociada y el trailer.
    """
    spec_filename = "inputs/lexer.yal"
    yalex_parser = YALexParser(spec_filename)
    yalex_parser.parse()
    print("Header extraído:")
    print(yalex_parser.header_code)
    print("\nDefiniciones encontradas:")
    for ident, definition in yalex_parser.definitions.items():
        print(f"  {ident} = {definition}")
    # print("\nReglas encontradas:")

    punct_map = {}
    for regex_str, action_code in yalex_parser.rules:
        lit = regex_str.strip().lstrip("| ").strip()
        if (lit.startswith("'") and lit.endswith("'")) or (lit.startswith('"') and lit.endswith('"')):
            char = lit[1:-1]
            # extraemos el nombre del token incluso si viene envuelto en paréntesis
            m = re.search(r"return\s*\(?\s*([A-Za-z_]\w*)", action_code)
            if m:
                punct_map[char] = m.group(1)
        
    rules = []
    for idx, (regex_str, action_code) in enumerate(yalex_parser.rules, start=1):
        # Limpieza de la regex: eliminar '|' inicial y espacios
        regex_str_clean = regex_str.lstrip("| ").strip()
        if not regex_str_clean:
            continue
        # 1) Expandir definiciones
        expanded_regex = yalex_parser.expand_definitions(regex_str_clean)
        # 2) Si la regla es exactamente un literal entre comillas,
        #    tratamos el salto de línea '\n' como un escape especial
        if (expanded_regex.startswith("'") and expanded_regex.endswith("'")) \
        or (expanded_regex.startswith('"') and expanded_regex.endswith('"')):
            lit = expanded_regex[1:-1]
            if lit == r"\n":
                # queremos un único backslash-n para que el parser lo convierta a '\n'
                escaped = r"\n"
            else:
                escaped = re.escape(lit)
            expanded_regex = escaped
        else:
            # Para literales incrustados, escapamos cada uno
            expanded_regex = re.sub(
                r'"([^"]*)"',
                lambda m: re.escape(m.group(1)),
                expanded_regex
            )
            expanded_regex = re.sub(
                r"'([^']*)'",
                lambda m: re.escape(m.group(1)),
                expanded_regex
            )
        # 3) Quitar saltos de línea (sin tocar espacios)
        expanded_regex = expanded_regex.replace("\n", "")
        # 4) Añadir centinela '#' al final
        expanded_regex_for_tree = expanded_regex + '#'
        '''
        # ——— DEPURACIÓN ———
        print(f"[DEBUG] Regla {idx}: expresión a tokenizar → {expanded_regex_for_tree!r}")
        r_parser = RegexParser(expanded_regex_for_tree)
        try:
            r_parser.tokenize()
        except ValueError as e:
            print(f"¡Error parseando la expresión expandida en la regla {idx}!")
            print(f"   expanded_regex_for_tree = {expanded_regex_for_tree!r}")
            # Re-lanzamos el mismo error para que se vea el stack trace
            raise
        # ——— fin depuración ———
        '''
        added_marker = False
        with contextlib.redirect_stdout(io.StringIO()):
            print(f"Regla {idx+1} expandida: {expanded_regex}")
        # Construir el DFA para la regla
        r_parser = RegexParser(expanded_regex_for_tree)
        r_parser.tokenize()
        postfix = r_parser.to_postfix()
        # (Debug opcional, envuelto en --verbose)
        """
        print(f"\n--- DEBUG Regla {idx+1} ---")
        print(" regex raw:     ", repr(expanded_regex))
        print(" tokens:        ", [str(t) for t in r_parser.tokens])
        print(" postfix:       ", [str(t) for t in postfix])
        """
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({
            'regex': expanded_regex,
            'action': action_code,
            'dfa': dfa,
            'order': idx,
            'added_marker': added_marker
        })
    
    output_filename = "thelexer.py"
    with open(output_filename, "w", encoding="utf-8") as f:
        # Escribir header (el código extraído del archivo YALex)
        f.write("# Código generado automáticamente por YALex\n")
        # 1) Import básico de regex
        f.write("import re\n")
        # 2) Import de todos los tokens DEFINIDO POR EL HEADER de la gramática
        header = "\n".join(line.lstrip() for line in yalex_parser.header_code.splitlines())
        if header:
            f.write(header + "\n\n")
        else:
            f.write("from src.runtime.token_types import *\n\n")
        # 3) definimos PUNCTUATIONS
        f.write("# Mapa de puntuaciones generado según las reglas de la gramática\n")
        f.write("PUNCTUATIONS = {\n")
        for ch, tok in punct_map.items():
            f.write(f"    {ch!r}: {tok},\n")
        f.write("}\n\n")

        # Definir la clase Lexer
        f.write("class Lexer:\n")
        f.write("    def __init__(self, input_text):\n")
        f.write("        self.input_text = input_text\n")
        f.write("        self.pos = 0\n")
        f.write("\n")
        f.write("    def get_tokens(self):\n")
        f.write("        tokens = []\n")
        f.write("        text = self.input_text\n")
        f.write("        pos = 0\n")
        f.write("        while pos < len(text):\n")
        # ——— Reconocimiento rápido de números científicos ———
        f.write("            m = re.match(r'\\d+\\.\\d+(?:[eE][+-]?\\d+)?', text[pos:])\n")
        f.write("            if m:\n")
        f.write("                lexeme = m.group(0)\n")
        f.write("                tokens.append((NUMBER, lexeme))\n")
        f.write("                print(f'⟶ Token: {NUMBER!r}, lexema: {lexeme!r}')\n")
        f.write("                pos += len(lexeme)\n")
        f.write("                continue\n")
        # Intentar, por cada regla, empatar el mayor prefijo
        f.write("            longest_match = 0\n")
        f.write("            selected_rule = None\n")
        f.write("            for rule in self.rules:\n")
        f.write("                ml = rule['dfa'].match_prefix(text[pos:])\n")
        f.write("                if ml > longest_match:\n")
        f.write("                    longest_match = ml\n")
        f.write("                    selected_rule = rule\n")
        f.write("            if longest_match > 1:\n")
        f.write("                lexeme = text[pos:pos+longest_match]\n")
        f.write("                action_code = selected_rule['action']\n")
        f.write("                local_env = {'lexeme': lexeme, 'text': text}\n")
        f.write("                exec(action_code.replace('return', 'token ='), globals(), local_env)\n")
        f.write("                tok = local_env.get('token')\n")
        f.write("                if tok is not None:\n")
        f.write("                    # si la acción ya devolvió (TOKEN, lexeme), lo usamos directamente\n")
        f.write("                    if isinstance(tok, tuple):\n")
        f.write("                        tokens.append(tok)\n")
        f.write("                    else:\n")
        f.write("                        tokens.append((tok, lexeme))\n")
        f.write("                    print(f'⟶ Token: {tok!r}, lexema: {lexeme!r}')\n")
        f.write("                pos += longest_match\n")
        f.write("                continue\n")
        # Si el DFA sólo empata 1 carácter (ej. ws de longitud 1, dígito suelto...)
        f.write("            if longest_match == 1:\n")
        f.write("                lexeme = text[pos]\n")
        f.write("                action_code = selected_rule['action']\n")
        f.write("                local_env = {'lexeme': lexeme, 'text': text}\n")
        f.write("                exec(action_code.replace('return', 'token ='), globals(), local_env)\n")
        f.write("                tok = local_env.get('token')\n")
        f.write("                if tok is not None:\n")
        f.write("                    # si la acción ya devolvió (TOKEN, lexeme), lo usamos directamente\n")
        f.write("                    if isinstance(tok, tuple):\n")
        f.write("                        tokens.append(tok)\n")
        f.write("                    else:\n")
        f.write("                        tokens.append((tok, lexeme))\n")
        f.write("                    print(f'⟶ Token: {tok!r}, lexema: {lexeme!r}')\n")
        f.write("                pos += 1\n")
        f.write("                continue\n")
        # Si no fue un token largo ni un match de un char vía DFA, símbolos puntuales
        f.write("            ch = text[pos]\n")
        f.write("            mapped = PUNCTUATIONS.get(ch)\n")
        f.write("            if mapped is not None:\n")
        f.write("                tokens.append((mapped, ch))\n")
        f.write("                print(f'⟶ Token: {mapped!r}, lexema: {ch!r}')\n")
        f.write("                pos += 1\n")
        f.write("                continue\n")
        # FALLÓ TODO: carácter no declarado → lo marcamos y seguimos
        f.write("            # Carácter no declarado en la gramática: lo marcamos como UNKNOWN y continuamos\n")
        f.write("            ch = text[pos]\n")
        f.write("            print(f\"⟶ Token no reconocido: {ch!r} en posición {pos}\")\n")
        f.write("            tokens.append((None, ch))  # None indica token no reconocido\n")
        f.write("            pos += 1\n")
        f.write("            continue\n")
        f.write("        tokens.append((EOF, ''))\n")
        f.write("        return tokens\n")
        f.write("\n")
        # Propiedad rules que reconstruye las reglas al momento de usar el lexer
        f.write("    @property\n")
        f.write("    def rules(self):\n")
        f.write("        rules = []\n")
        # Para cada regla, se genera el código que recrea el DFA (con la misma expresión expandida)
        for rule in rules:
            f.write("        from src.models.regex_parser import RegexParser\n")
            f.write("        from src.models.syntax_tree import SyntaxTree\n")
            f.write("        from src.models.dfa import DFA\n")
            f.write(f"        # Regla: {rule['regex']}\n")
            f.write(f"        parser = RegexParser({rule['regex']!r} + '#')\n")
            f.write("        parser.tokenize()\n")
            f.write("        postfix = parser.to_postfix()\n")
            f.write("        syntax_tree = SyntaxTree(postfix)\n")
            f.write("        dfa = DFA(syntax_tree)\n")
            f.write(f"        rules.append({{'regex': {rule['regex']!r}, 'action': {rule['action']!r}, 'dfa': dfa}})\n")
        f.write("        return rules\n")
        f.write("\n")
        
        # Escribir trailer (el código extraído del archivo YALex, si existe)
        # trailer = "\n".join(line.lstrip() for line in yalex_parser.trailer_code.splitlines())
        # f.write(trailer + "\n")
    
    print(f"\nAnalizador léxico generado y guardado en: {output_filename}")

if __name__ == "__main__":
    #extend_dfa_with_match_prefix()
    # test_full_pipeline("inputs/lexer.yal")
    
    # Ejecutar la generación del archivo final del analizador léxico
    generate_lexer()
    
    # run_app()