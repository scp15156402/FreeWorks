"""FreeWorks commands (FW_*).  Registered as real FreeCAD commands so they show
up in menus, the Customize dialog, macros and command search."""
import math
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import catalog, context, icon_path, log, safe, safe_slow, params

_registered = False


# ----------------------------------------------------------------- helpers
def run(name, *args):
    """Run a FreeCAD/FreeWorks command by name; returns False if unavailable."""
    try:
        c = Gui.Command.get(name)
        if c is None:
            return False
        if args:
            Gui.runCommand(name, *args)
        else:
            Gui.runCommand(name)
        return True
    except Exception as e:
        log("run %s failed: %s" % (name, e))
        return False


@safe_slow
def run_key(key):
    """Run a catalog entry by key."""
    e = catalog.C.get(key)
    if not e:
        return False
    cmd = catalog.first_existing(e)
    if cmd is None:
        msg("'%s' is not available - the add-on providing it is not installed." % e["label"])
        return False
    from . import sketchmode
    sketchmode.on_command(key)
    return run(cmd)


def msg(text, ms=4000):
    try:
        Gui.getMainWindow().statusBar().showMessage(text, ms)
    except Exception:
        pass


def view3d():
    v = Gui.activeView()
    return v if v is not None and hasattr(v, "getCamera") else None


def cursor_pos():
    return QtGui.QCursor.pos()


# ----------------------------------------------------------- camera history
_cam_stack = []


def push_view():
    v = view3d()
    if v is None:
        return
    try:
        cam = v.getCamera()
        if not _cam_stack or _cam_stack[-1] != cam:
            _cam_stack.append(cam)
            del _cam_stack[:-25]
    except Exception:
        pass


def prev_view():
    v = view3d()
    if v is None:
        return
    cur = None
    try:
        cur = v.getCamera()
    except Exception:
        pass
    while _cam_stack:
        cam = _cam_stack.pop()
        if cam != cur:
            v.setCamera(cam)
            return
    msg("No previous view")


def std_view(fn):
    def go():
        v = view3d()
        if v is None:
            return
        push_view()
        getattr(v, fn)()
        if params().GetBool("FitOnStandardView", False):
            v.fitAll()
    return go


_last_normal = [None, 0.0]


def normal_to():
    import time
    v = view3d()
    if v is None:
        return
    push_view()
    sel = Gui.Selection.getSelectionEx()
    sig = str([(s.ObjectName, s.SubElementNames) for s in sel])
    now = time.time()
    if sel:
        if _last_normal[0] == sig and now - _last_normal[1] < 6:
            # SolidWorks: clicking Normal To again flips to the opposite side
            rot = v.getCameraOrientation()
            v.setCameraOrientation(rot.multiply(App.Rotation(App.Vector(0, 1, 0), 180)))
        else:
            run("Std_AlignToSelection")
        _last_normal[:] = [sig, now]
    elif context.edited_sketch() is not None:
        run("Sketcher_ViewSketch")
    else:
        msg("Select a face or plane to view normal to")


# ---------------------------------------------------------------- features
def _sketch_then(cmd):
    sk = context.edited_sketch()
    if sk is not None:
        Gui.ActiveDocument.resetEdit()
        App.ActiveDocument.recompute()
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(sk)
    elif not Gui.Selection.getSelection():
        # SolidWorks: with nothing selected, Extrude uses the last sketch
        # that has not been consumed by a feature yet
        sk = _last_unused_sketch()
        if sk is not None:
            Gui.Selection.addSelection(sk)
    run(cmd)


def _last_unused_sketch():
    doc = App.ActiveDocument
    if doc is None:
        return None
    for o in reversed(doc.Objects):
        if o.isDerivedFrom("Sketcher::SketchObject"):
            if not [p for p in o.InList if p.isDerivedFrom("PartDesign::Feature")]:
                return o
            return None
    return None


def sketch_cmd():
    sk = context.edited_sketch()
    if sk is not None:
        exit_sketch()
        return
    sel = Gui.Selection.getSelection()
    if len(sel) == 1 and sel[0].isDerivedFrom("Sketcher::SketchObject"):
        Gui.ActiveDocument.setEdit(sel[0].Name)
        return
    if App.ActiveDocument is None:
        new_document("part")
    if not run("PartDesign_NewSketch"):
        run("Sketcher_NewSketch")


