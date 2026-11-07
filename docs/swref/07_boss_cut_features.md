# 07 — Boss / Base and Cut features

Tags as in 01: [H] official help, [B] blog/training, [F] forum, [O] owner settings, [K] known
behaviour, not yet confirmed by a fetched source.

## 7.0 Behaviour common to all sketch-based features (Extrude, Revolve, Sweep, Loft, Rib …)

**How the command finds its sketch** [K, consistent with H "Creating Revolve Features", "Closing
Sketches to Models"]:
1. **A sketch is open (being edited)** → clicking the feature closes the sketch and uses it. The
   sketch is consumed (absorbed under the feature in the tree, hidden).
2. **A sketch (or sketch contours / a planar face for Extrude) is preselected** in the tree or
   graphics area → used directly.
3. **Nothing suitable is selected** → the PM opens with a message asking for *a plane, planar face
   or edge to sketch on, or an existing sketch*. The three default planes are shown in the
   graphics area so one can be clicked. Picking a plane/face **starts a new sketch on it**
   (view rotates Normal To if that option is on), and **when the sketch is exited the feature PM
   returns** with the new sketch as its profile. ("Feature-first" workflow.)
4. Picking an existing sketch while the PM is open uses it.

**Absorbed sketch:** the feature node gets an expand arrow; the sketch sits under it
("Sketch1"), hidden by default. Editing the sketch: right-click feature > Edit Sketch, or click
the feature and use the context toolbar (Edit Sketch / Edit Feature). [K]

**Shared sketches:** a sketch already used by a feature can be selected again for another
feature (appears under both; hand-icon "shared" indicator). [K]

**Preview:** shaded preview of the resulting body updates live as values change; cut previews
show the material to be removed. Colours come from System Options > Colors > "Temporary
Graphics …" settings (see 18_visual_style). [H thread help: defaults pink = remove material,
green/yellow = add material — verify] 

**Multiple contours / regions:** open a sketch with several closed regions → Selected Contours
lets you pick regions (shaded when hovered) and model edges. [H]

**Errors:** e.g. "Zero thickness geometry" → fix by clearing Merge result (creates multibody)
[H]; "Rebuild errors" dialog / What's Wrong (see 04). Open sketches can only make thin/surface
features; Extrude of an open contour automatically turns **Thin Feature** on. [H]

## 7.1 Extruded Boss/Base · Extruded Cut · Extruded Surface

Where: Features tab (first button) / Insert > Boss/Base > Extrude; Insert > Cut > Extrude;
Surfaces tab / Insert > Surface > Extrude. Owner shortcut **E = Extruded Boss/Base** [O].
Tree names: **Boss-Extrude1**, **Cut-Extrude1**, **Surface-Extrude1**. [H title "Boss_Extrude1"]

### PM groups (in order) [H 2012–2024 unless marked]

**From** — starting condition (combo):
- *Sketch Plane* (default).
- *Surface/Face/Plane* — selection box; the face may be non-planar: "the sketch follows the
  shape of the nonplanar entity at the starting surface". [H 2024]
- *Vertex* — selection box (start at the plane through that vertex).
- *Offset* — Enter Offset Value spin + Reverse Direction.

**Direction 1**
- **Reverse Direction** button (left of the end condition combo).
- **End Condition** combo: *Blind* (default) · *Through All* (cut; boss when other geometry
  exists) · *Through All – Both* (cut; selecting it in Direction 1 **turns on Direction 2 with
  Through All automatically** [B TriMech]) · *Up To Next* (next surface that intercepts the
  entire profile, same part) · *Up To Vertex* (plane parallel to the sketch through the vertex;
  sketch vertices allowed) · *Up To Surface* (face/plane box; may auto-extend one analytic face if
  the sketch overhangs) · *Offset From Surface* (face box + Offset Distance + **Reverse offset** +
  **Translate surface** = translated copy rather than true offset) · *Up To Body* (body box;
  useful in assemblies and molds) · *Mid Plane* (Depth split equally). [H]
- **Double-click a surface in the graphics area → end condition switches to Up To Surface with
  that surface.** [H]
- **Direction of Extrusion** selection box — a sketch line, edge, axis, plane (normal) to extrude
  off-normal. [H]
- **Depth (D1)** spin — Blind/Mid Plane. Accepts `=` equations, global variables, functions,
  file properties (drop-down appears after `=`). [H]
- **Link to thickness** — links this extrusion's depth to the thickness of an existing
  coincident extrusion. [H 2024]
- **Flip side to cut** (Cut only) — removes material outside the profile instead of inside. [K]
- **Merge result** (Boss only; not shown for the first feature) — merge into existing body; clear
  to create a separate body. [H]
