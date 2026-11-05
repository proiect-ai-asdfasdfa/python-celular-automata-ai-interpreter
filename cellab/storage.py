"""Salvarea și restaurarea stării unui automat în fișiere JSON."""

import json
from copy import deepcopy


def save_state(automaton, filepath):
    """Salvează starea lumii curente într-un fișier JSON (generație, dimensiuni, nume, matrice)."""
    data = {
        "automaton_name": automaton.name,
        "generation": automaton.generation,
        "rows": automaton.rows,
        "cols": automaton.cols,
        "grid": automaton.grid
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data


def load_state(automaton, filepath):
    """Restaurează o stare salvată anterior și continuă simularea exact de la acea generație."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    automaton.generation = data.get("generation", 0)
    automaton.rows = data.get("rows", len(data.get("grid", [])))
    automaton.cols = data.get("cols", len(data.get("grid", [[]])[0]))
    automaton.grid = deepcopy(data.get("grid", []))
    return data
