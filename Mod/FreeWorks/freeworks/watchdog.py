"""UI stall watchdog and diagnostics.

A 4 Hz timer measures how late it fires. If the event loop was blocked for longer than
STALL_MS, the stall is recorded (with what was going on) in FreeWorks.log and in
Help > FreeWorks Diagnostics. Cost: one tiny Python call every 250 ms."""
import os
import sys
import time

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import STATS, __version__, harden, log, log_path, params

INTERVAL_MS = 250
STALL_MS = 500          # the UI did not respond for at least this long


@harden
class Watchdog(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.last = time.perf_counter()
        self.t = QtCore.QTimer(self)
        self.t.setTimerType(QtCore.Qt.CoarseTimer)
        self.t.timeout.connect(self.beat)
        self.t.start(INTERVAL_MS)

    def beat(self):
        now = time.perf_counter()
        late_ms = (now - self.last) * 1000.0 - INTERVAL_MS
        self.last = now
        if late_ms >= STALL_MS:
            what = _activity()
            STATS["stalls"].append((time.time(), late_ms, what))
            del STATS["stalls"][:-50]
            log("UI stall %.0f ms (%s)" % (late_ms, what))


def _activity():
    parts = []
    try:
        from . import context
        parts.append(context.current())
        if Gui.Control.activeDialog():
            parts.append("task dialog open")
        doc = App.ActiveDocument
        if doc is not None:
            parts.append("%d objects" % len(doc.Objects))
    except Exception:
        pass
    return ", ".join(parts) or "idle"


_wd = None


def start():
    global _wd
    if _wd is None:
        _wd = Watchdog()
    return _wd


def report():
    import platform
    lines = ["FreeWorks %s on FreeCAD %s" % (__version__, ".".join(App.Version()[:3])),
             "Python %s, %s" % (sys.version.split()[0], platform.platform()),
             "Startup: %s s" % (STATS.get("startup_s") or "?"),
             "Log file: %s" % log_path(), ""]
    lines.append("UI stalls (event loop blocked >= %d ms): %d" % (STALL_MS, len(STATS["stalls"])))
    for t, ms, what in STATS["stalls"][-15:]:
        lines.append("  %s  %6.0f ms  %s" % (time.strftime("%H:%M:%S", time.localtime(t)), ms, what))
    lines.append("")
    lines.append("Slow FreeWorks callbacks (> 60 ms): %d" % len(STATS["slow"]))
    for t, name, ms in STATS["slow"][-15:]:
        lines.append("  %s  %6.0f ms  %s" % (time.strftime("%H:%M:%S", time.localtime(t)), ms, name))
    lines.append("")
    lines.append("FreeWorks errors caught: %d" % len(STATS["errors"]))
    for t, name, last in STATS["errors"][-15:]:
        lines.append("  %s  %s: %s" % (time.strftime("%H:%M:%S", time.localtime(t)), name, last))
    lines.append("")
    lines.append("Stalls during long rebuilds come from FreeCAD's geometry engine; stalls with no rebuild,")
    lines.append("slow callbacks and errors are FreeWorks issues - please report them with this text.")
    return "\n".join(lines)


def show():
    from .widgets import ReportDialog
    ReportDialog.show_text("FreeWorks Diagnostics", report(), "options")
