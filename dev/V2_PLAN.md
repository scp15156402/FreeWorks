# FreeWorks 2.x master plan — own code, simple → complex

Rewritten 2026-11-08 after the research phase. Inputs: `docs/swref/` (catalogue with sources),
`docs/SW_BEHAVIOR_SPEC.md` (acceptance IDs), `docs/swref/95_gap_matrix.md`.
Owner direction: *"Plan features from simple to complex. This may now require your own code.
Plan the full thing."* The owner cannot supply screenshots or answers, so every open question is
decided below and the plan does not wait on anyone.

---------------------------------------------------------------------------------------------

## 0. Decisions (replacing the open questions)

| # | Question | Decision |
|---|---|---|
| D1 | Exact context-toolbar buttons per selection | Build from the documented commands (01 §1.4: Edit Feature, Edit Sketch, Sketch, Hide/Show, Isolate, Change Transparency, Appearance, Normal To, Zoom to Selection, Fillet/Chamfer on edges, Suppress/Rollback on features, relations on sketch entities, Component Properties on components). Buttons live in one table (`il/ctxtables.py`) so a later correction is a one-line edit. |
| D2 | Owner's X key (#33094) | Leave X unbound in the owner profile; ship the SOLIDWORKS default (X = Filter Faces) in the standard profile. |
| D3 | "Scroll button click had things configured" | Implement documented MMB behaviour: MMB-click an entity = rotate pivot (magenta, green-line pointer), double-MMB = zoom to fit. |
| D4 | Sketch Tab / gestures on Windows | Covered by automated XTEST + a Windows checklist in each alpha's notes; no blocking. |
| D5 | Geometry PartDesign lacks (variable/face/full-round/asymmetric fillets, thin features, selected contours, skip instances, feature scope) | **Own code**: PartDesign `FeatureAdditivePython` / `FeatureSubtractivePython` / dress-up style FeaturePython objects using OCC through `Part` (verified in 1.1.4: AdditivePython/SubtractivePython types exist, `Shape.makeFillet(r1, r2, edges)` variable radius works, `makeChamfer(d1, d2, edges)` works, `Face.makeOffset2D` works). Delivered after the UI tiers. |
| D6 | FreeCAD version | Develop on 1.1.4 (pinned). At every stage boundary run `dev/check_updates.py`; when 26.3 is final and the suite is green, switch the pin (26.3 brings window/crossing box selection and NaviCube improvements, which then replace our own versions). |
| D7 | Where 2.x lives until ready | `main` gets alpha builds (`2.0.0-aN`); `stable` keeps 1.5.x (fixes only) until the 2.0.0 milestone passes its acceptance list. |
| D8 | Verifying "exact layouts" without screenshots | Layout = catalogue text (help + tutorials). Every PM gets a layout test that asserts group order, labels, defaults and visibility rules against a spec table in `freeworks/pm/specs/`. Items still tagged [K] in the catalogue are listed in each PM spec as `unverified=True` so they can be corrected later. |

## 1. Strategy: what is FreeCAD's and what is ours

**FreeCAD keeps**: documents, PartDesign/Sketcher/Assembly objects, the sketch solver, OCC
geometry, recompute, undo/redo transactions, file I/O, TechDraw.
**FreeWorks owns (new code)**: every SOLIDWORKS-facing window, panel and interaction —
PropertyManagers, dialogs, the FeatureManager tree, context toolbars, breadcrumbs, cues, view
navigation physics, sketch tool behaviour, drag handles, and the missing geometry features.

Verified FreeCAD 1.1.4 APIs this plan relies on (run 2026-11-08 in the pinned build):
`PartDesign::FeatureAdditivePython/SubtractivePython` exist · `Body.insertObject` exists (tree
reorder) · features have `Suppressed` (suppression without deleting) · Sketch has `trim`, `split`,
`extend`, `setDatum`, `setLabelDistance`, `setLabelPosition`, `toggleConstruction`,
`autoconstraint`, `addRectangularArray` · Pad has `Type/Type2/Length2/Offset/TaperAngle/UpToFace/
UpToShape/Midplane/Reversed/SideType/UseCustomVector` · LinearPattern has `Direction2`,
`Occurrences2`, `Spacings` · 3D view Python: `getCameraNode`, `getPoint`, `getObjectInfo(s)`,
`addEventCallbackPivy`, `graphicsView`, `setAnimationEnabled`; **no Python rotation-centre API**
→ own orbit code · `Std_ClarifySelection` exists (Select Other basis).

