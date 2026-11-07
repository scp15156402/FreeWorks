"""Sketch-environment helpers: centerline mode and SolidWorks sketch status."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

from . import context, log, harden

_center = {"on": False, "sketch": None, "start": 0}


def start_centerline():
    sk = context.edited_sketch()
    if sk is None:
        return
    _center.update(on=True, sketch=sk.Name, start=sk.GeometryCount)
    _attach()
    from . import commands
    commands.run("Sketcher_CreateLine")
    commands.msg("Centerline: lines you draw now are construction lines (Esc to finish)", 5000)


def cancel():
    _center["on"] = False
    _detach()


def on_command(key):
    if key != "centerline" and _center["on"]:
        cancel()


def _convert():
    if not _center["on"]:
        return
    sk = context.edited_sketch()
    if sk is None or sk.Name != _center["sketch"]:
        cancel()
        return
    n0 = _center["start"]
    n = sk.GeometryCount
    changed = False
    for i in range(n0, n):
        g = sk.Geometry[i]
        if g.TypeId == "Part::GeomLineSegment" and not sk.getConstruction(i):
            sk.setConstruction(i, True)
            changed = True
    _center["start"] = n
    if changed:
        sk.recompute()


@harden
class _Obs:
    def slotChangedObject(self, obj, prop):
        if _center["on"] and prop == "Geometry" and obj.Name == _center["sketch"]:
            QtCore.QTimer.singleShot(0, _convert)


_obs = None


def _attach():
    """The observer sees every property change of every object, so it is registered only
    while the Centerline tool runs (never during normal modelling / big rebuilds)."""
    global _obs
    if _obs is None:
        _obs = _Obs()
        App.addDocumentObserver(_obs)


def _detach():
    global _obs
    if _obs is not None:
        try:
            App.removeDocumentObserver(_obs)
        except Exception:
            pass
        _obs = None


def install():
    pass   # nothing global to install any more (kept for API compatibility)


def status():
    """('Under Defined' | 'Fully Defined' | 'Over Defined', color) for the edited sketch."""
    sk = context.edited_sketch()
    if sk is None:
        return None
    try:
        if sk.ConflictingConstraints or sk.MalformedConstraints or sk.RedundantConstraints:
            return ("Over Defined", "#C62828")
        if sk.FullyConstrained:
            return ("Fully Defined", "#1B1B1B")
        dof = getattr(sk, "DoF", None)
        return ("Under Defined" + (" (%d DOF)" % dof if isinstance(dof, int) and dof > 0 else ""), "#1F5FD1")
    except Exception:
        return ("Under Defined", "#1F5FD1")
