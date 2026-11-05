"""Citirea configurației unui automat și detectarea tipului Elementary (1D)."""

import json
from copy import deepcopy


def load_config(config_source):
    """
    Citește configurația fie dintr-o cale către un fișier JSON, fie dintr-un dicționar.
    Returnează (config_path, config); config_path este None pentru dicționare.
    """
    if isinstance(config_source, str):
        with open(config_source, "r", encoding="utf-8") as f:
            return config_source, json.load(f)
    if isinstance(config_source, dict):
        return None, deepcopy(config_source)
    raise ValueError("config_source trebuie să fie o cale (str) sau un dicționar (dict).")


def is_elementary_config(config):
    """Verifică dacă automatul este de tip 1D Elementary (Wolfram)."""
    return (
        config.get("type") == "elementary"
        or "patterns" in config
        or "rule_number" in config
    )


def build_patterns(config):
    """Returnează tabelul de modele 1D, explicit din `patterns` sau calculat din `rule_number`."""
    if "patterns" in config:
        return config["patterns"]
    patterns = {}
    if "rule_number" in config:
        rule_num = int(config["rule_number"])
        for i, pat in enumerate(["111", "110", "101", "100", "011", "010", "001", "000"]):
            patterns[pat] = str((rule_num >> (7 - i)) & 1)
    return patterns
