"""Tools > Options the SOLIDWORKS way: System Options and Document Properties.

Document Properties: Drafting Standard (ISO / ANSI), Units (MMGS / CGS / MKS / IPS + decimal places,
stored in the document's UnitSystem so it travels with the file) and Material. System Options
gather FreeWorks' own options and FreeCAD's full preferences.
"""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import harden, icon, params
from .style import STYLE

Qt = QtCore.Qt
UNIT_SCHEMA = {"MMGS": "Standard (mm", "CGS": "Building Euro (cm", "MKS": "MKS (m", "IPS": "Imperial decimal (in"}
UNITS_PARAM = "User parameter:BaseApp/Preferences/Units"
TD_GENERAL = "User parameter:BaseApp/Preferences/Mod/TechDraw/General"


def doc_units(doc):
    try:
        cur = doc.UnitSystem
        for k, prefix in UNIT_SCHEMA.items():
            if cur.startswith(prefix):
                return k
    except Exception:
        pass
    return params().GetString("MassUnits", "MMGS")


def set_units(doc, system, decimals):
    if doc is not None and hasattr(doc, "UnitSystem"):
        for name in doc.getEnumerationsOfProperty("UnitSystem"):
            if name.startswith(UNIT_SCHEMA[system]):
                doc.UnitSystem = name
                break
    App.ParamGet(UNITS_PARAM).SetInt("Decimals", int(decimals))
    p = params()
    p.SetString("MassUnits", system)
    p.SetInt("MassDecimals", int(decimals))


def set_standard(std):
    from . import drawing
    import os
    g = App.ParamGet(drawing.TD_FILES)
    g.SetString("TemplateFile", os.path.join(drawing.TEMPLATE_DIR, drawing.DEFAULT_ANSI if std == "ANSI" else drawing.DEFAULT_ISO))
    App.ParamGet(TD_GENERAL).SetInt("ProjectionAngle", 1 if std == "ANSI" else 0)
    params().SetString("DraftingStandard", std)


@harden
class OptionsDialog(QtWidgets.QDialog):
    _inst = None

    @classmethod
    def open(cls, page=None):
        if cls._inst is not None:
            cls._inst.close()
        cls._inst = cls()
        if page == "document":
            cls._inst.tabs.setCurrentIndex(1)
        cls._inst.show()
        return cls._inst

    def __init__(self):
        super().__init__(Gui.getMainWindow())
        self.setWindowTitle("Options")
        self.setWindowIcon(icon("options"))
        self.setStyleSheet(STYLE)
        self.resize(520, 420)
        self.doc = App.ActiveDocument
        lay = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        lay.addWidget(self.tabs)
        # ---- System Options
        sys_ = QtWidgets.QWidget()
        sl = QtWidgets.QVBoxLayout(sys_)
        sl.addWidget(QtWidgets.QLabel("<b>System Options</b> apply to every document."))
        for text, fn in (("FreeWorks options (gestures, shortcuts, CommandManager, display) ...", self.fw_options),
                         ("Reset FreeWorks settings ...", self.reset),
                         ("FreeCAD preferences (all settings, advanced) ...", self.fc_prefs)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(fn)
            sl.addWidget(b)
        sl.addStretch(1)
        self.tabs.addTab(sys_, "System Options")
        # ---- Document Properties
        dp = QtWidgets.QWidget()
        f = QtWidgets.QFormLayout(dp)
        f.addRow(QtWidgets.QLabel("<b>Document Properties</b> - %s" % (self.doc.Label if self.doc else "no document open")))
        self.std = QtWidgets.QComboBox()
        self.std.addItems(["ISO", "ANSI"])
        self.std.setCurrentText(params().GetString("DraftingStandard", "ISO"))
        f.addRow("Overall drafting standard:", self.std)
        self.units = QtWidgets.QComboBox()
        self.units.addItems(["MMGS (millimeter, gram, second)", "CGS (centimeter, gram, second)",
                             "MKS (meter, kilogram, second)", "IPS (inch, pound, second)"])
        cur = doc_units(self.doc) if self.doc else params().GetString("MassUnits", "MMGS")
        self.units.setCurrentIndex(["MMGS", "CGS", "MKS", "IPS"].index(cur))
        f.addRow("Unit system:", self.units)
        self.dec = QtWidgets.QSpinBox()
        self.dec.setRange(0, 8)
        self.dec.setValue(App.ParamGet(UNITS_PARAM).GetInt("Decimals", 2))
        f.addRow("Decimals:", self.dec)
        mat = QtWidgets.QPushButton("Edit Material ...")
        mat.clicked.connect(self.material)
        mat.setEnabled(self.doc is not None)
        f.addRow("Material:", mat)
        self.tabs.addTab(dp, "Document Properties")
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        ok = QtWidgets.QPushButton("OK")
        ok.clicked.connect(self.ok)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.close)
        row.addWidget(ok)
        row.addWidget(cancel)
        lay.addLayout(row)

    def ok(self):
        system = ["MMGS", "CGS", "MKS", "IPS"][self.units.currentIndex()]
        set_units(self.doc, system, self.dec.value())
        set_standard(self.std.currentText())
        if self.doc is not None:
            self.doc.recompute()
        self.close()

    def fw_options(self):
        from . import widgets
        widgets.OptionsDialog.open_dialog()

    def reset(self):
        Gui.runCommand("FW_ResetSettings")

    def fc_prefs(self):
        Gui.runCommand("Std_DlgPreferences")

    def material(self):
        from . import evaluate
        evaluate.MaterialDialog.open()

    def closeEvent(self, e):
        OptionsDialog._inst = None
        super().closeEvent(e)
