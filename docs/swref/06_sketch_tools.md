# 06 — Sketch entities and sketch tools: what the left pane shows

Tags: [H] help, [B] blog/training, [F] forum, [O] owner settings, [K] known, unconfirmed.

Every sketch tool has **two left-pane states**:
- **Tool PM** — shown as soon as the tool is clicked, before/while drawing (e.g. "Insert Line",
  "Rectangle", "Circle"). Holds the type selector and creation options. After an entity is
  drawn with the tool still active, the PM switches to that entity's properties (with the tool
  still running).
- **Properties PM** — shown when an existing entity is selected with no tool active
  ("Line Properties", "Circle", "Arc", "Point" …): Existing Relations, Add Relations, Options,
  Parameters, Additional Parameters. Editing a Parameters value moves the geometry (if not
  over-constrained).

Shared groups used below:
- **Existing Relations** — list of relations on the entity (right-click Delete), plus an
  **Information** line with the entity status (*Under Defined*, *Fully Defined*, *Over Defined*,
  …). [H 2012 rectangle]
- **Add Relations** — buttons for the relations valid for the current selection only. [H]
- **Options** — at least **For construction** (converts to construction geometry). [H]
- **Add dimensions** — checkbox shown only when System Options > Sketch > *Enable on-screen
  numeric input on entity creation* is on; right-click in the graphics area > **Sketch Numeric
  Input** toggles it. [H 2022/2025 rectangle] (The owner has numeric input **and** add dimension
  on [O].)

Universal tool behaviour [K unless marked]:
- The tool stays active after an entity is finished (draw the next one). **Esc** or clicking the
  tool button again ends it; the **Select** pointer returns.
- **Click-click** and **click-drag** both work for two-point entities.
- While drawing, the pointer shows a **symbol** for the relation it will add (horizontal,
  vertical, coincident, midpoint, tangent, perpendicular, parallel, on-edge, intersection …) and
  **dashed inference lines** to points it aligns with; the relation is added automatically on
  click. **Hold Ctrl** to suppress automatic relations. [K; see 05]
- The pointer displays the live value (line length, radius …) next to it. [K]
- Numeric input (when on): fields appear next to the entity being drawn; **Tab** moves between
  fields (Shift+Tab in 3D sketches), **Enter** accepts. [H/K, see 05]

---

## 6.1 Line (and Centerline, Midpoint Line)

Where: Sketch tab, Line flyout (Line · Centerline · Midpoint Line); Tools > Sketch Entities.
Owner gesture: sketch **D (down) = Line** [O].

**Tool PM "Insert Line"** [H 2012–2020 "Insert Line PropertyManager - 2D", "Sketching Lines"]
- **Orientation**: *As sketched* (default; click-drag = one line, click-click = chain until
  double-click) · *Horizontal* · *Vertical* · *Angle* (relative to horizontal). Some
  orientations, and Infinite length, **override Quick Snaps**.
- **Options**: *For construction* (Centerline tool = Line with this ticked) · *Infinite length*
  (can be trimmed later; a finite line can be made infinite but not the reverse) · *Midpoint
  line* (symmetric about the first click; Midpoint Line tool) · *Add dimensions*.
- **Parameters** — shown for every orientation except As sketched: Horizontal/Vertical →
  *Length*; Angle → *Length* + *Angle*; each with *Add dimensions*. **With values set, one click
  creates the line with those values.**
- **Flow:** as soon as the first line is drawn the pane **switches to Line Properties** and you
  keep sketching with the same orientation. **Click OK (or double-click) to return to the Insert
  Line PM** to change Orientation/Options/Parameters. 3D sketch: only *As sketched*. [H]
- An angle set in the PM can be edited only within the same Line Properties session (and with a
  horizontal construction line as reference). [H 2012]

**Properties PM "Line Properties"** — open by selecting a line in an open sketch [H 2010–2020]
- **Existing Relations** (relations inferred while sketching or added) + **Information** status
  (Fully Defined, Under Defined …) · **Add Relations**
- **Options**: For construction · Infinite length
- **Parameters**: **Length**, **Angle** (relative to the grid: horizontal 180°, vertical 90°,
  counter-clockwise positive). Any combination can be set if the line is not constrained;
  changing one updates the others.