def edit_sketch():
    """Edit the sketch of the selected feature (or the selected sketch)."""
    for o in Gui.Selection.getSelection():
        sk = o if o.isDerivedFrom("Sketcher::SketchObject") else None
        if sk is None:
            prof = getattr(o, "Profile", None)
            if prof:
                sk = prof[0] if isinstance(prof, tuple) else prof
        if sk is not None and sk.isDerivedFrom("Sketcher::SketchObject"):
            Gui.Selection.clearSelection()
            Gui.ActiveDocument.setEdit(sk.Name)
            return
    msg("Select a sketch or a sketch-based feature")


def exit_sketch():
    gd = Gui.ActiveDocument
    if gd is not None and context.edited_sketch() is not None:
        gd.resetEdit()
        App.ActiveDocument.recompute()


def rebuild():
    doc = App.ActiveDocument
    if doc:
        doc.recompute()
        msg("Rebuild complete")


def force_rebuild():
    doc = App.ActiveDocument
    if doc:
        for o in doc.Objects:
            try:
                o.touch()
            except Exception:
                pass
        doc.recompute()
        msg("Force rebuild complete")


def roll_to_end():
    body = _active_body()
    if body is None:
        return
    feats = [o for o in body.Group if o.isDerivedFrom("PartDesign::Feature") and not o.isDerivedFrom("PartDesign::FeatureBase")]
    feats = [o for o in body.Group if o.isDerivedFrom("PartDesign::Feature")]
    if feats:
        body.Tip = feats[-1]
        App.ActiveDocument.recompute()


def _active_body():
    try:
        v = Gui.ActiveDocument.ActiveView
        b = v.getActiveObject("pdbody")
        if b:
            return b
    except Exception:
        pass
    doc = App.ActiveDocument
    if doc:
        bodies = [o for o in doc.Objects if o.isDerivedFrom("PartDesign::Body")]
        return bodies[0] if len(bodies) == 1 else None
    return None


def suppress():
    sel = [o for o in Gui.Selection.getSelection() if "Suppressed" in o.PropertiesList]
    if not sel:
        msg("Select a feature in the FeatureManager design tree to suppress / unsuppress")
        return
    App.ActiveDocument.openTransaction("Suppress")
    for o in sel:
        o.Suppressed = not o.Suppressed
    App.ActiveDocument.commitTransaction()
    App.ActiveDocument.recompute()


# ---------------------------------------------------------------- display
def draw_style(i):
    def go():
        run("Std_DrawStyle", i)
    return go


HIDE_SHOW_TYPES = [
    ("Planes", ("App::Plane", "PartDesign::Plane")),
    ("Axes", ("App::Line", "PartDesign::Line")),
    ("Points", ("App::Point", "PartDesign::Point")),
    ("Coordinate Systems", ("PartDesign::CoordinateSystem", "App::LocalCoordinateSystem")),
    ("Sketches", ("Sketcher::SketchObject",)),
]


def hide_show_menu():
    doc = App.ActiveDocument
    if doc is None:
        return
    m = QtWidgets.QMenu(Gui.getMainWindow())
    m.setObjectName("FreeWorksPopup")
    for name, types in HIDE_SHOW_TYPES:
        objs = [o for o in doc.Objects if any(o.isDerivedFrom(t) for t in types) and o.ViewObject]
        a = m.addAction("View " + name)
        a.setCheckable(True)
        a.setChecked(any(o.ViewObject.Visibility for o in objs))
        a.setEnabled(bool(objs))
        a.triggered.connect(lambda on, objs=objs: [setattr(o.ViewObject, "Visibility", on) for o in objs])
    m.exec_(cursor_pos())


SCENES = {
    "Gradient Light (FreeWorks default)": dict(mode="Gradient", top=(0.78, 0.84, 0.92), bottom=(1.0, 1.0, 1.0)),
    "Plain White": dict(mode="Simple", top=(1.0, 1.0, 1.0), bottom=(1.0, 1.0, 1.0)),
    "Gradient Grey": dict(mode="Gradient", top=(0.62, 0.65, 0.70), bottom=(0.95, 0.95, 0.96)),
    "Studio Dark": dict(mode="Gradient", top=(0.13, 0.14, 0.17), bottom=(0.33, 0.35, 0.40)),
    "Blueprint": dict(mode="Gradient", top=(0.20, 0.34, 0.60), bottom=(0.55, 0.68, 0.86)),
}


def rgba(c, a=1.0):
    r, g, b = [int(round(x * 255)) for x in c]
    return (r << 24) | (g << 16) | (b << 8) | int(a * 255)


