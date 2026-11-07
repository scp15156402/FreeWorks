# 95 — Gap matrix: SOLIDWORKS behaviour vs FreeCAD 1.1.4 / 26.3 vs FreeWorks 1.5.4

Severity: **S1** blocks a CSWA/CSWP workflow or was reported by the owner · **S2** a regular
SOLIDWORKS user notices within minutes · **S3** polish.
FreeCAD column: ✅ engine/UI can do it · 🟡 partly or different · ❌ missing. "26.3" = FreeCAD
26.3 (RC2, Oct 2026) adds it. FreeWorks column describes 1.5.4 as shipped.
Approach: **PM** = own SOLIDWORKS-structured PropertyManager driving FreeCAD objects ·
**IL** = interaction layer (event handling in the 3D view) · **skin** = relabel FreeCAD panel ·
**engine** = needs geometry FreeCAD lacks (OCC call or add-on) · **n/a** = not achievable.

## A. Root cause found by this research
FreeWorks 1.x mostly **relabels FreeCAD task panels** (pmskin) and maps commands. The owner's
complaint — "windows which open after certain interactions are just not there", "the minute
interactions aren't there" — comes from three things a skin cannot fix:
1. **Panel structure**: SOLIDWORKS PMs have different groups, options, defaults, conditional
   visibility and the two-state tool/properties pattern (06). FreeCAD panels have different
   controls in a different order; relabelling hides that only partly.
2. **Selection-driven flow**: SOLIDWORKS accepts picks at any moment into the active selection
   box (coloured), shows callouts/handles, RMB cues, context toolbars, breadcrumbs, and never asks
   to "confirm selection". FreeCAD often requires preselection, a "Select" toggle, or a separate
   dialog.
3. **View/interaction physics**: wheel-zoom rule, rotate-about rules with magenta highlight,
   Instant3D handles and rulers, drag-to-reorder/rollback, Ctrl/Shift/Alt drags (02, 90).

## B. Matrix (highest severity first within each area)

