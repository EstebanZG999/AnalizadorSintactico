# Código generado automáticamente por YALex
import re
from src.runtime.token_types import *

# Mapa de puntuaciones generado según las reglas de la gramática
PUNCTUATIONS = {
    '\\n': EOL,
    'if': IF,
    'else': ELSE,
    'while': WHILE,
    'for': FOR,
    'return': RETURN,
    'break': BREAK,
    'continue': CONTINUE,
    ':=': ASSIGNOP,
    '+': PLUS,
    '-': MINUS,
    '*': TIMES,
    '/': DIV,
    '(': LPAREN,
    ')': RPAREN,
    ',': COMMA,
    ';': SEMICOLON,
    ':': COLON,
    '<': LT,
    '=': EQ,
    '>': GT,
    '{': LBRACE,
    '}': RBRACE,
    '#': HASH,
}

class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.pos = 0

    def get_tokens(self):
        tokens = []
        text = self.input_text
        pos = 0
        while pos < len(text):
            m = re.match(r'\d+\.\d+(?:[eE][+-]?\d+)?', text[pos:])
            if m:
                lexeme = m.group(0)
                tokens.append((NUMBER, lexeme))
                print(f'⟶ Token: {NUMBER!r}, lexema: {lexeme!r}')
                pos += len(lexeme)
                continue
            longest_match = 0
            selected_rule = None
            for rule in self.rules:
                ml = rule['dfa'].match_prefix(text[pos:])
                if ml > longest_match:
                    longest_match = ml
                    selected_rule = rule
            if longest_match > 1:
                lexeme = text[pos:pos+longest_match]
                action_code = selected_rule['action']
                local_env = {'lexeme': lexeme, 'text': text}
                exec(action_code.replace('return', 'token ='), globals(), local_env)
                tok = local_env.get('token')
                if tok is not None:
                    # si la acción ya devolvió (TOKEN, lexeme), lo usamos directamente
                    if isinstance(tok, tuple):
                        tokens.append(tok)
                    else:
                        tokens.append((tok, lexeme))
                    print(f'⟶ Token: {tok!r}, lexema: {lexeme!r}')
                pos += longest_match
                continue
            if longest_match == 1:
                # Ejecutamos la acción (puede ser None para ws)
                lexeme = text[pos]
                action_code = selected_rule['action']
                local_env = {'lexeme': lexeme, 'text': text}
                exec(action_code.replace('return', 'token ='), globals(), local_env)
                tok = local_env.get('token')
                if tok is not None:
                    # si la acción ya devolvió (TOKEN, lexeme), lo usamos directamente
                    if isinstance(tok, tuple):
                        tokens.append(tok)
                    else:
                        tokens.append((tok, lexeme))
                    print(f'⟶ Token: {tok!r}, lexema: {lexeme!r}')
                pos += 1
                continue
            ch = text[pos]
            mapped = PUNCTUATIONS.get(ch)
            if mapped is not None:
                tokens.append((mapped, ch))
                print(f'⟶ Token: {mapped!r}, lexema: {ch!r}')
                pos += 1
                continue
            # Carácter no declarado en la gramática: lo marcamos como UNKNOWN y continuamos
            ch = text[pos]
            print(f"⟶ Token no reconocido: {ch!r} en posición {pos}")
            tokens.append((None, ch))  # None indica token no reconocido
            pos += 1
            continue
        tokens.append((EOF, ''))
        return tokens

    @property
    def rules(self):
        rules = []
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: (([\  \\t])+)
        parser = RegexParser('(([\\  \\\\t])+)' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '(([\\  \\\\t])+)', 'action': 'return None', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \#\#\#.*[\n]
        parser = RegexParser('\\#\\#\\#.*[\\n]' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\#\\#\\#.*[\\n]', 'action': 'return None', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \n
        parser = RegexParser('\\n' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\n', 'action': 'return EOL', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: if
        parser = RegexParser('if' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'if', 'action': 'return (IF,       lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: else
        parser = RegexParser('else' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'else', 'action': 'return (ELSE,     lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: while
        parser = RegexParser('while' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'while', 'action': 'return (WHILE,    lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: for
        parser = RegexParser('for' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'for', 'action': 'return (FOR,      lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: return
        parser = RegexParser('return' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'return', 'action': 'return (RETURN,   lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: break
        parser = RegexParser('break' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'break', 'action': 'return (BREAK,    lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: continue
        parser = RegexParser('continue' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'continue', 'action': 'return (CONTINUE, lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: (([A-Za-z]) ((([A-Za-z]) | ([0-9]) | _))*)
        parser = RegexParser('(([A-Za-z]) ((([A-Za-z]) | ([0-9]) | _))*)' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '(([A-Za-z]) ((([A-Za-z]) | ([0-9]) | _))*)', 'action': 'return (ID,       lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: (([0-9])+(\.([0-9])+)?(E(\+|\-)?([0-9])+)?)
        parser = RegexParser('(([0-9])+(\\.([0-9])+)?(E(\\+|\\-)?([0-9])+)?)' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '(([0-9])+(\\.([0-9])+)?(E(\\+|\\-)?([0-9])+)?)', 'action': 'return (NUMBER,   lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: :=
        parser = RegexParser(':=' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': ':=', 'action': 'return (ASSIGNOP, lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \+
        parser = RegexParser('\\+' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\+', 'action': 'return (PLUS,     lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \-
        parser = RegexParser('\\-' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\-', 'action': 'return (MINUS,    lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \*
        parser = RegexParser('\\*' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\*', 'action': 'return (TIMES,    lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: /
        parser = RegexParser('/' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '/', 'action': 'return (DIV,      lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \(
        parser = RegexParser('\\(' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\(', 'action': 'return (LPAREN,   lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \)
        parser = RegexParser('\\)' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\)', 'action': 'return (RPAREN,   lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ,
        parser = RegexParser(',' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': ',', 'action': 'return (COMMA,    lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ;
        parser = RegexParser(';' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': ';', 'action': 'return (SEMICOLON,lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: :
        parser = RegexParser(':' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': ':', 'action': 'return (COLON,    lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: <
        parser = RegexParser('<' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '<', 'action': 'return (LT,       lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: =
        parser = RegexParser('=' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '=', 'action': 'return (EQ,       lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: >
        parser = RegexParser('>' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '>', 'action': 'return (GT,       lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \{
        parser = RegexParser('\\{' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\{', 'action': 'return (LBRACE,   lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \}
        parser = RegexParser('\\}' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\}', 'action': 'return (RBRACE,   lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: \#
        parser = RegexParser('\\#' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '\\#', 'action': 'return (HASH,     lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: eof
        parser = RegexParser('eof' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'eof', 'action': 'return (EOF,      lexeme)', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: .
        parser = RegexParser('.' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '.', 'action': 'return (SYMBOL,   lexeme)', 'dfa': dfa})
        return rules