def apply_scene(name):
    s = SCENES[name]
    p = App.ParamGet("User parameter:BaseApp/Preferences/View")
    p.SetBool("Simple", s["mode"] == "Simple")
    p.SetBool("Gradient", s["mode"] == "Gradient")
    p.SetBool("RadialGradient", False)
    p.SetBool("UseBackgroundColorMid", False)
    p.SetUnsigned("BackgroundColor", rgba(s["top"]))
    p.SetUnsigned("BackgroundColor2", rgba(s["top"]))
    p.SetUnsigned("BackgroundColor3", rgba(s["bottom"]))
    params().SetString("Scene", name)
    for d in (Gui.getDocument(n) for n in App.listDocuments()):
        for v in d.mdiViewsOfType("Gui::View3DInventor") if hasattr(d, "mdiViewsOfType") else []:
            try:
                v.redraw()
            except Exception:
                pass


def scene_menu():
    m = QtWidgets.QMenu(Gui.getMainWindow())
    cur = params().GetString("Scene", "Gradient Light (FreeWorks default)")
    for n in SCENES:
        a = m.addAction(n)
        a.setCheckable(True)
        a.setChecked(n == cur)
        a.triggered.connect(lambda _=False, n=n: apply_scene(n))
    m.exec_(cursor_pos())


def view_orientation_menu():
    from . import widgets
    widgets.ViewSelector.popup()


def add_relation():
    from . import widgets
    keys = [k for k in catalog.C if k.startswith("rel_")]
    widgets.popup_commands(keys, "Add Relations", only_active=True)


def mate_menu():
    """SOLIDWORKS Mate PropertyManager (FreeWorks). FreeCAD's joint tools stay in the Assembly tab."""
    from . import matepm
    matepm.start()


def shortcut_bar():
    from . import widgets
    widgets.ShortcutBar.show_for(context.current())


def magnify():
    from . import widgets
    widgets.Magnifier.start()


def search_commands():
    from . import shell
    shell.focus_search()


def options():
    from . import widgets
    widgets.OptionsDialog.open_dialog()


def toggle_filter_toolbar():
    from . import shell
    shell.toggle_filter_toolbar()


# ------------------------------------------------------------ new document
def new_document(kind=None):
    if kind is None:
        from . import widgets
        widgets.NewDocumentDialog.ask()
        return
    from . import naming
    naming.new_document(kind)


# ---------------------------------------------------------------- evaluate
def _solids_from_selection():
    sel = Gui.Selection.getSelectionEx()
    objs = []
    if sel:
        for s in sel:
            o = s.Object
            if o.isDerivedFrom("PartDesign::Feature") and hasattr(o, "getParentGeoFeatureGroup"):
                b = o.getParentGeoFeatureGroup()
                o = b if b and b.isDerivedFrom("PartDesign::Body") else o
            objs.append(o)
    else:
        doc = App.ActiveDocument
        if doc is None:
            return []
        objs = [o for o in doc.Objects if o.isDerivedFrom("PartDesign::Body")] or \
               [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.ViewObject and o.ViewObject.Visibility
                and not o.isDerivedFrom("PartDesign::Feature") and not o.InList]
    out = []
    for o in objs:
        shp = getattr(o, "Shape", None)
        if shp is not None and not shp.isNull() and shp.Solids:
            out.append((o, shp))
    return out


def _density(obj):
    """kg/m^3 and material name (see materials.material_of)."""
    from . import materials
    name, rho = materials.material_of(obj)
    return rho, name


def mass_properties():
    from . import evaluate
    evaluate.MassPropertiesDialog.open()


def toggle_rigid():
    """SOLIDWORKS: right-click a sub-assembly > Make Subassembly Flexible / Rigid."""
    subs = [o for o in Gui.Selection.getSelection() if o.TypeId == "Assembly::AssemblyLink" and hasattr(o, "Rigid")]
    if not subs:
        msg("Select a sub-assembly in the FeatureManager design tree")
        return
    doc = subs[0].Document
    doc.openTransaction("Rigid / Flexible")
    for o in subs:
        o.Rigid = not o.Rigid
    doc.commitTransaction()
    doc.recompute()
    msg("%s is now %s" % (subs[0].Label, "rigid" if subs[0].Rigid else "flexible"))


def edit_material():
    from . import evaluate
    evaluate.MaterialDialog.open()


