"""Dialogurile de salvare și restaurare a stării (JSON)."""

from tkinter import filedialog, messagebox


class StateDialogsMixin:
    """Dialogurile de salvare și restaurare a stării (JSON)."""

    def save_state_dialog(self):
        """State Storage: Salvează starea curentă într-un fișier JSON."""
        if self.is_running:
            self._pause_simulation()

        safe_name = self.automata.name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        initial_name = f"{safe_name}_gen_{self.automata.generation}.json"
        filepath = filedialog.asksaveasfilename(
            title="Salvare Stare Curentă (JSON)",
            defaultextension=".json",
            initialfile=initial_name,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                self.automata.save_state(filepath)
                self.lbl_message.configure(text=f"[Salvat] Generația {self.automata.generation} salvată.")
                messagebox.showinfo("Salvare Reușită", f"Starea curentă (Generația {self.automata.generation}) a fost salvată în:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Eroare la Salvare", str(e))

    def load_state_dialog(self):
        """State Recovery: Încarcă și reia o stare dintr-un fișier JSON salvat anterior."""
        if self.is_running:
            self._pause_simulation()

        filepath = filedialog.askopenfilename(
            title="Încărcare Stare Salvată (JSON)",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                data = self.automata.load_state(filepath)
                saved_automaton = data.get("automaton_name")

                if saved_automaton and saved_automaton != self.automata.name:
                    for name, cfg_file in self.config_files.items():
                        if name.lower() in saved_automaton.lower() or saved_automaton.lower() in name.lower():
                            self._switch_to_config(cfg_file)
                            self.automata.load_state(filepath)
                            break

                self._init_canvas_grid()
                self._update_ui_stats()
                self.lbl_message.configure(text=f"[Restaurat] Reluat cu succes de la Generația {self.automata.generation}.")
                messagebox.showinfo("Restaurare Reușită", f"Simularea a fost restaurată de la Generația {self.automata.generation}.")
            except Exception as e:
                messagebox.showerror("Eroare la Restaurare", str(e))
