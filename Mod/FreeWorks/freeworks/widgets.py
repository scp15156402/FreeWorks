"""Pop-up widgets: view selector, shortcut bar, mouse-gesture wheel, magnifier,
report / interference / new-document / options dialogs."""
import math
import os
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import catalog, context, icon, params, safe

Qt = QtCore.Qt


def mw():
    return Gui.getMainWindow()


def _cmd_active(key):
    e = catalog.C.get(key)
    if not e:
        return False
    c = catalog.first_existing(e)
    if c is None:
        return False
    if c.startswith("FW_"):
        return True
    try:
        return bool(Gui.Command.get(c).isActive())
    except Exception:
        return True


def _run(key):
    from . import commands
    QtCore.QTimer.singleShot(0, lambda: commands.run_key(key))


def popup_commands(keys, title=None, only_active=False, pos=None):
    m = QtWidgets.QMenu(mw())
    m.setObjectName("FreeWorksPopup")
    if title:
        t = m.addAction(title)
        t.setEnabled(False)
        m.addSeparator()
    for k in keys:
        e = catalog.C.get(k)
        if not e or catalog.first_existing(e) is None:
            continue
        a = m.addAction(icon(e["icon"] or catalog.first_existing(e)), e["label"])
        a.setToolTip(e["tip"])
        a.setEnabled(_cmd_active(k) if only_active else True)
        a.triggered.connect(lambda _=False, k=k: _run(k))
    m.exec_(pos or QtGui.QCursor.pos())


