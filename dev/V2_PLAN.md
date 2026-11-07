# FreeWorks 2.0.0 plan

Written 2026-11-08 after the research phase (`docs/swref/`, `docs/SW_BEHAVIOR_SPEC.md`,
`docs/swref/95_gap_matrix.md`). Goal from the owner: *a regular SOLIDWORKS user should not feel a
difference in experience* — not only the same names, but the same windows, options, defaults and
minute interactions.

## 1. What changes from 1.x
1.x relabelled FreeCAD's task panels (pmskin) and mapped commands. Research shows the remaining
difference is structural (panel contents and flow), selection-driven (picks any time, context
toolbars, cues) and physical (zoom/rotate rules, drag handles). 2.0 therefore builds **its own
PropertyManagers and an interaction layer**, keeping FreeCAD as the geometry engine:

| Layer | 1.x | 2.0 |
|---|---|---|
| PropertyManagers | FreeCAD panels relabelled | **Own PM framework** (`freeworks/pm/`): SOLIDWORKS anatomy, selection boxes, cues, remembered state; each PM drives FreeCAD objects (PartDesign::Pad, ::Fillet, Sketcher constraints …) |
| 3D-view interaction | gesture filter only | **Interaction layer** (`freeworks/il/`): wheel-zoom rule, rotate pivot + magenta marker, context toolbar, breadcrumbs, Select Other, RMB cue, selection filters, drag handles/rulers (pivy draggers) |
| Sketch tools | FreeCAD tools with relabelled widget | Own **two-state sketch PMs** that start FreeCAD's drawing handlers in the right mode and post-process (construction lines, dimensions, relations); own Trim (power-trim trail), Quick Snaps filter, Smart Dimension rules, Modify box |
| FeatureManager | FreeCAD tree + renames | **Own FeatureManager tree widget** (model of the document): SOLIDWORKS folders and order, absorbed sketches, prefixes, rollback bar (Body Tip), drag reorder, What's Wrong |
| FreeCAD | 1.1.4 | 1.1.4 for development; **switch the pin to 26.3 when it ships final** and the suite passes (UPDATE_PROTOCOL) — 26.3 brings box window/crossing selection, NaviCube home/face double-click, 3D-view context actions |

Rules that stay: never crash (`@harden`, `@safe`), never add lag (no app-wide filters; work on
selection-change, not on mouse-move, except a cheap distance check while the RMB cue is
visible; recompute previews debounced ≥150 ms; timers ≤4 Hz), SOLIDWORKS terminology, original
icons, tests for every item.

## 2. Architecture details

### 2.1 PM framework (`freeworks/pm/`)
- `PMPage` (QWidget): title (icon+name; click → flyout tree), button row (✓ ✗ preview ? pushpin;
  wizard Back/Next), message box, `PMGroup` (collapsible, optional title checkbox), standard
  controls: `PMSelectionBox` (active colour, list, Delete/Clear/Autosize menu, highlight on
  select), `PMSpin` (units, `=` expressions → FreeCAD expression engine, spin with Ctrl/Alt
  multipliers), `PMCombo`, `PMRadioRow`, `PMCheck`, `PMButtonRow` (big type buttons like Fillet
  Type / Rectangle Type).
- Host: a FreeCAD task dialog (`Gui.Control.showDialog`) with FreeCAD's own buttons hidden, so
  undo, the Tasks dock, and FreeCAD's "edit mode" keep working; Enter/Esc/Tab handled by the page.
- Selection routing: one `Gui.Selection` observer installed **only while a PM is open**; picks go
  to the active box; boxes declare accepted types (edge, face, vertex, plane, sketch, body,
  feature, component) and filter.
- State memory: per-PM QSettings group (`RememberState`), restored on open.
- Transactions: PM open = `openTransaction`; live preview edits the real feature; OK commits,
  Cancel aborts (restores tree and model).
- RMB cue: small overlay widget near the pointer after a pick; hidden when the pointer leaves a
  radius; right-click while visible = OK or next box.

### 2.2 Interaction layer (`freeworks/il/`)
- **Zoom**: wheel events on the 3D view → own handler: zoom-in moves the picked point toward the
  centre by the zoom step fraction; zoom-out about centre; options mirrored.
