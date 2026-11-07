# SOLIDWORKS behaviour specification for FreeWorks 2.0

Distilled from the research catalogue in `docs/swref/` (sources and confidence tags live there).
Each item is an **acceptance criterion**: a FreeWorks build passes it when a SOLIDWORKS 2026 user
doing the described action sees the described result. IDs are stable; tests in
`dev/tests/` reference them. Severity S1/S2/S3 as in `docs/swref/95_gap_matrix.md`.
Target behaviour = SOLIDWORKS 2026 SP1 with the owner's settings (`docs/swref` tag [O]).

## 1. PropertyManager framework (PM)  — catalogue 01 §1.1–1.2
- **PM-1 (S1)** Every FreeWorks command that has a SOLIDWORKS PropertyManager opens one in the
  Manager Pane's PropertyManager tab: title (icon + name), ✓ / ✗ / (Detailed Preview) / ? /
  pushpin row, yellow message box, collapsible group boxes (some with a title checkbox), in the
  SOLIDWORKS order with SOLIDWORKS labels and defaults.
- **PM-2 (S1)** Selection boxes: exactly one is active and coloured (light blue); picks in the
  graphics area or tree go to the active box; clicking another box activates it; selected item in
  a box highlights its geometry; right-click in a box → Delete / Clear Selections; boxes grow with
  content.
- **PM-3 (S1)** Picks are accepted at any moment while the PM is open — never a "confirm
  selection" step, never a modal error for an empty selection; the message box says what to pick.
- **PM-4 (S1)** Enter = OK, Esc = Cancel, Tab moves between controls, Space toggles, arrows move
  radio buttons. Right-click in the graphics area offers OK / Cancel at the top.
- **PM-5 (S2)** RMB cue: after a pick, while the pointer stays near it, a small mouse icon shows
  a green check (right-click = OK) or an "enter" arrow (right-click = next selection box).
- **PM-6 (S2)** Pushpin keeps the PM open after OK (Fillet, Chamfer, Mate, Insert Components …).
- **PM-7 (S2)** "Remembers last used state" where SOLIDWORKS does (Fillet type/size/options,
  Draft, rectangle/arc/circle type).
- **PM-8 (S2)** Clicking the PM title shows the flyout FeatureManager in the graphics area.
- **PM-9 (S1)** Confirmation Corner ✓/✗ (and Exit/Cancel Sketch) top-right; D moves it to the
  pointer unless D is bound to another command (owner: D = Smart Dimension).

## 2. View and interaction physics  — catalogue 02, 03, 90
- **VW-1 (S1)** Wheel zoom-in: the point under the pointer moves toward the screen centre while
  zooming; wheel zoom-out: about the screen centre. Wheel away = zoom out. Option: Zoom About
  Screen Center; Reverse mouse wheel zoom direction.
- **VW-2 (S1)** MMB drag rotates about the model centroid when the whole model is visible,
  otherwise about a point picked on visible geometry; the pivot entity/point is shown magenta
  during the drag. MMB-click an entity then MMB-drag rotates about it (green-line pointer).
- **VW-3 (S1)** Ctrl+MMB pan, Shift+MMB zoom, Alt+MMB roll, double-MMB zoom to fit.
- **VW-4 (S2)** Keys: F, Z / Shift+Z, Space (View Orientation), Ctrl+1…8, Ctrl+Shift+Z, arrows
  15° / Shift 90° / Alt roll / Ctrl pan, Q show planes while held. Normal To rules: repeat flips,
  Ctrl second face sets up, nothing selected → closest orthogonal view.
- **VW-5 (S2)** New parts open in **Trimetric** (owner) with zoom-to-fit on standard views and
  ~0.5 s view transitions.
- **SEL-1 (S2)** Left→right drag = window (blue, solid outline); right→left = crossing (green,
  dashed); starts in empty space; default entity type per document.
- **SEL-2 (S2)** Select Other: right-click a face → it hides and a pick list of faces behind
  appears; right-click hides more; Esc restores (map Std_ClarifySelection + hide).