## 2. Architecture

```
freeworks/
  pm/                      PropertyManager framework + every PM
    core.py                PMPage, PMGroup, buttons, message box, pushpin, memory, host
    controls.py            PMSelectionBox, PMSpin (units, '=' expressions), PMCombo, PMRadioRow,
                           PMCheck, PMButtonRow (big type buttons), PMList, PMTable
    routing.py             selection routing (one Gui.Selection observer, only while a PM is open),
                           type filters, highlight of box items
    cue.py                 RMB cue overlay (OK / next box / hide)
    specs/                 one spec table per PM (groups, labels, defaults, visibility rules)
    sketch/  feature/  ref/  assembly/  evaluate/  drawing/      the PMs themselves
  il/                      interaction layer (3D view)
    viewfilter.py          the single per-viewport event filter (extends gestures.py)
    zoom.py  orbit.py      wheel-zoom rule, pivot rules + magenta marker, MMB-click pivot
    ctxbar.py ctxtables.py context toolbar engine + per-selection button tables
    crumbs.py              selection breadcrumbs
    selother.py filters.py Select Other, selection filters (Gui.Selection gates)
    draggers.py rulers.py  Coin drag arrows/handles, on-screen rulers, callouts
    sketchinput.py         sketch-mode mouse logic (power-trim trail, quick-snap filter, smart dim)
  tree/                    own FeatureManager (QTreeView + model), rollback, reorder, What's Wrong
  dlg/                     Modify box, Measure, Mass Properties, Equations, Options … (dialogs)
  geom/                    own geometry features (FeaturePython): AdvFillet, ThinExtrude,
                           SelectedContours, SkipPattern, FullRound, FaceFillet, …
```

Rules (unchanged from CLAUDE.md): `@harden`/`@safe` everywhere; no app-wide filters; the only
mouse-move work is in the viewport filter and must be O(1) unless a drag is in progress;
selection-driven UI reacts to selection *changes*; previews recompute debounced ≥150 ms; timers
≤4 Hz; every part adds tests; the suite stays < 2 min.

## 3. Complexity tiers

| Tier | Meaning | Typical work |
|---|---|---|
| **T1 simple** | settings, key maps, small dialogs, pure Qt, no geometry | prefs, shortcuts, status bar, simple dialogs |
| **T2 moderate** | own PMs/dialogs that set properties of existing FreeCAD objects | Plane, Shell, Revolve, Extrude (standard options), Modify box |
| **T3 complex** | interaction layer: mouse/Coin, live previews, draggers, sketch-mode logic | zoom/orbit rules, context toolbar, power trim, Smart Dimension rules, drag arrows |
| **T4 very complex** | own geometry or own big subsystems | own FeatureManager tree, advanced fillets, thin features, selected contours, Instant3D, SmartMates |
| **T5 research spike** | unknown feasibility; time-boxed, ends in a decision note in DEV_NOTES | full-round fillet, physical dynamics, fully define sketch |

## 4. Roadmap — stages ordered simple → complex

Each part ≤ 30 min (split when longer). `→ ID` = spec IDs the part satisfies; every part adds
tests (`T:`). Stages end with an alpha build on `main` and a CHANGELOG entry.