- **Draft On/Off** toggle button + **Draft Angle** + **Draft outward** checkbox. [H]

**Direction 2** (checkbox in group title) — same options as Direction 1, extrudes the other
way from the sketch plane. [H]

**Thin Feature** (checkbox in group title; forced on for open contours) [H]:
- Reverse Direction; **Type**: *One-Direction* · *Mid-Plane* · *Two-Direction*;
  Thickness T1 (and Direction 2 Thickness T2 for Two-Direction).
- **Auto-fillet corners** (open sketches only) + **Fillet Radius**.
- **Cap ends** + **Cap Thickness** — closed contours only, first extruded body only → hollow
  part.

**Selected Contours** (collapsible) — selection box; pick sketch regions/contours and model
edges to use only part of the sketch. [H]

**Feature Scope** (cuts, and bosses in multibody parts / assemblies) — *All bodies* · *Selected
bodies* (+ **Auto-select**, + bodies box). [H]

Surface-only: **Cap end** per direction (capping both ends of an enclosed volume makes a solid);
extrude from faces (Alt+select planar face for 2D face), **Delete original faces**, **Knit
result**. [H]

### Graphics-area handles [K — confirm]
- A grey **drag arrow** at the profile for each direction; drag to set depth. While dragging,
  a **ruler** appears; moving the pointer onto the ruler snaps to ruler ticks. A **callout**
  shows the depth and can be clicked to type a value.
- Selecting the end face of an existing extrude (Instant3D on) shows the same arrow for quick
  editing without opening the PM (see 05/§Instant3D).

## 7.2 Revolved Boss/Base · Revolved Cut · Revolved Surface

Rules [H 2025 "Revolves"]:
- Profile is a 2D sketch (axis may be in a 3D sketch). Solid revolve sketch may contain multiple
  intersecting profiles → **Selected Contours**.
- Thin/surface revolves allow multiple open or closed intersecting profiles.
- **Profiles cannot cross the centerline.** If the sketch has exactly one centerline it is used
  as the axis automatically [K]; with more than one, select the axis.
- Dimensioning to a centerline: from a line to the centerline gives a **radius**; across the
  centerline (place the dimension past the centerline) gives a **diameter** dimension (rebuild
  to show the symbol). [H]
- Missing axis → message "select axis of revolution". [H "Check Sketch for Feature" example]

PM "Revolve" [H 2010–2024]:
- **Axis of Revolution** selection box (centerline, line or edge depending on feature type).
- **Direction1**: **Reverse Direction** · **Revolve Type** — *Blind* (Direction 1 **Angle**,
  default **360°**, measured clockwise from the sketch) · *Up To Vertex* · *Up To Surface*
  (Face/Plane) · *Offset From Surface* (Face/Plane + Offset Distance + Reverse offset) · *Mid-Plane*
  (angle split clockwise/counter-clockwise) · **Merge result** (boss) · **Flip side to cut**
  (revolved cut: remove outside the profile).
- **Direction2** (optional, checkbox; after Direction1; same options; total angle ≤ 360°;
  picking the same entity in both directions cancels the feature).
- **Thin Feature** (checkbox): **Type** *One-Direction* (Reverse Direction) / *Mid-Plane* /
  *Two-Direction* (Direction 1 Thickness outward, Direction 2 Thickness inward); thickness.
- **Selected Contours**: hover a region → it changes colour → click to add; any combination,
  single- or multibody result.
- **Feature Scope** (cut / multibody): All bodies / Selected bodies / Auto-select.
- Equations allowed in numeric fields (`=`). [H 2013]
Tree names: Revolve1, Cut-Revolve1, Surface-Revolve1. [K]

## 7.3 Swept Boss/Base · Swept Cut · Swept Surface

PM "Sweep" [H 2012–2024, B Hawk Ridge, SOLIDWORKS blog]:
- **If the profile and path sketches are preselected, SOLIDWORKS fills both boxes.** [B]
- **Profile and Path**: **Sketch Profile** (Profile box — closed for boss/base, open or closed
  for surfaces; Path box) · **Circular Profile** (2016+: rod or tube along a sketch line, edge or
  curve — path + **Diameter**, no profile sketch) · Cut only: **Solid Profile** (tool body; path
  must be tangent-continuous and start on/in the tool body; not in assemblies; **Align with end
  faces**).
- Path: open or closed; sketch curves in one sketch, a curve, or model edges. **The start point of
  the path must lie on the plane of the profile.** Neither section, path nor result may
  self-intersect. [H]
- When the path runs through the profile: **Direction 1 / Bidirectional / Direction 2** (2016+;
  no guide curves or start/end tangency for bidirectional; twist per direction). [H]
