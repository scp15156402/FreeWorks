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

## 11.5 Instant3D  [K, from earlier summary]
- Toggle on the Features tab (default on). **Click a face** of a feature → its dimensions appear;
  **blue drag handles/arrows** on the face; drag to change, with a **ruler** (snaps when the
  pointer is on the ruler; ruler ticks show increments); release rebuilds.
- Click a dimension → edit box in place (quick edit); double-click → Modify box.
- Select a **closed contour or sketch** and drag its arrow to create an extrude/cut directly.
- **Ctrl+drag a feature's face/handle to copy a feature** (e.g. a hole) to another face; Alt-drag?
- **Instant2D** is the sketch equivalent (see 05 §5.12).
