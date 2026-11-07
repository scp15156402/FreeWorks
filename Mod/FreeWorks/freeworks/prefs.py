"""FreeCAD preferences for a SolidWorks look & feel, rendering quality and
smooth interaction.  Applied once (and again on demand from FreeWorks Options)."""
import os
import shutil
import FreeCAD as App

from . import THEME_DIR, log, params

PREFS_VERSION = 9


def c(hexstr, a=255):
    h = hexstr.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r << 24) | (g << 16) | (b << 8) | a


def P(path):
    return App.ParamGet("User parameter:BaseApp/Preferences/" + path)


SETTINGS = {
    # ---------------------------------------------------- 3D view / navigation
    "View": {
        "NavigationStyle": ("s", "Gui::SolidWorksNavigationStyle"),
        "OrbitStyle": ("i", 1),                 # trackball
        "RotationMode": ("i", 1),               # rotate about the window/model center like SW
        "ZoomAtCursor": ("b", True),
        "InvertZoom": ("b", False),             # SW: wheel toward you zooms in
        "ZoomStep": ("f", 0.2),
        "UseNavigationAnimations": ("b", True), # animated view transitions
        "AnimationDuration": ("i", 300),
        "Spinning": ("b", False),
        "ShowNaviCube": ("b", False),           # SW uses the spacebar view selector instead
        "CornerCoordSystem": ("b", True),       # reference triad
        "CornerCoordSystemSize": ("i", 9),
        "ShowAxisCross": ("b", False),
        "ShowFPS": ("b", False),
        # rendering quality + speed
        "AntiAliasing": ("i", 1),               # line smoothing (MSAA 4x is opt-in: it makes FreeCAD
                                                # re-allocate buffers on every sketch edit = memory growth)
        "UseVBO": ("b", True),                  # vertex buffer objects (GPU)
        "RenderCache": ("i", 0),                # auto render cache
        "TransparentObjectRenderType": ("i", 0),
        "MarkerSize": ("i", 7),
        "EnablePreselection": ("b", True),
        "EnableSelection": ("b", True),
        # colors (SolidWorks defaults: orange pre-highlight, blue selection)
        "HighlightColor": ("u", c("#D2601A")),
        "SelectionColor": ("u", c("#2F7BE5")),
        "DefaultShapeColor": ("u", c("#CDD2DA")),
        "RandomColor": ("b", False),
        "DefaultShapeLineColor": ("u", c("#1A1A1A")),
        "DefaultShapeVertexColor": ("u", c("#1A1A1A")),
        "DefaultShapeLineWidth": ("i", 1),
        "DefaultShapePointSize": ("i", 3),
        "DefaultShapeTransparency": ("i", 0),
        # background: SW-like light gradient
        "Simple": ("b", False),
        "Gradient": ("b", True),
        "RadialGradient": ("b", False),
        "UseBackgroundColorMid": ("b", False),
        "BackgroundColor": ("u", c("#C7D6EB")),
        "BackgroundColor2": ("u", c("#C7D6EB")),
        "BackgroundColor3": ("u", c("#FFFFFF")),
        "Dragger": ("b", True),
    },
    "View/LightSources": {
        "EnableHeadlight": ("b", True),
        "HeadlightIntensity": ("i", 90),
        "EnableFillLight": ("b", True),
        "FillLightIntensity": ("i", 45),
        "EnableBacklight": ("b", True),
        "BacklightIntensity": ("i", 20),
        "AmbientLightIntensity": ("i", 18),
    },
    # tessellation: finer = smoother round surfaces (SW "image quality" ~ high)
    "Mod/Part": {
        "MeshDeviation": ("f", 0.1),
        "MeshAngularDeflection": ("f", 12.0),
    },
    "Mod/Part/General": {"AutoRefine": ("b", True)},
    "Mod/PartDesign": {"RefineModel": ("b", True), "SwitchToTask": ("b", True), "PreviewTransparency": ("b", True)},
    # ---------------------------------------------------------------- sketcher
    "Mod/Sketcher": {
        "ShowDialogOnDistanceConstraint": ("b", True),   # Modify dialog after placing a dimension
        "AutoRecompute": ("b", True),
    },
    "Mod/Sketcher/General": {
        "AutoConstraints": ("b", True),        # automatic relations while sketching
        "AvoidRedundantAutoconstraints": ("b", True),
        "ContinuousCreationMode": ("b", True), # tools stay active like SW
        "ContinuousConstraintMode": ("b", True),
        "ShowDialogOnDistanceConstraint": ("b", True),
        "ShowGrid": ("b", False),
    },
    "Mod/Sketcher/View": {
        "ShowGrid": ("b", False),
        "ForceOrtho": ("b", True),
        "SectionView": ("b", False),
        "HideDependent": ("b", True),
        "ShowLinks": ("b", True),
        "ShowSupport": ("b", True),
        "RestoreCamera": ("b", True),
        "EditSketcherFontSize": ("i", 16),
        "ConstraintSymbolSize": ("i", 15),
        "ShowDimensionalName": ("b", False),
    },
    "View/Sketcher": {},
    # ------------------------------------------------------------------ tree
    "TreeView": {
        "SyncSelection": ("b", True),
        "SyncView": ("b", False),
        "PreSelection": ("b", True),
        "VisibilityIcon": ("b", False),        # SW tree has no eye icons
        "HideColumn": ("b", True),
        "HideInternalNames": ("b", True),
        "ResizableColumn": ("b", False),
        "CheckBoxesSelection": ("b", False),
        "FontSize": ("i", 0),
        "ItemSpacing": ("i", 1),
        "ItemBackgroundPadding": ("i", 0),
        "IconSize": ("i", 16),
        "TreeActiveColor": ("u", c("#DCE9F8")),
        "TreeEditColor": ("u", c("#FFE7B8")),
    },
    "DockWindows/TreeView": {"Enabled": ("b", False)},
    "DockWindows/PropertyView": {"Enabled": ("b", False)},
    "DockWindows/ComboView": {"Enabled": ("b", True)},
    # --------------------------------------------------------------- general
    "Mod/Start": {"ShowOnStartup": ("b", False), "FirstStart2024": ("b", False), "CloseStart": ("b", True)},
    "General": {
        "AutoloadModule": ("s", "FreeWorksWorkbench"),
        "RecentFiles": ("i", 10),
        "ToolbarIconSize": ("i", 24),
        "SubstituteDecimalSeparator": ("b", False),
    },
    "Units": {"UserSchema": ("i", 0), "Decimals": ("i", 2)},  # MMGS
    "Document": {
        "CreateBackupFiles": ("b", True), "CountBackupFiles": ("i", 1), "AutoSaveEnabled": ("b", True),
        "AutoSaveTimeout": ("i", 10), "SaveThumbnail": ("b", True), "ThumbnailSize": ("i", 256),
        "prefAuthor": ("s", ""),
    },
    # FreeCAD 1.1 theme system: built-in FreeCAD.qss + FreeWorks colour tokens
    "MainWindow": {"StyleSheet": ("s", "FreeCAD.qss"), "Theme": ("s", "FreeWorks")},
    "Themes": {"ThemeAccentColor1": ("u", c("#2F7BE5")), "ThemeAccentColor2": ("u", c("#CCE4F7")), "ThemeAccentColor3": ("u", c("#E8892B"))},
    "OutputWindow": {"checkShowReportViewOnError": ("b", False), "checkShowReportViewOnWarning": ("b", False)},
    "NotificationArea": {"NotificationAreaEnabled": ("b", True), "NonIntrusiveNotificationsEnabled": ("b", True)},
}

