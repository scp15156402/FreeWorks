"""FreeWorks automated test suite - runs inside FreeCAD (GUI under Xvfb).

Started by dev/run_tests.sh. Writes $FREEWORKS_TEST_OUT/results.json and screenshots,
then quits FreeCAD. Each test is small and independent; a failing test never stops the run.
"""
import json
import math
import os
import time
import traceback

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

OUT = os.environ.get("FREEWORKS_TEST_OUT", "/tmp/freeworks-tests")
os.makedirs(OUT, exist_ok=True)
RESULTS = []
STEPS = []
STATE = {}

# Performance budgets (milliseconds). Exceeding them = lag risk.
BUDGET = {"startup_s": 6.0, "tick_ms": 2.0, "cm_update_ms": 6.0, "context_ms": 0.5}
ADDON_PREFIXES = ("SheetMetal_", "Fasteners_", "FS", "ZebraTool", "Curves_", "Render_")


def record(name, ok, detail=""):
    RESULTS.append({"test": name, "ok": bool(ok), "detail": str(detail)[:2000]})
    App.Console.PrintMessage("[%s] %s %s\n" % ("PASS" if ok else "FAIL", name, detail))


def step(delay=300):
    def deco(fn):
        STEPS.append((fn, delay))
        return fn
    return deco


def shot(name):
    try:
        QtWidgets.QApplication.processEvents()
        Gui.getMainWindow().grab().save(os.path.join(OUT, name + ".png"))
    except Exception:
        pass


def mw():
    return Gui.getMainWindow()


# --------------------------------------------------------------------------- tests
@step(500)
def t_startup():
    from freeworks import shell
    ok = shell._S.get("dock") is not None and shell._S.get("cm") is not None
    secs = None
    log = os.environ.get("FREEWORKS_DEBUG_LOG")
    if log and os.path.exists(log):
        for line in open(log):
            if line.startswith("startup "):
                secs = float(line.split()[1].rstrip("s"))
    record("startup: shell installed", ok)
    record("startup: time <= %.1fs" % BUDGET["startup_s"], secs is not None and secs <= BUDGET["startup_s"], "%ss" % secs)
    record("startup: FreeWorks workbench active", Gui.activeWorkbench().name() == "FreeWorksWorkbench", Gui.activeWorkbench().name())


@step()
def t_catalog():
    from freeworks import catalog
    missing, addon_missing = [], []
    for k, e in catalog.C.items():
        if catalog.first_existing(e) is None:
            optional = e.get("optional") or any(c.startswith(ADDON_PREFIXES) for c in e["cmd"])
            (addon_missing if optional else missing).append("%s->%s" % (k, e["cmd"][0]))
    record("catalog: every core command exists", not missing, ", ".join(missing))
    record("catalog: optional/add-on commands (info)", True, "%d unavailable (add-on or newer FreeCAD): %s" % (len(addon_missing), ", ".join(addon_missing[:12])))
    refs = []
    for ctx, keys in list(catalog.GESTURES.items()) + list(catalog.SHORTCUT_BAR.items()):
        refs += [(ctx, k) for k in keys if k not in catalog.C]
    for kind, groups in catalog.TABS.items():
        for name, spec in groups:
            if isinstance(spec, list):
                for g in spec:
                    if g[0] == "L":
                        refs += [(name, x) for x in [g[1]] + list(g[2] if len(g) > 2 else []) if x not in catalog.C]
                    elif g[0] == "S":
                        refs += [(name, x) for x in g[1] if x not in catalog.C]
    for g in catalog.SKETCH_TAB:
        if g[0] == "L":
            refs += [("Sketch", x) for x in [g[1]] + list(g[2] if len(g) > 2 else []) if x not in catalog.C]
        elif g[0] == "S":
            refs += [("Sketch", x) for x in g[1] if x not in catalog.C]
    record("catalog: tabs/gestures/shortcut bar reference valid keys", not refs, refs[:10])
    from freeworks import icon_path
    noicon = [k for k, e in catalog.C.items() if e["icon"] and not icon_path(e["icon"])]
    record("catalog: every icon file exists", not noicon, noicon[:10])


