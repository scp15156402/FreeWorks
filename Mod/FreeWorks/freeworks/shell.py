"""The FreeWorks window shell: title/quick-access bar with menus and command
search, the CommandManager, the heads-up View toolbar, the FeatureManager /
PropertyManager panel, the selection-filter bar and the status bar."""
import os
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import catalog, context, icon, log, params, safe, warn
from . import commands

Qt = QtCore.Qt
_S = {}            # singletons: dock, topbar, cm, headsup, filters, status, controller


def mw():
    return Gui.getMainWindow()


# =========================================================== environments
ENV_WORKBENCHES = {
    "part": ["PartDesignWorkbench", "SketcherWorkbench", "PartWorkbench", "SurfaceWorkbench"],
    "assembly": ["AssemblyWorkbench"],
    "drawing": ["TechDrawWorkbench"],
    "addons": ["SMWorkbench", "FastenersWorkbench", "CurvesWorkbench"],
}
_loaded = set()


def load_environment(kind):
    """Make sure the FreeCAD workbenches behind an environment are loaded so
    their commands exist, then return to FreeWorks."""
    wbs = [w for w in ENV_WORKBENCHES.get(kind, []) if w in Gui.listWorkbenches() and w not in _loaded]
    if not wbs:
        return
    cur = Gui.activeWorkbench().name() if Gui.activeWorkbench() else None
    win = mw()
    win.setUpdatesEnabled(False)
    try:
        for w in wbs:
            try:
                Gui.activateWorkbench(w)
                _loaded.add(w)
            except Exception as e:
                warn("could not load %s: %s" % (w, e))
        if cur and cur != Gui.activeWorkbench().name():
            Gui.activateWorkbench(cur)
    finally:
        win.setUpdatesEnabled(True)
    after_workbench_change()


def preload_all():
    for k in ("part", "assembly", "drawing", "addons"):
        load_environment(k)


def after_workbench_change():
    from . import naming, shortcuts
    naming.rename_commands()
    shortcuts.resolve_conflicts()
    hide_native_toolbars()
    c = _S.get("controller")
    if c:
        c.fix_docks()


# =============================================================== styling
STYLE = """
#FreeWorksTop { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FDFDFD, stop:1 #EEEFF1); border-bottom: 1px solid #D0D3D8; }
#FreeWorksTop QMenuBar { background: transparent; border: none; font-size: 9pt; }
#FreeWorksTop QMenuBar::item { padding: 3px 8px; background: transparent; }
#FreeWorksTop QMenuBar::item:selected { background: #CCE4F7; border: 1px solid #99C9EF; }
#FreeWorksTitle { color: #222; font-size: 10pt; }
#FreeWorksLogo { border: none; padding: 1px 4px; }
#FreeWorksQuick QToolButton { border: 1px solid transparent; border-radius: 2px; padding: 1px; }
#FreeWorksQuick QToolButton:hover { background: #E5F1FB; border-color: #A9CDEF; }
#FreeWorksSearch { border: 1px solid #B9BEC6; border-radius: 2px; padding: 2px 6px; background: #FFFFFF; min-width: 220px; }
#FreeWorksSearch:focus { border-color: #2F7BE5; }
#FreeWorksSearchMode { border: none; padding: 0 2px; }
#FreeWorksCM { background: #F7F7F8; }
#FreeWorksCMPanel { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FFFFFF, stop:1 #F1F2F4); border-bottom: 1px solid #C9CCD1; }
#FreeWorksCMPanel QToolButton { border: 1px solid transparent; border-radius: 2px; padding: 1px 2px; color: #1B1B1B; font-size: 8pt; }
#FreeWorksCMPanel QToolButton:hover { background: #E5F1FB; border-color: #A9CDEF; }
#FreeWorksCMPanel QToolButton:pressed { background: #CCE4F7; border-color: #6FA8E3; }
#FreeWorksCMPanel QToolButton:disabled { color: #9AA0A8; }
#FreeWorksCMPanel QToolButton[popupMode="1"] { padding-right: 10px; }
#FreeWorksCMSep { background: #D3D6DB; max-width: 1px; min-width: 1px; margin: 4px 3px; }
#FreeWorksTabs { background: #EDEEF0; border: none; }
#FreeWorksTabs::tab { background: transparent; border: 1px solid transparent; border-top: none; padding: 2px 12px 3px 12px; margin-right: 1px; color: #333; font-size: 8.5pt; }
#FreeWorksTabs::tab:selected { background: #FFFFFF; border-color: #C9CCD1; color: #000; }
#FreeWorksTabs::tab:hover:!selected { background: #E5F1FB; }
#FreeWorksHeadsUp, #FreeWorksFilters { background: transparent; }
#FreeWorksHeadsUp QToolButton, #FreeWorksFilters QToolButton { background: transparent; border: 1px solid transparent; border-radius: 3px; padding: 2px; }
#FreeWorksHeadsUp QToolButton:hover, #FreeWorksFilters QToolButton:hover { background: rgba(229,241,251,200); border-color: #A9CDEF; }
#FreeWorksHeadsUp QToolButton:checked, #FreeWorksFilters QToolButton:checked { background: rgba(204,228,247,230); border-color: #6FA8E3; }
#FreeWorksFilters { background: rgba(250,250,251,235); border: 1px solid #C6C9CE; border-radius: 3px; }
#FreeWorksPopupFrame { background: #FAFAFB; border: 1px solid #A7ADB6; }
#FreeWorksPopupTitle { font-weight: bold; color: #333; padding: 2px; }
#FreeWorksViewCell { background: #FFFFFF; border: 1px solid #C6C9CE; border-radius: 2px; padding: 4px; }
#FreeWorksViewCell:hover { background: #E5F1FB; border-color: #6FA8E3; }
#FreeWorksNewButton { border: 1px solid #C6C9CE; border-radius: 3px; background: #FFFFFF; font-size: 11pt; padding: 8px; }
#FreeWorksNewButton:hover { background: #E5F1FB; border-color: #2F7BE5; }
#FreeWorksStatusCtx { color: #333; padding: 0 10px; }
#FreeWorksStatusUnits { color: #333; padding: 0 8px; border-left: 1px solid #C6C9CE; }
"""

