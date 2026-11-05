"""Simularea generațiilor și afișarea lor în consolă."""

from cellab.rules import find_matching_rule, next_elementary_row


def step_elementary(automaton):
    """Elementary CA (1D): generează rândul următor din diagrama spațio-temporală de pe matricea 2D."""
    curr_row_idx = min(automaton.generation, automaton.rows - 1)
    source_row = automaton.grid[curr_row_idx]
    next_row = next_elementary_row(automaton, source_row)

    if automaton.generation < automaton.rows - 1:
        automaton.grid[automaton.generation + 1] = next_row
    else:
        # Dacă am umplut matricea, derulăm în sus cu o linie (smooth scrolling)
        automaton.grid.pop(0)
        automaton.grid.append(next_row)

    automaton.generation += 1


def step_2d(automaton):
    """2D CA (Brian's Brain, Cyclic CA etc.): aplică regulile de tranziție tuturor celulelor simultan."""
    new_grid = [[automaton.grid[r][c] for c in range(automaton.cols)] for r in range(automaton.rows)]

    for r in range(automaton.rows):
        for c in range(automaton.cols):
            current_state = automaton.grid[r][c]
            neighbor_counts = automaton._get_neighbors(r, c)
            rule = find_matching_rule(automaton.transitions, current_state, neighbor_counts)
            if rule is not None:
                new_grid[r][c] = rule["next_state"]

    automaton.grid = new_grid
    automaton.generation += 1


def display(automaton):
    """Afișează matricea formatată în consolă folosind simbolurile din configurație."""
    for row in automaton.grid:
        line = "".join(automaton.symbols.get(cell, cell + " ") for cell in row)
        print(line)
