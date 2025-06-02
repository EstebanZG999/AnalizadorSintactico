# Analizador Léxico + Sintáctico SLR(1)

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Tests](https://img.shields.io/badge/tests-pytest-green?logo=pytest)

Generador **end-to-end** (lexer → parser) escrito en Python que:

1. Convierte especificaciones **YALex** (`*.yal`) en un lexer determinista (`thelexer.py`).
2. Convierte especificaciones **YAPar** (`*.yalp`) en un parser SLR (1) (`theparser.py`).
3. Permite ejecutar ambos en un solo paso sobre un archivo fuente, imprimiendo tokens, trazas *shift/reduce* y validación sintáctica.

## ✨ Características

| Módulo | Destacado |
|--------|-----------|
| **Lexer** | Construcción directa de DFA por `followpos`, minimización Hopcroft, mapa dinámico `PUNCTUATIONS`, números en notación científica, imágenes `Graphviz`. |
| **Parser** | FIRST/FOLLOW, LR(0) itens & estados, tablas ACTION/GOTO SLR(1) impresas en formato `tabulate`, trazado opcional paso a paso, generación de `theparser.py`. |
| **CLI**    | Flags `--show-grammar`, `--show-automaton`, `--show-tables`, `--show-parse` para depurar cada fase. |
| **Tests**  | Pytest unitarios para: YALex parser, Regex→DFA, FIRST/FOLLOW, LR(0) automata, tablas SLR, parser-interface, integración end-to-end. |

## 📁 Estructura del proyecto

```text
AnalizadorSintactico/
├── lexer/                  # Módulo del analizador léxico
│   ├── inputs/             # Archivos de entrada para el lexer
│   │   ├── lexer.yal       # Especificación YALex de tokens
│   │   └── entrada.txt     # Archivo de prueba para el lexer
│   ├── src/                # Código fuente del lexer
│   │   ├── models/         # Modelos y estructuras de datos
│   │   │   ├── regex_parser.py    # Parser de expresiones regulares
│   │   │   ├── syntax_tree.py     # Árbol sintáctico para regex
│   │   │   ├── dfa.py             # Construcción de DFA
│   │   │   ├── mindfa.py          # Minimización de DFA
│   │   │   └── yalex_parser.py    # Parser de archivos YALex
│   │   └── controllers/
│   │       └── main_controller.py # Controlador principal del lexer
│   └── run_lexer.py       # Script para generar y ejecutar el lexer
│
├── sintaxer/               # Módulo del analizador sintáctico
│   ├── inputs/             # Archivos de entrada para el parser
│   │   └── arithmetic.yalp # Especificación YAPar de la gramática
│   ├── src/                # Código fuente del parser
│   │   ├── models/         # Modelos y estructuras de datos
│   │   │   ├── yalp_parser.py     # Parser de archivos YAPar
│   │   │   ├── grammar_analysis.py# Análisis de la gramática (FIRST/FOLLOW)
│   │   │   ├── lr0.py             # Construcción de autómatas LR(0)
│   │   │   └── slr_table.py       # Generación de tablas SLR(1)
│   │   └── generators/
│   │       └── parser_generator.py# Generador del parser SLR(1)
│   └── run_parser.py      # Script para generar y ejecutar el parser
│
├── tests/                  # Pruebas unitarias y de integración
│   ├── test_lexer.py       # Pruebas para el lexer
│   └── test_parser.py      # Pruebas para el parser
│
├── docs/                   # Documentación y recursos adicionales
│   ├── README.md           # Documentación principal del proyecto
│   └── assets/             # Imágenes y diagramas
│
├── thelexer.py             # Archivo generado automáticamente del lexer
├── theparser.py            # Archivo generado automáticamente del parser
├── run_all.py              # Script para ejecutar lexer y parser en conjunto
├── requirements.txt        # Dependencias del proyecto
└── .venv/                  # Entorno virtual de Python (opcional)

```

## 🌐 Tecnologías Utilizadas
- Python → Lenguaje principal del proyecto.
- Graphviz → Visualización gráfica de árboles sintácticos y autómatas LR(0).
- Shunting-Yard → Algoritmo para convertir expresiones regulares infix a notación postfija, lo cual permite la construcción de árboles de sintaxis de forma estructurada.
- Followpos → Técnica utilizada para construir de forma directa un Autómata Finito Determinista (DFA) desde expresiones regulares.
- Hopcroft → Algoritmo de minimización de autómatas, aplicado para optimizar el DFA generado y reducir la cantidad de estados.
- SLR(1) → Algoritmo de análisis sintáctico que usa conjuntos FIRST y FOLLOW junto con autómatas LR(0) para construir las tablas ACTION y GOTO.
- Tabulate → Librería usada para imprimir las tablas del parser (ACTION y GOTO) en un formato tabular claro y legible.
- Pytest → Marco de pruebas unitarias utilizado para validar módulos individuales (lexer, parser, integración), asegurando consistencia y robustez.
- YALex → Lenguaje para definir especificaciones léxicas mediante expresiones regulares. Se traduce automáticamente a un lexer.
- YAPar → Lenguaje para definir gramáticas libres de contexto (GLC) y sus producciones. Permite generar automáticamente un parser SLR(1).

## ⚙️ Instalación y Uso

1. **Clona el repositorio**:
    ```
   git clone <repository-url>
    ```
2. **Navega al directorio**:
   ```
   cd AnalizadorSintactico
   ```
3. **Crea tu propio entorno virtual**:
    ```
   python3 -m venv .venv && source .venv/bin/activate
    ```
4. **Instala todos los requisitos**:
    ```
   pip install -r requirements.txt
    ```
    
5. **Corre el proyecto**:
   Desde tu terminal:
   En la carpeta raíz
    ```
   python3 run_all.py sintaxer/inputs/parser.yalp inputs/input2.txt --show-grammar --show-automaton --show-tables --show-parse
    ```
## 🧪 Ejemplo de Ejecución

Al ejecutar se imprimirá en consola:
1. Gramática extendida con producción aumentada (índice 0).
2. Autómata LR(0) con estados y transiciones.
3. Tablas ACTION y GOTO bien alineadas (usando tabulate).
4. Tokens generados por el lexer ([(tipo, lexema), …]).
5. Trazado paso a paso del análisis sintáctico (acciones shift, reduce, accept).
6. Resultado final de aceptación o error.

## 🛠️ Modificar tu gramática

1. Tokens → edita lexer/inputs/lexer.yal
2. Producciones → edita sintaxer/inputs/parser.yalp
3. Ejecuta run_all.py de nuevo: los archivos generados (thelexer.py, theparser.py) se reemplazan.

## ✅ Validación y Pruebas
Para ejecutar pruebas unitarias y de integración, necesitas estar en la carpeta  ```sintaxer```  y ejecutar :

 ```
pytest tests/
 ```
    
Esto validará:
- Parsing correcto de archivos .yalp (```test_yalp_parser.py```)
- Cálculo correcto de los conjuntos FIRST y FOLLOW (```test_grammar_analysis.py```)
- Construcción del autómata LR(0) (```test_lr0.py```)
- Generación adecuada de las tablas ACTION y GOTO (```test_slr_table.py```)
- Correcta creación del parser final (```test_parser_generator.py```)
- Comprobación de la interfaz theparser.py (```test_parser_interface.py```)
- Integración end-to-end del parser con simulaciones de entrada (```test_parser_integration.py```)

## 📚 Referencias
#### Graphviz - Graph Visualization Software
🔗[Graphviz Documentation](https://graphviz.org/)
#### Shunting-Yard Algorithm - Brillant
🔗[Shunting-Yard Algorithm](https://brilliant.org/wiki/shunting-yard-algorithm/)
#### IBM i 7.3 - Regular Expressions
🔗[IBM Documentation](https://www.ibm.com/docs/es/i/7.3?topic=expressions-regular)

## ⚖️ Licencia
📌 MIT License
Proyecto de código abierto bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente dando crédito a los autores originales.