- **Guide Curves** (sketch profiles only, not bidirectional): Guide Curves box (curves must be
  coincident with/pierce the profile) · **Move Up / Move Down** (order) · **Merge smooth faces**
  (clear to improve performance and segment at non-curvature-continuous points) · **Show
  Sections** (arrows step through Section Number to troubleshoot).
- **Options**: **Profile Orientation** (2016+ split): *Follow Path* (default) / *Keep Normal
  Constant*; **Profile Twist**: *None* / *Minimum Twist* (3D paths) / *Follow Path and First Guide
  Curve* / *Follow First and Second Guide Curves* / *Specify Twist Value* (**Degrees / Radians /
  Revolutions**; closed paths need whole revolutions) / *Specify Direction Vector* (plane, face,
  line, edge, axis, vertex pair) / *Tangent to Adjacent Faces* / *Natural*. (≤2015: one
  "Orientation/twist type" list incl. *Twist Along Path* / *Twist Along Path With Normal
  Constant* with **Define by** Degrees/Radians/Turns, and **Path alignment type**.) **Merge
  tangent faces** · **Show Preview** (on by default) · **Merge result** (on by default).
- **Start and End Tangency**: Start/End tangency type *None* / *Path Tangent* (normal to the path
  at the start/end).
- **Thin Feature**; **Curvature Display** (Mesh preview, Zebra stripes, Curvature combs).
- **Feature Scope** (cut).

## 7.4 Lofted Boss/Base · Lofted Cut · Lofted Surface

PM "Loft" [H 2010–2020]:
- **Profiles**: Profile box (sketch profiles, faces or edges; **lofts follow the selection
  order**; **for each profile click near the point from which the loft should travel** —
  matching points connect) · **Move Up / Move Down**. Bad twist → reselect/reorder.
  **Connectors** (points on the preview) can be dragged; right-click > Show All Connectors /
  Reset Connectors [K].
- **Start/End Constraints**: Start constraint / End constraint — *Default* (≥3 profiles; parabola
  between first and last) · *None* · *Direction Vector* (+ Direction Vector box) · *Normal To
  Profile* · *Tangency To Face* / *Curvature To Face* (attaching to existing geometry; **Next
  Face** toggles between candidate faces) · **Draft angle** (+ Reverse Direction) · **Start/End
  Tangent Length** · **Apply to all** (one handle per profile; cleared → handles per segment,
  drag to change tangent length).
- **Guide Curves**: **Guide curves influence** *To next guide* / *To next sharp* / *To next
  edge* / *Global* · Guide Curves box · Move Up/Down · **Guide tangency type** per curve *None* /
  *Normal to Profile* / *Direction Vector* / *Tangency to Face* (+ draft angle).
- **Centerline Parameters**: Centerline box, **Number of Sections** slider, **Show Sections**
  (arrows / enter a section number).
- **Sketch Tools** (3D-sketch profiles): **Drag Sketch** mode (drag segments/points/planes of the
  3D sketch; preview updates when the drag ends) · **Undo sketch drag** (multiple).
- **Thin Feature**: One-Direction / Mid-Plane / Two-Direction, Thickness(es).
- **Options**: **Merge tangent faces** · **Close loft** (joins last to first) · **Show preview**
  (right-click toggles **Transparent Preview / Opaque Preview**) · **Merge result** · Micro
  tolerance [K].
- **Curvature Display** (Mesh preview, Zebra stripes, Curvature combs) · **Feature Scope** (cut).

## 7.5 Boundary Boss/Base · Boundary Cut · Boundary Surface

[H 2024 "Creating Boundaries"]: Insert > Boss/Base > Boundary etc.; **curve callout colours match
the PropertyManager**; **click callouts to change the Tangent Type**. Directions 1 and 2 curves,
tangent types (None, Direction Vector, Normal To Profile, Tangency To Face, Curvature To Face),
Tangent influence, Options and Preview (Merge tangent faces, Close, Show preview, Trim by
direction 1), Display (mesh, zebra, curvature combs). [K for the list]

## 7.6 Rib (special extrude)

[H "Ribs"]: special extruded feature from open or closed contours; adds material of a given
thickness in a given direction **between the contour and the existing part**; single or multiple
sketches; optional draft (Draft outward, reference contour). PM [K]: Thickness *First Side /
Both Sides / Second Side*, Rib Thickness, **Extrusion direction** *Parallel to Sketch / Normal to
Sketch*, Flip material side, Draft On/Off + angle + Draft outward, Type (Linear / Natural, normal
to sketch only), Selected Contours. The preview arrow shows the material side; click it to flip.
