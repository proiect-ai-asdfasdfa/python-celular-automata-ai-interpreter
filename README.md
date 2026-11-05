# Project CellLab - Deliverable 2: Generic Cellular Automata Simulation System

Sistem generic de simulare și analiză a automatelor celulare, dezvoltat în Python conform cerințelor academice pentru **Deliverable 2**.

---

## 1. Structura Proiectului

Proiectul separă complet logica de calcul matematic/algoritmic de interfața grafică utilizator:

```text
python-celular-automata-ai-interpreter/
├── main.py                 # Punctul principal de lansare (GUI sau verificări CLI)
├── elementary_rule30.json  # Configurația pentru Elementary Cellular Automaton (Rule 30)
├── brians_brain.json       # Configurația pentru Brian's Brain (OFF, FIRING, DYING)
├── cyclic_ca.json          # Configurația pentru Cyclic Cellular Automaton (0, 1, 2, 3)
├── cellab/
│   ├── automaton.py        # Clasa CellularAutomata (API-ul public al motorului)
│   ├── config.py           # Citirea configurației JSON, detectarea automatelor 1D
│   ├── world.py            # Crearea grilelor și numărarea celulelor
│   ├── rules.py            # Vecinătăți și aplicarea regulilor de tranziție
│   ├── simulation.py       # Simularea generațiilor și afișarea în consolă
│   ├── storage.py          # Salvarea și restaurarea stării (JSON)
│   ├── analysis.py         # Răspunsurile la întrebările Q1-Q5
│   ├── cli_checks.py       # Verificările din linia de comandă
│   ├── paths.py            # Căile proiectului
│   └── gui/
│       ├── app.py          # Clasa CellLabGUI și tema interfeței
│       ├── panels.py       # Panourile ferestrei și etichetele
│       ├── canvas.py       # Randarea grilei și interacțiunea cu mouse-ul
│       ├── controls.py     # Play/Pause, Step, Randomize, Clear, viteză
│       ├── config_select.py # Scanarea configurațiilor și schimbarea automatului
│       ├── presets.py      # Modelele predefinite
│       ├── state_dialogs.py # Dialogurile Save/Load
│       └── analysis_dialog.py # Fereastra cu întrebările Q1-Q5
└── tests/                  # Teste și rezultate de referință (golden/)
```

> **Notă:** Proiectul utilizează **exclusiv biblioteca standard Python** (`json`, `tkinter`, `random`, `copy`, `os`, `sys`). Nu necesită pachete externe instalate prin `pip`.

---

## 2. Automatele Celulare Incluse (Cerința: 2-3 automate diferite)

Sistemul include 3 automate reprezentând familii complet diferite de automate celulare:

### 1. Elementary Cellular Automaton (Rule 30)
* **Tip**: Unidimensional (1D) proiectat pe matrice 2D în evoluție spațio-temporală.
* **Stări**: `0` (dead), `1` (alive).
* **Vecinătate**: Stânga, Centru, Dreapta (`left, current, right`).
* **Regula 30**:
  * `111 -> 0`
  * `110 -> 0`
  * `101 -> 0`
  * `100 -> 1`
  * `011 -> 1`
  * `010 -> 1`
  * `001 -> 1`
  * `000 -> 0`
* **Pornire canonică**: `000000010000000` (un singur bit de `1` în centru). Generațiile succesive generează celebrul triunghi haotic studiat de Stephen Wolfram.

### 2. Brian's Brain
* **Tip**: 2D celular înrudit cu Game of Life, dar mult mai dinamic.
* **Stări**: `OFF`, `FIRING`, `DYING`.
* **Reguli**:
  * `FIRING -> DYING` (necondiționat)
  * `DYING -> OFF` (necondiționat)
  * O celulă `OFF` devine `FIRING` dacă are **exact 2 vecini** în starea `FIRING`.
* **Comportament**: Produce structuri auto-propulsate (nave / glidere) și oscilatori activi.

