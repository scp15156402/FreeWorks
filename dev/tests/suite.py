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
    ready = freeworks.STATS.get("ready_at")
    record("stability: startup grace period ends", ready is not None, ready)
    freeworks.STATS["ready_at"] = 0           # outside the startup grace period for this check
    _fw_selftest_slow()
    freeworks.STATS["ready_at"] = ready
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
    ok = len(st) > STATE["stalls0"] and st[-1][1] >= 550   # 900 ms block minus up to one 250 ms beat
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
    from freeworks import commands, evaluate
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(STATE["body"])
    commands.mass_properties()
    d = evaluate.MassPropertiesDialog._inst
    txt = d.text.toPlainText() if d else ""
    record("evaluate: mass properties report", "Mass = 48.00 grams" in txt and "Volume = 48000.00" in txt,
           txt.splitlines()[3:9] if txt else "no dialog")
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
def t_session_and_modes():
    import freeworks
    from freeworks import safemode, perf, params
    sess = os.path.join(App.getUserAppDataDir(), "FreeWorks.session")
    ph = json.load(open(sess)).get("phase") if os.path.exists(sess) else None
    record("crash sentinel: session marked ready", ph == "ready", ph)
    pv = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part")
    perf.set_mode(True)
    on = (pv.GetFloat("MeshDeviation") == 0.5 and perf.is_on())
    perf.set_mode(False)
    off = (pv.GetFloat("MeshDeviation") == 0.1 and not perf.is_on())
    record("large model mode: on/off switches display quality", on and off)
    params().SetBool("Gestures", False)
    safemode.reset_settings()
    record("reset settings: FreeWorks defaults restored", params().GetBool("Gestures", True) and
           params().GetInt("PrefsVersion", 0) > 0 and params().GetString("ProjectsDir", "") != "")


@step(300)
def t_close_all():
    for n in list(App.listDocuments()):
        App.closeDocument(n)



# --------------------------------------------------------------------------- materials + mass properties (P12)
def _box_body(doc, name, size, base=(0, 0, 0)):
    b = doc.addObject("PartDesign::Body", name)
    bx = b.newObject("PartDesign::AdditiveBox", name + "Box")
    bx.Length, bx.Width, bx.Height = size
    b.Placement.Base = App.Vector(*base)
    return b


def _near(a, b, tol=0.01):
    return abs(a - b) <= tol * max(1.0, abs(b)) * 0.01 + 1e-6


@step(600)
def t_materials():
    from freeworks import materials, massprops
    names = {c["name"]: c for c in materials.cards()}
    need = ["AISI 1020", "Alloy Steel", "6061 Alloy", "1060 Alloy", "Copper", "Brass", "ABS", "Plain Carbon Steel"]
    record("materials: SOLIDWORKS-named cards", all(n in names for n in need) and names["AISI 1020"]["density"] == 7900,
           [n for n in need if n not in names])
    try:
        m = materials.get(names["AISI 1020"]["uuid"])
        ok = m.Name == "AISI 1020" and getattr(m, "LibraryName", "") == "FreeWorks"
    except Exception as e:
        ok, m = False, e
    record("materials: library registered with FreeCAD", ok, getattr(m, "LibraryName", m))
    doc = App.newDocument("FWMass")
    STATE["mass_doc"] = doc.Name
    b = _box_body(doc, "Body", (10, 20, 30), (100, 0, 0))
    doc.recompute()
    materials.apply([b], names["AISI 1020"]["uuid"])
    record("materials: assign to body", materials.material_of(b) == ("AISI 1020", 7900.0) and b.ShapeMaterial.Name == "AISI 1020",
           materials.material_of(b))
    Gui.Selection.clearSelection()
    res = massprops.compute(massprops.collect(use_selection=False))
    m = 6000 * 0.0079
    T = res["T"]
    ok = (_near(res["mass"], m) and all(_near(a, e) for a, e in zip(res["com"], (105, 10, 15)))
          and _near(T[0][0], m * (400 + 900) / 12) and _near(T[1][1], m * (100 + 900) / 12)
          and _near(T[2][2], m * (100 + 400) / 12) and abs(T[0][1]) < 1e-6)
    record("mass props: box mass, CoM, inertia (analytic)", ok, (round(res["mass"], 3), [round(x, 3) for x in res["com"]],
           [round(T[i][i], 2) for i in range(3)]))
    cs = b.newObject("PartDesign::CoordinateSystem", "CS")
    try:
        cs.MapMode = "Deactivated"
    except Exception:
        pass
    cs.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), 90))   # in the body: global (100,0,0)
    doc.recompute()
    labels = dict(massprops.coordinate_systems())
    txt = massprops.report(res, "FWMass", cs.Label, labels.get(cs.Label), "MMGS", 2) if cs.Label in labels else ""
    want = ["Mass = 47.40 grams", "X = 10.00", "Y = -5.00", "Z = 15.00", "Ixx = 15800.00", "Ixy = -2370.00", "Density = 0.0079 grams per cubic millimeter"]
    record("mass props: output coordinate system (moved + rotated)", all(w in txt for w in want),
           [w for w in want if w not in txt] or list(labels))
    txt2 = massprops.report(res, "FWMass", units="MKS", decimals=4)
    record("mass props: unit systems", "Mass = 0.0474 kilograms" in txt2, txt2.splitlines()[5:7])
    b2 = _box_body(doc, "Body2", (10, 10, 10), (0, 0, 100))
    doc.recompute()
    materials.apply_custom([b2], "Drawing density", 2700)
    res2 = massprops.compute(massprops.collect(use_selection=False))
    m2 = 1000 * 0.0027
    cz = (m * 15 + m2 * 105) / (m + m2)
    record("mass props: two bodies, different densities", _near(res2["mass"], m + m2) and _near(res2["com"][2], cz)
           and res2["density"] is None, (round(res2["mass"], 3), round(res2["com"][2], 3)))
    Gui.Selection.addSelection(doc.Name, "Body2", "Body2Box.Face1")
    res3 = massprops.compute(massprops.collect())
    record("mass props: selection = only the selected body", res3 and _near(res3["mass"], m2), res3 and res3["mass"])
    Gui.Selection.clearSelection()
    materials.remove([b2])
    record("materials: remove -> not specified (1000 kg/m^3)", materials.material_of(b2)[1] == 1000.0, materials.material_of(b2))