### Stage A — T1 quick wins (alpha a1)
| Part | Work | → | T |
|---|---|---|---|
| P40 | Owner profile + standard profile switch (Options page): keys C D E F M R T, S = Quick Snaps placeholder, X unbound; trimetric for new parts; 0.5 s transitions; arrow-key 15° | VW-4, VW-5, §7 | profile applied, keys resolve |
| P41 | Keyboard completion: Q (show planes while held), G magnifier stub → zoom-to-area, Ctrl+Shift+Z previous view, Alt+arrows roll, Shift+arrows 90°, F3 Quick Snaps default | VW-4 | key map table test |
| P42 | Normal To rules: repeat flips 180°, Ctrl second face = up, cylinder → axis, nothing → closest orthogonal | VW-4 | camera assertions |
| P43 | Status bar: selection measurements (edge length, face area, distance of two picks, point XYZ), "Editing Sketch1", unit-system button with list + Edit Document Units | EV-2 | selection → text |
| P44 | Selection filters: F5 toolbar (vertices, edges, faces, bodies, planes, axes, sketch segments/points, dimensions, notes), F6 toggle, E/V/X, funnel cursor (Gui.Selection gate) | SEL-4 | gate blocks types |
| P45 | Shift-held = no select-through-transparency; Select Other = Std_ClarifySelection on right-click face + temporary face hide (RMB) | SEL-2, SEL-5 | pick list opens |
| P46 | Contextual selection on menus: Select Loop (flip arrow), Select Tangency, Select Chain, Select Partial Loop, Select Midpoint | SEL-3 | topology tests |
| P47 | Isolate pop-up (Wireframe/Transparent/Hidden, Exit Isolate), Tab/Shift+Tab/Ctrl+Shift+Tab hide/show under pointer (verify existing), Top Level Transparency | 90 | visibility tests |
| P47a | CommandManager tab contents and order per catalogue 01 §1.3a; flyout buttons keep the last used command (rectangle/arc/circle/slot); large tooltips | 01 | catalog order test |
| P47b | View Orientation dialog (standard + named views, New View, Update/Reset Standard Views, pushpin, double-click applies) + View Selector cube toggle (Ctrl+Space) | VW-4 | dialog tests |
| P47c | Visual style: owner dark theme + standard light theme colour sets (gradient, preselection orange, selection blue, sketch black/blue/red, construction, preview add/remove colours), plane display | §7 | colour prefs test |
| P47d | Options pages that change behaviour: Sketch, Relations/Snaps, Display, Selection, View, FeatureManager, Spin Box Increments, General (Input dimension value, Single command per pick, Confirmation Corner) — each wired to the code paths that read it | 16 | option→behaviour tests |

### Stage B — PM framework (alpha a2) — T2 foundation
| Part | Work | → | T |
|---|---|---|---|
| P48 | `pm/core.py`: PMPage (title, ✓ ✗ ? pushpin, message box), PMGroup (collapsible, title checkbox), host in task dialog with FreeCAD buttons hidden; Enter/Esc/Tab/Space/arrows | PM-1, PM-4 | layout + key tests |
| P49 | `pm/controls.py`: PMSpin (units, Ctrl/Alt multipliers, `=` expressions via ExpressionEngine), PMCombo, PMRadioRow, PMCheck, PMButtonRow | PM-1 | widget tests |
| P50 | `pm/routing.py` + PMSelectionBox: active box colour, accepted types, Delete/Clear/Autosize menu, highlight on item select, picks any time | PM-2, PM-3 | routing tests |
| P51 | Pushpin (re-open after OK), remembered state (QSettings per PM), flyout tree on title click | PM-6, PM-7, PM-8 | persistence tests |
| P52 | `pm/cue.py` RMB cue overlay (OK / next box) + right-click OK/Cancel at the top of the graphics menu | PM-5, PM-4 | cue state machine |
| P53 | `pm/specs` format + layout test harness (group order, labels, defaults, visibility rules, unverified flags) | D8 | harness self-test |
| P54 | Port Mate PM and Move Component PM to the framework (proves it on existing features) | AS-2 | existing mate tests green |

