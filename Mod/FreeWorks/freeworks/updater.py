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

from . import __version__, log, params, safe

REPO = "scp15156402/FreeWorks"
STABLE_PKG = "https://raw.githubusercontent.com/%s/stable/Mod/FreeWorks/package.xml" % REPO
STABLE_LOG = "https://raw.githubusercontent.com/%s/stable/CHANGELOG.md" % REPO
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
    """Released version = version in package.xml on the 'stable' branch (same rule as get.ps1)."""
    try:
        pkg = _fetch(STABLE_PKG)
        v = pkg.split("<version>")[1].split("</version>")[0].strip()
        notes = ""
        try:
            notes = changelog_section(_fetch(STABLE_LOG), v)
        except Exception:
            pass
        _result.update(version=v, notes=notes, url="https://github.com/%s/blob/stable/CHANGELOG.md" % REPO)
    except Exception as e:
        _result.update(error=str(e))
    _result["done"] = True


@safe
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


@safe
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
    skipped = rolled_back_from()
    if not manual and skipped and latest.lstrip("vV") == skipped:
        return            # the user rolled back from this version; don't nag
    if latest and _vtuple(latest) > _vtuple(__version__):
        _offer(latest)
    elif manual:
        QtWidgets.QMessageBox.information(Gui.getMainWindow(), "FreeWorks", "FreeWorks %s is up to date." % __version__)


@safe
def _offer(latest):
    win = Gui.getMainWindow()
    box = QtWidgets.QMessageBox(win)
    box.setWindowTitle("FreeWorks update")
    box.setIcon(QtWidgets.QMessageBox.Information)
    box.setText("FreeWorks %s is available (you have %s)." % (latest.lstrip("vV"), __version__))
    notes = _result.get("notes", "").strip()
    if notes:
        box.setDetailedText(notes)       # "Show Details..." = what's new
    root = install_root()
    if root and sys.platform == "win32":
        box.setInformativeText("Update now? FreeWorks closes (it asks to save open documents), updates and starts again. Settings are kept; your projects are not affected.")
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
           "& ([scriptblock]::Create($s)) -InstallDir '%s' -UpdateOnly -WaitPid %d -Restart; "
           "Start-Sleep -Seconds 4") % (GET_PS1, root, os.getpid())
    try:
        subprocess.Popen(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                         creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    except Exception as e:
        QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "FreeWorks", "Could not start the updater:\n%s" % e)
        return
    Gui.getMainWindow().close()


# ---------------------------------------------------------------- release notes
def changelog_section(text, version):
    """The '## v<version>' section of CHANGELOG.md (without the heading)."""
    version = version.lstrip("vV")
    out, on = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if on:
                break
            on = line[3:].strip().lstrip("vV").startswith(version + " ") or line[3:].strip().lstrip("vV") == version
            continue
        if on:
            out.append(line)
    return "\n".join(out).strip()


def _local_changelog():
    from . import MOD_DIR
    root = install_root()
    for p in ([os.path.join(root, "CHANGELOG.md")] if root else []) + [os.path.join(MOD_DIR, "..", "..", "CHANGELOG.md")]:
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return f.read()
    return ""


@safe
def show_whats_new(force=False):
    """After an update, show what changed (once per version)."""
    last = params().GetString("LastSeenVersion", "")
    params().SetString("LastSeenVersion", __version__)
    if not force and (not last or last == __version__):
        return
    sec = changelog_section(_local_changelog(), __version__)
    if not sec:
        if force:
            sec = "No release notes found for this version."
        else:
            return
    d = QtWidgets.QDialog(Gui.getMainWindow())
    d.setWindowTitle("What's New in FreeWorks %s" % __version__)
    d.resize(620, 420)
    lay = QtWidgets.QVBoxLayout(d)
    tb = QtWidgets.QTextBrowser()
    tb.setOpenExternalLinks(True)
    try:
        tb.setMarkdown(sec)
    except Exception:
        tb.setPlainText(sec)
    lay.addWidget(tb)
    bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
    bb.accepted.connect(d.accept)
    lay.addWidget(bb)
    d.exec_()


# ---------------------------------------------------------------- rollback
def previous_version():
    root = install_root()
    if not root:
        return None
    p = os.path.join(root, "_previous")
    if not os.path.isdir(os.path.join(p, "Mod", "FreeWorks")):
        return None
    try:
        with open(os.path.join(p, "version.txt"), encoding="utf-8-sig") as f:
            return f.read().strip() or "previous"
    except Exception:
        return "previous"


def rolled_back_from():
    root = install_root()
    if not root:
        return None
    try:
        with open(os.path.join(root, "rolled_back_from.txt"), encoding="utf-8-sig") as f:
            return f.read().strip()
    except Exception:
        return None


@safe
def rollback():
    win = Gui.getMainWindow()
    prev = previous_version()
    if sys.platform != "win32" or not prev:
        QtWidgets.QMessageBox.information(win, "FreeWorks", "There is no previous FreeWorks version to roll back to.")
        return
    r = QtWidgets.QMessageBox.question(
        win, "Roll back FreeWorks",
        "Go back from FreeWorks %s to %s?\n\nFreeWorks closes (it asks to save open documents), switches version "
        "and starts again. Your projects and settings are kept. You can update again at any time." % (__version__, prev))
    if r != QtWidgets.QMessageBox.Yes:
        return
    import subprocess
    cmd = ("$s = Invoke-RestMethod -Uri '%s' -Headers @{'User-Agent'='FreeWorks-Updater'}; "
           "& ([scriptblock]::Create($s)) -Rollback -WaitPid %d -Restart; Start-Sleep -Seconds 4") % (GET_PS1, os.getpid())
    try:
        subprocess.Popen(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                         creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    except Exception as e:
        QtWidgets.QMessageBox.warning(win, "FreeWorks", "Could not start the rollback:\n%s" % e)
        return
    win.close()