TREE_STYLE = """
QTreeView { background: #FFFFFF; border: none; show-decoration-selected: 0; }
QTreeView::item { padding: 1px 0px; border: 1px solid transparent; }
QTreeView::item:hover { background: #E5F1FB; border-color: #E5F1FB; }
QTreeView::item:selected { background: #CCE4F7; border-color: #99C9EF; color: #000; }
"""


def two_line(label):
    if len(label) <= 9 or " " not in label.strip():
        return label
    words = label.split(" ")
    best, bi = None, 1
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        d = abs(len(a) - len(b))
        if best is None or d < best:
            best, bi = d, i
    return " ".join(words[:bi]) + "\n" + " ".join(words[bi:])


def cmd_icon(cmd):
    try:
        info = Gui.Command.get(cmd).getInfo()
        return icon(info.get("pixmap") or cmd)
    except Exception:
        return icon(cmd)


def entry_icon(key):
    e = catalog.C[key]
    return icon(e["icon"]) if e["icon"] else cmd_icon(catalog.first_existing(e) or "")


def key_active(key):
    e = catalog.C.get(key)
    if not e:
        return False
    c = catalog.first_existing(e)
    if c is None:
        return False
    try:
        return bool(Gui.Command.get(c).isActive())
    except Exception:
        return False


# =============================================================== menus
def _act(menu, key):
    e = catalog.C.get(key)
    if not e or catalog.first_existing(e) is None:
        return None
    a = menu.addAction(entry_icon(key), e["label"])
    a.setStatusTip(e["tip"])
    a.setData(key)
    a.triggered.connect(lambda _=False, k=key: commands.run_key(k))
    return a


def _cmd_act(menu, cmd, label=None, ic=None):
    c = Gui.Command.get(cmd)
    if c is None:
        return None
    info = c.getInfo()
    a = menu.addAction(icon(ic) if ic else cmd_icon(cmd), label or info.get("menuText", cmd).replace("&", ""))
    sc = info.get("shortcut", "")
    if sc:
        a.setShortcut(QtGui.QKeySequence(sc))
        a.setShortcutContext(Qt.WidgetShortcut)   # display only; real shortcut is the command's
    a.setData("cmd:" + cmd)
    a.triggered.connect(lambda _=False, c=cmd: commands.run(c))
    return a


def _sub(menu, title, keys, ic=None):
    m = menu.addMenu(icon(ic) if ic else QtGui.QIcon(), title)
    for k in keys:
        if k == "|":
            m.addSeparator()
        elif k.startswith("cmd:"):
            _cmd_act(m, k[4:])
        else:
            _act(m, k)
    _wire_enable(m)
    return m


def _wire_enable(menu):
    def upd():
        for a in menu.actions():
            d = a.data()
            if not d:
                continue
            if d.startswith("cmd:"):
                c = Gui.Command.get(d[4:])
                try:
                    a.setEnabled(bool(c and c.isActive()))
                except Exception:
                    pass
            elif d in catalog.C:
                a.setEnabled(key_active(d))
    menu.aboutToShow.connect(upd)