@step(800)
def t_mass_assembly():
    from freeworks import materials, massprops
    doc = App.getDocument(STATE["mass_doc"])
    for n in [o.Name for o in doc.Objects]:
        try:
            doc.removeObject(n)
        except Exception:
            pass
    b = _box_body(doc, "Pin", (10, 10, 10))
    doc.recompute()
    materials.apply([b], materials.card_by_name("1060 Alloy")["uuid"])
    b.Visibility = False
    asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
    l1 = asm.newObject("App::Link", "L1")
    l1.LinkedObject = b
    l2 = asm.newObject("App::Link", "L2")
    l2.LinkedObject = b
    l2.Placement.Base = App.Vector(50, 0, 0)
    sub = asm.newObject("App::Part", "Sub")
    sub.Placement.Base = App.Vector(0, 0, 100)
    l3 = sub.newObject("App::Link", "L3")
    l3.LinkedObject = b
    doc.recompute()
    Gui.Selection.clearSelection()
    res = massprops.compute(massprops.collect(use_selection=False))
    record("mass props: assembly = components only (no double count)", res and _near(res["mass"], 8.1),
           res and [c[:2] for c in res["components"]])
    ok = res and _near(res["com"][0], (5 + 55 + 5) / 3.0) and _near(res["com"][2], (5 + 5 + 105) / 3.0)
    record("mass props: assembly CoM incl. sub-assembly placement", ok, res and [round(x, 3) for x in res["com"]])
    l2.Visibility = False
    try:
        if l2.ViewObject:
            l2.ViewObject.Visibility = False
    except Exception:
        pass
    r_vis = massprops.compute(massprops.collect(hidden=False, use_selection=False))
    record("mass props: exclude hidden components", r_vis and _near(r_vis["mass"], 5.4), r_vis and r_vis["mass"])
    Gui.Selection.addSelection(doc.Name, "Assembly", "L2.")
    r_sel = massprops.compute(massprops.collect())
    record("mass props: selected component", r_sel and _near(r_sel["mass"], 2.7) and _near(r_sel["com"][0], 55),
           r_sel and (r_sel["mass"], r_sel["com"]))
    Gui.Selection.clearSelection()


