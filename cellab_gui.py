"""
Project CellLab - Graphical User Interface (GUI)
Alias de compatibilitate: interfața se află acum în pachetul `cellab.gui`.
Importul `from cellab_gui import CellLabGUI` și comanda `python cellab_gui.py` funcționează în continuare.
"""

from cellab.gui import CellLabGUI, main

__all__ = ["CellLabGUI", "main"]


if __name__ == "__main__":
    main()