def build_menubar(bar):
    bar.clear()
    m = bar.addMenu("&File")
    _act(m, "new_doc")
    for c in ("Std_Open", "Std_CloseActiveWindow", "|", "Std_Save", "Std_SaveAs", "Std_SaveCopy", "Std_SaveAll", "|",
              "Std_Import", "Std_Export", "|", "Std_PrintPreview", "Std_Print", "Std_PrintPdf", "|", "Std_ProjectInfo"):
        m.addSeparator() if c == "|" else _cmd_act(m, c)
    rec = m.addMenu("Recent Documents")
    rec.aboutToShow.connect(lambda r=rec: _fill_recent(r))
    m.addSeparator()
    _cmd_act(m, "Std_Quit", "Exit")
    _wire_enable(m)

    m = bar.addMenu("&Edit")
    for c in ("Std_Undo", "Std_Redo", "|", "Std_Cut", "Std_Copy", "Std_Paste", "Std_Delete", "|", "Std_SelectAll", "Std_ClarifySelection"):
        m.addSeparator() if c == "|" else _cmd_act(m, c)
    m.addSeparator()
    for k in ("rebuild", "force_rebuild", "|", "suppress", "rollback", "roll_end", "|", "appearance", "material"):
        m.addSeparator() if k == "|" else _act(m, k)
    m.addSeparator()
    _cmd_act(m, "Std_Edit", "Edit Feature")
    _cmd_act(m, "Std_Expressions", "Equations / Global Variables...")
    _cmd_act(m, "Std_Placement", "Move/Rotate (Placement)...")
    _wire_enable(m)

    m = bar.addMenu("&View")
    _sub(m, "Display", ["ds_edges", "ds_shaded", "ds_hlr", "ds_wire", "ds_points", "|", "perspective", "orthographic", "|", "section_view"], "display_style")
    _sub(m, "Hide/Show", ["hide_show", "toggle_vis", "cmd:Std_ShowSelection", "cmd:Std_HideSelection", "cmd:Std_ShowObjects", "cmd:Std_HideObjects"], "hide_show")
    _sub(m, "Modify (Orientation)", ["view_orient", "prev_view", "normal_to", "|", "v_front", "v_back", "v_left", "v_right", "v_top", "v_bottom", "v_iso", "v_dimetric", "v_trimetric", "|", "zoom_fit", "zoom_area", "zoom_sel", "zoom_in", "zoom_out"], "view_orientation")
    _act(m, "scene")
    m.addSeparator()
    ui = m.addMenu("User Interface")
    for title, opt in (("CommandManager", "CommandManager"), ("Heads-up View Toolbar", "HeadsUpToolbar")):
        a = ui.addAction(title)
        a.setCheckable(True)
        a.setChecked(params().GetBool(opt, True))
        a.toggled.connect(lambda on, opt=opt: _toggle_opt(opt, on))
    a = ui.addAction("Selection Filter (F6)")
    a.setCheckable(True)
    a.toggled.connect(lambda on: toggle_filter_toolbar(on))
    ui.aboutToShow.connect(lambda a=a: a.setChecked(bool(_S.get("filters") and _S["filters"].isVisible())))
    ui.addSeparator()
    for dn, title in (("Report view", "Report View (messages)"), ("Python console", "Python Console"), ("Selection view", "Selection View")):
        a = ui.addAction(title)
        a.setCheckable(True)
        a.toggled.connect(lambda on, dn=dn: _show_dock(dn, on))
        ui.aboutToShow.connect(lambda a=a, dn=dn: a.setChecked(bool(_dock(dn) and _dock(dn).isVisible())))
    ui.addSeparator()
    a = ui.addAction("Show FreeCAD Toolbars (advanced)")
    a.setCheckable(True)
    a.setChecked(params().GetBool("ShowNativeToolbars", False))
    a.toggled.connect(lambda on: (params().SetBool("ShowNativeToolbars", on), hide_native_toolbars(force_show=on)))
    m.addSeparator()
    _cmd_act(m, "Std_MainFullscreen", "Full Screen")
    _wire_enable(m)

    m = bar.addMenu("&Insert")
    _sub(m, "Boss/Base", ["extrude", "revolve", "sweep", "loft", "boundary", "helix_boss"], "extrude_boss")
    _sub(m, "Cut", ["extrude_cut", "revolve_cut", "sweep_cut", "loft_cut", "helix_cut"], "extrude_cut")
    _sub(m, "Features", ["fillet", "chamfer", "hole_wizard", "shell", "draft", "|", "combine", "intersect", "split", "move_copy_body", "scale", "delete_face", "thicken"], "fillet")
    _sub(m, "Pattern/Mirror", ["lpattern", "cpattern", "mirror", "multipattern"], "linear_pattern")
    _sub(m, "Surface", ["s_extrude", "s_revolve", "s_sweep", "s_loft", "s_boundary", "s_fill", "s_ruled", "s_offset", "s_extend", "s_knit", "s_blend"], "surface_loft")
    _sub(m, "Sheet Metal", ["sm_base", "sm_convert", "sm_edge", "sm_hem", "sm_sketched_bend", "sm_bend", "sm_relief", "sm_rip", "sm_extend", "sm_cutout", "sm_forming", "sm_sketch_on", "sm_unfold"], "base_flange")
    _sub(m, "Reference Geometry", ["plane", "axis", "point", "csys", "shapebinder"], "ref_geometry")
    m.addSeparator()
    _act(m, "sketch")
    _act(m, "body")
    m.addSeparator()
    _sub(m, "Component", ["insert_component", "new_component", "fasteners"], "insert_component")
    _act(m, "mate")
    _sub(m, "Mates", ["mate_fixed", "mate_revolute", "mate_concentric", "mate_distance", "mate_parallel", "mate_perpendicular", "mate_angle", "mate_slider", "mate_ball", "mate_gear", "mate_rack", "mate_screw", "mate_belt"], "mate")
    _act(m, "exploded_view")
    m.addSeparator()
    _sub(m, "Drawing View", ["std3view", "model_view", "projected_view", "section_dview", "aligned_section", "detail_view", "broken_view", "crop_view"], "model_view")
    _sub(m, "Annotations", ["d_smart_dim", "note", "balloon", "center_mark", "centerline_d", "surface_finish", "weld_symbol", "hatch", "d_bom", "table"], "note")
    _sub(m, "Drawing Sheet", ["new_sheet", "sheet_format"], "new_drawing")
    _wire_enable(m)

    m = bar.addMenu("&Tools")
    _sub(m, "Sketch Entities", ["line", "centerline", "corner_rect", "center_rect", "rounded_rect", "parallelogram", "slot", "arc_slot", "polygon", "circle", "perimeter_circle", "center_arc", "tangent_arc", "3pt_arc", "spline", "style_spline", "ellipse", "partial_ellipse", "parabola", "skpoint", "text"], "line")
    _sub(m, "Sketch Tools", ["sk_fillet", "sk_chamfer", "offset", "convert", "intersection", "carbon", "trim", "extend", "split_ent", "construction", "|", "sk_mirror", "sk_move", "sk_copy", "sk_rotate", "sk_scale", "sk_lpattern", "sk_cpattern", "|", "repair_sketch", "normal_sketch", "section_sketch", "grid", "snap"], "trim")
    _sub(m, "Relations", ["relations", "|"] + [k for k in catalog.C if k.startswith("rel_")] + ["|", "delete_relations"], "relations")
    _sub(m, "Dimensions", ["smart_dim", "rel_hdist", "rel_vdist", "rel_length", "rel_radius", "rel_diameter", "rel_angle"], "smart_dimension")
    _sub(m, "Evaluate", ["measure", "mass_props", "section_props", "interference", "check", "bbox", "curvature", "zebra", "draft_analysis", "section_cut"], "measure")
    _sub(m, "Selection Filter", ["sel_filter", "filter_vertex", "filter_edge", "filter_face", "filter_clear"], "selection_filter")
    m.addSeparator()
    mm = m.addMenu("Macro")
    for c in ("Std_DlgMacroExecute", "Std_DlgMacroRecord", "Std_OpenMacrosFolder"):
        _cmd_act(mm, c)
    _cmd_act(m, "Std_AddonMgr", "Add-Ins...")
    wbm = m.addMenu("FreeCAD Workbenches (advanced)")
    wbm.aboutToShow.connect(lambda wbm=wbm: _fill_workbenches(wbm))
    m.addSeparator()
    _act(m, "search")
    _act(m, "magnify")
    _act(m, "shortcut_bar")
    m.addSeparator()
    _cmd_act(m, "Std_DlgCustomize", "Customize...")
    _cmd_act(m, "Std_DlgPreferences", "Options...", "options")
    _act(m, "fw_options")
    _wire_enable(m)

    m = bar.addMenu("&Window")
    for c in ("Std_CloseActiveWindow", "Std_CloseAllWindows", "|", "Std_TileWindows", "Std_CascadeWindows", "|", "Std_ActivateNextWindow", "Std_ActivatePrevWindow"):
        m.addSeparator() if c == "|" else _cmd_act(m, c)
    m.addSeparator()
    wl = m.addMenu("Documents")
    wl.aboutToShow.connect(lambda wl=wl: _fill_windows(wl))
    _wire_enable(m)

    m = bar.addMenu("&Help")
    a = m.addAction(icon("freeworks"), "FreeWorks Command Map (SolidWorks → FreeCAD)")
    a.triggered.connect(show_command_map)
    a = m.addAction("FreeWorks Keyboard Shortcuts")
    a.triggered.connect(show_shortcut_map)
    from . import updater
    a = m.addAction("What's New in FreeWorks")
    a.triggered.connect(lambda: updater.show_whats_new(force=True))
    a = m.addAction("Check for FreeWorks Updates...")
    a.triggered.connect(lambda: updater.check(manual=True))
    rb = m.addAction("Roll Back to Previous Version...")
    rb.triggered.connect(updater.rollback)
    m.aboutToShow.connect(lambda rb=rb: rb.setEnabled(bool(updater.previous_version())))
    a = m.addAction("FreeWorks on GitHub")
    a.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/scp15156402/FreeWorks")))
    m.addSeparator()
    for c in ("Std_OnlineHelp", "Std_FreeCADUserHub", "Std_FreeCADForum", "|", "Std_About"):
        m.addSeparator() if c == "|" else _cmd_act(m, c)


