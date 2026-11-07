# 09 — Patterns and Mirror (features)

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.

Common behaviour [H 2012–2025]:
- Preselect the seed feature(s) in the tree or graphics area, then the pattern command — the
  seed fills **Features to Pattern**; the first direction box is active.
- Pattern PMs (2018+) group the seed selection into **Features and Faces** and **Bodies**
  checkbox groups (+ reference geometry: planes/axes can be patterned, one per pattern; a
  plane's sketch is not patterned).
- **Instances to Skip**: the pointer changes over instance markers (pink dots); click to skip —
  the instance's coordinates appear; click again to restore.
- **Options**: **Vary sketch** (instances re-solve their sketch, follow the path geometry) ·
  **Geometry pattern** (copy faces/edges only — faster, no end-condition re-solve; not for
  features whose faces merge with the part) · **Propagate visual properties** (colours,
  textures, cosmetic threads) · **Full preview** (computed geometry incl. end conditions) /
  **Partial preview** (seed geometry at each location).
- **Instances to Vary** (feature seeds only): Direction increments for spacing and for chosen
  **seed dimensions** (click dimensions in the graphics area → table with Increment column);
  **Modified Instances** list — left-click an instance marker → **Modify Instance** → override
  spacing/dimensions in a callout; right-click list > Delete / Clear All.
- **Feature Scope** (multibody): All bodies / Selected bodies (+ Auto-select / Bodies to Affect).
- Numeric fields take `=` equations.
- Tree names: LPattern1, CirPattern1, Mirror1, … (pattern instances listed under the feature).

## 9.1 Linear Pattern  [H 2025 (search snippet), K]
**Direction 1**: **Pattern Direction** box (linear edge, line, axis, **dimension**, planar or
conical faces/surfaces, circular edges, reference planes) + Reverse Direction · **Spacing and
instances** (Spacing + Number of Instances, incl. the seed) or **Up to reference** (Reference
Geometry, Offset distance, Reverse offset direction, **Centroid** / **Selected reference**) ·
graphics: an **arrow and callouts** "Spacing"/"Instances" that can be clicked to edit.
**Direction 2**: same + **Symmetric** (pattern both ways in Direction 2) + **Pattern seed only**.
Then Features and Faces, Bodies, Instances to Skip, Feature Scope, Options, Instances to Vary.

## 9.2 Circular Pattern  [H 2013–2025]
**Direction 1**: **Pattern Axis** (axis, circular edge, linear edge/sketch line, cylindrical or
revolved face/surface, angular dimension) + Reverse Direction · **Instance spacing** / **Equal
spacing** (sets Angle to 360°) · **Angle** · **Number of Instances**. **Direction 2** checkbox
(**Symmetric**, own spacing/angle/count). Features and Faces (**Features to Pattern**, **Faces to
Pattern** — pattern must stay within the same face/boundary), Bodies (**Solid/Surface Bodies to
Pattern**), reference geometry, Instances to Skip, Feature Scope, Options, Instances to Vary
(spacing increment is cumulative: 1.5 + 0.3 → 1.8, 2.1 … [H]).

## 9.3 Mirror  [H 2013–2024]
PM "Mirror" (Features tab; Insert > Pattern/Mirror > Mirror; assemblies: Assembly Features >
Mirror):
- **Mirror Face/Plane** (plane or planar face; Select Other if hidden) · **Secondary Mirror
  Face/Plane** (2022+: mirror about two planes in one feature) + **Mirror seed only** (when the
  second plane is perpendicular to the first).
- **Features to Mirror** (graphics or the flyout tree) · **Faces to Mirror** (parts; imported
  geometry) · **Bodies to Mirror** (parts; **Solid/Surface Bodies to Mirror** — the mirrored body
  attaches at the selected face).
- **Options**: **Geometry Pattern** (features/faces only; faster; not for features whose faces
  merge with the part) · **Merge solids** (bodies; cleared → a separate mirrored body) · **Knit
  surfaces** (surface bodies) · **Propagate visual properties** · **Full preview / Partial
  preview**.
- **Feature Scope** (multibody).
- Order of picks is free: preselect the plane and features before clicking Mirror and both boxes
  fill. [K]

## 9.4 Other feature patterns [K — verify]
- **Curve Driven Pattern**: Direction 1 curve/edge/sketch, Reverse, Number, Spacing / Equal
  spacing, **Curve method** Transform curve / Offset curve, **Alignment method** Tangent to curve /
  Align to seed, **Face normal** (3D curves); Direction 2. [H component-pattern version]
- **Sketch Driven Pattern**: Reference Sketch, **Reference point** Centroid / Selected point.
- **Table Driven Pattern**: dialog (not a PM): Read a file from, Reference point (Selected point /
  Centroid), Coordinate system, table of X/Y per instance, Save/Save As, Geometry pattern,
  Propagate visual properties.
- **Fill Pattern**: Fill Boundary (sketch/face), **Pattern Layout** Perforation / Concentric /
  Square / Polygon (instance spacing, stagger angle, margins, pattern direction, number of sides),
  Features to Pattern or **Create seed cut** (Circle / Square / Diamond / Polygon with size and
  vertex), Instances to Skip, Options.
- **Variable Pattern** (2017+): table of seed dimensions per instance, "Create table" for
  driving dimensions.
- Assemblies: Linear/Circular/Pattern-Driven/Sketch-Driven/Curve-Driven/Chain Component Patterns,
  Mirror Components — see 14.
