"""Sketch relations the SOLIDWORKS way: Display/Delete Relations and the sketch status.

Display/Delete Relations lists the relations (FreeCAD constraints) of the sketch being edited with
SOLIDWORKS names, the entities they act on and their state, filters All / Selected entities /
Dimensions, and deletes the chosen ones or all (after a confirmation) as one undo step.
"""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import context, harden, icon
from .style import STYLE

Qt = QtCore.Qt
SW_NAME = {
    "Coincident": "Coincident", "Horizontal": "Horizontal", "Vertical": "Vertical", "Parallel": "Parallel",
    "Perpendicular": "Perpendicular", "Tangent": "Tangent", "Equal": "Equal", "Symmetric": "Symmetric",
    "PointOnObject": "Coincident (point on curve)", "Block": "Fix", "Lock": "Fix (locked point)",
    "Distance": "Distance (dimension)", "DistanceX": "Horizontal distance (dimension)",
    "DistanceY": "Vertical distance (dimension)", "Radius": "Radius (dimension)", "Diameter": "Diameter (dimension)",
    "Angle": "Angle (dimension)", "Weight": "Weight", "SnellsLaw": "Snell's law", "InternalAlignment": "Internal alignment",
}
DIMENSIONS = ("Distance", "DistanceX", "DistanceY", "Radius", "Diameter", "Angle")


def _entity(sk, geo, pos):
    if geo == -1:
        return "Point1@Origin" if pos == 1 else "X Axis"
    if geo == -2:
        return "Y Axis"
    if geo <= -2000 or geo is None:
        return ""
    if geo < 0:
        return "External%d" % (-geo - 2)
    try:
        g = sk.Geometry[geo]
        kind = type(g).__name__.replace("LineSegment", "Line").replace("ArcOfCircle", "Arc")
    except Exception:
        kind = "Entity"
    p = {1: "Start", 2: "End", 3: "Center"}.get(pos, "")
    return "%s%d%s" % (kind, geo + 1, ("." + p) if p else "")


def rows(sk):
    """[(index, SOLIDWORKS name, entities text, driving, value)]"""
    out = []
    for i, c in enumerate(sk.Constraints):
        if c.Type == "InternalAlignment":
            continue
        ents = [_entity(sk, c.First, c.FirstPos)]
        if c.Second > -2000:
            ents.append(_entity(sk, c.Second, c.SecondPos))
        if c.Third > -2000:
            ents.append(_entity(sk, c.Third, c.ThirdPos))
        val = ""
        if c.Type in DIMENSIONS:
            import math
            val = "%.2f%s" % (math.degrees(c.Value) if c.Type == "Angle" else c.Value, " deg" if c.Type == "Angle" else "")
        name = (c.Name + ": ") if c.Name else ""
        out.append((i, name + SW_NAME.get(c.Type, c.Type), ", ".join(e for e in ents if e), c.Driving, val))
    return out


def status(sk):
    """'Fully Defined' / 'Under Defined (n DOF)' / 'Over Defined' ... like the SOLIDWORKS status bar."""
    try:
        sk.solve()
        if getattr(sk, "MalformedConstraints", None) or getattr(sk, "ConflictingConstraints", None):
            return "Over Defined"
        if getattr(sk, "RedundantConstraints", None):
            return "Over Defined (redundant)"
        dof = getattr(sk, "DoF", None)
        if dof is None:
            return ""
        return "Fully Defined" if dof == 0 else "Under Defined (%d degrees of freedom)" % dof
    except Exception:
        return ""


@harden
class RelationsPanel(QtWidgets.QDialog):
    _inst = None

    @classmethod
    def open(cls):
        sk = context.edited_sketch()
        if sk is None:
            QtWidgets.QMessageBox.information(Gui.getMainWindow(), "Display/Delete Relations", "Edit a sketch first.")
            return None
        if cls._inst is not None:
            cls._inst.close()
        cls._inst = cls(sk)
        cls._inst.show()
        return cls._inst

    def __init__(self, sk):
        super().__init__(Gui.getMainWindow(), Qt.Tool)
        self.sk = sk
        self.setWindowTitle("Display/Delete Relations - %s" % sk.Label)
        self.setWindowIcon(icon("delete_relations"))
        self.setStyleSheet(STYLE)
        self.resize(560, 420)
        lay = QtWidgets.QVBoxLayout(self)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Filter:"))
        self.filter = QtWidgets.QComboBox()
        self.filter.addItems(["All in this sketch", "Selected entities", "Relations only", "Dimensions only", "Not driving (reference)"])
        self.filter.currentIndexChanged.connect(lambda *_: self.populate())
        row.addWidget(self.filter, 1)
        lay.addLayout(row)
        self.state = QtWidgets.QLabel("")
        lay.addWidget(self.state)
        self.table = QtWidgets.QTreeWidget()
        self.table.setColumnCount(4)
        self.table.setHeaderLabels(["Relation", "Entities", "Value", "Driving"])
        self.table.setRootIsDecorated(False)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 200)
        lay.addWidget(self.table, 1)
        row = QtWidgets.QHBoxLayout()
        for text, fn in (("Delete", self.delete), ("Delete All", self.delete_all)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        row.addStretch(1)
        b = QtWidgets.QPushButton("Close")
        b.clicked.connect(self.close)
        row.addWidget(b)
        lay.addLayout(row)
        self.populate()

    def _selected_geo(self):
        out = set()
        for s in Gui.Selection.getSelectionEx():
            if s.Object != self.sk:
                continue
            for n in s.SubElementNames:
                if n.startswith("Edge"):
                    out.add(int(n[4:]) - 1)
        return out

    def populate(self):
        self.table.clear()
        f = self.filter.currentIndex()
        sel = self._selected_geo() if f == 1 else set()
        for i, name, ents, driving, val in rows(self.sk):
            c = self.sk.Constraints[i]
            if f == 1 and not ({c.First, c.Second, c.Third} & sel):
                continue
            if f == 2 and c.Type in DIMENSIONS:
                continue
            if f == 3 and c.Type not in DIMENSIONS:
                continue
            if f == 4 and driving:
                continue
            it = QtWidgets.QTreeWidgetItem([name, ents, val, "Yes" if driving else "No (driven)"])
            it.setData(0, Qt.UserRole, i)
            self.table.addTopLevelItem(it)
        self.state.setText("Sketch status: <b>%s</b>" % status(self.sk))

    def _delete(self, indices):
        if not indices:
            return
        doc = self.sk.Document
        doc.openTransaction("Delete Relations")
        try:
            self.sk.delConstraints(sorted(indices)) if hasattr(self.sk, "delConstraints") else \
                [self.sk.delConstraint(i) for i in sorted(indices, reverse=True)]
        finally:
            doc.commitTransaction()
        doc.recompute()
        self.populate()

    def delete(self):
        self._delete([it.data(0, Qt.UserRole) for it in self.table.selectedItems()])

    def delete_all(self, confirm=True):
        idx = [self.table.topLevelItem(i).data(0, Qt.UserRole) for i in range(self.table.topLevelItemCount())]
        if confirm and QtWidgets.QMessageBox.question(self, "Delete All", "Delete the %d relations listed?" % len(idx)) \
                != QtWidgets.QMessageBox.Yes:
            return
        self._delete(idx)

    def closeEvent(self, e):
        RelationsPanel._inst = None
        super().closeEvent(e)
