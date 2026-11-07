"""Context-sensitive SolidWorks keyboard shortcuts.

Implemented with QShortcut on the main window (no global event filter, so no
cost while you work).  Text fields keep their keys because Qt lets an
editing widget claim printable keys first.  FreeCAD shortcuts that would
collide with these are cleared so nothing is ambiguous."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import catalog, context, log, params, safe

Qt = QtCore.Qt

# key -> {context: action}.  context: sketch | part | assembly | drawing | *
# action: catalog key, or "fn:<name>" for a function below
KEYMAP = {
    "E": {"sketch": "extrude", "part": "extrude"},
    "F": {"sketch": "sk_fillet", "part": "fillet", "assembly": "fillet"},
    "L": {"sketch": "line", "part": "fn:sketch_line"},
    "R": {"sketch": "corner_rect", "part": "fn:sketch_rect"},
    "C": {"sketch": "circle", "part": "fn:sketch_circle"},
    "T": {"sketch": "trim"},
    "X": {"sketch": "construction"},
    "D": {"sketch": "smart_dim", "drawing": "d_smart_dim"},
    "A": {"sketch": "fn:arc_toggle"},
    "M": {"*": "measure"},
    "G": {"*": "magnify"},
    "W": {"*": "search"},
    "I": {"*": "fn:search_files"},
    "H": {"*": "fn:search_help"},
    "V": {"*": "fn:filter_vertex"},
    "Z": {"*": "zoom_out"},
    "Shift+Z": {"*": "zoom_in"},
    "S": {"*": "shortcut_bar"},
    "Space": {"sketch": "view_orient", "part": "view_orient", "assembly": "view_orient"},
    "F6": {"*": "sel_filter"},
    "Ctrl+1": {"*": "v_front"}, "Ctrl+2": {"*": "v_back"}, "Ctrl+3": {"*": "v_left"}, "Ctrl+4": {"*": "v_right"},
    "Ctrl+5": {"*": "v_top"}, "Ctrl+6": {"*": "v_bottom"}, "Ctrl+7": {"*": "v_iso"}, "Ctrl+8": {"*": "normal_to"},
    "Ctrl+B": {"*": "rebuild"},
    "Ctrl+Q": {"*": "force_rebuild"},
    "Ctrl+Shift+Z": {"*": "prev_view"},
    "Ctrl+N": {"*": "new_doc"},
    "Ctrl+Y": {"*": "fn:redo"},
    "Ctrl+R": {"*": "fn:redraw"},
    "Ctrl+Shift+F": {"*": "zoom_fit"},
}

# FreeCAD commands whose shortcuts are always removed: they would rearrange the
# SOLIDWORKS-style layout (overlay docks) or clash with SOLIDWORKS habits.
DISABLE_SHORTCUTS = ("Std_DockOverlayToggleLeft", "Std_DockOverlayToggleRight", "Std_DockOverlayToggleTop",
                     "Std_DockOverlayToggleBottom", "Std_DockOverlayMouseTransparent", "Std_DockOverlayToggle",
                     "Std_DockOverlayAll", "Std_DockOverlayTransparentAll", "Std_DockOverlayToggleTransparent")

CTX_NAMES = {"*": "Everywhere", "sketch": "Sketch", "part": "Part", "assembly": "Assembly", "drawing": "Drawing"}

_shortcuts = []
_cleared = {}


def _fn_sketch_tool(tool_key):
    """SolidWorks: pressing L/R/C with a plane or face selected starts a
    sketch and the tool in one go."""
    from . import commands
    commands.run_key("sketch")
    tries = {"n": 0}

    def poll():
        tries["n"] += 1
        if context.edited_sketch() is not None:
            commands.run_key(tool_key)
        elif tries["n"] < 120 and Gui.Control.activeDialog():
            QtCore.QTimer.singleShot(250, poll)
    QtCore.QTimer.singleShot(250, poll)


def _arc_toggle():
    """In the Line tool, A switches between line and tangent arc (FreeCAD's M)."""
    v = Gui.getMainWindow().focusWidget()
    target = None
    from . import gestures
    for vp in gestures.view_widgets():
        w = vp.parentWidget()       # the viewer (QGraphicsView) receives keys
        target = w
        if w is v or vp is v:
            break
    if target is None:
        return
    for t in (QtCore.QEvent.KeyPress, QtCore.QEvent.KeyRelease):
        QtWidgets.QApplication.sendEvent(target, QtGui.QKeyEvent(t, Qt.Key_M, Qt.NoModifier, "m"))


def _filter_vertex():
    from . import shell
    shell.set_filter("filter_vertex")


def _redo():
    from . import commands
    commands.run("Std_Redo")


def _redraw():
    v = Gui.activeView()
    try:
        v.redraw()
    except Exception:
        pass


def _search(mode):
    from . import shell
    shell.focus_search(mode)


FUNCS = {
    "sketch_line": lambda: _fn_sketch_tool("line"),
    "sketch_rect": lambda: _fn_sketch_tool("corner_rect"),
    "sketch_circle": lambda: _fn_sketch_tool("circle"),
    "arc_toggle": _arc_toggle,
    "filter_vertex": _filter_vertex,
    "redo": _redo,
    "redraw": _redraw,
    "search_files": lambda: _search("files"),
    "search_help": lambda: _search("help"),
}


@safe
def dispatch(seq):
    if not params().GetBool("Shortcuts", True):
        return
    m = KEYMAP.get(seq, {})
    ctx = context.current()
    act = m.get(ctx) or m.get("*")
    if ctx == "none" and act not in ("search", "new_doc", "fn:search_files", "fn:search_help", "magnify", "shortcut_bar"):
        return
    if not act:
        return
    if act.startswith("fn:"):
        FUNCS[act[3:]]()
    else:
        from . import commands
        commands.run_key(act)


def _norm(seq):
    return QtGui.QKeySequence(seq).toString(QtGui.QKeySequence.PortableText)


def resolve_conflicts():
    """Clear FreeCAD shortcuts whose first chord collides with ours and make
    sure the remaining FreeCAD shortcuts keep working with hidden toolbars."""
    ours = {_norm(k) for k in KEYMAP}
    win = Gui.getMainWindow()
    n = 0
    for name in Gui.Command.listAll():
        c = Gui.Command.get(name)
        if c is None:
            continue
        try:
            sc = c.getShortcut()
        except Exception:
            continue
        if not sc:
            continue
        first = _norm(sc.split(",")[0].strip())
        if first in ours or _norm(sc) in ours or name in DISABLE_SHORTCUTS:
            try:
                c.setShortcut("")
                _cleared[name] = sc
                n += 1
            except Exception:
                pass
            continue
        # keep FreeCAD's own shortcuts alive although menus/toolbars are hidden
        try:
            for a in c.getAction():
                if a not in win.actions():
                    win.addAction(a)
        except Exception:
            pass
    if n:
        log("cleared %d conflicting FreeCAD shortcuts" % n)


def install():
    if _shortcuts:
        return
    win = Gui.getMainWindow()
    for seq in KEYMAP:
        s = QtGui.QShortcut(QtGui.QKeySequence(seq), win)
        s.setContext(Qt.WindowShortcut)
        s.setAutoRepeat(False)
        s.activated.connect(lambda seq=seq: dispatch(seq))
        _shortcuts.append(s)
    resolve_conflicts()
    log("installed %d SolidWorks shortcuts" % len(_shortcuts))


def describe():
    rows = []
    for seq, m in KEYMAP.items():
        for ctx, act in m.items():
            if act.startswith("fn:"):
                label = {"sketch_line": "Sketch + Line", "sketch_rect": "Sketch + Rectangle", "sketch_circle": "Sketch + Circle",
                         "arc_toggle": "Line ↔ Tangent Arc", "filter_vertex": "Filter Vertices", "redo": "Redo",
                         "redraw": "Redraw", "search_files": "Search Files and Models", "search_help": "Search Help"}[act[3:]]
            else:
                label = catalog.C[act]["label"]
            rows.append((seq, CTX_NAMES[ctx], label))
    return rows
