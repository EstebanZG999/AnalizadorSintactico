# src/models/regex_parser.py

import re
from collections import deque

class Symbol:
    def __init__(self, value, is_operator=False):
        self.value = value
        self.is_operator = is_operator

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value 

class RegexParser:
    OPERATORS  = {'|', '*', '+', '?'}
    PRECEDENCE = {'|': 1, '.': 2, '*': 3, '+': 3, '?': 3}

    def __init__(self, regex):
        self.regex = regex
        self.tokens = []
    
    def should_concat(self, last_token, current_token_type):
        """
        Decide si se debe insertar un operador de concatenación antes de agregar un token
        """
        if last_token is None:
            return False
        if last_token.is_operator:
            if last_token.value not in {')', '*', '+', '?'}:
                return False
        # Si el token actual es literal o el inicio de un grupo, se concatena.
        if current_token_type in ['literal', 'group_start']:
            return True
        return False

    def expand_range(self, c1, c2):
        """
        Retorna la lista de caracteres que van desde c1..c2.
        """
        start = ord(c1)
        end = ord(c2)
        if start > end:
            start, end = end, start
        
        expanded = []
        for code in range(start, end + 1):
            expanded.append(chr(code))
        return expanded
    
    def parse_bracket_expression(self, bracket_content):
        """
        Dado el contenido dentro de [ ], genera una lista de tokens equivalente.
        Primero limpiamos las comillas y espacios para quedarnos solo con los
        caracteres puros (sin ' ni " ni espacios), luego expandimos rangos X–Y
        solo cuando ambos sean alfanuméricos.
        """
        # 1) Primero, decodificamos cualquier \n, \t, \\uXXXX, etc.
        decoded = bytes(bracket_content, "utf-8").decode("unicode_escape")
        # 2) Ahora removemos las comillas simples o dobles y espacios sobrantes
        clean = decoded.replace("'", "").replace('"', "")
        
        # 3) Recogemos cada carácter literal o rango a–b
        chars = []
        i = 0
        while i < len(clean):
            c = clean[i]
            # caso rango: a-b
            if i + 2 < len(clean) and clean[i+1] == "-" and clean[i].isalnum() and clean[i+2].isalnum():
                a, b = clean[i], clean[i+2]
                start, end = ord(a), ord(b)
                if start > end: start, end = end, start
                for code in range(start, end+1):
                    chars.append(chr(code))
                i += 3
            else:
                # carácter suelto
                chars.append(c)
                i += 1
        
        # 4) Eliminamos duplicados y ordenamos
        unique = []
        for c in chars:
            if c not in unique:
                unique.append(c)
        
        # Si la clase tiene solo un símbolo, lo devolvemos como literal
        if len(unique) == 1:
            return [ Symbol(unique[0], is_operator=False) ]

        # 5) Convertimos a tokens: ( c1 | c2 | ... cn )
        tokens = [Symbol("(", is_operator=True)]
        for idx, c in enumerate(unique):
            tokens.append(Symbol(c, is_operator=False))
            if idx < len(unique)-1:
                tokens.append(Symbol("|", is_operator=True))
        tokens.append(Symbol(")", is_operator=True))
        return tokens


    
    def tokenize(self):
        """
        Convierte la expresión regular en una lista de tokens, insertando concatenaciones explícitas.
        Se utiliza enumerate para saber cuándo es el último carácter (por ejemplo, para el '#' final).
        """
        output = []
        last_token = None 
        escaped = False

        skip_until = -1
        
        for i, char in enumerate(self.regex):
            if i < skip_until:
                continue
            if escaped: # Si el carácter está escapado, lo tratamos como literal.
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                escaped = False
                continue

            if char == '.':
                # si hacía falta concatenar, inyectamos explicitamente CONCAT (el “punto” interno)
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                # ahora metemos el '.' como literal comodín
                token = Symbol('.', is_operator=False)
                output.append(token)
                last_token = token
                continue

            elif char == '\\':
                # si hay un carácter tras la barra, lo consumimos como escape
                if i + 1 < len(self.regex):
                    esc_char = self.regex[i+1]
                    token_value = bytes(f"\\{esc_char}", "utf-8").decode("unicode_escape")
                    if self.should_concat(last_token, 'literal'):
                        output.append(Symbol('.', is_operator=True))
                    token = Symbol(token_value, is_operator=False)
                    output.append(token)
                    last_token = token
                    # avanzamos un paso extra para saltarnos el carácter escapado
                    skip_until = i + 2
                    continue
                else:
                    raise ValueError("Escape final sin carácter tras '\\'.")

            # Detectar '['
            elif char == '[':
                # Buscar la posición del ']' correspondiente
                j = i + 1
                found_closing = False
                while j < len(self.regex):
                    if self.regex[j] == ']':
                        found_closing = True
                        break
                    j += 1
                if not found_closing:
                    raise ValueError("Falta ']' de cierre en la expresión regular.")
                
                raw = self.regex[i+1 : j]
                # decodifica '\n', '\t', '\u1234', etc.
                bracket_content = bytes(raw, "utf-8").decode("unicode_escape")
                
                # Expandimos a un grupo de tokens
                bracket_tokens = self.parse_bracket_expression(bracket_content)
            
                # Verificamos si hace falta concatenar
                if self.should_concat(last_token, 'group_start'):
                    output.append(Symbol('.', is_operator=True))
                
                output.extend(bracket_tokens)
                last_token = bracket_tokens[-1] if bracket_tokens else None

                skip_until = j + 1
                continue

            elif char == "'" or char == '"':
                # Procesar literal entre comillas.
                quote_char = char
                literal = ""
                j = i + 1
                while j < len(self.regex) and self.regex[j] != quote_char:
                    literal += self.regex[j]
                    j += 1
                if j >= len(self.regex):
                    raise ValueError("No se encontró la comilla de cierre para literal.")
                # Actualizamos 'skip_until' para saltar el literal entero
                skip_until = j + 1
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                literal = bytes(literal, "utf-8").decode("unicode_escape")
                token = Symbol(literal, is_operator=False)
                output.append(token)
                last_token = token
                continue

            # (bloque de corchetes, literales entre comillas, alfanuméricos, operadores y paréntesis)
            # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            elif char.isalnum() or char in {'#', '$'}:
                # Igual que antes
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                continue

            elif char in self.OPERATORS:
                token = Symbol(char, is_operator=True)
                output.append(token)
                last_token = None if char == '|' else token
                continue

            elif char == '(':
                if self.should_concat(last_token, 'group_start'):
                    output.append(Symbol('.', is_operator=True))
                output.append(Symbol('(', is_operator=True))
                last_token = None
                continue

            elif char == ')':
                output.append(Symbol(')', is_operator=True))
                last_token = Symbol(')', is_operator=True)
                continue

            # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            # tratar cualquier otro carácter (ej. ':', ';', '<', '=', etc.) como literal
            elif char not in self.OPERATORS \
                 and char not in {'(',')','[',']','{','}','|'} \
                 and not char.isspace():
                # puntos, comas, dos puntos, etc.
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                continue

            # Ignorar espacios
            if char.isspace():
                continue

            # Si nada hizo `continue` antes, es un caracter inválido
            raise ValueError(f"Carácter no reconocido: {char}")

        if escaped:
            raise ValueError("Secuencia de escape incompleta en la expresión regular.")

        self.tokens = output
        return output
    
    def to_postfix(self):
        output = []
        stack = deque()
        
        for token in self.tokens:
            if not token.is_operator:
                output.append(token)
            elif token.value == '(':
                stack.append(token)
            elif token.value == ')':
                while stack and stack[-1].value != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()  # Descarta el '('
                else:
                    raise ValueError("No se encontró un '(' que haga match con ')'.")
            elif token.value in {'|', '.'}:  # operadores binarios
                while (stack and stack[-1].value in {'|', '.'} and
                       self.PRECEDENCE[token.value] <= self.PRECEDENCE[stack[-1].value]):
                    output.append(stack.pop())
                stack.append(token)
            elif token.value in {'*', '+', '?'}:  # operadores unarios
                output.append(token)
            else:
                stack.append(token)
        
        while stack:
            op = stack.pop()
            if op.value in {'(', ')'}:
                raise ValueError("Paréntesis desbalanceados")
            output.append(op)
    
        return output

    
    def parse(self):
        """
        Método principal que convierte la expresión en tokens y en notación postfija.
        """
        self.tokenize()
        return self.to_postfix()

if __name__ == "__main__":
    regex = "[A-Za-z]bb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    print("Tokens:", [str(token) for token in parser.tokens])  
    print("Postfix:", [str(token) for token in postfix])  
