# 14 — Assemblies (CSWA assembly questions, CSWP segment 3)

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.

## 14.1 New assembly and Insert Components  [H 2012–2025, B Lynda, power guide 2017]
- One PM with two names: **Begin Assembly** (new assembly) / **Insert Components** (existing
  assembly; Assembly tab or Insert > Component > Existing Part/Assembly). Also File > **Make
  Assembly from Part** opens a new assembly with it.
- **Create Layout** (new assemblies) · **Part/Assembly to Insert**: *Open documents* list (Ctrl-
  select several), **Browse…** (**Automatic Browse when creating new assembly** opens the file
  dialog if nothing is open) · **Thumbnail Preview** · **Options**: *Start command when creating
  new assembly* · *Graphics preview* (component follows the pointer) · *Make virtual* · *Envelope*
  · **Show Rotate context toolbar** (on by default: X / Y / Z buttons with an Angle field default
  90° to rotate the attached component before placing) · **Fix / float component on insert**
  (2023+: *Only fix first component* / *Fix* / *Float*).
- Placing: **click OK (✓) → the component origin is coincident with the assembly origin and the
  planes are aligned**; or move the pointer onto the assembly origin (graphics preview) and click;
  or click anywhere to drop it there. **The first component in an empty assembly is fixed `(f)`**;
  later ones float. Multiple components: double-click → all at that spot (at the origin if
  double-clicked there). If not pinned, the PM closes after placing. [H]
- Right-click a fixed component > **Float** (and Fix). [B]
- Drag a part from the File Explorer / Design Library / an open window into the assembly also
  inserts it; with **SmartMates** (Alt-drag) mates on drop.
- Tree: `Part1<1>`, `(f) Part1<1>` fixed, `(-) Part2<1>` under-defined, `(+)` over-defined;
  **Mates** folder (paper-clip icon) at the end with Coincident1, Concentric1 …; each component
  also has its own **Mates** sub-folder listing its mates. FreeWorks already names these
  (asmtree.py).

## 14.2 Mate PropertyManager  [H 2011–2025, B GoEngineer]
Open: Mate (Assembly tab) / Insert > Mate; edit: expand Mates, right-click > Edit Feature (several
mates selected → all appear in the Mates box).
- Tabs **Mates** (2018: Standard, Advanced, Mechanical tabs; earlier one list) + **Analysis**
  (mate properties for Motion/Simulation).
- **Mate Selections**: **Entities to Mate** box (faces, edges, planes, vertices, axes, sketch
  points…; pick from the graphics area or the flyout tree). **Multi-mate mode** (one common
  reference + many entities → many mates; *Link dimensions* for distance/angle multi-mates).
- **Standard Mates** (all shown; only applicable ones enabled): **Coincident · Parallel ·
  Perpendicular · Tangent · Concentric (+ Lock rotation) · Lock · Distance (value, Flip
  dimension) · Angle (value, Flip dimension)**; **Mate alignment** buttons *Aligned* (normals same
  direction) / *Anti-Aligned* (opposite) — **SOLIDWORKS picks the alignment closest to the current
  position**. [H][B]
- **Advanced Mates**: **Profile Center** · **Symmetric** · **Width** (Centered / Free /
  Dimension / Percent) · **Path Mate** · **Linear/Linear Coupler** · **Limit Distance** (max/min)
  · **Limit Angle** (max/min). **Mechanical Mates**: **Cam** · **Slot** · **Hinge** · **Gear**
  (ratio, Reverse) · **Rack Pinion** · **Screw** (Revolutions/length or Distance/revolution,
  Reverse) · **Universal Joint**.
- **Mates** box: the mates added during this PM session.
- **Options**: **Add to new folder** · **Show popup dialog** (Mate pop-up toolbar) · **Show
  preview** · **Use for positioning only** (moves the component, adds no mate) · **Make first
  selection transparent** (2016+; not for width, symmetry, linear coupler, cam, hinge).
- **Mate pop-up toolbar**: appears near the pointer as soon as two entities are picked, with a
  **default mate selected and the components already moved to preview it**; contains the valid
  mate types, distance/angle box, **flip alignment**, **Undo**, **Add/Finish Mate ✓**. Clicking ✓
  adds the mate and keeps the Mate PM open for the next pair. [H 2021, 2025 tutorial; B
  GoEngineer]
- Pin (Keep Visible) keeps the PM open after OK (owner has the mate pushpin on [O]).
- Errors: mate errors show in the tree (red ✖, yellow ⚠); **View Mate Errors**, **MateXpert**,
  **mate callouts** on the model. [H 2021]

## 14.3 Quick Mates and SmartMates  [H 2020–2023 context toolbars, K]
- **Quick Mates context toolbar**: Ctrl-select two entities on different components (no command
  active) → the context toolbar shows valid mate icons (and a distance/angle box); one click adds
  the mate; option **Show OK button** adds Add/Finish Mate for coincident, concentric, parallel,
  symmetric, tangent; option *Show flip alignment and lock rotation after quick mates*.