### Stage C — Simple feature PMs over existing FreeCAD features (alpha a3) — T2
| Part | Work | → |
|---|---|---|
| P55 | Plane PM: First/Second/Third Reference with constraint buttons (coincident, parallel, perpendicular, offset distance + flip + number of planes, angle, mid plane, tangent, project, parallel to screen) → attachment modes; status "Fully defined" message | FT-5 |
| P56 | Axis PM (5 types) and Point PM (arc centre, face centre, intersection, projection, along curve) | FT-5 |
| P57 | Coordinate System PM (origin, X/Y/Z references with reverse, numeric position/rotation) | FT-5, EV-1 |
| P58 | Shell PM (thickness, faces to remove, outward, multi-thickness list, preview, error diagnostics message) | FT-5 |
| P59 | Draft PM (neutral plane, faces, face propagation, angle; parting line/step later) | FT-5 |
| P60 | Revolve PM (axis box with auto single-centerline, Direction1/2 types, angle 360, thin later, contours later, flip side to cut) | FT-5 |
| P61 | Chamfer PM (Angle Distance, Distance Distance sym/asym, Vertex, flip arrow, preview radios; Offset Face/Face Face later) | FT-5 |
| P62 | Linear Pattern PM (directions, spacing/instances, up to reference, features/faces/bodies groups, options) | FT-5 |
| P63 | Circular Pattern PM (axis, instance spacing / equal spacing, Direction 2 symmetric) | FT-5 |
| P64 | Mirror PM (plane + secondary plane, features/faces/bodies, merge/knit, options) | FT-5 |
| P65 | Sweep PM (sketch/circular profile, path, orientation/twist list, guide curves where PartDesign supports) and Loft PM (profiles order/up/down, start/end constraints, centerline) | FT-5 |
| P66 | Hole Wizard PM: Type tab (favorites, hole type buttons, standard incl. AS, type, size, fit, custom sizing, end condition, options) and Positions tab (click on face places points; existing 2D sketch) over PartDesign::Hole | FT-5 |

### Stage D — Extrude and Fillet PMs, the owner's two named workflows (alpha a4) — T2→T3
| Part | Work | → |
|---|---|---|
| P67 | Feature-first flow framework: feature command with no profile → Edit Sketch message PM (planes **and planar faces** pickable) → sketch → exit → PM resumes | FT-1, SK-1, SK-2 |
| P68 | Extrude PM structure: From (Sketch Plane / Surface/Face/Plane / Vertex / Offset), Direction 1 and 2 (end condition combo with dependent boxes), draft, merge result, flip side to cut; live preview | FT-2 |
| P69 | Extrude end conditions complete: Up To Vertex (plane through vertex), Up To Body (shape), Offset From Surface (+ reverse, translate), Through All – Both auto-enables Direction 2, double-click face = Up To Surface | FT-2 |
| P70 | Fillet PM Constant Size: Items box (edges, faces → all edges, features, loops), picks with or without preselection, tangent propagation, Full/Partial/No preview (A steps partial), radius; pushpin | FT-3 |
| P71 | Fillet multiple radius (per-edge callouts → grouped PartDesign fillets under one node), Keep features, Select through faces, Round corners/Overflow mapped where possible | FT-3 |
| P72 | Fillet selection toolbar (pop-up near pointer: connected edges, loop, feature edges, all edges) | FT-3 |
| P73 | Edit Feature re-opens the same PMs with values; tree names Boss-Extrude1/Cut-Extrude1/Fillet1 | FT-6 |

