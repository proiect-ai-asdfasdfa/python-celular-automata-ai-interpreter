"""Characterization snapshot of the engine. Usage: characterize_engine.py <project_dir> <out.json>
Uses the public import `cellab.CellularAutomata`."""
import contextlib, hashlib, inspect, io, json, os, random, sys, tempfile

project, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sys.path.insert(0, project)
os.chdir(project)
from cellab import CellularAutomata

LIFE = {
    "name": "Game of Life (inline)", "neighborhood": "moore", "boundary": "wrap",
    "states": ["dead", "alive"], "dead_state": "dead", "active_states": ["alive"],
    "symbols": {"dead": ". ", "alive": "# "}, "default_rows": 12, "default_cols": 12,
    "default_probabilities": [0.7, 0.3],
    "transitions": [
        {"current_state": "alive", "neighbor_state": "alive", "counts": [2, 3], "next_state": "alive"},
        {"current_state": "alive", "counts": "any", "next_state": "dead"},
        {"current_state": "dead", "neighbor_state": "alive", "counts": 3, "next_state": "alive"},
    ],
}
VN_FIXED = dict(LIFE, name="Life VN fixed", neighborhood="von_neumann", boundary="fixed")
RULE110 = {"name": "Rule 110", "rule_number": 110, "boundary": "fixed", "states": ["0", "1"],
           "default_rows": 8, "default_cols": 13}
MINIMAL = {"states": ["a", "b"], "transitions": [], "default_rows": 4, "default_cols": 4}
SOURCES = {
    "rule30": "elementary_rule30.json", "brain": "brians_brain.json", "cyclic": "cyclic_ca.json",
    "life": LIFE, "life_vn_fixed": VN_FIXED, "rule110": RULE110, "minimal": MINIMAL,
}
FIXED = {
    "life": [["dead"] * 6, ["dead", "dead", "alive", "dead", "dead", "dead"], ["dead", "dead", "alive", "dead", "dead", "dead"],
             ["dead", "dead", "alive", "dead", "dead", "dead"], ["dead"] * 6, ["dead"] * 6],
    "brain": [["OFF"] * 5, ["OFF", "FIRING", "FIRING", "OFF", "OFF"], ["OFF"] * 5, ["OFF"] * 5, ["OFF"] * 5],
    "cyclic": [["1", "1", "0"], ["0", "0", "0"], ["0", "0", "0"]],
    "rule30": [["0"] * 7 for _ in range(6)],
}
FIXED["rule30"][0][3] = "1"
FIXED["life_vn_fixed"] = FIXED["life"]


def rng_probe():
    """Reveals how many RNG draws happened so far, without being able to hide consumption."""
    st = random.getstate()
    v = random.random()
    random.setstate(st)
    return v


