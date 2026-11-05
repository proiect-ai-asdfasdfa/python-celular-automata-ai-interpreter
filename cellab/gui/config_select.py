"""Descoperirea configurațiilor JSON și schimbarea automatului curent."""

import json
import os
from tkinter import filedialog, messagebox

from cellab.automaton import CellularAutomata
from cellab.paths import PROJECT_ROOT


class ConfigSelectMixin:
    """Descoperirea configurațiilor JSON și schimbarea automatului curent."""

    def _scan_available_configs(self):
        """Scanează dinamic fișierele .json din rădăcina proiectului și le adaugă în dicționar."""
        configs = {}
        for fname in sorted(os.listdir(PROJECT_ROOT)):
            if fname.endswith(".json") and not fname.endswith("_checkpoint.json"):
                full_path = os.path.join(PROJECT_ROOT, fname)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if "states" in data and ("transitions" in data or "patterns" in data or "rule_number" in data):
                        name = data.get("name", fname.replace(".json", "").replace("_", " ").title())
                        configs[name] = full_path
                except Exception:
                    pass
        return configs

    def _on_automaton_changed(self, _event=None):
        """Schimbă automatul pe baza alegerii din Dropdown."""
        selected_name = self.automaton_var.get()
        if selected_name in self.config_files:
            cfg_file = self.config_files[selected_name]
            self._switch_to_config(cfg_file)

    def _switch_to_config(self, cfg_path):
        """Încarcă un nou automat dintr-o cale JSON."""
        if self.is_running:
            self._pause_simulation()

        try:
            self.automata = CellularAutomata(cfg_path)

            if self.automata.name not in self.config_files:
                self.config_files[self.automata.name] = cfg_path
                self.selector_combo.configure(values=list(self.config_files.keys()))

            self.automaton_var.set(self.automata.name)
            self._update_info_badge_and_legend()
            self._update_preset_options()
            self._init_canvas_grid()
            self._update_ui_stats()
            self.lbl_message.configure(text=f"Automat încărcat: {self.automata.name}")
        except Exception as e:
            messagebox.showerror("Eroare la încărcarea configurației", str(e))

    def _load_custom_config(self):
        """Permite încărcarea oricărui fișier JSON definit de utilizator."""
        filepath = filedialog.askopenfilename(
            title="Alege fișier de configurare automat (JSON)",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filepath:
            self._switch_to_config(filepath)
