"""FreeWorks - a SolidWorks-style user experience layer for FreeCAD 1.1.x."""
import functools
import os
import time
import traceback

import FreeCAD as App

__version__ = "1.1.1"

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(MOD_DIR, "Resources")
ICON_DIR = os.path.join(RES_DIR, "icons")
THEME_DIR = os.path.join(RES_DIR, "theme")
PARAM_PATH = "User parameter:BaseApp/Preferences/Mod/FreeWorks"

SLOW_CALLBACK_MS = 60          # a FreeWorks callback slower than this is logged as a lag risk
_icon_cache = {}

# diagnostics shared by the stability tools
STATS = {"errors": [], "slow": [], "stalls": [], "startup_s": None}


def params():
    return App.ParamGet(PARAM_PATH)


# ------------------------------------------------------------------ logging
_LOG_MAX = 512 * 1024


def log_path():
    try:
        return os.path.join(App.getUserAppDataDir(), "FreeWorks.log")
    except Exception:
        return None


def _write(line):
    for p in (log_path(), os.environ.get("FREEWORKS_DEBUG_LOG")):
        if not p:
            continue
        try:
            if p == log_path() and os.path.exists(p) and os.path.getsize(p) > _LOG_MAX:
                os.replace(p, p + ".1")          # keep one rotated file
            with open(p, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass


def log(msg):
    App.Console.PrintLog("FreeWorks: %s\n" % msg)
    _write("%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg) if not os.environ.get("FREEWORKS_DEBUG_LOG") else str(msg))


def warn(msg):
    App.Console.PrintWarning("FreeWorks: %s\n" % msg)
    log("WARN " + str(msg))


# ------------------------------------------------------------------ crash / lag guard
def _guard(fn, default=None):
    name = getattr(fn, "__qualname__", getattr(fn, "__name__", "callback"))

    @functools.wraps(fn)
    def wrap(*a, **k):
        t0 = time.perf_counter()
        try:
            return fn(*a, **k)
        except Exception:
            tb = traceback.format_exc()
            STATS["errors"].append((time.time(), name, tb.strip().splitlines()[-1]))
            del STATS["errors"][:-50]
            App.Console.PrintLog("FreeWorks: error in %s:\n%s\n" % (name, tb))
            log("error in %s:\n%s" % (name, tb))
            return default
        finally:
            ms = (time.perf_counter() - t0) * 1000.0
            if ms > SLOW_CALLBACK_MS and name not in _SLOW_OK:
                STATS["slow"].append((time.time(), name, ms))
                del STATS["slow"][:-50]
                log("slow callback %s: %.0f ms" % (name, ms))
    wrap._fw_guarded = True
    return wrap


# callbacks that are slow by design (they open modal dialogs or run commands the user asked for)
_SLOW_OK = set()


def safe(fn):
    """Decorator: never let a FreeWorks callback raise into FreeCAD; log slow ones."""
    return _guard(fn)


def safe_slow(fn):
    """Like safe, for callbacks expected to take long (modal dialogs, user commands)."""
    g = _guard(fn)
    _SLOW_OK.add(getattr(fn, "__qualname__", fn.__name__))
    return g


_SPECIAL_DEFAULTS = {"eventFilter": False, "event": False}
_NO_WRAP = {"__init__", "__new__", "__del__", "__repr__", "sizeHint", "minimumSizeHint", "metaObject"}


def harden(cls):
    """Class decorator: guard every method the class defines (Qt virtual overrides included),
    so an exception in UI code can never propagate into FreeCAD."""
    for name, attr in list(vars(cls).items()):
        if name in _NO_WRAP or not callable(attr) or isinstance(attr, (staticmethod, classmethod, type)):
            continue
        if getattr(attr, "_fw_guarded", False):
            continue
        setattr(cls, name, _guard(attr, _SPECIAL_DEFAULTS.get(name)))
    cls._fw_hardened = True
    return cls


# ------------------------------------------------------------------ icons
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