- **SmartMates**: **Alt-drag** a component face/edge onto another (or drag from outside), the
  pointer shows the proposed mate type icon; **Tab** flips alignment while dragging; drop → mate
  and the pop-up toolbar. Also with Move Component's **SmartMates** button (double-click an
  entity, then click the target). Mate references in parts drive SmartMates.
- Peg-in-hole SmartMate: drag a cylindrical edge onto a hole edge → Concentric + Coincident.

## 14.4 Move Component / Rotate Component  [H 2011–2025, B CATI, Javelin 2026]
- Simple **left-drag of an under-defined component moves it** within its remaining DOF;
  right-drag rotates it (parts: right-drag = mouse gesture unless on a component — see 01 §1.8).
  You cannot move a fixed or fully defined component. [H][K]
- **Move Component PM** (Assembly tab; pointer changes): **Move** — **SmartMates** button ·
  list: *Free Drag* · *Along Assembly XYZ* (triad at the origin; click near an axis, then drag
  along it) · *Along Entity* (line/edge/axis → 1 DOF; plane/face → 2 DOF) · *By Delta XYZ*
  (ΔX ΔY ΔZ + **Apply**) · *To XYZ Position* (pick a point of the component or its origin; X Y Z +
  Apply). **Rotate** (collapsed group, or the Rotate Component command) — *Free Drag* · *About
  Entity* · *By Delta XYZ* (angles about assembly axes + Apply).
- **Options**: **Standard Drag** · **Collision Detection** — *Check between*: **All components** /
  **These components** (+ Components for Collision Check box + **Resume Drag**); **Stop at
  collision**; **Dragged part only** (otherwise the dragged components plus those moved by their
  mates are checked) · **Physical Dynamics** (sensitivity slider; pushes other components within
  their DOF; initially colliding parts turn transparent) .
- **Dynamic Clearance**: components for clearance check + Resume Drag; shows the current minimum
  clearance and the minimum over the drag (cannot run with Physical Dynamics).
- **Advanced Options**: **Highlight faces** (touching faces highlight) · **Sound** (beep at
  collision) · **Ignore complex surfaces** (only planar, cylindrical, conical, spherical,
  toroidal) · **This configuration** (move only in the active configuration; not for collision/
  dynamics/clearance).
- **Move with Triad**: right-click a component > Move with Triad → triad on the component; drag
  arrows/rings; right-click the centre ball: *Show Translate XYZ Box*, *Show Rotate Delta XYZ Box*,
  *Align to…*, *Align with Component Origin*, *Align with Assembly Origin*; click the graphics area
  to dismiss. [H 2012/2019]
- Move confirmation dialog when moving a component that would break mates? [H "Move Confirmation
  Dialog Box" exists — K detail]

## 14.5 Other assembly commands (CSWP list) [K — verify each]
- **Replace Components** PM: Selection (*This component to be replaced*, *All instances*), **With**
  (Browse…), Options (*Re-attach mates*, *Match name/configuration*: Match name / Manually select),
  then the **Mated Entities** PM to fix dangling mate references (each mate listed with status,
  Flip alignment, Accept/Reselect). FreeWorks has replace.py.
- **Insert sub-assembly**: same Insert Components; subassembly appears rigid by default;
  right-click > Component Properties / **Solve as Flexible/Rigid** (context toolbar icon).
- **Make Subassembly from selected components** (right-click > Form New Subassembly).
- **Mirror Components**: Step 1 Selections (Mirror plane, Components to Mirror), Step 2
  orientation (mirror/copy per component, Create opposite hand version), Step 3 file names, Step 4
  feature transfer.
- **Component patterns**: Linear Component Pattern, Circular, Pattern Driven (uses a part's
  pattern), Sketch Driven, Curve Driven, Chain; **Vary**? (component instances to skip).
- **In-context editing**: Edit Part (context toolbar) — the edited part shows in its colour,
  others transparent/grey ("Assembly transparency for in-context edit" option); sketch on another
  part's face creates external references (`->`); Exit via the Confirmation Corner / Edit
  Component button. **Insert > Component > New Part** (virtual part `[Part1^Assem1]`, place on a
  face/plane → editing begins with an InPlace mate).
- **Assembly features** (cuts, holes, fillets in the assembly with Feature Scope of components).
- **Interference Detection**, **Clearance Verification**, **Hole Alignment** — see 12.
- **Exploded View** PM: Explode Steps list, Explode Step Type (Regular / Radial), Settings
  (components, direction triad arrow, distance, angle, Auto-space components, Apply/Done), Options
  (Auto-space, Select subassembly parts, Show rotation rings), Reuse explode; drag the triad arrow
  in the graphics area; explode lines sketch; Animate Explode/Collapse.
- **Coordinate system in assemblies** and **Mass Properties relative to it** (CSWP) — see 10, 12.
- Component context toolbar: Edit Part, Open Part, Hide/Show (Tab/Shift+Tab under the pointer),
  Change Transparency, Isolate, Rebuild, Fix/Float, Make Rigid/Flexible, Component Properties,
  **Quick Mates** row when two entities are selected.
- **Component Properties** dialog: name, instance, description, file path, referenced configuration,
  display state, suppression state (Suppressed / Resolved / Lightweight), Solve as (Rigid/
  Flexible), Exclude from BOM, Envelope.