def section_properties():
    sel = Gui.Selection.getSelectionEx()
    faces = [f for s in sel for f in s.SubObjects if getattr(f, "ShapeType", "") == "Face"]
    if not faces:
        msg("Select one or more planar faces")
        return
    lines = []
    for i, f in enumerate(faces, 1):
        c = f.CenterOfMass
        M = f.MatrixOfInertia
        lines += ["Section properties of face %d" % i, "", "Area = %.2f square millimeters" % f.Area, "",
                  "Centroid relative to output coordinate system origin: ( millimeters )",
                  "     X = %.2f" % c.x, "     Y = %.2f" % c.y, "     Z = %.2f" % c.z, "",
                  "Moments of area, at the centroid: ( millimeters ^ 4 )",
                  "     Lxx = %.2f   Lxy = %.2f   Lxz = %.2f" % (M.A11, M.A12, M.A13),
                  "     Lyx = %.2f   Lyy = %.2f   Lyz = %.2f" % (M.A21, M.A22, M.A23),
                  "     Lzx = %.2f   Lzy = %.2f   Lzz = %.2f" % (M.A31, M.A32, M.A33),
                  "", "Polar moment of area, at the centroid = %.2f millimeters ^ 4" % (M.A11 + M.A22 + M.A33 - max(M.A11, M.A22, M.A33)), "", "-" * 60, ""]
    from . import widgets
    widgets.ReportDialog.show_text("Section Properties", "\n".join(lines), "section_properties")


def bounding_box():
    items = _solids_from_selection()
    if not items:
        msg("Nothing to measure")
        return
    bb = App.BoundBox()
    for _, s in items:
        bb.add(s.BoundBox)
    from . import widgets
    widgets.ReportDialog.show_text("Bounding Box", "Bounding box of %s\n\nX: %.3f .. %.3f   (length %.3f mm)\nY: %.3f .. %.3f   (width  %.3f mm)\nZ: %.3f .. %.3f   (height %.3f mm)\n\nDiagonal = %.3f mm" % (
        ", ".join(o.Label for o, _ in items), bb.XMin, bb.XMax, bb.XLength, bb.YMin, bb.YMax, bb.YLength, bb.ZMin, bb.ZMax, bb.ZLength, bb.DiagonalLength), "bounding_box")


def interference():
    items = _solids_from_selection()
    if len(items) < 2:
        doc = App.ActiveDocument
        if doc is not None:
            items = []
            for o in doc.Objects:
                shp = getattr(o, "Shape", None)
                if (o.TypeId in ("App::Link",) or o.isDerivedFrom("PartDesign::Body")) and shp and not shp.isNull() and shp.Solids:
                    items.append((o, shp))
    if len(items) < 2:
        msg("Select two or more bodies / components")
        return
    found = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, sa = items[i]
            b, sb = items[j]
            if not sa.BoundBox.intersect(sb.BoundBox):
                continue
            try:
                com = sa.common(sb)
                v = com.Volume
            except Exception:
                continue
            if v > 1e-6:
                found.append((a, b, v, com))
    from . import widgets
    widgets.InterferenceDialog.show_results(items, found)


@safe
def centerline():
    from . import sketchmode
    sketchmode.start_centerline()


def tangent_arc():
    msg("Tangent arc: draw a line, then press M to switch the polyline to tangent-arc mode", 8000)
    run("Sketcher_CreatePolyline")


def _reset_settings():
    r = QtWidgets.QMessageBox.question(Gui.getMainWindow(), "Reset FreeWorks Settings",
                                       "Restore the FreeWorks defaults (layout, colours, options)?\n"
                                       "Your projects and documents are not affected.")
    if r == QtWidgets.QMessageBox.Yes:
        from . import safemode
        safemode.reset_settings()
        msg("FreeWorks settings restored")


# ---------------------------------------------------------------- registry
class _Cmd:
    def __init__(self, key, fn, label=None, tip=None, icon_key=None, active="doc", accel=""):
        self.key, self.fn = key, fn
        e = catalog.C.get(key, {})
        self.label = label or e.get("label", key)
        self.tip = tip or e.get("tip", self.label)
        self.icon_key = icon_key or e.get("icon") or "freeworks"
        self.active = active
        self.accel = accel

    def GetResources(self):
        r = {"MenuText": self.label, "ToolTip": self.tip}
        p = icon_path(self.icon_key)
        if p:
            r["Pixmap"] = p
        if self.accel:
            r["Accel"] = self.accel
        return r

    def IsActive(self):
        if self.active == "always":
            return True
        if self.active == "sketch":
            return context.edited_sketch() is not None
        if self.active == "view":
            return view3d() is not None
        return App.ActiveDocument is not None

    def Activated(self):
        try:
            self.fn()
        except Exception:
            import traceback
            App.Console.PrintError("FreeWorks %s: %s\n" % (self.key, traceback.format_exc()))