- **Rotate**: on MMB press decide pivot (centroid if the model's bounding box is in view, else
  pick point); draw a small magenta sphere/marker; MMB click without drag = set entity pivot.
- **Context toolbar**: shown on selection change (not mouse move), positioned near the last pick
  (further away for graphics picks), opacity animation, buttons from a per-selection-type table
  (to be filled from owner screenshots — open question Q1).
- **Breadcrumbs**, **Select Other** (Std_ClarifySelection + temporary face hiding), **filters**
  (F5 toolbar, F6, E/V/X), **box/cross colours** (until 26.3 provides window/crossing).
- **Draggers**: Coin `SoTranslate1Dragger`-style arrow for extrude depth with a ruler overlay
  (snap when the pointer is on the ruler); reused by Instant3D handles.

### 2.3 Sketch
- `EditSketchMessage` PM replaces TaskFeaturePick for new sketches: planes **and planar faces**
  pickable (face pick = attach to face with FlatFace mode).
- Tool PMs (`pm/sketch/*.py`): Line, Rectangle, Circle, Arc, Slot, Polygon, Ellipse, Spline,
  Point, Text; each starts the matching FreeCAD handler/mode, then switches to the entity
  Properties PM bound to the new geometry (parameters editable; relations listed).
- Smart Dimension: own placement logic for the special cases (Shift min/max, across-centerline
  diameter, arc length/angle) using Sketcher constraints; FreeCAD's datum dialog off; **Modify
  box** opens on new/double-clicked dimensions.
- Trim: own handler for Power trim trail (sample the drag path; trim each crossed segment via
  Sketcher trim at the crossing point), Corner, Inside/Outside, Closest.
- Quick Snaps: pick filter active for the next click.

### 2.4 Features
- Feature-first flow: feature commands with no profile → EditSketchMessage → sketch → on exit
  reopen the feature PM.
- Extrude PM over Pad/Pocket (end conditions mapped; Up To Vertex via plane through vertex; Up To
  Body via shape; Thin Feature via offset wire + pad (or `PartDesign::Pad` with `Thickness`? —
  spike); Selected Contours via sub-sketch selection; Feature Scope later).
- Fillet PM over PartDesign::Fillet (constant symmetric); multiple radius → one FreeCAD fillet per
  radius grouped under one SOLIDWORKS-named node; asymmetric/conic/variable/face/full-round →
  `FreeWorksFillet` FeaturePython using OCC (spike).
- Instant3D: click face → show the owning feature's dimensions + drag arrow on planar end faces.

### 2.5 FeatureManager
Own `QTreeView` on a document model: SOLIDWORKS order (History, Sensors, Annotations, Solid
Bodies, Equations, Material, planes, Origin, features with absorbed sketches), icons, prefixes,
rollback bar row (drag → set Body Tip; insertion follows), drag-reorder (Body "move after"),
context menus/toolbars, What's Wrong. FreeCAD's tree stays available (hidden tab) for debugging.

## 3. Phases and parts (each part ≤ 30 min; tests named after spec IDs)

**Phase 0 – Research (done 2026-11-08)**: P37 catalogue (docs/swref 00–95), P38 spec, P39 plan.

**Phase 1 – PM framework** (2.0.0-a1)
- P40 PMPage/PMGroup/buttons/message; host in task dialog; Enter/Esc/Tab (PM-1, PM-4)
- P41 PMSelectionBox + selection routing observer (PM-2, PM-3)
- P42 PMSpin with units and `=` expressions; PMCombo/Radio/Check/ButtonRow
- P43 Pushpin, remembered state, flyout tree on title click (PM-6/7/8)
- P44 RMB cue overlay (PM-5)
- P45 Port Mate PM and Move Component PM to the framework (proves it)

**Phase 2 – View physics** (a2)
- P46 Wheel zoom rule + options (VW-1)
- P47 Rotate pivot rule + magenta marker + MMB-click entity pivot (VW-2, VW-3)
- P48 Keys and Normal To rules, trimetric default, transitions (VW-4, VW-5)

**Phase 3 – Selection and context** (a3)
- P49 Context toolbar engine + per-type tables (CTX-1) — needs owner screenshots (Q1)
- P50 Breadcrumbs (CTX-2)
- P51 Select Other (SEL-2), Select Loop/Tangency/Chain/Partial Loop (SEL-3)
- P52 Selection filters F5/F6/E/V/X + funnel cursor (SEL-4), Shift transparency (SEL-5)
- P53 Box/cross colours (SEL-1) (or adopt 26.3)

