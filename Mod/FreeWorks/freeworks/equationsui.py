"""The SOLIDWORKS Equations, Global Variables, and Dimensions dialog (Tools > Equations)."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import harden, icon, log, safe_slow
from . import equations as eq
from .style import STYLE

Qt = QtCore.Qt
ADD_VAR = "Add global variable"
ADD_EQ = "Add equation"


@harden
class EquationsDialog(QtWidgets.QDialog):
    _inst = None

    @classmethod
    def open(cls):
        if App.ActiveDocument is None:
            return None
        if cls._inst is not None:
            cls._inst.close()
        cls._inst = cls(App.ActiveDocument)
        cls._inst.show()
        return cls._inst

    def __init__(self, doc):
        super().__init__(Gui.getMainWindow(), Qt.Tool)
        self.doc = doc
        self.setWindowTitle("Equations, Global Variables, and Dimensions")
        self.setWindowIcon(icon("equations") if icon("equations") and not icon("equations").isNull() else icon("freeworks"))
        self.setStyleSheet(STYLE)
        self.resize(780, 460)
        lay = QtWidgets.QVBoxLayout(self)
        tip = QtWidgets.QLabel('SOLIDWORKS syntax: global variables in quotes ("A"), dimensions as "D1@Sketch1" or '
                               '"D1@Boss-Extrude1". Functions: sin, cos, sqrt, abs, ... ')
        tip.setWordWrap(True)
        lay.addWidget(tip)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Name", "Value / Equation", "Evaluates to", "Comments"])
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.EditKeyPressed
                                  | QtWidgets.QAbstractItemView.SelectedClicked)
        self.tree.header().setStretchLastSection(True)
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 260)
        self.tree.setColumnWidth(2, 110)
        self.tree.itemChanged.connect(self.on_changed)
        lay.addWidget(self.tree, 1)
        self.msg = QtWidgets.QLabel("")
        self.msg.setWordWrap(True)
        lay.addWidget(self.msg)
        row = QtWidgets.QHBoxLayout()
        b_del = QtWidgets.QPushButton("Delete")
        b_del.clicked.connect(self.delete_selected)
        row.addWidget(b_del)
        b_rb = QtWidgets.QPushButton("Rebuild")
        b_rb.clicked.connect(self.rebuild)
        row.addWidget(b_rb)
        row.addStretch(1)
        ok = QtWidgets.QPushButton("OK")
        ok.clicked.connect(self.ok)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.cancel)
        row.addWidget(ok)
        row.addWidget(cancel)
        lay.addLayout(row)
        self.doc.openTransaction("Equations")
        self._busy = False
        self.populate()

    # -------------------------------------------------------------- content
    def populate(self):
        self._busy = True
        self.tree.clear()
        self.g_vars = QtWidgets.QTreeWidgetItem(self.tree, ["Global Variables"])
        for name, val, ex in eq.variables(self.doc):
            it = QtWidgets.QTreeWidgetItem(self.g_vars, [name, "= " + eq.to_solidworks(ex) if ex else "%g" % val, "%g" % val, ""])
            it.setData(0, Qt.UserRole, ("var", name))
            it.setFlags(it.flags() | Qt.ItemIsEditable)
        add = QtWidgets.QTreeWidgetItem(self.g_vars, [ADD_VAR, "", "", ""])
        add.setData(0, Qt.UserRole, ("addvar", None))
        add.setFlags(add.flags() | Qt.ItemIsEditable)
        add.setForeground(0, self.palette().placeholderText())
        self.g_eq = QtWidgets.QTreeWidgetItem(self.tree, ["Equations"])
        for name, o, path, ex, val in eq.equations(self.doc):
            it = QtWidgets.QTreeWidgetItem(self.g_eq, ['"%s"' % name, "= " + eq.to_solidworks(ex), "" if val is None else "%g" % val, ""])
            it.setData(0, Qt.UserRole, ("eq", '"%s"' % name))
            it.setFlags(it.flags() | Qt.ItemIsEditable)
        add = QtWidgets.QTreeWidgetItem(self.g_eq, [ADD_EQ, "", "", ""])
        add.setData(0, Qt.UserRole, ("addeq", None))
        add.setFlags(add.flags() | Qt.ItemIsEditable)
        add.setForeground(0, self.palette().placeholderText())
        self.tree.expandAll()
        self._busy = False

    @safe_slow
    def on_changed(self, item, col):
        if self._busy:
            return
        kind, key = item.data(0, Qt.UserRole) or (None, None)
        name, value = item.text(0).strip(), item.text(1).strip()
        try:
            if kind in ("var", "addvar"):
                if kind == "addvar" and (name == ADD_VAR or not value):
                    return
                if kind == "var" and col == 0 and name != key:
                    old = [v for v in eq.variables(self.doc) if v[0] == key]
                    eq.set_variable(self.doc, name, value or (old and "%g" % old[0][1]) or "0")
                    eq.delete_variable(self.doc, key)
                else:
                    eq.set_variable(self.doc, name, value)
            elif kind in ("eq", "addeq"):
                if kind == "addeq" and (name == ADD_EQ or not value):
                    return
                if kind == "eq" and col == 0 and name != key:
                    eq.set_equation(self.doc, key, None)
                eq.set_equation(self.doc, name, value)
            self.doc.recompute()
            self.msg.setText("")
        except Exception as e:
            self.msg.setText("<span style='color:#B00020'>%s</span>" % e)
            log("equations: %s" % e)
            return
        QtCore.QTimer.singleShot(0, self.populate)

    def delete_selected(self):
        it = self.tree.currentItem()
        if it is None:
            return
        kind, key = it.data(0, Qt.UserRole) or (None, None)
        if kind == "var":
            eq.delete_variable(self.doc, key)
        elif kind == "eq":
            eq.set_equation(self.doc, key, None)
        else:
            return
        self.doc.recompute()
        self.populate()

    def rebuild(self):
        self.doc.recompute()
        self.populate()

    def ok(self):
        self.doc.recompute()
        self.doc.commitTransaction()
        self._done = True
        self.close()

    def cancel(self):
        self.doc.abortTransaction()
        self.doc.recompute()
        self._done = True
        self.close()

    def closeEvent(self, e):
        if not getattr(self, "_done", False):
            self.doc.commitTransaction()
            self._done = True
        EquationsDialog._inst = None
        super().closeEvent(e)