# Sketcher colors: SolidWorks (blue = under defined, black = fully defined,
# red = over defined, green relation symbols, black dimensions)
SKETCH_COLORS = {
    "SketchEdgeColor": "#1F5FD1", "SketchVertexColor": "#1F5FD1", "EditedEdgeColor": "#1F5FD1",
    "EditedVertexColor": "#1F5FD1", "CreateLineColor": "#1F5FD1",
    "FullyConstrainedColor": "#101010", "FullyConstraintElementColor": "#101010",
    "FullyConstraintConstructionElementColor": "#101010", "FullyConstraintInternalAlignmentColor": "#101010",
    "ConstructionColor": "#4A7FD8", "InternalAlignedGeoColor": "#4A7FD8", "ExternalColor": "#7A3FB0",
    "ExternalDefiningColor": "#7A3FB0", "InvalidSketchColor": "#D32F2F",
    "ConstrainedIcoColor": "#2E9E3A", "NonDrivingConstrDimColor": "#7A7A7A", "ConstrainedDimColor": "#101010",
    "ExprBasedConstrDimColor": "#9C27B0", "DeactivatedConstrDimColor": "#9E9E9E",
    "CursorTextColor": "#101010", "CursorCrosshairColor": "#5A5A5A",
    "SketchFaceColor": "#DDE9FA", "GridLineColor": "#C8D0DB", "GridDivLineColor": "#AAB4C2",
}


