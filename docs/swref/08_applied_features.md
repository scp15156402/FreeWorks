# 08 — Applied features (Fillet, Chamfer, Hole Wizard, Shell, Draft, Dome, Thread …)

Tags: [H] help, [B] blog/training, [F] forum, [O] owner settings, [K] known, unconfirmed.

## 8.1 Fillet  (Features tab · Insert > Features > Fillet/Round · owner shortcut **F** [O])

### Ways in
- **Preselect** edges/faces/features, then Fillet (or pick **Fillet on the context toolbar** that
  appears on edge selection) → PM opens with the items already in *Items to Fillet*. [B Javelin
  2023 "Select the edge(s) … click Fillet"]
- **Fillet with nothing selected** → PM opens with an empty, active *Items to Fillet* box; click
  edges/faces in the graphics area. No error dialog, no "confirm selection" step. [H][K]
- Editing: select the fillet → Edit Feature (context toolbar or right-click), or double-click the
  fillet face/feature to show its radius dimension for Instant3D / Modify. [K]

### PM top: **Manual** and **FilletXpert** tabs [H 2012–2025]
- Manual: you control the feature. FilletXpert (symmetric constant-radius fillets only, single
  configuration models [B]): SOLIDWORKS manages/reorders the underlying features.
- **When editing an existing fillet the tabs are not shown.** [H]
- **Keep Visible pushpin** works in Manual for Constant Size, Face and Full Round; settings in
  Items to Fillet, Fillet Parameters and Fillet Options are retained during the session; not
  available when editing. [H 2025]
- The PM **remembers its last used state** (type, size, options). [H]

### Fillet Type (four big buttons) [H]
**Constant Size Fillet** · **Variable Size Fillet** · **Face Fillet** · **Full Round Fillet**.

### Constant Size Fillet [H 2015–2019, B Engineers Rule, Learn SOLIDWORKS 2020]
**Items to Fillet**
- **Edges, Faces, Features and Loops** selection box. Edge → that edge; **face → all edges of
  that face** (e.g. 12 edges = outer loop 8 + inner loop 4); feature (from the tree) → its edges;
  loop → via right-click edge > **Select Loop** (an arrow on the edge flips which of the two loops
  is taken). [B fpgdesign/SOLIDWORKS blog 2014]
- **Show selection toolbar** checkbox. When on, picking an edge pops a small **selection
  toolbar** beside the pointer with selection shortcuts (e.g. connected edges, loops, edges of the
  feature, **All Edges** …). Hovering an icon highlights what it would add. The toolbar is
  "directional": slide toward it to use it; moving away fades and closes it (no close button). [B
  GSC, Learn SW 2020]
- **Tangent propagation** (default on): extends to all edges tangent to the selected one (one
  pick can select a whole tangent chain). [H][B]
- **Full preview** · **Partial preview** · **No preview** radio buttons. Partial = preview of one
  edge only; **press A to step the partial preview to the next edge**. No preview improves rebuild
  time. [H 2016] (Engineers Rule says No preview is the default; Full preview recommended.)

**Fillet Parameters**
- **Fillet Method**: *Symmetric* (one radius) / *Asymmetric* (two distances, + **Reverse
  Direction** per edge to swap sides; asymmetric added in 2015). [H][B CATI]
- **Radius** spin (asymmetric: Distance 1, Distance 2).
- **Multiple radius fillet** checkbox: each selected edge gets its own value; a **callout appears
  on every edge in the graphics area** showing its radius; click a callout value to edit it. [B]
- **Profile**: *Circular* · *Conic Rho* (0–1, API range 0.05–0.95) · *Conic Radius* (radius of
  curvature at the shoulder) · *Curvature Continuous*. Asymmetric offers *Elliptic* (2015 name)
  and conic options. [H][B]

**Setback Parameters** (for three or more fillets meeting at a vertex) [H][B]
- **Setback Vertices** selection box; **Distance** spin; **Setback Distances** list (one per
  edge, callouts on the model); **Set Unassigned** (apply Distance to edges without a value);
  **Set All**.

**Partial Edge Parameters** (2019+) [H]
- Fillet only part of an edge: **Start condition** / **End condition** = *None*, *Offset
  Distance*, *Percentage Offset*, *Selected Reference*; distance values; reverse.

**Fillet Options** [H][B]
- **Select through faces** — pick hidden edges through faces in shaded/HLR mode.
- **Keep features** — keep bosses/cuts the fillet would otherwise consume (clear it and a small
  boss/hole is swallowed). [B Hawk Ridge, Engineers Rule]
- **Round corners** — smooth transition where adjacent filleted edges meet (needs ≥2 adjacent
  edges).
- **Overflow type** — *Default* · *Keep edge* (edge stays, fillet may split) · *Keep surface*
  (one continuous fillet surface, the edge moves). Controls single closed edges meeting other
  edges.
- (Older) **Help point** for ambiguous selections; **Curvature continuous** (pre-2015 checkbox,
  now a Profile).

### Variable Size Fillet [H 2015–2024, B Javelin]
- Items to Fillet (edges) + Tangent propagation + preview radios.
- **Variable Radius Parameters** (Symmetric/Asymmetric): **Attached Radii** list (vertices V1,
  V2 … and control points P1…), **Radius** for the selected entry, **Set Unassigned**, **Set
  All**, **Number of Instances** (control points per edge), **Smooth transition** / **Straight
  transition** (linear change, no tangency match), profile.