@step(800)
def t_evaluate_dialogs():
    from freeworks import evaluate, commands
    doc = App.getDocument(STATE["mass_doc"])
    d = evaluate.MassPropertiesDialog.open()
    txt = d.text.toPlainText()
    record("mass props dialog: report + coordinate systems", "Mass = 8.10 grams" in txt and d.cs.count() >= 1,
           txt.splitlines()[:6])
    d.units.setCurrentText("CGS")
    record("mass props dialog: units switch", "grams per cubic centimeter" in d.text.toPlainText(), d.text.toPlainText().splitlines()[3:4])
    d.units.setCurrentText("MMGS")
    d.close()
    App.closeDocument(doc.Name)
    doc = App.newDocument("FWMat")
    b = _box_body(doc, "Body", (10, 10, 10))
    doc.recompute()
    Gui.Selection.clearSelection()
    commands.run_key("material")
    QtWidgets.QApplication.processEvents()
    md = evaluate.MaterialDialog._inst
    ok = False
    if md:
        it = md.tree.findItems("6061 Alloy", QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        if it:
            md.tree.setCurrentItem(it[0])
            md.apply()
            ok = b.ShapeMaterial.Name == "6061 Alloy" and "6061 Alloy" in md.target_lbl.text()
        md.close()
    record("material dialog: pick and apply", ok, b.ShapeMaterial.Name)
    App.closeDocument(doc.Name)


# --------------------------------------------------------------------------- mates (P13/P14)
def _v(q):
    return float(getattr(q, "Value", q))


def _bbl(o):
    import Part
    b = Part.getShape(o).BoundBox
    return [round(x, 2) for x in (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)]


@step(1200)
def t_mates():
    from freeworks import mates, matepm
    k = mates.suggest
    record("mates: suggestions", (k("plane", "plane"), k("cylinder", "cylinder"), k("cylinder", "plane"), k("circle", "line"), k("vertex", "plane"))
           == ("coincident", "concentric", "tangent", "concentric", "coincident"),
           (k("plane", "plane"), k("cylinder", "cylinder"), k("cylinder", "plane"), k("circle", "line"), k("vertex", "plane")))
    a = mates.allowed("plane", "plane")
    record("mates: allowed types for two planes", "angle" in a and "concentric" not in a and "tangent" not in a, a)
    doc = App.newDocument("FWMates")
    STATE["mates_doc"] = doc.Name

    def body(name, kind, dims):
        b = doc.addObject("PartDesign::Body", name)
        f = b.newObject("PartDesign::Additive" + ("Box" if kind == "box" else "Cylinder"), name + "F")
        if kind == "box":
            f.Length, f.Width, f.Height = dims
        else:
            f.Radius, f.Height = dims
        b.Visibility = False
        return b
    bodies = {"A": body("A", "box", (40, 40, 10)), "B": body("B", "box", (10, 10, 10)), "C": body("C", "cyl", (5, 20)),
              "D": body("D", "cyl", (3, 10)), "E": body("E", "box", (10, 10, 10))}
    asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
    asm.Type = "Assembly"
    plc = {"A": App.Placement(), "B": App.Placement(App.Vector(60, 0, 30), App.Rotation()),
           "C": App.Placement(App.Vector(0, 80, 0), App.Rotation()), "D": App.Placement(App.Vector(30, 80, 20), App.Rotation()),
           "E": App.Placement(App.Vector(60, 30, 7), App.Rotation(App.Vector(0, 0, 1), 30))}
    L = {}
    for n, b in bodies.items():
        l = asm.newObject("App::Link", "L" + n)
        l.LinkedObject = b
        l.Placement = plc[n]
        L[n] = l
    doc.recompute()
    import JointObject, UtilsAssembly
    gj = UtilsAssembly.getJointGroup(asm).newObject("App::FeaturePython", "GroundedJoint")
    JointObject.GroundedJoint(gj, L["A"])
    JointObject.ViewProviderGroundedJoint(gj.ViewObject)
    doc.recompute()
    STATE["mates_L"] = L
    STATE["mates_asm"] = asm
    Gui.Selection.clearSelection()
    matepm.start()
    p = matepm._PANEL["p"]
    record("mate PM: opens as task panel", p is not None and Gui.Control.activeDialog(), bool(p))
    if p is None:
        return
    p.add_selection(asm, "LA.AF.Face6", (20, 20, 10))
    p.add_selection(asm, "LB.BF.Face5", (65, 5, 30))
    record("mate PM: two planar faces -> Coincident, faces touch", p.mate == "coincident" and _bbl(L["B"])[2] == 10.0,
           (p.mate, _bbl(L["B"])))
    p.set_type("distance")
    p.value.setValue(15.0)
    record("mate PM: change to Distance 15", p.mate == "distance" and _bbl(L["B"])[2] == 25.0, (p.mate, _bbl(L["B"])))
    before = _bbl(L["B"])
    p.flip()
    flipped = _bbl(L["B"])
    record("mate PM: flip alignment moves the part", flipped != before, (before, flipped))
    p.flip()
    p.commit()
    j = p.added[-1] if p.added else None
    record("mate PM: commit -> Distance1 (A,B) in Mates", j is not None and j.Label.startswith("Distance1") and p.list.count() == 1,
           j.Label if j else None)
    p.add_selection(asm, "LC.CF.Face1", (5, 80, 10))
    p.add_selection(asm, "LD.DF.Face1", (33, 80, 25))
    c, d = _bbl(L["C"]), _bbl(L["D"])
    cc = ((c[0] + c[3]) / 2, (c[1] + c[4]) / 2)
    dc = ((d[0] + d[3]) / 2, (d[1] + d[4]) / 2)
    record("mate PM: two cylinders -> Concentric, axes aligned", p.mate == "concentric" and abs(cc[0] - dc[0]) < 0.05 and abs(cc[1] - dc[1]) < 0.05,
           (p.mate, cc, dc))
    p.commit()
    e0 = str(L["E"].Placement)
    p.add_selection(asm, "LE.EF.Face6", (62, 32, 17))
    p.add_selection(asm, "LA.AF.Face1", (0, 20, 5))
    p.set_type("lock")
    record("mate PM: Lock keeps the component where it is", p.mate == "lock" and str(L["E"].Placement) == e0, str(L["E"].Placement))
    p.discard()
    n_joints = len([o for o in UtilsAssembly.getJointGroup(asm).Group if hasattr(o, "JointType")])
    record("mate PM: discard leaves no joint", n_joints == 2 and str(L["E"].Placement) == e0, n_joints)
    p.accept()
    Gui.Control.closeDialog()
    QtWidgets.QApplication.processEvents()
    record("mate PM: OK closes, mates kept", not Gui.Control.activeDialog() and matepm._PANEL["p"] is None and
           [mates.mate_of(o) for o in UtilsAssembly.getJointGroup(asm).Group if hasattr(o, "JointType")] == ["distance", "concentric"],
           [o.Label for o in UtilsAssembly.getJointGroup(asm).Group])
    App.closeDocument(doc.Name)


@step(1200)
def t_mates_advanced():
    from freeworks import mates, matepm
    import JointObject, UtilsAssembly
    doc = App.newDocument("FWMates2")

    def body(name, feats):
        b = doc.addObject("PartDesign::Body", name)
        for kind, dims, base in feats:
            f = b.newObject("PartDesign::" + kind, name + kind)
            if "Box" in kind:
                f.Length, f.Width, f.Height = dims
            else:
                f.Radius, f.Height = dims
            f.Placement.Base = App.Vector(*base)
        b.Visibility = False
        return b
    G = body("G", [("AdditiveBox", (40, 20, 20), (0, 0, 0)), ("SubtractiveBox", (10, 20, 10), (15, 0, 10))])
    T = body("T", [("AdditiveBox", (6, 10, 10), (0, 0, 0))])
    C1 = body("C1", [("AdditiveCylinder", (10, 10), (0, 0, 0))])
    C2 = body("C2", [("AdditiveCylinder", (5, 10), (0, 0, 0))])
    R = body("R", [("AdditiveBox", (60, 8, 8), (0, 0, 0))])
    H1 = body("H1", [("AdditiveBox", (20, 20, 4), (0, 0, 0))])
    H2 = body("H2", [("AdditiveBox", (20, 20, 4), (0, 0, 0))])
    doc.recompute()
    asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
    asm.Type = "Assembly"
    pos = {"G": (0, 0, 0), "T": (50, 5, 12), "C1": (0, 60, 0), "C2": (40, 60, 0), "R": (0, 100, 0), "H1": (0, 140, 0), "H2": (40, 140, 0)}
    L = {}
    for b in (G, T, C1, C2, R, H1, H2):
        l = asm.newObject("App::Link", "L" + b.Name)
        l.LinkedObject = b
        l.Placement.Base = App.Vector(*pos[b.Name])
        L[b.Name] = l
    doc.recompute()
    gj = UtilsAssembly.getJointGroup(asm).newObject("App::FeaturePython", "GroundedJoint")
    JointObject.GroundedJoint(gj, L["G"])
    JointObject.ViewProviderGroundedJoint(gj.ViewObject)
    doc.recompute()

    def face(body, nx, x):
        tip = body.Tip
        for i, f in enumerate(tip.Shape.Faces, 1):
            n = f.normalAt(0, 0)
            if abs(n.x - nx) < 1e-6 and abs(f.CenterOfMass.x - x) < 1e-6:
                return "%s.Face%d" % (tip.Name, i), f.CenterOfMass
        return None, None
    Gui.Selection.clearSelection()
    matepm.start()
    p = matepm._PANEL["p"]
    g1, gp1 = face(G, 1, 15)
    g2, gp2 = face(G, -1, 25)
    t1, tp1 = face(T, -1, 0)
    t2, tp2 = face(T, 1, 6)
    p.set_type("width")
    for sub, pt, ln in ((g1, gp1, "LG"), (g2, gp2, "LG"), (t1, tp1 + L["T"].Placement.Base, "LT"), (t2, tp2 + L["T"].Placement.Base, "LT")):
        p.add_selection(asm, "%s.%s" % (ln, sub), pt)
    bbT = _bbl(L["T"])
    record("width mate: tab centred in the groove", p.mate == "width" and abs((bbT[0] + bbT[3]) / 2 - 20) < 0.05 and abs(bbT[0] - 17) < 0.05,
           (p.mate, bbT, p.hint.text()))
    p.commit()
    p.add_selection(asm, "LC1.C1AdditiveCylinder.Face1", (10, 65, 5))
    p.add_selection(asm, "LC2.C2AdditiveCylinder.Face1", (45, 60, 5))
    p.set_type("gear")
    j = p.joint
    record("gear mate: Gears joint with radii from geometry", j is not None and j.JointType == "Gears" and abs(_v(j.Distance) - 10) < 1e-6
           and abs(_v(j.Distance2) - 5) < 1e-6 and abs(p.value.value() - 0.5) < 1e-6, j and (j.JointType, _v(j.Distance), _v(j.Distance2)))
    p.flip()
    record("gear mate: flip = reverse direction", j is not None and j.JointType == "Belt", j and j.JointType)
    p.discard()
    p.add_selection(asm, "LR.RAdditiveBox.Edge1", (30, 100, 0))
    p.add_selection(asm, "LC2.C2AdditiveCylinder.Face1", (45, 60, 5))
    p.set_type("rack_pinion")
    j = p.joint
    record("rack pinion mate: pitch diameter from the pinion", j is not None and j.JointType == "RackPinion" and abs(_v(j.Distance) - 5) < 1e-6
           and j.Reference1[0].Name == "LR", j and (j.JointType, _v(j.Distance)))
    p.discard()
    p.add_selection(asm, "LC1.C1AdditiveCylinder.Face1", (10, 65, 5))
    p.add_selection(asm, "LC2.C2AdditiveCylinder.Face1", (45, 60, 5))
    p.set_type("concentric")
    p.commit()
    p.add_selection(asm, "LC1.C1AdditiveCylinder.Face2", (0, 60, 10))
    p.add_selection(asm, "LC2.C2AdditiveCylinder.Face3", (40, 60, 0))
    record("limit distance: offered once a Concentric mate exists", "limit_distance" in p.allowed_now(), p.allowed_now())
    p.vmin.setValue(2)
    p.vmax.setValue(12)
    p.set_type("limit_distance")
    j = p.joint
    ok = j is not None and j.JointType == "Cylindrical" and j.EnableLengthMin and j.EnableLengthMax and abs((_v(j.LengthMax) - _v(j.LengthMin)) - 10) < 1e-6
    record("limit distance: limits set on the Concentric joint", ok, j and (_v(j.LengthMin), _v(j.LengthMax)))
    p.commit()
    record("limit distance: listed as LimitDistance on Concentric1", p.list.item(p.list.count() - 1).text().startswith("LimitDistance on Concentric1"),
           p.list.item(p.list.count() - 1).text())
    p.add_selection(asm, "LH1.H1AdditiveBox.Face6", (10, 150, 4))
    p.add_selection(asm, "LH2.H2AdditiveBox.Face5", (50, 150, 0))
    p.set_type("hinge")
    p.commit()
    s1, c1 = face(H1, 1, 20)
    s2, c2 = face(H2, 1, 20)
    p.add_selection(asm, "LH1." + s1, c1 + L["H1"].Placement.Base)
    p.add_selection(asm, "LH2." + s2, c2 + L["H2"].Placement.Base)
    p.vmin.setValue(0)
    p.vmax.setValue(90)
    p.set_type("limit_angle")
    j = p.joint
    record("limit angle: limits set on the Hinge joint", j is not None and j.JointType == "Revolute" and j.EnableAngleMin
           and abs((_v(j.AngleMax) - _v(j.AngleMin)) - 90) < 1e-6, j and (j.JointType, _v(j.AngleMin), _v(j.AngleMax)))
    p.commit()
    p.accept()
    Gui.Control.closeDialog()
    QtWidgets.QApplication.processEvents()
    App.closeDocument(doc.Name)


@step(1200)
def t_assembly_tree():
    from freeworks import asmtree, mates, matepm
    import JointObject, UtilsAssembly
    doc = App.newDocument("FWTree")

    def body(name, dims):
        b = doc.addObject("PartDesign::Body", name)
        f = b.newObject("PartDesign::AdditiveBox", name + "F")
        f.Length, f.Width, f.Height = dims
        b.Visibility = False
        return b
    base = body("Base", (40, 40, 10))
    blk = body("Block", (10, 10, 10))
    asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
    asm.Type = "Assembly"
    l1 = asm.newObject("App::Link", "Link")
    l1.LinkedObject = base
    l1.Label = "Base"
    l2 = asm.newObject("App::Link", "Link001")
    l2.LinkedObject = blk
    l2.Placement.Base = App.Vector(60, 0, 20)
    l3 = asm.newObject("App::Link", "Link002")
    l3.LinkedObject = blk
    l3.Label = "Block001"
    l3.Placement.Base = App.Vector(90, 0, 20)
    doc.recompute()
    gj = UtilsAssembly.getJointGroup(asm).newObject("App::FeaturePython", "GroundedJoint")
    JointObject.GroundedJoint(gj, l1)
    JointObject.ViewProviderGroundedJoint(gj.ViewObject)
    Gui.Control.closeDialog()
    doc.recompute()
    asmtree.sweep(doc)
    labels = sorted(o.Label for o in (l1, l2, l3))
    record("assembly tree: instance names + (f) for fixed", labels == ["(f) Base<1>", "Block<1>", "Block<2>"], labels)
    record("assembly tree: Joints folder called Mates", UtilsAssembly.getJointGroup(asm).Label == "Mates", UtilsAssembly.getJointGroup(asm).Label)
    jg = UtilsAssembly.getJointGroup(asm)
    j = jg.newObject("App::FeaturePython", "Joint")
    JointObject.Joint(j, JointObject.JointTypes.index("Revolute"))
    JointObject.ViewProviderJoint(j.ViewObject)
    j.Label = "Revolute"
    comp, sub = UtilsAssembly.getComponentReference(asm, asm, "Link.BaseF.Face6")
    comp2, sub2 = UtilsAssembly.getComponentReference(asm, asm, "Link001.BlockF.Face5")
    j.Proxy.setJointConnectors(j, [[comp, [sub, sub]], [comp2, [sub2, sub2]]])
    doc.recompute()
    asmtree.sweep(doc)
    record("assembly tree: FreeCAD joint renamed like a SOLIDWORKS mate", j.Label.startswith("Hinge1 (Base<1>,Block<1>)"), j.Label)
    doc.removeObject(j.Name)
    doc.recompute()
    Gui.Selection.clearSelection()
    matepm.start()
    p = matepm._PANEL["p"]
    p.add_selection(asm, "Link.BaseF.Face6", (20, 20, 10))
    p.add_selection(asm, "Link001.BlockF.Face5", (65, 5, 20))
    p.accept()
    Gui.Control.closeDialog()
    QtWidgets.QApplication.processEvents()
    mate = [o for o in jg.Group if getattr(o, "MateType", "")][0]
    record("mate label uses component names without (f)", mate.Label == "Coincident1 (Base<1>,Block<1>)", mate.Label)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(mate)
    matepm.edit_selected()
    p = matepm._PANEL["p"]
    ok = p is not None and p.edit_name == mate.Name and p.mate == "coincident"
    record("edit mate: opens the PropertyManager on the mate", ok, p and (p.edit_name, p.mate))
    if ok:
        p.set_type("distance")
        p.value.setValue(12.0)
        p.commit()
        for _ in range(5):
            QtWidgets.QApplication.processEvents()
        js = [o for o in jg.Group if getattr(o, "MateType", "")]
        record("edit mate: type/value changed in place, PM closed", len(js) == 1 and js[0].MateType == "distance"
               and abs(_bbl(l2)[2] - 22) < 0.05 and not Gui.Control.activeDialog(), ([o.Label for o in js], _bbl(l2), bool(Gui.Control.activeDialog())))
    Gui.Control.closeDialog()
    App.closeDocument(doc.Name)


@step(1200)
def t_move_replace():
    from freeworks import movepm, replace, mates
    import JointObject, UtilsAssembly
    doc = App.newDocument("FWMove")

    def body(name, kind, dims):
        b = doc.addObject("PartDesign::Body", name)
        f = b.newObject("PartDesign::Additive" + ("Box" if kind == "box" else "Cylinder"), name + "F")
        if kind == "box":
            f.Length, f.Width, f.Height = dims
        else:
            f.Radius, f.Height = dims
        b.Visibility = False
        return b
    base = body("Base", "box", (40, 40, 10))
    blk = body("Block", "box", (10, 10, 10))
    blk2 = body("Block2", "box", (12, 12, 12))
    post = body("Post", "cyl", (5, 20))
    arm = body("Arm", "box", (30, 4, 4))
    wall = body("Wall", "box", (5, 40, 20))
    asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
    asm.Type = "Assembly"
    L = {}
    for b, pos in ((base, (0, 0, 0)), (blk, (60, 15, 0)), (post, (0, 100, 0)), (arm, (10, 98, 8)), (wall, (-30, 80, 0))):
        l = asm.newObject("App::Link", "L" + b.Name)
        l.LinkedObject = b
        l.Placement.Base = App.Vector(*pos)
        L[b.Name] = l
    doc.recompute()
    gj = UtilsAssembly.getJointGroup(asm).newObject("App::FeaturePython", "GroundedJoint")
    JointObject.GroundedJoint(gj, L["Base"])
    JointObject.ViewProviderGroundedJoint(gj.ViewObject)
    doc.recompute()
    t, hit = movepm.apply_move(asm, L["Block"], "translate", 1.0, vec=App.Vector(-50, 0, 0), collide=True)
    bb = _bbl(L["Block"])
    record("collision detection: move stops at first contact", hit and hit[0][0] == L["Base"] and abs(bb[0] - 40) < 0.02, (bb, [h[0].Label for h in hit]))
    L["Block"].Placement.Base = App.Vector(60, 15, 0)
    doc.recompute()
    t, hit = movepm.apply_move(asm, L["Block"], "translate", 1.0, vec=App.Vector(-50, 0, 30), collide=True)
    record("collision detection: free path moves all the way", not hit and abs(_bbl(L["Block"])[0] - 10) < 0.01, _bbl(L["Block"]))
    ref = mates.make_ref(asm, asm, "LPost.PostF.Face1", (5, 100, 10))
    ax = movepm.axis_of(ref)
    record("rotate: axis from a cylindrical face (assembly coordinates)", ax is not None and abs(ax[0].x) < 1e-6 and abs(ax[0].y - 100) < 1e-6
           and abs(abs(ax[1].z) - 1) < 1e-6, ax and (ax[0], ax[1]))
    t, hit = movepm.apply_move(asm, L["Arm"], "rotate", 180.0, axis=ax, collide=True)
    import Part
    over = Part.getShape(L["Arm"]).common(Part.getShape(L["Wall"])).Volume
    record("collision detection: rotation stops at the wall", hit and hit[0][0] == L["Wall"] and 0 < t < 1 and over < 1e-2,
           (round(t * 180.0, 2), over))
    # replace components keeps the mate
    r1 = mates.make_ref(asm, asm, "LBase.BaseF.Face6", (20, 20, 10))
    L["Block"].Placement.Base = App.Vector(60, 15, 30)
    doc.recompute()
    r2 = mates.make_ref(asm, asm, "LBlock.BlockF.Face5", (65, 20, 30))
    doc.openTransaction("Mate")
    j = mates.create(asm, "coincident", [r1, r2])
    doc.commitTransaction()
    ok_before = abs(_bbl(L["Block"])[2] - 10) < 0.02
    ok, bad = replace.replace(asm, L["Block"], blk2)
    bb = _bbl(L["Block"])
    record("replace components: new part, mate re-attached", ok_before and not bad and L["Block"].LinkedObject == blk2
           and abs(bb[2] - 10) < 0.02 and abs((bb[3] - bb[0]) - 12) < 0.01 and "Block2F" in j.Reference2[1][0],
           (ok, bad, bb, j.Reference2[1]))
    record("replace components: instance renamed", L["Block"].Label.startswith("Block2<"), L["Block"].Label)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, asm.Name, "LWall.")
    movepm.start(False)
    mp = movepm._PANEL["p"]
    ok = mp is not None and mp.comp == L["Wall"]
    if ok:
        mp.d[2].setValue(5.0)
        mp.apply()
        txt = mp.result.text()
        ok = "Moved 5.00 mm" in txt and abs(_bbl(L["Wall"])[2] - 5) < 0.01
        mp.accept()
    else:
        txt = mp and mp.comp
    Gui.Control.closeDialog()
    record("move component PM: pick component, By Delta XYZ, Apply", ok, txt)
    App.closeDocument(doc.Name)