### Stage E — Sketching (alpha a5–a6) — T2→T3
| Part | Work | → |
|---|---|---|
| P74 | Edit Sketch message PM as the default Sketch entry (faces pickable everywhere), Normal To on open, exit keep/discard view rules, Rapid sketch later | SK-1, SK-3 |
| P75 | Modify box dialog (calculator, `=`, globals/functions drop-down, click dimension to insert name, spin/thumbwheel/slider, Ctrl/Alt multipliers, ✓ ✗ Rebuild, Reverse sense, Reset spin increment, Mark for drawing, name field, configuration drop-down); replaces FreeCAD's datum dialog | SK-8 |
| P76 | Line: Insert Line PM (orientation, options, parameters) ↔ Line Properties PM (relations, parameters, additional parameters); chain/single click logic; OK returns to Insert Line | SK-4, SK-5 |
| P77 | Rectangle PM (5 types, add construction lines from corners/midpoints, Shift square, flyout memory) + properties | SK-6 |
| P78 | Circle / Perimeter Circle, Centerpoint / Tangent / 3 Point Arc PMs + properties | SK-4 |
| P79 | Slot PM (4 types, center-to-center/overall, equal slots) + Polygon PM (sides 3–40, inscribed/circumscribed, New Polygon) | SK-4 |
| P80 | Ellipse/Partial/Parabola/Conic, Point, Spline PMs (handles, show curvature), Sketch Text | SK-4 |
| P81 | Smart Dimension own tool: placement-driven orientation, angle quadrant by placement, circle diameter vs linear, across-centerline diameter, arc length/angle by three picks, right-click lock, Esc cancel → Modify box | SK-7 |
| P82 | Shift min/max to arcs + Leaders arc condition; Dimension PM (Value/Leaders/Other tabs) | SK-7 |
| P83 | Automatic relations check (glyphs, inference lines), Ctrl suppress (own handler if needed) | SK-10 |
| P84 | Quick Snaps filter (one-shot, double-click persistent; owner S) | SK-11 |
| P85 | Numeric input mapping (OVP ↔ "Enable on screen numeric input", "Create dimension only when value entered", Add dimensions checkbox in PMs) | SK-12 |
| P86 | Trim PM: Power trim drag trail + extend-by-drag, Corner, Inside/Outside, Closest, construction options | SK-9 |
| P87 | Extend, Split Entities, Construction Geometry toggle, Make Path | SK-13 |
| P88 | Offset Entities PM (distance drag preview, select chain, bi-directional, caps arcs/lines, base/offset construction, add dimensions, reverse) | SK-13 |
| P89 | Convert Entities PM (select chain, select all inner loops, face → edges, Ctrl loop) | SK-13 |
| P90 | Mirror Entities PM (copy, RMB cue) + Dynamic Mirror | SK-13 |
| P91 | Sketch Fillet (keep constrained corners / virtual sharp, dimension each fillet) + Sketch Chamfer PMs | SK-13 |
| P92 | Linear / Circular Sketch Pattern PMs (dimension options, skip, count edit) | SK-13 |
| P93 | Move / Copy / Rotate / Scale / Stretch PM family | SK-13 |
| P94 | Add Relations via context toolbar + Add Relations PM; Display/Delete completion (suppressed, repair dangling, replace) | SK-14 |
| P95 | Sketch status: colours per owner theme, tree prefixes, "Make dimension driven?" prompt | SK-15 |
| P95a | Relation Groups (2026 SP1): one relation applied to many entities, managed as a group in Display/Delete | 91 |

### Stage F — Interaction layer (alpha a7) — T3
| Part | Work | → |
|---|---|---|
| P96 | Wheel zoom rule (zoom-in pulls point toward centre, zoom-out about centre, direction default, Zoom About Screen Center, reverse option, accelerated zoom) | VW-1 |
| P97 | Own orbit: pivot rules (centroid if visible, else picked point), magenta marker, MMB-click entity pivot with green-line pointer, mouse speed | VW-2, VW-3 |
| P98 | Context toolbar engine (fade in/out, placement, also above right-click menu) + tables for face, edge, vertex, feature, sketch, plane, body, sketch entities, component | CTX-1 |
| P99 | Selection breadcrumbs (face → feature → sketch → body → part → mates → assemblies), each crumb selectable | CTX-2 |
| P100 | Drag arrows + rulers + editable callouts for Extrude/Revolve previews (Coin draggers) | FT-2 |
| P101 | Drag modifiers: Ctrl+drag copy feature/sketch entities/components, Shift+drag move feature, Ctrl+drag fillet onto edge | DRG-1 |
| P102 | Box window (blue, solid) / crossing (green, dashed) by direction; lasso (unless 26.3 already provides) | SEL-1 |
| P102a | Shortcut menus per selection type: OK/Cancel on top in PMs, truncated menus with ▾ expand, Customize Menu, selection context toolbar on empty-space right-click | 01 §1.5 |