- **SEL-3 (S2)** Select Loop / Select Tangency / Select Chain / Select Partial Loop on the
  right-click menu of edges/faces/sketch segments.
- **SEL-4 (S2)** Selection filters: F5 toolbar, F6 toggle, E/V/X (unless rebound), funnel cursor.
- **SEL-5 (S2)** Shift held while picking = do not select through transparency.
- **CTX-1 (S1)** Context toolbar appears on selection (semi-transparent → opaque on hover → fades
  when the pointer leaves) and on top of the right-click menu, with SOLIDWORKS' per-type buttons
  (face, edge, feature, sketch, plane, body, component, sketch entities → valid relations).
- **CTX-2 (S2)** Selection breadcrumbs top-left of the graphics area; every crumb selectable.
- **DRG-1 (S2)** Ctrl+drag feature/sketch entities/components copies; Shift+drag moves a feature;
  Alt+drag component = SmartMate; Ctrl+drag fillet onto an edge copies it.

## 3. Sketching  — catalogue 05, 06
- **SK-1 (S1)** Sketch with nothing selected → "Edit Sketch" message PM; the three planes appear
  (trimetric) **and every planar face of the model is pickable**; picking rotates Normal To and
  opens the sketch. Same for clicking a sketch entity tool first (the tool stays active).
- **SK-2 (S1)** A sketch on a model face stays on that face when upstream features change.
- **SK-3 (S1)** Exit keeping changes leaves the view normal; Exit without saving restores the
  previous view.
- **SK-4 (S1)** Every entity tool shows its **tool PM** (type buttons, options, parameters) and,
  after the first entity, the **properties PM** of that entity while the tool stays active; OK
  (or double-click) returns to the tool PM; selecting an entity with no tool shows its properties
  PM (Existing Relations + status, Add Relations, Options, Parameters, Additional Parameters).
  Exact contents per tool: 06 §6.1–6.9.
- **SK-5 (S1)** Line: click-click chain, click-drag single, double-click/Esc/right-click End Chain
  ends; A or return-to-endpoint switches to tangent arc (intent zones).
- **SK-6 (S1)** Rectangle: 5 types, Add construction lines (From Corners / From Midpoints),
  Shift = square, flyout keeps the last type.
- **SK-7 (S1)** Smart Dimension result rules (06 table §5.5) incl. placement-driven orientation,
  angle quadrant by placement, diameter across a centerline, arc length/angle by three picks,
  Shift = min/max, right-click locks orientation.
- **SK-8 (S1)** Modify box after placing (Input dimension value): calculator, `=` with globals/
  functions/file properties drop-down, click other dimensions to insert their names, spin arrows
  and thumbwheel (slider when bounded), Ctrl ×10 / Alt ÷10, ✓ ✗ Rebuild, Reverse sense, Reset
  spin increment, Mark for drawing (on), name field `D1@Sketch1`, configuration drop-down.
- **SK-9 (S1)** Trim PM with Power trim (drag trail across entities trims each; drag from an end
  extends), Corner, Trim away inside/outside, Trim to closest, Keep trimmed as construction,
  Ignore construction.
- **SK-10 (S2)** Automatic relations with pointer glyphs and inference lines; Ctrl suppresses.
- **SK-11 (S2)** Quick Snaps: one-shot filter of the next pick; owner key S; double-click keeps it.
- **SK-12 (S2)** On-screen numeric input: fields beside the entity, Tab/Enter, "create dimension
  only when value entered".
- **SK-13 (S2)** Offset, Convert, Mirror (+Dynamic), Sketch Fillet/Chamfer, Linear/Circular
  pattern, Move/Copy/Rotate/Scale/Stretch PMs with the options in 06.
- **SK-14 (S2)** Add Relations via the context toolbar of the selected entities; Display/Delete
  Relations PM complete (filters, suppressed, repair/replace).