@step()
def t_shortcuts():
    from freeworks import shortcuts, catalog
    bad = []
    for seq, m in shortcuts.KEYMAP.items():
        for ctx, act in m.items():
            if act.startswith("fn:"):
                if act[3:] not in shortcuts.FUNCS:
                    bad.append((seq, act))
            elif act not in catalog.C:
                bad.append((seq, act))
    record("shortcuts: every key maps to a valid command", not bad, bad)
    record("shortcuts: installed", len(shortcuts._shortcuts) == len(shortcuts.KEYMAP), len(shortcuts._shortcuts))


@step()
def t_ui():
    from freeworks import shell
    win = mw()
    visible_tb = [t.objectName() for t in win.findChildren(QtWidgets.QToolBar) if t.isVisible() and t.parent() is win]
    record("ui: FreeCAD toolbars hidden", not visible_tb, visible_tb)
    tasks = shell._dock("Tasks")
    model = shell._dock("Model")
    record("ui: PropertyManager docked (not overlay)", tasks is not None and tasks.parent() is win and
           win.dockWidgetArea(tasks) == QtCore.Qt.LeftDockWidgetArea, tasks.parent().metaObject().className() if tasks else None)
    record("ui: PropertyManager tabbed with FeatureManager", tasks in win.tabifiedDockWidgets(model) if tasks and model else False)
    ov = [w for w in win.findChildren(QtWidgets.QWidget) if w.metaObject().className() == "Gui::OverlayTabWidget" and w.isVisible()]
    record("ui: no stray overlay panels", not ov, len(ov))
    record("ui: native menu bar hidden", not win.menuBar().isVisible())


@step(300)
def t_stability_guards():
    import inspect
    import freeworks
    from freeworks import shell, widgets, gestures, naming, sketchmode, watchdog, contextmenu, shortcuts
    unguarded = []
    for mod in (shell, widgets, gestures, naming, sketchmode, watchdog):
        for name, obj in vars(mod).items():
            if inspect.isclass(obj) and obj.__module__ == mod.__name__ and name not in ("_NoTitle",):
                if not getattr(obj, "_fw_hardened", False):
                    unguarded.append("%s.%s" % (mod.__name__, name))
    record("stability: every UI/observer class guarded", not unguarded, unguarded)
    record("stability: no global document observer while not in Centerline", sketchmode._obs is None)
    record("stability: watchdog running", watchdog._wd is not None)
    left = [c for c in shortcuts.DISABLE_SHORTCUTS if Gui.Command.get(c) and Gui.Command.get(c).getShortcut()]
    record("stability: overlay-toggle shortcuts disabled", not left, left)
    n_err = len(freeworks.STATS["errors"])

    @freeworks.safe
    def _fw_selftest_error():
        raise ValueError("deliberate")
    r = _fw_selftest_error()
    record("stability: exceptions in callbacks are caught", r is None and len(freeworks.STATS["errors"]) == n_err + 1)
    freeworks.STATS["errors"].pop()

    @freeworks.safe
    def _fw_selftest_slow():
        time.sleep(0.09)
    n_slow = len(freeworks.STATS["slow"])
    _fw_selftest_slow()
    record("stability: slow callbacks are detected", len(freeworks.STATS["slow"]) == n_slow + 1)
    freeworks.STATS["slow"].pop()
    cm = shell._S["cm"]
    built = [k for k in cm.panels if k[0] == cm.kind]
    record("stability: CommandManager tabs pre-built at idle", len(built) == len(cm.tabset), "%d/%d" % (len(built), len(cm.tabset)))


@step(1500)   # delay = time until the NEXT step: let the freeze happen and the watchdog beat
def t_freeze():
    # block the event loop on purpose; the watchdog must notice
    STATE["stalls0"] = len(__import__("freeworks").STATS["stalls"])
    QtCore.QTimer.singleShot(50, lambda: time.sleep(0.9))


@step(2500)
def t_freeze_check():
    import freeworks
    st = freeworks.STATS["stalls"]
    ok = len(st) > STATE["stalls0"] and st[-1][1] >= 700
    record("stability: watchdog detects a UI freeze", ok, st[-1][1] if st else None)
    if ok:
        st.pop()
    win = mw()
    tbs = [t for t in win.findChildren(QtWidgets.QToolBar) if t.parent() is win and not t.objectName().startswith("FreeWorks")]
    if tbs:
        tbs[0].show()
        STATE["tb"] = tbs[0]


