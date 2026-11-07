"""ConfigurationManager window: configurations list + design table grid (SOLIDWORKS-style)."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import harden, icon, log, safe_slow, prefs
from . import configurations as cf
from .style import STYLE

Qt = QtCore.Qt


@harden
class ConfigurationManager(QtWidgets.QDialog):
    _inst = None

    @classmethod
    def open(cls):
        if App.ActiveDocument is None:
            return None
        if cls._inst is not None and cls._inst.doc is not App.ActiveDocument:
            cls._inst.close()
        if cls._inst is None:
            cls._inst = cls(App.ActiveDocument)
        cls._inst.refresh()
        cls._inst.show()
        cls._inst.raise_()
        return cls._inst

    def __init__(self, doc):
        super().__init__(Gui.getMainWindow(), Qt.Tool)
        self.doc = doc
        self.setWindowTitle("ConfigurationManager - %s" % doc.Label)
        self.setWindowIcon(icon("configurations"))
        self.setStyleSheet(STYLE)
        self.resize(820, 440)
        lay = QtWidgets.QHBoxLayout(self)
        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel("<b>%s Configuration(s)</b>" % doc.Label))
        self.list = QtWidgets.QListWidget()
        self.list.itemDoubleClicked.connect(lambda it: self.activate(it.text().replace(" (active)", "")))
        left.addWidget(self.list, 1)
        for text, fn in (("Show Configuration", self.activate_selected), ("Add Configuration...", self.add),
                         ("Rename...", self.rename), ("Delete", self.delete)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(fn)
            left.addWidget(b)
        lay.addLayout(left, 1)
        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel("<b>Design Table</b> - rows are configurations, columns are configured values "
                                         "(D1@Sketch1, $STATE@Fillet1, global variables). Everything else is shared."))
        self.grid = QtWidgets.QTableWidget()
        self.grid.itemChanged.connect(self.cell_changed)
        right.addWidget(self.grid, 1)
        row = QtWidgets.QHBoxLayout()
        self.pick = QtWidgets.QComboBox()
        self.pick.setEditable(True)
        self.pick.setMinimumWidth(200)
        row.addWidget(self.pick, 1)
        for text, fn in (("Add Column", self.add_column), ("Remove Column", self.remove_column)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        right.addLayout(row)
        row = QtWidgets.QHBoxLayout()
        for text, fn in (("Import Design Table...", self.import_table), ("Export Design Table...", self.export_table)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        row.addStretch(1)
        right.addLayout(row)
        self.msg = QtWidgets.QLabel("")
        self.msg.setWordWrap(True)
        right.addWidget(self.msg)
        lay.addLayout(right, 3)
        self._busy = False

    def refresh(self):
        self._busy = True
        order, cols, rows = cf.table(self.doc)
        a = cf.active(self.doc)
        self.list.clear()
        for n in order:
            it = QtWidgets.QListWidgetItem(icon("configurations"), n + (" (active)" if n == a else ""))
            if n == a:
                f = it.font()
                f.setBold(True)
                it.setFont(f)
            self.list.addItem(it)
        self.grid.clear()
        self.grid.setRowCount(len(order))
        self.grid.setColumnCount(len(cols))
        self.grid.setVerticalHeaderLabels(order)
        self.grid.setHorizontalHeaderLabels(cols)
        for r, n in enumerate(order):
            for c, k in enumerate(cols):
                self.grid.setItem(r, c, QtWidgets.QTableWidgetItem(rows.get(n, {}).get(k, "")))
        self.grid.resizeColumnsToContents()
        self.pick.clear()
        self.pick.addItems([k for k in cf.candidate_columns(self.doc) if k not in cols])
        self._busy = False

    def _selected(self):
        it = self.list.currentItem()
        return it.text().replace(" (active)", "") if it else None

    @safe_slow
    def activate(self, name):
        if not name:
            return
        self.doc.openTransaction("Show Configuration")
        try:
            errs = cf.activate(self.doc, name)
        finally:
            self.doc.commitTransaction()
        self.msg.setText("; ".join(errs))
        self.refresh()

    def activate_selected(self):
        self.activate(self._selected())

    def add(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Configuration", "Configuration name:")
        if ok and name.strip():
            try:
                cf.add(self.doc, name.strip(), self._selected())
            except Exception as e:
                self.msg.setText(str(e))
            self.refresh()

    def rename(self):
        old = self._selected()
        if not old:
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "Rename Configuration", "New name:", text=old)
        if ok and name.strip() and name.strip() != old:
            try:
                cf.rename(self.doc, old, name.strip())
            except Exception as e:
                self.msg.setText(str(e))
            self.refresh()

    def delete(self):
        n = self._selected()
        if n:
            try:
                cf.delete(self.doc, n)
            except Exception as e:
                self.msg.setText(str(e))
            self.refresh()

    @safe_slow
    def cell_changed(self, item):
        if self._busy:
            return
        order, cols, _ = cf.table(self.doc)
        try:
            cf.set_cell(self.doc, order[item.row()], cols[item.column()], item.text())
            self.msg.setText("")
        except Exception as e:
            self.msg.setText(str(e))

    def add_column(self):
        k = self.pick.currentText().strip()
        try:
            cf.add_column(self.doc, k)
            self.msg.setText("")
        except Exception as e:
            self.msg.setText(str(e))
        self.refresh()

    def remove_column(self):
        c = self.grid.currentColumn()
        cols = cf.columns(self.doc)
        if 0 <= c < len(cols):
            cf.remove_column(self.doc, cols[c])
            self.refresh()

    @safe_slow
    def import_table(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Design Table", prefs.projects_dir(),
                                                        "Design tables (*.csv *.xlsx *.txt)")
        if not path:
            return
        try:
            self.doc.openTransaction("Design Table")
            first = cf.import_table(self.doc, path)
            self.doc.commitTransaction()
            self.msg.setText("Design table imported. Double-click a configuration to show it." if first else "")
        except Exception as e:
            self.doc.abortTransaction()
            self.msg.setText("Import failed: %s" % e)
        self.refresh()

    def export_table(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Design Table", prefs.projects_dir(), "CSV (*.csv)")
        if path:
            cf.export_table(self.doc, path if path.lower().endswith(".csv") else path + ".csv")

    def closeEvent(self, e):
        ConfigurationManager._inst = None
        super().closeEvent(e)
