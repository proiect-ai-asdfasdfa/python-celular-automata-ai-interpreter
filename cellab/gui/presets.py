"""Modelele predefinite (presets) pentru fiecare automat."""

import random


class PresetsMixin:
    """Modelele predefinite (presets) pentru fiecare automat."""

    def _update_preset_options(self):
        """Actualizează lista de pattern-uri cunoscute în funcție de automat."""
        if "Elementary" in self.automata.name or getattr(self.automata, "is_elementary", False):
            presets = ["-- Alege pattern --", "Single Center Seed (0..010..0)", "Random Row Seed", "Two Center Seeds (11)"]
        elif "Brian" in self.automata.name:
            presets = ["-- Alege pattern --", "Oscilator simplu", "Glider (Spaceship)", "Pattern Complex"]
        elif "Cyclic" in self.automata.name:
            presets = ["-- Alege pattern --", "Grilă Aleatorie (Spirale)", "Punct Central (Valuri)"]
        else:
            presets = ["-- Alege pattern --"]

        self.preset_combo.configure(values=presets)
        self.preset_var.set(presets[0])

    def _on_preset_selected(self, _event=None):
        """Desenează un preset în grilă."""
        preset = self.preset_var.get()
        if preset.startswith("--"):
            return

        if self.is_running:
            self._pause_simulation()

        self.automata.clear_grid()
        r_mid = self.automata.rows // 2
        c_mid = self.automata.cols // 2

        if "Elementary" in self.automata.name or getattr(self.automata, "is_elementary", False):
            if "Single Center" in preset:
                self.automata.grid[0][c_mid] = "1"
            elif "Two Center" in preset:
                self.automata.grid[0][c_mid] = "1"
                if c_mid + 1 < self.automata.cols:
                    self.automata.grid[0][c_mid + 1] = "1"
            elif "Random Row" in preset:
                self.automata.grid[0] = [random.choice(self.automata.states) for _ in range(self.automata.cols)]

        elif "Brian" in self.automata.name:
            if "Glider" in preset:
                coords = [
                    (r_mid, c_mid, "FIRING"), (r_mid, c_mid + 1, "FIRING"),
                    (r_mid + 1, c_mid - 1, "FIRING"), (r_mid + 1, c_mid + 2, "FIRING"),
                    (r_mid + 2, c_mid, "DYING"), (r_mid + 2, c_mid + 1, "DYING")
                ]
                self._paint_cells(coords)
            elif "Oscilator" in preset:
                coords = [
                    (r_mid, c_mid - 1, "FIRING"), (r_mid, c_mid, "FIRING"), (r_mid, c_mid + 1, "OFF"),
                    (r_mid + 1, c_mid - 1, "DYING"), (r_mid + 1, c_mid, "DYING")
                ]
                self._paint_cells(coords)
            elif "Pattern Complex" in preset:
                coords = [
                    (r_mid - 1, c_mid, "FIRING"), (r_mid - 1, c_mid + 1, "FIRING"),
                    (r_mid, c_mid - 1, "FIRING"), (r_mid, c_mid + 2, "FIRING"),
                    (r_mid + 1, c_mid, "DYING"), (r_mid + 1, c_mid + 1, "DYING")
                ]
                self._paint_cells(coords)

        elif "Cyclic" in self.automata.name:
            if "Grilă Aleatorie" in preset:
                self.automata.generate_random_grid()
            elif "Punct Central" in preset:
                self.automata.clear_grid(state="0")
                if 0 <= r_mid < self.automata.rows and 0 <= c_mid < self.automata.cols:
                    self.automata.grid[r_mid][c_mid] = "1"
                    if r_mid + 1 < self.automata.rows:
                        self.automata.grid[r_mid + 1][c_mid] = "1"
                    if c_mid + 1 < self.automata.cols:
                        self.automata.grid[r_mid][c_mid + 1] = "1"

        self._init_canvas_grid()
        self._update_ui_stats()
        self.lbl_message.configure(text=f"Preset aplicat: {preset}")

    def _paint_cells(self, coords):
        """Setează stările (r, c, stare), ignorând coordonatele din afara grilei."""
        for r, c, st in coords:
            if 0 <= r < self.automata.rows and 0 <= c < self.automata.cols:
                self.automata.grid[r][c] = st
