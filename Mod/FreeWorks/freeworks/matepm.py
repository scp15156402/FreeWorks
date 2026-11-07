"""Mate PropertyManager - the SOLIDWORKS way of mating in a FreeCAD assembly.

Pick two faces/edges/vertices: the best mate is applied at once (preview), a pop-up mate toolbar
appears at the cursor, the PropertyManager shows Mate Selections, Standard / Mechanical mates,
distance/angle values and Mate alignment. Click OK (or press Enter) to keep the mate and continue
with the next one; Close finishes. Every mate is its own undo step; cancelling a pending mate
puts the parts back.
"""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import harden, icon, log, safe
from . import mates
from .style import STYLE

Qt = QtCore.Qt
ICON = {"coincident": "mate_coincident", "parallel": "mate_parallel", "perpendicular": "mate_perpendicular",
        "tangent": "mate_tangent", "concentric": "mate_concentric", "lock": "mate_lock",
        "distance": "mate_distance", "angle": "mate_angle", "hinge": "mate_hinge"}
_PANEL = {"p": None}


def start():
    """FW_Mate entry point."""
    doc = App.ActiveDocument
    asm = mates.assembly_of(doc)
    if asm is None:
        QtWidgets.QMessageBox.information(Gui.getMainWindow(), "Mate",
                                          "Mates are added in an assembly. Create one with File > New > Assembly.")
        return
    if Gui.Control.activeDialog():
        Gui.Control.closeDialog()
    mates.activate(asm)
    pre = []
    for s in Gui.Selection.getSelectionEx("", 0):
        for n, p in zip(s.SubElementNames, s.PickedPoints or [None] * len(s.SubElementNames)):
            pre.append((s.Object, n, p))
    panel = MatePanel(asm)
    _PANEL["p"] = panel
    Gui.Control.showDialog(panel)
    Gui.Selection.clearSelection()
    for root, sub, pos in pre[:2]:
        panel.add_selection(root, sub, pos)


@harden
class _Observer:
    def __init__(self, panel):
        self.panel = panel

    def addSelection(self, doc_name, obj_name, sub, pos):
        if self.panel.busy:
            return
        root = App.getDocument(doc_name).getObject(obj_name)
        QtCore.QTimer.singleShot(0, lambda: self.panel.add_selection(root, sub, pos))

    def removeSelection(self, doc_name, obj_name, sub):
        pass

    def clearSelection(self, doc_name):
        pass


@harden
class MateToolbar(QtWidgets.QFrame):
    """Pop-up mate toolbar shown next to the cursor after the second pick."""

    def __init__(self, panel):
        super().__init__(Gui.getMainWindow(), Qt.Tool | Qt.FramelessWindowHint)
        self.setObjectName("FreeWorksPopupFrame")
        self.setStyleSheet(STYLE)
        self.panel = panel
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(4, 3, 4, 3)
        lay.setSpacing(2)
        self.buttons = {}
        for t in mates.STANDARD:
            b = QtWidgets.QToolButton()
            b.setIcon(icon(ICON[t]))
            b.setToolTip(mates.LABEL[t])
            b.setCheckable(True)
            b.setAutoRaise(True)
            b.clicked.connect(lambda _=False, t=t: panel.set_type(t))
            lay.addWidget(b)
            self.buttons[t] = b
        self.value = QtWidgets.QDoubleSpinBox()
        self.value.setRange(0, 1e6)
        self.value.setDecimals(2)
        self.value.setKeyboardTracking(False)
        self.value.valueChanged.connect(panel.value_changed_from_toolbar)
        self.value.setVisible(False)
        lay.addWidget(self.value)
        self.flip = QtWidgets.QToolButton()
        self.flip.setIcon(icon("mate_antialign"))
        self.flip.setToolTip("Flip mate alignment")
        self.flip.setAutoRaise(True)
        self.flip.clicked.connect(panel.flip)
        lay.addWidget(self.flip)
        ok = QtWidgets.QToolButton()
        ok.setIcon(icon("ok"))
        ok.setToolTip("Add/Finish Mate")
        ok.setAutoRaise(True)
        ok.clicked.connect(panel.commit)
        lay.addWidget(ok)
        no = QtWidgets.QToolButton()
        no.setIcon(icon("cancel"))
        no.setToolTip("Undo this mate")
        no.setAutoRaise(True)
        no.clicked.connect(panel.discard)
        lay.addWidget(no)

    def sync(self, allowed, current, value, show_value):
        for t, b in self.buttons.items():
            b.setEnabled(t in allowed)
            b.setChecked(t == current)
        self.value.blockSignals(True)
        self.value.setVisible(show_value)
        self.value.setSuffix(" deg" if current == "angle" else " mm")
        self.value.setValue(value)
        self.value.blockSignals(False)

    def show_near_cursor(self):
        self.adjustSize()
        p = QtGui.QCursor.pos() + QtCore.QPoint(18, 18)
        scr = QtGui.QGuiApplication.screenAt(p) or QtGui.QGuiApplication.primaryScreen()
        r = scr.availableGeometry()
        self.move(min(p.x(), r.right() - self.width()), min(p.y(), r.bottom() - self.height()))
        self.show()
        self.raise_()


