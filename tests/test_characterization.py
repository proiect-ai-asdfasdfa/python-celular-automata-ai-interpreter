"""
Teste de caracterizare: compară comportamentul curent cu rezultatele de referință din tests/golden/.

Rulare, din rădăcina proiectului:
    python -m unittest

Rezultatele de referință au fost generate din codul dinaintea refactorizării (Windows, Python 3.13).
Pe alte platforme sau versiuni de Python pot apărea diferențe minore (ex. fonturi, mesaje de eroare).
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TESTS_DIR)
GOLDEN_DIR = os.path.join(TESTS_DIR, "golden")
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="1", PYTHONDONTWRITEBYTECODE="1")


def first_difference(expected, actual, path="$"):
    """Returnează calea primei diferențe dintre două structuri JSON, sau None dacă sunt identice."""
    if type(expected) is not type(actual):
        return f"{path}: {expected!r} != {actual!r}"
    if isinstance(expected, dict):
        for key in sorted(set(expected) | set(actual)):
            if key not in expected or key not in actual:
                return f"{path}.{key}: cheie prezentă doar într-o parte"
            diff = first_difference(expected[key], actual[key], f"{path}.{key}")
            if diff:
                return diff
        return None
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return f"{path}: lungimi diferite ({len(expected)} != {len(actual)})"
        for i, (a, b) in enumerate(zip(expected, actual)):
            diff = first_difference(a, b, f"{path}[{i}]")
            if diff:
                return diff
        return None
    return None if expected == actual else f"{path}: {expected!r} != {actual!r}"


def read_golden_text(name):
    with open(os.path.join(GOLDEN_DIR, name), encoding="utf-8") as f:
        return f.read()


class ScriptOutputTests(unittest.TestCase):
    """Scripturile scriu un checkpoint în directorul curent, deci rulează într-un director temporar."""

    def run_python(self, *args):
        with tempfile.TemporaryDirectory() as cwd:
            for config in glob.glob(os.path.join(PROJECT_DIR, "*.json")):
                shutil.copy(config, cwd)
            result = subprocess.run(
                [sys.executable, *args],
                cwd=cwd, env=ENV, capture_output=True, encoding="utf-8",
            )
            self.assertTrue(os.path.exists(os.path.join(cwd, "brians_brain_checkpoint.json")))
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_main_cli_output(self):
        self.assertEqual(self.run_python(os.path.join(PROJECT_DIR, "main.py"), "--cli"), read_golden_text("cli_output.txt"))

    def test_main_test_flag_output(self):
        self.assertEqual(self.run_python(os.path.join(PROJECT_DIR, "main.py"), "--test"), read_golden_text("cli_output.txt"))


class SnapshotTests(unittest.TestCase):
    def compare_snapshot(self, script, golden_name):
        with tempfile.TemporaryDirectory() as out_dir:
            out = os.path.join(out_dir, "snapshot.json")
            result = subprocess.run(
                [sys.executable, os.path.join(TESTS_DIR, script), PROJECT_DIR, out],
                env=ENV, capture_output=True, encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with open(out, encoding="utf-8") as f:
                actual = json.load(f)
        with open(os.path.join(GOLDEN_DIR, golden_name), encoding="utf-8") as f:
            expected = json.load(f)
        self.assertIsNone(first_difference(expected, actual))

    def test_engine_snapshot(self):
        self.compare_snapshot("characterize_engine.py", "engine.json")

    def test_gui_snapshot(self):
        try:
            tk.Tk().destroy()
        except tk.TclError as e:
            self.skipTest(f"Tk indisponibil: {e}")
        self.compare_snapshot("characterize_gui.py", "gui.json")


if __name__ == "__main__":
    unittest.main()
