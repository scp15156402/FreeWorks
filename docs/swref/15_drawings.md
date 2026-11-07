# 15 — Drawings (CSWA drafting competencies; basic detailing)

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.

## 15.1 New drawing  [H 2012–2024, K]
- New > Drawing → **Sheet Format/Size** dialog (Standard sheet size list with *Only show standard
  formats*, *Display sheet format*, Browse; or *Custom sheet size* width/height) — unless the
  template defines it.
- Then the **Model View PM** starts automatically (option *Start command when creating new
  drawing*) — except via **Make Drawing from Part/Assembly** (which opens the **View Palette**
  in the Task Pane to drag views onto the sheet).
- **Model View PM**: **Part/Assembly to Insert** (Open documents list, Browse…) → Next ➜ ·
  **Thumbnail Preview** · **Reference Configuration** · **Orientation**: *Create multiple views*,
  standard views (Front, Top, Right, Left, Bottom, Back, Isometric), **More views** (Current Model
  View, *Trimetric, *Dimetric, named views), **Preview** · **Mirror** (Mirror view, horizontal/
  vertical) · **Import Options** (*Import annotations*: Design annotations, DimXpert annotations,
  Include items from hidden features) · **Options** (*Auto-start projected view* — after placing,
  move the pointer to drop projected views, Esc ends) · **Display State** (assemblies) · **Display
  Style** (Wireframe, Hidden Lines Visible, Hidden Lines Removed, Shaded With Edges, Shaded; High/
  Draft quality) · **Scale** (*Use sheet scale* / *Use custom scale* — list or *User Defined*
  "x:x") · **Dimension Type** (*Projected* / *True*) · **Cosmetic Thread Display** (High/Draft
  quality) · Select Bodies (multibody), Angle, Flip view (flat patterns).
- **Standard 3 View**: three orthographic views (front, top, right in third angle; projection from
  the sheet properties), fixed orientation, aligned. [B Javelin 2026]

## 15.2 View types (CSWA multiple-choice topics)  [B Javelin 2026, H, K]
**Standard 3 View · Model View · Projected View · Auxiliary View** (perpendicular to a selected
edge) · **Section View** (cutting line through a view → drag the section view; **Section View
Assist**: Cutting Line types *Vertical / Horizontal / Auxiliary / Aligned*, *Auto-start section
view*, *Edit sketch*; Half Section types; offset pop-up toolbar for steps/arcs/notches) · **Aligned
Section** · **Detail View** (circle/profile sketch → magnified view; style per standard, label,
scale, full outline, jagged outline, pin position) · **Broken-out Section** (closed spline/profile
on a view → depth or "Up to" an edge; Preview) · **Break View** (break lines vertical/horizontal,
gap, line style straight/curve/zig-zag/small zig-zag; dimensions stay true) · **Crop View** (closed
sketch → crop) · **Alternate Position View** (assemblies: phantom lines) · **Relative View** (two
faces define front/right) · **Predefined / Empty view** · **3D Drawing View**.
- **Section View PM** (drawings) [H 2012–2022]: Section Line (**Flip direction** — also
  double-click the section line; **Label** letter; Document font/Font…) · Section View (**Partial
  section**, **Display only cut faces**, **Auto hatching** (alternating in assemblies/multibody),
  **Randomize scale**, **Scale hatch pattern**, **Emphasize outline**, Exclude fasteners,
  **Hide cutting line shoulders** (creation only), **Display surface bodies**, **Cut surface
  bodies**, Foreshorten view) · **Section Depth** (single-segment cutting line; drag the pink section
  plane) · Import annotations · Display Style (Use parent style) · Scale (Use parent scale / Use
  sheet scale / Use custom scale) · Dimension Type · Cosmetic Thread Display.

## 15.3 Annotations and dimensions [K]
**Model Items** PM (Source: Entire model / Selected feature / Selected component; Import items into
all views; Dimensions: Marked for drawing, Not marked, Instance/revolution counts, Tolerance
dimensions, Hole Wizard profile/locations, Hole callout; Annotations; Reference Geometry; Options:
Include items from hidden features, Use dimension placement in sketch; Layer) · Smart Dimension in
drawings (driven/reference, grey parentheses option) · **Note** · **Balloon / Auto Balloon** ·
**Surface Finish** · **Weld Symbol** · **Geometric Tolerance** · **Datum Feature / Target** ·
**Hole Callout** · **Center Mark** (single/linear/circular; slot centre marks) · **Centerline**
(select two edges or a face) · **Area Hatch/Fill** · **Revision Cloud** · **Tables** (BOM, Hole
table, Revision, General, Weld) · **Dimension Palette** (pop-up next to a placed dimension: style,
tolerance, precision, text …; fades unless the pointer moves onto it).

## 15.4 Sheet operations [K]
Sheet tabs at the bottom (add sheet "+", right-click: Properties (Name, Scale, Type of projection
*First angle / Third angle*, Next view label, Next datum label, Sheet Format/Size), Edit Sheet
Format, Activate, Delete). Edit Sheet / Edit Sheet Format modes; title-block fields linked to
properties ($PRPSHEET, $PRP). Owner uses AS standard [O]; FreeWorks has drawing.py templates.
