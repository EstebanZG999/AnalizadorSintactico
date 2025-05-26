import sys
import os
from src.controllers.main_controller import generate_lexer, generate_global_dfa

# Asegurarnos de que el directorio raíz y 'src' estén en el path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))


# Generar (o actualizar) el analizador léxico a partir de la especificación YALex
generate_lexer()

from thelexer import Lexer

def main():
    # 2) Construir y renderizar el DFA global para depuración
    try:
        global_dfa = generate_global_dfa()
        print("DFA global construido con éxito.")
    except Exception as e:
        print(f"No pude generar el DFA global: {e}")

    # Si no se pasa un archivo de entrada, usamos uno por defecto en 'inputs'
    if len(sys.argv) < 2:
        default_input_file = os.path.join("inputs", "entrada.txt")
        print(f"No se especificó archivo de entrada. Usando '{default_input_file}' por defecto.")
        input_file = default_input_file
    else:
        input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: El archivo '{input_file}' no existe.")
        sys.exit(1)
    
    with open(input_file, "r", encoding="utf-8") as f:
        entrada = f.read()
    
    lexer = Lexer(entrada)
    tokens = lexer.get_tokens()
    
    print("Tokens reconocidos:")
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()