@step(1000)
def t_equations():
    from freeworks import equations as eq, equationsui
    import Part, Sketcher
    doc = App.newDocument("FWEq")
    b = doc.addObject("PartDesign::Body", "Body")
    sk = b.newObject("Sketcher::SketchObject", "Sketch")
    sk.Label = "Sketch1"
    pts = [App.Vector(0, 0, 0), App.Vector(40, 0, 0), App.Vector(40, 20, 0), App.Vector(0, 20, 0)]
    for i in range(4):
        sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4]))
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", 0))
    sk.addConstraint(Sketcher.Constraint("Horizontal", 2))
    sk.addConstraint(Sketcher.Constraint("Vertical", 1))
    sk.addConstraint(Sketcher.Constraint("Vertical", 3))
    sk.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
    sk.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, 40))
    sk.addConstraint(Sketcher.Constraint("DistanceY", 1, 1, 1, 2, 20))
    pad = b.newObject("PartDesign::Pad", "Pad")
    pad.Label = "Boss-Extrude1"
    pad.Profile = sk
    pad.Length = 10
    doc.recompute()
    eq.set_variable(doc, "A", "50")
    eq.set_variable(doc, "B", '= "A" / 5')
    eq.set_equation(doc, '"D1@Sketch1"', '"A"')
    eq.set_equation(doc, '"D1@Boss-Extrude1"', '"B" + 2')
    doc.recompute()
    vol = b.Shape.Volume
    record("equations: global variables drive sketch + feature", abs(vol - 50 * 20 * 12) < 1e-6, vol)
    eq.set_variable(doc, "A", "60")
    doc.recompute()
    record("equations: change a global variable -> model updates", abs(b.Shape.Volume - 60 * 20 * 14) < 1e-6, b.Shape.Volume)
    names = sorted(n for n, *_ in eq.equations(doc))
    record("equations: SOLIDWORKS names", names == ["D1@Boss-Extrude1", "D1@Sketch1"], names)
    shown = [eq.to_solidworks(ex) for _, _, _, ex, _ in eq.equations(doc)]
    record("equations: shown in SOLIDWORKS syntax", sorted(shown) == ['"A"', '"B" + 2'], shown)
    record("equations: dimension picker", "D2@Sketch1" in eq.dimension_names(doc) and "D1@Boss-Extrude1" in eq.dimension_names(doc),
           eq.dimension_names(doc))
    d = equationsui.EquationsDialog.open()
    gv = d.g_vars
    rows = [gv.child(i).text(0) for i in range(gv.childCount())]
    ok = rows[:2] == ["A", "B"] and d.g_eq.childCount() == 3
    add = d.g_eq.child(d.g_eq.childCount() - 1)
    add.setText(0, '"D2@Sketch1"')
    add.setText(1, '"A" / 4')
    QtWidgets.QApplication.processEvents()
    doc.recompute()
    record("equations dialog: lists variables and equations", ok, (rows, d.g_eq.childCount()))
    record("equations dialog: Add equation row drives the model", abs(b.Shape.Volume - 60 * 15 * 14) < 1e-6, (b.Shape.Volume, d.msg.text()))
    d.ok()
    App.closeDocument(doc.Name)


