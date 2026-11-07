# Gap analysis — CSWA/CSWP scope vs FreeCAD 1.1.4 + FreeWorks 1.0.5

Part P9, 2026-11-07. Requirement IDs come from `docs/CSWA_CSWP_SCOPE.md`. FreeCAD facts were
checked against the pinned FreeCAD 1.1.4 build (command list dumped with all workbenches loaded,
`Mod/Assembly/JointObject.py`, the material library), not from memory.

Legend — **FreeCAD**: ✅ engine does it · 🟡 partly / different workflow · ❌ not available.
**FreeWorks today**: ✅ SW-like · 🟡 mapped (FreeCAD UI) · ⬜ nothing yet.
**Plan**: backlog part that closes it. *own* = FreeWorks code, *map* = name/icon/command mapping,
*UI* = SOLIDWORKS-style PropertyManager over the FreeCAD engine, *add-on* = community project.

## 1. Document set-up and evaluation — CSWA critical (every question ends in a mass or CoM)
| ID | FreeCAD 1.1.4 | FreeWorks today | Gap | Plan |
|---|---|---|---|---|
| R-DOC-1 Units MMGS/IPS, decimals | 🟡 unit schemas (mm/kg/s, MKS, inch…) + global decimals; no per-document "MMGS" | ⬜ | SW unit-system names, per-document decimals in Document Properties | P33 (P12 shows unit choice in Mass Properties) |
| R-DOC-2 Material by SW name | 🟡 material system + `Std_SetMaterial`; library has *Aluminum-6061-T6*, *Steel-C10*… but **no AISI 1020, 1060 Alloy, Alloy Steel, Copper, Brass, ABS** | ✅ 1.1.1: FreeWorks library + Edit Material | SW-named library with SW densities; *Edit Material* on the Material node | **P12** own library (.FCMat files) |
| R-DOC-3 Mass Properties dialog | 🟡 shape volume/CoM/inertia via API, no dialog | ✅ 1.1.1 (override mass not yet) | **output coordinate system**, assembly CoM across links/placements, override mass, SW layout | **P12** |
| R-DOC-4 Measure | ✅ `Std_Measure` (unified measure, 1.0+) | 🟡 mapped (M) | SW Measure panel look, XYZ / centre-to-centre options | P31 polish |
| R-DOC-5 Coordinate system | ✅ `PartDesign_CoordinateSystem` + core datums (1.1) | 🟡 mapped | usable as *Report relative to* target | P12 |
| R-DOC-6 3D section view | ✅ `Std_ToggleClipPlane`, `Part_SectionCut` | 🟡 mapped | SW Section View PM (plane picker, offset) | P31 |
| R-DOC-7 Neutral files | ✅ STEP/IGES/BREP; ❌ native SLDPRT | ✅ File ▸ Open | — (SLDPRT can't be read without SW) | — |

## 2. Sketching
| ID | FreeCAD | FreeWorks | Gap | Plan |
|---|---|---|---|---|
| R-SK-1 Entities | ✅ all incl. slots, polygon, splines; text only in 1.2+ | ✅ mapped with SW names, L/R/C keys | midpoint line, perimeter-circle wording; sketch text | P28 (text appears automatically with FreeCAD 1.2) |
| R-SK-2 Tools | ✅ offset, external geometry/projection (= Convert), trim, extend, split, mirror, arrays, move/rotate/scale | ✅ mapped | Offset PM options (chain, bi-directional, cap ends) | P29 |
| R-SK-3 Relations | ✅ all SW relations except *pierce*/*merge* as names (coincident covers merge) | 🟡 FW_AddRelation + mapped | Add Relations PM, auto-relations display, Display/Delete Relations PM | P28 |
| R-SK-4 Smart Dimension | ✅ `Sketcher_Dimension` contextual; expressions in input | 🟡 mapped (D) | SW Modify box (spin, rebuild, ✓), driven toggle wording | P28 |
| R-SK-5 Fully defined state | ✅ colours + solver messages | 🟡 colours set SW-like, status bar text | "(-)" prefix on under-defined sketches in tree | P30 |
| R-SK-6 Linked dims & equations | ✅ expressions, `Std_VarSet` (global variables), spreadsheets | ⬜ | **Equations dialog** (global variables, equations, functions) over VarSet/expressions | **P26** |

## 3. Part features
| ID | FreeCAD | FreeWorks | Gap | Plan |
|---|---|---|---|---|
| R-PF-1 Extrude boss/cut | 🟡 Pad/Pocket: Blind, Two dims, Through all, Up to first/last/face/shape, symmetric, offset, taper; ❌ thin feature, ❌ Up To Vertex/Body as names, ❌ feature scope | 🟡 FW_ExtrudedBoss/Cut | SW Extrude PM (From, Dir 1/2, end-condition names), thin feature via Thickness | **P22** |
| R-PF-2 Revolve | ✅ Revolution/Groove (angle, symmetric, two angles, up to face) | 🟡 mapped | Revolve PM names | P23 |
| R-PF-3 Sweep | ✅ AdditivePipe/SubtractivePipe (profile, path, twist via Frenet/aux) | 🟡 mapped | Sweep PM; solid-body sweep cut ❌ | P23 |
| R-PF-4 Loft | ✅ AdditiveLoft/SubtractiveLoft; ❌ guide curves | 🟡 mapped | Loft PM; guides via Curves add-on (outside body) | P23 |
| R-PF-5 Fillet/Chamfer | 🟡 constant fillet, chamfer (equal, two distances, distance-angle); ❌ variable / face / full-round | 🟡 mapped (F) | Fillet PM; variable via Part_Fillet (radius per edge, outside body) | P23 |
| R-PF-6 Hole Wizard | 🟡 `PartDesign_Hole`: hole, counterbore, countersink, threads ISO/UTS, positions from sketch points; ❌ slot, pipe tap | 🟡 mapped | Hole Wizard PM with Type / Position tabs | **P24** |
| R-PF-7 Patterns & mirror | 🟡 linear with **two directions and custom spacings** (1.1: `Direction2`, `Occurrences2`, `Spacings`), polar, mirror, MultiTransform; ❌ fill, curve-driven, skip instances | 🟡 mapped | SW Linear Pattern PM (Direction 1/2), skip instances = own wrapper | P25 |
| R-PF-8 Draft / shell / rib | ✅ Draft, Thickness (shell, faces to remove, inward/outward); ❌ multi-thickness faces, ❌ **rib** | 🟡 mapped | **Rib** = own feature (pad of an offset open profile, both directions) | P23 |
| R-PF-9 Reference geometry | ✅ plane (attachment modes cover offset/angle/3-point/normal), axis, point, CS | 🟡 mapped | SW Plane PM wording ("First/Second/Third reference", constraints) ; mate reference ❌ | P25 |
| R-PF-10 Multibody | 🟡 several Bodies per document + `PartDesign_Boolean`, Part booleans; body = one solid | 🟡 combine/split mapped | "Merge result" off = new Body; Solid Bodies folder in tree | P30 |
| R-PF-11 Move/Delete Face | 🟡 `Part_Defeaturing` (delete face); ❌ move face | 🟡 mapped | — (document as closest equivalent) | — |
| R-PF-12 Feature editing | ✅ edit, rollback (MoveTip), reorder (MoveFeatureInTree), suppress (1.1 `Suppressed`) | ✅ mapped, rollback bar ⬜ | rollback **bar** drag in tree | P30 |

## 4. Configurations — CSWP segment 2
| ID | FreeCAD | FreeWorks | Gap | Plan |
|---|---|---|---|---|
| R-CF-1 ConfigurationManager | 🟡 no configurations; closest: **Spreadsheet "Setup Configuration Table"** (enumeration property switches rows) + per-feature `Suppressed` | ⬜ | ConfigurationManager panel: list/add/activate configurations backed by a configuration table; dimension "This configuration / All" | **P27** |
| R-CF-2 Design table | 🟡 spreadsheet configuration table (rows = configs, columns = aliases bound by expressions) | ⬜ | Design Table importer (CSV/XLSX → configuration table + expression bindings), `$STATE` columns → `Suppressed` | **P27** |
| R-CF-3 Mass per configuration | ✅ follows recompute | 🟡 | — | P27 test |

## 5. Assemblies
| ID | FreeCAD | FreeWorks | Gap | Plan |
|---|---|---|---|---|
| R-AS-1 Insert components | ✅ `Assembly_InsertLink`, first part grounded, `InsertNewPart` (1.1) | 🟡 mapped; instance names `Part<1>` + `(f)` (1.1.4) | Begin Assembly / Insert Components PM, instance names `Part<1>`, (f) prefix | **P16** |
| R-AS-2 Standard mates | 🟡 joints: Fixed (=Lock), Revolute, Cylindrical, Slider, Ball, **Distance** (0 = coincident/tangent/concentric by geometry pair), Parallel, Perpendicular, Angle; flip via *Reverse* | ✅ 1.1.2 Mate PM + pop-up toolbar | **Mate PM** that takes two selections and picks the SW mate (coincident/concentric/tangent/distance/angle…), alignment aligned/anti-aligned, pop-up mate toolbar | **P13, P14** |
| R-AS-3 Advanced mates | 🟡 limits on Cylindrical/Slider (length) and Revolute/Cylindrical (angle); ❌ width, symmetric, profile center, path, linear coupler | 🟡 1.1.3: Width (static), Limit Distance/Angle on motion joints | Limit mates via joint limits; **width / symmetric / profile center** = own constructions (computed distance joints) | **P15** |
| R-AS-4 Mechanical mates | 🟡 Gears, Belt, RackPinion, Screw; Revolute ≈ Hinge; ❌ cam, slot, universal joint | ✅ 1.1.3 Hinge, Gear, Rack Pinion, Screw in Mate PM | Hinge = Revolute (+ angle limit); slot ≈ Slider + limits; cam/universal ❌ (document) | P15 |
| R-AS-5 Mates folder | 🟡 "Joints" group | ✅ 1.1.4 Mates folder, SW mate names, Edit Mate (no per-component mate list) | rename to *Mates*, show mates under components, over-defined warnings | P16 |
| R-AS-6 Move/Rotate, collision | 🟡 drag with solver; `Std_TransformManip`; ❌ collision detection | 🟡 mapped | **Collision detection while dragging** (own: stop on first boolean common > ε, highlight faces) | **P17** |
| R-AS-7 Sub-assemblies | ✅ assembly in assembly (rigid); flexible ❌ | 🟡 | insert sub-assembly from file, rigid/flexible wording | P17 |
| R-AS-8 Replace components | 🟡 `Std_LinkReplace` (joints may lose references) | ⬜ | Replace Components PM that re-maps joint references by face/edge type | **P17** |
| R-AS-9 Interference detection | ❌ native command | ✅ FW_Interference (pairwise volumes) | SW panel look; coincident-as-interference option | P17 |
| R-AS-10 Assembly features | ❌ (cuts must be made in parts) | ⬜ | assembly cut = own feature applying a cut to selected components (feature scope) | later (v1.6) |
| R-AS-11 In-context / external refs | 🟡 edit part in place, cross-document links, SubShapeBinder | 🟡 | `->` markers, lock/break references | P30 |
| R-AS-12 Assembly mass props | 🟡 API only | ✅ 1.1.1 | include link placements, sub-assemblies, CS output | **P12** |
| R-AS-13 Suppression states | 🟡 visibility, `Suppressed` property, no lightweight | 🟡 | SW wording | P16 |
| R-AS-14 Exploded view & BOM | ✅ `Assembly_CreateView` (exploded), `Assembly_CreateBom` | 🟡 mapped | Explode PM wording, BOM in drawing | P17, P20 |

## 6. Drawings
| ID | FreeCAD | FreeWorks | Gap | Plan |
|---|---|---|---|---|
| R-DR-1 Sheets | ✅ templates ISO/ANSI, scale, 1st/3rd angle | 🟡 mapped | SW-style sheet formats with title-block fields (part number, material, mass) | **P18** |
| R-DR-2 Standard views | ✅ ProjectionGroup (= Standard 3 View / projected), View (= Model View); ❌ relative / predefined / empty views as such | 🟡 mapped | Model View PM workflow (pick part → orientation → place; then drag to project) | **P19** |
| R-DR-3 Derived views | ✅ Section, ComplexSection (aligned/offset), Detail, BrokenView, ClipGroup (≈ crop); 🟡 auxiliary (view direction from edge); ❌ broken-out section, alternate position, removed section | 🟡 mapped | Auxiliary view from edge (own helper); broken-out & alternate position ❌ (document) | P19 |
| R-DR-4 Annotations | ✅ dimensions (all types, chain/coord), centerlines/marks, notes, balloons, surface finish, weld, GD&T via symbols, hole/shaft fits, BOM via spreadsheet view; ❌ model items import, hole callout, hole table, revision table | 🟡 mapped | **Model Items** (import sketch dims as drawing dims), hole callout from Hole feature data, revision table | **P20** |
| R-DR-5 View display | ✅ hidden lines, smooth (tangent) edges, shaded via `CoarseView`/`ActiveView`, lock view | 🟡 | SW display-style buttons per view | P21 |

## 7. Conclusions
1. **Biggest CSWA risk is evaluation, not modeling.** FreeCAD can model every CSWA part, but
   a CSWA answer needs the SW material by name and a Mass Properties dialog that reports in grams
   relative to the right coordinate system. → P12 stays first.
2. **Assemblies are the second risk (120 of 240 CSWA points).** FreeCAD's joints are kinematic
   (revolute, slider…) while SOLIDWORKS mates are geometric (coincident, concentric…). The
   FreeWorks Mate PM must translate *selection pairs* into joints — the engine is capable
   (Distance joint with 0 covers coincident/tangent/concentric). → P13–P15 as planned.
3. **CSWP segment 2 (configurations) has no FreeCAD equivalent UI** but the engine pieces exist
   (spreadsheet configuration table + `Suppressed`). → P27 is feasible, moved up to v1.2 together
   with equations (P26) because CSWP segments 1–2 depend on both.
4. Items that stay ❌ (documented, not faked): assembly features, cam/universal-joint mates,
   broken-out section, alternate position views, move face, guide-curve lofts inside a body,
   variable-radius fillets inside a body.

## 8. Re-prioritised backlog (applied to dev/TRACKER.md)
| Version | Parts |
|---|---|
| v1.1 | P10 community survey, P11 release |
| v1.2 | P12 materials + Mass Properties · P13–P15 mates · P16 assembly tree · P17 collision/replace/sub-assemblies |
| v1.3 | P26 equations · P27 configurations + design tables · P22 Extrude PM · P24 Hole Wizard PM |
| v1.4 | P18–P21 drawings |
| v1.5 | P23, P25 remaining part PMs · P28–P29 sketch · P30–P34 GUI polish |