### Stage G — Own FeatureManager tree (alpha a8) — T4  → **2.0.0 release candidate**
| Part | Work | → |
|---|---|---|
| P103 | Tree model + view: SOLIDWORKS order and folders (History, Sensors, Annotations, Solid Bodies, Equations, Material, planes, Origin), icons, absorbed sketches | FM-3 |
| P104 | Rollback bar (drag, arrow keys, Roll to Previous/End) mapped to Body Tip | FM-1 |
| P105 | Drag reorder via Body.insertObject with "no" cursor for illegal moves | FM-2 |
| P106 | Prefixes (-)/(+)/(?), error/warning icons, What's Wrong dialog, Parent/Child dialog | FM-3 |
| P107 | Rename (slow double-click/F2, name on creation), tree filter box, dynamic highlight, Hide/Show Tree Items options | FM-3 |
| P108 | Feature context menus/toolbars from the tree; flyout tree in PMs uses the new widget | FM-3, PM-8 |
| P109 | **2.0.0 acceptance**: owner walkthrough script (V2 §6) automated as XTEST; stress + perf; docs; release to `stable` | — |

### Stage H — Own geometry features (2.1) — T4/T5
| Part | Work |
|---|---|
| P110 | `geom/` framework: FeaturePython base for additive/subtractive/dress-up features inside a Body (recompute, TNP-safe references via element maps, icons, Edit → PM) |
| P111 | Fillet: Asymmetric (two distances via makeChamfer-like OCC fillet law) + Conic Rho/Radius + Curvature Continuous (spike → decision) |
| P112 | Variable Size Fillet (vertex radii, control points via OCC variable-radius law) + PM with callouts |
| P113 | Setback parameters, Partial edge parameters (start/end offset) |
| P114 | Face Fillet (two face sets; OCC face blend spike) and Full Round Fillet (spike) |
| P115 | FilletXpert-lite (Add / Change: sort by size, resize, remove) |
| P116 | Chamfer Offset Face / Face Face / multi-distance |
| P117 | Extrude Thin Feature (one-direction/mid-plane/two-direction, auto-fillet corners, cap ends) |
| P118 | Selected Contours (region detection in sketch faces, hover-highlight regions) for Extrude/Revolve |
| P119 | Feature Scope + multibody (Merge result off → new body; All/Selected bodies) — design spike first |
| P120 | Pattern extras: Instances to Skip, Vary sketch, Geometry pattern, Instances to Vary, Curve/Sketch/Table driven, Fill pattern |
| P121 | Rib, Dome, Wrap, Thread, Thicken, Move/Copy Bodies, Combine/Split/Delete Body, Move/Delete Face PMs |
| P122 | Instant3D: click face → feature dimensions + handles, ruler snap, Alt snap to geometry, drag contour to extrude (M = mid plane) |

### Stage I — Evaluate, configurations, assemblies (2.2) — T2→T4
| Part | Work |
|---|---|
| P123 | Mass Properties layout update: COM triad (magenta) + tri-colour reference triad, Create Center of Mass feature, Override dialog |
| P124 | Measure dialog (arc conditions, units/precision, XYZ, point-to-point, XYZ relative to, projected on, history, pin, quick copy) |
| P125 | Section View PM (three planes, offsets/rotations, triad drag, caps, selected bodies) |
| P126 | Equations dialog: four views, type-ahead, colour syntax, automatic solve order, link to file, import/export |
| P127 | Add Configuration / Configuration Properties PM, Modify Configurations table, Design Table PM layout (Auto-create/Blank/From file, edit control, options) |
| P128 | Begin Assembly / Insert Components PM (OK → origin fixed, Rotate context toolbar, fix/float options, pushpin, graphics preview) |
| P129 | Mate PM extras: Make first selection transparent, Use for positioning only, Add to new folder, multi-mate |
| P130 | Quick Mates context toolbar; SmartMates (Alt-drag, Tab flips, peg-in-hole) |
| P131 | Move Component extras: Dynamic Clearance, Sound, Highlight faces, Ignore complex surfaces; Physical Dynamics spike |
| P132 | Interference Detection PM (calculate, results with volumes shaded red, ignore, options, non-interfering display) |
| P133 | Exploded View PM, Mirror Components, component patterns (linear/circular/pattern-driven) |

