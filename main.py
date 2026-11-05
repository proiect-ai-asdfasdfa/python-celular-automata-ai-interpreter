"""
Project CellLab - Punctul Principal de Intrare (Main Entry Point)
Lansează interfața grafică Tkinter sau rulează testele automatizate din linia de comandă.
"""

import sys
import tkinter as tk
from cellab.cli_checks import run_cli_tests
from cellab.gui import CellLabGUI


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "--cli"):
        run_cli_tests()
    else:
        root = tk.Tk()
        _app = CellLabGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
