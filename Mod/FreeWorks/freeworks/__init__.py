"""FreeWorks - a SolidWorks-style user experience layer for FreeCAD 1.1.x."""
import os
import FreeCAD as App

__version__ = "1.0.0"

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(MOD_DIR, "Resources")
ICON_DIR = os.path.join(RES_DIR, "icons")
THEME_DIR = os.path.join(RES_DIR, "theme")
PARAM_PATH = "User parameter:BaseApp/Preferences/Mod/FreeWorks"

_icon_cache = {}


def params():
    return App.ParamGet(PARAM_PATH)


def log(msg):
    App.Console.PrintLog("FreeWorks: %s\n" % msg)
    dbg = os.environ.get("FREEWORKS_DEBUG_LOG")
    if dbg:
        with open(dbg, "a") as f:
            f.write(str(msg) + "\n")


def warn(msg):
    App.Console.PrintWarning("FreeWorks: %s\n" % msg)
    log("WARN " + str(msg))


def icon_path(key):
    p = os.path.join(ICON_DIR, key + ".svg")
    return p if os.path.exists(p) else None


def icon(key):
    """QIcon for a FreeWorks icon key, or for a FreeCAD pixmap name."""
    from PySide import QtGui
    if key in _icon_cache:
        return _icon_cache[key]
    p = icon_path(key) if key else None
    if p:
        ic = QtGui.QIcon(p)
    else:
        import FreeCADGui as Gui
        try:
            ic = QtGui.QIcon(Gui.getIcon(key)) if key else QtGui.QIcon()
        except Exception:
            ic = QtGui.QIcon()
    _icon_cache[key] = ic
    return ic


def safe(fn):
    """Decorator: never let a FreeWorks callback take FreeCAD down."""
    import functools, traceback

    @functools.wraps(fn)
    def wrap(*a, **k):
        try:
            return fn(*a, **k)
        except Exception:
            # logged, not shown as a pop-up notification (Report view shows logs)
            msg = "error in %s:\n%s" % (fn.__name__, traceback.format_exc())
            App.Console.PrintLog("FreeWorks: %s\n" % msg)
            log(msg)
    return wrap
