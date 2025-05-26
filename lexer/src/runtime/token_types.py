# src/runtime/token_types.py

SKIP      = "skip"
EOL       = "EOL"
PLUS      = "PLUS"
MINUS     = "MINUS"
TIMES     = "TIMES"
DIV       = "DIV"        
LPAREN    = "LPAREN"
RPAREN    = "RPAREN"
LBRACE    = "LBRACE"     
RBRACE    = "RBRACE"     
COMMA     = "COMMA"      
SEMICOLON = "SEMICOLON"  
COLON     = "COLON"      
LT        = "LT"
EQ        = "EQ"
GT        = "GT"         
ASSIGNOP  = "ASSIGNOP" 
HASH      = "HASH"       
EOF       = "EOF"

# Tipos básicos
WORD      = "WORD"
LETTER    = "LETTER"
NUMBER    = "NUMBER"
ID        = "ID"
SYMBOL    = "SYMBOL"   

# Keywords
IF        = "IF"
ELSE      = "ELSE"
WHILE     = "WHILE"
FOR       = "FOR"
RETURN    = "RETURN"
BREAK     = "BREAK"
CONTINUE  = "CONTINUE"

KEYWORDS = {
    "if":       IF,
    "else":     ELSE,
    "while":    WHILE,
    "for":      FOR,
    "return":   RETURN,
    "break":    BREAK,
    "continue": CONTINUE,
}


# ——— Mapeo directo de símbolos de un solo carácter ———
PUNCTUATIONS = {
    '(': LPAREN,
    ')': RPAREN,
    '{': LBRACE,
    '}': RBRACE,
    '+': PLUS,
    '-': MINUS,
    '*': TIMES,
    '/': DIV,
    ',': COMMA,
    ';': SEMICOLON,
    ':': COLON,
    '<': LT,
    '=': EQ,
    '>': GT,
    '#': HASH,
}