- **SK-15 (S2)** Sketch status: colours (black/blue/red), tree prefix (-)/(+)/(?), status bar
  "Under Defined" etc.; over-defining dimension asks "Make this dimension driven?".

## 4. Features  — catalogue 07–11
- **FT-1 (S1)** Sketch-based features find their sketch: open sketch → used; preselected → used;
  nothing → message + pick plane/face → sketch → exit → PM resumes.
- **FT-2 (S1)** Extrude PM exactly as 07 §7.1 (From, Direction 1/2, end conditions with their
  extra boxes, double-click face → Up To Surface, Thin Feature, Selected Contours, Feature Scope,
  draft) with a live preview, a drag arrow per direction, ruler snapping, editable depth callout.
- **FT-3 (S1)** Fillet PM exactly as 08 §8.1 for Constant Size (Items box with selection toolbar,
  tangent propagation, preview modes with A-key stepping, Symmetric/Asymmetric, profile,
  Multiple radius with per-edge callouts, setbacks, partial edge, options); picking edges/faces/
  features/loops works with or without preselection; Variable/Face/Full Round as later items.
- **FT-4 (S1)** Instant3D: single click a face shows the feature's dimensions and drag handles;
  ruler snap; Alt snaps to geometry; drag a selected contour to extrude (M = mid plane).
- **FT-5 (S2)** Revolve, Sweep, Loft, Chamfer, Shell, Draft, Hole Wizard (Type/Positions tabs),
  Mirror, Linear/Circular Pattern (skip instances), Plane (three references), Axis, Coordinate
  System PMs as catalogued.
- **FT-6 (S2)** Feature names and tree icons as SOLIDWORKS (04 §4.5); rename on creation option.

## 5. FeatureManager  — catalogue 04
- **FM-1 (S1)** Rollback bar: drag, arrow keys, right-click Rollback / Roll to Previous / Roll to
  End; new features insert at the bar (maps to FreeCAD Body Tip).
- **FM-2 (S1)** Drag to reorder with "no" cursor for illegal moves.
- **FM-3 (S2)** Default folders and nodes (History, Sensors, Annotations, Solid Bodies, Equations,
  Material, Front/Top/Right, Origin), absorbed sketches under features, prefixes and error/warning
  icons, What's Wrong dialog, Parent/Child, slow-double-click/F2 rename, tree filter, dynamic
  highlight.

## 6. Evaluate, configurations, assemblies, drawings  — catalogue 12–15
- **EV-1 (S1)** Mass Properties as 12 §12.1 incl. COM triad, Create Center of Mass feature,
  Report coordinate values relative to.
- **EV-2 (S2)** Measure dialog toolbar (arc conditions, units, XYZ, point-to-point, projected,
  history, pin) and status-bar measurements of the selection.
- **EV-3 (S2)** Section View PM.
- **CF-1 (S1)** Configurations and design tables as 13 (already engine; PM layout to match).
- **AS-1 (S1)** Begin Assembly/Insert Components PM: OK places the first component fixed at the
  origin with aligned planes; Rotate context toolbar; pushpin.
- **AS-2 (S1)** Mate PM + pop-up (exists) plus Make first selection transparent, Use for
  positioning only, Add to new folder.
- **AS-3 (S2)** Quick Mates context toolbar (two entities Ctrl-selected), SmartMates (Alt-drag,
  Tab flips), Move Component options (Physical Dynamics, Dynamic Clearance, Highlight faces, Sound).
- **DR-1 (S3)** Drawing PMs as 15 (CSWA needs recognition of view types; detailing later).

## 7. Owner-specific settings that must be honoured  — catalogue [O]
Simplified Interface layout; dark theme colours; MMGS; numeric input + add dimension; Modify on
creation; auto-rotate normal; automatic relations; grid off; zoom about cursor; triad on, cube off;
trimetric default; breadcrumbs; context toolbars on selection and shortcut menu; mate pushpin;
keyboard C D E F M R T, S = Quick Snaps, X = (unknown, ask); gestures (8) per 01 §1.8.
