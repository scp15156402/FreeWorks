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
    p.value.setValue(15.0)
    p.set_type("distance")
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
