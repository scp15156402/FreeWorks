"""SolidWorks terminology everywhere: command texts, feature names in the
FeatureManager tree, default planes, and SolidWorks-style new documents."""
import os
import re
import shutil
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

from . import catalog, icon_path, ICON_DIR, log, params, safe, safe_slow, harden

# FreeCAD type -> SolidWorks base name used in the tree
FEATURE_NAMES = {
    "PartDesign::Pad": "Boss-Extrude", "PartDesign::Pocket": "Cut-Extrude",
    "PartDesign::Revolution": "Revolve", "PartDesign::Groove": "Cut-Revolve",
    "PartDesign::AdditivePipe": "Sweep", "PartDesign::SubtractivePipe": "Cut-Sweep",
    "PartDesign::AdditiveLoft": "Loft", "PartDesign::SubtractiveLoft": "Cut-Loft",
    "PartDesign::AdditiveHelix": "Helix-Boss", "PartDesign::SubtractiveHelix": "Helix-Cut",
    "PartDesign::Fillet": "Fillet", "PartDesign::Chamfer": "Chamfer", "PartDesign::Thickness": "Shell",
    "PartDesign::Draft": "Draft", "PartDesign::Hole": "Hole",
    "PartDesign::LinearPattern": "LPattern", "PartDesign::PolarPattern": "CirPattern",
    "PartDesign::Mirrored": "Mirror", "PartDesign::MultiTransform": "Pattern",
    "PartDesign::Boolean": "Combine", "PartDesign::Plane": "Plane", "PartDesign::Line": "Axis",
    "PartDesign::Point": "Point", "PartDesign::CoordinateSystem": "Coordinate System",
    "Sketcher::SketchObject": "Sketch", "PartDesign::Body": "Body",
    "PartDesign::SubShapeBinder": "Reference", "PartDesign::ShapeBinder": "Reference",
    "Part::Common": "Intersect", "Part::Cut": "Combine-Subtract", "Part::MultiFuse": "Combine-Add",
    "Part::Scale": "Scale", "Part::Thickness": "Thicken", "Part::Offset": "Offset-Surface",
    "Surface::Filling": "Surface-Fill", "Surface::Sections": "Surface-Loft", "Surface::GeomFillSurface": "Boundary-Surface",
    "Part::Extrusion": "Surface-Extrude", "Part::Revolution": "Surface-Revolve", "Part::Sweep": "Surface-Sweep",
}

# Origin planes: FreeCAD is Z-up; SolidWorks' Front plane faces the viewer in
# the Front view, so XZ -> Front, XY -> Top, YZ -> Right.
ORIGIN_NAMES = {"XZ_Plane": "Front Plane", "XY_Plane": "Top Plane", "YZ_Plane": "Right Plane",
                "X_Axis": "X Axis", "Y_Axis": "Y Axis", "Z_Axis": "Z Axis", "Origin": "Point1@Origin"}


def _next_label(doc, base):
    pat = re.compile(r"^%s([1-9]\d*)$" % re.escape(base))
    n = 0
    for o in doc.Objects:
        m = pat.match(o.Label)
        if m:
            n = max(n, int(m.group(1)))
    return "%s%d" % (base, n + 1)


_pending = []


def _flush():
    while _pending:
        name, docname = _pending.pop(0)
        doc = App.getDocument(docname) if docname in App.listDocuments() else None
        o = doc.getObject(name) if doc else None
        if o is None:
            continue
        try:
            _relabel(o)
        except Exception as e:
            log("relabel %s: %s" % (name, e))


def _relabel(o):
    role = getattr(o, "Role", None)
    if role in ORIGIN_NAMES and o.TypeId in ("App::Plane", "App::Line", "App::Point"):
        o.Label = ORIGIN_NAMES[role]
        return
    if o.TypeId == "App::Origin":
        o.Label = "Origin"
        return
    base = FEATURE_NAMES.get(o.TypeId)
    if not base:
        return
    # only rename default labels (user renames are respected)
    default = re.sub(r"\d+$", "", o.Name)
    if not re.match(r"^%s\d*$" % re.escape(default), o.Label):
        return
    if o.TypeId == "PartDesign::Body":
        # SolidWorks shows solid bodies under the part; keep a plain name
        o.Label = "Body" if not [x for x in o.Document.Objects if x is not o and x.TypeId == "PartDesign::Body"] else _next_label(o.Document, "Body")
        return
    o.Label = _next_label(o.Document, base)


