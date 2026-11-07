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

## Memory and widget growth (P7 stress findings, FreeCAD 1.1.4, Xvfb/llvmpipe)
- Each sketch edit/exit leaves ~60 widgets behind **in plain FreeCAD too** (30 cycles: +1856 widgets).
  Upstream behaviour; the stress suite measures FreeWorks leaks only after the sketch stage.
- `View/AntiAliasing = 3` (MSAA 4x) grows RSS by ~8 MB per sketch edit (view buffers re-created);
  `1` (line smoothing) behaves like plain FreeCAD. Default is now 1; MSAA is an Options checkbox
  (`FreeWorks/HighQualityAA`). prefs.apply() keeps that choice and Large Model Mode across upgrades.
- Creating/closing 12 documents: plain FreeCAD +444, +146, +44 MB over three rounds (caches and
  allocator arenas, levels off). FreeWorks: +349, +151, +37. The suite checks the plateau (round 3).
- A stylesheet on the main window re-polishes every FreeCAD widget on each change; FreeWorks styles
  only its own widgets (`freeworks/style.py`).
- `QObject.findChildren()` over the whole main window costs 60-100 ms with ~3000 widgets; search
  direct children or known parents only.

## Assembly joints as SOLIDWORKS mates (verified in FreeCAD 1.1.4, P13/P14)
- Create a joint without the task panel: `jg = UtilsAssembly.getJointGroup(asm)`,
  `j = jg.newObject("App::FeaturePython", "Joint")`, `JointObject.Joint(j, JointTypes.index(t))`,
  `JointObject.ViewProviderJoint(j.ViewObject)`, set Distance/Angle, then
  `j.Proxy.setJointConnectors(j, [ref1, ref2])` (presolves and solves).
- Reference = `[component, [sub, sub_vertex]]`, built like FreeCAD's task: `resolveSubElement` →
  `fixBodyExtraFeatureInSub` → `getComponentReference(asm, root, sub)` → `findElementClosestVertex`
  → `addVertexToReference`.
- Grounding: `GroundedJoint(jg.newObject(...), link)` (CommandCreateJoint.createGroundedJoint needs
  an active assembly). Nothing moves on solve without a grounded part.
- Distance joint with 0: plane/plane = coincident face to face; round face/plane = **tangent**.
  Cylindrical joint on two cylinder faces = concentric. `Proxy.flipOnePart(j)` + solve = flip
  alignment. Fixed joint with whole-component refs (`[c, ["", ""]]`) and
  `Offset2 = P2.inverse() * P1` = SOLIDWORKS Lock (nothing moves).
- The active assembly must be in edit mode (`Gui.ActiveDocument.setEdit(asm)`) for FreeCAD's
  assembly commands; `UtilsAssembly.setJointsPickableState(doc, False)` while picking.
- `getStandardButtons` must return an int: `(sb.Ok | sb.Close).value` in PySide6.

## Collision detection and Replace Components (P17)
- Collision = `moving.common(other).Volume > 1e-3 mm^3` after a bounding-box prefilter; touching
  faces (coincident mates) give zero volume and don't count. Moves are sampled (0.5 mm / 2 deg) and
  the first hit is bisected. Collision moves are user commands (`@safe_slow`).
- `Part.getShape(link)` = component shape in assembly coordinates; `face.Surface` / `edge.Curve`
  of a sub-shape from `Part.getShape(comp, sub, needSubElement=True)` are already transformed.
- Replace: `link.LinkedObject = new`; references `[link, ["Tip.FaceN", same]]` re-pointed by
  matching (kind, position, direction, radius) in `Part.getShape(link)` (same element order as
  the body's Tip shape), then `Proxy.setJointConnectors`.

## Expressions / Equations (P26)
- FreeCAD's expression parser reads a bare `A` (and `C`, `K`, `s`, ...) as a **unit** (ampere,
  coulomb ...): `VarSet.A` fails to parse. FreeWorks stores global variables as `GV_<name>`.
- Sketch constraint expressions are stored in ExpressionEngine as `.Constraints.D1` (leading dot);
  `setExpression("Constraints.D1", ...)` works; constraints need a name (`renameConstraint`).
- `setExpression(prop, None)` on a property without an expression raises; check
  `prop in dict(obj.ExpressionEngine)` first.

## TechDraw (P18/P19)
- Templates: SVG with `freecad:editable="key"` (+ `freecad:autofill="title|author|date|scale|sheet|organization"`);
  an empty editable text should hold a non-breaking space so it stays clickable. Fill via
  `page.Template.EditableTexts` (dict).
- Defaults: `Preferences/Mod/TechDraw/Files` TemplateDir / TemplateFile.
- Scripted `DrawProjGroup` in 1.1.4: views render but the group stays at the page origin whatever
  X/Y is set to (before/after recompute, delayed). FreeWorks' Standard 3 View therefore places
  three `DrawViewPart` views itself. `XSource` (cross-document) needs both documents saved.

## Windows downloads (field test, v1.5.3)
- Windows PowerShell 5.1 defaults to TLS 1.0 (`ServicePointManager.SecurityProtocol` = Ssl3|Tls) and
  GitHub refuses it: "The underlying connection was closed: An unexpected error occurred on a send".
  Every published one-liner sets `[Net.ServicePointManager]::SecurityProtocol='Tls12'` first.
- The same error with TLS 1.2 forced means the connection is cut on the way: Indian ISPs (Jio, ACT,
  BSNL) block `raw.githubusercontent.com` from time to time; antivirus web shields can also reset it.
  `github.com`, `codeload.github.com` and `api.github.com` normally stay reachable.
- Fallback for text files: `https://api.github.com/repos/<repo>/contents/<path>?ref=<branch>` with
  header `Accept: application/vnd.github.raw` returns the raw file (content type
  `application/vnd.github.raw; charset=utf-8`; Invoke-WebRequest in 5.1 gives byte[] for it, decode
  as UTF-8). Unauthenticated limit 60 requests/hour/IP - fine as a fallback, not as the first choice
  (CGNAT shares IPs). jsDelivr (`cdn.jsdelivr.net/gh/<repo>@<branch>/<path>`) is the third choice;
  it caches branches for hours, so never trust its version alone.
- get.ps1 takes the version from the downloaded ZIP's package.xml, not from the check.
- Not testable in the sandbox: no PowerShell, and downloading it is not permitted. `dev/tests/pscheck.py`
  checks bracket balance; Windows behaviour is confirmed by the owner's field test.

## Sandbox constraint (Claude sessions)
Running third-party add-on code may be blocked in Claude's sandbox; test FreeWorks' own code
only, read add-on sources instead.
