"""SOLIDWORKS terms inside FreeCAD's feature panels (the PropertyManager).

While a task panel is open, a light timer (400 ms, stops when the panel closes) relabels texts that
FreeCAD shows - end conditions ("Dimension" -> "Blind", "To first" -> "Up To Next" ...), field names
("Length" -> "Depth", "Taper angle" -> "Draft") and panel titles ("Pad parameters" ->
"Boss-Extrude") - and gives OK / Cancel SOLIDWORKS' green check / red cross. Only display texts
change: FreeCAD's panels work with item indices, so behaviour is untouched. Items that have no
SOLIDWORKS equivalent keep FreeCAD's wording.
"""
from PySide import QtCore, QtWidgets

import FreeCADGui as Gui

from . import icon, safe

TITLES = {
    "Pad parameters": "Boss-Extrude", "Pocket parameters": "Cut-Extrude",
    "Revolution parameters": "Revolve", "Groove parameters": "Cut-Revolve",
    "Fillet parameters": "Fillet", "Chamfer parameters": "Chamfer", "Thickness parameters": "Shell",
    "Draft parameters": "Draft", "Hole parameters": "Hole Wizard", "Linear pattern parameters": "Linear Pattern",
    "Polar pattern parameters": "Circular Pattern", "Mirror parameters": "Mirror",
    "Pipe parameters": "Sweep", "Loft parameters": "Loft", "Helix parameters": "Helix/Spiral",
    "Datum plane parameters": "Plane", "Datum line parameters": "Axis", "Datum point parameters": "Point",
    "Attachment": "References",
}
EXTRUDE = {
    "Dimension": "Blind", "Through all": "Through All", "To first": "Up To Next", "To last": "Up To Last",
    "Up to face": "Up To Surface", "Up to shape": "Up To Body", "Offset to face": "Offset From Surface",
    "Two dimensions": "Two Directions", "Symmetric to plane": "Mid Plane", "One side": "One Direction",
    "Two sides": "Two Directions", "Symmetric": "Mid Plane", "Length": "Depth", "2nd length": "Depth (Direction 2)",
    "Reversed": "Reverse Direction", "Taper angle": "Draft angle", "Custom direction": "Direction of Extrusion",
    "Along sketch normal": "Normal to sketch", "Sketch normal": "Normal to sketch",
    "One sided": "One Direction", "Two sided": "Two Directions", "Side 1": "Direction 1", "Side 2": "Direction 2",
    "Mode": "Directions", "Type": "End Condition", "Length along sketch normal": "Depth along sketch normal",
}
EXTRUDE_BOSS = dict(EXTRUDE, **{"To last": "Through All"})       # a boss "to last face" = SOLIDWORKS Through All
REVOLVE = {
    "Mode": "Directions", "Type": "Revolve Type", "Side 1": "Direction 1", "Side 2": "Direction 2", "One sided": "One Direction",
    "Two sided": "Two Directions",
    "Dimension": "Blind", "Through all": "Through All", "To first": "Up To Next", "To last": "Up To Last",
    "Up to face": "Up To Surface", "Two dimensions": "Two Directions", "Symmetric to plane": "Mid Plane",
    "One side": "One Direction", "Two sides": "Two Directions", "Symmetric": "Mid Plane",
    "Axis": "Axis of Revolution", "Reversed": "Reverse Direction",
}
CHAMFER = {"Equal distance": "Distance Distance (equal)", "Two distances": "Distance Distance",
           "Distance and angle": "Angle Distance", "Size": "Distance"}