def _set(grp, k, typ, v):
    if typ == "b":
        grp.SetBool(k, v)
    elif typ == "i":
        grp.SetInt(k, v)
    elif typ == "f":
        grp.SetFloat(k, v)
    elif typ == "u":
        grp.SetUnsigned(k, v)
    elif typ == "s":
        grp.SetString(k, v)


def install_stylesheet():
    """Install the FreeWorks token file where FreeCAD's theme loader finds it
    (qss:parameters/<Theme>.yaml)."""
    dst_dir = os.path.join(App.getUserAppDataDir(), "Gui", "Stylesheets", "parameters")
    os.makedirs(dst_dir, exist_ok=True)
    src = os.path.join(THEME_DIR, "FreeWorks.yaml")
    if os.path.exists(src):
        shutil.copyfile(src, os.path.join(dst_dir, "FreeWorks.yaml"))


def projects_dir():
    """Documents\\FreeWorks - outside the installation, so updates and uninstall never touch it."""
    from PySide import QtCore
    try:
        docs = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
    except Exception:
        docs = ""
    return os.path.join(docs or os.path.expanduser("~"), "FreeWorks")


def guard_save_folder():
    """Never let File > Save default into the program folder or a temp folder
    (those are replaced by updates and removed by uninstall)."""
    g = P("General")
    cur = g.GetString("FileOpenSavePath", "")
    install = os.path.dirname(os.path.dirname(os.path.normpath(App.getHomePath())))
    bad = (not cur or not os.path.isdir(cur)
           or os.path.normcase(cur).startswith(os.path.normcase(install))
           or os.path.normcase(cur).startswith(os.path.normcase(os.path.normpath(App.getUserAppDataDir())))
           or os.path.normcase(cur).startswith(os.path.normcase(os.path.realpath(__import__("tempfile").gettempdir()))))
    if bad:
        d = params().GetString("ProjectsDir", "") or projects_dir()
        try:
            os.makedirs(d, exist_ok=True)
            g.SetString("FileOpenSavePath", d)
        except Exception:
            pass


def setup_projects_folder():
    fw = params()
    if fw.GetBool("ProjectsFolderSet", False):
        return
    d = projects_dir()
    try:
        os.makedirs(os.path.join(d, "Macros"), exist_ok=True)
    except Exception:
        return
    P("General").SetString("FileOpenSavePath", d)
    P("Macro").SetString("MacroPath", os.path.join(d, "Macros"))
    fw.SetString("ProjectsDir", d)
    fw.SetBool("ProjectsFolderSet", True)
    log("projects folder: %s" % d)


def apply(force=False):
    fw = params()
    try:
        setup_projects_folder()
    except Exception as e:
        log("projects folder: %s" % e)
    if not force and fw.GetInt("PrefsVersion", 0) >= PREFS_VERSION:
        install_stylesheet()
        return False
    for path, kv in SETTINGS.items():
        g = P(path)
        for k, (t, v) in kv.items():
            _set(g, k, t, v)
    for grp in ("View", "Mod/Sketcher/Colors", "Mod/Sketcher/View"):
        g = P(grp)
        for k, v in SKETCH_COLORS.items():
            g.SetUnsigned(k, c(v))
    # user choices made in FreeWorks Options win over the defaults above
    if fw.GetBool("HighQualityAA", False):
        P("View").SetInt("AntiAliasing", 3)
    if fw.GetBool("LargeModelMode", False):
        from .perf import LARGE
        P("View").SetInt("AntiAliasing", LARGE["AntiAliasing"])
        P("View").SetBool("UseNavigationAnimations", LARGE["UseNavigationAnimations"])
        P("Mod/Part").SetFloat("MeshDeviation", LARGE["MeshDeviation"])
        P("Mod/Part").SetFloat("MeshAngularDeflection", LARGE["MeshAngularDeflection"])
    install_stylesheet()
    fw.SetInt("PrefsVersion", PREFS_VERSION)
    log("preferences applied")
    return True