### 3. Cyclic Cellular Automaton
* **Tip**: 2D celular cu valuri de fază.
* **Stări**: `0`, `1`, `2`, `3`.
* **Regulă**:
  Pentru o celulă aflată în starea $x$, starea următoare este $\text{next} = (x + 1) \pmod 4$.
  Dacă **cel puțin 2 vecini** au starea $\text{next}$, celula își schimbă starea în $\text{next}$. Altfel, rămâne neschimbată.
* **Comportament**: Generează spirale organice hipnotizante și vortexuri auto-organizate.

---

## 3. Modelare Genericã bazată pe JSON (Cerința 1)

Niciun comportament specific nu este hardcodat în codul Python. Fiecare fișier JSON definește:
1. **Tipul automatului**: 2D clasic sau 1D Elementary (`rule_number` / `patterns`).
2. **Topologia de vecinătate**: `moore` (8 vecini), `von_neumann` (4 vecini) sau `left, current, right` (1D).
3. **Condițiile de bordură**: `wrap` (toroidal) sau `fixed` (bordură moartă).
4. **Stările posibile și culorile**: Nume, simboluri consolă și coduri hexazecimale pe Canvas.
5. **Tabelul de tranziții**:
   * Reguli necondiționate (`counts: "any"`).
   * Reguli condiționate de numărul sau pragul de vecini (`counts: [2]` sau `min_count: 2`).

---

## 4. State Storage & Recovery (Cerința 2)

* **Salvarea stării (`save_state(filepath)`)**:
  Exportă într-un fișier JSON metadatele automatului activ (`automaton_name`, `generation`, `rows`, `cols`) și matricea completă a stărilor `grid`.
* **Recuperarea stării (`load_state(filepath)`)**:
  Încarcă fișierul salvat anterior și reia simularea exact de la acea generație. Dacă starea salvată aparține altui automat, GUI-ul comută automat configurația corespunzătoare.

---

## 5. Interfața Grafică Interactivă Tkinter (Cerința 3)

Construită în pachetul `cellab/gui/`:
* **Canvas interactiv**:
  * Fiecare celulă este colorată conform stării ei.
  * **Editare manuală**: Click stânga pe o celulă pentru a-i schimba starea, **drag** cu mouse-ul pentru a desena liber, click dreapta pentru resetare la starea inactivă.
* **Controale complete**:
  * Dropdown selector ce scanează automat toate configurațiile JSON disponibile.
  * Buton **"▶ Play / ⏸ Pause"** (simulare fluidă la viteză reglabilă prin slider).
  * Buton **"⏭ Next Step"** (avansează exact 1 generație).
  * Buton **"🎲 Randomize / Reset"** (reinițializează conform automatului: centru 1 pentru Rule 30, matrice aleatorie pentru Brian's Brain / Cyclic CA).
  * Buton **"🧹 Clear Grid"** (golește grila pentru desenare liberă).
  * Butoane **"💾 Save State"** și **"📂 Load State"**.
  * Selector **Preset**: încarcă tipare celebre pentru fiecare automat (Single Center Seed, Glider, Oscillators, Spirale).
  * **Etichetă de stare**: arată numărul generației curente, celulele active și distribuția stărilor.

---

## 6. Răspunsul la Întrebările Proiectului

Motorul include metode algoritmice gata implementate pentru cele 5 întrebări din enunț:

| Nr. | Întrebare | Metodă Algoritmică în `CellularAutomata` |
|---|---|---|
| **Q1** | *Care este starea după N iterații?* | `get_state_after_n_steps(n)` |
| **Q2** | *Când atinge sistemul o stare stabilă?* | `find_stable_state(max_steps=1000)` |
| **Q3** | *Apare vreodată o anumită configurație?* | `does_configuration_occur(target_grid, max_steps=1000)` |
| **Q4** | *Câte celule de tip X există după N iterații?* | `count_cells_after_n_steps(state, n)` |
| **Q5** | *Intră simularea într-un ciclu repetitiv?* | `detect_cycle(max_steps=1000)` |

---

## 7. Instrucțiuni de Rulare

### Lansarea Interfeței Grafice (GUI):
```bash
python main.py
```

### Rularea Suitei de Teste Automate (CLI):
```bash
python main.py --cli
```
sau:
```bash
python -m cellab.cli_checks
```

### Rularea Testelor:
```bash
python -m unittest
```
