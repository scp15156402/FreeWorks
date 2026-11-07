# 90 — Hidden interactions (modifier keys, drags, double-clicks, pointer cues)

The behaviour that SOLIDWORKS users rely on without thinking and that a look-alike misses.
Tags: [H] help "Time Saving Keyboard Shortcuts" 2016–2021, [B] Javelin 2014 (Peltier, CSWE),
GoEngineer, TriMech, SolidSmack, Solid Solutions; [K] known, unconfirmed.

## 90.1 Ctrl
| Gesture | Effect |
|---|---|
| Ctrl while sketching / after picking a point | **no automatic relations / inference** [H][B] |
| Ctrl+drag a sketch endpoint | suppresses inference lines while dragging [H] |
| **Ctrl+drag sketch entities** | copy them [B] |
| **Ctrl+drag a feature** (in the graphics area or **from the tree onto a face/edge**) | **copy the feature** there (e.g. a fillet onto a new edge, a hole to another face); works since 1997 and **from one part to another** [B Javelin, TriMech] |
| Ctrl+drag a component (graphics or tree) | copy the component [H][B] |
| Ctrl+drag a selection box in an assembly with components preselected | invert selection [H] |
| Ctrl+drag a note leader's arrowhead | add another leader [H] |
| Ctrl+drag a dimension | copy it (also to another drawing view) [B TriMech] |
| Ctrl+C / Ctrl+V | sketches: copy sketch entities; parts: copy a **sketch** onto a selected plane/face; assemblies: copy a part feature as an assembly feature [H][B] |
| Ctrl+Shift+Tab | show all hidden components transparent; click one to show it [H] |
| Ctrl+Shift+Alt (mates) | show all temporarily hidden faces semi-transparent [H] |
| Ctrl+click in Mirror Components | toggle *Create Opposite Hand Version* per item [B Javelin] |
| Ctrl + second planar face then Normal To | that face points up [B] |

## 90.2 Shift
| Gesture | Effect |
|---|---|
| **Shift while drawing a rectangle** | square [H] |
| Shift while sketching a line | snaps to specific lengths (increments) [H][B SolidSmack] |
| Shift+click | turns on snapping (sketch) [H]; in the tree selects the range between two items [H][B] |
| **Shift+drag a feature** | **move** it (e.g. a fillet or a hole from one face to another) [B Javelin] |
| Shift+drag an unconstrained feature / group of sketch entities | move it [B SolidSmack] |
| Shift+drag a dimension | move it to another drawing view [H] |
| **Shift held while picking** | select through transparency off (pick the transparent face) [H][B] |
| Shift+click an arc/circle with Smart Dimension | dimension to min/max [B] |
| Shift+MMB drag | zoom [H] |
| Shift+Tab | show components under the pointer; while inserting a component rotate −90° [H] |
| Shift+Alt (mates) | re-show a temporarily hidden face under the pointer [H] |
| Shift+arrow | rotate view 90° [B] |

## 90.3 Alt
| Gesture | Effect |
|---|---|
| **Alt+drag a component** | **SmartMate** (Tab flips alignment) [H][B] |
| **Ctrl+Alt+drag a component** | copy **and** SmartMate [H][B GoEngineer] |
| Alt+drag a triad's centre ball/handle onto an edge or face | align the triad to it (Move with Triad, Exploded View, Move/Copy Body …) [H][B] |
| Alt (hover a face) while mating | temporarily hide that face [H] |
| Alt+click | show a hidden body/component under the pointer [H] |
| Alt while inserting a component | rotate 90° [H 2018 "Alt+drag … While Inserting a Component"] |
| Alt+drag a spline handle | adjust both handles symmetrically [H] |
| Alt+drag an appearance from the Task Pane | opens the Appearances PM instead of applying directly [H] |
| Alt (sketch) | disable soft snapping; toggle selection of sketch contours [B GoEngineer] |
| Alt+drag a table in drawings | move the table from anywhere [H] |
| Alt+drag in the tree (assemblies) | move a part into/below a subassembly safely [B SolidSmack, GoEngineer] |
| Alt+MMB drag | roll view [B] |
| Alt+arrow | roll by the increment [B] |
| Alt+click a triad axis | rotate about it by the increment [B] |
| Alt+click the View Selector | select its back faces [H] |

## 90.4 Tab
- **Tab** over a component: hide it; **Shift+Tab** show components under the pointer; with
  Ctrl+Shift → show hidden transparent (see above). [H]
- Tab while inserting a component? (rotate); Tab flips SmartMate alignment while dragging; Tab
  flips forming-tool direction (sheet metal); **Tab changes the XYZ plane in a 3D sketch** [H];
  Tab moves between numeric input fields while sketching (Shift+Tab in 3D). [H]

## 90.5 Right-mouse button
- Right-click near the last pick: **OK** (green check cue) or **advance to the next selection box**
  (enter cue). [B TriMech]
- Right-drag: mouse gestures (parts, sketches, drawings); in assemblies right-drag on a component
  rotates it? (Alt+right-drag for gestures) [K]
- Right-click and drag in assemblies: copy/paste parts; in drawings copy/paste views. [H 2016]
- Right-click while placing a dimension locks its orientation. [B TriMech]
- In Select Other: right-click hides the face under the pointer. [B Javelin]

## 90.6 Double-click
- Double-click a dimension → Modify box. Double-click a feature (tree or face) → show its
  dimensions. Double-click a surface during Extrude → Up To Surface. Double-click the section line
  in a drawing → flip direction. Double-click a sketch-pattern instance count → edit it.
  Double-click a floating PM title → re-dock. Double-click a configuration → activate it.
  Double-click a tool (option *Single command per pick*) → keep the tool active. Double-click a
  view in the View Orientation dialog → apply. Double-click MMB → zoom to fit. [mix of H/B/K]

## 90.7 Dragging geometry
- Drag sketch geometry to change it (under-defined only); drag a dimension's arrow handles with
  Instant2D; drag feature faces/arrows with Instant3D; drag the rollback bar; drag features to
  reorder; drag a plane's edge with Ctrl to create an offset plane; drag planes' corner handles to
  resize; drag the section-view triad; drag pattern direction arrows/instance count handles; drag
  loft connectors; drag fillet control points along the edge. [K/H]

## 90.8 Pointer cues worth reproducing
Selection-type glyphs next to the pointer (face, edge, vertex, plane, axis, point, sketch
entity); relation glyphs while sketching; **RMB cue** icons (OK, enter/next box, hide); filter
funnel when a selection filter is on; ruler snap feedback on Instant3D drags; magenta highlight +
green line for rotate-about-entity; trim cursor; "no" cursor for illegal reorder drags. [K/B]
