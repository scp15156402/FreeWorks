"""Move Component / Rotate Component PropertyManager with SOLIDWORKS-style Collision Detection.

Moves are exact (By Delta XYZ, To XYZ, rotate About Entity / assembly X, Y, Z by an angle). With
"Collision Detection" on, the move stops at the first contact with another component (bisection to
0.01 mm / 0.01 deg), the colliding component is reported and highlighted - the way CSWP segment 3
uses "rotate the arm until it collides, then report...". Free drag stays FreeCAD's dragger.
"""
import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import harden, icon, log, safe_slow
from . import mates
from .style import STYLE

Qt = QtCore.Qt
VOL_TOL = 1e-3          # mm^3: touching faces (mates) are not collisions
_PANEL = {"p": None}


# ------------------------------------------------------------------ engine
def components(asm):
    out = []
    for o in asm.Group:
        if o.TypeId == "App::Link" or o.isDerivedFrom("App::Link") or o.TypeId == "Assembly::AssemblyLink":
            out.append(o)
    return out


def _shape(o):
    import Part
    try:
        s = Part.getShape(o, "", needSubElement=False, transform=True)
        return s if s is not None and not s.isNull() and s.Solids else None
    except Exception:
        return None


def collisions(moving_shape, others):
    """[(component, overlap volume)] of `others` [(obj, shape)] that overlap the moving shape."""
    out = []
    bb = moving_shape.BoundBox
    for o, s in others:
        if not bb.intersect(s.BoundBox):
            continue
        try:
            v = moving_shape.common(s).Volume
        except Exception:
            continue
        if v > VOL_TOL:
            out.append((o, v))
    return out


def _moved(base, delta):
    s = base.copy()
    s.Placement = delta.multiply(s.Placement)
    return s


def motion(kind, amount, axis_point=None, axis_dir=None, vec=None):
    """Placement for fraction t of a move: translation vec*amount*t or rotation amount*t degrees."""
    if kind == "translate":
        return lambda t: App.Placement(vec * (amount * t), App.Rotation())
    c, d = axis_point, axis_dir

    def rot(t):
        r = App.Rotation(d, amount * t)
        # rotation about an axis through c: x -> c + R (x - c)
        return App.Placement(c - r.multVec(c), r)
    return rot


def move_until_collision(comp, others, delta_of_t, length, step):
    """Largest t in [0, 1] reachable without collision. length = path length (mm or deg)."""
    base = _shape(comp)
    if base is None:
        return 1.0, []
    n = max(2, int(math.ceil(abs(length) / step)))
    prev = 0.0
    for k in range(1, n + 1):
        t = k / float(n)
        hit = collisions(_moved(base, delta_of_t(t)), others)
        if hit:
            lo, hi = prev, t
            for _ in range(24):
                mid = (lo + hi) / 2.0
                if collisions(_moved(base, delta_of_t(mid)), others):
                    hi = mid
                else:
                    lo = mid
                if (hi - lo) * abs(length) < 1e-3:
                    break
            return lo, hit
        prev = t
    return 1.0, []


def apply_move(asm, comp, kind, amount, vec=None, axis=None, collide=True):
    """Move one component. Returns (fraction done, [(colliding component, volume)])."""
    if kind == "translate":
        n = vec.Length
        if n < 1e-12:
            return 1.0, []
        d = vec * (1.0 / n)
        f = motion("translate", n * amount, vec=d)
        length, step = n * amount, 0.5
    else:
        c, d = axis
        f = motion("rotate", amount, c, d)
        length, step = amount, 2.0
    t, hit = 1.0, []
    if collide:
        others = [(o, s) for o in components(asm) if o is not comp for s in [_shape(o)] if s is not None]
        t, hit = move_until_collision(comp, others, f, length, step)
    comp.Placement = f(t).multiply(comp.Placement)
    asm.Document.recompute()
    return t, hit


