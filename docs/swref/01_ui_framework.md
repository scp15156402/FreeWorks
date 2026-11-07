# 01 — UI framework

Confidence tags: **[H]** official help, **[B]** reseller blog / training material, **[F]** forum,
**[O]** the owner's own SOLIDWORKS 2026 settings export, **[K]** known SOLIDWORKS behaviour not
yet confirmed by a fetched source (verify before building).

## 1.1 PropertyManager (PM) anatomy

Where: the **PropertyManager tab** of the Manager Pane (left panel), replacing the
FeatureManager tab while a command runs. Opens automatically for commands that use it; whether it
also opens on plain selection is set in Tools > Options > System Options > General. [H]
(help r_pm_overview, 2013–2022)

Top to bottom:

| Part | What it is |
|---|---|
| Title bar | Feature icon + feature name, e.g. "Boss-Extrude1" (read-only). **Clicking the title bar shows the flyout FeatureManager design tree** in the graphics area (top-left, transparent, expandable) so tree items can be picked while the PM covers the tree. [H] |
| Buttons row | **OK** (green check: accept, execute, close), **Cancel** (red X: ignore, close), **Detailed Preview** (some PMs; older name Preview), **Help** (opens the help topic), **Keep Visible** (pushpin: PM stays open after OK for the next feature of the same type). Wizard PMs add **Back**, **Next**, **Undo**. [H] |
| Message box | Yellow box with an (i) icon at the top: what to select next, or errors/warnings. Collapsible. [H][K] |
| Group boxes | Titled groups (e.g. "Direction 1") with an expand/collapse chevron; some have a **checkbox in the title** that turns the whole group on (Direction 2, Thin Feature, Draft …). Unchecked → collapsed. [H] |
| Selection boxes | List boxes that receive picks from the graphics area or tree. **The active box is coloured** (pink in ≤2015 help; light blue in 2016+ UI — TriMech 2018 calls it "the blue selection box"). Picked items highlight in the graphics area when selected in the box. Right-click in a box: **Delete** (one item), **Clear Selections** (all). The box grows as items are added; drag its bottom handle to resize; right-click **Autosize** or double-click the handle to restore. [H][B] |
| Controls | Spin boxes (with up/down arrows, accept units and `=` equations with global variables/functions/file properties from a drop-down), combos, radio buttons, checkboxes, push buttons. [H] |

Keyboard inside a PM: **Tab** moves between controls, **Space** toggles checkboxes and presses
buttons, **arrow keys** move between radio buttons. **Enter = OK, Esc = Cancel.** [H]

Layout: the PM opens at "optimum width"; drag the divider to resize — it **snaps** to the optimum
width. A **split bar** at the top of the Manager Pane splits it into two panels showing any
combination of PropertyManager / FeatureManager / ConfigurationManager / add-in tabs; double-click
the split bar to return to one panel. **Floating:** drag the title bar off; docking icons appear
(dock upper-left as a tab, upper-left in the graphics area, lower-left, lower-right);
double-click a floating PM's title bar to return it to its last dock. [H]

"The PropertyManager remembers its last used state" — e.g. Fillet reopens with the last type,
radius and options. [H] (Fillet help 2012–2025)

## 1.2 Accepting and cancelling (all PMs and sketches)

[H] help "Accepting Features" (2011–2020), [B] Javelin 2012, TriMech 2018:

- **OK / Cancel** buttons in the PM; **Enter / Esc**.
- **Confirmation Corner** (top-right of the graphics area): OK / Cancel while a PM is open;
  **Exit Sketch / Cancel Sketch** (discard changes) while a sketch is open. Can be turned off:
  System Options > General > Enable Confirmation Corner.
