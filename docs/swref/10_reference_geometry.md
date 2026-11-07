# 10 — Reference geometry

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.
Where: Features tab > **Reference Geometry** flyout (Plane · Axis · Coordinate System · Point ·
Center of Mass · Bounding Box · Mate Reference); Insert > Reference Geometry.

## 10.1 Plane  [H 2011–2018, B TriMech, Hawk Ridge, LibreTexts]
**PM "Plane"** — three selection groups: **First Reference**, **Second Reference**, **Third
Reference** (each a selection box + constraint buttons that appear according to what was
picked).
- **Message box colour, plane preview colour and messages guide you; the plane must reach
  "Fully defined" status to be created** (message turns from yellow "Select references and
  constraints" to green "Fully defined"). [H 2017, B]
- **The software proposes the most likely plane from the first pick** (planar face/plane → Offset
  distance by default). [H 2013, B LibreTexts]
- Constraint buttons (by reference type): **Coincident** · **Parallel** · **Perpendicular** (edge/
  curve + point; **Set origin on curve**) · **Project** (point onto a non-planar surface: *Nearest
  location on surface* / *Along sketch normal*) · **Parallel to screen** (at a vertex; **Update
  Plane** after rotating) · **Tangent** · **At angle** (edge/axis/line + face/plane; angle + Flip,
  Number of planes) · **Offset distance** (+ **Flip offset**, **Number of planes to create** —
  equally spaced) · **Mid Plane** (two faces/planes; selecting the second parallel reference
  **switches to Mid Plane automatically**) · **Flip Normal**. [H][B]
- Typical recipes: offset from face; 3 points (Coincident ×3); line + point; angle through edge;
  parallel through a point; tangent to cylinder + parallel/perpendicular; mid plane; normal to a
  curve at a point. Right-click a face > **Create a Plane Parallel to Screen**. [B]
- Remove a reference: right-click it in the box > Delete. [H 2014]
- Graphics: translucent plane preview with name label; **Ctrl+drag an existing plane's edge
  creates an offset plane** (drag handle) [K].
- Tree: Plane1…; planes show as transparent rectangles with names; resize by dragging the
  corner handles [K].

## 10.2 Axis  [H 2012–2014]
PM "Axis": **Selections** box + type buttons: **One Line/Edge/Axis** (sketch line, edge, or a
temporary axis — View > Temporary Axes) · **Two Planes** (planar faces or planes) · **Two
Points/Vertices** (vertices, points, midpoints) · **Cylindrical/Conical Face** · **Point and
Face/Plane** (axis normal to the face through the point; on non-planar faces the point must lie
on the face). Tree: Axis1.

## 10.3 Coordinate System  [H 2010–2022] (CSWP segment 3 needs it)
PM "Coordinate System" (Insert > Reference Geometry > Coordinate System):
- **Position**: **Origin** box (vertex, point, midpoint or the default origin) · **Define position
  with numeric values** → X/Y/Z Coordinate fields (relative to the *local* origin; 2022+).
- **Orientation**: **X axis**, **Y axis**, **Z axis** direction reference boxes — vertex/point/
  midpoint (axis toward it), linear edge or sketch line (parallel), non-linear edge/sketch entity
  (toward the picked location), planar face (normal) — each with **Reverse Axis Direction** ·
  **Define rotation with numeric values** → X/Y/Z Rotation Angle (applied in X, then Y, then Z
  sequence; 2022+).
- Right-click in the graphics area > Clear Selections to restart. Triad preview with coloured
  axes. When entities are insufficient, define it elsewhere and move the origin. [H 2010]
- Uses: Measure and Mass Properties output, export (IGES, STL, ACIS, STEP, Parasolid, VRML, VDA),
  assembly mates; its planes, axes and origin can be referenced (sketch on its XY plane, revolve
  about its Z axis); Measure the angle between two coordinate systems. [H 2024]
- Tree: Coordinate System1.

## 10.4 Point  [B Narayanpure (CSWE)]
Types: **Arc Center** · **Center of Face** · **Intersection** · **Projection** · **On Point**
(sketch point/end) · **Along curve distance or multiple reference points** (Distance /
Percentage / **Evenly Distributed**, number of points).

## 10.5 Center of Mass, Bounding Box, Mate Reference [K]
- **Center of Mass** (COM point that updates; can be referenced by dimensions/mates).
- **Bounding Box** (2018+): Best fit / Custom plane, include hidden bodies/surfaces, properties.
- **Mate Reference**: primary/secondary/tertiary entity + mate type + alignment; used by
  SmartMates when inserting the part.