def _fill_recent(menu):
    from .widgets import NewDocumentDialog
    menu.clear()
    for f in NewDocumentDialog.recent():
        a = menu.addAction(os.path.basename(f))
        a.setToolTip(f)
        a.triggered.connect(lambda _=False, f=f: Gui.open(f))
    if not menu.actions():
        menu.addAction("(none)").setEnabled(False)


def _fill_windows(menu):
    menu.clear()
    mdi = context.mdi_area()
    for sw in mdi.subWindowList():
        a = menu.addAction(sw.windowTitle())
        a.setCheckable(True)
        a.setChecked(sw is mdi.activeSubWindow())
        a.triggered.connect(lambda _=False, sw=sw: mdi.setActiveSubWindow(sw))


def _fill_workbenches(menu):
    menu.clear()
    for name, wb in sorted(Gui.listWorkbenches().items(), key=lambda x: x[1].MenuText):
        if name in ("NoneWorkbench", "TestWorkbench"):
            continue
        a = menu.addAction(wb.MenuText)
        a.triggered.connect(lambda _=False, n=name: Gui.activateWorkbench(n))


def _toggle_opt(name, on):
    params().SetBool(name, on)
    refresh_options()


def _dock(name):
    for d in mw().findChildren(QtWidgets.QDockWidget):
        if d.objectName() == name:
            return d
    return None


def _show_dock(name, on):
    d = _dock(name)
    if d:
        d.setVisible(on)
        if on:
            d.raise_()
        _S.setdefault("user_docks", {})[name] = on


# ============================================================ top bar
class TopBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("FreeWorksTop")
        self.setAttribute(Qt.WA_StyledBackground, True)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(4, 1, 6, 1)
        lay.setSpacing(4)
        logo = QtWidgets.QToolButton()
        logo.setObjectName("FreeWorksLogo")
        logo.setIcon(icon("freeworks"))
        logo.setIconSize(QtCore.QSize(20, 20))
        logo.setToolTip("FreeWorks")
        logo.clicked.connect(lambda: commands.run_key("fw_options"))
        lay.addWidget(logo)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setNativeMenuBar(False)
        build_menubar(self.menubar)
        lay.addWidget(self.menubar)
        quick = QtWidgets.QWidget()
        quick.setObjectName("FreeWorksQuick")
        ql = QtWidgets.QHBoxLayout(quick)
        ql.setContentsMargins(6, 0, 0, 0)
        ql.setSpacing(1)
        for item in ("new_doc", "cmd:Std_Open", "cmd:Std_Save", "cmd:Std_Print", "|", "cmd:Std_Undo", "cmd:Std_Redo", "|",
                     "cmd:Std_SelectAll", "rebuild", "|", "options"):
            if item == "|":
                s = QtWidgets.QFrame()
                s.setFrameShape(QtWidgets.QFrame.VLine)
                s.setStyleSheet("color:#C9CCD1")
                ql.addWidget(s)
                continue
            b = QtWidgets.QToolButton()
            b.setIconSize(QtCore.QSize(18, 18))
            b.setAutoRaise(True)
            if item.startswith("cmd:"):
                c = item[4:]
                b.setIcon(cmd_icon(c))
                info = Gui.Command.get(c).getInfo() if Gui.Command.get(c) else {}
                b.setToolTip(info.get("menuText", c).replace("&", ""))
                b.clicked.connect(lambda _=False, c=c: commands.run(c))
            else:
                b.setIcon(entry_icon(item))
                b.setToolTip(catalog.C[item]["label"])
                b.clicked.connect(lambda _=False, k=item: commands.run_key(k))
            ql.addWidget(b)
        lay.addWidget(quick)
        lay.addStretch(1)
        self.title = QtWidgets.QLabel("FreeWorks")
        self.title.setObjectName("FreeWorksTitle")
        lay.addWidget(self.title)
        lay.addStretch(1)
        # command search (W / I / H)
        self.mode = QtWidgets.QToolButton()
        self.mode.setObjectName("FreeWorksSearchMode")
        self.mode.setIcon(icon("search"))
        self.mode.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        mm = QtWidgets.QMenu(self.mode)
        for title, m in (("Commands", "commands"), ("Files and Models", "files"), ("Help", "help")):
            a = mm.addAction(title)
            a.triggered.connect(lambda _=False, m=m: self.set_mode(m))
        self.mode.setMenu(mm)
        lay.addWidget(self.mode)
        self.search = QtWidgets.QLineEdit()
        self.search.setObjectName("FreeWorksSearch")
        self.search.setClearButtonEnabled(True)
        lay.addWidget(self.search)
        self.model = QtGui.QStandardItemModel(self)
        self.comp = QtWidgets.QCompleter(self.model, self)
        self.comp.setCaseSensitivity(Qt.CaseInsensitive)
        self.comp.setFilterMode(Qt.MatchContains)
        self.comp.setMaxVisibleItems(16)
        self.comp.setCompletionRole(Qt.DisplayRole)
        self.search.setCompleter(self.comp)
        self.comp.activated[QtCore.QModelIndex].connect(self.on_pick)
        self.search.returnPressed.connect(self.on_return)
        self.set_mode("commands")

    def set_mode(self, m):
        self.mode_name = m
        self.search.setPlaceholderText({"commands": "Search Commands", "files": "Search Files and Models",
                                        "help": "Search FreeCAD Help"}[m])
        self.model.clear()
        if m == "commands":
            seen = set()
            for k, e in catalog.C.items():
                if catalog.first_existing(e) is None:
                    continue
                it = QtGui.QStandardItem(entry_icon(k), e["label"])
                it.setData(k, Qt.UserRole)
                it.setToolTip(e["tip"])
                self.model.appendRow(it)
                for a in e["aliases"]:
                    t = "%s  →  %s" % (a, e["label"])
                    if t in seen:
                        continue
                    seen.add(t)
                    it = QtGui.QStandardItem(entry_icon(k), t)
                    it.setData(k, Qt.UserRole)
                    self.model.appendRow(it)
        elif m == "files":
            from .widgets import NewDocumentDialog
            for f in NewDocumentDialog.recent():
                it = QtGui.QStandardItem(icon("new_document"), os.path.basename(f))
                it.setData("file:" + f, Qt.UserRole)
                it.setToolTip(f)
                self.model.appendRow(it)

    def on_pick(self, idx):
        d = idx.data(Qt.UserRole)
        QtCore.QTimer.singleShot(0, lambda: self._do(d))

    def on_return(self):
        txt = self.search.text().strip()
        if not txt:
            return
        if self.mode_name == "help":
            QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://wiki.freecad.org/index.php?search=" + QtCore.QUrl.toPercentEncoding(txt).data().decode()))
            self.search.clear()
            return
        if self.mode_name == "files" and os.path.exists(txt):
            self._do("file:" + txt)
            return
        low = txt.lower()
        for text, key in catalog.search_index():
            if text == low or text.startswith(low):
                self._do(key)
                return

    def _do(self, d):
        if not d:
            return
        self.search.clear()
        mw().setFocus()
        if d.startswith("file:"):
            Gui.open(d[5:])
        else:
            commands.run_key(d)

    def focus(self, mode="commands"):
        if mode != self.mode_name:
            self.set_mode(mode)
        self.search.setFocus(Qt.ShortcutFocusReason)
        self.search.selectAll()