- **Additional Parameters**: **Start X, Start Y, End X, End Y, Delta X, Delta Y** (3D adds Z).
- Dragging: drag an endpoint to change length; drag the line to move it; a Horizontal/Vertical
  relation must be deleted (here) before dragging to a new angle. [H 2012]

Drawing behaviour [K]:
- Click-click-click = **chain** (each click ends one segment and starts the next);
  click-drag-release = **one segment** and the tool waits for a new start.
- End the chain: **double-click**, **Esc**, right-click > **End Chain**, or click the start point
  to close the loop.
- **Line → tangent arc without changing tools**: press **A**, or move the pointer back to the
  last endpoint and out again; intent zones decide tangent vs. normal arc. Press **A** again to
  return to line.
- Inference to midpoints/endpoints/centres of other entities appears after hovering them
  ("wakes up" points).

## 6.2 Rectangle family  [H 2013–2025, F cad forum 2025]

Where: Sketch tab, Rectangle flyout; Tools > Sketch Entities. Owner shortcut **R = Corner
Rectangle** [O]. **SOLIDWORKS defaults to the last used rectangle type** when the flyout button
is clicked. [H]

**Tool PM "Rectangle"**
- **Rectangle Type** (five buttons, the active one highlighted): **Corner Rectangle** ·
  **Center Rectangle** · **3 Point Corner Rectangle** (at an angle) · **3 Point Center
  Rectangle** · **Parallelogram**. Switching here changes the tool. [H]
- **Add dimensions** (numeric input on). [H 2025]
- **Add construction lines** checkbox → **From Corners** (diagonals) / **From Midpoints**. Works
  for all five types. Center types get diagonals automatically. [H][B CATI]
  - Quirk: for Center and 3 Point Center types the construction-line options only appear after
    the first rectangle is drawn. [F]
- **Shift while creating a rectangle makes a square.** [H 2022]

**After drawing / Properties**
- Existing Relations · Add Relations (for the selected segment(s)) · Options **For construction**
- **Parameters**: the **X/Y coordinates of all four corner points** (four pairs); Center types
  add the **center X/Y**. [H 2013]
- A rectangle is four lines with horizontal/vertical (or parallel/perpendicular) relations;
  selecting one side shows Line Properties. [K]

## 6.3 Circle and Perimeter Circle

Where: Sketch tab, Circle flyout; owner shortcut **C = Circle**, sketch gesture **L (left) =
Circle** [O].

**Tool PM "Circle"** [H 2010–2017 "Circle", "Circle PropertyManager"]
- **Circle Type**: *Circle* (centre-based) · *Perimeter Circle* (points on the perimeter; snaps
  tangent to entities). Switching here changes the tool. **Defaults to the last used circle
  type.**
- Add dimensions (numeric input on).
**Properties "Circle"** (select a circle in an open sketch): Existing Relations (+ Information) ·
Add Relations (only relations possible for the selection) · Options *For construction* ·
**Parameters** (if not constrained; changing one updates the rest): *Center X*, *Center Y*,
*Radius*.
Drawing: click centre, drag/move (pointer shows the radius), click. Perimeter: click a perimeter
point, drag, click further points. Editing by dragging: drag the edge away from/toward the centre
to resize; drag the centre point to move. [H]

## 6.4 Arc family

**Tool PM "Arc"** [H 2012–2020]: **Arc Type**: *Centerpoint Arc* · *Tangent Arc* · *3 Point Arc*
(switching here changes the tool; **defaults to the last used arc type**).
**Properties "Arc"** (select an arc): Existing Relations · Add Relations · Options *For
construction* · **Parameters**: *Center X/Y*, *Start X/Y*, *End X/Y*, *Radius*, *Angle*
(subtended).
Drawing [H 2012]:
- Centerpoint: click centre → release and drag to set radius and angle → click start point →
  drag and click end point.
- Tangent: click the endpoint of a line, arc, ellipse or spline and drag. SOLIDWORKS infers
  **tangent or normal** from the pointer motion — **four intent zones, eight possible results**;
  return to the endpoint and leave in another direction to toggle. Lines **auto-transition** to a
  tangent arc without changing tools (see Line).
- 3 Point: click start → drag, click end → drag to set the radius → click.

## 6.5 Slot family

