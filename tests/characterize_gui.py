"""Characterization snapshot of the GUI, driven headlessly (hidden root, dialogs stubbed).
Usage: characterize_gui.py <project_dir> <out.json>
Uses the public names `cellab.gui.CellLabGUI`, `cellab.gui.main` and `main.main`."""
import atexit, hashlib, json, os, random, shutil, sys, tempfile, types
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb

project, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sys.path.insert(0, project)
os.chdir(project)

tmp = tempfile.mkdtemp()
atexit.register(shutil.rmtree, tmp, ignore_errors=True)


def norm(s):
    return str(s).replace(tmp, "<TMP>").replace(tmp.replace("\\", "/"), "<TMP>").replace(project, "<PROJECT>").replace(project.replace("\\", "/"), "<PROJECT>").replace("\\", "/")


log = []
for fn in ("showinfo", "showerror", "showwarning"):
    setattr(mb, fn, (lambda n: lambda title=None, message=None, **k: log.append([n, norm(title), norm(message)]))(fn))
open_queue, save_queue, dialog_kwargs = [], [], []


def _ask(queue, kind):
    def inner(**k):
        dialog_kwargs.append([kind, {a: norm(b) for a, b in k.items() if a != "parent"}])
        return queue.pop(0) if queue else ""
    return inner


fd.askopenfilename = _ask(open_queue, "open")
fd.asksaveasfilename = _ask(save_queue, "save")
tk.Toplevel.grab_set = lambda self: None  # hidden parent cannot take a grab

import cellab.gui

root = tk.Tk()
root.withdraw()
app = cellab.gui.CellLabGUI(root)


def dump_widget(w):
    d = {"path": str(w), "class": w.winfo_class(), "pytype": type(w).__name__}
    for opt in ("text", "values", "bg", "fg", "style", "font", "foreground", "state", "width", "from", "to", "relief", "title"):
        try:
            d[opt] = str(w.cget(opt))
        except tk.TclError:
            pass
    if w.winfo_manager() == "pack":
        d["pack"] = {k: str(v) for k, v in w.pack_info().items() if k != "in"}
    d["binds"] = sorted(w.bind())
    d["children"] = [dump_widget(c) for c in w.winfo_children()]
    return d


def canvas_sig():
    c = app.canvas
    items = [(i, c.coords(i), c.itemcget(i, "fill"), c.itemcget(i, "outline")) for i in c.find_all()]
    return hashlib.sha256(json.dumps(items).encode()).hexdigest(), len(items), str(c.cget("bg"))


def snap(label):
    a = app.automata
    return {
        "label": label, "name": a.name, "generation": a.generation, "rows": a.rows, "cols": a.cols,
        "grid_sha": hashlib.sha256(json.dumps(a.grid).encode()).hexdigest(), "canvas": canvas_sig(),
        "stats": app.lbl_stats.cget("text"), "message": app.lbl_message.cget("text"),
        "badge": app.info_badge.cget("text"), "selector": app.automaton_var.get(),
        "selector_values": list(app.selector_combo.cget("values")), "preset": app.preset_var.get(),
        "preset_values": list(app.preset_combo.cget("values")), "running": app.is_running,
        "speed": [app.speed_ms, app.lbl_speed_val.cget("text")],
        "legend": [str(x.cget("text")) if x.winfo_class() == "TLabel" else str(x.cget("bg"))
                   for f in app.legend_frame.winfo_children() for x in f.winfo_children()],
        "play": [app.btn_play.cget("text"), app.btn_play.cget("bg")],
    }


def ev(x=0, y=0, **k):
    return types.SimpleNamespace(x=x, y=y, **k)


def cell_xy(r, c):
    s = app.cell_size
    return app.offset_x + c * s + s // 2, app.offset_y + r * s + s // 2


def find(w, cls, text=None):
    res = []
    for c in w.winfo_children():
        if c.winfo_class() == cls and (text is None or text in str(c.cget("text"))):
            res.append(c)
        res += find(c, cls, text)
    return res


r = {"init_title": root.title(), "geometry_min": root.minsize(), "config_files": {k: norm(v) for k, v in app.config_files.items()},
     "current_config": norm(app.current_config_file), "init_snapshot": snap("init"), "widget_tree": dump_widget(root), "scenarios": {}}
r["colors"] = [app._get_cell_color(s) for s in ("0", "1", "2", "3", "OFF", "FIRING", "DYING", "off", "on", "dying", "dead", "alive")]