@step(300)
def t_toolbar_heal():
    tb = STATE.get("tb")
    record("stability: stray FreeCAD toolbar is hidden again", tb is not None and not tb.isVisible(), tb.objectName() if tb else None)


@step(1500)
def t_new_part():
    from freeworks import naming
    doc = naming.new_document("part")
    STATE["doc"] = doc
    body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"]
    record("part: new Part has a Body", len(body) == 1)
    STATE["body"] = body[0] if body else None


@step(800)
def t_model():
    import Part
    import Sketcher
    V = App.Vector
    doc, body = STATE["doc"], STATE["body"]
    labels = {o.Label for o in doc.Objects}
    record("naming: origin planes Front/Top/Right", {"Front Plane", "Top Plane", "Right Plane"} <= labels, sorted(labels))
    top = [f for f in body.Origin.OriginFeatures if f.Role == "XY_Plane"][0]
    sk = body.newObject("Sketcher::SketchObject", "Sketch")
    sk.AttachmentSupport = [(top, "")]
    sk.MapMode = "FlatFace"
    pts = [V(-30, -20, 0), V(30, -20, 0), V(30, 20, 0), V(-30, 20, 0)]
    for i in range(4):
        sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4]))
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
    for i, t in ((0, "Horizontal"), (2, "Horizontal"), (1, "Vertical"), (3, "Vertical")):
        sk.addConstraint(Sketcher.Constraint(t, i))
    sk.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, 60))
    sk.addConstraint(Sketcher.Constraint("DistanceY", 1, 1, 1, 2, 40))
    sk.addConstraint(Sketcher.Constraint("Symmetric", 0, 1, 1, 2, -1, 1))
    doc.recompute()
    pad = body.newObject("PartDesign::Pad", "Pad")
    pad.Profile = sk
    pad.Length = 20
    doc.recompute()
    STATE.update(sketch=sk, pad=pad)
    record("model: box 60x40x20 volume", abs(pad.Shape.Volume - 48000) < 1e-6, pad.Shape.Volume)
    record("model: sketch fully defined", bool(sk.FullyConstrained), "DoF=%s" % getattr(sk, "DoF", "?"))


@step(600)
def t_feature_names():
    names = [o.Label for o in STATE["doc"].Objects if o.TypeId in ("Sketcher::SketchObject", "PartDesign::Pad")]
    record("naming: Sketch1 / Boss-Extrude1", names == ["Sketch1", "Boss-Extrude1"], names)
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    shot("01_part")


@step(300)
def t_mass_properties():
    from freeworks import commands, widgets
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(STATE["body"])
    commands.mass_properties()
    d = widgets.ReportDialog._open.get("Mass Properties")
    txt = d.text.toPlainText() if d else ""
    record("evaluate: mass properties report", "Mass = 48.00 grams" in txt and "Volume = 48000.00" in txt,
           txt.splitlines()[4:8] if txt else "no dialog")
    if d:
        d.close()
    Gui.Selection.clearSelection()


@step(1200)
def t_sketch_context():
    from freeworks import context, shell
    Gui.ActiveDocument.setEdit(STATE["sketch"].Name)
    STATE["t0"] = time.time()


@step(800)
def t_sketch_context_check():
    from freeworks import context, shell
    record("sketch: context is 'sketch'", context.current() == "sketch", context.current())
    record("sketch: CommandManager switched to Sketch tab", shell._S["cm"].current_name() == "Sketch", shell._S["cm"].current_name())
    st = shell._S["status"].sketch.text()
    record("sketch: status bar shows Fully Defined", st.startswith("Fully Defined"), st)
    shot("02_sketch")
    Gui.ActiveDocument.resetEdit()


@step(800)
def t_back_to_part():
    from freeworks import context, shell
    record("sketch: back to part context after exit", context.current() == "part", context.current())
    record("sketch: CommandManager back on Features", shell._S["cm"].current_name() == "Features", shell._S["cm"].current_name())


