"""
Modelul automatului celular: API-ul public care reunește configurația, lumea, regulile,
simularea, stocarea și analiza.
Regulile, dimensiunile, topologia de vecinătate și stările sunt încărcate complet din fișiere JSON.
"""

from copy import deepcopy

from cellab import analysis, rules, simulation, storage, world
from cellab.config import build_patterns, is_elementary_config, load_config


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
        self.config_path, self.config = load_config(config_source)

        self.name = self.config.get("name", "Generic Cellular Automaton")
        self.neighborhood_type = self.config.get("neighborhood", "moore").lower()
        self.boundary = self.config.get("boundary", "wrap").lower()
        self.states = self.config.get("states", [])
        self.dead_state = self.config.get("dead_state", self.states[0] if self.states else "0")
        self.symbols = self.config.get("symbols", {})
        self.colors = self.config.get("colors", {})
        self.active_states = self.config.get("active_states", [s for s in self.states if s != self.dead_state])
        self.transitions = self.config.get("transitions", [])

        self.is_elementary = is_elementary_config(self.config)
        self.patterns = build_patterns(self.config) if self.is_elementary else {}

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
        self.grid = world.filled_grid(self.rows, self.cols, fill_state)
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
            self.grid = world.elementary_start_grid(
                self.rows, self.cols, self.states, self.dead_state, self.active_states, probabilities
            )
        else:
            probs = probabilities or self.config.get("default_probabilities")
            self.grid = world.random_grid(self.rows, self.cols, self.states, probs)

    def _get_neighbors(self, r, c):
        """
        Calculează frecvența stărilor vecinilor pentru celula (r, c) în automate 2D.
        Suportă cartier Moore (8 vecini) și von Neumann (4 vecini),
        precum și bordură toroidală (wrap) sau fixă (fixed/dead).
        """
        return rules.count_neighbors(self, r, c)

    def step(self):
        """
        Calculează și aplică tranzițiile de stare, avansând universul cu o generație:
        - În Elementary CA (1D): generează rândul următor din diagrama spațio-temporală.
        - În 2D CA: aplică regulile de tranziție pentru toate celulele matricei simultan.
        """
        if self.is_elementary:
            simulation.step_elementary(self)
        else:
            simulation.step_2d(self)

    def run_simulation(self, steps, verbose=True):
        """Rulează simularea pentru un număr dat de iterații."""
        simulation.run_simulation(self, steps, verbose)

    def count_cells(self, state=None):
        """
        Numără celulele dintr-o anumită stare.
        Dacă state=None, returnează numărul total de celule considerate active.
        """
        return world.count_cells(self.grid, self.active_states, state)

    def get_state_counts(self):
        """Returnează un dicționar cu distribuția curentă a tuturor stărilor."""
        return world.state_counts(self.grid, self.states)

    def display(self):
        """Afișează matricea formatată în consolă folosind simbolurile din configurație."""
        simulation.display(self)

    def save_state(self, filepath):
        """
        State Storage:
        Salvează starea lumii curente într-un fișier JSON (generație, dimensiuni, nume, matrice).
        """
        return storage.save_state(self, filepath)

    def load_state(self, filepath):
        """
        State Recovery:
        Restaurează o stare salvată anterior și continuă simularea exact de la acea generație.
        """
        return storage.load_state(self, filepath)

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
        return analysis.get_state_after_n_steps(self, n)

    def find_stable_state(self, max_steps=1000):
        """
        Întrebarea 2: Când atinge sistemul o stare stabilă? (nicio schimbare pe viitor)
        Returnează (True, generație) dacă a atins stabilitate, altfel (False, None).
        """
        return analysis.find_stable_state(self, max_steps)

    def does_configuration_occur(self, target_grid, max_steps=1000):
        """
        Întrebarea 3: Apare vreodată o anumită configurație?
        Returnează (True, generație) dacă matricea target apare în intervalul dat.
        """
        return analysis.does_configuration_occur(self, target_grid, max_steps)

    def count_cells_after_n_steps(self, state, n):
        """
        Întrebarea 4: Câte celule de tipul X există după N iterații?
        """
        return analysis.count_cells_after_n_steps(self, state, n)

    def detect_cycle(self, max_steps=1000):
        """
        Întrebarea 5: Intră simularea într-un ciclu? (o secvență repetitivă de stări)
        Returnează:
          (has_cycle: bool, period: int, start_gen: int, cycle_gen: int)
        """
        return analysis.detect_cycle(self, max_steps)