def focus_search(mode="commands"):
    t = _S.get("topbar")
    if t:
        t.focus(mode)


# ======================================================== CommandManager
class CommandManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("FreeWorksCM")
        self.setAttribute(Qt.WA_StyledBackground, True)
        v = QtWidgets.QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        self.stack = QtWidgets.QStackedWidget()
        v.addWidget(self.stack)
        self.tabs = QtWidgets.QTabBar()
        self.tabs.setObjectName("FreeWorksTabs")
        self.tabs.setShape(QtWidgets.QTabBar.RoundedSouth)
        self.tabs.setDrawBase(False)
        self.tabs.setExpanding(False)
        self.tabs.currentChanged.connect(self.on_tab)
        v.addWidget(self.tabs)
        self.panels = {}       # tab name -> (widget, [(button, key)])
        self.tabset = None
        self.kind = None
        self.saved_tab = {}
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_states)
        self.timer.start(400)

    # -- building
    def _layout_for(self, name, spec):
        if spec == "sketch":
            return catalog.SKETCH_TAB
        if isinstance(spec, str) and spec.startswith("part:"):
            return dict(catalog.TABS["part"])[spec[5:]]
        return spec

    def build_panel(self, name, spec):
        layout = self._layout_for(name, spec)
        w = QtWidgets.QWidget()
        w.setObjectName("FreeWorksCMPanel")
        w.setAttribute(Qt.WA_StyledBackground, True)
        h = QtWidgets.QHBoxLayout(w)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(1)
        buttons = []
        large = params().GetInt("LargeIconSize", 32)
        with_text = params().GetBool("CommandManagerText", True)
        for g in layout:
            if g[0] == "|":
                s = QtWidgets.QFrame()
                s.setObjectName("FreeWorksCMSep")
                s.setFrameShape(QtWidgets.QFrame.NoFrame)
                h.addWidget(s)
            elif g[0] == "L":
                b = self._button(g[1], large, with_text, "large", g[2] if len(g) > 2 else None)
                if b:
                    h.addWidget(b)
                    buttons.append((b, g[1]))
            elif g[0] == "S":
                col = QtWidgets.QVBoxLayout()
                col.setSpacing(0)
                col.setContentsMargins(0, 0, 0, 0)
                n = 0
                for k in g[1]:
                    b = self._button(k, 16, with_text, "small")
                    if b:
                        col.addWidget(b)
                        buttons.append((b, k))
                        n += 1
                if n:
                    col.addStretch(1)
                    h.addLayout(col)
        h.addStretch(1)
        return w, buttons

    def _button(self, key, size, with_text, kind, flyout=None):
        e = catalog.C.get(key)
        if not e or catalog.first_existing(e) is None:
            return None
        b = QtWidgets.QToolButton()
        b.setIcon(entry_icon(key))
        b.setIconSize(QtCore.QSize(size, size))
        b.setToolTip("<b>%s</b><br>%s" % (e["label"], e["tip"]) + ("<br><i>(closest FreeCAD equivalent)</i>" if e["approx"] else ""))
        b.setAutoRaise(True)
        if kind == "large":
            b.setText(two_line(e["label"]) if with_text else "")
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon if with_text else Qt.ToolButtonIconOnly)
            b.setMinimumWidth(52 if with_text else 36)
            b.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        else:
            b.setText(e["label"] if with_text else "")
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon if with_text else Qt.ToolButtonIconOnly)
            b.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        b.clicked.connect(lambda _=False, k=key: commands.run_key(k))
        if flyout:
            m = QtWidgets.QMenu(b)
            for fk in flyout:
                fe = catalog.C.get(fk)
                if fe and catalog.first_existing(fe):
                    a = m.addAction(entry_icon(fk), fe["label"])
                    a.setData(fk)
                    a.triggered.connect(lambda _=False, k=fk: commands.run_key(k))
            _wire_enable(m)
            b.setMenu(m)
            b.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        return b

    def tabs_for(self, kind):
        if kind in ("part", "sketch", "none", None):
            spec = list(catalog.TABS["part"])
            spec = [t for t in spec if t[0] != "Sheet Metal" or catalog.first_existing(catalog.C["sm_base"]) and Gui.Command.get("SheetMetal_AddWall")]
            return spec
        return list(catalog.TABS[kind])

    def set_context(self, ctx, force=False):
        kind = context.doc_type() if ctx in ("sketch",) else ctx
        if kind in (None, "none", "sketch"):
            kind = "part"
        if force or kind != self.kind:
            if self.kind:
                self.saved_tab[self.kind] = self.tabs.tabText(self.tabs.currentIndex())
            self.kind = kind
            self.tabset = self.tabs_for(kind)
            self.tabs.blockSignals(True)
            while self.tabs.count():
                self.tabs.removeTab(0)
            for name, _ in self.tabset:
                self.tabs.addTab(name)
            self.tabs.blockSignals(False)
            want = self.saved_tab.get(kind) or self.tabset[0][0]
            self.select(want)
        if ctx == "sketch":
            if self.current_name() != "Sketch":
                self._before_sketch = self.current_name()
                self.select("Sketch")
        elif getattr(self, "_before_sketch", None):
            if self.current_name() == "Sketch":
                self.select(self._before_sketch)
            self._before_sketch = None

    def current_name(self):
        return self.tabs.tabText(self.tabs.currentIndex())

    def select(self, name):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == name:
                self.tabs.setCurrentIndex(i)
                self.on_tab(i)
                return

    def on_tab(self, i):
        if i < 0 or not self.tabset or i >= len(self.tabset):
            return
        name, spec = self.tabset[i]
        pk = (self.kind, name)
        if pk not in self.panels:
            w, btns = self.build_panel(name, spec)
            self.panels[pk] = (w, btns)
            self.stack.addWidget(w)
        self.stack.setCurrentWidget(self.panels[pk][0])
        self.update_states()

    def rebuild(self):
        for w, _ in self.panels.values():
            self.stack.removeWidget(w)
            w.deleteLater()
        self.panels = {}
        self.set_context(context.current(), force=True)

    def update_states(self):
        if not self.isVisible() or not QtWidgets.QApplication.activeWindow():
            return
        w = self.stack.currentWidget()
        for pk, (pw, btns) in self.panels.items():
            if pw is w:
                for b, k in btns:
                    on = key_active(k)
                    if b.isEnabled() != on:
                        b.setEnabled(on)
                break


