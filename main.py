"""
Project CellLab - Punctul Principal de Intrare (Main Entry Point)
Lansează interfața grafică Tkinter sau rulează testele automatizate din linia de comandă.
"""

import sys
import tkinter as tk
from cellab_gui import CellLabGUI
from cellab_engine import CellularAutomata


def run_cli_tests():
    """Rulează bateria de teste și validare pentru Deliverable 2."""
    print("==========================================================")
    print(" PROJECT CELLLAB - TESTARE AUTOMATIZATĂ DELIVERABLE 2")
    print("==========================================================")

    # 1. Test Conway
    print("\n[1] Inițializare Conway's Game of Life...")
    conway = CellularAutomata("conway.json")
    print(f"    Nume: {conway.name}")
    print(f"    Vecinătate: {conway.neighborhood_type}, Bordură: {conway.boundary}")
    print(f"    Stări posibile: {conway.states}")

    blinker = [
        ["dead", "dead", "dead", "dead", "dead"],
        ["dead", "dead", "dead", "dead", "dead"],
        ["dead", "alive", "alive", "alive", "dead"],
        ["dead", "dead", "dead", "dead", "dead"],
        ["dead", "dead", "dead", "dead", "dead"]
    ]
    conway.set_grid(blinker)
    print("    Stare inițială (Blinker orizontal):")
    conway.display()

    conway.step()
    print("    Generația 1 (Blinker vertical):")
    conway.display()

    # 2. Test Storage & Recovery
    print("\n[2] Testare State Storage & Recovery...")
    test_checkpoint = "conway_checkpoint.json"
    conway.save_state(test_checkpoint)
    print(f"    Stare salvată în '{test_checkpoint}'.")

    recovered = CellularAutomata("conway.json")
    recovered.load_state(test_checkpoint)
    print(f"    Stare recuperată cu succes. Generație reluată: {recovered.generation}")
    assert recovered.grid == conway.grid, "Eroare: Grila recuperată nu este identică!"
    print("    [PASS] Grid-ul recuperat este identic cu cel salvat.")

    # 3. Test Întrebări Analitice
    print("\n[3] Testare Răspuns la Întrebările Proiectului...")
    has_cycle, period, s_gen, c_gen = conway.detect_cycle(max_steps=50)
    print(f"    Q5 (Ciclu): Ciclu detectat? {has_cycle} | Perioadă: {period} (de la Gen {s_gen} la Gen {c_gen})")
    assert has_cycle and period == 2, "Blinker ar trebui să aibă perioada 2!"

    alive_count = conway.count_cells_after_n_steps("alive", 4)
    print(f"    Q4 (Numărare stări): Celule 'alive' după 4 pași: {alive_count}")
    assert alive_count == 3, "Blinker ar trebui să aibă 3 celule active!"

    is_stable, _ = conway.find_stable_state(max_steps=10)
    print(f"    Q2 (Stabilitate): Devine Blinker neschimbat/stabil? {is_stable} (Corect: este un oscilator, deci nu e still life)")

    # 4. Test Brian's Brain
    print("\n[4] Inițializare Brian's Brain...")
    brain = CellularAutomata("brians_brain.json")
    print(f"    Nume: {brain.name}")
    print(f"    Stări posibile: {brain.states}")
    brain_grid = [
        ["off", "off", "off", "off", "off"],
        ["off", "on",  "on",  "off", "off"],
        ["off", "off", "off", "off", "off"],
        ["off", "off", "off", "off", "off"],
        ["off", "off", "off", "off", "off"]
    ]
    brain.set_grid(brain_grid)
    print("    Generația 0:")
    brain.display()
    brain.step()
    print("    Generația 1 (on -> dying, vecini cu 2 on devin on):")
    brain.display()
    print(f"    Celule active Brian's Brain: {brain.count_cells()}")

    # 5. Test Wireworld (Automat complet diferit: 4 stări, bordură fixă, porți logice)
    print("\n[5] Inițializare Wireworld (Dovada că motorul NU este hardcodat)...")
    wire = CellularAutomata("wireworld.json")
    print(f"    Nume: {wire.name} | Stări: {wire.states} | Bordură: {wire.boundary}")
    wire_grid = [
        ["empty", "empty",     "empty", "empty"],
        ["head",  "conductor", "conductor", "empty"],
        ["empty", "empty",     "empty", "empty"]
    ]
    wire.set_grid(wire_grid)
    print("    Generația 0 (electron head -> conductor -> conductor):")
    wire.display()
    wire.step()
    print("    Generația 1 (head -> tail, conductor cu 1 head devine head):")
    wire.display()
    assert wire.grid[1][0] == "tail" and wire.grid[1][1] == "head", "Propagarea electronului în Wireworld a eșuat!"
    print("    [PASS] Wireworld simulează corect propagarea semnalului electric!")

    print("\n==========================================================")
    print(" TOATE TESTELE DELIVERABLE 2 AU FOST VALIDATE CU SUCCES!")
    print("==========================================================")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "--cli"):
        run_cli_tests()
    else:
        root = tk.Tk()
        _app = CellLabGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()

