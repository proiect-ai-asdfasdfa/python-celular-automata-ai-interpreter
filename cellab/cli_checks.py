"""Verificările din linia de comandă pentru Deliverable 2 (`python main.py --cli`)."""

from cellab.automaton import CellularAutomata


def run_cli_tests():
    """Rulează bateria de teste și validare pentru Deliverable 2."""
    print("==========================================================")
    print(" PROJECT CELLLAB - TESTARE AUTOMATIZATĂ DELIVERABLE 2")
    print("==========================================================")

    # 1. Test Elementary Cellular Automaton (Rule 30)
    print("\n[1] Inițializare Elementary Cellular Automaton (Rule 30)...")
    elem = CellularAutomata("elementary_rule30.json")
    print(f"    Nume: {elem.name} | Tip: 1D Elementary | Regula 30")
    print(f"    Stări: {elem.states} | Vecinătate: (stânga, centru, dreapta)")

    test_1d_grid = [["0"] * 15 for _ in range(5)]
    test_1d_grid[0][7] = "1"  # Un singur 1 în centru
    elem.set_grid(test_1d_grid)
    print("    Generația 0 (000000010000000):")
    elem.display()

    elem.step()
    print("    Generația 1 (după aplicarea regulii 30):")
    elem.display()
    assert elem.grid[1][6] == "1" and elem.grid[1][7] == "1" and elem.grid[1][8] == "1", "Regula 30 a eșuat!"
    print("    [PASS] Regula 30 calculată corect (111->0, 100->1, 011->1, 001->1)!")

    # 2. Test Brian's Brain (OFF, FIRING, DYING)
    print("\n[2] Inițializare Brian's Brain...")
    brain = CellularAutomata("brians_brain.json")
    print(f"    Nume: {brain.name}")
    print(f"    Stări posibile: {brain.states} | Cartier: {brain.neighborhood_type}")
    brain_grid = [
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"],
        ["OFF", "FIRING", "FIRING", "OFF", "OFF"],
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"],
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"],
        ["OFF", "OFF",    "OFF",    "OFF", "OFF"]
    ]
    brain.set_grid(brain_grid)
    print("    Generația 0:")
    brain.display()
    brain.step()
    print("    Generația 1 (FIRING -> DYING, OFF cu 2 FIRING devine FIRING):")
    brain.display()
    assert brain.grid[1][1] == "DYING" and brain.grid[1][2] == "DYING", "Brian's Brain a eșuat!"
    print(f"    [PASS] Celule active Brian's Brain: {brain.count_cells()} (FIRING + DYING)")

    # 3. Test Cyclic Cellular Automaton (0, 1, 2, 3)
    print("\n[3] Inițializare Cyclic Cellular Automaton...")
    cyclic = CellularAutomata("cyclic_ca.json")
    print(f"    Nume: {cyclic.name} | Stări: {cyclic.states}")
    print(f"    Regulă: x -> (x + 1) mod 4 dacă cel puțin 2 vecini au (x + 1) mod 4")
    cyclic_grid = [
        ["1", "1", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"]
    ]
    cyclic.set_grid(cyclic_grid)
    print("    Generația 0:")
    cyclic.display()
    cyclic.step()
    print("    Generația 1 (propagare cyclic):")
    cyclic.display()
    assert cyclic.count_cells("1") > 2, "Tranziția ciclică nu s-a declanșat!"
    print("    [PASS] Tranzițiile ciclice produc tipare corecte!")

    # 4. Test State Storage & Recovery
    print("\n[4] Testare State Storage & Recovery (JSON)...")
    test_checkpoint = "brians_brain_checkpoint.json"
    brain.save_state(test_checkpoint)
    print(f"    Stare salvată în '{test_checkpoint}'.")

    recovered = CellularAutomata("brians_brain.json")
    recovered.load_state(test_checkpoint)
    print(f"    Stare recuperată cu succes. Generație reluată: {recovered.generation}")
    assert recovered.grid == brain.grid, "Eroare: Grila recuperată nu este identică!"
    print("    [PASS] Grid-ul recuperat este identic cu cel salvat.")

    # 5. Test Întrebări Analitice
    print("\n[5] Testare Răspuns la Întrebările Proiectului...")
    has_cycle, period, s_gen, c_gen = brain.detect_cycle(max_steps=50)
    print(f"    Q5 (Ciclu): Ciclu detectat? {has_cycle} | Perioadă: {period} (de la Gen {s_gen} la Gen {c_gen})")

    active_count = brain.count_cells_after_n_steps("DYING", 2)
    print(f"    Q4 (Numărare stări): Celule 'DYING' după 2 pași: {active_count}")

    is_stable, _ = brain.find_stable_state(max_steps=10)
    print(f"    Q2 (Stabilitate): A atins stabilitate totală? {is_stable}")

    print("\n==========================================================")
    print(" TOATE TESTELE DELIVERABLE 2 AU FOST VALIDATE CU SUCCES!")
    print("==========================================================")