@harden
class MatePanel:
    """FreeCAD task panel (= PropertyManager) for mates."""

    def __init__(self, asm):
        self.asm = asm
        self.doc = asm.Document
        self.refs = []
        self.joint = None
        self.mate = None
        self.busy = False
        self.added = []
        self.form = self._build()
        self.toolbar = MateToolbar(self)
        self.obs = _Observer(self)
        try:
            _, U = mates._asm_modules()
            U.setJointsPickableState(self.doc, False)
        except Exception:
            pass
        Gui.Selection.addObserver(self.obs)
        self.sync()

    # ---------------------------------------------------------------- UI
    def _build(self):
        w = QtWidgets.QWidget()
        w.setWindowTitle("Mate")
        w.setWindowIcon(icon("mate"))
        lay = QtWidgets.QVBoxLayout(w)
        g = QtWidgets.QGroupBox("Mate Selections")
        gl = QtWidgets.QVBoxLayout(g)
        self.sel = QtWidgets.QListWidget()
        self.sel.setMaximumHeight(64)
        gl.addWidget(self.sel)
        self.hint = QtWidgets.QLabel("Select two faces, edges or vertices on different components.")
        self.hint.setWordWrap(True)
        gl.addWidget(self.hint)
        lay.addWidget(g)

        g = QtWidgets.QGroupBox("Standard Mates")
        grid = QtWidgets.QGridLayout(g)
        self.type_btns = {}
        group = QtWidgets.QButtonGroup(w)
        group.setExclusive(True)
        for i, t in enumerate(mates.STANDARD):
            b = QtWidgets.QToolButton()
            b.setText(mates.LABEL[t])
            b.setIcon(icon(ICON[t]))
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            b.setCheckable(True)
            b.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            b.clicked.connect(lambda _=False, t=t: self.set_type(t))
            group.addButton(b)
            grid.addWidget(b, i // 2, i % 2)
            self.type_btns[t] = b
        row = len(mates.STANDARD) // 2
        self.value = QtWidgets.QDoubleSpinBox()
        self.value.setRange(0, 1e6)
        self.value.setDecimals(2)
        self.value.setKeyboardTracking(False)
        self.value.valueChanged.connect(self.value_changed)
        grid.addWidget(self.value, row, 0)
        self.flip_dim = QtWidgets.QCheckBox("Flip dimension")
        self.flip_dim.toggled.connect(lambda *_: self.value_changed(self.value.value()))
        grid.addWidget(self.flip_dim, row, 1)
        lay.addWidget(g)

        g = QtWidgets.QGroupBox("Mechanical Mates")
        ml = QtWidgets.QHBoxLayout(g)
        b = QtWidgets.QToolButton()
        b.setText("Hinge")
        b.setIcon(icon(ICON["hinge"]))
        b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        b.setCheckable(True)
        b.clicked.connect(lambda: self.set_type("hinge"))
        group.addButton(b)
        self.type_btns["hinge"] = b
        ml.addWidget(b)
        for key, label in (("mate_gear", "Gear"), ("mate_rack", "Rack Pinion"), ("mate_screw", "Screw")):
            bb = QtWidgets.QToolButton()
            bb.setText(label)
            bb.setToolTip(label + " - opens FreeCAD's joint panel for this mechanical mate")
            bb.clicked.connect(lambda _=False, k=key: self.mechanical(k))
            ml.addWidget(bb)
        ml.addStretch(1)
        lay.addWidget(g)

        g = QtWidgets.QGroupBox("Mate alignment")
        al = QtWidgets.QHBoxLayout(g)
        self.b_align = QtWidgets.QToolButton()
        self.b_align.setIcon(icon("mate_align"))
        self.b_align.setText("Aligned")
        self.b_anti = QtWidgets.QToolButton()
        self.b_anti.setIcon(icon("mate_antialign"))
        self.b_anti.setText("Anti-Aligned")
        for b in (self.b_align, self.b_anti):
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            b.setCheckable(True)
            al.addWidget(b)
        ag = QtWidgets.QButtonGroup(w)
        ag.addButton(self.b_align)
        ag.addButton(self.b_anti)
        self.b_anti.setChecked(True)
        self.b_align.clicked.connect(lambda: self._alignment_clicked(True))
        self.b_anti.clicked.connect(lambda: self._alignment_clicked(False))
        al.addStretch(1)
        lay.addWidget(g)

        g = QtWidgets.QGroupBox("Mates")
        ml = QtWidgets.QVBoxLayout(g)
        self.list = QtWidgets.QListWidget()
        self.list.setMaximumHeight(110)
        ml.addWidget(self.list)
        lay.addWidget(g)
        btns = QtWidgets.QHBoxLayout()
        self.b_add = QtWidgets.QPushButton("Add Mate")
        self.b_add.clicked.connect(self.commit)
        btns.addStretch(1)
        btns.addWidget(self.b_add)
        lay.addLayout(btns)
        lay.addStretch(1)
        w.setStyleSheet(STYLE)
        return w

    def sync(self):
        k = [mates.kind(r) for r in self.refs]
        allowed = mates.allowed(*k) if len(k) == 2 else []
        for t, b in self.type_btns.items():
            b.setEnabled(t in allowed)
            b.setChecked(t == self.mate)
        show = self.mate in ("distance", "angle")
        self.value.setVisible(show)
        self.flip_dim.setVisible(self.mate == "distance")
        self.value.setSuffix(" deg" if self.mate == "angle" else " mm")
        can_flip = self.mate in mates.FLIPPABLE and self.joint is not None
        self.b_align.setEnabled(can_flip)
        self.b_anti.setEnabled(can_flip)
        self.b_add.setEnabled(self.joint is not None)
        self.sel.clear()
        for r, kk in zip(self.refs, k):
            el = r[1][0].split(".")[-1] if r[1] and r[1][0] else ""
            self.sel.addItem("%s@%s  (%s)" % (el or "Origin", r[0].Label, kk))
        if len(self.refs) < 2:
            self.hint.setText("Select %s face, edge or vertex." % ("a" if not self.refs else "a second"))
        else:
            self.hint.setText("%s mate. Change the type, then OK to add it." % mates.LABEL.get(self.mate, ""))
        if self.joint is not None:
            self.toolbar.sync(allowed, self.mate, self.value.value(), show)

    # ---------------------------------------------------------------- selection
    def add_selection(self, root, sub, pos):
        if self.busy or root is None:
            return
        if len(self.refs) >= 2:
            self.commit()                       # third pick: keep the current mate, start the next
        ref = mates.make_ref(self.asm, root, sub, pos)
        if ref is None:
            self.hint.setText("That isn't part of a component of this assembly.")
            return
        if self.refs and mates.component(self.refs[0]) == mates.component(ref):
            self.hint.setText("Pick the second entity on a different component.")
            return
        self.refs.append(ref)
        if len(self.refs) == 2:
            k = [mates.kind(r) for r in self.refs]
            self.apply(mates.suggest(*k))
            self.toolbar.show_near_cursor()
        self.sync()

    # ---------------------------------------------------------------- mate life cycle
    def apply(self, mate):
        """(Re)create the pending joint for this mate type inside its own transaction."""
        self.busy = True
        try:
            if self.joint is not None:
                self.doc.abortTransaction()
                self.joint = None
            self.mate = mate
            self.doc.openTransaction("Mate")
            if mate == "distance" and self.value.value() == 0:
                self.value.blockSignals(True)
                self.value.setValue(10.0)
                self.value.blockSignals(False)
            if mate == "angle" and self.value.value() == 0:
                self.value.blockSignals(True)
                self.value.setValue(90.0)
                self.value.blockSignals(False)
            self.joint = mates.create(self.asm, mate, [list(r) for r in self.refs], self.value.value(), self.flip_dim.isChecked())
            self.b_anti.setChecked(True)
        except Exception as e:
            log("mate %s: %s" % (mate, e))
            self.hint.setText("Couldn't add a %s mate with these selections." % mates.LABEL.get(mate, mate))
            try:
                self.doc.abortTransaction()
            except Exception:
                pass
            self.joint = None
        finally:
            self.busy = False
        Gui.Selection.clearSelection()
        self.sync()

    def set_type(self, mate):
        if len(self.refs) == 2 and mate != self.mate:
            self.apply(mate)

    def value_changed(self, v):
        if self.joint is not None and self.mate in ("distance", "angle"):
            mates.set_value(self.asm, self.joint, self.mate, v, self.flip_dim.isChecked())
        self.toolbar.sync(mates.allowed(*[mates.kind(r) for r in self.refs]) if len(self.refs) == 2 else [],
                          self.mate, v, self.mate in ("distance", "angle"))

    def value_changed_from_toolbar(self, v):
        self.value.setValue(v)

    def _alignment_clicked(self, aligned):
        if self.joint is not None and self.mate in mates.FLIPPABLE:
            mates.flip(self.asm, self.joint)

    def flip(self):
        if self.joint is not None and self.mate in mates.FLIPPABLE:
            mates.flip(self.asm, self.joint)
            (self.b_align if self.b_anti.isChecked() else self.b_anti).setChecked(True)

    def commit(self):
        if self.joint is None:
            return False
        self.doc.commitTransaction()
        self.added.append(self.joint)
        it = QtWidgets.QListWidgetItem(icon(ICON.get(self.mate, "mate")), self.joint.Label)
        self.list.addItem(it)
        self.joint = None
        self.mate = None
        self.refs = []
        self.toolbar.hide()
        Gui.Selection.clearSelection()
        self.sync()
        return True

    def discard(self):
        if self.joint is not None:
            self.doc.abortTransaction()
            self.doc.recompute()
        self.joint = None
        self.mate = None
        self.refs = []
        self.toolbar.hide()
        Gui.Selection.clearSelection()
        self.sync()

    def mechanical(self, key):
        self.discard()
        self._cleanup()
        Gui.Control.closeDialog()
        from . import commands
        QtCore.QTimer.singleShot(0, lambda: commands.run_key(key))

    # ---------------------------------------------------------------- task dialog API
    def getStandardButtons(self):
        sb = QtWidgets.QDialogButtonBox.StandardButton
        v = sb.Ok | sb.Close
        return getattr(v, "value", v)

    def accept(self):
        self.commit()
        self._cleanup()
        self.asm.recompute(True)
        return True

    def reject(self):
        self.discard()
        self._cleanup()
        return True

    def _cleanup(self):
        try:
            Gui.Selection.removeObserver(self.obs)
        except Exception:
            pass
        try:
            _, U = mates._asm_modules()
            U.setJointsPickableState(self.doc, True)
        except Exception:
            pass
        try:
            self.toolbar.close()
            self.toolbar.deleteLater()
        except Exception:
            pass
        _PANEL["p"] = None
