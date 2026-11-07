"""SolidWorks-style right-click menus, built from the current selection."""
import FreeCADGui as Gui

from . import catalog, context, harden, safe


LAST = []          # labels FreeWorks added to the menu being built

KEEP = {"Zoom to Fit", "Zoom to Selection", "Appearance...", "Edit Material", "Delete", "Placement",
        "Toggle Transparency", "Hide/Show", "Hide", "Show", "Rename", "Edit Feature", "Recompute object",
        "Expand/Collapse", "Select all instances", "Copy", "Paste", "Cut"}


def _cmds(keys):
    out = []
    for k in keys:
        if k == "|":
            out.append("Separator")
            continue
        e = catalog.C.get(k)
        c = catalog.first_existing(e) if e else None
        if c:
            out.append(c)
            LAST.append(e["label"])
    return out


def items(recipient):
    del LAST[:]
    ctx = context.current()
    sel = Gui.Selection.getSelectionEx()
    subs = [n for s in sel for n in s.SubElementNames]
    objs = [s.Object for s in sel]
    res = []
    if ctx == "sketch":
        res.append(("", _cmds(["exit_sketch", "|", "smart_dim", "relations", "construction", "trim", "|",
                               "line", "corner_rect", "circle", "center_arc", "|", "normal_sketch", "zoom_fit"])))
        return res
    if ctx == "drawing":
        res.append(("", _cmds(["d_smart_dim", "note", "balloon", "center_mark", "|", "projected_view", "section_dview", "detail_view"])))
        return res
    top = []
    if any(n.startswith("Face") for n in subs):
        top += ["sketch", "normal_to", "zoom_sel", "|", "extrude_cut", "hole_wizard", "fillet", "shell", "draft", "|", "appearance", "measure"]
    elif any(n.startswith("Edge") for n in subs):
        top += ["fillet", "chamfer", "|", "zoom_sel", "measure", "appearance"]
    elif objs:
        o = objs[0]
        if o.isDerivedFrom("Sketcher::SketchObject"):
            top += ["edit_sketch", "extrude", "extrude_cut", "revolve", "|", "normal_to", "toggle_vis"]
        elif o.isDerivedFrom("PartDesign::Plane") or o.TypeId == "App::Plane":
            top += ["sketch", "normal_to", "|", "plane", "toggle_vis"]
        elif o.isDerivedFrom("PartDesign::Feature") or o.isDerivedFrom("Part::Feature"):
            top += ["edit_feature", "edit_sketch", "|", "suppress", "rollback", "roll_end", "|", "toggle_vis", "appearance", "zoom_sel"]
        elif o.TypeId.startswith("Assembly") or o.TypeId == "App::Link":
            top += ["mate", "move_component", "fix_component", "|", "toggle_vis", "appearance", "zoom_sel"]
        else:
            top += ["toggle_vis", "appearance", "zoom_sel"]
    else:
        top += ["sketch", "|", "zoom_fit", "prev_view", "view_orient", "|", "hide_show", "scene", "|", "rebuild"]
    res.append(("", _cmds(top)))
    return res


def _txt(a):
    return a.text().replace("&", "").strip()


@safe
def reorganize(menu=None):
    """SolidWorks order: FreeWorks commands first, the common FreeCAD items
    next, everything else under 'More'."""
    from PySide import QtWidgets
    menu = menu or QtWidgets.QApplication.activePopupWidget()
    if menu is None or not isinstance(menu, QtWidgets.QMenu) or menu.property("fw_done"):
        return
    menu.setProperty("fw_done", True)
    acts = menu.actions()
    if not acts:
        return
    ours, used = [], set()
    for label in LAST:
        for a in acts:
            if a not in used and not a.isSeparator() and _txt(a) == label:
                ours.append(a)
                used.add(a)
                break
    rest = [a for a in acts if a not in used]
    keep = [a for a in rest if not a.isSeparator() and _txt(a) in KEEP]
    more = [a for a in rest if not a.isSeparator() and a not in keep]
    for a in acts:
        menu.removeAction(a)
    seen = set()
    for a in ours:
        if _txt(a) not in seen:
            menu.addAction(a)
            seen.add(_txt(a))
    if ours:
        menu.addSeparator()
    for a in keep:
        if _txt(a) not in seen:
            menu.addAction(a)
            seen.add(_txt(a))
    if more:
        sub = menu.addMenu("More")
        for a in more:
            sub.addAction(a)
    menu.adjustSize()


@harden
class TreeHook:
    """Applies the same ordering to the FeatureManager tree's right-click menu."""

    def __init__(self):
        from PySide import QtCore

        @harden
        class F(QtCore.QObject):
            def eventFilter(self, o, e):
                if e.type() == QtCore.QEvent.ContextMenu:
                    QtCore.QTimer.singleShot(0, reorganize)
                return False
        self.f = F()

    def hook(self, w):
        w.removeEventFilter(self.f)
        w.installEventFilter(self.f)
