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
        "distance": "mate_distance", "angle": "mate_angle", "hinge": "mate_hinge", "gear": "mate_gear",
        "rack_pinion": "mate_rack", "screw": "mate_screw", "width": "mate_width",
        "limit_distance": "mate_limit_distance", "limit_angle": "mate_limit_angle"}
LIMITS = ("limit_distance", "limit_angle")
PM_STYLE = """
QGroupBox QToolButton { padding: 2px 4px; border: 1px solid transparent; border-radius: 3px; }
QGroupBox QToolButton:hover { border-color: #9DB7E0; background: #EEF4FD; }
QGroupBox QToolButton:checked { border-color: #2F7BE5; background: #D6E6FC; }
"""
_PANEL = {"p": None}


def start(edit=None):
    """FW_Mate entry point; edit = an existing mate (joint) to edit."""
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
    panel = MatePanel(asm, edit)
    _PANEL["p"] = panel
    Gui.Control.showDialog(panel)
    Gui.Selection.clearSelection()
    if edit is None:
        for root, sub, pos in pre[:2]:
            panel.add_selection(root, sub, pos)


def edit_selected():
    """FW_EditMate: edit the selected mate in the Mate PropertyManager."""
    for o in Gui.Selection.getSelection():
        if hasattr(o, "JointType") and getattr(o, "Reference2", None):
            start(edit=o)
            return
    QtWidgets.QMessageBox.information(Gui.getMainWindow(), "Edit Mate", "Select a mate in the Mates folder first.")


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
        self.value.setSuffix(mates.VALUE.get(current, ("", " mm", 0))[1])
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

    def __init__(self, asm, edit=None):
        self.asm = asm
        self.edit_name = None
        self.doc = asm.Document
        self.refs = []
        self.joint = None
        self.mate = None
        self.busy = False
        self._value_for = None
        self.added = []
        self.width_mode = False
        self.type_btns = {}
        self.form = self._build()
        self.toolbar = MateToolbar(self)
        self.obs = _Observer(self)
        try:
            _, U = mates._asm_modules()
            U.setJointsPickableState(self.doc, False)
        except Exception:
            pass
        Gui.Selection.addObserver(self.obs)
        if edit is not None:
            self._begin_edit(edit)
        self.sync()

    def _begin_edit(self, j):
        self.edit_name = j.Name
        self.refs = [[r[0], list(r[1])] for r in (j.Reference1, j.Reference2)]
        self.mate = mates.mate_of(j)
        val, neg = None, False
        if self.mate == "distance":
            d = mates._num(j.Distance)
            val, neg = abs(d), d < 0
        elif self.mate == "angle":
            val = mates._num(j.Angle)
        elif self.mate == "gear":
            val = mates._num(j.Distance2) / max(mates._num(j.Distance), 1e-9)
        elif self.mate == "rack_pinion":
            val = 2 * mates._num(j.Distance)
        elif self.mate == "screw":
            val = mates._num(j.Distance)
        if val is not None:
            self.value.blockSignals(True)
            self.value.setValue(val)
            self.value.blockSignals(False)
            self._value_for = self.mate
        self.flip_dim.blockSignals(True)
        self.flip_dim.setChecked(neg)
        self.flip_dim.blockSignals(False)
        self.doc.openTransaction("Edit Mate")
        self.joint = j
        self.form.setWindowTitle("Mate: " + j.Label)

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
        self.value_lbl = QtWidgets.QLabel()
        grid.addWidget(self.value_lbl, row, 0, 1, 2)
        row += 1
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

        g = QtWidgets.QGroupBox("Advanced Mates")
        grid = QtWidgets.QGridLayout(g)
        for i, t in enumerate(mates.ADVANCED):
            b = self._type_button(t, group)
            grid.addWidget(b, 0, i)
        self.lim_lbl = QtWidgets.QLabel("Min / Max:")
        self.vmin = QtWidgets.QDoubleSpinBox()
        self.vmax = QtWidgets.QDoubleSpinBox()
        for sp in (self.vmin, self.vmax):
            sp.setRange(-1e6, 1e6)
            sp.setDecimals(2)
            sp.setKeyboardTracking(False)
            sp.valueChanged.connect(lambda *_: self.limits_changed())
        grid.addWidget(self.lim_lbl, 1, 0)
        grid.addWidget(self.vmin, 1, 1)
        grid.addWidget(self.vmax, 1, 2)
        lay.addWidget(g)

        g = QtWidgets.QGroupBox("Mechanical Mates")
        grid = QtWidgets.QGridLayout(g)
        for i, t in enumerate(mates.MECHANICAL):
            grid.addWidget(self._type_button(t, group), i // 2, i % 2)
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
        w.setStyleSheet(STYLE + PM_STYLE)
        return w

    def _type_button(self, t, group):
        b = QtWidgets.QToolButton()
        b.setText({"rack_pinion": "Rack Pinion", "limit_distance": "Limit Distance", "limit_angle": "Limit Angle"}.get(t, mates.LABEL[t]))
        b.setIcon(icon(ICON[t]))
        b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        b.setCheckable(True)
        b.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        b.clicked.connect(lambda _=False, t=t: self.set_type(t))
        group.addButton(b)
        self.type_btns[t] = b
        return b

    def allowed_now(self):
        if self.width_mode:
            return ["width"]
        k = [mates.kind(r) for r in self.refs]
        if len(k) != 2:
            return ["width"]
        out = mates.allowed(*k)
        c1, c2 = mates.component(self.refs[0]), mates.component(self.refs[1])
        for t in LIMITS:
            if mates.motion_joint(self.asm, c1, c2, mates.LIMIT_JOINTS[t]) is not None:
                out.append(t)
        if "plane" in k and k[0] == k[1]:
            out.append("width")
        return out

    def sync(self):
        k = [mates.kind(r) for r in self.refs]
        allowed = self.allowed_now()
        for t, b in self.type_btns.items():
            b.setEnabled(t in allowed)
            b.setChecked(t == self.mate)
        show = self.mate in mates.VALUE
        self.value.setVisible(show)
        self.value_lbl.setVisible(show)
        if show:
            lbl, suffix, _ = mates.VALUE[self.mate]
            self.value_lbl.setText(lbl + ":")
            self.value.setSuffix(suffix)
        self.flip_dim.setVisible(self.mate == "distance")
        lim = self.mate in LIMITS
        for w in (self.lim_lbl, self.vmin, self.vmax):
            w.setVisible(lim)
        if lim:
            suf = " deg" if self.mate == "limit_angle" else " mm"
            self.vmin.setSuffix(suf)
            self.vmax.setSuffix(suf)
        can_flip = self.mate in mates.FLIPPABLE and self.joint is not None
        self.b_align.setEnabled(can_flip)
        self.b_anti.setEnabled(can_flip)
        self.b_add.setEnabled(self.joint is not None)
        self.sel.clear()
        for r, kk in zip(self.refs, k):
            el = r[1][0].split(".")[-1] if r[1] and r[1][0] else ""
            self.sel.addItem("%s@%s  (%s)" % (el or "Origin", r[0].Label, kk))
        if self.width_mode and len(self.refs) < 4:
            self.hint.setText(("Width selections: pick the two faces of the groove (%d/2)." % len(self.refs)) if len(self.refs) < 2
                              else "Tab selections: pick the two faces of the tab (%d/2)." % (len(self.refs) - 2))
        elif len(self.refs) < 2:
            self.hint.setText("Select %s face, edge or vertex." % ("a" if not self.refs else "a second"))
        else:
            self.hint.setText("%s mate. Change the type, then OK to add it." % mates.LABEL.get(self.mate, ""))
        if self.joint is not None:
            self.toolbar.sync(allowed, self.mate, self.value.value(), show)
        self.b_align.setEnabled(can_flip)

    # ---------------------------------------------------------------- selection
    def add_selection(self, root, sub, pos):
        if self.busy or root is None:
            return
        if self.edit_name:
            self.hint.setText("Editing a mate: change its type or values, or close the PropertyManager.")
            Gui.Selection.clearSelection()
            return
        need = 4 if self.width_mode else 2
        if len(self.refs) >= need:
            self.commit()                       # one pick too many: keep the current mate, start the next
        ref = mates.make_ref(self.asm, root, sub, pos)
        if ref is None:
            self.hint.setText("That isn't part of a component of this assembly.")
            return
        if self.width_mode:
            n = len(self.refs)
            if n == 1 and mates.component(self.refs[0]) != mates.component(ref):
                self.hint.setText("Both groove faces must be on the same component.")
                return
            if n >= 2 and mates.component(ref) == mates.component(self.refs[0]):
                self.hint.setText("Tab faces must be on the other component.")
                return
            if n == 3 and mates.component(self.refs[2]) != mates.component(ref):
                self.hint.setText("Both tab faces must be on the same component.")
                return
            self.refs.append(ref)
            if len(self.refs) == 4:
                self.apply("width")
                self.toolbar.show_near_cursor()
            self.sync()
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
            self.doc.openTransaction("Edit Mate" if self.edit_name else "Mate")
            if self.edit_name:
                orig = self.doc.getObject(self.edit_name)
                if orig is not None:
                    self.doc.removeObject(orig.Name)
            if mate in mates.VALUE and (mate != self._value_for or self.value.value() == 0):
                self.value.blockSignals(True)
                self.value.setValue(mates.default_value(mate, self.refs))
                self.value.blockSignals(False)
                self._value_for = mate
            if mate in LIMITS and self.vmin.value() == self.vmax.value() == 0:
                for sp, v in ((self.vmin, 0.0), (self.vmax, 90.0 if mate == "limit_angle" else 10.0)):
                    sp.blockSignals(True)
                    sp.setValue(v)
                    sp.blockSignals(False)
            self.joint = mates.create(self.asm, mate, [list(r) for r in self.refs], self.value.value(), self.flip_dim.isChecked(),
                                      self.vmin.value(), self.vmax.value())
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
        if self.edit_name and mate in ("width",) + LIMITS:
            self.hint.setText("Width and limit mates are added as new mates, not by editing this one.")
            return
        if mate == "width" and not self.width_mode:
            if self.joint is not None:
                self.doc.abortTransaction()
                self.joint = None
            keep = self.refs if len(self.refs) == 2 and mates.component(self.refs[0]) == mates.component(self.refs[1]) else []
            self.width_mode = True
            self.mate = "width"
            self.refs = list(keep)
            self.sync()
            return
        if mate != "width" and self.width_mode:
            self.width_mode = False
            self.refs = []
            self.mate = None
            self.sync()
            return
        if len(self.refs) == 2 and mate != self.mate:
            self.apply(mate)

    def limits_changed(self):
        if self.joint is not None and self.mate in LIMITS:
            self.apply(self.mate)

    def value_changed(self, v):
        if self.joint is not None and self.mate in mates.VALUE:
            mates.set_value(self.asm, self.joint, self.mate, v, self.flip_dim.isChecked())
        self.toolbar.sync(self.allowed_now(), self.mate, v, self.mate in mates.VALUE)

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
        text = self.joint.Label if self.mate not in LIMITS else "%s on %s" % (mates.LABEL[self.mate], self.joint.Label)
        it = QtWidgets.QListWidgetItem(icon(ICON.get(self.mate, "mate")), text)
        self.list.addItem(it)
        self.joint = None
        self.mate = None
        self.refs = []
        self.width_mode = False
        if self.edit_name:
            self.edit_name = None
            self._close_soon()
        self.toolbar.hide()
        Gui.Selection.clearSelection()
        self.sync()
        return True

    def _close_soon(self):
        self._cleanup()
        QtCore.QTimer.singleShot(0, Gui.Control.closeDialog)

    def discard(self):
        if self.joint is not None:
            self.doc.abortTransaction()
            self.doc.recompute()
        if self.edit_name:
            self.edit_name = None
            self.joint = None
            self.toolbar.hide()
            self._close_soon()
            return
        self.joint = None
        self.mate = None
        self.refs = []
        self.width_mode = False
        self.toolbar.hide()
        Gui.Selection.clearSelection()
        self.sync()

    # ---------------------------------------------------------------- task dialog API
    def getStandardButtons(self):
        sb = QtWidgets.QDialogButtonBox.StandardButton
        v = sb.Ok | sb.Close
        return getattr(v, "value", v)

    def accept(self):
        self.commit()
        self.edit_name = None
        self._cleanup()
        self.asm.recompute(True)
        return True

    def reject(self):
        if self.edit_name and self.joint is not None:
            self.doc.abortTransaction()
            self.doc.recompute()
            self.joint = None
            self.edit_name = None
        self.discard()
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
        doc = self.doc

        def _names():
            from . import asmtree
            if doc.Name in App.listDocuments():
                asmtree.sweep(doc)
        QtCore.QTimer.singleShot(0, _names)
