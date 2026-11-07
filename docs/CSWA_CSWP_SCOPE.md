# CSWA + CSWP scope — what FreeWorks must cover

Researched 2026-11-07 (part P8). This is the **target scope** for FreeWorks: everything a
CSWA/CSWP-level user does in SOLIDWORKS, with the workflow details that matter. Each line has a
requirement ID (`R-…`) that `docs/GAP_ANALYSIS.md` maps to FreeCAD 1.1 / FreeWorks status.

> The real exams require SOLIDWORKS itself (they ship SOLIDWORKS files and are taken through the
> 3DEXPERIENCE virtual tester). FreeWorks' goal is that a CSWA/CSWP user can do the same *work*
> with the same commands, names, panels and results (masses must match to the second decimal).

## 1. Exam structure (official)

### CSWA — SOLIDWORKS Design Associate
- 3 hours, 14 questions, 240 points, pass at 165 (≈70 %). Can be taken in two 90-minute parts.
- Categories:

| Category | Questions × points | Content |
|---|---|---|
| Drafting competencies | 3 × 5 | Identify drawing view types / drafting functions (multiple choice) |
| Basic part creation & modification | 2 × 15 | Sketch, Extruded Boss, Extruded Cut, change key dimensions |
| Intermediate part creation & modification | 2 × 15 | Sketch, Revolved Boss, Extruded Cut, Circular Pattern |
| Advanced part creation & modification | 3 × 15 | Sketch, Offset, Extrude Boss/Cut, key-dimension changes, harder geometry changes |
| Assembly creation & modification | 4 × 30 | Place base part, mates, change key assembly parameters, report centre of mass |

- Typical question header: *Unit system MMGS (millimeter, gram, second), 2 decimal places, part
  origin arbitrary, material e.g. AISI 1020 Steel (0.0079 g/mm³) / 6061 Alloy (0.0027 g/mm³) /
  1060 Alloy / Copper (0.0089 g/mm³) / Alloy Steel; A = 81, B = 57, C = 43 …* → answer: **mass in
  grams** (parts) or **centre of mass X/Y/Z** (assemblies, relative to a given coordinate system or
  the assembly origin). Answers are multiple choice within 1 %.
- Hands-on areas listed by Dassault: sketch entities (line, rectangle, circle, arc, ellipse,
  centerline), sketch tools (offset, convert, trim), sketch relations, boss/cut (extrude, revolve,
  sweep, loft), fillets/chamfers, linear/circular/fill patterns, dimensions, end conditions,
  mass properties, materials, inserting components, standard mates, reference geometry (planes,
  axes, mate references), drawing views, annotations.

### CSWP — SOLIDWORKS Design Professional (three segments, any order)

| Segment | Time / pass | Content |
|---|---|---|
| 1 Part modeling from a drawing | 70 min, 75/105 | Model from a drawing; link dimensions; **equations / global variables**; change parameters in stages keeping design intent; modify geometry into a more complex part; mass properties |
| 2 Configurations & design tables | 50 min, 77/104 | Create configurations from others; change configurations; change/re-order features of a given part; **design table**; mass properties per configuration |
| 3 Assembly modeling | 80 min, 77/109 | Create assembly; add parts; **insert sub-assemblies**; **replace a component**; basic + advanced mates; **collision detection** while moving; **interference detection**; **create a coordinate system**; mass properties **relative to that coordinate system** |

Official "standard tools covered" list for CSWP adds to CSWA: sweeps, lofts, draft, shell,
Hole Wizard, rib, mirror, fill pattern, feature scope, Move/Delete Face, multibody parts, mate
references, design tables, in-context features, suppression states, Move/Rotate Component,
assembly features, external references, materials, dimensions & model items.

## 2. Requirements

### 2.1 Document set-up and evaluation (both exams, every question)
| ID | Requirement | SOLIDWORKS detail that matters |
|---|---|---|
| R-DOC-1 | Unit systems | Tools ▸ Options ▸ Document Properties ▸ Units: **MMGS**, IPS, CGS, MKS; decimal places (2) |
| R-DOC-2 | Material assignment | Right-click *Material* in FeatureManager ▸ Edit Material; SOLIDWORKS library names (AISI 1020, Alloy Steel, 6061 Alloy, 1060 Alloy, Copper, Brass, ABS, Cast Alloy Steel, Titanium…); custom density |
| R-DOC-3 | Mass Properties dialog | Evaluate ▸ Mass Properties: density, mass (g), volume, surface area, centre of mass X/Y/Z, principal axes & moments, moments at CoM and at output coordinate system; **Report coordinate values relative to:** dropdown; Override mass; units from document; Recalculate; Copy to clipboard |
| R-DOC-4 | Measure | Evaluate ▸ Measure: distance/angle/radius/area between picks, XYZ, centre-to-centre, min/max |
| R-DOC-5 | Reference coordinate system | Insert ▸ Reference Geometry ▸ Coordinate System (origin + axis directions from edges/points) |
| R-DOC-6 | Section view (3D) | View ▸ Display ▸ Section View, used to check internal geometry |
| R-DOC-7 | Opening neutral files | STEP/IGES/Parasolid import as base part (exam ships native files; STEP is our substitute) |

