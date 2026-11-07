# 16–18 — Options, file handling, visual style

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.

## 16 Tools > Options
One dialog with two tabs: **System Options** (per user) and **Document Properties** (per file /
template); left list of pages, **Reset…** per page or all, **Search Options** box (2014+), OK /
Cancel / Help. [H/K]

System Options pages (2024–2026) [K list; pages detailed elsewhere are linked]:
General (Input dimension value, Single command per pick, Show dimension names, Show errors every
rebuild, Enable Confirmation Corner, Auto-show PropertyManager, Auto-size PropertyManager when
splitting, Show thumbnail graphics in Windows Explorer, Use English menus/language, Enable Freeze
bar, When rebuild error occurs: Prompt/Stop/Continue, Custom property used as component
description, Show latest technical alerts …) · MBD · Drawings (+ Display Style, Area Hatch/Fill,
Colors, Performance) · **Colors** (Color scheme settings list, Current color scheme, background
appearance: Use document scene background / Plain / Gradient / Image file / Environment) ·
**Sketch** (see 05 §5.13; sub-pages Relations/Snaps, Display) · **Display** (Hidden edges displayed
as solid/dashed, Part/Assembly tangent edge display As visible / As phantom / Removed, Edge display
in shaded with edges mode HLR/Wireframe, Anti-aliasing (None / Anti-alias edges/sketches only /
Full scene), Display shading in HLR?, Highlight all edges of features selected in graphics view,
**Dynamic highlight from graphics view**, Show open edges of surfaces in different color, Display
shaded planes, Display reference triad, Display scrollbars in graphics view, Display draft quality
ambient occlusion, Display SpeedPak graphics circle, Display notification of hidden components,
Projection type for four view viewport) · **Selection** (Select hidden edges/vertices in
wireframe/HLV/HLR/shaded, Enhanced small face/edge selection, Enable selection through
transparency, Select over geometry, …) · **Performance** (Verification on rebuild, Ignore
self-intersection check for some sheet metal features, Transparency high quality, Curvature
generation, Level of detail slider, Assemblies: Automatically load components lightweight, Always
resolve subassemblies, Check out-of-date lightweight components, Resolve lightweight components,
Rebuild assembly on load, Purge cached configuration data, **Update mass properties while saving
document**, Use shaded preview, Use Software OpenGL, No preview during open) · Assemblies (Move
components by dragging, Prompt before changing mate alignments on edit, Optimize mate solving,
Save new components to external files, Update model graphics when saving files, Large
assemblies/design review thresholds …) · External References · Default Templates · File Locations
· FeatureManager (see 04) · **Spin Box Increments** (Length increments English/Metric, Angle
increments, Time increments) · **View** (see 02) · Backup/Recover · Touch · Hole Wizard/Toolbox ·
File Search · Collaboration · Messages/Errors/Warnings (dismissed messages) · Synchronize
settings · Import · Export.

Document Properties pages: **Drafting Standard** (Overall drafting standard ANSI/ISO/DIN/JIS/BSI/
GOST/GB; Rename/Copy/Delete/Load from external file) with sub-pages Annotations, Borders,
Dimensions, Virtual Sharps, Tables, DimXpert · **Detailing** · **Grid/Snap** (Display grid, Dash,
Automatic scaling, Major grid spacing, Minor-lines per major, Snap points per minor, Go To System
Snaps) · **Units** (**Unit system: MKS / CGS / MMGS / IPS / Custom**, table Type × Unit × Decimals ×
Fractions × More: Basic units Length/Dual dimension length/Angle; Mass/Section Properties
Length/Mass/Per unit volume; Motion units Time/Force/Power/Energy; Decimal rounding Round half
away from zero/towards zero/to even/Truncate) · Line Font · Line Style · Line Thickness · Model
Display (colours of model, transparency, apply same colour to wireframe/HLR/shaded) · **Material
Properties** (Density, Area hatch/fill) · Image Quality (shaded & draft HLR/HLV resolution
slider, deviation, Save tessellation with part document; Wireframe and high quality HLR/HLV
resolution; Apply to all referenced part documents) · Sheet Metal · Weldments · Plane Display
(Faces: front/back colour, transparency; Edges; Intersections Show intersections) · DimXpert ·
Configurations · Additive Manufacturing. Owner: MMGS, density 1000, positive inertia tensor
notation [O]. FreeWorks 1.5.1 built a first Options dialog (optionsdlg.py).

