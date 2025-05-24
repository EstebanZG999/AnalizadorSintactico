def construct_slr_table(states: list[State],
                        transitions: dict[(int, str), int],
                        productions: dict,
                        follow: dict[str, set[str]]) -> (action, goto):
    """
    - `action[(i, a)]`: 
       * shift j  si existe transición (i, a)=j y a es terminal
       * reduce k si i contiene ítem A → α· y producción k es A→α, para cada a ∈ follow[A]
       * accept   si i contiene S' → S·
       * error    en cualquier otro caso
    - `goto[(i, A)]` = estado j para producciones de no-terminal
    """