@step(1000)
def t_configurations():
    from freeworks import configurations as cf, configui, massprops, materials
    doc = App.newDocument("FWCfg")
    b = doc.addObject("PartDesign::Body", "Body")
    bx = b.newObject("PartDesign::AdditiveBox", "Box")
    bx.Label = "Boss-Box1"
    bx.Length, bx.Width, bx.Height = 40, 20, 10
    hole = b.newObject("PartDesign::SubtractiveCylinder", "Hole")
    hole.Label = "Cut-Hole1"
    hole.Radius, hole.Height = 4, 10
    hole.Placement.Base = App.Vector(20, 10, 0)
    doc.recompute()
    v_full = b.Shape.Volume
    cf.add_column(doc, "D1@Boss-Box1")
    cf.add_column(doc, "$STATE@Cut-Hole1")
    cf.add(doc, "Long")
    cf.set_cell(doc, "Long", "D1@Boss-Box1", "100")
    cf.set_cell(doc, "Long", "$STATE@Cut-Hole1", "S")
    errs = cf.activate(doc, "Long")
    record("configurations: activate applies dimension + suppression", not errs and abs(b.Shape.Volume - 100 * 20 * 10) < 1e-6,
           (errs, b.Shape.Volume))
    cf.activate(doc, "Default")
    record("configurations: back to Default", abs(b.Shape.Volume - v_full) < 1e-6, b.Shape.Volume)
    bx.Height = 12          # change while Default is active: Height is not configured -> shared
    doc.recompute()
    cf.activate(doc, "Long")
    record("configurations: unconfigured values are shared", abs(b.Shape.Volume - 100 * 20 * 12) < 1e-6, b.Shape.Volume)
    bx.Length = 120         # configured value changed in this configuration -> kept for Long only
    doc.recompute()
    cf.activate(doc, "Default")
    cf.activate(doc, "Long")
    record("configurations: change kept in this configuration only", abs(bx.Length.Value - 120) < 1e-9, bx.Length.Value)
    path = os.path.join(OUT, "design_table.csv")
    with open(path, "w") as f:
        f.write(",D1@Boss-Box1,D2@Boss-Box1,$STATE@Cut-Hole1\nSmall,30,15,U\nWide,30,40,S\n")
    first = cf.import_table(doc, path)
    cf.activate(doc, "Wide")
    record("design table: import creates configurations", first == "Small" and "Wide" in cf.names(doc)
           and abs(b.Shape.Volume - 30 * 40 * 12) < 1e-6, (cf.names(doc), b.Shape.Volume))
    m = massprops.compute(massprops.collect(use_selection=False))["mass"]
    record("design table: mass properties follow the configuration", abs(m - 30 * 40 * 12 * 0.001) < 1e-6, m)
    out = cf.export_table(doc, os.path.join(OUT, "design_table_out.csv"))
    record("design table: export", "Wide" in open(out).read(), out)
    d = configui.ConfigurationManager.open()
    dk = configui._DOCK.get("d")
    from freeworks import shell
    record("ConfigurationManager tab lists configurations + table", d.list.count() == 4 and d.grid.columnCount() == 3,
           (d.list.count(), d.grid.columnCount()))
    record("ConfigurationManager is a tab next to the FeatureManager", dk is not None and dk in mw().tabifiedDockWidgets(shell._dock("Model")),
           dk and [x.windowTitle() for x in mw().tabifiedDockWidgets(dk)])
    d.close()
    App.closeDocument(doc.Name)