### 2.2 Sketching
| ID | Requirement | Detail |
|---|---|---|
| R-SK-1 | Entities | Line (+ centerline, midpoint line), corner / center / 3-point rectangles, parallelogram, slot types, circle / perimeter circle, center / tangent / 3-point arcs, ellipse, polygon, spline, point, fillet/chamfer (sketch), text |
| R-SK-2 | Tools | Offset (with chain/bi-directional/cap ends), Convert Entities, Trim (power trim, trim to closest), Extend, Mirror, linear/circular sketch pattern, Move/Copy/Rotate/Scale, construction toggle |
| R-SK-3 | Relations | Automatic relations while sketching (inference lines); Add Relations PropertyManager: horizontal, vertical, collinear, coincident, midpoint, parallel, perpendicular, tangent, concentric, equal, symmetric, fix, pierce, merge; Display/Delete Relations |
| R-SK-4 | Smart Dimension | One tool for linear/angular/radial/diameter dimensions; driven vs driving; edit-in-place Modify box accepting `=` expressions and global variables |
| R-SK-5 | Fully defined state | Blue/black/red colours, "Under Defined / Fully Defined" status bar, (-) / (+) prefix in FeatureManager |
| R-SK-6 | Linked dimensions & equations | Link Values (shared names), Equations dialog with **Global Variables**, functions, equations in sketch dimensions |

### 2.3 Part features
| ID | Requirement | Detail |
|---|---|---|
| R-PF-1 | Extruded Boss/Base & Cut | From sketch plane/surface/vertex/offset; end conditions Blind, Through All, Through All-Both, Up To Next, Up To Vertex, Up To Surface, Offset From Surface, Up To Body, Mid Plane; Direction 2; draft; thin feature; **feature scope**; selected contours |
| R-PF-2 | Revolved Boss & Cut | Axis from centerline/edge; One-Direction / Mid-Plane / Two-Direction; thin |
| R-PF-3 | Swept Boss & Cut | Profile + path; twist; guide curves; solid-sweep cut |
| R-PF-4 | Lofted Boss & Cut | Profiles, guide curves, start/end constraints, centerline |
| R-PF-5 | Fillet / Chamfer | Constant, variable, face, full-round fillets; chamfer angle-distance, distance-distance, vertex; FilletXpert-like selection by feature/face |
| R-PF-6 | Hole Wizard | Counterbore, countersink, hole, tapped, pipe tap, legacy, slot; standards ANSI/ISO; position on face via sketch points |
| R-PF-7 | Patterns & mirror | Linear (2 directions, instances to skip), circular (equal spacing), fill pattern, curve-driven, mirror features/bodies |
| R-PF-8 | Draft, shell, rib | Neutral-plane draft; shell inward/outward with multi-thickness faces; rib from open sketch |
| R-PF-9 | Reference geometry | Plane (offset, angle, 3-point, mid-plane, normal-to-curve), axis, point, coordinate system, mate reference |
| R-PF-10 | Multibody | Merge result on/off, Combine (add/subtract/common), Delete/Keep Body, Split, Solid Bodies folder |
| R-PF-11 | Direct edits | Move Face, Delete Face (delete & patch / delete & fill) |
| R-PF-12 | Feature editing | Edit Feature / Edit Sketch, rollback bar, reorder by drag, suppress/unsuppress, parent/child, What's Wrong |

### 2.4 Configurations (CSWP segment 2)
| ID | Requirement | Detail |
|---|---|---|
| R-CF-1 | ConfigurationManager | Add/derive/copy configurations, activate by double-click, per-configuration dimension values ("This configuration / All / Specify"), suppression state per configuration |
| R-CF-2 | Design table | Excel table: rows = configurations, columns = `D1@Sketch1`, `$STATE@Feature`, `$PARTNUMBER`; edit table → configurations update |
| R-CF-3 | Per-configuration mass properties | Switch configuration → Mass Properties updates |

