# 11 — Multibody parts and direct editing (CSWP: multibody, Move/Delete Face)

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.

## 11.1 Creating and seeing bodies [K]
- A boss with **Merge result** cleared (or not touching) creates another body; the tree shows
  **Solid Bodies(n)** — expand to list bodies (named after the last feature that touched them,
  e.g. "Boss-Extrude2"); select a body → hide/show, isolate, appearance, delete, material per
  body (2015+? "Material <per body>").
- **Feature Scope** decides which bodies a cut/boss affects (see 07).
- Right-click Solid Bodies > *Show bodies / Hide bodies*, *Isolate*, *Add to New Folder*.

## 11.2 Move/Copy Bodies  [H 2024]
Features tab or Insert > Features > Move/Copy. Two pages switched by buttons at the bottom:
- **Translate/Rotate**: **Bodies to Move/Copy** (solid, surface or graphics bodies; selected
  bodies move as one; others are fixed); **Copy** + **Number of Copies** (translate/rotate only);
  **Translate** — reference entity (edge/vertex pair) + distance, or **Delta X/Y/Z**; **Rotate** —
  reference (edge/axis) + angle, or X/Y/Z rotation origin + angles; a **triad** appears at the
  bounding-box centre (drag arrows/rings) when Translate/Rotate is clicked; equations allowed.
- **Constraints**: **Bodies to Move**; **Mate Settings** — mate types (Coincident, Parallel,
  Perpendicular, Tangent, Concentric, Distance, Angle), **Mate Alignment** *Aligned /
  Anti-Aligned*; **Mates** box lists the mate set; several mate sets allowed (may conflict).
- Tree: Body-Move/Copy1.

## 11.3 Combine, Intersect, Split, Delete/Keep Body [K — verify]
- **Combine**: Operation Type *Add / Subtract / Common*; Main Body + Bodies to Combine (or to
  Subtract); **Show Preview**. Tree: Combine1.
- **Intersect**: Selections (bodies, surfaces, planes) → *Create internal regions* / *Cap planar
  openings on surfaces*; **Intersect** button; Regions to Exclude list; *Merge result*,
  *Consume surfaces*.
- **Split**: Trim Tools (planes, surfaces, sketches) → **Cut Part** → resulting bodies list with
  checkboxes, *Save as* file names, *Consume cut bodies*, *Propagate visual properties*.
- **Delete/Keep Body**: Type *Delete Bodies / Keep Bodies*, bodies box.
- **Insert Part**, **Mirror bodies** (Mirror PM Bodies group), **Pattern bodies**.

## 11.4 Direct editing (Direct Editing tab / Insert > Face)  [K — verify]
- **Move Face**: *Offset* / *Translate* / *Rotate*; Faces box; distance/direction/axis; triad for
  Translate/Rotate; Feature Scope. (CSWP segment 1 lists Move/Delete Face.)
- **Delete Face**: Faces to delete; Options *Delete* / *Delete and Patch* / *Delete and Fill*
  (+ Tangent fill).
- **Offset Surface**, **Replace Face**, **Instant3D on imported faces**.

## 11.5 Instant3D  [H 2012–2022, B Hawk Ridge, TriMech, CATI, CADimensions]
- Toggle on the **Features** tab, **on by default**; parts and assemblies.
- **Single click a face** of a feature → that feature's dimensions appear (with Instant3D off a
  double-click is needed) and **drag handles/arrows** (blue dots / arrows; a green arrow on an
  edge) appear on the face/edge; drag to resize; the whole model updates. [B]
- **Rulers**: while dragging, a ruler appears; **pointer away from the ruler = free drag;
  pointer on the ruler = snap to its increments**; an **angular ruler** for revolves, drafts and
  section-plane rings. Rulers also show in Edit Feature for extrudes, revolves, base flanges. [H]
- **Snap to geometry**: while dragging a handle **hold Alt and move over a face/vertex** to snap
  the size to it. [H 2012]
- **Create features**: exit the sketch, **select a closed contour** → an arrow appears → drag
  away from the solid = boss, into the solid = cut (a contour on a face cuts, one off the face
  bosses; overhanging contours depend on where you click); **hold M for a mid-plane extrude**
  [B Hawk Ridge]; an optional **context toolbar** lets you add draft or swap boss/cut. [H 2017]
- **Move/copy features**: drag the triad centre to move a feature to another face; **Ctrl+drag
  to copy** (e.g. Ctrl+drag a fillet to another edge). Drag an extrude handle the other way to
  turn growth into a cut. Works for Fillet, Simple Hole, Move Face (offset/translate/rotate),
  Revolve (sketch lines, angle), Shell, mirrored/patterned instances (dragging an instance edits
  the seed). [H 2012–2022]
- **Not draggable** → the handle turns black or a "no" icon appears (unsupported or constrained).
  [H]
- Dimension handles: drag the **blue balloon at the end of a dimension line**; click a dimension
  → in-place edit; double-click → Modify box. [B]
- **Instant2D** is the sketch equivalent (see 05 §5.12); disabling Instant3D/Instant2D restores
  plain single-click selection of dimension values. [B]
