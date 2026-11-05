"""Randarea grilei pe Canvas și interacțiunea cu mouse-ul."""


class CanvasMixin:
    """Randarea grilei pe Canvas și interacțiunea cu mouse-ul."""

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
