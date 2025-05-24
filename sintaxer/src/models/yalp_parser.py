import re

class YalpParser:
    """
    Parser para archivos YAPar (.yalp).
    Extrae:
      - tokens (%token ...)
      - tokens a ignorar (IGNORE ...)
      - producciones (sección de gramática)
    """
    TOKEN_DECLARATION = re.compile(r'^%token\s+(?P<tokens>[A-Z0-9_ ]+)')
    IGNORE_DECLARATION = re.compile(r'^IGNORE\s+(?P<tokens>[A-Z0-9_ ]+)')
    RULE_START = re.compile(r'^(?P<lhs>[a-z][a-z0-9_]*)\s*:\s*(?P<rhs>.*)')
    PROD_SEPARATOR = re.compile(r'\|')
    PROD_END = re.compile(r';')

    def __init__(self):
        self.tokens = []            # lista de tokens (terminales)
        self.ignores = set()        # tokens a ignorar
        self.productions = {}       # {lhs: [ [symbols], ... ], ...}

    def parse_file(self, path: str):
        """Parsea todo el archivo .yalp"""
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        self._parse_sections(lines)

    def _parse_sections(self, lines):
        """Procesa líneas hasta '%%' para tokens e ignores, luego gramática"""
        section = 'tokens'
        buffer = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('/*'):
                continue
            if stripped == '%%':
                section = 'grammar'
                continue
            if section == 'tokens':
                self._parse_token_line(stripped)
            else:
                buffer.append(stripped)
        if section == 'grammar':
            self._parse_productions(buffer)

    def _parse_token_line(self, line: str):
        """Parsea una línea de tokens o ignores"""
        m = self.TOKEN_DECLARATION.match(line)
        if m:
            toks = m.group('tokens').split()
            self.tokens.extend(toks)
            return
        m = self.IGNORE_DECLARATION.match(line)
        if m:
            toks = m.group('tokens').split()
            self.ignores.update(toks)
            return

    def _parse_productions(self, lines):
        """Parsea producciones desde la sección de gramática"""
        current_lhs = None
        rhs_accum = ''
        for line in lines:
            # busca inicio de producción
            m = self.RULE_START.match(line)
            if m:
                current_lhs = m.group('lhs')
                rhs_accum = m.group('rhs')
                continue
            # en reglas continuadas, acumula
            if current_lhs and not self.PROD_END.search(line):
                rhs_accum += ' ' + line
                continue
            # fin de producción (';')
            if current_lhs and self.PROD_END.search(line):
                rhs_accum = rhs_accum.rstrip(';').strip()
                alternatives = self.PROD_SEPARATOR.split(rhs_accum)
                self.productions[current_lhs] = [alt.strip().split() for alt in alternatives]
                current_lhs = None
                rhs_accum = ''
                continue
