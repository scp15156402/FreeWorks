"""Safe mode and crash sentinel.

FreeWorks writes UserData/FreeWorks.session while it runs:
  phase "starting" - FreeWorks is building its interface
  phase "ready"    - normal session
The file is removed on a clean exit. On the next start:
  previous phase "starting" -> FreeWorks itself failed to start -> start in SAFE MODE (plain FreeCAD)
  previous phase "ready"    -> the last session ended unexpectedly -> notice only (FreeCAD offers
                               document recovery on its own)
Safe mode is also forced with FREEWORKS_SAFE=1 (FreeWorks.exe --safe, or Shift held at launch).
"""
import json
import os
import time

import FreeCAD as App

_state = {"mode": None, "reason": "", "previous": None}


def _file():
    return os.path.join(App.getUserAppDataDir(), "FreeWorks.session")


def _read():
    try:
        with open(_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def mark(phase):
    try:
        from . import __version__
        with open(_file(), "w", encoding="utf-8") as f:
            json.dump({"phase": phase, "pid": os.getpid(), "time": time.time(), "version": __version__}, f)
    except Exception:
        pass


def clear():
    try:
        os.remove(_file())
    except Exception:
        pass


def decide():
    """Called once, early (InitGui). Returns 'safe' or 'normal'."""
    if _state["mode"]:
        return _state["mode"]
    prev = _read()
    _state["previous"] = prev
    if os.environ.get("FREEWORKS_SAFE") == "1":
        _state.update(mode="safe", reason="requested")
    elif prev and prev.get("phase") == "starting":
        _state.update(mode="safe", reason="startup-failed")
        clear()                      # next launch tries normal mode again
    else:
        _state["mode"] = "normal"
    return _state["mode"]


def is_safe():
    return decide() == "safe"


def previous_session_crashed():
    p = _state.get("previous")
    return bool(p and p.get("phase") == "ready")


def install_exit_hook():
    from PySide import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is not None and not getattr(app, "_fw_exit_hooked", False):
        app.aboutToQuit.connect(clear)
        app._fw_exit_hooked = True


def enter_safe_mode_ui():
    """Plain FreeCAD with its own menus and toolbars, plus an explanation."""
    import FreeCADGui as Gui
    from PySide import QtCore, QtWidgets
    try:
        Gui.activateWorkbench("PartDesignWorkbench")
    except Exception:
        pass
    win = Gui.getMainWindow()
    win.menuBar().show()
    for tb in win.findChildren(QtWidgets.QToolBar):
        if tb.parent() is win:
            tb.show()
    win.statusBar().showMessage("FreeWorks SAFE MODE - plain FreeCAD. Restart FreeWorks normally to get the FreeWorks interface back.")
    if _state["reason"] == "startup-failed":
        def ask():
            box = QtWidgets.QMessageBox(win)
            box.setWindowTitle("FreeWorks Safe Mode")
            box.setIcon(QtWidgets.QMessageBox.Warning)
            box.setText("FreeWorks did not finish starting last time, so this session runs in Safe Mode "
                        "(plain FreeCAD, nothing of FreeWorks loaded). Your documents are not affected.")
            box.setInformativeText("Next time FreeWorks starts normally again. If the problem repeats, reset the "
                                   "FreeWorks settings or update FreeWorks.")
            reset = box.addButton("Reset FreeWorks settings", QtWidgets.QMessageBox.ActionRole)
            box.addButton(QtWidgets.QMessageBox.Ok)
            box.exec_()
            if box.clickedButton() is reset:
                reset_settings(apply_now=False)
                QtWidgets.QMessageBox.information(win, "FreeWorks", "FreeWorks settings were reset. Restart FreeWorks.")
        QtCore.QTimer.singleShot(1500, ask)


def reset_settings(apply_now=True):
    """Forget FreeWorks options and re-apply the FreeWorks defaults to FreeCAD."""
    from . import PARAM_PATH, prefs, naming
    grp = App.ParamGet(PARAM_PATH)
    keep = {k: grp.GetString(k) for k in ("ProjectsDir", "LastSeenVersion")}
    grp.Clear()
    for k, v in keep.items():
        if v:
            grp.SetString(k, v)
    grp.SetBool("ProjectsFolderSet", bool(keep.get("ProjectsDir")))
    prefs.apply(force=True)
    try:
        stamp = os.path.join(App.getUserAppDataDir(), "icons", ".freeworks")
        if os.path.exists(stamp):
            os.remove(stamp)
        naming.sync_icon_theme()
    except Exception:
        pass
    if apply_now:
        try:
            from . import shell
            shell.refresh_options()
            c = shell._S.get("controller")
            if c:
                c.docks_done = False
                c.fix_docks()
        except Exception:
            pass
