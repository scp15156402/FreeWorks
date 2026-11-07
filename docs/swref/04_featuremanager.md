# 04 — FeatureManager design tree

Tags: [H] help, [B] blog/training, [O] owner, [K] known, unconfirmed.

## 4.1 Default part tree (top to bottom) [K]
`Part1 (Default<<Default>_Display State 1>)` · **History** (2016+, recent features) ·
**Sensors** · **Annotations** · **Solid Bodies(n)** / **Surface Bodies(n)** (appear when present) ·
**Equations** (when present) · **Material <not specified>** · **Front Plane** · **Top Plane** ·
**Right Plane** · **Origin** · features in creation order … · rollback bar at the end.
Owner's Simplified Interface tree shows Equations, Material, Planes, Origin [O summary].
Visibility of each folder: System Options > FeatureManager > **Hide/show tree items** — per item
*Automatic* (show if present) / *Hide* / *Show* (Blocks, Design Binder, Annotations, Solid
Bodies, Surface Bodies, Tables, Favorites, Default Planes, Mate References, Design Table,
Equations, Material, Sensors, History …). Right-click in the tree > Hide/Show Tree Items opens
it. [H]

## 4.2 Node states and prefixes [K]
- Sketch status prefix: **(-)** under defined, **(+)** over defined, **(?)** not solved; none =
  fully defined.
- **Errors**: red ✖ on the node (and parents) — rebuild failures; **warnings**: yellow ⚠
  triangle. Hover shows the message; **What's Wrong** dialog (right-click > What's Wrong, or the
  rebuild-error dialog shown after a failing rebuild with *Continue*/*Stop and Repair*) lists
  type, feature, description, with Show/Hide warnings and *Show error/warning icons*. Option
  *Display warnings: Always / Never / In top-level only*. [H 2011 "Display warnings"]
- **Suppressed** features greyed; rolled-back features greyed below the bar.
- **External references**: `->` (in context), `->?` (out of context), `->*` (locked), `->x`
  (broken). [B Essentials quick reference]
- Absorbed sketches nested under their feature (expand arrow); **shared** sketches appear under
  each user. Feature icon per type.
- Equations-driven dimensions show Σ; linked values show 🔗 (in dimensions, not in the tree).

## 4.3 Interaction [H 2011–2025 options, K behaviours]
- **Click** selects (geometry highlights in the graphics area; context toolbar appears).
  **Dynamic highlight**: hovering a tree item highlights its edges/faces/planes/axes. [H]
- **Double-click a feature** → shows its dimensions in the graphics area (Instant3D editing);
  double-click a dimension → Modify. [K]
- **Slow double-click** (click-pause-click) renames; **F2** renames (option *Edit name with slow
  double click*). **Name feature on creation** option puts the new feature's name in edit mode.
  [H]
- **Drag and drop** to **reorder** features (cursor shows a reorder arrow; not allowed before a
  parent → "no" cursor). Drag into a folder; right-click > **Add to New Folder**. [K]
- **Rollback bar** (yellow/blue line at the end): drag up/down, or right-click a feature >
  **Rollback**; right-click the bar > **Roll to Previous** / **Roll to End** / **Roll Forward**;
  **arrow keys move it** when it is selected (with Arrow key navigation on); new features insert
  at the bar; the model can be saved rolled back. [H 2011 arrow-key table, K rest]
- **Arrow key navigation** (with the pointer in the tree): up/down scroll, left/right collapse/
  expand an item (at the top item: the whole tree), up/down move the rollback bar when it is
  selected. [H 2011]
- **Scroll selected item into view**: picking in the graphics area scrolls the tree to the
  feature; when cleared, right-click in graphics > **Go To Feature (in Tree)**. [H]
- **Tree filter** box at the top (*Enable FeatureManager tree filter*): type to filter by name
  (and by feature type, component, tags…). [H]
- **Flyout FeatureManager**: while a PM is open, a copy of the tree appears top-left of the
  graphics area (click the PM title to toggle); *Use transparent flyout FeatureManager tree in
  parts/assemblies* makes it transparent. [H]
- **F9** toggles the Manager Pane; **Ctrl+T**? flat tree view in assemblies [K].
- Right-click a feature: **Edit Feature** · **Edit Sketch** · **Suppress / Unsuppress** (with
  *This configuration / All / Specify* in multi-config parts) · **Rollback** · **Parent/Child…**
  (dialog listing parents and children) · **Feature Properties…** (name, description, created by,
  dates, **Suppressed** per configuration) · **Configure Feature** · **Hide/Show** · **Appearance**
  · **Delete** (dialog with *Delete absorbed features*, *Delete child features*, *Don't ask*) ·
  **Add to Favorites** · **Comment** · **Go To…** · **Collapse Items** · **Hide/Show Tree Items**
  · **Customize Menu**. [K]
- Ctrl+Q force rebuild, Ctrl+B rebuild; rebuild indicator on the tree after changes. [K]
- **Freeze bar** (optional, System Options > General > *Enable Freeze bar*): drag to lock
  features above it from rebuilding. [K]

## 4.4 Manager Pane tabs and splitting  [H r_pm_overview]
FeatureManager · PropertyManager · ConfigurationManager · DimXpertManager · DisplayManager (+
add-in tabs). Split bar for two panes. F9 toggles. 2026: customise which tabs appear. Owner's
dark theme colours the pane accordingly [O].

## 4.5 Feature naming conventions (SOLIDWORKS defaults) [K]
Sketch1…, Boss-Extrude1, Cut-Extrude1, Revolve1, Cut-Revolve1, Sweep1, Cut-Sweep1, Loft1,
Cut-Loft1, Boundary-Loft1?, Fillet1, Chamfer1, Shell1, Draft1, Rib1, Dome1, LPattern1,
CirPattern1, Mirror1, Fill Pattern1, CrvPattern1, Sketch Pattern1? (SketchPattern1), TPattern1,
VarPattern1, Plane1, Axis1, Coordinate System1, Point1, CBORE for …, M6x1.0 Tapped Hole1,
Split Line1, Helix/Spiral1, Composite Curve1, Combine1, Body-Move/Copy1, Delete/Keep Body1,
Thicken1, Surface-Extrude1, Surface-Knit1 … (FreeWorks already maps many in naming.py.)
