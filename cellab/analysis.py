"""Răspunsurile la întrebările proiectului. Toate rulează pe o copie, fără a modifica automatul curent."""

from copy import deepcopy


def _advanced_copy(automaton, n):
    """Returnează o copie a automatului avansată cu n pași."""
    sim = automaton.clone()
    for _ in range(n):
        sim.step()
    return sim


def get_state_after_n_steps(automaton, n):
    """Q1: Returnează (matricea, generația) după N pași."""
    sim = _advanced_copy(automaton, n)
    return sim.grid, sim.generation


def find_stable_state(automaton, max_steps=1000):
    """Q2: Returnează (True, generație) dacă sistemul a atins stabilitate, altfel (False, None)."""
    sim = automaton.clone()
    for _ in range(max_steps):
        prev_grid = deepcopy(sim.grid)
        sim.step()
        if sim.grid == prev_grid:
            return True, sim.generation
    return False, None


def does_configuration_occur(automaton, target_grid, max_steps=1000):
    """Q3: Returnează (True, generație) dacă matricea target apare în intervalul dat, altfel (False, None)."""
    sim = automaton.clone()
    if sim.grid == target_grid:
        return True, sim.generation

    for _ in range(max_steps):
        sim.step()
        if sim.grid == target_grid:
            return True, sim.generation
    return False, None


def count_cells_after_n_steps(automaton, state, n):
    """Q4: Returnează numărul de celule de tipul dat după N pași."""
    return _advanced_copy(automaton, n).count_cells(state)


def _grid_to_key(grid):
    return tuple(tuple(row) for row in grid)


def detect_cycle(automaton, max_steps=1000):
    """
    Q5: Detectează intrarea într-un ciclu (o secvență repetitivă de stări).
    Returnează (has_cycle: bool, period: int, start_gen: int, cycle_gen: int).
    """
    sim = automaton.clone()
    history = {_grid_to_key(sim.grid): sim.generation}

    for _ in range(max_steps):
        sim.step()
        key = _grid_to_key(sim.grid)
        if key in history:
            start_gen = history[key]
            period = sim.generation - start_gen
            return True, period, start_gen, sim.generation
        history[key] = sim.generation

    return False, 0, None, None