**PM "Slot"** [H 2016–2019]
- **Slot Types** (for new slots): *Straight Slot* (two end points, then width) · *Centerpoint
  Straight Slot* (centre, then length, then width) · *3 Point Arc Slot* · *Centerpoint Arc Slot*.
- **Add dimensions** (shows the length and arc dimensions).
- For new or existing slots: **Center to Center** / **Overall Length** (how straight-slot
  length is dimensioned; arc-slot angles are always centre to centre).
- **Equal Slots** (when several slots are selected: keep them the same size).
- **Parameters** (if not constrained): slot centre X, Y · **Width** · **Length**; arc slots add
  **Radius** and **Angle** of the arc.
- A slot is two lines + two tangent arcs + a construction centreline; selecting one segment
  shows that segment's properties, selecting the whole slot (box/right-click > Select slot)
  shows the Slot PM. [K]

## 6.6 Polygon

**PM "Polygon"** [H 2013–2024]:
- Existing Relations: "No relations exist for polygons" + Information status. Add Relations:
  only to the polygon's points and lines.
- Options: *For construction*.
- **Parameters** (change any; others update): **Number of Sides** (3–40; default 6 [K]) ·
  **Inscribed circle** / **Circumscribed circle** (construction circle that sizes the polygon) ·
  **Center X**, **Center Y** · **Circle Diameter** · **Angle** (rotation) · **New Polygon**
  button (start another polygon with the tool still active).
- Drawing: click centre, drag to a vertex (inscribed) or flat (circumscribed), click.
- After creation the PM stays in polygon edit mode until you click New Polygon, OK or elsewhere.
  [H API remark]
- Editing later: select a side > Tools > Sketch Tools > **Edit Polygon**, or right-click a side >
  **Edit polygon** → the Polygon PM again. [H]

## 6.7 Ellipse, Partial Ellipse, Parabola, Conic

[K]: Ellipse — click centre, click major axis end, click minor; Parameters: centre X/Y, major
radius, minor radius (+ start/end for partial). Parabola — focus, apex, ends. Conic — start, end,
top vertex, **Rho** (0–1) in Parameters.

## 6.8 Spline family

[K — verify] Spline (click points; double-click/Esc ends), Style Spline, Spline on Surface,
Equation Driven Curve (Explicit / Parametric; equation, x1/x2 parameters), Fit Spline.
**Spline PM**: Existing Relations · Add Relations · Options *For construction*, **Show
curvature**, **Maintain internal continuity** · **Parameters**: *Spline Point Number*, *X*, *Y*,
**Tangent Weighting 1/2**, **Tangent Radial Direction**, **Tangent Driving**, **Reset This
Handle**, **Reset All Handles**, **Relax Spline**, **Proportional**. Handles (blue arrows) on
each point drag tangency direction/weight; Alt-drag symmetric.

## 6.9 Point, Text, Plane (sketch), Sketch Picture

- **Point**: Parameters X, Y (Z in 3D). [K]
- **Sketch Text** PM [K]: **Curves** selection box (text follows a curve/edge) · Text box ·
  Bold / Italic / Rotate · alignment Left / Center / Right / Full Justify · Flip vertical / Flip
  horizontal · Width factor % · Spacing % · **Use document font** · **Font…** button. Link to
  property button. [H "Link to Property" topic exists]
- **Sketch Picture**: picture opens with a PM for origin X/Y, angle, width/height, lock aspect,
  transparency (none / from file / full image / user-defined colour), Auto-trace.

---

## 6.20 Trim Entities  [H 2012–2024, B GoEngineer, Lynda]

Where: Sketch tab; Tools > Sketch Tools > Trim. Owner shortcut **T = Trim**, sketch gesture
**DL = Trim** [O].

**PM "Trim"**
- Message: how to use the current option.
- **Options** (five big buttons): **Power trim** (default) · **Corner** · **Trim away inside** ·
  **Trim away outside** · **Trim to closest**.
- Checkboxes: **Keep trimmed entities as construction geometry** (trimmed parts become
  construction instead of being deleted) · **Ignore trimming of construction geometry**
  (construction is not affected). Both → solid entities converted, construction untouched.

Behaviour:
- **Power trim**: hold the left button and **drag across entities** — every entity the grey
  trail crosses is trimmed to its nearest intersections; release hides the trail. Click a single
  entity also trims it. **Extend** with Power trim: drag from an entity's end along its direction
  to extend it to the next entity. [H][B Lynda]