@harden
class _DocObserver:
    def slotCreatedObject(self, obj):
        if not params().GetBool("AutoRenameFeatures", True):
            return
        if obj.TypeId in FEATURE_NAMES or obj.TypeId in ("App::Plane", "App::Line", "App::Point", "App::Origin"):
            _pending.append((obj.Name, obj.Document.Name))
            QtCore.QTimer.singleShot(0, _flush)


_obs = None


def install_observer():
    global _obs
    if _obs is None:
        _obs = _DocObserver()
        App.addDocumentObserver(_obs)


# ------------------------------------------------------------------ actions
def _rename_action(cmd, label, icon_key=None, tip=None):
    c = Gui.Command.get(cmd)
    if c is None:
        return False
    try:
        acts = c.getAction()
    except Exception:
        acts = []
    for a in acts:
        a.setText(label)
        a.setIconText(label)
        a.setToolTip("<b>%s</b><br>%s" % (label, tip) if tip else label)
        a.setStatusTip(tip or label)
        if icon_key and icon_path(icon_key):
            from . import icon
            a.setIcon(icon(icon_key))
    return bool(acts)


@safe
def rename_commands():
    n = 0
    for e in catalog.C.values():
        cmd = e["cmd"][0]
        if not cmd.startswith("FW_") and _rename_action(cmd, e["label"], e["icon"], e["tip"]):
            n += 1
    for cmd, (label, ic) in catalog.EXTRA_RENAMES.items():
        if _rename_action(cmd, label, ic):
            n += 1
    _rename_action("Std_Edit", "Edit Feature")
    log("renamed %d command actions" % n)


# -------------------------------------------------------------- icon theme
def sync_icon_theme():
    """Copy FreeWorks icons into <UserAppData>/icons under FreeCAD's pixmap
    names.  FreeCAD searches that folder before its built-in icons, so the
    FeatureManager tree, menus and dialogs all pick up the FreeWorks icons."""
    dst = os.path.join(App.getUserAppDataDir(), "icons")
    os.makedirs(dst, exist_ok=True)
    stamp = os.path.join(dst, ".freeworks")
    from . import __version__
    if os.path.exists(stamp) and open(stamp).read().strip() == __version__:
        return False
    for pix, key in catalog.PIXMAP_OVERRIDES.items():
        src = os.path.join(ICON_DIR, key + ".svg")
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(dst, pix + ".svg"))
    with open(stamp, "w") as f:
        f.write(__version__)
    return True


# ------------------------------------------------------------ new documents
_counter = {"part": 0, "assembly": 0, "drawing": 0}
BASENAMES = {"part": "Part", "assembly": "Assem", "drawing": "Draw"}


def ensure_workbench(kind):
    from . import shell
    shell.load_environment(kind)


@safe_slow
def new_document(kind="part"):
    _counter[kind] += 1
    name = "%s%d" % (BASENAMES[kind], _counter[kind])
    while name in App.listDocuments():
        _counter[kind] += 1
        name = "%s%d" % (BASENAMES[kind], _counter[kind])
    doc = App.newDocument(name)
    try:
        m = dict(doc.Meta)
        m["FreeWorksType"] = kind
        doc.Meta = m
    except Exception:
        pass
    ensure_workbench(kind)
    if kind == "part":
        body = doc.addObject("PartDesign::Body", "Body")
        try:
            Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", body)
        except Exception:
            pass
        doc.recompute()
        Gui.activeDocument().activeView().viewIsometric()
    elif kind == "assembly":
        Gui.runCommand("Assembly_CreateAssembly")
    elif kind == "drawing":
        Gui.runCommand("TechDraw_PageDefault")
    doc.recompute()
    try:
        if kind == "part":
            from .commands import home_camera
            home_camera()            # a fit on the empty part would zoom to a few millimetres
        else:
            Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass
    from . import shell
    shell.on_context_change(force=True)
    return doc
