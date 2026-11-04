"""
Project CellLab - Graphical User Interface (GUI)
Interfață grafică completă dezvoltată cu Tkinter (Python Standard Library).
Permite simularea interactivă a automatelor celulare:
1. Elementary Cellular Automaton (Rule 30)
2. Brian's Brain (OFF, FIRING, DYING)
3. Cyclic Cellular Automaton (0, 1, 2, 3)
și orice alt automat definit în format JSON.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from cellab_engine import CellularAutomata


class CellLabGUI:
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

    def _scan_available_configs(self):
        """Scanează dinamic fișierele .json din folderul curent și le adaugă în dicționar."""
        configs = {}
        script_dir = os.path.dirname(os.path.abspath(__file__)) if __file__ else "."
        if os.path.exists(script_dir):
            for fname in sorted(os.listdir(script_dir)):
                if fname.endswith(".json") and not fname.endswith("_checkpoint.json"):
                    full_path = os.path.join(script_dir, fname)
                    try:
                        import json
                        with open(full_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if "states" in data and ("transitions" in data or "patterns" in data or "rule_number" in data):
                            name = data.get("name", fname.replace(".json", "").replace("_", " ").title())
                            configs[name] = full_path
                    except Exception:
                        pass
        return configs

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

    # =========================================================================
    # CONSTRUIRE COMPONENTE UI
    # =========================================================================

    def _build_top_panel(self):
        """Bara superioară: selector automat, detalii topologice și legendă."""
        top_frame = ttk.Frame(self.root, padding=(12, 10, 12, 6))
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Dropdown / Selector Automate
        lbl_selector = ttk.Label(top_frame, text="Automat:", font=("Segoe UI", 10, "bold"))
        lbl_selector.pack(side=tk.LEFT, padx=(0, 6))

        self.automaton_var = tk.StringVar(value=self.automata.name)
        self.selector_combo = ttk.Combobox(
            top_frame,
            textvariable=self.automaton_var,
            values=list(self.config_files.keys()),
            state="readonly",
            width=28,
            font=("Segoe UI", 9)
        )
        self.selector_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.selector_combo.bind("<<ComboboxSelected>>", self._on_automaton_changed)

        # Buton încărcare configurație JSON externă
        btn_load_cfg = ttk.Button(top_frame, text="📂 Load JSON...", command=self._load_custom_config)
        btn_load_cfg.pack(side=tk.LEFT, padx=(0, 15))

        # Badge-uri de informare
        self.info_badge = ttk.Label(
            top_frame,
            text="",
            font=("Segoe UI", 9, "italic"),
            foreground="#475569"
        )
        self.info_badge.pack(side=tk.LEFT, padx=5)

        # Legendă stări (dreapta)
        self.legend_frame = ttk.Frame(top_frame)
        self.legend_frame.pack(side=tk.RIGHT)

        self._update_info_badge_and_legend()

    def _build_canvas_panel(self):
        """Zona centrală: Canvas interactiv pentru vizualizarea și editarea grilei."""
        canvas_container = ttk.Frame(self.root, padding=(12, 6, 12, 6))
        canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_container,
            bg="#0F172A",
            width=self.canvas_width,
            height=self.canvas_height,
            highlightthickness=1,
            highlightbackground="#CBD5E1"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Evenimente mouse
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _build_control_panel(self):
        """Bara de acțiuni: Play/Pause, Step, Randomize/Reset, Salvare/Încărcare, Analiză."""
        ctrl_frame = ttk.Frame(self.root, padding=(12, 6, 12, 6))
        ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        # Rândul 1: Controale de rulare
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill=tk.X, pady=(0, 6))

        self.btn_play = tk.Button(
            row1,
            text="▶ Play",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="raised",
            padx=12,
            pady=3,
            command=self.toggle_play_pause
        )
        self.btn_play.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_step = ttk.Button(row1, text="⏭ Next Step", command=self.step_forward)
        self.btn_step.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_randomize = ttk.Button(row1, text="🎲 Randomize / Reset", command=self.randomize_grid)
        self.btn_randomize.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_clear = ttk.Button(row1, text="🧹 Clear Grid", command=self.clear_grid)
        self.btn_clear.pack(side=tk.LEFT, padx=(0, 15))

        # Slider de viteză
        lbl_speed = ttk.Label(row1, text="Interval viteză:")
        lbl_speed.pack(side=tk.LEFT, padx=(0, 5))

        self.speed_scale = ttk.Scale(
            row1,
            from_=20,
            to=500,
            value=self.speed_ms,
            orient=tk.HORIZONTAL,
            length=130,
            command=self._on_speed_changed
        )
        self.speed_scale.pack(side=tk.LEFT, padx=(0, 5))

        self.lbl_speed_val = ttk.Label(row1, text=f"{self.speed_ms} ms", width=7)
        self.lbl_speed_val.pack(side=tk.LEFT)

        # Rândul 2: State Storage & Recovery + Presets + Întrebări Analitice
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill=tk.X)

        btn_save = ttk.Button(row2, text="💾 Save State (JSON)", command=self.save_state_dialog)
        btn_save.pack(side=tk.LEFT, padx=(0, 6))

        btn_load = ttk.Button(row2, text="📂 Load State (JSON)", command=self.load_state_dialog)
        btn_load.pack(side=tk.LEFT, padx=(0, 15))

        # Modele predefinite (Presets)
        lbl_preset = ttk.Label(row2, text="Preset:")
        lbl_preset.pack(side=tk.LEFT, padx=(0, 5))

        self.preset_var = tk.StringVar(value="-- Alege pattern --")
        self.preset_combo = ttk.Combobox(
            row2,
            textvariable=self.preset_var,
            state="readonly",
            width=22
        )
        self.preset_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)
        self._update_preset_options()

        # Buton pentru întrebările proiectului (Analiză)
        btn_analysis = tk.Button(
            row2,
            text="❓ Analiză & Întrebări",
            bg="#0D9488",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="raised",
            padx=10,
            pady=3,
            command=self._open_analysis_dialog
        )
        btn_analysis.pack(side=tk.RIGHT)

    def _build_status_bar(self):
        """Bara de stare inferioară: număr generație, celule active, stări detaliate."""
        status_frame = ttk.Frame(self.root, padding=(12, 6, 12, 8))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_stats = ttk.Label(
            status_frame,
            text="",
            style="Stats.TLabel"
        )
        self.lbl_stats.pack(side=tk.LEFT)

        self.lbl_message = ttk.Label(
            status_frame,
            text="Gata. Click pe celule pentru editare manuală sau apasă Play/Randomize.",
            font=("Segoe UI", 9),
            foreground="#64748B"
        )
        self.lbl_message.pack(side=tk.RIGHT)

    # =========================================================================
    # MANAGEMENTUL CANVASULUI ȘI RANDAREA CULORILOR
    # =========================================================================

    def _get_cell_color(self, state):
        """Determină culoarea stării din fișierul JSON sau atribuie o culoare distinctă."""
        if state in self.automata.colors:
            return self.automata.colors[state]

        default_palette = {
            "0": "#0F172A", "1": "#F59E0B", "2": "#10B981", "3": "#EF4444",
            "OFF": "#0F172A", "FIRING": "#38BDF8", "DYING": "#EF4444",
            "off": "#0F172A", "on": "#38BDF8", "dying": "#EF4444",
            "dead": "#0F172A", "alive": "#4ADE80"
        }
        if state in default_palette:
            return default_palette[state]

        h = abs(hash(str(state))) % 0xFFFFFF
        return f"#{h:06X}"

    def _init_canvas_grid(self):
        """Construiește dreptunghiurile pe Canvas optimizat pentru performanță."""
        self.canvas.delete("all")
        self.cell_rects = []
        self.last_grid_cache = []

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            w = self.canvas_width
            h = self.canvas_height

        rows = self.automata.rows
        cols = self.automata.cols

        if rows == 0 or cols == 0:
            return

        cell_w = max(3, w // cols)
        cell_h = max(3, h // rows)
        self.cell_size = min(cell_w, cell_h)

        self.offset_x = (w - cols * self.cell_size) // 2
        self.offset_y = (h - rows * self.cell_size) // 2

        bg_color = self._get_cell_color(self.automata.dead_state)
        self.canvas.configure(bg=bg_color)
        grid_border_color = "#334155" if bg_color.upper() in ("#0F172A", "#020617", "#000000", "#1E293B") else "#CBD5E1"

        for r in range(rows):
            row_rects = []
            row_cache = []
            for c in range(cols):
                x1 = self.offset_x + c * self.cell_size
                y1 = self.offset_y + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                state = self.automata.grid[r][c]
                color = self._get_cell_color(state)

                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=grid_border_color,
                    width=1
                )
                row_rects.append(rect_id)
                row_cache.append(state)
            self.cell_rects.append(row_rects)
            self.last_grid_cache.append(row_cache)

    def _update_canvas_cells(self):
        """Actualizează doar celulele ale căror stări s-au schimbat (fără flickering)."""
        if len(self.cell_rects) != self.automata.rows or len(self.cell_rects[0]) != self.automata.cols:
            self._init_canvas_grid()
            return

        for r in range(self.automata.rows):
            for c in range(self.automata.cols):
                curr_state = self.automata.grid[r][c]
                if curr_state != self.last_grid_cache[r][c]:
                    color = self._get_cell_color(curr_state)
                    self.canvas.itemconfig(self.cell_rects[r][c], fill=color)
                    self.last_grid_cache[r][c] = curr_state

    def _on_canvas_resize(self, event):
        """Reconstruiește grila când fereastra își modifică dimensiunea."""
        if event.width > 50 and event.height > 50:
            self.canvas_width = event.width
            self.canvas_height = event.height
            self._init_canvas_grid()

    # =========================================================================
    # INTERACȚIUNE MOUSE CU GRILA
    # =========================================================================

    def _coords_to_cell(self, event_x, event_y):
        """Transformă coordonatele pixel în indexul (r, c) din matrice."""
        if not hasattr(self, "cell_size") or self.cell_size <= 0:
            return None, None
        c = (event_x - self.offset_x) // self.cell_size
        r = (event_y - self.offset_y) // self.cell_size
        if 0 <= r < self.automata.rows and 0 <= c < self.automata.cols:
            return int(r), int(c)
        return None, None

    def _on_canvas_click(self, event):
        """Click stânga: ciclează starea celulei."""
        r, c = self._coords_to_cell(event.x, event.y)
        if r is not None and c is not None:
            curr = self.automata.grid[r][c]
            states = self.automata.states
            next_idx = (states.index(curr) + 1) % len(states) if curr in states else 0
            new_state = states[next_idx]

            self.automata.grid[r][c] = new_state
            self.drag_paint_state = new_state
            self.canvas.itemconfig(self.cell_rects[r][c], fill=self._get_cell_color(new_state))
            self.last_grid_cache[r][c] = new_state
            self._update_ui_stats()

    def _on_canvas_drag(self, event):
        """Drag mouse stânga: pictează celulele pe traseu."""
        r, c = self._coords_to_cell(event.x, event.y)
        if r is not None and c is not None and self.drag_paint_state:
            if self.automata.grid[r][c] != self.drag_paint_state:
                self.automata.grid[r][c] = self.drag_paint_state
                self.canvas.itemconfig(self.cell_rects[r][c], fill=self._get_cell_color(self.drag_paint_state))
                self.last_grid_cache[r][c] = self.drag_paint_state
                self._update_ui_stats()

    def _on_canvas_release(self, _event):
        self.drag_paint_state = None

    def _on_canvas_right_click(self, event):
        """Click dreapta: resetează celula la starea inactivă."""
        r, c = self._coords_to_cell(event.x, event.y)
        if r is not None and c is not None:
            dead_state = self.automata.dead_state
            self.automata.grid[r][c] = dead_state
            self.canvas.itemconfig(self.cell_rects[r][c], fill=self._get_cell_color(dead_state))
            self.last_grid_cache[r][c] = dead_state
            self._update_ui_stats()

    # =========================================================================
    # CONTROALE DE SIMULARE (PLAY / PAUSE / STEP / RANDOMIZE)
    # =========================================================================

    def toggle_play_pause(self):
        """Pornește sau oprește bucla automată de simulare."""
        if self.is_running:
            self._pause_simulation()
        else:
            self._start_simulation()

    def _start_simulation(self):
        self.is_running = True
        self.btn_play.configure(text="⏸ Pause", bg="#DC2626")
        self.lbl_message.configure(text="Simulare în rulare...")
        self._simulation_loop()

    def _pause_simulation(self):
        self.is_running = False
        if self.sim_timer_id:
            self.root.after_cancel(self.sim_timer_id)
            self.sim_timer_id = None
        self.btn_play.configure(text="▶ Play", bg="#2563EB")
        self.lbl_message.configure(text="Simulare pusă pe pauză.")

    def _simulation_loop(self):
        """Bucla repetitivă rulată asincron prin Tkinter after."""
        if self.is_running:
            self.automata.step()
            self._update_canvas_cells()
            self._update_ui_stats()
            self.sim_timer_id = self.root.after(self.speed_ms, self._simulation_loop)

    def step_forward(self):
        """Avansează o singură generație."""
        if self.is_running:
            self._pause_simulation()
        self.automata.step()
        self._update_canvas_cells()
        self._update_ui_stats()
        self.lbl_message.configure(text=f"Avansat la generația {self.automata.generation}.")

    def randomize_grid(self):
        """Inițializează grila cu valori aleatorii conform automatului selectat."""
        if self.is_running:
            self._pause_simulation()
        self.automata.generate_random_grid()
        self._init_canvas_grid()
        self._update_ui_stats()
        self.lbl_message.configure(text="Grilă reinițializată.")

    def clear_grid(self):
        """Golește complet grila (toate celulele devin inactive)."""
        if self.is_running:
            self._pause_simulation()
        self.automata.clear_grid()
        self._init_canvas_grid()
        self._update_ui_stats()
        self.lbl_message.configure(text="Grilă curățată.")

    def _on_speed_changed(self, value):
        self.speed_ms = int(float(value))
        self.lbl_speed_val.configure(text=f"{self.speed_ms} ms")

    # =========================================================================
    # SELECTOR AUTOMATE & CONFIGURARE
    # =========================================================================

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
            self.current_config_file = cfg_path

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

    def _update_info_badge_and_legend(self):
        """Afișează neighborhood/type, boundary și legenda de culori."""
        if getattr(self.automata, "is_elementary", False):
            neigh_text = "1D Elementary (Left, Center, Right)"
        else:
            neigh_text = "Moore (8)" if self.automata.neighborhood_type == "moore" else "von Neumann (4)"
        bound_text = "Wrap (toroidal)" if self.automata.boundary == "wrap" else "Bordură fixă"
        self.info_badge.configure(text=f"Tip: {neigh_text}  |  Bordură: {bound_text}")

        for child in self.legend_frame.winfo_children():
            child.destroy()

        for state in self.automata.states:
            color = self._get_cell_color(state)
            item_frame = ttk.Frame(self.legend_frame)
            item_frame.pack(side=tk.LEFT, padx=4)

            color_box = tk.Label(item_frame, bg=color, width=2, height=1, relief="ridge")
            color_box.pack(side=tk.LEFT, padx=(0, 2))

            lbl_name = ttk.Label(item_frame, text=state, font=("Segoe UI", 8))
            lbl_name.pack(side=tk.LEFT)

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
                import random
                self.automata.grid[0] = [random.choice(self.automata.states) for _ in range(self.automata.cols)]

        elif "Brian" in self.automata.name:
            if "Glider" in preset:
                coords = [
                    (r_mid, c_mid, "FIRING"), (r_mid, c_mid + 1, "FIRING"),
                    (r_mid + 1, c_mid - 1, "FIRING"), (r_mid + 1, c_mid + 2, "FIRING"),
                    (r_mid + 2, c_mid, "DYING"), (r_mid + 2, c_mid + 1, "DYING")
                ]
                for r, c, st in coords:
                    if 0 <= r < self.automata.rows and 0 <= c < self.automata.cols:
                        self.automata.grid[r][c] = st
            elif "Oscilator" in preset:
                coords = [
                    (r_mid, c_mid - 1, "FIRING"), (r_mid, c_mid, "FIRING"), (r_mid, c_mid + 1, "OFF"),
                    (r_mid + 1, c_mid - 1, "DYING"), (r_mid + 1, c_mid, "DYING")
                ]
                for r, c, st in coords:
                    if 0 <= r < self.automata.rows and 0 <= c < self.automata.cols:
                        self.automata.grid[r][c] = st
            elif "Pattern Complex" in preset:
                coords = [
                    (r_mid - 1, c_mid, "FIRING"), (r_mid - 1, c_mid + 1, "FIRING"),
                    (r_mid, c_mid - 1, "FIRING"), (r_mid, c_mid + 2, "FIRING"),
                    (r_mid + 1, c_mid, "DYING"), (r_mid + 1, c_mid + 1, "DYING")
                ]
                for r, c, st in coords:
                    if 0 <= r < self.automata.rows and 0 <= c < self.automata.cols:
                        self.automata.grid[r][c] = st

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

    # =========================================================================
    # STATE STORAGE & RECOVERY (JSON)
    # =========================================================================

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

    # =========================================================================
    # STATISTICI ȘI ACTUALIZARE ETICHETE
    # =========================================================================

    def _update_ui_stats(self):
        """Actualizează eticheta cu numărul generației și numărul celulelor active."""
        active_count = self.automata.count_cells()
        state_counts = self.automata.get_state_counts()

        details = ", ".join(f"{s}: {count}" for s, count in state_counts.items())

        stats_text = (
            f"Generația: {self.automata.generation}  |  "
            f"Celule active: {active_count}  |  "
            f"Dimensiuni: {self.automata.rows}x{self.automata.cols}  |  "
            f"Distribuție stări: [{details}]"
        )
        self.lbl_stats.configure(text=stats_text)

    # =========================================================================
    # MODAL PENTRU RĂSPUNSUL LA ÎNTREBĂRILE PROIECTULUI (ANALIZĂ)
    # =========================================================================

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
                    import json
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


def main():
    root = tk.Tk()
    _app = CellLabGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