@step(1500)
def t_pm_terms():
    from freeworks import pmskin, naming
    doc = App.newDocument("FWSkin")
    b = doc.addObject("PartDesign::Body", "Body")
    import Part, Sketcher
    sk = b.newObject("Sketcher::SketchObject", "Sketch")
    sk.AttachmentSupport = [(b.Origin.OriginFeatures[3], "")]
    sk.MapMode = "FlatFace"
    sk.addGeometry(Part.Circle(App.Vector(), App.Vector(0, 0, 1), 10))
    pad = b.newObject("PartDesign::Pad", "Pad")
    pad.Profile = sk
    pad.Length = 10
    doc.recompute()
    Gui.ActiveDocument.setEdit(pad.Name)
    STATE["skin_doc"] = doc.Name


@step(1500)
def t_pm_terms_check():
    from freeworks import pmskin
    root = pmskin._task_root()
    texts = set()
    if root is not None:
        for w in root.findChildren(QtWidgets.QComboBox):
            texts.update(w.itemText(i) for i in range(w.count()))
        for w in root.findChildren(QtWidgets.QLabel):
            texts.add(w.text().rstrip(":"))
    shot("05_extrude_pm")
    want = {"Blind", "Through All", "Up To Next", "Up To Surface", "Up To Body", "Direction 1", "End Condition"}
    record("PropertyManager terms: extrude end conditions renamed", want <= texts and "Dimension" not in texts and "To first" not in texts,
           sorted(t for t in texts if t)[:40])
    record("PropertyManager terms: Depth instead of Length", "Depth" in texts, "Depth" in texts)
    from freeworks import shell
    c = shell._S.get("corner")
    record("confirmation corner: shown while a PropertyManager is open", c is not None and c.isVisible()
           and c.x() > shell._S["corner"].mdi.width() // 2, c and (c.isVisible(), c.x()))
    if c is not None:
        c.accept()
        for _ in range(10):
            QtWidgets.QApplication.processEvents()
        record("confirmation corner: check mark accepts the PropertyManager", not Gui.Control.activeDialog(), bool(Gui.Control.activeDialog()))
    t = dict(pmskin.TITLES)
    t.update(pmskin.HOLE)
    record("PropertyManager terms: Hole Wizard table", pmskin._map("Depth type:", t) == "End Condition:" and pmskin._map("Dimension", t) == "Blind"
           and pmskin._map("Hole parameters", t) == "Hole Wizard", (pmskin._map("Depth type:", t), pmskin._map("Hole parameters", t)))
    try:
        Gui.ActiveDocument.resetEdit()
    except Exception:
        pass
    Gui.Control.closeDialog()
    App.closeDocument(STATE["skin_doc"])


@step(2500)
def t_drawings():
    from freeworks import drawing, materials, naming
    import xml.dom.minidom
    tp = drawing.templates()
    ok = len(tp) == 11
    for f in tp:
        d = xml.dom.minidom.parse(os.path.join(drawing.TEMPLATE_DIR, f))
        eds = [t.getAttribute("freecad:editable") for t in d.getElementsByTagName("text") if t.getAttribute("freecad:editable")]
        ok = ok and {"title", "material", "weight", "drawing_number", "scale", "sheet"} <= set(eds)
    record("drawings: 11 sheet formats with title-block fields", ok, tp)
    g = App.ParamGet(drawing.TD_FILES)
    record("drawings: FreeWorks sheet formats are TechDraw's default", g.GetString("TemplateFile", "").endswith(drawing.DEFAULT_ISO),
           g.GetString("TemplateFile", ""))
    part = App.newDocument("Bracket")
    b = part.addObject("PartDesign::Body", "Body")
    bx = b.newObject("PartDesign::AdditiveBox", "Box")
    bx.Length, bx.Width, bx.Height = 81, 57, 43
    part.recompute()
    materials.apply([b], materials.card_by_name("AISI 1020")["uuid"])
    STATE["dw_part"] = part.Name
    dw = naming.new_document("drawing")
    STATE["dw_doc"] = dw.Name
    page = drawing.page_of(dw)
    record("drawings: new drawing uses a FreeWorks sheet format", page is not None and drawing.is_freeworks_template(page),
           page and page.Template.Template)
    vs = drawing.standard_3view(page, b)
    roles = {v.StandardView: v for v in vs}
    f, t, r = roles.get("Front"), roles.get("Top"), roles.get("Right")
    ok = f and t and r and float(t.Y) < float(f.Y) and float(r.X) < float(f.X) and abs(float(t.X) - float(f.X)) < 1e-6
    record("drawings: Standard 3 View = Front, Top, Right in first-angle layout (ISO)", ok,
           [(v.StandardView, round(float(v.X), 1), round(float(v.Y), 1), v.Scale) for v in vs])
    v = drawing.model_view(page, b, "Isometric")
    dw.recompute()
    et = dict(page.Template.EditableTexts)
    record("drawings: title block material + weight from the part", et.get("material") == "AISI 1020" and et.get("weight") == "1.568 kg"
           and et.get("drawing_number") == "Bracket", {k: et.get(k) for k in ("material", "weight", "drawing_number")})


@step(2500)
def t_model_items():
    from freeworks import drawing
    import Part, Sketcher
    part = App.getDocument(STATE["dw_part"])
    b2 = part.addObject("PartDesign::Body", "Body2")
    sk = b2.newObject("Sketcher::SketchObject", "Sketch")
    sk.AttachmentSupport = [(b2.Origin.OriginFeatures[3], "")]
    sk.MapMode = "FlatFace"
    pts = [App.Vector(0, 0, 0), App.Vector(81, 0, 0), App.Vector(81, 57, 0), App.Vector(0, 57, 0)]
    for i in range(4):
        sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4]))
    sk.addGeometry(Part.Circle(App.Vector(40, 28, 0), App.Vector(0, 0, 1), 10))
    sk.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, 81))
    sk.addConstraint(Sketcher.Constraint("DistanceY", 1, 1, 1, 2, 57))
    sk.addConstraint(Sketcher.Constraint("Radius", 4, 10))
    pad = b2.newObject("PartDesign::Pad", "Pad")
    pad.Profile = sk
    pad.Length = 43
    part.recompute()
    dw = App.getDocument(STATE["dw_doc"])
    page = drawing.page_of(dw)
    v = drawing.model_view(page, b2, "Top", 0.25, 0.3)
    dw.recompute()
    STATE["mi_view"] = v.Name


