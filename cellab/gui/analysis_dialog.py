"""Fereastra de dialog pentru întrebările analitice ale proiectului (Q1-Q5)."""

import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class AnalysisDialogMixin:
    """Fereastra de dialog pentru întrebările analitice ale proiectului (Q1-Q5)."""

    def _open_analysis_dialog(self):
        """Fereastră de dialog dedicată întrebărilor analitice din proiect."""
        if self.is_running:
            self._pause_simulation()

        dialog = tk.Toplevel(self.root)
        dialog.title("CellLab - Întrebări Analitice Automate")
        dialog.geometry("640x520")
        dialog.transient(self.root)
        dialog.grab_set()

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_iterations_tab(notebook)
        self._build_stability_tab(notebook)
        self._build_cycle_tab(notebook)
        self._build_configuration_tab(notebook, dialog)

    def _build_iterations_tab(self, notebook):
        """Tab-ul pentru Q1 și Q4."""
        # Tab 1: Q1 & Q4 (Iterații N & Numărare)
        tab_iter = ttk.Frame(notebook, padding=12)
        notebook.add(tab_iter, text="Stare & Numărare la N")

        ttk.Label(tab_iter, text="Întrebarea 1 & 4: Analiză după N Iterații", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        frame_n = ttk.Frame(tab_iter)
        frame_n.pack(fill=tk.X, pady=4)
        ttk.Label(frame_n, text="Număr iterații N:").pack(side=tk.LEFT, padx=(0, 6))
        entry_n = ttk.Entry(frame_n, width=8)
        entry_n.insert(0, "10")
        entry_n.pack(side=tk.LEFT)

        frame_state = ttk.Frame(tab_iter)
        frame_state.pack(fill=tk.X, pady=4)
        ttk.Label(frame_state, text="Celule de tipul X:").pack(side=tk.LEFT, padx=(0, 6))
        combo_state = ttk.Combobox(frame_state, values=self.automata.states, state="readonly", width=10)
        combo_state.set(self.automata.states[1] if len(self.automata.states) > 1 else self.automata.states[0])
        combo_state.pack(side=tk.LEFT)

        lbl_iter_result = ttk.Label(tab_iter, text="Apasă 'Calculează' pentru a obține răspunsul.", foreground="#475569")
        lbl_iter_result.pack(anchor=tk.W, pady=10)

        def run_q1_q4():
            try:
                n = int(entry_n.get())
                target_state = combo_state.get()
                count = self.automata.count_cells_after_n_steps(target_state, n)
                _grid, future_gen = self.automata.get_state_after_n_steps(n)
                lbl_iter_result.configure(
                    text=f"[Rezultat Q1 & Q4]\n• Generație viitoare: {future_gen}\n• Număr celule de tip '{target_state}' după {n} iterații: {count}",
                    foreground="#0F172A",
                    font=("Segoe UI", 10, "bold")
                )
            except Exception as ex:
                messagebox.showerror("Eroare", str(ex))

        ttk.Button(tab_iter, text="Calculează Q1 & Q4", command=run_q1_q4).pack(anchor=tk.W)

    def _build_stability_tab(self, notebook):
        """Tab-ul pentru Q2."""
        # Tab 2: Q2 (Stare Stabilă)
        tab_stable = ttk.Frame(notebook, padding=12)
        notebook.add(tab_stable, text="Stare Stabilă (Q2)")

        ttk.Label(tab_stable, text="Întrebarea 2: Când atinge sistemul o stare stabilă?", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(tab_stable, text="O stare este stabilă dacă generația următoare este identică cu cea curentă.").pack(anchor=tk.W, pady=(0, 8))

        frame_stable_limit = ttk.Frame(tab_stable)
        frame_stable_limit.pack(fill=tk.X, pady=4)
        ttk.Label(frame_stable_limit, text="Limită maximă de pași:").pack(side=tk.LEFT, padx=(0, 6))
        entry_stable_max = ttk.Entry(frame_stable_limit, width=8)
        entry_stable_max.insert(0, "500")
        entry_stable_max.pack(side=tk.LEFT)

        lbl_stable_res = ttk.Label(tab_stable, text="Apasă 'Verifică Stabilitate'.", foreground="#475569")
        lbl_stable_res.pack(anchor=tk.W, pady=10)

        def run_q2():
            try:
                max_s = int(entry_stable_max.get())
                is_st, st_gen = self.automata.find_stable_state(max_steps=max_s)
                if is_st:
                    lbl_stable_res.configure(
                        text=f"[Rezultat Q2] Sistemul atinge o stare STABILĂ la generația {st_gen}!\n(Nicio modificare nu va mai surveni).",
                        foreground="#15803D",
                        font=("Segoe UI", 10, "bold")
                    )
                else:
                    lbl_stable_res.configure(
                        text=f"[Rezultat Q2] Sistemul NU a atins o stare stabilă în limita a {max_s} generații.",
                        foreground="#B91C1C",
                        font=("Segoe UI", 10, "bold")
                    )
            except Exception as ex:
                messagebox.showerror("Eroare", str(ex))

        ttk.Button(tab_stable, text="Verifică Stabilitate Q2", command=run_q2).pack(anchor=tk.W)

    def _build_cycle_tab(self, notebook):
        """Tab-ul pentru Q5."""
        # Tab 3: Q5 (Detecție Ciclu)
        tab_cycle = ttk.Frame(notebook, padding=12)
        notebook.add(tab_cycle, text="Detecție Ciclu (Q5)")

        ttk.Label(tab_cycle, text="Întrebarea 5: Intră simularea într-un ciclu repetitiv?", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(tab_cycle, text="Detectează oscilatori și cicluri periodice comparând amprenta matricelor.").pack(anchor=tk.W, pady=(0, 8))

        frame_cycle_limit = ttk.Frame(tab_cycle)
        frame_cycle_limit.pack(fill=tk.X, pady=4)
        ttk.Label(frame_cycle_limit, text="Limită maximă de pași:").pack(side=tk.LEFT, padx=(0, 6))
        entry_cycle_max = ttk.Entry(frame_cycle_limit, width=8)
        entry_cycle_max.insert(0, "500")
        entry_cycle_max.pack(side=tk.LEFT)

        lbl_cycle_res = ttk.Label(tab_cycle, text="Apasă 'Detectează Ciclu'.", foreground="#475569")
        lbl_cycle_res.pack(anchor=tk.W, pady=10)

        def run_q5():
            try:
                max_s = int(entry_cycle_max.get())
                has_c, period, s_gen, c_gen = self.automata.detect_cycle(max_steps=max_s)
                if has_c:
                    lbl_cycle_res.configure(
                        text=f"[Rezultat Q5] CICLU DETECTAT!\n• Perioada ciclului: {period}\n• Ciclul a început la generația: {s_gen}\n• Repetarea a fost confirmată la generația: {c_gen}",
                        foreground="#15803D",
                        font=("Segoe UI", 10, "bold")
                    )
                else:
                    lbl_cycle_res.configure(
                        text=f"[Rezultat Q5] Nu s-a detectat niciun ciclu repetitiv în limita a {max_s} pași.",
                        foreground="#B91C1C",
                        font=("Segoe UI", 10, "bold")
                    )
            except Exception as ex:
                messagebox.showerror("Eroare", str(ex))

        ttk.Button(tab_cycle, text="Detectează Ciclu Q5", command=run_q5).pack(anchor=tk.W)

    def _build_configuration_tab(self, notebook, dialog):
        """Tab-ul pentru Q3."""
        # Tab 4: Q3 (Apariție Configurație)
        tab_cfg = ttk.Frame(notebook, padding=12)
        notebook.add(tab_cfg, text="Verificare Configurație (Q3)")

        ttk.Label(tab_cfg, text="Întrebarea 3: Apare vreodată o anumită configurație?", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 8))
        lbl_target_path = ttk.Label(tab_cfg, text="Niciun fișier țintă selectat.", foreground="#64748B")
        lbl_target_path.pack(anchor=tk.W, pady=4)

        target_grid_holder = {"grid": None}

        def pick_target_file():
            fp = filedialog.askopenfilename(parent=dialog, filetypes=[("JSON Files", "*.json")])
            if fp:
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        d = json.load(f)
                    target_grid_holder["grid"] = d["grid"]
                    lbl_target_path.configure(text=f"Fișier țintă: {os.path.basename(fp)} ({len(d['grid'])}x{len(d['grid'][0])})", foreground="#0F172A")
                except Exception as err:
                    messagebox.showerror("Eroare", str(err))

        ttk.Button(tab_cfg, text="Alege Configurație Țintă (JSON)...", command=pick_target_file).pack(anchor=tk.W, pady=4)

        lbl_cfg_res = ttk.Label(tab_cfg, text="", foreground="#475569")
        lbl_cfg_res.pack(anchor=tk.W, pady=10)

        def run_q3():
            if not target_grid_holder["grid"]:
                messagebox.showwarning("Atenție", "Te rog alege mai întâi un fișier JSON țintă.")
                return
            found, gen = self.automata.does_configuration_occur(target_grid_holder["grid"], max_steps=500)
            if found:
                lbl_cfg_res.configure(
                    text=f"[Rezultat Q3] Configurația apare la generația {gen}!",
                    foreground="#15803D",
                    font=("Segoe UI", 10, "bold")
                )
            else:
                lbl_cfg_res.configure(
                    text="[Rezultat Q3] Configurația NU apare în următoarele 500 de generații.",
                    foreground="#B91C1C",
                    font=("Segoe UI", 10, "bold")
                )

        ttk.Button(tab_cfg, text="Verifică Configurația Q3", command=run_q3).pack(anchor=tk.W)
