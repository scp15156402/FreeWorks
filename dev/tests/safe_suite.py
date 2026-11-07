"""Safe-mode check: FreeWorks must leave FreeCAD untouched (run by dev/run_tests.sh)."""
import json, os, sys
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

OUT = os.environ["FREEWORKS_TEST_OUT"]
NAME = os.environ.get("FREEWORKS_SAFE_CASE", "safe")


def check():
    res = []
    win = Gui.getMainWindow()
    shell_built = "freeworks.shell" in sys.modules and bool(sys.modules["freeworks.shell"]._S.get("dock"))
    res.append({"test": "%s: FreeWorks interface not built" % NAME, "ok": not shell_built, "detail": ""})
    res.append({"test": "%s: FreeCAD menu bar visible" % NAME, "ok": win.menuBar().isVisible(), "detail": ""})
    vis = [t for t in win.findChildren(QtWidgets.QToolBar) if t.parent() is win and t.isVisible()]
    res.append({"test": "%s: FreeCAD toolbars visible" % NAME, "ok": len(vis) > 0, "detail": len(vis)})
    wb = Gui.activeWorkbench().name()
    res.append({"test": "%s: plain FreeCAD workbench active" % NAME, "ok": wb != "FreeWorksWorkbench", "detail": wb})
    sess = os.path.join(App.getUserAppDataDir(), "FreeWorks.session")
    res.append({"test": "%s: stale session marker cleared" % NAME, "ok": not os.path.exists(sess) or NAME == "safe", "detail": ""})
    json.dump(res, open(os.path.join(OUT, "safe_%s.json" % NAME), "w"), indent=1)
    for w in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(w, QtWidgets.QMessageBox):
            w.close()
    QtWidgets.QApplication.quit()


QtCore.QTimer.singleShot(9000, check)
