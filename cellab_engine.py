"""
Project CellLab - Engine
Motor generic de simulare pentru automate celulare 2D.
Regulile, dimensiunile, topologia de vecinătate și stările sunt încărcate complet din fișiere JSON.
"""

import json
import random
from copy import deepcopy


class CellularAutomata:
    """
    Simulator generic de automate celulare bidimensionale.
    Permite orice număr de stări, tipuri de vecinătate (Moore, von Neumann),
    condiții de bordură (wrap/toroidal, fixed/dead) și tranziții bazate pe reguli.
    """

    def __init__(self, config_source):
        """
        Inițializează automatul fie dintr-o cale către un fișier JSON,
        fie direct dintr-un dicționar de configurare.
        """
        if isinstance(config_source, str):
            self.config_path = config_source
            with open(config_source, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        elif isinstance(config_source, dict):
            self.config_path = None
            self.config = deepcopy(config_source)
        else:
            raise ValueError("config_source trebuie să fie o cale (str) sau un dicționar (dict).")

        self.name = self.config.get("name", "Generic Cellular Automaton")
        self.neighborhood_type = self.config.get("neighborhood", "moore").lower()
        self.boundary = self.config.get("boundary", "wrap").lower()
        self.states = self.config.get("states", [])
        self.dead_state = self.config.get("dead_state", self.states[0] if self.states else "dead")
        self.symbols = self.config.get("symbols", {})
        self.colors = self.config.get("colors", {})
        self.active_states = self.config.get("active_states", [s for s in self.states if s != self.dead_state])
        self.transitions = self.config.get("transitions", [])

        # Dimensiuni implicite
        default_rows = self.config.get("default_rows", 25)
        default_cols = self.config.get("default_cols", 25)

        self.rows = default_rows
        self.cols = default_cols
        self.generation = 0
        self.grid = []

        # Inițializează o grilă goală (inactivă)
        self.clear_grid(default_rows, default_cols)

    def set_grid(self, grid, generation=0):
        """Setează manual starea grilei (util pentru teste unitare sau pattern-uri specifice)."""
        if not grid or not grid[0]:
            raise ValueError("Grila nu poate fi goală.")
        self.grid = deepcopy(grid)
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.generation = generation

    def clear_grid(self, rows=None, cols=None, state=None):
        """Resetează grila la o stare unică (de regulă starea inactivă / dead / off)."""
        if rows is not None:
            self.rows = rows
        if cols is not None:
            self.cols = cols
        fill_state = state or self.dead_state
        self.grid = [[fill_state for _ in range(self.cols)] for _ in range(self.rows)]
        self.generation = 0

    def generate_random_grid(self, rows=None, cols=None, probabilities=None):
        """
        Generează o stare inițială aleatorie conform probabilităților specificate
        sau configurate implicit în fișierul JSON.
        """
        if rows is not None:
            self.rows = rows
        if cols is not None:
            self.cols = cols
        self.generation = 0

        probs = probabilities or self.config.get("default_probabilities")

        if probs and len(probs) == len(self.states):
            self.grid = [
                random.choices(self.states, weights=probs, k=self.cols)
                for _ in range(self.rows)
            ]
        else:
            self.grid = [
                [random.choice(self.states) for _ in range(self.cols)]
                for _ in range(self.rows)
            ]

    def _get_neighbors(self, r, c):
        """
        Calculează frecvența stărilor vecinilor pentru celula (r, c).
        Suportă cartier Moore (8 vecini) și von Neumann (4 vecini),
        precum și bordură toroidală (wrap) sau fixă (fixed/dead).
        """
        if self.neighborhood_type == "moore":
            offsets = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
        else:  # von Neumann (4 vecini ortogonali)
            offsets = [
                (-1, 0),
                (0, -1), (0, 1),
                (1, 0)
            ]

        neighbor_counts = {state: 0 for state in self.states}

        for dr, dc in offsets:
            nr, nc = r + dr, c + dc

            if self.boundary == "wrap":
                nr %= self.rows
                nc %= self.cols
                neighbor_state = self.grid[nr][nc]
                neighbor_counts[neighbor_state] = neighbor_counts.get(neighbor_state, 0) + 1
            else:
                # Bordură fixă (celulele din afara matricei sunt tratate ca dead_state)
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbor_state = self.grid[nr][nc]
                    neighbor_counts[neighbor_state] = neighbor_counts.get(neighbor_state, 0) + 1
                else:
                    neighbor_counts[self.dead_state] = neighbor_counts.get(self.dead_state, 0) + 1

        return neighbor_counts

    def step(self):
        """
        Calculează și aplică tranzițiile de stare pentru toți indivizii,
        avansând universul cu exact o generație.
        """
        new_grid = [[self.grid[r][c] for c in range(self.cols)] for r in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                current_state = self.grid[r][c]
                neighbor_counts = self._get_neighbors(r, c)

                # Caută prima regulă compatibilă din lista de tranziții
                for rule in self.transitions:
                    if rule.get("current_state") == current_state:
                        target_counts = rule.get("counts")
                        req_neighbor = rule.get("neighbor_state")

                        # Regula necondiționată (ex: starea "on" trece necondiționat în "dying")
                        if target_counts == "any":
                            new_grid[r][c] = rule["next_state"]
                            break

                        # Regula condiționată de numărul de vecini de un anumit tip
                        elif req_neighbor:
                            counts_list = [target_counts] if isinstance(target_counts, int) else target_counts
                            if counts_list is not None and neighbor_counts.get(req_neighbor, 0) in counts_list:
                                new_grid[r][c] = rule["next_state"]
                                break

        self.grid = new_grid
        self.generation += 1

    def run_simulation(self, steps, verbose=True):
        """Rulează simularea pentru un număr dat de iterații."""
        if verbose:
            print(f"\n--- Stare Inițială (Generația {self.generation}) ---")
            self.display()

        for _ in range(steps):
            self.step()
            if verbose:
                print(f"\n--- Generația {self.generation} ---")
                self.display()

    def count_cells(self, state=None):
        """
        Numără celulele dintr-o anumită stare.
        Dacă state=None, returnează numărul total de celule considerate active.
        """
        if state is not None:
            return sum(row.count(state) for row in self.grid)
        active_set = set(self.active_states)
        return sum(1 for row in self.grid for cell in row if cell in active_set)

    def get_state_counts(self):
        """Returnează un dicționar cu distribuția curentă a tuturor stărilor."""
        counts = {s: 0 for s in self.states}
        for row in self.grid:
            for cell in row:
                counts[cell] = counts.get(cell, 0) + 1
        return counts

    def display(self):
        """Afișează matricea formatată în consolă folosind simbolurile din configurație."""
        for row in self.grid:
            line = "".join(self.symbols.get(cell, cell + " ") for cell in row)
            print(line)

    def save_state(self, filepath):
        """
        State Storage:
        Salvează starea lumii curente într-un fișier JSON (generație, dimensiuni, nume, matrice).
        """
        data = {
            "automaton_name": self.name,
            "generation": self.generation,
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data

    def load_state(self, filepath):
        """
        State Recovery:
        Restaurează o stare salvată anterior și continuă simularea exact de la acea generație.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.generation = data.get("generation", 0)
        self.rows = data.get("rows", len(data.get("grid", [])))
        self.cols = data.get("cols", len(data.get("grid", [[]])[0]))
        self.grid = deepcopy(data.get("grid", []))
        return data

    def clone(self):
        """Creează o copie identică a automatului pentru analize și predicții fără a afecta starea curentă."""
        cloned = CellularAutomata(self.config)
        cloned.rows = self.rows
        cloned.cols = self.cols
        cloned.generation = self.generation
        cloned.grid = deepcopy(self.grid)
        return cloned

    # =========================================================================
    # METODE DE ANALIZĂ ȘI RĂSPUNS LA ÎNTREBĂRILE PROIECTULUI
    # =========================================================================

    def get_state_after_n_steps(self, n):
        """
        Întrebarea 1: Care este starea după N iterații?
        Returnează matricea stării după N pași fără a modifica starea curentă.
        """
        sim = self.clone()
        for _ in range(n):
            sim.step()
        return sim.grid, sim.generation

    def find_stable_state(self, max_steps=1000):
        """
        Întrebarea 2: Când atinge sistemul o stare stabilă? (nicio schimbare pe viitor)
        Returnează (True, generație) dacă a atins stabilitate, altfel (False, None).
        """
        sim = self.clone()
        for step_idx in range(max_steps):
            prev_grid = deepcopy(sim.grid)
            sim.step()
            if sim.grid == prev_grid:
                return True, sim.generation
        return False, None

    def does_configuration_occur(self, target_grid, max_steps=1000):
        """
        Întrebarea 3: Apare vreodată o anumită configurație?
        Returnează (True, generație) dacă matricea target apare în intervalul dat.
        """
        sim = self.clone()
        if sim.grid == target_grid:
            return True, sim.generation

        for _ in range(max_steps):
            sim.step()
            if sim.grid == target_grid:
                return True, sim.generation
        return False, None

    def count_cells_after_n_steps(self, state, n):
        """
        Întrebarea 4: Câte celule de tipul X există după N iterații?
        """
        sim = self.clone()
        for _ in range(n):
            sim.step()
        return sim.count_cells(state)

    def detect_cycle(self, max_steps=1000):
        """
        Întrebarea 5: Intră simularea într-un ciclu? (o secvență repetitivă de stări)
        Returnează:
          (has_cycle: bool, period: int, start_gen: int, cycle_gen: int)
        """
        sim = self.clone()

        def grid_to_key(grid):
            return tuple(tuple(row) for row in grid)

        history = {grid_to_key(sim.grid): sim.generation}

        for _ in range(max_steps):
            sim.step()
            key = grid_to_key(sim.grid)
            if key in history:
                start_gen = history[key]
                period = sim.generation - start_gen
                return True, period, start_gen, sim.generation
            history[key] = sim.generation

        return False, 0, None, None


# =========================================================================
# TESTARE ȘI VERIFICARE CLI (DELIVERABLE 2)
# =========================================================================
if __name__ == "__main__":
    print("==================================================")
    print("DEMO TEST 1: Conway's Game of Life (Oscilator Blinker)")
    print("==================================================")

    conway = CellularAutomata("conway.json")
    blinker_grid = [
        ["dead", "dead", "dead", "dead", "dead"],
        ["dead", "dead", "dead", "dead", "dead"],
        ["dead", "alive", "alive", "alive", "dead"],
        ["dead", "dead", "dead", "dead", "dead"],
        ["dead", "dead", "dead", "dead", "dead"]
    ]
    conway.set_grid(blinker_grid)

    print("\n--- Rulare 2 pași ---")
    conway.run_simulation(steps=2, verbose=True)

    # Test State Storage
    checkpoint_file = "conway_checkpoint.json"
    conway.save_state(checkpoint_file)

    # Test State Recovery
    print("\n--- Testare State Recovery ---")
    conway_resumed = CellularAutomata("conway.json")
    conway_resumed.load_state(checkpoint_file)
    print("Continuare pas următor după recovery:")
    conway_resumed.run_simulation(steps=1, verbose=True)

    # Testare Întrebări Analitice
    print("\n--- Testare Răspuns la Întrebările Proiectului ---")
    has_cycle, period, start_gen, cycle_gen = conway.detect_cycle(max_steps=50)
    print(f"[Q5 - Ciclu] Oscilatorul Blinker detectat ca ciclu? {has_cycle} (Perioadă: {period}, de la Gen {start_gen} la Gen {cycle_gen})")

    alive_after_5 = conway.count_cells_after_n_steps("alive", 5)
    print(f"[Q4 - Numărare celule] Celule 'alive' după 5 iterații: {alive_after_5}")

    is_stable, stable_gen = conway.find_stable_state(max_steps=20)
    print(f"[Q2 - Stabilitate] Este Blinker stabil (fără nicio mișcare)? {is_stable}")

    print("\n==================================================")
    print("DEMO TEST 2: Brian's Brain")
    print("==================================================")
    brain = CellularAutomata("brians_brain.json")
    brain_test_grid = [
        ["off", "off", "off", "off", "off"],
        ["off", "on",  "on",  "off", "off"],
        ["off", "off", "off", "off", "off"],
        ["off", "off", "off", "off", "off"],
        ["off", "off", "off", "off", "off"]
    ]
    brain.set_grid(brain_test_grid)
    brain.run_simulation(steps=2, verbose=True)
    print(f"Număr celule active: {brain.count_cells()} (on/dying)")
    print("\nToate testele de bază au rulat cu succes!")

    print(f"Număr celule active: {brain.count_cells()} (on/dying)")
    print("\nToate testele de bază au rulat cu succes!")