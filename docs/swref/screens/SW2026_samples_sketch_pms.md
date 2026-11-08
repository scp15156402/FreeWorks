# SOLIDWORKS 2026 samples from the owner (sketch PMs) — text record
Owner-supplied screenshots (2026-11-08), Student 2026 SP3, **dark theme + Simplified Interface** (so layout differs from the 2020 course). Image files are kept **locally only** in `dev/refshots/` (git-ignored); this file is the committed description. Treat as version-3 reference where it differs from the course.

## sw2026_sketch_edit-sketch_pm_cmdmgr.png — Sketch tool, nothing selected
- CommandManager tabs: Features, **Sketch** (active), Evaluate, Surfaces, Simulation, Analysis Preparation.
- Sketch tab, left to right: **Sketch** (large, with dropdown), **Smart Dimension** (large, dropdown); two columns of small tools (Line/Corner Rectangle/Slot in column 1 with dropdowns; Circle, Polygon-like, Ellipse, Spline, Text "A", Point in columns 2–3); **Trim Entities**, **Convert Entities**, **Offset Entities**, **Offset On Surface** (large, stacked label text); small stack **Mirror Entities, Linear Sketch Pattern, Move Entities** (with dropdown); **Add Relation, Repair Sketch, Quick Snaps** (large); **Rapid Sketch, Instant2D, Shaded Sketch Contours** (large). Greyed buttons while no sketch is active.
- Heads-up toolbar centred above the graphics: orient, select, pan, rotate, zoom-to-area etc.; right-hand task-pane tab icons (Design Library, File Explorer, View Palette, Appearances, Custom Properties/…).
- Left pane: PropertyManager tab active in the five-tab strip (FeatureManager, PropertyManager, ConfigurationManager, DimXpertManager, DisplayManager). Title **Edit Sketch** with help "?"; only a red ✕ under it; group **Message** (yellow box): "Select a plane on which to create a sketch for the entity."
- Graphics: Front, Top, Right planes in blue outline with italic labels; dashed axes; triad bottom left; view label "*Trimetric"; large faint red ✕ at top right (confirmation corner for cancel).
- Status bar: prompt text left; "Editing Part", "Simplified Interface", "MKS" right. Bottom tabs: Model | Motion Study 1.
- Left strip of vertical icons (Simplified-Interface features) next to the PM.

## sw2026_trim_pm.png — Trim Entities PropertyManager
- Title **Trim** with help "?"; green ✔ only.
- **Message** (yellow): "To trim entities, hold down and drag your cursor across the entities, or pick on an entity and then pick on a bounding entity or anywhere on the screen. To extend entities, hold down the shift key and drag your cursor across the entities."
- Group **Options** (icon + label rows, one pressed): **Power trim**, **Corner**, **Trim away inside**, **Trim away outside**, **Trim to closest**; checkboxes **Keep trimmed entities as construction geometry**, **Ignore trimming of construction geometry**.

## sw2026_convert_entities_pm_offset_tooltip.png
- **Convert Entities** PM: title with cube-edge icon and "?"; buttons ✔ ✕ and pushpin (keep visible); group **Entities to Convert** (blue selection box); checkboxes **Select chain**, **Inner loops one by one**; button **Select all inner loops**; checkbox **For Construction**.
- Rich tooltip for **Offset Entities** (hovering the CommandManager button): bold title, illustration (square with offset yellow outline, 1.00mm callout with mouse icon), text "Offsets one or more sketch entities by a specified distance. For example, creates a line offset from the selected line. If the original entity changes, then the offset entity also changes when you rebuild the model."

## Corrections/additions to the catalogue
- 06_sketch_tools: Trim PM (five options + two checkboxes + message), Convert Entities PM (Select chain, Inner loops one by one, Select all inner loops, For Construction), Offset Entities tooltip wording; Sketch tab button order above. Verify 2020 differences (e.g. Quick Snaps/Repair Sketch placement, Rapid Sketch/Instant2D, Shaded Sketch Contours) against course frames in W2.
