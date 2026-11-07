"""SOLIDWORKS-style Material dialog and Mass Properties dialog."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import harden, icon, params, safe_slow
from . import materials, massprops
from .style import STYLE

Qt = QtCore.Qt


def _mw():
    return Gui.getMainWindow()


def _fixed_font():
    return QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)


# ====================================================================== Material
@harden
class MaterialDialog(QtWidgets.QDialog):
    """Tree of materials on the left, properties on the right, Apply / Close - like SOLIDWORKS."""
    _inst = None

    @classmethod
    def open(cls):
        if cls._inst is None:
            cls._inst = cls()
        cls._inst.refresh_targets()
        cls._inst.show()
        cls._inst.raise_()
        cls._inst.activateWindow()
        return cls._inst

    def __init__(self):
        super().__init__(_mw(), Qt.Tool)
        self.setWindowTitle("Material")
        self.setWindowIcon(icon("appearance"))
        self.setStyleSheet(STYLE)
        self.resize(760, 480)
        self.targets = []
        lay = QtWidgets.QHBoxLayout(self)
        left = QtWidgets.QVBoxLayout()
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search materials")
        self.search.textChanged.connect(self.filter)
        left.addWidget(self.search)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.currentItemChanged.connect(self.show_item)
        self.tree.itemDoubleClicked.connect(lambda *a: self.apply())
        left.addWidget(self.tree, 1)
        lay.addLayout(left, 2)

        right = QtWidgets.QVBoxLayout()
        self.target_lbl = QtWidgets.QLabel()
        self.target_lbl.setWordWrap(True)
        right.addWidget(self.target_lbl)
        box = QtWidgets.QGroupBox("Properties")
        form = QtWidgets.QFormLayout(box)
        self.name = QtWidgets.QLineEdit()
        self.name.setReadOnly(True)
        self.cat = QtWidgets.QLabel()
        self.desc = QtWidgets.QLabel()
        self.desc.setWordWrap(True)
        self.density = QtWidgets.QDoubleSpinBox()
        self.density.setRange(0.0, 100000.0)
        self.density.setDecimals(2)
        self.density.setSuffix(" kg/m^3")
        self.density.setReadOnly(True)
        form.addRow("Name:", self.name)
        form.addRow("Category:", self.cat)
        form.addRow("Description:", self.desc)
        form.addRow("Mass density:", self.density)
        self.props = QtWidgets.QTableWidget(0, 2)
        self.props.setHorizontalHeaderLabels(["Property", "Value"])
        self.props.horizontalHeader().setStretchLastSection(True)
        self.props.verticalHeader().setVisible(False)
        self.props.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        form.addRow(self.props)
        right.addWidget(box, 1)
        btns = QtWidgets.QHBoxLayout()
        self.b_apply = QtWidgets.QPushButton("Apply")
        self.b_remove = QtWidgets.QPushButton("Remove Material")
        b_close = QtWidgets.QPushButton("Close")
        self.b_apply.clicked.connect(self.apply)
        self.b_remove.clicked.connect(self.remove)
        b_close.clicked.connect(self.close)
        btns.addWidget(self.b_remove)
        btns.addStretch(1)
        btns.addWidget(self.b_apply)
        btns.addWidget(b_close)
        right.addLayout(btns)
        lay.addLayout(right, 3)
        self.populate()

    def populate(self):
        self.tree.clear()
        top = QtWidgets.QTreeWidgetItem(["FreeWorks Materials"])
        top.setIcon(0, icon("freeworks"))
        self.tree.addTopLevelItem(top)
        cats = {}
        for c in materials.cards():
            parent = cats.get(c["category"])
            if parent is None:
                parent = cats[c["category"]] = QtWidgets.QTreeWidgetItem(top, [c["category"]])
            it = QtWidgets.QTreeWidgetItem(parent, [c["name"]])
            it.setData(0, Qt.UserRole, ("card", c))
        top.setExpanded(True)
        custom = QtWidgets.QTreeWidgetItem(["Custom Materials"])
        self.tree.addTopLevelItem(custom)
        it = QtWidgets.QTreeWidgetItem(custom, ["Custom density..."])
        it.setData(0, Qt.UserRole, ("custom", None))
        custom.setExpanded(True)
        fc = QtWidgets.QTreeWidgetItem(["FreeCAD Materials"])
        self.tree.addTopLevelItem(fc)
        folders = {}
        for folder, name, uid, rho in materials.freecad_materials():
            parent = folders.get(folder)
            if parent is None:
                parent = folders[folder] = QtWidgets.QTreeWidgetItem(fc, [folder])
            it = QtWidgets.QTreeWidgetItem(parent, [name])
            it.setData(0, Qt.UserRole, ("fc", {"name": name, "uuid": uid, "density": rho, "category": folder,
                                              "description": "", "props": {}}))

    def filter(self, text):
        t = text.strip().lower()

        def visit(item):
            data = item.data(0, Qt.UserRole)
            if data:
                show = not t or t in item.text(0).lower()
            else:
                show = False
                for i in range(item.childCount()):
                    show = visit(item.child(i)) or show
                show = show or not t
                if t and show:
                    item.setExpanded(True)
            item.setHidden(not show)
            return show

        for i in range(self.tree.topLevelItemCount()):
            visit(self.tree.topLevelItem(i))

    def refresh_targets(self):
        self.targets = materials.targets()
        if not self.targets:
            self.target_lbl.setText("<b>Select a part, body or component</b> to assign a material.")
            cur = None
        else:
            names = ", ".join(o.Label for o in self.targets[:6]) + (" ..." if len(self.targets) > 6 else "")
            cur = materials.material_of(self.targets[0])[0]
            self.target_lbl.setText("Applies to: <b>%s</b><br>Current material: %s" % (names, cur))
        self.b_apply.setEnabled(bool(self.targets))
        self.b_remove.setEnabled(bool(self.targets))
        if cur:
            self.select_name(cur)

    def select_name(self, name):
        found = self.tree.findItems(name, Qt.MatchExactly | Qt.MatchRecursive)
        if found:
            self.tree.setCurrentItem(found[0])

    def show_item(self, item, _prev=None):
        data = item.data(0, Qt.UserRole) if item else None
        self.props.setRowCount(0)
        if not data:
            return
        kind, c = data
        custom = kind == "custom"
        self.name.setReadOnly(not custom)
        self.density.setReadOnly(not custom)
        if custom:
            self.name.setText("Custom")
            self.cat.setText("Custom Materials")
            self.desc.setText("Enter the density given on the drawing (1 g/mm^3 = 1 000 000 kg/m^3).")
            if self.targets:
                self.density.setValue(materials.material_of(self.targets[0])[1])
            return
        self.name.setText(c["name"])
        self.cat.setText(c["category"])
        self.desc.setText(c.get("description", ""))
        self.density.setValue(c["density"])
        labels = {"YoungsModulus": "Elastic modulus", "PoissonRatio": "Poisson's ratio",
                  "YieldStrength": "Yield strength", "UltimateTensileStrength": "Tensile strength",
                  "Density": "Mass density"}
        rows = [(labels.get(k, k), v) for k, v in c.get("props", {}).items()]
        self.props.setRowCount(len(rows))
        for r, (k, v) in enumerate(rows):
            self.props.setItem(r, 0, QtWidgets.QTableWidgetItem(k))
            self.props.setItem(r, 1, QtWidgets.QTableWidgetItem(v))

    @safe_slow
    def apply(self):
        item = self.tree.currentItem()
        data = item.data(0, Qt.UserRole) if item else None
        if not data or not self.targets:
            return
        kind, c = data
        doc = self.targets[0].Document
        doc.openTransaction("Edit Material")
        try:
            if kind == "custom":
                materials.apply_custom(self.targets, self.name.text().strip() or "Custom", self.density.value())
            else:
                materials.apply(self.targets, c["uuid"])
        finally:
            doc.commitTransaction()
        self.refresh_targets()

    @safe_slow
    def remove(self):
        if not self.targets:
            return
        doc = self.targets[0].Document
        doc.openTransaction("Remove Material")
        try:
            materials.remove(self.targets)
        finally:
            doc.commitTransaction()
        self.refresh_targets()

    def closeEvent(self, e):
        MaterialDialog._inst = None
        super().closeEvent(e)


# ====================================================================== Mass Properties
@harden
class MassPropertiesDialog(QtWidgets.QDialog):
    _inst = None

    @classmethod
    def open(cls):
        if cls._inst is None:
            cls._inst = cls()
        cls._inst.recalc()
        cls._inst.show()
        cls._inst.raise_()
        cls._inst.activateWindow()
        return cls._inst

    def __init__(self):
        super().__init__(_mw(), Qt.Tool)
        self.setWindowTitle("Mass Properties")
        self.setWindowIcon(icon("mass_properties"))
        self.setStyleSheet(STYLE)
        self.resize(640, 680)
        units, dec, hidden = massprops.settings()
        lay = QtWidgets.QVBoxLayout(self)
        bar = QtWidgets.QHBoxLayout()
        for label, fn in (("Copy to Clipboard", self.copy), ("Recalculate", self.recalc)):
            b = QtWidgets.QPushButton(label)
            b.clicked.connect(fn)
            bar.addWidget(b)
        bar.addStretch(1)
        bar.addWidget(QtWidgets.QLabel("Units:"))
        self.units = QtWidgets.QComboBox()
        self.units.addItems(list(massprops.UNITS))
        self.units.setCurrentText(units)
        self.units.currentTextChanged.connect(self.options_changed)
        bar.addWidget(self.units)
        bar.addWidget(QtWidgets.QLabel("Decimal places:"))
        self.dec = QtWidgets.QSpinBox()
        self.dec.setRange(0, 8)
        self.dec.setValue(dec)
        self.dec.valueChanged.connect(self.options_changed)
        bar.addWidget(self.dec)
        lay.addLayout(bar)
        lay.addWidget(QtWidgets.QLabel("Selected items (nothing selected = whole part or assembly):"))
        self.items = QtWidgets.QListWidget()
        self.items.setMaximumHeight(70)
        lay.addWidget(self.items)
        self.hidden = QtWidgets.QCheckBox("Include hidden bodies/components")
        self.hidden.setChecked(hidden)
        self.hidden.toggled.connect(self.options_changed)
        lay.addWidget(self.hidden)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Report coordinate values relative to:"))
        self.cs = QtWidgets.QComboBox()
        self.cs.currentIndexChanged.connect(lambda *_: self.render())
        row.addWidget(self.cs, 1)
        lay.addLayout(row)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(_fixed_font())
        self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        lay.addWidget(self.text, 1)
        self.res = None
        self.title = ""

    def options_changed(self, *_):
        p = params()
        p.SetString("MassUnits", self.units.currentText())
        p.SetInt("MassDecimals", self.dec.value())
        p.SetBool("MassIncludeHidden", self.hidden.isChecked())
        self.recalc()

    @safe_slow
    def recalc(self):
        doc = App.ActiveDocument
        self.title = doc.Label if doc else ""
        cur = self.cs.currentText()
        self.cs.blockSignals(True)
        self.cs.clear()
        self.cs.addItem("-- default --", None)
        for label, plc in massprops.coordinate_systems():
            self.cs.addItem(label, plc)
        i = self.cs.findText(cur)
        self.cs.setCurrentIndex(i if i >= 0 else 0)
        self.cs.blockSignals(False)
        items = massprops.collect(hidden=self.hidden.isChecked())
        self.res = massprops.compute(items)
        self.items.clear()
        for lab, m, mat, rho in (self.res or {}).get("components", []):
            self.items.addItem(lab)
        self.render()

    def render(self):
        if self.res is None:
            self.text.setPlainText("No solid bodies found. Open a part or assembly, or select bodies/components.")
            return
        self.text.setPlainText(massprops.report(self.res, self.title, self.cs.currentText(), self.cs.currentData(),
                                                self.units.currentText(), self.dec.value()))

    def copy(self):
        QtWidgets.QApplication.clipboard().setText(self.text.toPlainText())

    def closeEvent(self, e):
        MassPropertiesDialog._inst = None
        super().closeEvent(e)