HOLE = {
    "Head type": "Hole Type", "None": "Hole (no head)", "Hole type": "Hole Usage",
    "Clearance / Passthrough": "Clearance hole", "Tap drill (to be threaded)": "Tap drill", "Modeled thread": "Modeled thread",
    "Depth type": "End Condition", "Dimension": "Blind", "Through all": "Through All", "Depth": "Hole depth",
    "Diameter": "Hole diameter", "Head diameter": "Counterbore/Countersink diameter", "Head depth": "Counterbore depth",
    "Countersink angle": "Countersink angle", "Clearance": "Fit", "Close": "Close", "Wide": "Loose",
    "Base profile types": "Positions from", "Switch direction": "Reverse Direction", "Thread Depth Type": "Thread end condition",
    "Hole depth": "Hole depth", "Custom head values": "Custom Sizing", "Custom Clearance": "Custom clearance",
}
BY_TYPE = {
    "PartDesign::Pad": EXTRUDE_BOSS, "PartDesign::Pocket": EXTRUDE,
    "PartDesign::Revolution": REVOLVE, "PartDesign::Groove": REVOLVE,
    "PartDesign::Chamfer": CHAMFER,
    "PartDesign::Hole": HOLE,
    "PartDesign::Fillet": {"Use all edges": "Select all edges"},
    "PartDesign::Thickness": {"Make thickness inwards": "Shell inward (clear = Shell outward)", "Thickness": "Thickness"},
    "PartDesign::LinearPattern": {"Length": "Spacing / total length", "Occurrences": "Number of Instances"},
    "PartDesign::PolarPattern": {"Occurrences": "Number of Instances", "Angle": "Angle (total)"},
    "PartDesign::Mirrored": {"Plane": "Mirror Face/Plane"},
    "PartDesign::Draft": {"Angle": "Draft Angle", "Neutral plane": "Neutral Plane", "Pull direction": "Direction of Pull",
                          "Reverse pull direction": "Reverse Direction"},
}
OKS = {"OK", "&OK"}
CANCELS = {"Cancel", "&Cancel", "Close", "&Close"}
_state = {"timer": None, "type": None}


def _map(text, table):
    t = text.strip()
    colon = t.endswith(":")
    base = t[:-1].strip() if colon else t
    base = base.replace("&", "")
    new = table.get(base)
    if new is None:
        new = table.get("\0" + base.lower())        # titles: "Pad Parameters" / "Pad parameters"
    if new is None:
        return None
    return new + (":" if colon else "")


def skin(root, typeid):
    table = dict(TITLES)
    table.update({"\0" + k.lower(): v for k, v in TITLES.items()})
    table.update(BY_TYPE.get(typeid, {}))
    n = 0
    for w in root.findChildren(QtWidgets.QWidget):
        try:
            if isinstance(w, QtWidgets.QLabel):
                m = _map(w.text(), table)
                if m and m != w.text():
                    w.setText(m)
                    n += 1
            elif isinstance(w, QtWidgets.QComboBox):
                for i in range(w.count()):
                    m = _map(w.itemText(i), table)
                    if m and m != w.itemText(i):
                        w.setItemText(i, m)
                        n += 1
            elif isinstance(w, QtWidgets.QGroupBox):
                m = _map(w.title(), table)
                if m:
                    w.setTitle(m)
                    n += 1
            elif isinstance(w, QtWidgets.QPushButton) and w.property("fw_pm") is None:
                t = w.text()
                if t in OKS or t in CANCELS:
                    w.setIcon(icon("ok" if t in OKS else "cancel"))
                    w.setProperty("fw_pm", True)
                    n += 1
            elif isinstance(w, QtWidgets.QAbstractButton):
                m = _map(w.text(), table)
                if m and m != w.text():
                    w.setText(m)
                    n += 1
        except RuntimeError:
            continue                 # widget deleted while we walk
    return n


def _task_root():
    from . import shell
    d = shell._dock("Tasks")
    return d.widget() if d is not None else None


def _edited_type():
    try:
        vp = Gui.ActiveDocument.getInEdit() if Gui.ActiveDocument else None
        return vp.Object.TypeId if vp is not None else None
    except Exception:
        return None


@safe
def _pass():
    try:
        open_ = Gui.Control.activeDialog()
    except Exception:
        open_ = False
    if not open_:
        stop()
        return
    root = _task_root()
    if root is not None:
        skin(root, _edited_type())


def start():
    """Called when a task panel opens (controller tick)."""
    from . import params
    if not params().GetBool("SolidWorksTerms", True):
        return
    t = _state["timer"]
    if t is None:
        t = _state["timer"] = QtCore.QTimer()
        t.setInterval(400)
        t.timeout.connect(_pass)
    if not t.isActive():
        t.start()
    QtCore.QTimer.singleShot(0, _pass)


def stop():
    t = _state["timer"]
    if t is not None and t.isActive():
        t.stop()
