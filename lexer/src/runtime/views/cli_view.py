# views/cli_view.py

def ask_for_regex():
    """Pide al usuario que ingrese la expresión regular."""
    return input("Ingresa la expresión regular, termina la cadena en un # (aab#): ")

def ask_for_num_strings():
    """Pide al usuario cuántas cadenas desea probar."""
    count = input("¿Cuántas cadenas deseas probar? ")
    return int(count)

def ask_for_string(index):
    """Pide al usuario que ingrese la cadena enésima."""
    return input(f"Ingresa la cadena {index+1}: ")

def show_dfa_info(dfa):
    """Muestra información del DFA por consola."""
    dfa.print_dfa()

def show_simulation_result(string, accepted):
    """Muestra el resultado de la simulación de una cadena."""
    msg = f"La cadena '{string}' es {'aceptada' if accepted else 'NO es aceptada'}."
    print(msg)

def show_message(msg):
    """Muestra un mensaje cualquiera por consola."""
    print(msg)
