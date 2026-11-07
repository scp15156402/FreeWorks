# 12 — Evaluate (Mass Properties, Measure, Section View, Interference, Section Properties)

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.

## 12.1 Mass Properties  (Evaluate tab · Tools > Evaluate > Mass Properties)  [H 2011–2024, B CATI, Hawk Ridge]
A **non-modal dialog** (not a PM) — it stays open while you select other things.
- **Selected items** box: components or solid bodies to evaluate; **nothing selected = whole
  part/assembly**. Change the selection and click **Recalculate** without closing. [H 2022]
- Top buttons: **Print** · **Copy to Clipboard** · **Recalculate** · **Options…** (Mass/Section
  Property Options: **Use document settings / Use custom settings** — length, mass, volume units
  and decimal places, scientific notation; **Material Properties** density; **Accuracy level**
  slider (speed vs precision); **Show output coordinate system in corner of window**) ·
  **Override Mass Properties…** (mass, centre of mass (X/Y/Z, *As defined in* a coordinate
  system), moments of inertia; not for multiple items or bodies of a multibody part; the COM
  point icon changes when overridden).
- **Report coordinate values relative to:** drop-down — *-- default --* (origin) or any
  **Coordinate System** in the model (renamed from "Output coordinate system" in 2013). [H 2013]
- **Include hidden bodies/components** · **Create Center of Mass feature** (adds a COM point to
  the tree; usable for reference, not driving, dimensions) · **Show weld bead mass** (weldments).
- **Results** (text, document units unless overridden): **Density**, **Mass**, **Volume**,
  **Surface area**, **Center of mass (X, Y, Z)**, **Principal axes of inertia and principal
  moments of inertia** (taken at the centre of mass: Ix, Iy, Iz with direction vectors, Px, Py,
  Pz), **Moments of inertia taken at the center of mass and aligned with the output coordinate
  system** (Lxx…Lzz), **Moments of inertia taken at the output coordinate system** (Ixx…Izz).
  Components with overridden mass are listed at the bottom (assemblies).
- Graphics: a **single-colour (pink/magenta) triad at the centre of mass** showing principal
  axes, and a **tri-colour reference triad** at the origin (or the chosen coordinate system / in
  the corner). [H 2021, B Hawk Ridge]
- Option *Update mass properties while saving document* (System Options > Performance) caches
  the values. [H]
- Mass properties can feed custom/configuration properties ("SW-Mass@Part1.SLDPRT"). [H]
- CSWA/CSWP use: mass in grams to 2 decimals (MMGS), COM relative to a coordinate system. FreeWorks
  already has an engine (massprops.py) — match these fields and layout.

## 12.2 Measure  (Evaluate tab · Tools > Evaluate > Measure; owner shortcut **M** [O])  [H 2013–2024, B CATI, Visiativ]
Non-modal floating dialog, title "Measure - <doc>".
- **Toolbar icons** (left to right): **Arc/Circle Measurements** (*Center to Center* (default) /
  *Minimum Distance* / *Maximum Distance* / *Custom Distance* — per-arc condition) · **Units/
  Precision** (*Use document settings* / *Use custom settings*: length unit, decimals, angular
  unit, dual units, **accuracy** level) · **Show XYZ Measurements** (dX, dY, dZ in the graphics
  area; off → only the minimum distance) · **Point-to-Point** (measure between the exact clicked
  points) · **XYZ Relative To** (Part Origin or a coordinate system; only when one exists) ·
  **Projected On** (*None* / *Screen* / *Select Face/Plane* → shows **Projection** and **Normal**
  distances; also projected area) · **Measurement History** (all measurements of the session) ·
  **Create Sensor** · **Pin** (keep the dialog; when unpinned **Esc** closes it) · **expand/
  collapse** results · **Increase/Decrease Font Size** · **Quick Copy Setting** (*Turn on quick
  copy*: hovering the result highlights *number only* / *number and units* to copy). [H]