def register():
    global _registered
    if _registered:
        return
    _registered = True
    defs = [
        ("extrude", lambda: _sketch_then("PartDesign_Pad"), "FW_ExtrudedBoss", "doc"),
        ("extrude_cut", lambda: _sketch_then("PartDesign_Pocket"), "FW_ExtrudedCut", "doc"),
        ("sketch", sketch_cmd, "FW_Sketch", "doc"),
        ("exit_sketch", exit_sketch, "FW_ExitSketch", "sketch"),
        ("edit_sketch", edit_sketch, "FW_EditSketch", "doc"),
        ("centerline", centerline, "FW_Centerline", "sketch"),
        ("tangent_arc", tangent_arc, "FW_TangentArc", "sketch"),
        ("relations", add_relation, "FW_AddRelation", "sketch"),
        ("mate", mate_menu, "FW_Mate", "doc"),
        ("edit_mate", lambda: __import__("freeworks.matepm", fromlist=["edit_selected"]).edit_selected(), "FW_EditMate", "doc"),
        ("move_component", lambda: __import__("freeworks.movepm", fromlist=["start"]).start(False), "FW_MoveComponent", "doc"),
        ("rotate_component", lambda: __import__("freeworks.movepm", fromlist=["start"]).start(True), "FW_RotateComponent", "doc"),
        ("replace_components", lambda: __import__("freeworks.replace", fromlist=["start"]).start(), "FW_ReplaceComponents", "doc"),
        ("sub_rigid", toggle_rigid, "FW_ToggleRigid", "doc"),
        ("mass_props", mass_properties, "FW_MassProperties", "doc"),
        ("material", edit_material, "FW_EditMaterial", "doc"),
        ("section_props", section_properties, "FW_SectionProperties", "doc"),
        ("interference", interference, "FW_Interference", "doc"),
        ("bbox", bounding_box, "FW_BoundingBox", "doc"),
        ("prev_view", prev_view, "FW_PreviousView", "view"),
        ("v_front", std_view("viewFront"), "FW_ViewFront", "view"),
        ("v_back", std_view("viewRear"), "FW_ViewBack", "view"),
        ("v_left", std_view("viewLeft"), "FW_ViewLeft", "view"),
        ("v_right", std_view("viewRight"), "FW_ViewRight", "view"),
        ("v_top", std_view("viewTop"), "FW_ViewTop", "view"),
        ("v_bottom", std_view("viewBottom"), "FW_ViewBottom", "view"),
        ("v_iso", std_view("viewIsometric"), "FW_ViewIso", "view"),
        ("normal_to", normal_to, "FW_NormalTo", "view"),
        ("view_orient", view_orientation_menu, "FW_ViewOrientationMenu", "view"),
        ("ds_edges", draw_style(0), "FW_DisplayShadedEdges", "view"),
        ("ds_shaded", draw_style(5), "FW_DisplayShaded", "view"),
        ("ds_hlr", draw_style(3), "FW_DisplayHLR", "view"),
        ("ds_wire", draw_style(2), "FW_DisplayWireframe", "view"),
        ("ds_points", draw_style(1), "FW_DisplayPoints", "view"),
        ("hide_show", hide_show_menu, "FW_HideShowItems", "doc"),
        ("scene", scene_menu, "FW_SceneMenu", "always"),
        ("rebuild", rebuild, "FW_Rebuild", "doc"),
        ("force_rebuild", force_rebuild, "FW_ForceRebuild", "doc"),
        ("roll_end", roll_to_end, "FW_RollToEnd", "doc"),
        ("suppress", suppress, "FW_Suppress", "doc"),
        ("fw_options", options, "FW_Options", "always"),
        ("search", search_commands, "FW_SearchCommands", "always"),
        ("new_doc", new_document, "FW_New", "always"),
        ("sel_filter", toggle_filter_toolbar, "FW_ToggleFilterToolbar", "always"),
        ("magnify", magnify, "FW_Magnify", "view"),
        ("shortcut_bar", shortcut_bar, "FW_ShortcutBar", "always"),
        ("large_mode", lambda: __import__("freeworks.perf", fromlist=["toggle"]).toggle(), "FW_LargeModelMode", "always"),
        ("reset_settings", _reset_settings, "FW_ResetSettings", "always"),
    ]
    for key, fn, name, act in defs:
        Gui.addCommand(name, _Cmd(key, fn, active=act))