- **Corner**: click two entities; hovering the second shows a preview; both are trimmed **or
  extended** to meet at a corner (overhang removed); order doesn't matter. [H][B]
- **Trim away inside / outside**: pick two **bounding entities** (can differ), then the entities to
  trim; only open segments; entities must cross each boundary once or not at all. [H]
- **Trim to closest**: click an entity → removed up to the closest intersection; **drag** it to
  extend to an intersection; pointer changes to the trim cursor. [H]
- Hover highlights the segment that will be removed (red). [K]

## 6.21 Extend Entities [K]
Pointer changes; hovering an entity previews (red) the extension to the next entity; click to
extend. Mostly replaced by Power trim extend.

## 6.22 Offset Entities [H 2012–2018, B Learn SW 2020]
Where: Sketch tab; Tools > Sketch Tools > Offset Entities. Preselect (or pick after) sketch
entities, **a model face** (offsets its loops) or **model edges**.
**PM "Offset Entities"** — **Parameters**:
- **Offset Distance** · **Add dimensions** (adds the offset dimension → fully defined; clearing it
  leaves the offset undefined) · **Reverse** (one-directional side; default outward) · **Select
  chain** (all contiguous entities from one pick; clear to offset a single line of a rectangle) ·
  **Bi-directional** · **Construction geometry**: **Base geometry** and/or **Offset geometry**
  (2013 and earlier: "Make base construction") · **Cap ends** (open chains; with Bi-directional or
  one-directional) → **Arcs** / **Lines**.
- **Dynamic preview: hold the mouse button and drag in the graphics area**; releasing finishes the
  offset at that distance.
- Creates an **Offset relation** — the offset follows the original. Change the size by
  double-clicking the offset dimension (bi-directional has two dimensions).
- Cannot offset fit splines, already-offset splines or results that would self-intersect.

## 6.23 Convert Entities [H 2014–2025, B Javelin 2015]
Where: Sketch tab (flyout with Intersection Curve, Silhouette Entities); Tools > Sketch Tools.
**Preselect-and-click converts immediately**; clicking the tool first opens the PM.
**PM "Convert Entities"** — **Entities to Convert**: selection box "Select Faces, Edges, or
Sketch Entities to Convert" (model edge, loop, face, curve, external sketch contour, sets of
edges/curves) · **Select chain** (all contiguous entities) · **Select all inner loops** button
(2016+: picks every inner loop/hole of the selected face).
Picking rules: a **face converts all its edges**; **face + Ctrl-pick one edge of a loop → only that
loop**; contiguous faces → their outline.
Relations created: **On Edge** (curve follows the model) and an internal **Fixed** on endpoints
(not shown in Display/Delete Relations; dragging an endpoint removes it). In-context with
external references disabled, no relations are created.

## 6.24 Mirror Entities, Dynamic Mirror [B TriMech right-click cue]
**PM "Mirror"**: **Entities to mirror** box · **Copy** checkbox (default on; clear = move) ·
**Mirror about** box (centerline, line, linear edge, plane, planar face). Right-click cue:
after picking entities, right-click (enter symbol) activates *Mirror about*; after picking the
centerline, right-click (check) = OK. Adds **Symmetric** relations.
**Dynamic Mirror**: select a centerline, click the tool → a symmetry symbol appears at both ends;
everything sketched afterwards is mirrored live.

## 6.25 Sketch Fillet / Sketch Chamfer [H 2012–2025, B training guide 2023, Solid Solutions]
Owner gesture **DR = Sketch Fillet** [O]. 2D and 3D sketches.
**PM "Sketch Fillet"**
- **Entities to Fillet** box: one picked entity/corner appears in the list; with two entities
  the fillet name appears. Pick a **corner point**, or two entities, or box-select corners.
- **Fillet Parameters**: **Radius** · **Keep constrained corners** (default on — if the corner
  has dimensions/relations a **virtual sharp** (two short crossing lines) is kept so they
  survive; cleared → a dialog asks whether to delete those relations) · **Dimension each
  fillet** (each gets its own dimension; cleared → fillets get an **Equal** relation and only the
  last is dimensioned).
- The tool trims the corner and creates a tangent arc. Workflow tip: dimension first, then
  fillet, so dimensions go to the virtual sharp. A virtual sharp can be added later: select two
  lines (Shift) and click **Point**. [B]
