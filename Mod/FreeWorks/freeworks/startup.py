"""Startup sequence: load the CAD environments, build the shell, show Welcome."""
import os
import time
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import log, params, warn, safe_slow

_state = {"done": False}


@safe_slow
def on_activated():
    if _state["done"]:
        from . import shell
        shell.hide_native_toolbars()
        return
    _state["done"] = True
    t0 = time.time()
    win = Gui.getMainWindow()
    from . import safemode
    safemode.mark("starting")          # if FreeWorks fails before "ready", next start is safe mode
    safemode.install_exit_hook()
    try:
        from . import commands, shell, naming, shortcuts, sketchmode, gestures
        win.statusBar().showMessage("FreeWorks: loading environments...")
        QtWidgets.QApplication.processEvents()
        commands.register()
        from . import prefs
        prefs.guard_save_folder()
        shell.preload_all()
        if Gui.activeWorkbench().name() != "FreeWorksWorkbench":
            Gui.activateWorkbench("FreeWorksWorkbench")
        naming.install_observer()
        sketchmode.install()
        shell.install()
        shortcuts.install()
        naming.rename_commands()
        gestures.hook_views()
        _close_start_page()
        win.statusBar().showMessage("FreeWorks ready (%.1f s)" % (time.time() - t0), 4000)
        from . import updater
        QtCore.QTimer.singleShot(1200, updater.show_whats_new)
        QtCore.QTimer.singleShot(15000, updater.check)
        from . import STATS, watchdog
        STATS["startup_s"] = round(time.time() - t0, 2)
        log("startup %.2fs" % (time.time() - t0))
        watchdog.start()
        safemode.mark("ready")
        if safemode.previous_session_crashed():
            log("previous session ended unexpectedly")
            win.statusBar().showMessage("The last FreeWorks session ended unexpectedly - FreeCAD offers to recover "
                                        "unsaved documents. Help > FreeWorks Diagnostics has details.", 12000)
        QtCore.QTimer.singleShot(800, lambda: shell._S["cm"].prebuild())
        if params().GetBool("ShowWelcome", True) and not App.listDocuments() and not os.environ.get("FREEWORKS_NO_WELCOME"):
            from .widgets import NewDocumentDialog
            QtCore.QTimer.singleShot(300, lambda: NewDocumentDialog.ask(welcome=True))
    except Exception:
        import traceback
        warn("startup failed:\n" + traceback.format_exc())


def _close_start_page():
    mdi = Gui.getMainWindow().findChild(QtWidgets.QMdiArea)
    if mdi is None:
        return
    for sw in mdi.subWindowList():
        w = sw.widget()
        if w is not None and "Start" in w.metaObject().className():
            sw.close()
