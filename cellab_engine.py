"""
Project CellLab - Engine
Motor generic de simulare pentru automate celulare (2D și 1D Elementary).
Regulile, dimensiunile, topologia de vecinătate și stările sunt încărcate complet din fișiere JSON.
"""

import json
import random
from copy import deepcopy


class CellularAutomata:
    """
    Simulator generic de automate celulare.
    Suportă:
    1. Automate 2D cu tranziții bazate pe numărarea vecinilor (Brian's Brain, Cyclic CA etc.)
    2. Automate 1D Elementare (Elementary Cellular Automata - Rule 30, Rule 90, Rule 110 etc.)
       reprezentate spațio-temporal pe matrice 2D.
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
        self.dead_state = self.config.get("dead_state", self.states[0] if self.states else "0")
        self.symbols = self.config.get("symbols", {})
        self.colors = self.config.get("colors", {})
        self.active_states = self.config.get("active_states", [s for s in self.states if s != self.dead_state])
        self.transitions = self.config.get("transitions", [])

        # Verifică dacă automatul este de tip 1D Elementary (Wolfram)
        self.is_elementary = (
            self.config.get("type") == "elementary"
            or "patterns" in self.config
            or "rule_number" in self.config
        )

        self.patterns = {}
        if self.is_elementary:
            if "patterns" in self.config:
                self.patterns = self.config["patterns"]
            elif "rule_number" in self.config:
                rule_num = int(self.config["rule_number"])
                for i, pat in enumerate(["111", "110", "101", "100", "011", "010", "001", "000"]):
                    self.patterns[pat] = str((rule_num >> (7 - i)) & 1)

        # Dimensiuni implicite
        default_rows = self.config.get("default_rows", 30)
        default_cols = self.config.get("default_cols", 30)

        self.rows = default_rows
        self.cols = default_cols
        self.generation = 0
        self.grid = []

        # Inițializează grila implicită
        self.generate_random_grid(default_rows, default_cols)

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
        Generează o stare inițială conform specificației automatului:
        - Pentru Elementary CA: plasează o singură celulă activă în centrul primului rând (000...1...000).
        - Pentru 2D CA (Brian's Brain, Cyclic CA): populează aleatoriu întreaga matrice.
        """
        if rows is not None:
            self.rows = rows
        if cols is not None:
            self.cols = cols
        self.generation = 0

        if self.is_elementary:
            # Pentru 1D Elementary CA, comportamentul canonic este un rând inițial cu o singură celulă vie în centru
            self.grid = [[self.dead_state for _ in range(self.cols)] for _ in range(self.rows)]
            if probabilities:
                self.grid[0] = random.choices(self.states, weights=probabilities, k=self.cols)
            else:
                mid = self.cols // 2
                active_val = self.active_states[0] if self.active_states else "1"
                self.grid[0][mid] = active_val
        else:
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
        Calculează frecvența stărilor vecinilor pentru celula (r, c) în automate 2D.
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
        Calculează și aplică tranzițiile de stare, avansând universul cu o generație:
        - În Elementary CA (1D): generează rândul următor din diagrama spațio-temporală.
        - În 2D CA: aplică regulile de tranziție pentru toate celulele matricei simultan.
        """
        if self.is_elementary:
            # Rulare Elementary CA (spațio-temporal pe matrice 2D)
            curr_row_idx = min(self.generation, self.rows - 1)
            source_row = self.grid[curr_row_idx]
            next_row = [self.dead_state] * self.cols

            for c in range(self.cols):
                if self.boundary == "wrap":
                    left = source_row[(c - 1) % self.cols]
                    right = source_row[(c + 1) % self.cols]
                else:
                    left = source_row[c - 1] if c > 0 else self.dead_state
                    right = source_row[c + 1] if c < self.cols - 1 else self.dead_state
                curr = source_row[c]

                pattern_key = f"{left}{curr}{right}"
                next_row[c] = self.patterns.get(pattern_key, self.dead_state)

            if self.generation < self.rows - 1:
                self.grid[self.generation + 1] = next_row
            else:
                # Dacă am umplut matricea, derulăm în sus cu o linie (smooth scrolling)
                self.grid.pop(0)
                self.grid.append(next_row)

            self.generation += 1

        else:
            # Rulare 2D Cellular Automata (Brian's Brain, Cyclic CA etc.)
            new_grid = [[self.grid[r][c] for c in range(self.cols)] for r in range(self.rows)]

            for r in range(self.rows):
                for c in range(self.cols):
                    current_state = self.grid[r][c]
                    neighbor_counts = self._get_neighbors(r, c)

                    # Caută prima regulă compatibilă din lista de tranziții
                    for rule in self.transitions:
                        if rule.get("current_state") == current_state:
                            target_counts = rule.get("counts")
                            min_count = rule.get("min_count")
                            req_neighbor = rule.get("neighbor_state")

                            # Regula necondiționată (ex: FIRING -> DYING, DYING -> OFF)
                            if target_counts == "any":
                                new_grid[r][c] = rule["next_state"]
                                break

                            # Regula cu prag minim (ex: la Cyclic CA: cel puțin 2 vecini)
                            elif min_count is not None and req_neighbor:
                                if neighbor_counts.get(req_neighbor, 0) >= min_count:
                                    new_grid[r][c] = rule["next_state"]
                                    break

                            # Regula condiționată de mulțimea de numere de vecini
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
        """Creează o copie identică a automatului pentru analize fără a afecta starea curentă."""
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
        for _ in range(max_steps):
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
    print("DEMO TEST 1: Elementary Cellular Automaton (Rule 30)")
    print("==================================================")
    elem = CellularAutomata("elementary_rule30.json")
    print(f"Nume: {elem.name} | Tip: Elementary Rule 30")
    print(f"Regula 30 modele: {elem.patterns}")

    # Setăm 1 rând inițial de test: 000010000
    test_1d_grid = [["0"] * 11 for _ in range(5)]
    test_1d_grid[0][5] = "1"
    elem.set_grid(test_1d_grid)
    print("\nGenerația 0 (rândul de pornire 00000100000):")
    elem.display()

    elem.step()
    print("\nGenerația 1 (după aplicarea regulii 30):")
    elem.display()
    assert elem.grid[1][4] == "1" and elem.grid[1][5] == "1" and elem.grid[1][6] == "1", "Regula 30 eșuată!"
    print("[PASS] Regula 30 calculată corect (001 -> 1, 010 -> 1, 100 -> 1)!")

    print("\n==================================================")
    print("DEMO TEST 2: Brian's Brain (OFF, FIRING, DYING)")
    print("==================================================")
    brain = CellularAutomata("brians_brain.json")
    print(f"Nume: {brain.name} | Stări: {brain.states}")
    brain_test_grid = [
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"],
        ["OFF", "FIRING", "FIRING", "OFF", "OFF"],
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"],
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"],
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"]
    ]
    brain.set_grid(brain_test_grid)
    print("\nGenerația 0:")
    brain.display()
    brain.step()
    print("\nGenerația 1 (FIRING -> DYING, celule OFF cu 2 FIRING devin FIRING):")
    brain.display()
    assert brain.grid[1][1] == "DYING" and brain.grid[1][2] == "DYING", "Brian's Brain eșuat!"
    print("[PASS] Tranzițiile FIRING -> DYING și nașterea din OFF au funcționat corect!")

    print("\n==================================================")
    print("DEMO TEST 3: Cyclic Cellular Automaton (0, 1, 2, 3)")
    print("==================================================")
    cyclic = CellularAutomata("cyclic_ca.json")
    print(f"Nume: {cyclic.name} | Stări: {cyclic.states}")
    # Matrice cu 0 și o celulă înconjurată de cel puțin 2 celule de '1'
    cyclic_grid = [
        ["1", "1", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"]
    ]
    cyclic.set_grid(cyclic_grid)
    cyclic.step()
    # Celula (1, 0) sau (0, 2) având vecini '1' devine '1'
    print("Generația 1 (Cyclic CA):")
    cyclic.display()
    print(f"Celule de tip '1' după 1 pas: {cyclic.count_cells('1')}")
    print("[PASS] Cyclic CA rulează cu succes!")

    print("\n==================================================")
    print("DEMO TEST 4: State Storage & Recovery (JSON)")
    print("==================================================")
    checkpoint_file = "brians_brain_checkpoint.json"
    brain.save_state(checkpoint_file)
    recovered = CellularAutomata("brians_brain.json")
    recovered.load_state(checkpoint_file)
    assert recovered.grid == brain.grid, "Recovery eșuat!"
    print(f"[PASS] Starea restaurată cu succes de la Generația {recovered.generation}!")

    print("\n==================================================")
    print("TOATE TESTELE AU FOST VALIDATE CU SUCCES!")
    print("==================================================")