### Stage J — Drawings and remaining polish (2.3) — T2/T3
| Part | Work |
|---|---|
| P134 | Model View PM + Standard 3 View in SOLIDWORKS layout; projected view auto-start |
| P135 | Section View (drawing) PM with Section View Assist cutting lines; Detail, Broken-out, Break, Crop, Auxiliary PMs |
| P136 | Model Items PM, Smart Dimension in drawings, Dimension Palette |
| P137 | Annotations: Note, Balloon/Auto Balloon, Center Mark/Centerline, Hole Callout, Surface Finish, GTOL, BOM table |
| P138 | Fully Define Sketch (spike → own algorithm), SketchXpert, Check Sketch for Feature |
| P139 | Simplified Interface CommandManager mode, Manager Pane tab customisation (2026), dismissed messages |
| P139a | File dialogs: New SOLIDWORKS Document (Novice/Advanced, templates), Open extras (configurations, mode, references), Recent Documents (R) grid, Save As options (copy and continue/open, include references) |
| P140 | Final 2.3 acceptance + docs |

## 5. Release train
| Version | Contents | Gate |
|---|---|---|
| 2.0.0-a1…a8 | Stages A–G on `main` (owner can install from a branch zip) | suite green, stress green |
| **2.0.0** | Stages A–G | all S1 spec IDs pass; owner walkthrough XTEST passes |
| 2.1.0 | Stage H (own geometry) | geometry tests incl. mass-property comparisons |
| 2.2.0 | Stage I (evaluate, configurations, assemblies) | CSWP segment 2/3 practice models reproduce masses/CoM |
| 2.3.0 | Stage J (drawings, remaining) | CSWA drafting recognition list covered |

## 6. 2.0.0 acceptance walkthrough (automated XTEST + Windows checklist)
New part (trimetric) → Sketch with nothing selected, pick Top Plane → Corner Rectangle with
numeric input → Smart Dimension both sides via Modify box → exit → Extrude (Blind 20, drag arrow
to 25, ruler snap) → Sketch on the top face → circle → Extrude cut Through All → Fillet with
nothing selected, pick four edges, radius 3, pushpin, second fillet → change the first extrude
to 40 (sketch on face follows) → rollback above the fillet and back → Mass Properties (MMGS,
2 decimals) → wheel zoom/orbit rules → context toolbar and breadcrumbs on a face → Trim with
power-trim → assembly: Insert Components ✓ at origin, second part, Mate pop-up, Move Component
with collision.

## 7. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Own PMs drift from FreeCAD feature semantics | PM specs + property-mapping tests per PM; Edit Feature round-trip tests |
| Preview recompute lag on large models | debounce, preview on the feature only, Large Model Mode skips live preview |
| Own orbit/zoom fights FreeCAD navigation style | consume only wheel/MMB events we handle; fall back to FreeCAD style when disabled; XTEST on camera matrices |
| Sketcher handler internals change in 26.3 | wrap via commands + document observer, not private APIs; run against 26.3 RC in CI at each stage |
| OCC limits for face/full-round fillets | T5 spikes with explicit go/no-go notes; ship constant/variable first |
| Own tree diverges from document | model rebuilt from document signals; FreeCAD tree kept as hidden debug tab |
| Scope size | stages ship independently; each alpha is usable |

## 8. Bookkeeping
- Tracker: next part = first unfinished part in §4; parts are added to `dev/TRACKER.md` stage by
  stage (the table there lists stages; this file holds part detail).
- Each part: commit + tests; each stage: alpha version bump, CHANGELOG, push `main`.
- Catalogue corrections go into `docs/swref/` first, then the PM spec table, then code.