### 2.5 Assemblies (CSWA 4 × 30 pts, CSWP segment 3)
| ID | Requirement | Detail |
|---|---|---|
| R-AS-1 | Insert components | Begin Assembly PropertyManager on new assembly; first part fixed at origin `(f)`; Insert Components (browse, keep visible, multiple instances); drag from file explorer |
| R-AS-2 | Standard mates | Coincident, Parallel, Perpendicular, Tangent, Concentric, Lock, Distance, Angle; aligned / anti-aligned; flip; mate pop-up toolbar on selection |
| R-AS-3 | Advanced mates | Profile Center, Symmetric, Width (centered / free / dimension / percent), Path, Linear/Linear Coupler, Limit distance, Limit angle |
| R-AS-4 | Mechanical mates | Cam, Slot, Hinge, Gear, Rack Pinion, Screw, Universal Joint |
| R-AS-5 | Mates folder | Mates listed under each component and in the Mates folder; edit, suppress, delete, flip; over-defined errors shown |
| R-AS-6 | Move/Rotate Component | Free drag, along assembly XYZ, by delta XYZ / to XYZ; **Collision Detection** (stop at collision, highlight faces, sound), physical dynamics |
| R-AS-7 | Sub-assemblies | Insert assembly as component, rigid/flexible, dissolve, form new sub-assembly |
| R-AS-8 | Replace Components | Replace a part with another, re-attach mates (Mated Entities dialog) |
| R-AS-9 | Interference Detection | Selected components, results list with volumes, coincidence as interference, hide/transparent display |
| R-AS-10 | Assembly features | Hole/cut through several components with feature scope |
| R-AS-11 | In-context / external references | Edit Part inside assembly, references to other components (`->` marker), lock/break references |
| R-AS-12 | Assembly mass properties | CoM of whole assembly relative to assembly origin or a coordinate system |
| R-AS-13 | Suppression states | Resolved / lightweight / suppressed components, hide/show |
| R-AS-14 | Exploded view & BOM | Explode steps, explode lines; BOM table in drawing (CSWA-level awareness; exam uses mates more) |

### 2.6 Drawings (CSWA drafting competencies; CSWP awareness)
| ID | Requirement | Detail |
|---|---|---|
| R-DR-1 | New drawing | Sheet format / size (A-, B- … A4, A3) with title block; sheet properties (scale, projection: first/third angle) |
| R-DR-2 | Standard views | Standard 3 View, Model View (named views, isometric), Relative View, Predefined View, Empty View, View Palette |
| R-DR-3 | Derived views | Projected, Auxiliary, Section (+ half section, offset via Section View Assist), Aligned Section, Detail, Crop, Break, Broken-out Section, Alternate Position, Removed Section |
| R-DR-4 | Annotations | Model Items import, Smart Dimension in drawings, centerlines, center marks, notes, GD&T symbols, surface finish, hole callout, balloons, tables (BOM, hole table, revision table) |
| R-DR-5 | View display | Hidden lines visible/removed, shaded, tangent edges, scale per view, alignment, lock view focus/position |

## 3. Where this leads
- `docs/GAP_ANALYSIS.md` (P9) maps every requirement to FreeCAD 1.1.4 / FreeWorks status and the
  backlog part that closes it.
- Community add-ons that cover some gaps are surveyed in `docs/COMMUNITY.md` (P10).

## Sources
- [SOLIDWORKS Design Professional (CSWP) — official page](https://www.solidworks.com/certifications/solidworks-design-professional)
- [SOLIDWORKS Design Associate (CSWA) — official page](https://www.solidworks.com/certifications/mechanical-design-cswa-mechanical-design)
- [CSWA academic version — question breakdown](https://www.solidworks.com/sw/support/cswa-academic.htm)
- [CSWP sample exam guide (Segment 1)](https://sites.ualberta.ca/~dnobes/CSWA/CSWP_Material/CSWP_SampleExam_2.pdf)
- [CSWA sample exam 2007 (GoEngineer mirror)](https://cdn.goengineer.com/cswasampleexam2007.pdf)
- [SOLIDWORKS Help — types of mates](https://help.solidworks.com/2021/english/SolidWorks/sldworks/r_Types_of_Mates_SWassy.htm)
- [SOLIDWORKS Help — derived drawing views](https://nexthelp.solidworks.com/2024/english/SolidWorks/sldworks/c_derived_drawing_views.htm)
- [SOLIDWORKS Help — Drawing toolbar](https://help.solidworks.com/2023/English/SolidWorks/sldworks/r_Drawing_Toolbar.htm)
- [GoEngineer — standard, advanced and mechanical mates](https://www.goengineer.com/blog/introduction-to-solidworks-mates)
- [FreeCAD 1.1 release notes](https://wiki.freecad.org/Release_notes_1.1)
