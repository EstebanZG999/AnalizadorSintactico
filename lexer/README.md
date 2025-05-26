# Generador de Lexer a partir de Especificaciones YALex
Este proyecto expande la funcionalidad de construcción de Autómatas Finitos Deterministas (AFD) para crear un Lexer (analizador léxico) basado en una especificación YALex. El sistema combina la creación de DFAs —mediante la técnica de followpos— con la lectura de definiciones YALex y la generación automática de código para el analizador léxico final.

## Funcionalidad Principal
1. Lectura de la especificación en YALex (archivo .yal).
2. Construcción del árbol de expresión (y su graficación) que representa la definición regular de los tokens.
3. Generación de un programa fuente (thelexer.py) que implementa un analizador léxico según las reglas definidas en YALex.
4. Posibilidad de probar el lexer resultante con un script de ejemplo, verificando los tokens reconocidos.

## 📁 Estructura del Proyecto
📄 ```main.py``` → Funciona como punto de entrada o script principal

📄 ```thelexer.py``` → (Generado automáticamente) Contiene la clase Lexer final. Se construye combinando cada regla y su DFA correspondiente para reconocer tokens. No se edita manualmente.

📄 ```run_lexer.py``` → Script que genera (o actualiza) el analizador léxico a partir de la especificación YALex y luego ejecuta dicho lexer sobre un archivo de texto dado (por defecto, entrada.txt).

### 📂 models/
- 📄 ```regex_parser.py``` → Convierte expresiones regulares en notación postfija (usando una variante del algoritmo Shunting-Yard).
- 📄 ```syntax_tree.py``` → Construye y representa el árbol sintáctico a partir de la notación postfija. También permite graficarlo con Graphviz.
- 📄 ```dfa.py``` → Implementa la construcción directa de un AFD usando la técnica de followpos, e incluye métodos de simulación.
- 📄 ```mindfa.py``` → Aplica el algoritmo de Hopcroft para minimizar el AFD resultante.

### 📂 inputs/
- 📄 ```yalex_parser.py``` → Parsea un archivo .yal (YALex) para extraer definiciones y reglas.
- 📄 ```entrada.txt``` → Archivo de entrada que contiene las cadenas (texto) a ser procesadas y tokenizadas por el analizador léxico.  

### 📂 controllers/
- 📄 ```main_controller.py``` → Orquestador principal. Genera el DFA global a partir de YALex, asigna marcadores a cada regla y construye la clase Lexer.

### 📂 tests/
- 📄 ```test_lexer.py``` → Ejemplo de script para probar el lexer generado. Lee una cadena de ejemplo y muestra los tokens generados.

## 🛠 Tecnologías Utilizadas
- Python → Lenguaje principal del proyecto.
- Graphviz → Visualización de árboles sintácticos y AFDs.
- Shunting-Yard → Conversión de expresiones regulares a notación postfija.
- Hopcroft → Minimización de AFD.
- YALex → Especificación de reglas léxicas en un archivo .yal.

## ⚙️ Instalación y Uso
1. **Clona el repositorio**:
    ```
   git clone <repository-url>
    ```
2. **Navega al directorio**:
   ```
   cd <repository-name>
   ```
3. **Instala las dependencias**:
    ```
   pip install graphviz
    ```
4. **Preparar el archivo .yal**:

   En la carpeta inputs/, ubica o edita el archivo lexer.yal con tus definiciones y reglas.
5. **Generar el lexer**:
   Desde tu terminal:
    ```
   python run_lexer.py
    ```
    El programa leerá el texto de entrada.txt, reconocerá los tokens definidos en el .yal y mostrará en pantalla tanto los tokens identificados como los errores léxicos, de existir.

### Ejemplo de Archivo YALex
  ```
{ 
    # Código de header (opcional)
}
    let DIGIT = [0-9]
    let LETTER = [A-Za-z]
    rule gettoken =
        | LETTER (LETTER | DIGIT)+ { return ("WORD", lexeme) }
        | LETTER { return ("LETTER", lexeme) }
        | [' ' '\t'] { return None }
        | eof    { return ("EOF", None) }
        | '\n' { return ("EOL", None) }
{ 
    # Código de trailer (opcional)
}
  ```

### Cuando se ejecute, el sistema:
1. Leer el archivo YALex:
   Se extraen definiciones, reglas y el header o trailer opcional.
2. Construir un DFA global que reconoce todos los tokens, asignando un marcador único a cada regla.
3. Generar (o reutilizar) DFAs específicos para cada regla y construir el archivo thelexer.py.
4. Usar el lexer en scripts de prueba, identificando tokens en la cadena de entrada.

## Ejemplo de Entrada y Salida
Entrada:
```
Hola como 45 X

A + B
```

Salida Esperada:

```[('WORD', 'Hola'), ('WORD', 'Como'), ('NUMBER', 45), ('LETTER', 'X'), ('EOL', None), ('EOL', None), ('LETTER', 'A'), ('PLUS', '+'), ('LETTER', 'B'), ('EOL', None)]```

## 📚 Referencias
#### Graphviz - Graph Visualization Software
🔗[Graphviz Documentation](https://graphviz.org/)
#### Regular Expressions - MDN Web Docs
🔗[Mozilla Developer Network (MDN)]( https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions)
#### IBM i 7.3 - Regular Expressions
🔗[IBM Documentation](https://www.ibm.com/docs/es/i/7.3?topic=expressions-regular)

## ⚖️ Licencia
📌 UVG License
Proyecto de código abierto bajo la licencia UVG. Puedes usarlo, modificarlo y distribuirlo libremente dando crédito a los autores originales.