@step(1500)
def t_model_items_check():
    from freeworks import drawing
    dw = App.getDocument(STATE["dw_doc"])
    v = dw.getObject(STATE["mi_view"])
    dims = drawing.model_items(v)
    types = sorted(d.Type for d in dims)
    record("drawings: Model Items inserts the sketch dimensions", types == ["DistanceX", "DistanceY", "Radius"], types)
    drawing.set_display_style([v], "hlv")
    record("drawings: display style Hidden Lines Visible", v.HardHidden is True, v.HardHidden)
    record("drawings: centre marks on by default", App.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Decorations").GetBool("ShowCenterMarks", False))


@step(500)
def t_drawings_close():
    for k in ("dw_doc", "dw_part"):
        try:
            App.closeDocument(STATE[k])
        except Exception:
            pass
    record("drawings: close", True)


@step(1500)
def t_relations():
    import Part, Sketcher
    doc = App.newDocument("FWRel")
    b = doc.addObject("PartDesign::Body", "Body")
    sk = b.newObject("Sketcher::SketchObject", "Sketch")
    sk.AttachmentSupport = [(b.Origin.OriginFeatures[3], "")]
    sk.MapMode = "FlatFace"
    pts = [App.Vector(0, 0, 0), App.Vector(40, 0, 0), App.Vector(40, 20, 0), App.Vector(0, 20, 0)]
    for i in range(4):
        sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4]))
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", 0))
    sk.addConstraint(Sketcher.Constraint("Horizontal", 2))
    sk.addConstraint(Sketcher.Constraint("Vertical", 1))
    sk.addConstraint(Sketcher.Constraint("Vertical", 3))
    sk.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, 40))
    doc.recompute()
    Gui.ActiveDocument.setEdit(sk.Name)
    STATE["rel_doc"] = doc.Name


