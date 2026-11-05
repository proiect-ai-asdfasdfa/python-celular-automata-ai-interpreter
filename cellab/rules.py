"""Definirea vecinătăților și aplicarea regulilor de tranziție."""

MOORE_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]

VON_NEUMANN_OFFSETS = [
    (-1, 0),
    (0, -1), (0, 1),
    (1, 0)
]


def count_neighbors(automaton, r, c):
    """
    Calculează frecvența stărilor vecinilor pentru celula (r, c) în automate 2D.
    Suportă cartier Moore (8 vecini) și von Neumann (4 vecini),
    precum și bordură toroidală (wrap) sau fixă (fixed/dead).
    """
    offsets = MOORE_OFFSETS if automaton.neighborhood_type == "moore" else VON_NEUMANN_OFFSETS
    neighbor_counts = {state: 0 for state in automaton.states}

    for dr, dc in offsets:
        nr, nc = r + dr, c + dc

        if automaton.boundary == "wrap":
            nr %= automaton.rows
            nc %= automaton.cols
            neighbor_state = automaton.grid[nr][nc]
            neighbor_counts[neighbor_state] = neighbor_counts.get(neighbor_state, 0) + 1
        else:
            # Bordură fixă (celulele din afara matricei sunt tratate ca dead_state)
            if 0 <= nr < automaton.rows and 0 <= nc < automaton.cols:
                neighbor_state = automaton.grid[nr][nc]
                neighbor_counts[neighbor_state] = neighbor_counts.get(neighbor_state, 0) + 1
            else:
                neighbor_counts[automaton.dead_state] = neighbor_counts.get(automaton.dead_state, 0) + 1

    return neighbor_counts


def find_matching_rule(transitions, current_state, neighbor_counts):
    """Returnează prima regulă compatibilă din lista de tranziții sau None dacă nu există."""
    for rule in transitions:
        if rule.get("current_state") == current_state:
            target_counts = rule.get("counts")
            min_count = rule.get("min_count")
            req_neighbor = rule.get("neighbor_state")

            # Regula necondiționată (ex: FIRING -> DYING, DYING -> OFF)
            if target_counts == "any":
                return rule

            # Regula cu prag minim (ex: la Cyclic CA: cel puțin 2 vecini)
            elif min_count is not None and req_neighbor:
                if neighbor_counts.get(req_neighbor, 0) >= min_count:
                    return rule

            # Regula condiționată de mulțimea de numere de vecini
            elif req_neighbor:
                counts_list = [target_counts] if isinstance(target_counts, int) else target_counts
                if counts_list is not None and neighbor_counts.get(req_neighbor, 0) in counts_list:
                    return rule
    return None


def next_elementary_row(automaton, source_row):
    """Calculează rândul următor al unui automat 1D Elementary din modelele (stânga, centru, dreapta)."""
    next_row = [automaton.dead_state] * automaton.cols

    for c in range(automaton.cols):
        if automaton.boundary == "wrap":
            left = source_row[(c - 1) % automaton.cols]
            right = source_row[(c + 1) % automaton.cols]
        else:
            left = source_row[c - 1] if c > 0 else automaton.dead_state
            right = source_row[c + 1] if c < automaton.cols - 1 else automaton.dead_state
        curr = source_row[c]

        pattern_key = f"{left}{curr}{right}"
        next_row[c] = automaton.patterns.get(pattern_key, automaton.dead_state)

    return next_row
