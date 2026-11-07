# 05 — The sketch environment

Tags: [H] help, [B] blog/training, [F] forum, [O] owner settings, [K] known, unconfirmed.

## 5.1 Starting a sketch

Ways in [H/K]:
1. **Select a plane or planar face first**, then click **Sketch** (Sketch tab, or the **context
   toolbar** that pops up on the selection, or right-click > Sketch). The sketch opens on it
   immediately.
2. **Click Sketch (or any sketch entity tool — Line, Circle …) with nothing selected** → the
   **"Edit Sketch" message PropertyManager** asks you to select a plane; **in new parts the three
   default planes are displayed, in Trimetric orientation**, and a plane or planar face can be
   clicked. **The plane then rotates Normal To** and the sketch opens — and if you started from
   an entity tool (e.g. Line), that tool is active straight away. [H 2013–2018 "Edit Sketch
   Message PropertyManager"]
3. Feature-first: click Extrude/Revolve/… with nothing selected → pick a plane/face → sketch opens
   → exit the sketch → the feature PM continues (see 07 §7.0).
4. **Create sketch on new part** option (System Options > Sketch): new parts open with an active
   sketch on the Front Plane. [H]
5. Editing: select a sketch or a feature → **Edit Sketch** (context toolbar / right-click). [H/K]

**Sketching on a model face** works the same as on a plane: click any planar face of the body
(including a face just created by an extrude) → Sketch. The new sketch is attached to that face;
when the face's feature changes (e.g. extrude depth), the sketch moves with the face because
SOLIDWORKS references it by its topological identity. [K — core behaviour the owner relies on]

**Auto-rotate view normal to sketch plane on sketch creation and sketch edit** (System Options >
Sketch; renamed in 2018 when it was extended to sketch *edit*) [H 2018 What's New, B CATI]:
- Opening a new or existing sketch rotates the view Normal To the sketch plane.
- **Exit keeping changes** (Confirmation Corner Exit Sketch, Insert > Exit Sketch) → the view
  **stays** normal to the plane.
- **Exit discarding changes** (Confirmation Corner Cancel, Edit > **Exit Sketch without Saving
  Changes**) → the view **reverts** to the orientation before the sketch was opened.
- The owner has this on [O].

## 5.2 Inside a sketch

- **Confirmation Corner** shows **Exit Sketch** (sketch icon with check) and **Cancel Sketch**
  (discard changes). [H] Owner gesture **UR = Sketch (exit)** [O].
- **Display plane when shaded**: the sketch plane is drawn (transparent) while editing a sketch in
  Shaded / Shaded With Edges. [H]
- The sketch is edited "in place": other bodies stay visible; the FeatureManager shows the sketch
  name highlighted and the status bar reads **"Editing Sketch1"**. [K]
- **Status bar** while sketching: pointer **X, Y, Z** coordinates, sketch status (**Under
  Defined / Fully Defined / Over Defined**), "Editing Sketch*n*", the unit system (MMGS) button.
  [K]
- **Sketch status in the tree**: prefix **(-)** under defined, **(+)** over defined, none when
  fully defined; **(?)** cannot be solved. [K]
- **Colours** [H Sketch options]: entity points (when *Display entity points in part/assembly
  sketches* is on) — **black fully defined, blue under defined, red over defined, green
  selected**; over-defined and dangling points are always shown. Entities: black fully defined,
  blue under defined, red over defined; dangling (lost reference) brownish-yellow; pink "not
  solved"; yellow "invalid". [K for the last three]
- **Dragging under-defined geometry** in the Select mode moves it (lines rotate/stretch, circles
  resize from the edge, move from the centre); *Ghost image on drag* shows the original. *Override
  dimensions on drag/move* lets dimensions update while dragging. [H]
- **Right-click menu in a sketch** [K]: Select · Recent Commands · the last entity tools · **End
  Chain** (while drawing) · **Sketch Numeric Input** toggle · Add Relation · Display/Delete
  Relations · **Fully Define Sketch** · Construction Geometry · Exit Sketch · Zoom/Pan/Rotate ·
  Customize Menu.
- **Shortcut bar (S key)** in a sketch shows the Sketch shortcut bar (entities, trim, offset,
  relations, dimension) with command search. [K; owner has S rebound — see 01]

## 5.3 Inference, automatic relations, snaps

[K, consistent with H "Insert Line" Quick Snaps note]
- While drawing, **dashed inference lines** (blue/yellow) align the pointer to existing points
  horizontally/vertically and along line directions; points "wake up" when hovered.
- The pointer shows a **relation glyph** (horizontal, vertical, coincident, midpoint, tangent,
  perpendicular, parallel, on-edge, intersection, concentric). The relation is created on click
  when **Automatic relations** is on (Sketch > Relations/Snaps options). **Hold Ctrl** while
  drawing to suppress inference and automatic relations.
- **Quick Snaps** (Sketch toolbar flyout and right-click > Relations/Snaps): Point, Center,
  Midpoint, Quadrant, Intersection, Nearest, Tangent, Perpendicular, Parallel, Horizontal/Vertical
  lines, Horizontal/Vertical to points, Length (snaps to grid increment), Grid, Angle (snap to
  angle increment). One-shot: pick a quick snap during a tool to apply it to the next pick.
  Some line orientations override quick snaps. [H line PM note]
- Grid off in the owner's settings [O].

## 5.4 On-screen numeric input

[H Sketch options 2024, Rectangle PM 2025, B CATI]
- **Enable on screen numeric input on entity creation** — numeric fields appear beside the
  entity being created (line length/angle, rectangle width/height, circle diameter, arc radius
  …). Also toggled by right-click > **Sketch Numeric Input**.
- Sub-option **Create dimension only when value is entered** — a dimension is added only if you
  type a value and press Enter or Tab; clicking without typing adds none. Not available for
  slots.
- **Tab** moves between fields; **Enter** accepts and continues (e.g. a line chain continues
  from the new end); **Esc** ends the tool. Keep the mouse still while typing (moving changes the
  live geometry). [B CATI]
- Each entity PM has **Add dimensions** while this option is on. The owner has numeric input
  **and** add dimension on [O].

## 5.5 Smart Dimension  (owner shortcut **D**, sketch gesture **U = Smart Dimension** [O])

What to click → what you get [H 2012–2021 "Dimensioning a 2D Sketch", B TriMech, SOLIDWORKS
blog, Javelin]:

| Click | Result |
|---|---|
| a line or edge | its length (placement decides aligned / horizontal / vertical) |
| two lines (or line + model edge) | angle; **where you place it decides which of the four angles** |
| two parallel lines | distance between them |
| point + line | perpendicular distance |
| two points | distance (aligned/horizontal/vertical by placement) |
| an arc | radius |
| a circle (circumference) | diameter; **shown linear or as diameter depending on placement** |
| arc + both endpoints | true **arc length** |
| both arc endpoints + arc centre | **arc angle** |
| line, then centerline, pointer dragged **across** the centerline | **doubled distance** (diameter for revolves) |
| an arc/circle together with something else | distance to its **centre** by default |
| **Shift**+click an arc/circle | distance to its **min/max** (the side you click) |

- The dimension **snaps to the nearest orientation as you move**; its text is semi-transparent
  until placed. Right-click while placing **locks** the orientation. [H 2021, TriMech]
- After a centre-to-centre dimension exists, select it → Leaders tab → **Arc Condition**
  First/Second: **Center / Min / Max**; or drag its arc-end handle to min/max. [B]
- After placing, the **Modify** box opens (System Options > General > **Input dimension value**,
  on by default and on for the owner [O]) — see 5.6.
- Esc while placing cancels the pick ("helpful if you accidentally select an entity"). [H]
- **Virtual sharps**: select two lines with Shift and click Point, then dimension to it. [B]
- Moving/copying dimensions: **Shift-drag moves, Ctrl-drag copies** (also to another drawing
  view). [B TriMech]
- **Dimension types flyout**: Smart Dimension, Horizontal, Vertical, Baseline, Ordinate
  (Horizontal/Vertical), Chamfer, Path Length. [K]
- Owner setting "Modify on creation" on [O].

## 5.6 Modify dialog box  [H 2010–2019, B CATI, GoEngineer]

Opens on dimension creation (Input dimension value) or **double-click any dimension** (sketch,
part, assembly, drawing).

- Title bar: dimension full name e.g. **D1@Sketch1** (renaming the sketch updates it); the name
  can be edited here. [B GoEngineer, K]
- **Value box**: type a value, units allowed; works **as a calculator** (`25*2+3`); `=` starts an
  equation with a drop-down of **Global Variables, Functions, File Properties, Measure**.
  Icons appear in the box when the dimension is **linked** (Link Value), **driven by an
  equation**, or is a **global variable**. [H]
- **Spin arrows** (or keyboard Up/Down, mouse wheel) — step by the spin-box increment
  (Tools > Options > Spin Box Increments; default 10 mm per CATI / document units).
  **Ctrl + arrow/wheel/thumbwheel = 10×**, **Alt + … = 1/10**. [H 2012]
- **Thumbwheel** below the value: drag left/right to change by increments; becomes a
  **slider** when the value is bounded (e.g. an angle 0–90°). [H 2017]
- Buttons: **✓ Save** (keep value, close) · **✗ Restore** (original value, close) · **Rebuild**
  (regenerate with the current value, dialog stays open) · **Reverse sense** of the dimension ·
  **Reset spin increment** (opens the Increment box: pick from the list or type a value; **Make
  Default** stores it) · **Mark dimension to be imported into a drawing** (on by default; used by
  Model Items). [H][B]
- **This Configuration / All Configurations / Specify** drop-down for configured parts. [H 2017]
- **Enter** = Save. Values update live in the model as you spin.

## 5.7 Dimension PropertyManager (selecting a dimension) [H 2010–2025 Dimension Value / Leaders]

Three tabs at the top: **Value** · **Leaders** · **Other**. With several dimensions selected only
the common properties are shown. [H]
- **Value**: **Style** (favourites: Apply default, Add/Update/Delete/Save/Load) ·
  **Tolerance/Precision** (Tolerance Type list by dimension type — None, Basic, Bilateral, Limit,
  Symmetric, MIN, MAX, Fit, Fit with tolerance, Fit (tolerance only); Maximum/Minimum Variation;
  Classification, Hole Fit/Shaft Fit; **Show parentheses**; **Unit Precision**; **Tolerance
  Precision**; Link precisions with model; Inward rounding) · **Primary Value** (dimension name
  `D1@Sketch1`, **value** — changing it drives the model; **Override value** (does not update with
  geometry; clearing restores the value, keeps the tolerance); **Reverse Direction**;
  **Configurations** for parts/assemblies) · **Dimension Text** (text box with `<DIM>`; **Add
  Value** to re-insert it; symbol buttons; justify) · **Dual Dimension** (both unit systems,
  dual shown in brackets) · 2nd Tolerance/Precision.
- **Leaders**: Witness/Leader Display (arrows outside/inside/smart, arrow style; **Radius /
  Diameter / Linear** for radial dimensions; Parallel to Axis; arc extension line), Break Lines
  (document gap or custom), **Custom Text Position** (Solid leader aligned text / Broken leader
  horizontal / Broken leader aligned), **Arc Condition** — First / Second: **Center** (default) /
  **Min** (closest) / **Max** (farthest). Dimension to inside of arc; Extend bent leader to text.
- **Other**: **Override Units**, Text Fonts (Use document font / Font…), Layer, Options (Read
  only, Driven). [K]
- **Driven** dimensions (reference) are grey; an over-defining dimension prompts **"Make
  Dimension Driven?" — Make this dimension driven / Leave this dimension driving** (option
  *Prompt to set driven state*; *Set driven by default*). [H Sketch options "Over defining
  dimensions"]

## 5.8 Relations

- **Add Relations PM** (Sketch toolbar Display/Delete flyout > Add Relation, or select entities
  and use the **context toolbar** / PM that appears on selection) [K]: **Selected Entities** box ·
  **Existing Relations** (+ status) · **Add Relations** — buttons only for valid relations:
  Horizontal, Vertical, Collinear, Coradial, Perpendicular, Parallel, ParallelYZ, ParallelZX,
  AlongZ, Equal, Fix, Tangent, Concentric, Midpoint, Intersection, Coincident, Symmetric, Merge,
  Pierce, Equal Curve Length, On Edge.
  **Fastest path in SOLIDWORKS:** select entities (Ctrl/box) → the **context toolbar** next to
  the pointer shows the valid relation icons → one click adds it; the PM on the left shows the
  same buttons. [K]
- **Display/Delete Relations PM** [H 2012–2025] (Tools > Relations > Display/Delete):
  - **Relations**: **Filter** *All in this sketch · Dangling · Over Defining/Not Solved · External
    · Defined In Context · Locked · Broken · Selected Entities* (the last shows the names of the
    entities you pick). **Relations** list — selecting one highlights its entities **and its
    relation icons** in the graphics area (all relation icons shown if View > Sketch Relations is
    on, the selected one in another colour) and lists the entities below. **Information** status
    (Satisfied, Driven, Dangling …; Broken/Locked for in-context). **Suppressed** (this
    configuration; name greys, status Satisfied → Driven). **Undo last relation change**.
    **Delete** / **Delete All**. **Repair All Dangling** (2D, not for external references).
  - **Entities**: table **Entity · Status · Defined In** (Current Sketch / Same Model / External
    Model; external: Owner, Assembly). **Replace** a dangling entity: pick a new entity in the
    graphics area → Replace (status Invalid if unsuitable); **Undo last relation change**.
  - **Configurations** (multi-config models): This configuration / All / Specify (+ All, Reset).
  - **Options**: **Show PropertyManager when the sketch becomes over defined or unsolvable**
    (opens e.g. the Circle PM to fix it); SketchXpert for over-defined sketches.
- **Relation glyphs** on the entities (View > Hide/Show > Sketch Relations); click a glyph to
  select the relation; Delete removes it. [K]

## 5.9 Fully Define Sketch  (Tools > Dimensions > Fully Define Sketch) [K — verify]
**Entities to Fully Define**: *All entities in sketch* / selected · **Calculate**. **Relations**
group (Select All / Deselect All, per-relation buttons). **Dimensions** group: Horizontal
Dimensions scheme (*Baseline* / *Chain* / *Ordinate*) + datum, Vertical scheme + datum,
**Dimension placement** (Above / Below sketch, Right / Left).

## 5.10 SketchXpert  [B SDC book]
Opens on an over-defined/unsolvable sketch (or Tools > Sketch Tools > SketchXpert):
**Diagnose** → **Results** with solution sets (**< >** to step, preview highlights the relations
/dimensions to delete) → **Accept**; **Manual Repair** list of conflicting items; **More
Information/Options** (*Always open this dialog when sketch error occurs*). Message bar colour
shows status.

## 5.11 Check Sketch for Feature  [H 2025]
Tools > Sketch Tools > Check Sketch for Feature: **Feature usage** list (e.g. Base Revolve) →
shows the required **Contour type** (e.g. Multiple Disjoint Closed) → **Check** → message and
**highlighted problem geometry** (e.g. "endpoint wrongly shared by multiple entities").

## 5.12 Instant2D, Rapid Sketch, Close Sketch to Model
- **Instant2D** (Sketch toolbar toggle): click a sketch dimension → drag its arrow handles to
  change the value; a ruler appears for snapping. [K]
- **Rapid Sketch** (Sketch toolbar): sketch on any planar face/plane by hovering it with a sketch
  tool, no need to start a sketch first. [H "Using Rapid Sketch" exists; K detail]
- **Close Sketch to Model** / *Prompt to close sketch*: an open profile + Extruded Boss asks
  "Close Sketch With Model Edges?"; an arrow shows which side closes; Reverse direction option.
  [H]

## 5.13 Sketch options (System Options > Sketch) [H 2010–2025]
Use fully defined sketches · Display arc centerpoints in part/assembly sketches · Display entity
points in part/assembly sketches · Prompt to close sketch · Create sketch on new part ·
Override dimensions on drag/move · Display plane when shaded · Line length measured between
virtual sharps in 3D · Enable spline tangency and curvature handles · Show spline control polygon
by default · Ghost image on drag · Show curvature comb bounding curve · **Enable on screen numeric
input on entity creation** (+ Create dimension only when value is entered) · **Preview sketch
dimension when selected** (selecting an entity previews a dimension you can click to keep) ·
Auto-rotate view normal to sketch plane on sketch creation and sketch edit · Over defining
dimensions: **Prompt to set driven state**, **Set driven by default**. Sub-pages: **Relations/
Snaps** (Enable snapping, Snap to model geometry, Automatic relations, sketch snaps list, Grid,
Snap only when grid is displayed, Angle snap), **Display** (sketch colours).