**PM "Sketch Chamfer"**: **Chamfer Parameters**: *Angle-distance* / *Distance-distance* ·
**Equal distance** · **Distance 1** · *Direction 1 Angle* / *Distance 2*. Pick a corner or two
lines.

## 6.26 Linear / Circular Sketch Pattern [H 2012–2025]
**PM "Linear Pattern"** (Tools > Sketch Tools > Linear Pattern)
- **Direction 1**: **Pattern Direction** box (X-axis by default; or a linear entity, model edge, or
  a line in the same sketch — that line itself cannot be patterned; not a block line) · **Reverse
  direction** · **Spacing** · **Dimension X spacing** · **Number of Instances** (includes the
  seed) · **Display instance count** · **Angle** (from horizontal) · **Fix X-axis direction**.
- **Direction 2** (Y-axis; activates as soon as Number of Instances > 1 / Direction 1 is set):
  Pattern Direction · Reverse · Spacing · **Dimension Y spacing** · Number of Instances · Display
  instance count · **Angle** (from vertical) · **Dimension angle between axes**.
- **Entities to Pattern** box (preselection fills it).
- **Instances to Skip**: click the box, then click instance markers in the graphics area.
- Fully defined pattern: tick Dimension X spacing, Fix X-axis, Dimension Y spacing, Dimension
  angle between axes.
- Graphics: **drag the selection point** (handle) to change distance and angle; with Display
  instance count on, **double-click the count in the graphics area to edit it**; right-click an
  instance > **Edit Linear Pattern** to reopen. [H 2012]

**PM "Circular Pattern"** (Tools > Sketch Tools > Circular Pattern)
- **Parameters**: Reverse direction · **Center X / Center Y** (the sketch origin by default; a
  point/vertex can be picked as the centre) · **Spacing** (total degrees) · **Equal spacing** ·
  **Dimension radius** · **Dimension angular spacing** · **Number** of instances · **Display
  instance count** · **Radius** · **Arc Angle** (from the centre to the seed's centre).
- **Entities to Pattern** · **Instances to Skip** — as linear.
- Edit: right-click an instance > Edit Circular Pattern; double-click the count. [H 2012]

## 6.27 Move / Copy / Rotate / Scale / Stretch Entities [H 2011–2024]
One PM family ("Move-Copy-Rotate-Scale-Stretch PropertyManager"), used in sketches **and
drawings**. Move and Copy **do not create relations** to the new location.
- **Move** / **Copy**: **Entities to Move/Copy** box · **Keep relations** (on: relations kept;
  off: relations to *unselected* entities break, relations among the selected ones stay) ·
  **Parameters**: **From/To** (pick a Base point = start, then click the destination; preview
  follows the pointer) or **X/Y** (Delta X, Delta Y) · **Repeat** (move/copy again by the same
  amount). Copy carries dimensions and relations to the copy. 3D sketch: Translate Delta X/Y/Z
  and a **triad** (drag arrows/rings).
- **Rotate**: entities · Keep relations · **Center of Rotation** (Base point) · **Angle**; or
  drag the handles of the rotate icon. 3D sketch: Rotation Reference (a line) + Reference Angle,
  or Rotation Origin + Rotation Angle (clear the reference to get them back).
- **Scale**: entities · **Scale about** (Base point) · **Scale Factor** (2 = double, 0.5 = half)
  · **Copy** + **Number of Copies**.
- **Stretch**: **Entities to Stretch** (box-select so some endpoints are inside) · **From/To**
  (Base point, drag; on release the entities stretch and **the PM closes**) or **X/Y** (Delta X,
  Delta Y) · **Repeat**.

## 6.28 Split Entities, Construction Geometry, Make Path, Jog Line, Segment [K]
- Split: click on an entity to add a split point.
- Construction Geometry: toggles selected entities between solid and construction (dashed).
- Make Path: chains entities so they act as one path (for belts/cams).
- Segment: equally spaced sketch points or segments on an entity (count).

## 6.29 Smart Dimension and the Dimension PM — see 05_sketch_environment.md §5.6–5.7
## 6.30 Add Relations, Display/Delete Relations, Fully Define Sketch, SketchXpert,
Check Sketch for Feature — see 05_sketch_environment.md §5.8–5.12
