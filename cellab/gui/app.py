"""
Project CellLab - Graphical User Interface (GUI)
Interfață grafică completă dezvoltată cu Tkinter (Python Standard Library).
Permite simularea interactivă a automatelor celulare:
1. Elementary Cellular Automaton (Rule 30)
2. Brian's Brain (OFF, FIRING, DYING)
3. Cyclic Cellular Automaton (0, 1, 2, 3)
și orice alt automat definit în format JSON.
"""

import tkinter as tk
from tkinter import ttk

from cellab.automaton import CellularAutomata
from cellab.gui.analysis_dialog import AnalysisDialogMixin
from cellab.gui.canvas import CanvasMixin
from cellab.gui.config_select import ConfigSelectMixin
from cellab.gui.controls import ControlsMixin
from cellab.gui.panels import PanelsMixin
from cellab.gui.presets import PresetsMixin
from cellab.gui.state_dialogs import StateDialogsMixin


class CellLabGUI(
    PanelsMixin,
    CanvasMixin,
    ControlsMixin,
    ConfigSelectMixin,
    PresetsMixin,
    StateDialogsMixin,
    AnalysisDialogMixin,
):
    """Aplicație GUI pentru simularea automatelor celulare."""

    def __init__(self, root):
        self.root = root
        self.root.title("Project CellLab - Cellular Automata Simulator")
        self.root.geometry("940x840")
        self.root.minsize(780, 700)

        # Stare simulare
        self.is_running = False
        self.sim_timer_id = None
        self.speed_ms = 120  # interval de rulare implicit

        # Date grafice Canvas
        self.canvas_width = 640
        self.canvas_height = 580
        self.cell_rects = []
        self.last_grid_cache = []
        self.drag_paint_state = None

        # Descoperire automată a tuturor fișierelor de configurare din folder
        self.config_files = self._scan_available_configs()

        # Prioritate automat inițial: Rule 30 sau Brian's Brain
        default_choice = None
        for preferred in ("Elementary Cellular Automaton (Rule 30)", "Brian's Brain", "Cyclic Cellular Automaton"):
            if preferred in self.config_files:
                default_choice = preferred
                break
        if not default_choice and self.config_files:
            default_choice = list(self.config_files.keys())[0]

        self.current_config_file = self.config_files.get(default_choice, "brians_brain.json")
        self.automata = CellularAutomata(self.current_config_file)

        # Construire interfață
        self._apply_theme()
        self._build_top_panel()
        self._build_canvas_panel()
        self._build_control_panel()
        self._build_status_bar()

        # Desenare inițială
        self._init_canvas_grid()
        self._update_ui_stats()

    def _apply_theme(self):
        """Configurează stilurile TTK pentru un aspect curat și modern."""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.configure(bg="#F1F5F9")
        style.configure("TFrame", background="#F1F5F9")
        style.configure("TLabel", background="#F1F5F9", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"), foreground="#0F172A")
        style.configure("Stats.TLabel", font=("Segoe UI", 10, "bold"), foreground="#1E293B")
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=5)
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), foreground="#FFFFFF", background="#2563EB")
        style.configure("Stop.TButton", font=("Segoe UI", 10, "bold"), foreground="#FFFFFF", background="#DC2626")


def main():
    root = tk.Tk()
    _app = CellLabGUI(root)
    root.mainloop()