# ============================================================ heads-up bar
class HeadsUp(QtWidgets.QFrame):
    ITEMS = ["zoom_fit", "zoom_area", "prev_view", "section_view", "|", "view_orient", "display", "hide_show", "appearance", "scene"]

    def __init__(self, mdi):
        super().__init__(mdi)
        self.setObjectName("FreeWorksHeadsUp")
        self.mdi = mdi
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)
        self.btns = []
        for k in self.ITEMS:
            if k == "|":
                s = QtWidgets.QFrame()
                s.setFixedWidth(6)
                lay.addWidget(s)
                continue
            b = QtWidgets.QToolButton()
            b.setIconSize(QtCore.QSize(22, 22))
            b.setAutoRaise(True)
            if k == "display":
                b.setIcon(icon("display_style"))
                b.setToolTip("Display Style")
                m = QtWidgets.QMenu(b)
                for dk in ("ds_edges", "ds_shaded", "ds_hlr", "ds_wire"):
                    a = m.addAction(entry_icon(dk), catalog.C[dk]["label"])
                    a.triggered.connect(lambda _=False, dk=dk: commands.run_key(dk))
                b.setMenu(m)
                b.setPopupMode(QtWidgets.QToolButton.InstantPopup)
            elif k == "view_orient":
                b.setIcon(icon("view_orientation"))
                b.setToolTip("View Orientation (Spacebar)")
                m = QtWidgets.QMenu(b)
                for vk in ("v_front", "v_back", "v_left", "v_right", "v_top", "v_bottom", "v_iso", "v_dimetric", "v_trimetric", "|", "normal_to"):
                    if vk == "|":
                        m.addSeparator()
                        continue
                    a = m.addAction(entry_icon(vk), catalog.C[vk]["label"])
                    a.triggered.connect(lambda _=False, vk=vk: commands.run_key(vk))
                b.setMenu(m)
                b.setPopupMode(QtWidgets.QToolButton.InstantPopup)
            else:
                e = catalog.C[k]
                b.setIcon(entry_icon(k))
                b.setToolTip("<b>%s</b><br>%s" % (e["label"], e["tip"]))
                b.clicked.connect(lambda _=False, k=k: commands.run_key(k))
            lay.addWidget(b)
            self.btns.append(b)
        mdi.installEventFilter(self)
        self.reposition()

    def eventFilter(self, o, e):
        if e.type() == QtCore.QEvent.Resize:
            self.reposition()
        return False

    def reposition(self):
        self.adjustSize()
        x = max(0, (self.mdi.width() - self.width()) // 2)
        self.move(x, 4)
        self.raise_()

    def refresh(self):
        show = params().GetBool("HeadsUpToolbar", True) and bool(context.mdi_area().subWindowList())
        self.setVisible(show)
        if show:
            self.raise_()


class FilterBar(QtWidgets.QFrame):
    def __init__(self, mdi):
        super().__init__(mdi)
        self.setObjectName("FreeWorksFilters")
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(1)
        t = QtWidgets.QLabel(" Filter: ")
        lay.addWidget(t)
        self.group = QtWidgets.QButtonGroup(self)
        self.group.setExclusive(False)
        self.btn = {}
        for k in ("filter_vertex", "filter_edge", "filter_face", "filter_clear"):
            b = QtWidgets.QToolButton()
            b.setIcon(entry_icon(k))
            b.setIconSize(QtCore.QSize(20, 20))
            b.setToolTip(catalog.C[k]["label"])
            b.setCheckable(k != "filter_clear")
            b.clicked.connect(lambda _=False, k=k: set_filter(k))
            lay.addWidget(b)
            self.btn[k] = b
        self.adjustSize()
        self.move(8, 8)
        self.hide()

    def sync(self, active):
        for k, b in self.btn.items():
            if b.isCheckable():
                b.setChecked(k == active)


_filter = {"active": None}


def set_filter(key):
    if key == "filter_clear" or _filter["active"] == key:
        commands.run("Part_RemoveSelectionGate")
        _filter["active"] = None
        commands.msg("Selection filters cleared")
    else:
        if catalog.first_existing(catalog.C[key]):
            commands.run(catalog.first_existing(catalog.C[key]))
            _filter["active"] = key
            commands.msg(catalog.C[key]["label"] + " (press again to clear)")
    fb = _S.get("filters")
    if fb:
        fb.sync(_filter["active"])


def toggle_filter_toolbar(on=None):
    fb = _S.get("filters")
    if fb is None:
        return
    fb.setVisible(not fb.isVisible() if on is None else on)
    if fb.isVisible():
        fb.raise_()


# ============================================================ native UI
_OURS = ("FreeWorks",)


class _ToolbarGuard(QtCore.QObject):
    """Keeps FreeCAD's own toolbars hidden (the CommandManager replaces them)."""

    def eventFilter(self, o, e):
        t = e.type()
        if t == QtCore.QEvent.Show and isinstance(o, QtWidgets.QToolBar):
            if not params().GetBool("ShowNativeToolbars", False) and not o.objectName().startswith(_OURS):
                QtCore.QTimer.singleShot(0, o.hide)
        elif t == QtCore.QEvent.ChildAdded and o is mw():
            ch = e.child()
            if isinstance(ch, QtWidgets.QToolBar):
                ch.installEventFilter(self)
                if not params().GetBool("ShowNativeToolbars", False):
                    QtCore.QTimer.singleShot(0, ch.hide)
        return False


def hide_native_toolbars(force_show=False):
    win = mw()
    g = _S.get("guard")
    for tb in win.findChildren(QtWidgets.QToolBar):
        if tb.objectName().startswith(_OURS) or tb.parent() is not win:
            continue
        if g:
            tb.removeEventFilter(g)
            tb.installEventFilter(g)
        if force_show:
            tb.show()
        elif not params().GetBool("ShowNativeToolbars", False):
            tb.hide()
    win.menuBar().setVisible(params().GetBool("ShowNativeToolbars", False))


# ============================================================== status bar
class Status:
    def __init__(self):
        sb = mw().statusBar()
        self.sketch = QtWidgets.QLabel("")
        self.sketch.setObjectName("FreeWorksStatusCtx")
        self.ctx = QtWidgets.QLabel("")
        self.ctx.setObjectName("FreeWorksStatusCtx")
        self.units = QtWidgets.QToolButton()
        self.units.setObjectName("FreeWorksStatusUnits")
        self.units.setAutoRaise(True)
        self.units.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        um = QtWidgets.QMenu(self.units)
        for i, (name, schema) in enumerate((("MMGS (millimeter, gram, second)", 0), ("MKS (meter, kilogram, second)", 1),
                                            ("IPS (inch, pound, second)", 3), ("CGS (centimeter, gram, second)", 0))):
            a = um.addAction(name)
            a.triggered.connect(lambda _=False, s=schema, n=name.split(" ")[0]: self.set_units(s, n))
        self.units.setMenu(um)
        sb.addPermanentWidget(self.sketch)
        sb.addPermanentWidget(self.ctx)
        sb.addPermanentWidget(self.units)
        self.units.setText(params().GetString("UnitsLabel", "MMGS"))

    def set_units(self, schema, label):
        App.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema", schema)
        try:
            App.Units.setSchema(schema)
        except Exception:
            pass
        params().SetString("UnitsLabel", label)
        self.units.setText(label)

    def update(self, ctx):
        from . import sketchmode
        st = sketchmode.status() if ctx == "sketch" else None
        if st:
            self.sketch.setText(st[0])
            self.sketch.setStyleSheet("color:%s; font-weight:bold; padding:0 10px;" % st[1])
            self.sketch.show()
        else:
            self.sketch.hide()
        self.ctx.setText(context.label(ctx))


# ============================================================== controller
class Controller(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ctx = None
        self.task_open = False
        self.t = QtCore.QTimer(self)
        self.t.timeout.connect(self.tick)
        self.t.start(250)
        mdi = context.mdi_area()
        mdi.subWindowActivated.connect(lambda *_: QtCore.QTimer.singleShot(0, lambda: on_context_change(True)))
        try:
            mw().workbenchActivated.connect(lambda *_: QtCore.QTimer.singleShot(0, after_workbench_change))
        except Exception:
            pass
        self.docks_done = False

    @safe
    def tick(self):
        c = context.current()
        if c != self.ctx:
            self.ctx = c
            on_context_change()
        st = _S.get("status")
        if st:
            st.update(c)
        # PropertyManager behaviour: show the task panel tab while a command runs
        try:
            open_ = Gui.Control.activeDialog()
        except Exception:
            open_ = False
        if open_ != self.task_open:
            self.task_open = open_
            d = _dock("Tasks") if open_ else _dock("Model")
            if d:
                d.show()
                d.raise_()
        tb = _S.get("topbar")
        if tb:
            doc = App.ActiveDocument
            t = ""
            if doc:
                t = doc.Label + (" *" if doc.isTouched() or _modified(doc) else "")
            if tb.title.text() != (t or "FreeWorks"):
                tb.title.setText(t or "FreeWorks")

    def fix_docks(self):
        win = mw()
        model, tasks = _dock("Model"), _dock("Tasks")
        win.setTabPosition(Qt.LeftDockWidgetArea, QtWidgets.QTabWidget.North)
        if model:
            model.setWindowTitle("FeatureManager")
            if win.dockWidgetArea(model) != Qt.LeftDockWidgetArea:
                win.addDockWidget(Qt.LeftDockWidgetArea, model)
            from . import contextmenu
            hook = _S.setdefault("treehook", contextmenu.TreeHook())
            for tv in model.findChildren(QtWidgets.QTreeView):
                if tv.styleSheet() != TREE_STYLE:
                    tv.setStyleSheet(TREE_STYLE)
                if tv.metaObject().className() == "Gui::TreeWidget":
                    hook.hook(tv)
            if not self.docks_done:
                for sp in model.findChildren(QtWidgets.QSplitter):
                    tot = sum(sp.sizes()) or 800
                    sp.setSizes([int(tot * 0.72), int(tot * 0.28)])
        if tasks:
            tasks.setWindowTitle("PropertyManager")
            # FreeCAD 1.1 puts the task panel into a floating overlay
            if tasks.parent() is not win:
                tasks.setParent(win)
                win.addDockWidget(Qt.LeftDockWidgetArea, tasks)
                tasks.show()
            if tasks.isFloating():
                tasks.setFloating(False)
            for ov in win.findChildren(QtWidgets.QWidget):
                if ov.metaObject().className() == "Gui::OverlayTabWidget" and not ov.findChildren(QtWidgets.QDockWidget):
                    ov.hide()
            ov = App.ParamGet("User parameter:BaseApp/MainWindow/DockWindows/OverlayRight")
            if "Tasks" in ov.GetString("Widgets", ""):
                ov.SetString("Widgets", "")
        for d in (model, tasks):
            if d is not None and not isinstance(d.titleBarWidget(), _NoTitle):
                d.setTitleBarWidget(_NoTitle())
            if model and win.dockWidgetArea(tasks) != Qt.LeftDockWidgetArea:
                win.addDockWidget(Qt.LeftDockWidgetArea, tasks)
            if model and tasks not in win.tabifiedDockWidgets(model):
                win.tabifyDockWidget(model, tasks)
            if model and not self.task_open:
                model.raise_()
        user = _S.get("user_docks", {})
        for n in ("Tree view", "Property view"):
            d = _dock(n)
            if d and d is not model:
                d.hide()
        for n in ("Report view", "Python console", "Selection view"):
            d = _dock(n)
            if d and not user.get(n, False):
                d.hide()
        self.docks_done = True


class _NoTitle(QtWidgets.QWidget):
    """Empty dock title bar: the tab already names the panel (as in SolidWorks)."""

    def sizeHint(self):
        return QtCore.QSize(0, 0)


def _modified(doc):
    try:
        gd = Gui.getDocument(doc.Name)
        return gd.Modified
    except Exception:
        return False


@safe
def on_context_change(force=False):
    ctx = context.current()
    cm = _S.get("cm")
    if cm:
        cm.set_context(ctx, force=force)
    hu = _S.get("headsup")
    if hu:
        hu.refresh()
    from . import gestures
    gestures.hook_views()


def refresh_options():
    d = _S.get("dock")
    if d:
        _S["cm"].setVisible(params().GetBool("CommandManager", True))
        _S["cm"].rebuild()
    hu = _S.get("headsup")
    if hu:
        hu.refresh()


# ================================================================= install
def install():
    if _S.get("dock"):
        return
    win = mw()
    # our widgets are styled at main-window level (survives FreeCAD re-applying
    # its application stylesheet when preferences change)
    if "FreeWorksTop" not in (win.styleSheet() or ""):
        win.setStyleSheet((win.styleSheet() or "") + STYLE)
    _S["guard"] = _ToolbarGuard()
    win.installEventFilter(_S["guard"])
    dock = QtWidgets.QDockWidget("FreeWorks", win)
    dock.setObjectName("FreeWorksCommandDock")
    dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
    dock.setAllowedAreas(Qt.TopDockWidgetArea)
    dock.setTitleBarWidget(QtWidgets.QWidget())
    body = QtWidgets.QWidget()
    v = QtWidgets.QVBoxLayout(body)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(0)
    _S["topbar"] = TopBar()
    v.addWidget(_S["topbar"])
    _S["cm"] = CommandManager()
    v.addWidget(_S["cm"])
    _S["cm"].setVisible(params().GetBool("CommandManager", True))
    dock.setWidget(body)
    win.setCorner(Qt.TopLeftCorner, Qt.TopDockWidgetArea)
    win.setCorner(Qt.TopRightCorner, Qt.TopDockWidgetArea)
    win.addDockWidget(Qt.TopDockWidgetArea, dock)
    _S["dock"] = dock
    mdi = context.mdi_area()
    _S["headsup"] = HeadsUp(mdi)
    _S["filters"] = FilterBar(mdi)
    _S["status"] = Status()
    _S["controller"] = Controller()
    hide_native_toolbars()
    _S["controller"].fix_docks()
    on_context_change(force=True)
    log("shell installed")


# ============================================================ help windows
def _table_dialog(title, headers, rows):
    d = QtWidgets.QDialog(mw())
    d.setWindowTitle(title)
    d.resize(760, 620)
    lay = QtWidgets.QVBoxLayout(d)
    f = QtWidgets.QLineEdit()
    f.setPlaceholderText("Filter...")
    lay.addWidget(f)
    t = QtWidgets.QTableWidget(len(rows), len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().hide()
    t.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            it = QtWidgets.QTableWidgetItem(val) if not isinstance(val, tuple) else QtWidgets.QTableWidgetItem(val[0], val[1])
            t.setItem(r, c, it)
    t.resizeColumnsToContents()
    t.horizontalHeader().setStretchLastSection(True)
    lay.addWidget(t)
    f.textChanged.connect(lambda s: [t.setRowHidden(r, s.lower() not in " ".join(t.item(r, c).text().lower() for c in range(len(headers)) if t.item(r, c))) for r in range(t.rowCount())])
    d.show()


def show_command_map():
    rows = []
    for k, e in catalog.C.items():
        c = catalog.first_existing(e)
        rows.append(((entry_icon(k), e["label"]), c or "(add-on not installed: %s)" % e["cmd"][0],
                     "approximate" if e["approx"] else "", ", ".join(e["aliases"])))
    _table_dialog("FreeWorks Command Map", ["SolidWorks command", "FreeCAD command", "Note", "Search aliases"], rows)


def show_shortcut_map():
    from . import shortcuts
    _table_dialog("FreeWorks Keyboard Shortcuts", ["Key", "Context", "Command"], shortcuts.describe())
