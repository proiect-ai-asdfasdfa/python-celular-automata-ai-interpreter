"""Teste scurte și ușor de citit, pe rezultate cunoscute ale automatelor."""

import os
import tempfile
import unittest

from cellab_engine import CellularAutomata

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GAME_OF_LIFE = {
    "name": "Game of Life",
    "neighborhood": "moore",
    "boundary": "wrap",
    "states": ["dead", "alive"],
    "dead_state": "dead",
    "transitions": [
        {"current_state": "alive", "neighbor_state": "alive", "counts": [2, 3], "next_state": "alive"},
        {"current_state": "alive", "counts": "any", "next_state": "dead"},
        {"current_state": "dead", "neighbor_state": "alive", "counts": [3], "next_state": "alive"},
    ],
}


def config(name):
    return os.path.join(PROJECT_DIR, name)


def blinker():
    grid = [["dead"] * 5 for _ in range(5)]
    for r in (1, 2, 3):
        grid[r][2] = "alive"
    return grid


class KnownResultsTests(unittest.TestCase):
    def test_rule30_first_generation(self):
        ca = CellularAutomata(config("elementary_rule30.json"))
        grid = [["0"] * 11 for _ in range(5)]
        grid[0][5] = "1"
        ca.set_grid(grid)
        ca.step()
        self.assertEqual("".join(ca.grid[1]), "00001110000")

    def test_game_of_life_blinker_has_period_2(self):
        ca = CellularAutomata(GAME_OF_LIFE)
        ca.set_grid(blinker())
        self.assertEqual(ca.detect_cycle(max_steps=10), (True, 2, 0, 2))
        self.assertEqual(ca.find_stable_state(max_steps=10), (False, None))
        self.assertEqual(ca.count_cells_after_n_steps("alive", 5), 3)

    def test_brians_brain_transitions(self):
        ca = CellularAutomata(config("brians_brain.json"))
        grid = [["OFF"] * 5 for _ in range(5)]
        grid[1][1] = grid[1][2] = "FIRING"
        ca.set_grid(grid)
        ca.step()
        self.assertEqual(ca.grid[1][1], "DYING")
        self.assertEqual(ca.grid[1][2], "DYING")
        self.assertEqual(ca.grid[0][1], "FIRING")

    def test_analysis_does_not_change_current_state(self):
        ca = CellularAutomata(GAME_OF_LIFE)
        ca.set_grid(blinker())
        ca.get_state_after_n_steps(3)
        self.assertEqual(ca.grid, blinker())
        self.assertEqual(ca.generation, 0)

    def test_save_and_load_round_trip(self):
        ca = CellularAutomata(config("cyclic_ca.json"))
        ca.step()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "state.json")
            ca.save_state(path)
            restored = CellularAutomata(config("cyclic_ca.json"))
            restored.load_state(path)
        self.assertEqual(restored.grid, ca.grid)
        self.assertEqual(restored.generation, 1)


if __name__ == "__main__":
    unittest.main()
