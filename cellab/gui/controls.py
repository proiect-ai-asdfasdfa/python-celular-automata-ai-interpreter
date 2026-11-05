"""Controalele de simulare: play/pause, pas, randomize, clear, viteză."""


class ControlsMixin:
    """Controalele de simulare: play/pause, pas, randomize, clear, viteză."""

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
