"""SolidWorks mouse gestures: hold the right button in the graphics area and
drag toward a command.  A plain right-click still opens the context menu."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import catalog, context, params, safe, harden

Qt = QtCore.Qt
THRESHOLD = 12


def view_widgets():
    """The OpenGL widgets of all 3D views (mouse events land on these)."""
    mdi = context.mdi_area()
    out = []
    if mdi is None:
        return out
    for sw in mdi.subWindowList():
        w = sw.widget()
        if w is None or w.metaObject().className() != "Gui::View3DInventor":
            continue
        for gv in w.findChildren(QtWidgets.QGraphicsView):
            if gv.metaObject().className() == "Gui::View3DInventorViewer":
                out.append(gv.viewport())     # the QOpenGLWidget that gets the mouse
    return out


@harden
class _Gesture(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.reset()
        self.replaying = False

    def reset(self):
        self.down = None
        self.wheel = None
        self.widget = None

    def eventFilter(self, obj, ev):
        t = ev.type()
        if t not in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonRelease):
            return False
        if self.replaying:
            return False
        try:
            if t == QtCore.QEvent.MouseButtonPress:
                if ev.button() == Qt.RightButton and ev.buttons() == Qt.RightButton and params().GetBool("Gestures", True):
                    self.down = ev.globalPosition().toPoint()
                    self.local = ev.position()
                    self.widget = obj
                    return True                     # hold back until we know: click or gesture
                return False
            if self.down is None:
                return False
            gpos = ev.globalPosition().toPoint()
            if t == QtCore.QEvent.MouseMove:
                if self.wheel is None and (gpos - self.down).manhattanLength() > THRESHOLD:
                    self.open_wheel()
                if self.wheel is not None:
                    self.wheel.update_pos(gpos)
                return True
            if t == QtCore.QEvent.MouseButtonRelease and ev.button() == Qt.RightButton:
                if self.wheel is not None:
                    key = self.wheel.selected_key()
                    self.wheel.close()
                    self.wheel.deleteLater()
                    self.reset()
                    if key:
                        from . import commands
                        QtCore.QTimer.singleShot(0, lambda: commands.run_key(key))
                else:
                    w, loc, g = self.widget, self.local, self.down
                    self.reset()
                    # after this filter returns: a context menu opened here could close the
                    # document (and delete this view) while we are still inside its event
                    QtCore.QTimer.singleShot(0, lambda: self.replay(w, loc, g))
                return True
        except Exception:
            self.reset()
        return False

    def open_wheel(self):
        from .widgets import GestureWheel
        ctx = context.current()
        keys = catalog.GESTURES.get(ctx) or catalog.GESTURES["part"]
        keys = [k if k in catalog.C and catalog.first_existing(catalog.C[k]) else None for k in keys]
        self.wheel = GestureWheel(keys, self.down)
        self.wheel.show()

    def replay(self, w, loc, gpos):
        """Plain right-click: give FreeCAD the click it would have received."""
        if w is None:
            return
        self.replaying = True
        from . import contextmenu
        QtCore.QTimer.singleShot(0, contextmenu.reorganize)
        try:
            for t in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
                btns = Qt.RightButton if t == QtCore.QEvent.MouseButtonPress else Qt.NoButton
                e = QtGui.QMouseEvent(t, loc, QtCore.QPointF(gpos), Qt.RightButton, btns, Qt.NoModifier)
                QtWidgets.QApplication.sendEvent(w, e)
        finally:
            self.replaying = False


_g = None


@safe
def hook_views():
    global _g
    if _g is None:
        _g = _Gesture()
    for w in view_widgets():
        try:
            if not w.property("fw_gesture"):
                w.installEventFilter(_g)
                w.setProperty("fw_gesture", True)
        except RuntimeError:
            pass