- Graphics: **callouts at each vertex and control point**; click a callout to type a radius;
  **drag control points** along the edge (their % position shows). [H "Using Variable Radius
  Control Points"]
- Setback Parameters, Fillet Options as above.

### Face Fillet [H][B]
- **Face Set 1** and **Face Set 2** selection boxes (non-adjacent, non-continuous faces blended);
  arrows show the fillet side — click to flip.
- Fillet Parameters: method (Symmetric / Asymmetric / **Chord Width** / **Hold Line**),
  radius or chord width; hold line selection; profile.
- Options: Tangent propagation, Curvature continuous (old), **Trim and attach** / **Do not trim
  or attach**, **Help point**, Show preview.

### Full Round Fillet [H][B]
- **Side Face Set 1**, **Center Face Set**, **Side Face Set 2** selection boxes (colour coded,
  right-click/Enter cue advances to the next box); no radius — tangent to three faces.
- Options: Tangent propagation, preview.

### FilletXpert [H 2012–2015]
- Tabs **Add**, **Change**, **Corner**.
- Add: Items To Fillet, Radius, Options: Select through faces, Tangent propagation. **Apply**
  creates fillets without closing; FilletXpert organises them into features automatically.
- Change: **Fillets to Change** box; **Sort by Size** list (pick a size → selects every fillet
  of that size); **Radius** + **Resize**; **Remove**.
- Corner: pick a fillet corner face → **Show Alternatives** pop-up with preview thumbnails to
  pick another corner blend; **Copy Targets** to copy a corner style. [H "Choosing Alternative
  Fillet Corners"]

### Feedback and errors
- Rebuild error when the radius is too large: "Failed to create fillet…" in What's Wrong. [K]
- Fillet feature names: **Fillet1, Fillet2 …** (VarFillet1 for variable size in older versions). [K]

## 8.2 Chamfer  (Features tab, Fillet flyout · Insert > Features > Chamfer)

[K — verify] Chamfer Type buttons: **Angle Distance** · **Distance Distance** · **Vertex** ·
**Offset Face** · **Face Face**. Items to Chamfer (edges/faces/vertex), Show selection toolbar,
Tangent propagation, preview radios. Chamfer Parameters: Distance + Angle (with **Flip
direction** arrow on the model), D1/D2 (Symmetric/Asymmetric) for Distance Distance, three
distances (+ Equal distance) for Vertex; **Multi distance chamfer**. Partial Edge Parameters.
Chamfer Options: Select through faces, **Keep features**. Graphics callouts with arrows on the
edge.

## 8.3 Hole Wizard  (Features tab · Insert > Features > Hole > Wizard)

[H 2025 "Hole Wizard Overview"]
- Two-tab PM: **Type** and **Positions**. Hole Wizard features own **two sketches** (a 2D/3D
  placement sketch and the profile sketch).
- Choosing a hole type changes capabilities, selections and previews; choosing a fastener
  updates parameters dynamically; PM graphics show details of the chosen type.
- Positions tab: click a face, then click to place points (a sketch point per hole, the sketch
  tools are active for dimensioning/relations); **Existing 2D Sketch** → holes at every
  endpoint/vertex/point of a selected sketch.
- **Favorite** group: Add/Update/Delete/Save/Load favourites per hole type (not Legacy).
- [K] Type tab groups: **Hole Type** (Counterbore, Countersink, Hole, Straight Tap, Tapered Tap,
  Legacy, Counterbore Slot, Countersink Slot, Slot) · **Standard** (ANSI Inch/Metric, ISO, DIN,
  JIS …; the owner uses **AS** [O]) · **Type** (fastener) · **Hole Specifications** (Size, Fit
  Close/Normal/Loose, Show custom sizing) · **End Condition** (Blind, Through All, Up To Next,
  Up To Vertex, Up To Surface, Offset From Surface; depth, tip angle) · **Options** (head
  clearance, near/far side countersink, cosmetic thread, thread class) · **Feature Scope**.
- Tree name e.g. "CBORE for M6 Hex Head Bolt1", "M6x1.0 Tapped Hole1". [K]

## 8.4 Shell  (Insert > Features > Shell) [K — verify]
Parameters: **Thickness**, **Faces to Remove** box, **Shell outward**, **Show preview**.
**Multi-thickness Settings**: Multi-thickness faces box + per-face thickness (callouts).
Errors: thickness ≥ smallest fillet radius → failure; Error Diagnostics group (Check body,
"Go to geometry"). Tree: Shell1.

## 8.5 Draft  (Insert > Features > Draft) [K — verify]
Manual / DraftXpert tabs. **Type of Draft**: Neutral Plane · Parting Line · Step Draft (Tapered
steps / Perpendicular steps). Draft angle; Neutral Plane box (arrow for pull direction, click to
flip); Faces to Draft box; **Face propagation** (None, Along Tangent, All Faces, Inner Faces,
Outer Faces). Draft Analysis link. Tree: Draft1.

## 8.6 Dome, Wrap, Thread, Thicken
- **Thicken** [H 2024]: Surface to Thicken; **Thicken Side 1 / Both Sides / Side 2** buttons
  with preview; Thickness; optional **Direction of Thicken** (lines, points, planes, axes, edges,
  vertex pairs, cylindrical/conical/planar faces); Create solid from enclosed volume; cut variant
  with Feature Scope (Selected bodies expands a list of bodies with checkboxes to keep).
- **Thread** [H 2025]: Insert > Features > Thread; select a circular edge; **Specification**
  (Type e.g. Metric Die/Tap, Size e.g. M6x1.0); **Thread method** Cut thread / Extrude thread
  (preview pink for cut, green for extrude per Colors > Temporary Graphics); **Thread Location**
  (Offset, Reverse Direction, Offset Distance, end condition, maintain thread length); thread
  profile sketch always on the Front plane of the profile library part.
- **Dome**, **Wrap** [K]: Dome — faces, distance, constraint point/direction, elliptical dome,
  continuous dome. Wrap — Emboss/Deboss/Scribe, analytical/spline surface, source sketch, face,
  depth.
