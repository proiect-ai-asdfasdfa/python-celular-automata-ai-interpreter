"""
Project CellLab - Engine
Alias de compatibilitate: motorul se află acum în pachetul `cellab`.
Importul `from cellab_engine import CellularAutomata` funcționează în continuare.
"""

from cellab.automaton import CellularAutomata
from cellab.cli_checks import run_engine_demo

__all__ = ["CellularAutomata"]


if __name__ == "__main__":
    run_engine_demo()
