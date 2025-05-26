# src/models/yalex_parser.py

import re

class YALexParser:
    def __init__(self, filename):
        self.filename = filename
        self.header_code = ""
        self.trailer_code = ""
        self.definitions = {}  # guardará {ident: regex_string}
        self.rules = []        # lista de (regex_string, action_code)
        self.entrypoint = None # nombre de la regla principal, si lo usas

    def parse(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # eliminar comentarios estilo YALex y C:
        content = re.sub(r'\(\*.*?\*\)', '', content, flags=re.DOTALL)   # (* … *)
        content = re.sub(r'/\*.*?\*/',  '', content, flags=re.DOTALL)   # /* … */

        content = re.sub(r'\(\*.*?\*\)', '', content, flags=re.DOTALL)

        # 1. Extraer {header} (asumiendo que el header es el primer bloque entre { })
        header_match = re.search(r'^\s*\{(.*?)\}', content, re.DOTALL)
        if header_match:
            self.header_code = header_match.group(1).strip()
            content = content[header_match.end():]  # quitar el header

        # 2. Extraer definiciones de tipo "let IDENT = regex"
        for match in re.finditer(r'let\s+(\w+)\s*=\s*([^\n]+)', content):
            ident = match.group(1)
            regex_str = match.group(2).strip()
            self.definitions[ident] = regex_str

        # 3. Extraer la sección de reglas
        rule_match = re.search(r'rule\s+(\w+)(?:\s*\[.*?\])?\s*=\s*(.*)', content, re.DOTALL)
        if rule_match:
            self.entrypoint = rule_match.group(1).strip()
            rc = rule_match.group(2)
            n = len(rc)
            i = 0
            rules = []

            def _collect_one():
                nonlocal i
                # salto espacios
                while i < n and rc[i].isspace():
                    i += 1
                start = i
                in_lit = None
                # lee hasta '{' que abre la acción, ignorando literales
                while i < n:
                    c = rc[i]
                    if in_lit:
                        if c == in_lit and rc[i-1] != '\\':
                            in_lit = None
                    else:
                        if c in ('"', "'"):
                            in_lit = c
                        elif c == '{':
                            break
                    i += 1
                regex_part = rc[start:i].strip()

                # extraigo el bloque {…}
                brace = 0
                action_start = i
                while i < n:
                    c = rc[i]
                    if c == '{':
                        brace += 1
                    elif c == '}':
                        brace -= 1
                        if brace == 0:
                            i += 1
                            break
                    i += 1
                action_part = rc[action_start:i]
                # quita llaves exteriores y comentarios
                raw = action_part.strip()
                if raw.startswith('{') and raw.endswith('}'):
                    raw = raw[1:-1].strip()
                action_clean = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL).strip()
                if not action_clean:
                    action_clean = 'pass'
                return regex_part, action_clean

            # Primera alternativa (sin '|' al inicio)
            rules.append(_collect_one())
            # Resto de alternativas
            while i < n:
                if rc[i] != '|':
                    i += 1
                    continue
                i += 1
                rules.append(_collect_one())

            self.rules = rules

        # 4. Extraer {trailer} (si existe, asumimos que es el último bloque entre { } al final)
        trailer_match = re.search(r'\{(.*?)\}\s*$', content, re.DOTALL)
        if trailer_match:
            self.trailer_code = trailer_match.group(1).strip()


    def expand_definitions(self, regex_str):
        """
        Sustituye cada identificador por su definición hasta que
        no queden más nombres de definiciones en la cadena.
        """
        # Repetimos hasta que no haya ningún cambio
        while True:
            new_regex = regex_str
            for ident, definition in self.definitions.items():
                pattern = re.compile(r'\b' + re.escape(ident) + r'\b')
                new_regex = pattern.sub(lambda m: f"({definition})", new_regex)
            if new_regex == regex_str:
                break
            regex_str = new_regex
        return regex_str