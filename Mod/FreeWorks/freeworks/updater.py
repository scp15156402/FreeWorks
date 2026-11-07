"""Checks GitHub for a newer FreeWorks release and offers a one-click update.

The check runs in a background thread (no effect on interaction smoothness),
at most once a day, and only on a Windows FreeWorks installation."""
import json
import os
import sys
import threading
import time
import urllib.request

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import __version__, log, params

REPO = "scp15156402/FreeWorks"
API = "https://api.github.com/repos/%s/releases/latest" % REPO
RAW_PKG = "https://raw.githubusercontent.com/%s/main/Mod/FreeWorks/package.xml" % REPO
GET_PS1 = "https://raw.githubusercontent.com/%s/main/get.ps1" % REPO

_result = {}


def _vtuple(v):
    out = []
    for p in v.lstrip("vV").split("."):
        num = "".join(ch for ch in p if ch.isdigit())
        out.append(int(num) if num else 0)
    return tuple(out + [0] * (3 - len(out)))


def install_root():
    """D:\\FreeWorks when running from a FreeWorks installation, else None."""
    root = os.path.dirname(os.path.normpath(App.getUserAppDataDir()))
    if any(os.path.exists(os.path.join(root, n)) for n in ("FreeWorks.exe", "FreeWorks.cmd")):
        return root
    return None


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "FreeWorks-Updater", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", "replace")


def _check_thread():
    try:
        try:
            rel = json.loads(_fetch(API))
            _result.update(version=rel.get("tag_name", ""), notes=rel.get("body", "") or "", url=rel.get("html_url", ""))
        except Exception:
            # no release published yet: use the version on the main branch
            pkg = _fetch(RAW_PKG)
            v = pkg.split("<version>")[1].split("</version>")[0].strip()
            _result.update(version=v, notes="", url="https://github.com/%s" % REPO)
    except Exception as e:
        _result.update(error=str(e))
    _result["done"] = True


def check(manual=False):
    if not manual:
        if not params().GetBool("CheckForUpdates", True) or sys.platform != "win32" or install_root() is None:
            return
        last = params().GetFloat("LastUpdateCheck", 0.0)
        if time.time() - last < 86400:
            return
    params().SetFloat("LastUpdateCheck", time.time())
    _result.clear()
    threading.Thread(target=_check_thread, daemon=True).start()
    _poll(manual, 0)


def _poll(manual, n):
    if not _result.get("done"):
        if n < 30:
            QtCore.QTimer.singleShot(1000, lambda: _poll(manual, n + 1))
        return
    if "error" in _result:
        log("update check failed: %s" % _result["error"])
        if manual:
            QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "FreeWorks", "Could not check for updates:\n%s" % _result["error"])
        return
    latest = _result.get("version", "")
    if latest and _vtuple(latest) > _vtuple(__version__):
        _offer(latest)
    elif manual:
        QtWidgets.QMessageBox.information(Gui.getMainWindow(), "FreeWorks", "FreeWorks %s is up to date." % __version__)


def _offer(latest):
    win = Gui.getMainWindow()
    box = QtWidgets.QMessageBox(win)
    box.setWindowTitle("FreeWorks update")
    box.setIcon(QtWidgets.QMessageBox.Information)
    box.setText("FreeWorks %s is available (you have %s)." % (latest.lstrip("vV"), __version__))
    notes = _result.get("notes", "").strip()
    if notes:
        box.setDetailedText(notes)
    root = install_root()
    if root and sys.platform == "win32":
        box.setInformativeText("Update now? FreeWorks will close, update (your settings are kept) and start again.")
        upd = box.addButton("Update now", QtWidgets.QMessageBox.AcceptRole)
    else:
        box.setInformativeText("Download it from GitHub.")
        upd = None
    page = box.addButton("Open GitHub page", QtWidgets.QMessageBox.HelpRole)
    box.addButton("Later", QtWidgets.QMessageBox.RejectRole)
    box.exec_()
    clicked = box.clickedButton()
    if clicked is page:
        from PySide import QtGui
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(_result.get("url") or "https://github.com/%s" % REPO))
    elif upd is not None and clicked is upd:
        _run_update(root)


def _run_update(root):
    import subprocess
    cmd = ("$s = Invoke-RestMethod -Uri '%s' -Headers @{'User-Agent'='FreeWorks-Updater'}; "
           "& ([scriptblock]::Create($s)) -InstallDir '%s' -UpdateOnly -WaitPid %d -Restart") % (GET_PS1, root, os.getpid())
    try:
        subprocess.Popen(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                         creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    except Exception as e:
        QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "FreeWorks", "Could not start the updater:\n%s" % e)
        return
    Gui.getMainWindow().close()