def captured(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


def attrs(ca):
    return {k: getattr(ca, k) for k in ("name", "neighborhood_type", "boundary", "states", "dead_state", "symbols", "colors",
            "active_states", "transitions", "is_elementary", "patterns", "rows", "cols", "generation", "grid")}


def scenario(key, src, tmp):
    r = {}
    random.seed(12345)
    ca = CellularAutomata(src)
    r["init"] = attrs(ca)
    r["rng_init"] = rng_probe()
    r["counts_init"] = [ca.count_cells(), ca.get_state_counts()]
    r["display"] = captured(ca.display)[1]

    random.seed(1)
    ca.generate_random_grid(5, 6); r["rand_5x6"] = [ca.rows, ca.cols, ca.grid, rng_probe()]
    n = len(ca.states)
    ca.generate_random_grid(4, 4, probabilities=[1] * n); r["rand_probs"] = [ca.grid, rng_probe()]
    ca.generate_random_grid(4, 4, probabilities=[1] * (n + 1) if not ca.is_elementary else None); r["rand_badprobs"] = [ca.grid, rng_probe()]
    ca.clear_grid(); r["clear"] = [ca.rows, ca.cols, ca.grid, ca.generation]
    ca.clear_grid(3, 2, state=ca.states[-1]); r["clear_state"] = [ca.rows, ca.cols, ca.grid]

    random.seed(777)
    ca = CellularAutomata(src)
    if key in FIXED:
        ca.set_grid(FIXED[key], generation=2)
    traj = []
    for _ in range(40):  # includes scrolling for elementary automata
        ca.step()
        traj.append(hashlib.sha256(json.dumps(ca.grid).encode()).hexdigest())
    r["trajectory_sha"] = traj
    r["after_40"] = [ca.generation, ca.grid, ca.get_state_counts(), ca.count_cells()]

    # Analysis questions: results, no mutation of current state, RNG consumption by clone().
    random.seed(99)
    ca = CellularAutomata(src)
    if key in FIXED:
        ca.set_grid(FIXED[key])
    before = json.dumps(ca.grid)
    g, gen = ca.get_state_after_n_steps(7); r["q1"] = [g, gen, rng_probe()]
    r["q2"] = [ca.find_stable_state(max_steps=60), rng_probe()]
    r["q3_found"] = [ca.does_configuration_occur(g, max_steps=20), rng_probe()]
    r["q3_initial"] = ca.does_configuration_occur(json.loads(before), max_steps=3)
    r["q3_missing"] = ca.does_configuration_occur([["nope"]], max_steps=5)
    r["q4"] = [ca.count_cells_after_n_steps(st, 5) for st in ca.states] + [rng_probe()]
    r["q5"] = [ca.detect_cycle(max_steps=60), rng_probe()]
    r["unchanged"] = json.dumps(ca.grid) == before and ca.generation == 0

    # Clone copies state, including after set_grid.
    c = ca.clone(); r["clone"] = [c.grid == ca.grid, c.rows, c.cols, c.generation]

    # Storage: exact bytes of the saved format and round trip.
    path = os.path.join(tmp, f"{key}.json")
    ca.step(); ca.step()
    ret = ca.save_state(path)
    with open(path, "rb") as f:
        r["saved_bytes_sha"] = hashlib.sha256(f.read()).hexdigest()
    r["save_return"] = ret
    other = CellularAutomata(src)
    loaded = other.load_state(path)
    r["load"] = [loaded, attrs(other)["grid"], other.rows, other.cols, other.generation]
    other.step(); ca.step()
    r["resume_equal"] = other.grid == ca.grid
    return r


def errors():
    r = {}
    for label, fn in {
        "bad_source": lambda: CellularAutomata(123),
        "missing_file": lambda: CellularAutomata("does_not_exist.json"),
        "empty_grid": lambda: CellularAutomata(MINIMAL).set_grid([]),
        "empty_row": lambda: CellularAutomata(MINIMAL).set_grid([[]]),
        "no_states": lambda: CellularAutomata({}).grid,
    }.items():
        try:
            r[label] = ["ok", fn()]
        except Exception as e:
            r[label] = [type(e).__name__, str(e)]
    # dict configs must be copied, not aliased
    cfg = json.loads(json.dumps(MINIMAL))
    ca = CellularAutomata(cfg); cfg["states"].append("zzz")
    r["config_copied"] = ca.states
    # load_state fallbacks for missing keys
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "s.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"grid": [["a", "b", "a"]]}, f)
        ca = CellularAutomata(MINIMAL); d = ca.load_state(p)
        r["load_defaults"] = [d, ca.rows, ca.cols, ca.generation, ca.grid]
    return r


def public_surface():
    methods = {n: str(inspect.signature(m)) for n, m in inspect.getmembers(CellularAutomata, inspect.isfunction)}
    return {"methods": methods, "doc": CellularAutomata.__doc__, "method_docs": {
        n: m.__doc__ for n, m in inspect.getmembers(CellularAutomata, inspect.isfunction)}}


result = {"public_surface": public_surface(), "errors": errors(), "scenarios": {}}
with tempfile.TemporaryDirectory() as tmp:
    for key, src in SOURCES.items():
        result["scenarios"][key] = scenario(key, src, tmp)

with open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=1, ensure_ascii=False, sort_keys=True, default=repr)
print("engine snapshot written:", out, "| scenarios:", len(result["scenarios"]))