- **Input box** lists up to six selections; selections need no Ctrl (each click adds). Click
  empty space / right-click > Clear Selections to restart. [H][B]
- Results by selection: vertex/sketch point → **X, Y, Z**; edge → **length**; circle → **diameter**
  (and centre), arc → **radius**, arc length; face → **area** and perimeter (several faces → total
  area); two entities → **distance** (min/centre per arc setting) and **angle**; two parallel faces
  → normal distance; with XYZ on → dX, dY, dZ. [B Visiativ, K]
- **Graphics**: a callout box at the selection with the value(s) and dimension-like lines for the
  distance and dX/dY/dZ (colour coded). [K]
- **When Measure is not open, common measurements of the current selection appear in the status
  bar** (edge length, face area, distance between two picks …). [H 2020]

## 12.3 Section View  (Heads-up toolbar · View > Display > Section View)  [H 2024 offset options, K rest]
PM "Section View":
- **Section Method** (2022+?): *Planar* / *Zonal* (assemblies) [K].
- **Section 1**: reference plane/face (default **Front**; buttons Front / Top / Right), **Reverse
  section direction**, **Offset distance**, **X rotation**, **Y rotation**, **Edit Color**;
  Offset Method *Reference Plane* (default) / *Selected Plane*. [H 2024]
- **Section 2**, **Section 3** checkboxes (up to three planes).
- **Section by body/component** (selected bodies included/excluded), **Show section cap**, **Keep
  cap color**, **Graphics-only section** (fast, no geometry), **Preview**, **Save** (saves as a
  named view), **Show only highlighted?** [K].
- Graphics: the section plane with a **triad** (drag the arrow to offset, rings to rotate); cap
  faces shown in a colour/hatch. Toggling Section View again turns it off; *Section view stays
  active when the PM closes*. [K]

## 12.4 Interference Detection (assemblies; also Clearance Verification, Hole Alignment)  [H 2010–2025, B CATI, GrabCAD]
Evaluate tab / Assembly tab / Tools > Interference Detection. PM:
- **Selected Components**: *Components to Check* (default: the **top-level assembly** is
  preselected; clear it to pick parts/subassemblies) + **Calculate** button.
- **Excluded Components** (checkbox group): components box, *Hide excluded components from view*,
  *Remember excluded components*.
- **Results**: list "Interference1 (volume)…", expand → the two component names; **select an
  interference → its volume is shaded red** in the graphics area; right-click → *Zoom to
  selection*, *Ignore* / *Un-Ignore* (button too); **Component view** toggle (list by component
  instead of number); ignored items grey (when shown).
- **Options**: *Treat coincidence as interference* · *Show ignored interferences* · *Treat
  subassemblies as components* · *Include multibody part interferences* · *Include surface
  bodies* (2024+; no volume) · *Make interfering parts transparent* · *Create fasteners folder*
  (Toolbox fasteners) · *Create matching cosmetic threads folder* · *Ignore hidden bodies/
  components* (incl. isolated-hidden).
- **Non-interfering Components**: *Wireframe / Hidden / Transparent / Use current*.
- Coincident-curved-face false positives possible (facets). [H 2025]
- FreeCAD note: no equivalent PM; Part Common/check geometry can compute overlaps — FreeWorks
  candidate (CSWP segment 3 lists interference detection).

## 12.5 Section Properties, Check, Draft/Thickness/Curvature analysis [K]
- **Section Properties** (select planar faces or a sketch): area, centroid, moments of area;
  dialog like Mass Properties.
- **Check** (Tools > Evaluate > Check): invalid faces/edges, short edges, min radius, convex/
  concave curvature …
- **Draft Analysis**, **Undercut Analysis**, **Thickness Analysis**, **Curvature**, **Zebra
  Stripes**, **Deviation Analysis**, **Geometry Analysis** — PMs with colour plots (lower
  priority for CSWA/CSWP).
- **Performance Evaluation**, **Statistics**, **Equations** (Evaluate tab button) — see 13.