@step(1000)
def t_relations_check():
    from freeworks import relations
    doc = App.getDocument(STATE["rel_doc"])
    sk = doc.getObject("Sketch")
    p = relations.RelationsPanel.open()
    n_all = p.table.topLevelItemCount() if p else 0
    p.filter.setCurrentIndex(3)
    n_dims = p.table.topLevelItemCount()
    st = relations.status(sk)
    record("relations: Display/Delete lists relations with SOLIDWORKS names", n_all == 9 and n_dims == 1 and
           p.table.topLevelItem(0).text(0).startswith("Horizontal distance"), (n_all, n_dims, p.table.topLevelItem(0).text(0)))
    record("relations: sketch status under defined", st.startswith("Under Defined"), st)
    p.filter.setCurrentIndex(0)
    p.table.topLevelItem(0).setSelected(True)
    p.delete()
    record("relations: delete selected", len(sk.Constraints) == 8 and p.table.topLevelItemCount() == 8, len(sk.Constraints))
    p.close()
    from freeworks import pmskin
    root = pmskin._task_root()
    texts = set()
    if root is not None:
        for w in root.findChildren(QtWidgets.QLabel):
            texts.add(w.text())
        for w in root.findChildren(QtWidgets.QAbstractButton):
            texts.add(w.text())
    for _ in range(3):
        pmskin._pass()
        QtWidgets.QApplication.processEvents()
    texts = set()
    if root is not None:
        for w in root.findChildren(QtWidgets.QLabel):
            texts.add(w.text())
        for w in root.findChildren(QtWidgets.QAbstractButton):
            texts.add(w.text())
    blob = " | ".join(sorted(t for t in texts if t and ("onstrain" in t or "reedom" in t or "Defined" in t or "Relations" in t)))
    record("sketch panel in SOLIDWORKS terms (Relations, Under Defined)", "Under Defined" in blob and "Under constrained" not in blob,
           blob[:600])
    Gui.ActiveDocument.resetEdit()
    App.closeDocument(doc.Name)


@step(800)
def t_document_properties():
    from freeworks import optionsdlg, drawing, massprops
    doc = App.newDocument("FWOpt")
    d = optionsdlg.OptionsDialog.open("document")
    d.units.setCurrentIndex(3)
    d.dec.setValue(3)
    d.std.setCurrentText("ANSI")
    d.ok()
    ok = optionsdlg.doc_units(doc) == "IPS" and doc.UnitSystem.startswith("Imperial decimal") and massprops.settings()[:2] == ("IPS", 3)
    record("document properties: IPS units stored in the document", ok, (doc.UnitSystem, massprops.settings()))
    record("document properties: ANSI drafting standard -> ANSI sheet, third angle",
           App.ParamGet(drawing.TD_FILES).GetString("TemplateFile", "").endswith(drawing.DEFAULT_ANSI)
           and App.ParamGet(optionsdlg.TD_GENERAL).GetInt("ProjectionAngle", 0) == 1)
    d = optionsdlg.OptionsDialog.open("document")
    d.units.setCurrentIndex(0)
    d.dec.setValue(2)
    d.std.setCurrentText("ISO")
    d.ok()
    record("document properties: back to MMGS / ISO", optionsdlg.doc_units(doc) == "MMGS" and massprops.settings()[:2] == ("MMGS", 2),
           doc.UnitSystem)
    App.closeDocument(doc.Name)

@step(800)
def t_field_fixes():
    """Windows field test (v1.5.4): smooth view, rotation centre, view cube, plane picking."""
    v = App.ParamGet("User parameter:BaseApp/Preferences/View")
    record("view: no line-smoothing anti-aliasing (opaque planes, slow drivers)", v.GetInt("AntiAliasing", -1) in (0, 3), v.GetInt("AntiAliasing", -1))
    record("view: rotate about the model (Object center)", v.GetInt("RotationMode", -1) == 2, v.GetInt("RotationMode", -1))
    record("view: view cube shown", v.GetBool("ShowNaviCube", False), v.GetBool("ShowNaviCube", False))
    from freeworks import gestures
    gestures._last_input[0] = time.monotonic()
    busy = gestures.should_wait("test")
    gestures._last_input[0] = 0.0
    record("smoothness: periodic work waits while the user drags/zooms", busy and not gestures.should_wait("test"), busy)
    from freeworks import naming, commands
    doc = naming.new_document("part")
    STATE["pick_doc"] = doc.Name
    cam = Gui.activeView().getCameraNode()
    h = cam.height.getValue() if hasattr(cam, "height") else None
    record("new part: view shows ~100 mm around the origin (not a 4 mm empty fit)", h is not None and 50 <= h <= 500, h)
    Gui.Selection.clearSelection()
    commands.run_key("sketch")
    for _ in range(10):
        QtWidgets.QApplication.processEvents()
    from freeworks import shell
    d = shell._dock("Tasks")
    lws = [w for w in d.widget().findChildren(QtWidgets.QListWidget) if w.property("fw_quickpick")] if d and d.widget() else []
    record("sketch: plane list picks with one click", bool(Gui.Control.activeDialog()) and bool(lws), (bool(Gui.Control.activeDialog()), len(lws)))
    shot("07_plane_pick")
    if lws and lws[0].count():
        it = lws[0].item(1 if lws[0].count() > 1 else 0)     # Front Plane
        STATE["pick_label"] = it.text()
        it.setSelected(True)
        lws[0].itemClicked.emit(it)


@step(1500)
def t_field_fixes_check():
    from freeworks import context, shell
    sk = context.edited_sketch()
    record("sketch: one click on a plane opens the sketch", sk is not None, (STATE.get("pick_label"), sk and sk.Label))
    c = shell._S.get("corner")
    ok = c is not None and c.isVisible() and c.x() + c.width() <= c.mdi.width() - 150
    record("confirmation corner: left of the view cube", ok, c and (c.isVisible(), c.x(), c.width(), c.mdi.width()))
    try:
        Gui.ActiveDocument.resetEdit()
    except Exception:
        pass
    Gui.Control.closeDialog()
    App.closeDocument(STATE["pick_doc"])


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