# --------------------------------------------------------------- base popup
class _Popup(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent or mw(), Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("FreeWorksPopupFrame")
        self.setAttribute(Qt.WA_DeleteOnClose)

    def show_at(self, pos):
        self.adjustSize()
        g = QtGui.QGuiApplication.screenAt(pos) or QtGui.QGuiApplication.primaryScreen()
        r = g.availableGeometry()
        x = min(max(pos.x() - self.width() // 2, r.left()), r.right() - self.width())
        y = min(max(pos.y() - self.height() // 2, r.top()), r.bottom() - self.height())
        self.move(x, y)
        self.show()


def _tool_button(key, size=24, text=True, parent=None, on_click=None):
    e = catalog.C[key]
    b = QtWidgets.QToolButton(parent)
    b.setIcon(icon(e["icon"] or catalog.first_existing(e) or ""))
    b.setIconSize(QtCore.QSize(size, size))
    b.setToolTip("<b>%s</b><br>%s" % (e["label"], e["tip"]))
    if text:
        b.setText(e["label"])
        b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    b.setAutoRaise(True)
    b.setEnabled(_cmd_active(key))

    def go():
        if on_click:
            on_click()
        _run(key)
    b.clicked.connect(go)
    return b


# ------------------------------------------------------------ view selector
class ViewSelector(_Popup):
    """Spacebar 'Orientation' dialog."""

    @classmethod
    def popup(cls):
        w = cls()
        w.show_at(QtGui.QCursor.pos())

    def __init__(self):
        super().__init__()
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 8)
        lay.setSpacing(4)
        h = QtWidgets.QLabel("Orientation")
        h.setObjectName("FreeWorksPopupTitle")
        lay.addWidget(h)
        top = QtWidgets.QHBoxLayout()
        for k in ("normal_to", "prev_view", "zoom_fit"):
            top.addWidget(_tool_button(k, 22, False, self, self.close))
        top.addStretch(1)
        lay.addLayout(top)
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(2)
        cells = [("v_top", 0, 1), ("v_left", 1, 0), ("v_front", 1, 1), ("v_right", 1, 2), ("v_back", 1, 3),
                 ("v_bottom", 2, 1), ("v_iso", 0, 3), ("v_dimetric", 2, 3), ("v_trimetric", 2, 2)]
        for k, r, c in cells:
            b = QtWidgets.QPushButton(catalog.C[k]["label"])
            b.setObjectName("FreeWorksViewCell")
            b.setMinimumSize(76, 30)
            b.clicked.connect(lambda _=False, k=k: (self.close(), _run(k)))
            grid.addWidget(b, r, c)
        lay.addLayout(grid)


# ---------------------------------------------------------- shortcut bar (S)
class ShortcutBar(_Popup):
    @classmethod
    def show_for(cls, ctx):
        keys = catalog.SHORTCUT_BAR.get(ctx if ctx in catalog.SHORTCUT_BAR else "part")
        w = cls(keys)
        w.show_at(QtGui.QCursor.pos())

    def __init__(self, keys):
        super().__init__()
        lay = QtWidgets.QGridLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(1)
        keys = [k for k in keys if k in catalog.C and catalog.first_existing(catalog.C[k])]
        cols = max(4, int(math.ceil(math.sqrt(len(keys) * 2))))
        for i, k in enumerate(keys):
            lay.addWidget(_tool_button(k, 24, False, self, self.close), i // cols, i % cols)


# --------------------------------------------------------- gesture wheel
class GestureWheel(QtWidgets.QWidget):
    R_IN, R_OUT = 26, 92

    def __init__(self, keys, center):
        # a child of the main window (not a top-level window) so it is
        # transparent on every system, with or without desktop compositing
        super().__init__(mw())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.keys = keys
        self.sel = -1
        s = 2 * (self.R_OUT + 52)
        self.resize(int(s * 1.6), s)
        self.center = center
        lp = mw().mapFromGlobal(center)
        self.move(lp.x() - self.width() // 2, lp.y() - s // 2)
        self.raise_()
        self.icons = [icon(catalog.C[k]["icon"] or catalog.first_existing(catalog.C[k]) or "") if k else None for k in keys]

    def update_pos(self, gpos):
        d = gpos - self.center
        dist = math.hypot(d.x(), d.y())
        if dist < self.R_IN:
            sel = -1
        else:
            ang = (math.degrees(math.atan2(d.x(), -d.y())) + 360 + 22.5) % 360   # 0 = north, clockwise
            sel = int(ang // 45)
        if sel != self.sel:
            self.sel = sel
            self.update()
        return dist

    def selected_key(self):
        return self.keys[self.sel] if 0 <= self.sel < len(self.keys) else None

    def paintEvent(self, ev):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        c = QtCore.QPointF(self.width() / 2, self.height() / 2)
        p.setPen(QtGui.QPen(QtGui.QColor(80, 90, 105, 160), 1))
        p.setBrush(QtGui.QColor(255, 255, 255, 70))
        p.drawEllipse(c, self.R_IN - 6, self.R_IN - 6)
        f = p.font()
        f.setPointSizeF(8.0)
        p.setFont(f)
        fm = QtGui.QFontMetrics(f)
        for i, k in enumerate(self.keys):
            if not k:
                continue
            a = math.radians(i * 45)
            r = self.R_OUT * 0.86
            pt = QtCore.QPointF(c.x() + math.sin(a) * r * 1.55, c.y() - math.cos(a) * r)
            on = i == self.sel
            label = catalog.C[k]["label"]
            tw = fm.horizontalAdvance(label) + 30
            box = QtCore.QRectF(pt.x() - tw / 2, pt.y() - 12, tw, 24)
            p.setPen(QtGui.QPen(QtGui.QColor("#2E7CE6") if on else QtGui.QColor(120, 128, 140, 200), 1.2))
            p.setBrush(QtGui.QColor("#DCEBFF") if on else QtGui.QColor(250, 251, 253, 235))
            p.drawRoundedRect(box, 4, 4)
            ic = self.icons[i]
            if ic:
                ic.paint(p, QtCore.QRect(int(box.left()) + 4, int(box.top()) + 4, 16, 16))
            p.setPen(QtGui.QColor("#1B1F24"))
            p.drawText(QtCore.QRectF(box.left() + 24, box.top(), tw - 26, 24), Qt.AlignVCenter | Qt.AlignLeft, label)
        p.end()


# --------------------------------------------------------- magnifier (G)
class Magnifier(QtWidgets.QWidget):
    _inst = None
    SIZE, ZOOM = 240, 2.5

    @classmethod
    def start(cls):
        if cls._inst is not None:
            cls._inst.stop()
            return
        cls._inst = cls()
        cls._inst.show()

    def __init__(self):
        super().__init__(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.SIZE, self.SIZE)
        self.pix = None
        self.t = QtCore.QTimer(self)
        self.t.timeout.connect(self.grab_area)
        self.t.start(33)
        QtWidgets.QApplication.instance().installEventFilter(self)

    def stop(self):
        QtWidgets.QApplication.instance().removeEventFilter(self)
        self.t.stop()
        self.close()
        Magnifier._inst = None

    def eventFilter(self, obj, ev):
        if ev.type() == QtCore.QEvent.KeyPress and ev.key() in (Qt.Key_Escape, Qt.Key_G):
            self.stop()
            return True
        if ev.type() == QtCore.QEvent.Wheel and ev.modifiers() & Qt.ControlModifier:
            self.ZOOM = max(1.5, min(6.0, self.ZOOM * (1.15 if ev.angleDelta().y() > 0 else 1 / 1.15)))
            return True
        return False

    def grab_area(self):
        pos = QtGui.QCursor.pos()
        scr = QtGui.QGuiApplication.screenAt(pos)
        if scr is None:
            return
        src = int(self.SIZE / self.ZOOM)
        geo = scr.geometry()
        self.pix = scr.grabWindow(0, pos.x() - geo.x() - src // 2, pos.y() - geo.y() - src // 2, src, src)
        self.move(pos.x() + 24, pos.y() + 24)
        self.update()

    def paintEvent(self, ev):
        if self.pix is None:
            return
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        path = QtGui.QPainterPath()
        path.addEllipse(QtCore.QRectF(2, 2, self.SIZE - 4, self.SIZE - 4))
        p.setClipPath(path)
        p.drawPixmap(self.rect(), self.pix)
        p.setClipping(False)
        p.setPen(QtGui.QPen(QtGui.QColor("#3A3F47"), 3))
        p.drawEllipse(QtCore.QRectF(2, 2, self.SIZE - 4, self.SIZE - 4))
        p.setPen(QtGui.QPen(QtGui.QColor(200, 30, 30, 160), 1))
        c = self.SIZE / 2
        p.drawLine(QtCore.QPointF(c - 8, c), QtCore.QPointF(c + 8, c))
        p.drawLine(QtCore.QPointF(c, c - 8), QtCore.QPointF(c, c + 8))
        p.end()


# ------------------------------------------------------------ report dialog
class ReportDialog(QtWidgets.QDialog):
    _open = {}

    @classmethod
    def show_text(cls, title, text, icon_key):
        d = cls._open.get(title)
        if d is None:
            d = cls(title, icon_key)
            cls._open[title] = d
        d.text.setPlainText(text)
        d.show()
        d.raise_()
        d.activateWindow()

    def __init__(self, title, icon_key):
        super().__init__(mw(), Qt.Tool)
        self.setWindowTitle(title)
        self.setWindowIcon(icon(icon_key))
        self.resize(560, 560)
        lay = QtWidgets.QVBoxLayout(self)
        bar = QtWidgets.QHBoxLayout()
        for label, fn in (("Recalculate", self.recalc), ("Copy to Clipboard", self.copy)):
            b = QtWidgets.QPushButton(label)
            b.clicked.connect(fn)
            bar.addWidget(b)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        f = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.text.setFont(f)
        lay.addWidget(self.text)
        self.title = title

    def recalc(self):
        from . import commands
        {"Mass Properties": commands.mass_properties, "Section Properties": commands.section_properties,
         "Bounding Box": commands.bounding_box}.get(self.title, lambda: None)()

    def copy(self):
        QtWidgets.QApplication.clipboard().setText(self.text.toPlainText())

    def closeEvent(self, e):
        ReportDialog._open.pop(self.title, None)
        super().closeEvent(e)


class InterferenceDialog(QtWidgets.QDialog):
    _inst = None

    @classmethod
    def show_results(cls, items, found):
        if cls._inst:
            cls._inst.close()
        cls._inst = cls(items, found)
        cls._inst.show()

    def __init__(self, items, found):
        super().__init__(mw(), Qt.Tool)
        self.setWindowTitle("Interference Detection")
        self.resize(460, 380)
        self.found = found
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(QtWidgets.QLabel("Checked %d components / bodies" % len(items)))
        self.lst = QtWidgets.QListWidget()
        if not found:
            self.lst.addItem("No Interferences")
        for a, b, v, _ in found:
            self.lst.addItem("Interference: %s  ↔  %s   (%.3f mm³)" % (a.Label, b.Label, v))
        self.lst.currentRowChanged.connect(self.highlight)
        lay.addWidget(self.lst)
        self.cb_show = QtWidgets.QCheckBox("Make interfering components transparent")
        self.cb_show.setChecked(True)
        lay.addWidget(self.cb_show)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        bb.rejected.connect(self.close)
        lay.addWidget(bb)
        self.tmp = None
        self.saved = {}

    def highlight(self, row):
        self.clear_tmp()
        if not (0 <= row < len(self.found)):
            return
        a, b, v, com = self.found[row]
        doc = App.ActiveDocument
        self.tmp = doc.addObject("Part::Feature", "FW_Interference")
        self.tmp.Shape = com
        if self.tmp.ViewObject:
            self.tmp.ViewObject.ShapeAppearance = [App.Material(DiffuseColor=(1.0, 0.1, 0.1))]
            self.tmp.ViewObject.LineColor = (0.6, 0.0, 0.0)
        if self.cb_show.isChecked():
            for o in (a, b):
                if o.ViewObject and hasattr(o.ViewObject, "Transparency"):
                    self.saved[o.Name] = o.ViewObject.Transparency
                    o.ViewObject.Transparency = 75
        doc.recompute()

    def clear_tmp(self):
        doc = App.ActiveDocument
        if self.tmp is not None and doc is not None:
            try:
                doc.removeObject(self.tmp.Name)
            except Exception:
                pass
        self.tmp = None
        if doc is not None:
            for n, t in self.saved.items():
                o = doc.getObject(n)
                if o and o.ViewObject:
                    o.ViewObject.Transparency = t
        self.saved = {}

    def closeEvent(self, e):
        self.clear_tmp()
        InterferenceDialog._inst = None
        super().closeEvent(e)


# ------------------------------------------------------- new document dialog
class NewDocumentDialog(QtWidgets.QDialog):
    """SolidWorks-style 'New Document' / Welcome dialog."""

    @classmethod
    def ask(cls, welcome=False):
        d = cls(welcome)
        d.exec_()

    def __init__(self, welcome=False):
        super().__init__(mw())
        self.setWindowTitle("Welcome - FreeWorks" if welcome else "New FreeWorks Document")
        self.setObjectName("FreeWorksNewDialog")
        self.setMinimumWidth(620)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(12)
        row = QtWidgets.QHBoxLayout()
        for kind, title, desc, ic in (
                ("part", "Part", "a 3D representation of a single design component", "new_part"),
                ("assembly", "Assembly", "a 3D arrangement of parts and/or other assemblies", "new_assembly"),
                ("drawing", "Drawing", "a 2D engineering drawing, typically of a part or assembly", "new_drawing")):
            b = QtWidgets.QToolButton()
            b.setObjectName("FreeWorksNewButton")
            b.setIcon(icon(ic))
            b.setIconSize(QtCore.QSize(64, 64))
            b.setText(title)
            b.setToolTip(desc)
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            b.setMinimumSize(180, 130)
            b.clicked.connect(lambda _=False, k=kind: self.make(k))
            row.addWidget(b)
        lay.addLayout(row)
        self.desc = QtWidgets.QLabel("Choose a document type.")
        lay.addWidget(self.desc)
        rec = self.recent()
        if rec:
            lay.addWidget(QtWidgets.QLabel("<b>Recent Documents</b>"))
            self.lst = QtWidgets.QListWidget()
            self.lst.setMaximumHeight(160)
            for f in rec:
                it = QtWidgets.QListWidgetItem(icon("new_document"), os.path.basename(f))
                it.setToolTip(f)
                it.setData(Qt.UserRole, f)
                self.lst.addItem(it)
            self.lst.itemActivated.connect(lambda it: self.open_file(it.data(Qt.UserRole)))
            self.lst.itemDoubleClicked.connect(lambda it: self.open_file(it.data(Qt.UserRole)))
            lay.addWidget(self.lst)
        bb = QtWidgets.QHBoxLayout()
        op = QtWidgets.QPushButton("Open...")
        op.clicked.connect(self.open_dialog)
        bb.addWidget(op)
        bb.addStretch(1)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        bb.addWidget(cancel)
        lay.addLayout(bb)

    @staticmethod
    def recent():
        p = App.ParamGet("User parameter:BaseApp/Preferences/RecentFiles")
        out = []
        for i in range(p.GetInt("RecentFiles", 8)):
            f = p.GetString("MRU%d" % i, "")
            if f and os.path.exists(f):
                out.append(f)
        return out[:8]

    def make(self, kind):
        self.accept()
        from . import naming
        QtCore.QTimer.singleShot(0, lambda: naming.new_document(kind))

    def open_file(self, f):
        self.accept()
        QtCore.QTimer.singleShot(0, lambda: Gui.open(f) if f.lower().endswith(".fcstd") else Gui.insert(f))

    def open_dialog(self):
        self.accept()
        QtCore.QTimer.singleShot(0, lambda: Gui.runCommand("Std_Open"))


# ---------------------------------------------------------- options dialog
class OptionsDialog(QtWidgets.QDialog):
    BOOLS = [
        ("Gestures", "Mouse gestures (right-drag in the graphics area)", True),
        ("Shortcuts", "SolidWorks keyboard shortcuts", True),
        ("HeadsUpToolbar", "Heads-up View toolbar in the graphics area", True),
        ("CommandManager", "CommandManager (tabbed command area)", True),
        ("AutoRenameFeatures", "Name new features like SolidWorks (Boss-Extrude1, Sketch1 ...)", True),
        ("FitOnStandardView", "Zoom to fit when changing to a standard view", False),
        ("ShowWelcome", "Show the Welcome dialog at startup", True),
        ("CommandManagerText", "Show command text in the CommandManager", True),
        ("CheckForUpdates", "Check GitHub for FreeWorks updates (once a day)", True),
    ]

    @classmethod
    def open_dialog(cls):
        cls().exec_()

    def __init__(self):
        super().__init__(mw())
        self.setWindowTitle("FreeWorks Options")
        lay = QtWidgets.QVBoxLayout(self)
        self.boxes = {}
        p = params()
        for k, text, d in self.BOOLS:
            cb = QtWidgets.QCheckBox(text)
            cb.setChecked(p.GetBool(k, d))
            self.boxes[k] = cb
            lay.addWidget(cb)
        form = QtWidgets.QFormLayout()
        self.zoom = QtWidgets.QComboBox()
        self.zoom.addItems(["SolidWorks (roll wheel toward you to zoom in)", "Reversed (roll wheel away to zoom in)"])
        vp = App.ParamGet("User parameter:BaseApp/Preferences/View")
        self.zoom.setCurrentIndex(1 if vp.GetBool("InvertZoom", False) else 0)
        form.addRow("Mouse wheel zoom:", self.zoom)
        self.icon_size = QtWidgets.QComboBox()
        self.icon_size.addItems(["Small (24 px)", "Large (32 px)"])
        self.icon_size.setCurrentIndex(0 if p.GetInt("LargeIconSize", 32) <= 24 else 1)
        form.addRow("CommandManager icons:", self.icon_size)
        lay.addLayout(form)
        btn = QtWidgets.QPushButton("Re-apply FreeWorks look && settings (colors, lighting, performance)")
        btn.clicked.connect(self.reapply)
        lay.addWidget(btn)
        note = QtWidgets.QLabel("FreeCAD's own settings remain under Tools > Options (System Options).")
        note.setStyleSheet("color:#666")
        lay.addWidget(note)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        bb.accepted.connect(self.save)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def reapply(self):
        from . import prefs
        prefs.apply(force=True)
        QtWidgets.QMessageBox.information(self, "FreeWorks", "FreeWorks settings re-applied. Some changes take effect after restart.")

    def save(self):
        p = params()
        for k, cb in self.boxes.items():
            p.SetBool(k, cb.isChecked())
        App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("InvertZoom", self.zoom.currentIndex() == 1)
        p.SetInt("LargeIconSize", 24 if self.icon_size.currentIndex() == 0 else 32)
        from . import shell
        shell.refresh_options()
        self.accept()
