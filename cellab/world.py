"""Crearea grilelor și numărarea celulelor."""

import random


def filled_grid(rows, cols, state):
    """Creează o grilă în care toate celulele au aceeași stare."""
    return [[state for _ in range(cols)] for _ in range(rows)]


def elementary_start_grid(rows, cols, states, dead_state, active_states, probabilities=None):
    """
    Starea inițială pentru Elementary CA: o singură celulă activă în centrul primului rând
    (000...1...000) sau, dacă sunt date probabilități, un prim rând aleatoriu.
    """
    grid = filled_grid(rows, cols, dead_state)
    if probabilities:
        grid[0] = random.choices(states, weights=probabilities, k=cols)
    else:
        mid = cols // 2
        active_val = active_states[0] if active_states else "1"
        grid[0][mid] = active_val
    return grid


def random_grid(rows, cols, states, probabilities=None):
    """Populează aleatoriu matricea; probabilitățile sunt folosite doar dacă acoperă toate stările."""
    if probabilities and len(probabilities) == len(states):
        return [
            random.choices(states, weights=probabilities, k=cols)
            for _ in range(rows)
        ]
    return [
        [random.choice(states) for _ in range(cols)]
        for _ in range(rows)
    ]


def count_cells(grid, active_states, state=None):
    """Numără celulele dintr-o stare dată sau, dacă state=None, toate celulele active."""
    if state is not None:
        return sum(row.count(state) for row in grid)
    active_set = set(active_states)
    return sum(1 for row in grid for cell in row if cell in active_set)


def state_counts(grid, states):
    """Returnează un dicționar cu distribuția tuturor stărilor din grilă."""
    counts = {s: 0 for s in states}
    for row in grid:
        for cell in row:
            counts[cell] = counts.get(cell, 0) + 1
    return counts