**Phase 4 – Sketch** (a4–a5)
- P54 EditSketchMessage PM with face picking (SK-1, SK-2, SK-3)
- P55 Line tool + properties PMs (SK-4, SK-5)
- P56 Rectangle PM (SK-6), P57 Circle/Arc PMs, P58 Slot/Polygon/Ellipse/Point/Spline PMs
- P59 Smart Dimension rules (SK-7), P60 Modify box (SK-8)
- P61 Trim PM incl. power-trim trail (SK-9)
- P62 Automatic relation glyph check + Ctrl suppress (SK-10), P63 Quick Snaps (SK-11)
- P64 Numeric input mapping + Windows Tab check (SK-12)
- P65 Offset/Convert PMs, P66 Mirror/Dynamic Mirror, P67 Sketch Fillet/Chamfer, P68 Sketch
  patterns, P69 Move/Copy/Rotate/Scale/Stretch (SK-13)
- P70 Relations on context toolbar + Display/Delete completion (SK-14), P71 sketch status (SK-15)

**Phase 5 – Features** (b1–b2)
- P72 Feature-first flow (FT-1)
- P73 Extrude PM structure, P74 end conditions incl. vertex/body/offset/translate, P75 Thin
  Feature + Selected Contours spike, P76 drag arrow + ruler + callout (FT-2)
- P77 Fillet PM constant size, P78 multiple radius + setbacks + options, P79 FilletXpert-lite,
  P80 advanced fillet spike (FT-3)
- P81 Instant3D basics (FT-4)
- P82 Revolve, P83 Chamfer, P84 Shell/Draft, P85 Hole Wizard tabs, P86 Linear/Circular pattern +
  skip, P87 Mirror, P88 Plane/Axis/CSYS PMs, P89 Sweep/Loft PMs (FT-5)

**Phase 6 – FeatureManager** (b3)
- P90 Tree model + SOLIDWORKS order/folders/icons, P91 rollback bar, P92 drag reorder,
  P93 prefixes/errors/What's Wrong/Parent-Child, P94 rename/filter/dynamic highlight (FM-1…3)

**Phase 7 – Evaluate, assemblies** (rc)
- P95 Mass Properties COM triad + COM feature (EV-1), P96 Measure dialog (EV-2), P97 Section View
  PM (EV-3), P98 Insert Components PM (AS-1), P99 Mate PM options (AS-2), P100 Quick Mates +
  SmartMates (AS-3)

**Phase 8 – Release 2.0.0**
- P101 Owner settings profile (spec §7), P102 stress + performance pass, P103 Windows field test
  with the owner, P104 docs/What's New, release to `stable`.

Interim releases: alpha builds go to `main` only; the owner tests from a branch zip; `stable`
receives 2.0.0 when Phase 8 passes. 1.5.x stays on `stable` meanwhile (bug fixes only).

## 4. Open questions for the owner
- **Q1** Screenshots of the context toolbar in your SOLIDWORKS for: a planar face, a cylindrical
  face, an edge, a feature in the tree, a sketch in the tree, a plane, a sketch entity selection,
  a component — to copy the exact buttons.
- **Q2** What is bound to **X** in your SOLIDWORKS (command #33094)? (S is Quick Snaps.)
- **Q3** "Scroll button click had things configured": do you mean the MMB-click-entity rotate
  pivot, or something else bound to the middle button?
- **Q4** On Windows with 1.5.4: does Tab in a sketch (numeric input) work now, and are gestures
  back?
- **Q5** Variable/Face/Full Round fillets and Thin Feature need geometry FreeCAD's PartDesign
  lacks — acceptable to deliver Constant Size first and these in 2.1?

## 5. Definition of done for 2.0.0
All S1 spec items pass automated tests (or an interactive XTEST where input is involved) and the
owner's Windows walkthrough: new part → sketch on a plane and on a face → rectangle/circle/line
with numeric input → Smart Dimension + Modify → Trim → Extrude with drag arrow → Fillet edges
without preselection → change extrude depth (sketch on face follows) → Mass Properties → new
assembly with OK-at-origin → mates via pop-up → Move Component with collision.