@step(200)
def t_performance():
    from freeworks import shell, context
    c = shell._S["controller"]
    n = 200
    t = time.perf_counter()
    for _ in range(n):
        c.tick()
    tick = (time.perf_counter() - t) / n * 1000
    cm = shell._S["cm"]
    t = time.perf_counter()
    for _ in range(50):
        cm.update_states()
    cmu = (time.perf_counter() - t) / 50 * 1000
    t = time.perf_counter()
    for _ in range(n):
        context.current()
    ctx = (time.perf_counter() - t) / n * 1000
    record("perf: controller tick <= %.1f ms" % BUDGET["tick_ms"], tick <= BUDGET["tick_ms"], "%.3f ms" % tick)
    record("perf: CommandManager state update <= %.1f ms" % BUDGET["cm_update_ms"], cmu <= BUDGET["cm_update_ms"], "%.3f ms" % cmu)
    record("perf: context detection <= %.1f ms" % BUDGET["context_ms"], ctx <= BUDGET["context_ms"], "%.3f ms" % ctx)
    STATE["perf"] = {"tick_ms": tick, "cm_update_ms": cmu, "context_ms": ctx}


@step(2500)
def t_assembly():
    from freeworks import naming
    naming.new_document("assembly")


@step(500)
def t_assembly_check():
    from freeworks import context, shell
    tabs = [shell._S["cm"].tabs.tabText(i) for i in range(shell._S["cm"].tabs.count())]
    record("assembly: context", context.current() == "assembly", context.current())
    record("assembly: tabs Assembly + Mates", "Assembly" in tabs and "Mates" in tabs, tabs)
    shot("03_assembly")


@step(3000)
def t_drawing():
    from freeworks import naming
    naming.new_document("drawing")


@step(800)
def t_drawing_check():
    from freeworks import context, shell
    tabs = [shell._S["cm"].tabs.tabText(i) for i in range(shell._S["cm"].tabs.count())]
    record("drawing: context", context.current() == "drawing", context.current())
    record("drawing: tabs View Layout + Annotation", "View Layout" in tabs and "Annotation" in tabs, tabs)
    shot("04_drawing")


@step(300)
def t_close_all():
    for n in list(App.listDocuments()):
        App.closeDocument(n)


@step(800)
def t_no_errors():
    import freeworks
    log = os.environ.get("FREEWORKS_DEBUG_LOG")
    errs = []
    if log and os.path.exists(log):
        lines = [l.strip() for l in open(log)]
        errs = [l for l in lines if (l.startswith("error in") or l.startswith("WARN")) and "_fw_selftest" not in l]
    record("stability: no FreeWorks errors logged", not errs, errs[:5])
    slow = [(n, round(ms)) for _, n, ms in freeworks.STATS["slow"] if "_fw_selftest" not in n]
    record("lag: no slow FreeWorks callbacks (> 60 ms)", not slow, slow[:8])
    stalls = [(round(ms), w) for _, ms, w in freeworks.STATS["stalls"]]
    record("lag: UI stalls during the run (info)", True, stalls[:8])


# --------------------------------------------------------------------------- runner
def run(i=0):
    if i >= len(STEPS):
        finish()
        return
    fn, delay = STEPS[i]
    try:
        fn()
    except Exception:
        record(fn.__name__ + " (exception)", False, traceback.format_exc())
    QtCore.QTimer.singleShot(delay, lambda: run(i + 1))


def finish():
    passed = sum(r["ok"] for r in RESULTS)
    data = {"passed": passed, "failed": len(RESULTS) - passed, "results": RESULTS, "perf": STATE.get("perf"),
            "freecad": ".".join(App.Version()[:3])}
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(data, f, indent=2)
    QtWidgets.QApplication.quit()


def wait_for_freeworks(n=0):
    try:
        from freeworks import shell
        ready = shell._S.get("dock") is not None
    except Exception:
        ready = False
    if ready or n > 120:
        QtCore.QTimer.singleShot(1500, run)
    else:
        QtCore.QTimer.singleShot(250, lambda: wait_for_freeworks(n + 1))


mw().resize(1700, 1000)
QtCore.QTimer.singleShot(500, wait_for_freeworks)