def axis_of(ref):
    """(point, direction) of a cylinder face, circular edge or line edge reference."""
    s = mates.element(ref)
    if s is None:
        return None
    try:
        if s.ShapeType == "Face":
            surf = s.Surface
            if hasattr(surf, "Axis") and hasattr(surf, "Center"):
                return surf.Center, surf.Axis
            if hasattr(surf, "Axis") and hasattr(surf, "Position"):
                return surf.Position, surf.Axis
            u0, u1, v0, v1 = s.ParameterRange
            return s.CenterOfMass, s.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
        if s.ShapeType == "Edge":
            c = s.Curve
            if hasattr(c, "Center") and hasattr(c, "Axis"):
                return c.Center, c.Axis
            return s.Vertexes[0].Point, (s.Vertexes[-1].Point - s.Vertexes[0].Point).normalize()
    except Exception as e:
        log("axis: %s" % e)
    return None


# ------------------------------------------------------------------ PropertyManager
def start(rotate=False):
    doc = App.ActiveDocument
    asm = mates.assembly_of(doc)
    if asm is None:
        QtWidgets.QMessageBox.information(Gui.getMainWindow(), "Move Component", "Open an assembly first.")
        return
    if Gui.Control.activeDialog():
        Gui.Control.closeDialog()
    mates.activate(asm)
    sel = [(s.Object, n, p) for s in Gui.Selection.getSelectionEx("", 0)
           for n, p in zip(s.SubElementNames or [""], s.PickedPoints or [None] * max(1, len(s.SubElementNames)))]
    p = MovePanel(asm, rotate)
    _PANEL["p"] = p
    Gui.Control.showDialog(p)
    for root, sub, pos in sel[:1]:
        p.pick(root, sub, pos)


@harden
class _Observer:
    def __init__(self, panel):
        self.panel = panel

    def addSelection(self, doc_name, obj_name, sub, pos):
        root = App.getDocument(doc_name).getObject(obj_name)
        QtCore.QTimer.singleShot(0, lambda: self.panel.pick(root, sub, pos))


