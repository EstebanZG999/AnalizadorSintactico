def compute_first(productions):
    first = { nt: set() for nt in productions }  # FIRST sets vacíos
    changed = True

    while changed:
        changed = False
        for nt, prods in productions.items():
            for prod in prods:
                # caso: producción vacía
                if prod == ["ε"]:
                    if "ε" not in first[nt]:
                        first[nt].add("ε")
                        changed = True
                    continue

                # recorremos símbolos de la derecha
                nullable_prefix = True
                for sym in prod:
                    if sym not in productions:  # es terminal
                        if sym not in first[nt]:
                            first[nt].add(sym)
                            changed = True
                        nullable_prefix = False
                        break
                    else:
                        # añadimos FIRST(sym) \ {ε} a FIRST(nt)
                        before = len(first[nt])
                        first[nt] |= (first[sym] - {"ε"})
                        if len(first[nt]) > before:
                            changed = True
                        # si FIRST(sym) contiene ε, seguimos; si no, cortamos
                        if "ε" in first[sym]:
                            nullable_prefix = True
                        else:
                            nullable_prefix = False
                            break

                # si todos los símbolos pueden derivar ε, entonces ε ∈ FIRST(nt)
                if nullable_prefix:
                    if "ε" not in first[nt]:
                        first[nt].add("ε")
                        changed = True

    return first    

def compute_follow(productions, start_symbol, first):
    follow = { nt: set() for nt in productions }
    follow[start_symbol].add("$")   # marcador de fin de cadena

    changed = True
    while changed:
        changed = False
        for nt, prods in productions.items():
            for prod in prods:
                trailer = follow[nt].copy()
                # recorremos la producción de derecha a izquierda
                for sym in reversed(prod):
                    if sym in productions:  # si es no terminal
                        before = len(follow[sym])
                        follow[sym] |= trailer
                        if len(follow[sym]) > before:
                            changed = True

                        # si FIRST(sym) contiene ε, extendemos trailer
                        if "ε" in first[sym]:
                            trailer |= (first[sym] - {"ε"})
                        else:
                            trailer = first[sym] - {"ε"}
                    else:
                        # sym es terminal: el trailer pasa a ser {sym}
                        trailer = {sym}

    return follow
