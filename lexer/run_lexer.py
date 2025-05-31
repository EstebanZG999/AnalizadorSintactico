import sys
import os

# ------------------------------------------------------------------
# Aseguramos que el paquete 'lexer' sea importable
# ------------------------------------------------------------------
# project_root = .../AnalizadorSintactico (la carpeta raíz del proyecto)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# ------------------------------------------------------------------
# Cambiamos el cwd a la carpeta 'lexer/' para que las rutas relativas dentro
# de generate_lexer() apunten correctamente a 'lexer/inputs/lexer.yal'.
# ------------------------------------------------------------------
lexer_dir = os.path.dirname(__file__)
os.chdir(lexer_dir)

# ------------------------------------------------------------------
# Ahora los imports absolutos desde 'lexer.src.controllers...' 
# ------------------------------------------------------------------
from lexer.src.controllers.main_controller import generate_lexer, generate_global_dfa

# ------------------------------------------------------------------
# Generar (o actualizar) thelexer.py a partir de lexer/inputs/lexer.yal
# ------------------------------------------------------------------
generate_lexer()

# ------------------------------------------------------------------
# Generar el DFA global (opcional para depuración)
# ------------------------------------------------------------------
try:
    global_dfa = generate_global_dfa()
    print("DFA global construido con éxito.")
except Exception as e:
    print(f"No pude generar el DFA global: {e}")

# ------------------------------------------------------------------
# NOTA: Ya no hacemos análisis léxico de ningún archivo aquí.
#       Este script solo genera thelexer.py y el DFA, y sale.
# ------------------------------------------------------------------
sys.exit(0)