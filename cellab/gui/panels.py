"""Construirea panourilor ferestrei principale și actualizarea etichetelor."""

import tkinter as tk
from tkinter import ttk


class PanelsMixin:
    """Construirea panourilor ferestrei principale și actualizarea etichetelor."""

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