Status bar unit button: click → list of unit systems + **Edit Document Units…** (jumps to the Units
page). [K]

## 17 Files [K]
- **New SOLIDWORKS Document** dialog: Novice view (Part / Assembly / Drawing big buttons +
  descriptions) / **Advanced** view (template tabs from File Locations > Document Templates, list/
  icon views, preview); remembers the last view. **Welcome dialog** (2018+; Home / Recent /
  Learn / Alerts tabs; New Part/Assembly/Drawing buttons; Recent documents & folders; "Do not show
  at startup").
- **Open** (Ctrl+O): Windows dialog + SOLIDWORKS extras — **Mode** (Resolved / Lightweight / Large
  Design Review), **Configurations** list, **Display States**, **References…**, Quick Filter
  buttons (parts/assemblies/drawings/top-level assemblies), thumbnail preview; file type list for
  imports (STEP, IGES, Parasolid, ACIS, DXF/DWG, STL, 3MF …) with **Options…** (import as solid/
  surface, 3D Interconnect).
- **Recent documents** (R): thumbnails grid, pin documents, Show all, open folder.
- **Save / Save As** (Save as copy and continue / Save as copy and open; Description; **Include
  all referenced components**, Add prefix/suffix, Advanced); **Save All**; Pack and Go; **Save as
  previous version** (2026 option default version); Export formats with Options (STEP AP203/
  AP214/AP242, IGES, STL resolution, PDF, DXF/DWG …).
- **Rebuild indicators** on the document tab; *Modified documents* prompt on close (Save All /
  Don't Save / Cancel; list with checkboxes).
- **Document properties (File > Properties)**: Summary, **Custom**, **Configuration Specific**
  tabs; property names drop-down, value/text expression with links to mass etc. (`"SW-Mass@…"`).
- Templates (.prtdot/.asmdot/.drwdot) carry Document Properties and custom properties.

## 18 Visual style [O, K]
- Owner theme: **dark** (Color Theme ID 3), viewport **gradient top RGB(94,109,132) → bottom
  RGB(45,50,60)**, preselection **orange**, selected face **blue**, sketch under-defined **blue**,
  fully defined **black** (on a dark theme rendered light), over-defined **red**, construction
  purple-ish [O]. Default (light) theme: light grey-blue gradient background, dynamic highlight
  orange, selection light blue, temporary graphics (previews) yellow/green for add and pink for
  remove material [H thread preview], plane display translucent blue-grey with name labels.
- **Colors** page "Color scheme settings" items include: Viewport Background, Top/Bottom Gradient,
  Dynamic Highlight, Highlight, Selected Item 1/2/3/4, **Temporary Graphics Shaded / Wireframe /
  Add Material / Remove Material**, Sketch Fully/Under/Over Defined, Sketch Invalid Geometry, Sketch
  Not Solved, Inactive Sketch Entities, Dimensions Imported/Not imported/Controlled by design
  table/Dangling, Text, Grid lines, Edges in shaded mode, Hidden edges, Inactive entities,
  Construction geometry, Surfaces open edges, Assembly edit part & non-edit parts, Drawing paper,
  sheet background, PropertyManager skin/selection box colours … [K]
- Fonts: Segoe UI in the UI; "Century Gothic" for dimensions in ANSI templates; **DS ISO font**
  (2026). Icons: flat 2016+ style (FreeWorks keeps original icons — project rule).
- Feature preview: semi-transparent shaded preview; **selection boxes and their picks share colour
  coding** (e.g. Full Round fillet face sets, Boundary curves, Loft profiles: callout colours match
  the PM).