@harden
class MovePanel:
    def __init__(self, asm, rotate=False):
        self.asm = asm
        self.doc = asm.Document
        self.comp = None
        self.axis = None
        self.picking_axis = False
        self.form = self._build(rotate)
        self.obs = _Observer(self)
        Gui.Selection.addObserver(self.obs)

    def _build(self, rotate):
        w = QtWidgets.QWidget()
        w.setWindowTitle("Rotate Component" if rotate else "Move Component")
        w.setWindowIcon(icon("rotate_component" if rotate else "move_component"))
        lay = QtWidgets.QVBoxLayout(w)
        g = QtWidgets.QGroupBox("Component")
        gl = QtWidgets.QVBoxLayout(g)
        self.comp_lbl = QtWidgets.QLabel("Select a component in the graphics area or the FeatureManager.")
        self.comp_lbl.setWordWrap(True)
        gl.addWidget(self.comp_lbl)
        lay.addWidget(g)

        g = QtWidgets.QGroupBox("Move")
        f = QtWidgets.QFormLayout(g)
        self.b_move = QtWidgets.QRadioButton("By Delta XYZ")
        self.b_rot = QtWidgets.QRadioButton("Rotate by angle")
        self.b_move.setChecked(not rotate)
        self.b_rot.setChecked(rotate)
        f.addRow(self.b_move)
        self.d = []
        for a in "XYZ":
            sp = QtWidgets.QDoubleSpinBox()
            sp.setRange(-1e6, 1e6)
            sp.setDecimals(2)
            sp.setSuffix(" mm")
            f.addRow("Δ%s:" % a, sp)
            self.d.append(sp)
        f.addRow(self.b_rot)
        self.axis_box = QtWidgets.QComboBox()
        self.axis_box.addItems(["About Entity (pick an edge or cylinder)", "Assembly X axis", "Assembly Y axis", "Assembly Z axis"])
        self.axis_box.currentIndexChanged.connect(self._axis_mode)
        f.addRow("Axis:", self.axis_box)
        self.axis_lbl = QtWidgets.QLabel("")
        f.addRow("", self.axis_lbl)
        self.angle = QtWidgets.QDoubleSpinBox()
        self.angle.setRange(-3600, 3600)
        self.angle.setDecimals(2)
        self.angle.setSuffix(" deg")
        self.angle.setValue(90.0)
        f.addRow("Angle:", self.angle)
        lay.addWidget(g)

        g = QtWidgets.QGroupBox("Options")
        ol = QtWidgets.QVBoxLayout(g)
        self.collide = QtWidgets.QCheckBox("Collision Detection: stop at collision")
        self.collide.setChecked(True)
        ol.addWidget(self.collide)
        lay.addWidget(g)
        row = QtWidgets.QHBoxLayout()
        b = QtWidgets.QPushButton("Apply")
        b.clicked.connect(self.apply)
        row.addStretch(1)
        row.addWidget(b)
        drag = QtWidgets.QPushButton("Free Drag...")
        drag.setToolTip("FreeCAD's dragger for free moves (no collision detection)")
        drag.clicked.connect(self.free_drag)
        row.addWidget(drag)
        lay.addLayout(row)
        self.result = QtWidgets.QLabel("")
        self.result.setWordWrap(True)
        lay.addWidget(self.result)
        lay.addStretch(1)
        w.setStyleSheet(STYLE)
        self._axis_mode(0)
        return w

    def _axis_mode(self, i):
        self.picking_axis = (i == 0)
        if self.picking_axis and self.axis is None:
            self.axis_lbl.setText("Pick a cylindrical face or an edge for the axis.")

    def pick(self, root, sub, pos):
        if root is None:
            return
        ref = mates.make_ref(self.asm, root, sub or "", pos)
        if ref is None:
            return
        if self.comp is not None and self.b_rot.isChecked() and self.picking_axis and (sub or "").split(".")[-1][:4] in ("Edge", "Face"):
            ax = axis_of(ref)
            if ax:
                self.axis = ax
                self.axis_lbl.setText("Axis: %s@%s" % (sub.split(".")[-1], ref[0].Label))
            return
        self.comp = mates.component(ref)
        self.comp_lbl.setText("<b>%s</b>" % self.comp.Label)

    def current_axis(self):
        i = self.axis_box.currentIndex()
        if i == 0:
            return self.axis
        d = [App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)][i - 1]
        return (self.comp.Placement.Base if self.comp else App.Vector()), d

    @safe_slow
    def apply(self):
        """User-invoked move; collision detection runs boolean checks, so it may take a moment."""
        if self.comp is None:
            self.result.setText("Select a component first.")
            return
        self.doc.openTransaction("Move Component")
        try:
            if self.b_move.isChecked():
                vec = App.Vector(*[sp.value() for sp in self.d])
                t, hit = apply_move(self.asm, self.comp, "translate", 1.0, vec=vec, collide=self.collide.isChecked())
                done = "%.2f mm" % (vec.Length * t)
            else:
                ax = self.current_axis()
                if ax is None:
                    self.result.setText("Pick the rotation axis first.")
                    self.doc.abortTransaction()
                    return
                t, hit = apply_move(self.asm, self.comp, "rotate", self.angle.value(), axis=ax, collide=self.collide.isChecked())
                done = "%.2f deg" % (self.angle.value() * t)
        finally:
            self.doc.commitTransaction()
        if hit:
            names = ", ".join(o.Label for o, _ in hit)
            self.result.setText("<b>Collision</b> with %s after %s." % (names, done))
            try:
                Gui.Selection.clearSelection()
                for o, _ in hit:
                    Gui.Selection.addSelection(self.asm.Document.Name, self.asm.Name, o.Name + ".")
            except Exception:
                pass
        else:
            self.result.setText("Moved %s." % done)

    def free_drag(self):
        comp = self.comp
        self._cleanup()
        Gui.Control.closeDialog()
        if comp is not None:
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(comp)
        QtCore.QTimer.singleShot(0, lambda: Gui.runCommand("Std_TransformManip"))

    def getStandardButtons(self):
        sb = QtWidgets.QDialogButtonBox.StandardButton
        v = sb.Ok
        return getattr(v, "value", v)

    def accept(self):
        self._cleanup()
        return True

    def reject(self):
        self._cleanup()
        return True

    def _cleanup(self):
        if getattr(self, "_cleaned", False):
            return
        self._cleaned = True
        try:
            Gui.Selection.removeObserver(self.obs)
        except Exception:
            pass
        _PANEL["p"] = None
