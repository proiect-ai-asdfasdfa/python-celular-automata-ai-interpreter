# Project CellLab - Deliverable 2: Generic 2D Cellular Automata Simulation System

Sistem generic de simulare și analiză a automatelor celulare bidimensionale, dezvoltat în Python conform cerințelor academice pentru **Deliverable 2**.

---

## 1. Structura Proiectului

Proiectul este structurat modular, separând complet logica de calcul matematic/algoritmic de interfața grafică utilizator:

```text
ai/
├── cellab_engine.py       # Motorul generic de simulare și analize algoritmice
├── cellab_gui.py          # Interfața grafică minimală și interactivă (Tkinter Canvas)
├── main.py                # Punctul principal de lansare (GUI sau CLI test suite)
├── conway.json            # Configurația generică pentru Conway's Game of Life
├── brians_brain.json      # Configurația generică pentru Brian's Brain
└── conway_checkpoint.json # Exemplu de salvare de stare (State Storage / Recovery)
```

> **Notă:** Proiectul utilizează **exclusiv biblioteca standard Python** (`json`, `tkinter`, `random`, `copy`, `os`, `sys`). Nu necesită pachete externe instalate prin `pip`.

---

## 2. Modelare Genericã bazată pe JSON (Cerința 1)

Niciun comportament specific automatelor celulare **nu este hardcodat** în motorul `cellab_engine.py`. Toate regulile, topologia și proprietățile sunt citite din fișiere JSON:

1. **Tip de vecinătate (`neighborhood`)**:
   - `"moore"`: 8 vecini (toate celulele adiacente orizontal, vertical și pe diagonale).
   - `"von_neumann"`: 4 vecini ortogonali (cruce: sus, jos, stânga, dreapta).
2. **Comportament la bordură (`boundary`)**:
   - `"wrap"`: bordură toroidală (coordonatele depășite se reîntorc pe latura opusă, `nr % rows`, `nc % cols`).
   - `"fixed"` / `"dead"`: bordură fixă (orice celulă din afara matricei este tratată ca celulă inactivă/moartă).
3. **Stări posibile (`states`)**:
   - Listă ordonată de stări (ex: `["dead", "alive"]` sau `["off", "on", "dying"]`).
4. **Tabel de tranziții (`transitions`)**:
   - Permite reguli condiționate de numărul de vecini de o anumită stare (`"neighbor_state"` și `"counts": [2, 3]`).
   - Permite reguli necondiționate (`"counts": "any"`).
   - Inerție implicită: dacă nicio regulă nu se aplică unei celule, aceasta își păstrează starea curentă.

### Fișiere Predefinite Incluse:
* **`conway.json`**: Conway's Game of Life (stări: `dead`, `alive`; reguli B3/S23; cartier Moore; bordură wrap).
* **`brians_brain.json`**: Brian's Brain (stări: `off`, `on`, `dying`; cartier Moore; reguli: `off` devine `on` dacă are exact 2 vecini `on`; `on` devine `dying`; `dying` devine `off`).

---

## 3. State Storage & Recovery (Cerința 2)

Sistemul include funcționalități complete de persistență:
* **Salvarea stării (`save_state(filepath)`)**:
  - Exportă starea completă într-un fișier JSON conținând:
    * `"automaton_name"`: Numele automatului activ.
    * `"generation"`: Numărul iterației curente.
    * `"rows"`, `"cols"`: Dimensiunile matricei.
    * `"grid"`: Matricea bidimensională $N \times M$ a stărilor fiecărei celule.
* **Recuperarea stării (`load_state(filepath)`)**:
  - Încarcă starea salvată și continuă simularea exact de la acea generație.
  - În GUI, la încărcarea unei stări salvate de la alt automat, sistemul detectează automat diferența și comută automatul.

---

## 4. Interfața Grafică Interactivă Tkinter (Cerința 3)

Interfața construită în `cellab_gui.py` oferă:
1. **Grilă vizuală interactivă pe `Canvas`**:
   - Fiecare celulă este colorată conform stării ei (ex: alb/negru pentru Conway; bleumarin/cyan/roșu pentru Brian's Brain).
   - **Editare interactivă**:
     * Click stânga pe o celulă pentru a-i cicla starea manual.
     * Click & drag cu mouse-ul pentru a desena tipare libere pe grilă.
     * Click dreapta pentru a șterge (reseta la starea moartă/inactivă) o celulă.
2. **Controale complete**:
   - **Dropdown Selector**: Comutare instantă între `"Conway's Game of Life"` și `"Brian's Brain"` (sau butonul `Load JSON Config` pentru oricare alt automat personalizat).
   - **Buton "▶ Play / ⏸ Pause"**: Rulează simularea fluid la un interval configurabil (implicit 150ms).
   - **Buton "⏭ Next Step"**: Avansează simularea cu o singură generație.
   - **Buton "🎲 Randomize / Reset"**: Generează o nouă stare inițială aleatorie conform probabilităților automatului.
   - **Buton "🧹 Clear Grid"**: Curăță complet grila pentru desenarea facilă a formelor proprii.
   - **Slider de Viteză**: Permite reglarea intervalului de animație (între 30ms și 500ms).
   - **Selector de Presets**: Încarcă rapid oscilatori cunoscuți (Blinker, Glider, Beacon, Block, Pulsar etc.).
   - **Buton "💾 Save State (JSON)"**: Dialog de export al stării curente.
   - **Buton "📂 Load State (JSON)"**: Dialog de import al stării salvate.
   - **Etichetă (Label) de Stare**: Afișează numărul generației curente, numărul total de celule active și distribuția pe fiecare stare.

---

## 5. Răspunsul la Întrebările Proiectului (Cerința din Enunț)

Motorul implementează metode algoritmice pentru a răspunde la **toate cele 5 întrebări analitice**:

| Nr. | Întrebare | Metodă Algoritmică în `CellularAutomata` |
|---|---|---|
| **Q1** | *Care este starea după N iterații?* | `get_state_after_n_steps(n)` |
| **Q2** | *Când atinge sistemul o stare stabilă?* | `find_stable_state(max_steps=1000)` |
| **Q3** | *Apare vreodată o anumită configurație?* | `does_configuration_occur(target_grid, max_steps=1000)` |
| **Q4** | *Câte celule de tip X există după N iterații?* | `count_cells_after_n_steps(state, n)` |
| **Q5** | *Intră simularea într-un ciclu repetitiv?* | `detect_cycle(max_steps=1000)` |

> În GUI, butonul **"❓ Analiză & Întrebări"** deschide o fereastră dedicată unde utilizatorul poate rula și vizualiza răspunsurile la aceste întrebări direct din interfață.

---

## 6. Instrucțiuni de Rulare

### Lansarea Interfeței Grafice (GUI):
```bash
python main.py
```
sau:
```bash
python cellab_gui.py
```

### Rularea Suitei de Teste Automate (CLI):
```bash
python main.py --cli
```
sau:
```bash
python cellab_engine.py
```

