# src/models/dfa.py
import os
import graphviz
from src.models.syntax_tree import NodoHoja, NodoBinario, NodoUnario, SyntaxTree

class DFA:
    def __init__(self, syntax_tree):
        self.syntax_tree = syntax_tree
        # Calcula la función followpos y el mapeo de posiciones a símbolos
        self.followpos = self.compute_followpos(syntax_tree.raiz)
        self.pos_to_symbol = self.compute_pos_to_symbol(syntax_tree.raiz)
        # Definir el alfabeto (excluimos el marcador '#' de entrada)
        self.alphabet = { sym for sym in self.pos_to_symbol.values() if sym != '#' }
        # Diccionario para almacenar los estados (clave: frozenset de posiciones, valor: ID del estado)
        self.states = {}
        # Tabla de transiciones: {estado_id: {símbolo: estado_id_destino}}
        self.transitions = {}
        self.initial_state = None
        self.accepting_states = set()
        # Construir el AFD
        self.build_dfa()
        # Creo un mapeo inverso {estado_id -> frozenset(posiciones)}
        self.state_sets = { state_id: state_set
                        for state_set, state_id in self.states.items() }
        # Averiguo la posición del marcador interno '#', si existe
        try:
            self.marker_pos = next(pos for pos, sym in self.pos_to_symbol.items()
                                   if sym == '#')
        except StopIteration:
            self.marker_pos = None

    def compute_followpos(self, node):
        followpos = {}

        def init_followpos(n):
            if isinstance(n, NodoHoja):
                followpos[n.posicion] = set()
            elif isinstance(n, NodoBinario):
                init_followpos(n.izquierdo)
                init_followpos(n.derecho)
            elif isinstance(n, NodoUnario):
                init_followpos(n.hijo)
        init_followpos(node)

        def traverse(n):
            if isinstance(n, NodoBinario):
                traverse(n.izquierdo)
                traverse(n.derecho)
                if n.valor == '.':
                    # Para cada p en lastpos(izquierdo), followpos[p] += firstpos(derecho)
                    for pos in n.izquierdo.lastpos:
                        followpos[pos].update(n.derecho.firstpos)
            elif isinstance(n, NodoUnario):
                traverse(n.hijo)
                if n.valor == '*':
                    # Para cada p en lastpos(hijo), followpos[p] += firstpos(hijo)
                    for pos in n.hijo.lastpos:
                        followpos[pos].update(n.hijo.firstpos)
            # NodoHoja no hace nada
        traverse(node)

        return followpos


    def compute_pos_to_symbol(self, node):
        """Crea un diccionario que mapea cada posición de un nodo hoja a su símbolo."""
        pos_to_symbol = {}

        def traverse(n):
            if isinstance(n, NodoHoja):
                pos_to_symbol[n.posicion] = n.valor
            elif isinstance(n, NodoBinario):
                traverse(n.izquierdo)
                traverse(n.derecho)
            elif isinstance(n, NodoUnario):
                traverse(n.hijo)
        traverse(node)
        return pos_to_symbol

    def build_dfa(self):
        initial = frozenset(self.syntax_tree.raiz.firstpos)
        self.states[initial] = 0
        self.initial_state = 0
        unmarked_states = [initial]
        state_id_counter = 0

        while unmarked_states:
            current = unmarked_states.pop(0)
            current_state_id = self.states[current]
            self.transitions[current_state_id] = {}

            for symbol in self.alphabet:
                u = set()
                for pos in current:
                    if self.pos_to_symbol[pos] == symbol:
                        u.update(self.followpos[pos])
                if u:
                    u = frozenset(u)
                    if u not in self.states:
                        state_id_counter += 1
                        self.states[u] = state_id_counter
                        unmarked_states.append(u)
                    self.transitions[current_state_id][symbol] = self.states[u]

        # Estados de aceptación: usa get() para evitar KeyError si falta alguna posición
        for state_set, state_id in self.states.items():
            if any(self.pos_to_symbol[p] == '#' for p in state_set):
                self.accepting_states.add(state_id)
        # Fallback: solo si aún no hay aceptadores Y hay posiciones definidas
        if not self.accepting_states and self.pos_to_symbol:
            max_pos = max(self.pos_to_symbol)
            for state_set, state_id in self.states.items():
                if max_pos in state_set:
                    self.accepting_states.add(state_id)
        

    def simulate(self, string):
        """
        Simula el AFD con la cadena de entrada 'string'.
        Retorna True si, tras procesar todos los caracteres,
        el estado en que quedas está marcado como de aceptación.
        """
        current = self.initial_state
        for ch in string:
            trans = self.transitions.get(current, {})
            if ch not in trans:
                return False
            current = trans[ch]
        return current in self.accepting_states



    def print_dfa(self):
        """Imprime la tabla de transiciones y los estados de aceptación."""
        print("Estados y sus conjuntos de posiciones:")
        for state_set, state_id in self.states.items():
            aceptacion = " (aceptación)" if state_id in self.accepting_states else ""
            print(f"Estado {state_id}{aceptacion}: {set(state_set)}")
        print("\nTransiciones:")
        for state_id, trans in self.transitions.items():
            for symbol, target in trans.items():
                print(f"  δ({state_id}, '{symbol}') = {target}")




    def render_dfa(self, filename="dfa"):
        """
        Genera un diagrama del AFD usando Graphviz y lo guarda en la carpeta 'imagenes/'.
        """
        # Asegurar que la carpeta 'imagenes' existe
        if not os.path.exists("imagenes"):
            os.makedirs("imagenes")

        dot = graphviz.Digraph(format="png")

        # Agregar estados
        for state_set, state_id in self.states.items():
            shape = "doublecircle" if state_id in self.accepting_states else "circle"
            label = f"q{state_id}\n{state_set}"
            dot.node(str(state_id), label=label, shape=shape)

        # Estado inicial
        dot.node("start", shape="none", label="")
        dot.edge("start", str(self.initial_state))

        # Agregar transiciones
        for state_id, trans_dict in self.transitions.items():
            for symbol, target_id in trans_dict.items():
                symbol_escaped = symbol.replace('\\', '\\\\').replace('"', '\\"')
                dot.edge(str(state_id), str(target_id), label=f"\"{symbol_escaped}\"")

        # Guardar la imagen en la carpeta 'imagenes/'
        output_path = f"imagenes/{filename}"
        dot.render(output_path, view=False)

        print(f"Imagen del DFA guardada en: {output_path}.png")

    def match_prefix(self, input_str):
        """
        Escanea input_str + '#' al final y devuelve la longitud
        del mayor prefijo reconocido por el DFA (sin contar '#').
        """
        current_state = self.initial_state
        last_accept_pos = -1
        # Escaneamos los caracteres reales más un '#' al final
        stream = input_str + '#'
        for i, ch in enumerate(stream, start=1):
            trans = self.transitions.get(current_state, {})
            if ch not in trans:
                break
            current_state = trans[ch]
            # Si es estado de aceptacion, guardamos la posición
            if current_state in self.accepting_states:
                last_accept_pos = i
        # last_accept_pos == índice en stream donde fue aceptado;
        # como en stream aparece '#' en la última posición válida,
        # y queremos la longitud sobre input_str, devolvemos last_accept_pos
        # sólo si es ≥ 0 y menor que len(input_str)+1
        return last_accept_pos
    
    
    def match_prefix_and_token(self, input_str):
        """
        Recorre input_str y devuelve (largo, token_info) donde token_info
        proviene de marker_to_rule para el marcador más prioritario.
        """
        current_state = self.initial_state
        last_accept_pos = -1
        accepted_state = None
        pos = 0

        for ch in input_str:
            trans = self.transitions.get(current_state, {})
            if ch in trans:
                current_state = trans[ch]
                pos += 1
                if current_state in self.accepting_states:
                    last_accept_pos = pos
                    accepted_state = current_state
            else:
                break

        if last_accept_pos != -1 and accepted_state is not None:
            # obtenemos el conjunto de posiciones del estado aceptador
            state_set = self.state_sets[accepted_state]
            matched_marker = None
            for p in state_set:
                sym = self.pos_to_symbol[p]
                if sym in self.marker_to_rule:
                    # elegimos el marcador de menor 'order'
                    if (matched_marker is None or
                        self.marker_to_rule[sym]['order'] <
                        self.marker_to_rule[matched_marker]['order']):
                        matched_marker = sym
            if matched_marker is not None:
                return last_accept_pos, self.marker_to_rule[matched_marker]

        return 0, None

 
 
if __name__ == "__main__":
    # Ejemplo de uso:
    # 1. Se define una expresión regular.
    regex = "(a|b)*abb#"
    # 2. Se crea el parser y se genera la notación postfija.
    from regex_parser import RegexParser
    parser = RegexParser(regex)
    postfix = parser.parse()
    # 3. Se construye el árbol sintáctico.
    syntax_tree = SyntaxTree(postfix)
    # 4. Se construye el AFD a partir del árbol sintáctico.
    dfa = DFA(syntax_tree)
    
    # Imprime la tabla de transiciones y los estados.
    print("Tokens:", [str(token) for token in parser.tokens])
    print("Postfix:", [str(token) for token in postfix])

    dfa.print_dfa()
    
    # 5. Simulación del AFD con cadenas de prueba.
    test_strings = ["aaabb", "aabb", "ababb", "ababbbbabb"]
    for s in test_strings:
        result = dfa.simulate(s)
        print(f"\nLa cadena '{s}' {'es aceptada' if result else 'NO es aceptada'} por la expresión regular.")

    dfa.render_dfa("dfa")  