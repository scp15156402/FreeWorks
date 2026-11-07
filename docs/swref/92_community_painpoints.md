# 92 — What SOLIDWORKS / commercial-CAD users trip over in FreeCAD (community evidence)

Sources: r/FreeCAD threads 2024–2026 (via mirrors), FreeCAD tracker #3402, V1 Engineering forum,
OpenSCAD list, Duet3D forum, Lemmy threads, maker forums (search 2026-11-08). These match the
owner's own report (sketch-on-face retention, fillet edge selection, zoom to pointer, missing
windows after interactions).

| Pain point | Evidence | SOLIDWORKS behaviour to copy (catalogue ref) |
|---|---|---|
| Constraint/dimension tools feel clunky and slow | V1 Engineering forum; r/FreeCAD "dimension tool … always works" rant after 1.0 | One Smart Dimension with placement-driven results, Modify box, automatic relations with glyphs, context-toolbar relations (05 §5.3–5.8) |
| Fillet/chamfer unreliable; "works on one edge but not its copy"; "sometimes a separate selection window appears" | Lemmy, OpenSCAD list, Duet3D, teamfdm (TNP + fillets) | Fillet PM accepts picks any time, no confirm step, preview modes, setbacks/overflow options, Keep features, Select through faces (08 §8.1) |
| Can't select sketch regions/faces to extrude | Duet3D forum | Selected Contours, Instant3D contour drag (07 §7.1, 11 §11.5) |
| Can't click a dimension to reference it in another dimension | Reddit 2026 | Modify box: click any dimension to insert its name; `=` with global variables (05 §5.6, 13) |
| Selection in dense geometry is hard | IntoFPV forum | Select Other, filters (E/V/X), Quick Snaps, Shift transparency, box/cross colours (03, 05) |
| Missing the **S** shortcut bar | r/FreeCAD "Tips for a Solidworks user" | Shortcut bar with search per context (01 §1.7) |
| Workflow differs; must "unlearn" habits; topological naming breaks models | Lemmy, teamfdm | Sketch-on-face that follows the face; feature-first workflow; rollback/reorder (05 §5.1, 07 §7.0, 04) |
| UI "janky"; forks (AstoCAD, Ondsel) praised for UI | Reddit | Reference for UI patterns, not code (AstoCAD is paid; Ondsel discontinued) |
