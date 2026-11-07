# FreeCAD 1.1 internals verified while building FreeWorks

Everything here was checked against FreeCAD 1.1.4 (Linux AppImage, PySide6). Re-verify after
a FreeCAD upgrade (see UPDATE_PROTOCOL.md).

## Paths and profile
- `FREECAD_USER_HOME=<dir>` puts user data *and* config directly in `<dir>` (`<dir>/Mod`,
  `<dir>/user.cfg`, `<dir>/icons`, `<dir>/Gui/Stylesheets`). The Windows launcher sets it to
  `D:\FreeWorks\UserData`.
- Branding: `branding.xml` + images next to the executable (`bin/`) changes window title, icon
  and splash (verified: title becomes "FreeWorks - FreeCAD 1.1.4").

## Icons
- `QDir.searchPaths("icons")` order: `<install>/icons`, `<UserData>/icons`, `:/icons/`, …
  → SVGs named like FreeCAD pixmaps (e.g. `PartDesign_Pad.svg`) in `<UserData>/icons`
  override toolbar **and tree** icons, provided they exist before the icon is first cached.
- `Gui.addIcon(name, …)` fails for already-registered names ("Icon with this name already registered").

## Theme
- 1.1 uses `FreeCAD.qss` + token files `qss:parameters/<Theme>.yaml`. FreeWorks sets
  `MainWindow/StyleSheet=FreeCAD.qss`, `MainWindow/Theme=FreeWorks` and installs
  `<UserData>/Gui/Stylesheets/parameters/FreeWorks.yaml`.
- Our own widget styles are set on the main window (`mw.setStyleSheet`) so they survive
  FreeCAD re-applying the application stylesheet.

## Docks
- Tasks (task panel) starts as an **overlay** (`User parameter:BaseApp/MainWindow/DockWindows/OverlayRight`
  `Widgets="Tasks,"`), parent `Gui::OverlaySplitter` → reparent to the main window,
  `addDockWidget(Left)`, `tabifyDockWidget(Model, Tasks)`, hide empty `Gui::OverlayTabWidget`.
- `DockWindows/TreeView/Enabled` and `DockWindows/PropertyView/Enabled` create separate docks –
  keep them False (combo view "Model" dock is used).
- Dock object names: `Model`, `Tasks`, `Report view`, `Python console`, `Selection view`.

## 3D view
- `Gui::View3DInventor` → child `Gui::View3DInventorViewer` (a `QGraphicsView`) → its
  `viewport()` is a `QOpenGLWidget` (shiboken types it as plain `QWidget`; compare
  `metaObject().className()`, not `isinstance`). Mouse events arrive on the viewport; keys on the viewer.
- Translucent top-level windows render black without a compositor → overlays (gesture wheel)
  are child widgets of the main window.
- Navigation style name: `Gui::SolidWorksNavigationStyle`.

## Commands / shortcuts
- `Gui.Command.get(name).getAction()` returns `[]` for commands not placed in any menu/toolbar;
  use `isActive()` to compute enabled state.
- Hidden menus/toolbars: re-add command QActions to the main window (`mw.addAction`) to keep
  their shortcuts alive.
- Clearing shortcuts: `Gui.Command.get(c).setShortcut("")` (persists in user.cfg).
- Python workbench `ContextMenu(recipient)` items are appended *after* FreeCAD's standard
  items; FreeWorks reorders the live `QMenu` (`contextmenu.reorganize`).

## Preferences (names verified with `strings libFreeCADGui.so`)
- Light: `View/LightSources`: `EnableHeadlight/FillLight/Backlight`, `HeadlightIntensity`,
  `FillLightIntensity`, `BacklightIntensity`, `AmbientLightIntensity`.
- Start page: `Mod/Start/ShowOnStartup`, `FirstStart2024`.
- Tree: `TreeView/VisibilityIcon`, `TreeActiveColor`, `TreeEditColor`.

## Objects
- Body origin features have `Role` (`XY_Plane`, `XZ_Plane`, `YZ_Plane`, `X_Axis`, …).
- PartDesign features have `Suppressed`; sketches expose `FullyConstrained`, `DoF`,
  `ConflictingConstraints`, `RedundantConstraints`, `MalformedConstraints`.
- Assembly document object `Assembly::AssemblyObject` with `Assembly::JointGroup`.

## Add-on facts (read from source, not executed)
- SheetMetal workbench key `SMWorkbench`; commands `SheetMetal_AddBase/AddWall/AddFoldWall/AddBend/
  AddCornerRelief/AddJunction/AddRelief/AddHem/AddCutout/Extrude/FromSolid/Forming/Unfold/SketchOnSheet`.
- Fasteners key `FastenersWorkbench`; `Fasteners_Search`, `Fasteners_BOM`; per-part commands `FS<type>`.
- Curves key `CurvesWorkbench`; `ZebraTool`, `Curves_SurfaceAnalysis`, `Curves_DraftAnalysis`.

## Sandbox constraint (Claude sessions)
Running third-party add-on code may be blocked in Claude's sandbox; test FreeWorks' own code
only, read add-on sources instead.
