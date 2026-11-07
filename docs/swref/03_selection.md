# 03 — Selection

Tags: [H] help, [B] blog/training, [O] owner, [K] known, unconfirmed.

## 3.1 Picking and highlighting
- **Dynamic highlight** (pre-selection): faces, edges, vertices highlight as the pointer moves
  over them; the pointer shows a small glyph for the entity type (face/edge/vertex/plane/axis/
  sketch point …). [K]
- Click selects (replaces); **Ctrl+click** adds/removes (toggle); **Shift+click** is also used to
  add in many contexts [K]; click empty space clears. Selected items take the selection colour
  (blue in the default/2016+ theme). [B Javelin 2026: "highlighted in blue"]
- Hold **Shift** while picking to **not select through transparency** (temporarily). [B
  GoEngineer cheat sheet]
- **Selection breadcrumbs** and the **context toolbar** appear on each pick (see 01).
- **Right-click "advance pointer"**: right-click in the graphics area advances to the next PM
  selection box when several are needed (RMB cue icon). [H 2015 Selection Overview]

## 3.2 Box, cross and lasso  [H 2010–2026, B Engineers Rule, Javelin 2026, CATI]
- **Left → right drag = Box (window) selection**: only items **completely inside** — box is
  **blue/light blue with a solid outline**.
- **Right → left drag = Cross selection**: items **inside or crossing** — box is **green with a
  dashed outline**.
- Box selection must start in **empty space**, unless **Select over Geometry** (Select flyout)
  is on.
- Each document type has a **default entity type** for box selection (parts: edges; assemblies:
  components; sketches: sketch entities; drawings: dimensions/annotations …); other types need
  **selection filters**. Shift/Ctrl modify a box selection (add/toggle) and leave prior
  selections outside the box unchanged. Hidden edges selectable per System Options > Selection.
  [B Javelin 2026]
- **Lasso Selection** (Select flyout): freehand loop, need not be closed. **Clockwise = blue,
  only enclosed items; counter-clockwise = green, enclosed + crossing** (counter-clockwise only in
  drawings and sketches). [H 2016–2026, 2025 tutorial]
- **Select flyout** (Standard toolbar, Select ▾): Select · Box Selection · Lasso Selection ·
  Select over Geometry · Select All (Ctrl+A) · Invert Selection · Select Identical? · Select
  Hidden/Suppressed/Internal components (assemblies; "internal" checked from 6 orthogonal
  directions) · Volume Select · Assembly Visualization · Selection Manager. [H 2026]
- **Selection context toolbar**: right-click **empty space** in a part/assembly → a toolbar of
  common selection tools above the shortcut menu (e.g. Previous Selection, Select Other, Invert
  Selection, Select All …). [H 2022]

## 3.3 Contextual selection (right-click)  [B GoEngineer 2023, dezignstuff, fpgdesign]
- **Select Loop** — right-click an edge of a face; arrow on the edge flips which loop (every
  edge belongs to two loops).
- **Select Tangency** — right-click a face or edge with tangent neighbours.
- **Select Chain** — right-click a sketch segment connected to others.
- **Select Partial Loop** — pick the first edge, right-click the last edge (on the side of its
  midpoint toward the wanted direction) → edges between.
- **Select Open Loop / Select Open Tangency** — open edges of surface bodies.
- **Select Other** — see 01 §1.5 (hides the face under the pointer, pick list of faces behind;
  RMB = hide more faces; "Temporarily hide faces: RMB while Select Other is active").
- **Select Midpoint** — right-click an edge → selects its midpoint (for mates/sketch relations).
  [K]
- **Select Connected Faces** pop-up toolbar (right-click a face) — hover images to preview
  (e.g. All co-planar …) and click one. [H 2014–2016]

## 3.4 Selection filters  [B GoEngineer 2023, Engineers Rule]
- **F5** shows/hides the **Selection Filter toolbar**; **F6** toggles filtering on/off (only if
  some filter is on); **E** edges, **X** faces, **V** vertices toggle their filters (owner rebinds
  E and X [O]).
- Filters stay active until turned off; the **pointer shows a funnel** when a filter is active.
  "If SOLIDWORKS suddenly refuses to select a face, a filter is probably still on." [B]
- Toolbar buttons: Toggle Selection Filter Toolbar · Toggle Selection Filters · Clear All Filters
  · Select All Filters · Invert Filters · then per type: Vertices, Edges, Faces, Surface Bodies,
  Solid Bodies, Axes, Planes, Sketch Segments, Sketch Points, Center Marks, Centerlines,
  Dimensions, Surface Finish, Geometric Tolerances, Notes/Balloons, Weld Symbols, Datum
  Features/Targets, Cosmetic Threads, Blocks, Spot Welds, Routing points, Mid points? … [K]
- SOLIDWORKS 2026 adds **feature and component selection filters** and lets filters be assigned
  to shortcuts. [summary of earlier What's New research]

## 3.5 Selecting in the FeatureManager
- Click a feature → it highlights in the graphics area (dynamic highlight of the feature's
  faces); context toolbar appears; **Zoom to Selection** brings it into view.
- Hovering a tree item highlights its geometry (FeatureManager option *Dynamic highlight*). [K]
- Selecting reference geometry: planes/axes/origins can be picked in the graphics area when
  visible, or from the tree (also from the **flyout tree** while a PM is open). [K]