### B1 Sketching
| SOLIDWORKS behaviour (ref) | Sev | FreeCAD | FreeWorks 1.5.4 | Approach |
|---|---|---|---|---|
| Sketch on any planar **model face** via Sketch-then-pick or pick-then-Sketch; follows the face when the feature changes (05 §5.1) | S1 | ✅ attach to face; TNP mitigation 1.0+ | ❌ Sketch-then-pick only lists planes (TaskFeaturePick); pick-then-Sketch works | IL: face picking in the plane-pick state + own "Edit Sketch message" PM |
| Feature-first: Extrude with nothing selected → pick plane/face → sketch → exit → PM resumes (07 §7.0) | S1 | ❌ | ❌ | PM + IL |
| Smart Dimension placement rules, Shift min/max, doubled distance across centerline (05 §5.5) | S1 | 🟡 contextual dimension; no Shift min/max, no diameter-across-centerline | mapped | IL on top of Sketcher constraints |
| Modify box (calculator, `=`, spin/thumbwheel, Ctrl/Alt ×10/÷10, Rebuild, Reverse sense, name, Mark for drawing) (05 §5.6) | S1 | 🟡 datum dialog | ❌ | own dialog |
| Two-state entity PMs (Insert Line → Line Properties with Parameters/Additional Parameters, Rectangle types/construction lines, Circle/Arc types, Slot, Polygon) (06) | S1 | 🟡 tool widget + no per-entity property PM | 🟡 relabelled sketch panel | PM (sketch-mode panel) |
| Trim PM: Power trim drag-across, Corner, Inside/Outside, Closest, construction options (06 §6.20) | S1 | 🟡 trim by click only; no drag trail, no corner/inside/outside | mapped | IL + PM |
| Automatic relations with glyphs, Ctrl suppresses; inference lines (05 §5.3) | S2 | ✅ autoconstraints with icons; Ctrl? (verify) | as FreeCAD | verify, adapt |
| Quick Snaps (one-shot filter; owner's S key) (05 §5.3) | S2 | ❌ (snap settings only) | ❌ | IL filter on pick |
| Numeric input Tab/Enter, Create dimension only when value entered (05 §5.4) | S2 | ✅ On-View Parameters | owner reported Tab issue on Windows | verify on Windows; map settings |
| Offset PM (select chain, bi-directional, cap ends arcs/lines, base/offset construction, drag preview) (06 §6.22) | S2 | 🟡 offset tool (no caps/bi-dir?) | partial skin | PM |
| Convert Entities PM (Select chain, Select all inner loops, face→all edges) (06 §6.23) | S2 | 🟡 external geometry/carbon copy | mapped | PM |
| Mirror (Copy, RMB cue), Dynamic Mirror (06 §6.24) | S2 | ✅ symmetric/mirror | mapped | PM + cue |
| Sketch Fillet (Keep constrained corners virtual sharp, Dimension each fillet) (06 §6.25) | S2 | 🟡 fillet keeps point? | mapped | PM |
| Linear/Circular sketch pattern PMs with skip, dimension options, count edit in place (06 §6.26) | S2 | 🟡 rectangular/polar array dialogs | mapped | PM |
| Move/Copy/Rotate/Scale/Stretch PM family (06 §6.27) | S3 | 🟡 translate/rotate/scale tools | mapped | PM |
| Add Relations PM + relation icons on context toolbar (05 §5.8) | S2 | 🟡 constraint toolbar | menu | context toolbar + PM |
| Display/Delete Relations full (filters, suppressed, replace dangling) (05 §5.8) | S3 | 🟡 | ✅ partial (1.5.1) | extend |
| Fully Define Sketch (05 §5.9) | S3 | ❌ | ❌ | engine (own algorithm) — later |
| SketchXpert / Check Sketch for Feature (05 §5.10–11) | S3 | 🟡 solver messages, validate sketch | ❌ | PM over Sketcher_ValidateSketch |
| Sketch status in tree (-)/(+), status bar texts (05 §5.2) | S2 | 🟡 | 🟡 status bar only | tree delegate decoration (not labels) |

### B2 Features
| SOLIDWORKS behaviour | Sev | FreeCAD | FreeWorks | Approach |
|---|---|---|---|---|
| Fillet PM: picks any time, no confirm step, Items box + selection toolbar + tangent propagation + preview modes; radius callouts; multiple radius; setbacks; overflow; keep features (08 §8.1) | S1 | 🟡 PartDesign Fillet: one radius; "Select" mode; error popups; Part_Fillet per-edge radius outside body | skin; owner: "refused to select an edge" | PM driving PartDesign::Fillet (+ multiple features for multi-radius) |
| Variable / Face / Full Round fillet (08) | S2 | ❌ in PartDesign (Part_Fillet variable radius only) | ❌ | engine: OCC BRepFilletAPI via a FeaturePython in the Body — later |
| Extrude PM: From (Sketch Plane/Surface/Vertex/Offset), Dir 1/2 end conditions incl. Up To Vertex/Body, double-click face → Up To Surface, Thin Feature, Selected Contours, Feature Scope, draft (07 §7.1) | S1 | 🟡 Pad/Pocket cover most end conditions; ❌ thin, contours, vertex as name | skin | PM; thin = offset sketch wire + pad; contours = sub-sketch selection |
| Drag arrow + ruler + depth callout on the preview; Instant3D on faces (07, 11 §11.5) | S1 | ❌ | ❌ | IL (Coin draggers) |
| Revolve PM incl. auto-axis from single centerline, radius/diameter dims (07 §7.2) | S2 | ✅ Revolution/Groove | skin | PM |
| Sweep/Loft PMs (07 §7.3–7.4) | S2 | 🟡 Pipe/Loft (no loft guides in PD) | mapped | PM; guides later |
| Chamfer PM (5 types) (08 §8.2) | S2 | 🟡 3 types | skin | PM |
| Hole Wizard Type/Positions tabs, favourites, standards (08 §8.3) | S2 | 🟡 Hole feature (ISO/UTS tables) | skin | PM (two tabs) over PartDesign::Hole |
| Shell (faces to remove, multi-thickness, outward) (08 §8.4) | S2 | ✅ Thickness | skin | PM |
| Draft (neutral plane, face propagation) (08 §8.5) | S3 | 🟡 | skin | PM |
| Mirror/Patterns with Instances to Skip, vary, geometry pattern, two directions (09) | S2 | 🟡 MultiTransform/LinearPattern (2 dirs in 1.1), no skip | skin | PM; skip via FreeCAD pattern "Mask"? (verify) else split features |
| Plane PM with three references and constraint buttons (10 §10.1) | S2 | 🟡 Datum plane attachment modes | skin | PM translating references → attachment mode |
| Coordinate System PM (10 §10.3) | S2 | ✅ LCS | mapped | PM |
| Move/Copy Bodies, Combine, Split, Delete Body, Move/Delete Face (11) | S2 | 🟡 Part workbench / Boolean in PD | mapped | PM |
| Feature Scope / multibody behaviour (07, 11) | S2 | 🟡 multiple bodies = multiple Body objects | ❌ | design decision (see plan) |

### B3 UI framework, view, selection, tree
| SOLIDWORKS behaviour | Sev | FreeCAD | FreeWorks | Approach |
|---|---|---|---|---|
| Wheel zoom: zoom-in pulls the point under the pointer toward the centre; zoom-out about the centre (02 §2.2) | S1 | 🟡 ZoomAtCursor = pure cursor zoom both ways | pure cursor zoom | IL: own wheel handler |
| Rotate: centroid if all visible, else picked point with magenta marker; MMB-click entity rotate (02 §2.1) | S1 | 🟡 RotationMode; no highlight | rotation mode 2 (object centre) | IL |
| PM anatomy: coloured active selection box, Tab/Space/arrows, message box, pushpin, flyout tree, RMB OK cue (01 §1.1–1.2) | S1 | ❌ | partial (green/red buttons) | own PM framework |
| Context toolbar on selection + above shortcut menu (01 §1.4) | S1 | ❌ | ❌ (open P36) | IL widget |
| Breadcrumbs (01 §1.6) | S2 | ❌ | ❌ | widget |
| Select Other with RMB-hide (01 §1.5) | S2 | 🟡 (verify 1.1 "clarify selection") | ❌ | IL |
| Box (blue, window) / cross (green, crossing) by drag direction; lasso (03 §3.2) | S2 | ✅ 26.3 drag box window/crossing; 1.1 Shift+B box | ❌ | adopt 26.3 or IL |
| Selection filters F5/F6/E/V/X, 2026 feature/component filters (03 §3.4) | S2 | 🟡 selection filter toolbar? (verify) | ❌ | IL |
| FeatureManager: rollback bar, drag reorder, slow-double-click rename, (-) prefixes, folders, What's Wrong (04) | S1 | 🟡 tree reorder via move, no rollback bar (Tip only) | 🟡 names | custom tree delegate + "Set Tip" mapping |
| Mouse gestures exactly as configured (01 §1.8) | S1 (owner) | ❌ | ✅ wheel; owner said they disappeared in 1.5.3 | verify on Windows |
| Shortcut bar with search (owner uses S for Quick Snaps instead) (01 §1.7) | S3 | ❌ | ✅ | keep |
| Heads-up toolbar, View Orientation dialog, View Selector cube, Normal To rules (02) | S2 | 🟡 NaviCube (26.3 home/face double-click) | 🟡 | polish |
| Confirmation corner (+ D to pointer) | S2 | ❌ | ✅ | keep |
| Status bar measurement of selection (12 §12.2) | S2 | 🟡 | ❌ | small |
| Simplified Interface layout (owner) (91) | S2 | ❌ | ❌ | CommandManager mode |

### B4 Evaluate, configurations, assemblies, drawings
| SOLIDWORKS behaviour | Sev | FreeCAD | FreeWorks | Approach |
|---|---|---|---|---|
| Mass Properties dialog layout + triad at COM (12 §12.1) | S1 | ❌ dialog | ✅ (1.1.1) | add COM triad, Create COM feature |
| Measure dialog toolbar (arc conditions, XYZ, point-to-point, projected, history) (12 §12.2) | S2 | 🟡 unified Measure | mapped | own dialog over Measure |
| Section View PM (12 §12.3) | S2 | 🟡 clip planes | mapped | PM |
| Equations dialog 4 views (13 §13.1) | S2 | 🟡 | ✅ one view | extend |
| Configurations / design tables (13) | S1 (CSWP 2) | ❌ native | ✅ engine + manager | polish to PM layout |
| Begin Assembly / Insert Components PM (OK → origin, Rotate context toolbar) (14 §14.1) | S1 | 🟡 Insert component dialog | FreeCAD's | PM |
| Mate PM + pop-up (14 §14.2) | S1 | 🟡 joints | ✅ | keep; add Make first selection transparent, Use for positioning only |
| Quick Mates / SmartMates (Alt-drag) (14 §14.3) | S2 | ❌ | ❌ | IL |
| Move Component full option set incl. Physical Dynamics, Dynamic Clearance (14 §14.4) | S2 | 🟡 drag | ✅ part | extend |
| Drawings view PMs (15) | S3 (CSWA = recognition) | 🟡 TechDraw | 🟡 | later |

## C. Biggest levers (ordered)
1. **Own PropertyManager framework** (PM anatomy, selection boxes, cues) — unlocks every S1 PM.
2. **Interaction layer in the 3D view**: wheel zoom rule, rotate rule, context toolbar, Select
   Other, drag handles/rulers, face picking for sketches, RMB cue.
3. **Sketch PMs** (two-state) + Smart Dimension rules + Modify box + Trim/Offset/Convert.
4. **Feature PMs**: Extrude, Fillet, Hole Wizard, Revolve, Chamfer, Shell, Patterns, Plane.
5. **FeatureManager tree**: rollback bar, reorder, prefixes, folders.
6. Assemblies: Insert Components PM, Quick Mates/SmartMates.