names = list(app.config_files)
for name in names:
    s = []
    random.seed(2024)
    app.automaton_var.set(name); app._on_automaton_changed(); s.append(snap("switched"))
    for _ in range(3):
        app.step_forward()
    s.append(snap("3 steps"))
    app.randomize_grid(); s.append(snap("randomized"))
    app.toggle_play_pause(); s.append(snap("playing"))
    app.toggle_play_pause(); s.append(snap("paused"))
    app._on_speed_changed("250.7"); s.append(snap("speed"))
    app._on_speed_changed("120")
    for p in app.preset_combo.cget("values"):
        app.preset_var.set(p); app._on_preset_selected(); s.append(snap(f"preset {p}"))
        app.step_forward(); s.append(snap(f"preset {p} +1"))
    app.clear_grid(); s.append(snap("cleared"))
    # mouse: click cycles, drag paints, release stops, right click clears
    x, y = cell_xy(2, 2); app._on_canvas_click(ev(x, y)); s.append(snap("click"))
    app._on_canvas_click(ev(x, y)); s.append(snap("click2"))
    x2, y2 = cell_xy(2, 3); app._on_canvas_drag(ev(x2, y2)); s.append(snap("drag"))
    app._on_canvas_release(ev()); x3, y3 = cell_xy(2, 4); app._on_canvas_drag(ev(x3, y3)); s.append(snap("drag after release"))
    app._on_canvas_right_click(ev(x, y)); s.append(snap("right click"))
    app._on_canvas_click(ev(-500, -500)); s.append(snap("click outside"))
    app._on_canvas_resize(ev(width=800, height=600)); s.append(snap("resize"))
    app._on_canvas_resize(ev(width=40, height=40)); s.append(snap("resize ignored"))
    app._on_canvas_resize(ev(width=640, height=580))
    # storage
    path = os.path.join(tmp, f"state_{names.index(name)}.json")
    save_queue.append(path); app.save_state_dialog(); s.append(snap("saved"))
    with open(path, "rb") as f:
        s.append(["saved_sha", hashlib.sha256(f.read()).hexdigest()])
    app.step_forward(); open_queue.append(path); app.load_state_dialog(); s.append(snap("loaded"))
    app.save_state_dialog()   # cancelled dialog
    app.load_state_dialog()   # cancelled dialog
    # analysis dialog: every button with its default inputs, on a small preset-free grid
    app.automata.clear_grid(8, 8)
    app.automata.grid[1][1] = app.automata.states[-1]; app.automata.grid[1][2] = app.automata.states[-1]
    app._init_canvas_grid(); app._update_ui_stats()
    app._open_analysis_dialog()
    dlg = [c for c in root.winfo_children() if isinstance(c, tk.Toplevel)][-1]
    tree = dump_widget(dlg)
    for b in find(dlg, "TButton"):
        if "Alege" not in b.cget("text"):
            b.invoke()  # Q3 without target => warning
    open_queue.append(path)
    find(dlg, "TButton", "Alege")[0].invoke()
    find(dlg, "TButton", "Q3")[0].invoke()
    bad = os.path.join(tmp, "bad.json")
    with open(bad, "w") as f:
        f.write("{not json")
    open_queue.append(bad); find(dlg, "TButton", "Alege")[0].invoke()
    entries = find(dlg, "TEntry")
    entries[0].delete(0, tk.END); entries[0].insert(0, "abc"); find(dlg, "TButton", "Q1")[0].invoke()
    s.append(["analysis_labels", [l.cget("text") for l in find(dlg, "TLabel")], "tree", tree, "title", dlg.title(), "geom", dlg.geometry().split("+")[0]])
    dlg.destroy()
    r["scenarios"][name] = s

# Cross-automaton recovery: state saved from Brian's Brain loaded while Rule 30 is active.
random.seed(3)
brain_name = "Brian's Brain"
app.automaton_var.set(brain_name); app._on_automaton_changed(); app.step_forward()
cross = os.path.join(tmp, "cross.json"); save_queue.append(cross); app.save_state_dialog()
app.automaton_var.set(names[0]); app._on_automaton_changed()
open_queue.append(cross); app.load_state_dialog(); r["cross_load"] = snap("cross load")

# External config loaded through the dialog, then broken config and broken state.
ext = os.path.join(tmp, "ext.json")
with open(ext, "w", encoding="utf-8") as f:
    json.dump({"name": "External", "states": ["x", "y", "mystery"], "transitions": [], "default_rows": 5, "default_cols": 5,
               "default_probabilities": [1, 1, 1], "neighborhood": "von_neumann", "boundary": "fixed",
               "colors": {"x": "#111111", "y": "#222222", "mystery": "#333333"}}, f)
open_queue.append(ext); random.seed(4); app._load_custom_config(); r["external"] = snap("external"); r["external_cfg"] = {k: norm(v) for k, v in app.config_files.items()}
bad = os.path.join(tmp, "bad.json")
open_queue.append(bad); app._load_custom_config(); r["bad_config"] = snap("bad config")
open_queue.append(bad); app.load_state_dialog(); r["bad_state"] = snap("bad state")
app._load_custom_config()

r["messagebox_log"] = log
r["dialog_kwargs"] = dialog_kwargs
root.destroy()

# Entry points: main.main() and cellab.gui.main() must build the app and enter mainloop once.
calls = []
tk.Tk.mainloop = lambda self, n=0: calls.append(self.title())
tk.Misc.mainloop = tk.Tk.mainloop
import main as main_mod
sys.argv = ["main.py"]
main_mod.main(); tk._default_root.destroy()
cellab.gui.main(); tk._default_root.destroy()
r["entry_points"] = calls

with open(out, "w", encoding="utf-8") as f:
    json.dump(r, f, indent=1, ensure_ascii=False, sort_keys=True, default=repr)
print("gui snapshot written:", out, "| automata:", names, "| dialogs logged:", len(log))