- **D** moves the Confirmation Corner buttons to the pointer (press D again to send them back);
  with no PM/sketch open, D moves the **selection breadcrumbs** to the pointer. D is the default
  key unless D is assigned to another command (the owner assigned **D = Smart Dimension** [O],
  so in the owner's setup D does *not* do this).
- **Right-click → OK / Cancel** at the top of the graphics-area shortcut menu.
- **Right-mouse-button cue:** right after a pick, a small mouse icon appears next to the pointer
  with a symbol over the right button. **Green check = right-click accepts (OK). "Enter" arrow =
  right-click moves to the next selection box** (e.g. Mirror: pick entities → right-click → the
  next box ("Mirror about") becomes active → pick centerline → right-click = OK). The cue only
  shows while the pointer stays **within a small radius of the last pick**; moving away hides it
  and right-click then opens the normal menu. [B]
- After a preview: "Right-click when the pointer changes to [OK cue] to accept the preview, or
  click [cue] to return to the preview without accepting". [H]

## 1.3 Window layout (SOLIDWORKS 2024–2026)

Top to bottom [K unless marked; owner runs **Simplified Interface** + dark theme [O]]:
- **Menu bar** (title strip): SOLIDWORKS logo/menu flyout (pin it to show File, Edit, View,
  Insert, Tools, Window, Help as a classic menu), **Quick Access** tools (New, Open, Save, Print,
  Undo, Redo, Select, Rebuild, File Properties, Options), document name, **search box**
  (Search Commands / Help / Files and Models), help flyout, user/3DEXPERIENCE. [H "Displaying
  the Quick Access Tools": shown in the Menu Bar or on the left of the CommandManager]
- **CommandManager**: context tabs — Part: **Features · Sketch · Markup · Evaluate · MBD
  Dimensions · SOLIDWORKS Add-Ins · MBD · Analysis Preparation** (+ Sheet Metal, Weldments,
  Mold, Surfaces, Direct Editing when enabled); Assembly: **Assembly · Layout · Sketch · Markup
  · Evaluate · …**; Drawing: **Drawing · Annotation · Sketch · Markup · Evaluate · Sheet
  Format**. Buttons with text below icons ("Use Large Buttons with Text"), flyouts with ▾.
  Right-click a tab > **Tabs** (show/hide), **Use Large Buttons with Text**, **Customize
  CommandManager**. Simplified Interface shows an abridged set [O].
- **Graphics area** with, overlaid: **FeatureManager flyout** (when a PM covers the tree),
  **Heads-up View toolbar** (top centre), **Confirmation Corner** (top right while a PM/sketch is
  open), **Selection breadcrumbs** (top left when something is selected), **reference triad**
  (bottom left), optional **View Cube** (owner: off [O]).
- **Manager Pane** (left): tabs **FeatureManager design tree · PropertyManager ·
  ConfigurationManager · DimXpertManager · DisplayManager** (+ add-ins: CAM, Simulation …);
  2026 lets you choose which tabs appear (customizable Manager Pane tabs). **F9** toggles the
  pane. A split bar divides it into two panels. [H r_pm_overview]
- **Task Pane** (right, collapsible): SOLIDWORKS Resources, Design Library, File Explorer, View
  Palette, Appearances/Scenes/Decals, Custom Properties, 3DEXPERIENCE; Import Model (2026).
  Pushpin keeps it open; otherwise it auto-hides when the pointer leaves.
- **Status bar** (bottom): description of the hovered tool / measured info for the selection
  (length of an edge, area of a face, distance between two picks), pointer XYZ in sketches,
  sketch status, "Editing Part/Sketch …", **unit system** button (click → MMGS/IPS/… list and
  Edit Document Units), rebuild indicator, quick tips toggle. [K]

## 1.3a CommandManager tab contents (default, non-simplified) [K — verify against a 2026 screenshot list]
Order left→right; "▾" = flyout; **|** = separator.
- **Features** (part): Extruded Boss/Base · Revolved Boss/Base · Swept Boss/Base · Lofted
  Boss/Base · Boundary Boss/Base **|** Extruded Cut · Hole Wizard ▾ (Hole Wizard, Advanced Hole,
  Thread, Stud Wizard) · Revolved Cut · Swept Cut · Lofted Cut · Boundary Cut **|** Fillet ▾
  (Fillet, Chamfer) · Linear Pattern ▾ (Linear, Circular, Mirror, Curve Driven, Sketch Driven,
  Table Driven, Fill, Variable) · Rib · Draft · Shell · Wrap · Intersect · Mirror **|** Reference
  Geometry ▾ (Plane, Axis, Coordinate System, Point, Center of Mass, Bounding Box, Mate Reference) ·
  Curves ▾ (Split Line, Projected, Composite, Through XYZ Points, Through Reference Points, Helix
  and Spiral) · **Instant3D** (toggle).
- **Sketch**: Sketch (enter/exit) · 3D Sketch ▾ **|** Smart Dimension ▾ · Line ▾ (Line,
  Centerline, Midpoint Line) · Rectangle ▾ (5 types) · Slot ▾ (4 types) · Circle ▾ (Circle,
  Perimeter Circle) · Arc ▾ (Centerpoint, Tangent, 3 Point) · Polygon · Spline ▾ (Spline, Style
  Spline, Spline on Surface, Equation Driven Curve) · Ellipse ▾ (Ellipse, Partial Ellipse,
  Parabola, Conic) · Sketch Fillet ▾ (Fillet, Chamfer) · Text · Plane · Point **|** Trim Entities ▾
  (Trim, Extend) · Convert Entities ▾ (Convert, Intersection Curve, Silhouette Entities) · Offset
  Entities ▾ (Offset, Offset on Surface) · Mirror Entities · Linear Sketch Pattern ▾ (Linear,
  Circular) · Move Entities ▾ (Move, Copy, Rotate, Scale, Stretch) **|** Display/Delete Relations ▾
  (Display/Delete, Add Relation, Fully Define Sketch?) · Repair Sketch · Quick Snaps ▾ · Rapid
  Sketch · Instant2D · Shaded Sketch Contours.
- **Evaluate**: Design Checker ▾ · Measure · Markup · Mass Properties · Section Properties ·
  Sensor · Performance Evaluation · Check · Import Diagnostics · Deviation Analysis · Zebra
  Stripes · Curvature · Draft Analysis · Undercut Analysis · Parting Line Analysis · Thickness
  Analysis · Symmetry Check · Compare Documents · Check Active Document · Equations? · Costing ·
  Sustainability. (Assemblies add Interference Detection, Clearance Verification, Hole Alignment,
  AssemblyXpert.)
- **Assembly**: Insert Components ▾ (Insert Components, New Part, New Assembly, Copy with Mates)
  · Mate · Component Preview Window · Linear Component Pattern ▾ (Linear, Circular, Pattern
  Driven, Sketch Driven, Curve Driven, Chain, Mirror Components) · Smart Fasteners · Move
  Component ▾ (Move, Rotate) · Show Hidden Components **|** Assembly Features ▾ · Reference
  Geometry ▾ · New Motion Study · Bill of Materials · Exploded View ▾ (Exploded View, Explode Line
  Sketch) · Instant3D · Update Speedpak · Take Snapshot · Large Assembly Mode / Large Design Review.
- **Drawing**: Model View · Projected View · Auxiliary View · Section View · Detail View · Broken-out
  Section · Break · Crop View · Alternate Position View **|** Standard 3 View … ; **Annotation**:
  Smart Dimension ▾ · Model Items · Spell Checker · Format Painter · Note · Linear Note Pattern ·
  Balloon · Auto Balloon · Magnetic Line · Surface Finish · Weld Symbol · Hole Callout · Geometric
  Tolerance · Datum Feature · Datum Target · Blocks · Center Mark · Centerline · Area Hatch/Fill ·
  Revision Symbol / Cloud · Tables ▾.
- Hovering a button shows a **large tooltip** (name, description, small picture; owner has large
  tooltips on [O]); flyout arrows open on click; **the flyout button keeps the last used command
  on its face** (Rectangle/Circle/Arc "default to the last used type"). [H for arcs/circles/rectangles]

## 1.4 Context toolbars  [H 2011–2023, B SOLIDWORKS blog 2009, Solid Solutions]

- Appear **when items are selected in the graphics area or FeatureManager** and **on top of the
  right-click shortcut menu**. Introduced 2008 (parts/assemblies), drawings 2010.
- Behaviour like Office's mini toolbar: **appears semi-transparent, becomes opaque when the
  pointer moves onto it, fades/disappears when the pointer moves away**.
- **Buttons are hard-coded per selection type and cannot be customised**; they are the most
  common shortcut-menu commands.
- Right-click while it is shown → the rest of the shortcut menu for that item.
- Options (Tools > Customize > Toolbars > Context toolbar settings): **Show on selection** ·
  **Show in shortcut menu** (both cleared → commands appear as text in the shortcut menu) ·
  **Show quick configurations** · **Show quick mates** · **Show flip alignment and lock rotation
  after quick mates** · **Show OK button** (Quick Mates: Add/Finish Mate for coincident,
  concentric, parallel, symmetric, tangent).
- Keyboard: Shift+F10 or the menu key opens the shortcut menu; arrows navigate; Enter runs; Esc
  dismisses (a context toolbar on its own has no keyboard navigation). [H 2022–2023]
- Bottom row includes **Zoom to Selection** (magnifier with =) — handy after picking a feature
  in the tree. [B Solid Solutions]
- Typical contents [K — to verify per selection type in a later pass]:
  - *Planar face*: Edit Feature · Edit Sketch · **Sketch** · Hide/Show body · Isolate ·
    Appearance · **Normal To** · Zoom to Selection · Measure / Section View / Select Other.
  - *Edge*: Edit Feature · Edit Sketch · **Fillet** · **Chamfer** · Hide/Show · Appearance ·
    Select Tangency / Select Loop.
  - *Feature in tree*: Edit Feature · Edit Sketch · **Suppress / Unsuppress** · **Rollback** ·
    Hide/Show · Appearance · Zoom to Selection.
  - *Sketch in tree*: Edit Sketch · Hide/Show · Zoom to Selection.
  - *Plane*: **Sketch** · Edit Feature · Hide/Show · **Normal To** · Zoom to Selection.
  - *Sketch entities in a sketch*: valid **Add Relations** icons + Construction Geometry +
    Smart Dimension (+ "Make Path", "Mirror" etc. depending on selection).
  - Evidence found in text (screenshots could not be viewed — image fetches fail and no browser
    was available): component → **Hide Components / Show Components** (both shown when the
    selection mixes states, 2024+), **Change Transparency**, **Component Properties**, Isolate;
    right-click the top assembly → **Top Level Transparency**; **Isolate pop-up toolbar**:
    Wireframe / Transparent / Hidden, Save as Display State, Exit Isolate; planes → Hide/Show
    toggle; face → Edit Feature (FeatureWorks on imported faces). [H 2012–2024, B Javelin 2026,
    3DSwym wiki]
  - *Component (assembly)*: Edit Part / Open Part · Hide/Show · Change Transparency · Isolate ·
    Rebuild · **Quick Mates** row when two entities from different components are selected.

## 1.5 Shortcut menus (right-click) [K]
- Graphics area, **nothing selected**: context toolbar of *Previous Selection* etc. on top,
  then Select Other, Zoom/Pan/Rotate (Zoom to Fit, Zoom to Area, Zoom In/Out, Rotate View, Pan,
  Roll View), Recent Commands, Insert Sketch?, Comment, Customize Menu.
- **While a PM is open**: **OK** and **Cancel** at the top, then items relevant to the active
  selection box (Clear Selections, Delete), view commands, Recent Commands.
- Menus are **truncated**: "▾" at the bottom expands to all items; **Customize Menu** lets the
  user tick which items show.
- **Select Other** (right-click a face): hides that face and shows a **pick list** of the faces
  behind it; hover highlights; the pointer shows a mouse icon whose **right button = Hide** —
  right-click more faces to hide them; Esc restores. [B Javelin 2016, GoEngineer cheat sheet]

## 1.6 Selection breadcrumbs  [B Javelin 2024–2025, H 2016 "D key"]
- Appear **top-left of the graphics area** when something is selected; show the selection in
  context: the face → its feature → the feature's **sketch** → body → part → **mates** of the
  part → parent assemblies up to the top level (assemblies: far left).
- **Every crumb is selectable** (and has its own context toolbar / right-click).
- **D** moves the breadcrumbs to the pointer when no PM/sketch is open (owner rebinds D [O]).

## 1.7 Shortcut bars (S key)  [B Javelin, GoEngineer 2015]
- **S** pops a **shortcut bar** at the pointer: a user-customisable toolbar per context —
  Part, Assembly, Drawing, **Sketch** — with a **command search box** at the top (2016+).
  Customised in Tools > Customize > **Shortcut Bars** (drag commands onto it). Disappears on
  Esc, after a command, or when the pointer moves away.
- Owner rebinds S to command #33513 [O] (to identify).

## 1.8 Mouse gestures  [B Javelin 2025, owner settings [O]]
- Hold the **right mouse button and move slightly** → a **gesture guide ring** appears with 2,
  3, 4, 8 or 12 commands around it (Tools > Customize > Mouse Gestures: count, per-context
  assignments for Part, Assembly, Drawing, Sketch). Drag toward a slot → the slot highlights and
  the command runs on release. A plain right-click (no move) still opens the shortcut menu.
- In assemblies right-drag on a component rotates it; **Alt + right-drag** gives gestures. [K]
- Owner configuration (Guide type 3, i.e. 8 gestures) [O]:
  - Part/assembly: L=Left, R=Right, U=Top, D=Bottom, UL=Front, UR=Trimetric, DR=Zoom to Area(?),
    DL=Back.
  - Sketch: L=Circle, R=Center Rectangle, U=Smart Dimension, D=Line, UL=Convert Entities,
    UR=Sketch (exit), DR=Sketch Fillet, DL=Trim.

## 1.9 Keyboard  [K defaults; O owner overrides]
Defaults: **S** shortcut bar · **F** zoom to fit · **Space** View Orientation dialog / View
Selector · **Ctrl+Space** View Selector · **Ctrl+1…8** Front, Back, Left, Right, Top, Bottom,
Isometric, Normal To · **Ctrl+Shift+Z** previous view · **Shift+Z** zoom in, **Z** zoom out ·
arrows rotate 15° (Shift+arrow 90°, Alt+left/right roll, Ctrl+arrow pan) · **Ctrl+B** rebuild ·
**Ctrl+Q** force rebuild · **Ctrl+R** redraw · **R** recent documents · **Q** temporarily show
planes/origins/coordinate systems · **D** confirmation corner / breadcrumbs to pointer · **E / V
/ X** edge / vertex / face selection filters · **F5** selection filter toolbar · **F6** toggle
filters · **Enter** repeat last command · **Tab / Shift+Tab / Ctrl+Shift+Tab** hide / show /
show hidden components under the pointer · **Alt** (hover) hide faces? · **W** search commands
· **H** help · **I** file search · **F9** toggle Manager Pane, **F10** toggle toolbars, **F11**
full screen · Ctrl+C/V/X/Z/Y, Ctrl+N/O/S/P/W, Ctrl+Tab next document, Ctrl+F4 close.
More defaults from shortcut lists [B scribd/GrabCAD lists, unverified individually]: **F3 Quick
Snaps** (View > Quick Snaps), F7 spell checker, F8 Display Pane, Shift+F3 toggle note upper case,
**Ctrl+F1 Task Pane**, **T Select over Geometry**, **C expand/collapse tree**, End = scroll tree
to bottom, Shift+F10 shortcut menu.
Owner overrides: C Circle, D Smart Dimension, E Extruded Boss/Base, F Fillet, M Measure, R
Corner Rectangle, T Trim, X #33094 (replaced Filter Faces; unidentified), and **S = command
#33513, the same command as the default F3 → Quick Snaps** (so in the owner's SOLIDWORKS, S
does not open the shortcut bar) [O + lists].

## 1.10 Heads-up View toolbar  [H 2012–2019 View toolbar, owner list O]
Transparent toolbar at the top centre of every viewport: **Zoom to Fit · Zoom to Area ·
Previous View · Section View · Dynamic Annotation Views · View Orientation (flyout: standard
views, Normal To, Single view / Two view / Four view layouts, Link views, View Selector toggle)
· Display Style (Shaded With Edges, Shaded, Hidden Lines Removed, Hidden Lines Visible,
Wireframe) · Hide/Show Items (planes, axes, origins, sketches, sketch relations, dimensions,
annotations, lights, cameras …) · Edit Appearance · Apply Scene · View Settings (RealView,
Shadows in Shaded Mode, Ambient Occlusion, Perspective, Cartoon) · Rotate View?** Simplified
Interface hides appearances/scenes/view settings [O summary]. Customisable via right-click.
