# SOLIDWORKS reference catalogue (docs/swref)

Research for FreeWorks 2.0.0, started 2026-11-08. The owner asked for exhaustive research
**before any further development**: for every command and UI element in CSWA/CSWP scope, what
clicking it opens, every option with its exact name, when options appear, what the graphics area
shows, how the tree/status bar/selection behave, and how the mouse and keyboard work.

This catalogue is the source of truth for "what SOLIDWORKS does". The gap matrix and
`docs/SW_BEHAVIOR_SPEC.md` build on it; `dev/V2_PLAN.md` builds on those.

## How each entry is written

```
### <Command name>  (where it lives: CommandManager tab / menu path / shortcut)
Opens:        what appears (PropertyManager, dialog, pop-up toolbar, cursor change)
Preselection: what happens if something is selected first / nothing is selected
Groups:       each PropertyManager group box, in order, with every control:
              exact label · type (selection box, combo, spin, checkbox, button) · default ·
              when it is shown/enabled
Graphics:     preview colour/transparency, callouts, handles, arrows, rulers, triads
Interaction:  clicks, double-clicks, drags, right-clicks, keyboard keys, Tab/Enter/Esc
Tree/status:  FeatureManager node name/icon, status bar text, error/warning text
Edit:         how the feature is edited later (Edit Feature, Instant3D, double-click)
Sources:      URLs
```

Sources are mostly the official help (help.solidworks.com / nexthelp.solidworks.com, 2015–2026),
reseller blogs (GoEngineer, Javelin, TriMech, Hawk Ridge, CADimensions, CATI, Engineers Rule),
What's New notes, and forum threads. Where sources disagree the newest SOLIDWORKS version
(2026, which the owner uses: 2026 SP1.1) wins and the difference is noted.

## Files and coverage

| File | Area | Status |
|---|---|---|
| 01_ui_framework.md | CommandManager, menus, Manager Pane, PropertyManager anatomy, confirmation corner, heads-up toolbar, status bar, task pane, shortcut bar, context toolbars, breadcrumbs, gestures, Welcome/New, Customize, Simplified Interface | todo |
| 02_view_navigation.md | mouse/keyboard view control, view orientation, view selector, zoom/pan/rotate rules, display styles, section view | todo |
| 03_selection.md | pick rules, selection filters, box/lasso, Select Other, Ctrl/Shift, hidden edges, Select Tangency/Loop/Chain | todo |
| 04_featuremanager.md | design tree, rollback, reorder, rename, folders, flyout, What's Wrong, parent/child | todo |
| 05_sketch_environment.md | entering/exiting a sketch, sketch on face/plane, inference, automatic relations, numeric input, Smart Dimension, Modify box, Add/Display relations, sketch states, SketchXpert | todo |
| 06_sketch_tools.md | every sketch entity and sketch tool PropertyManager | todo |
| 07_boss_cut_features.md | Extrude, Revolve, Sweep, Loft, Boundary (boss and cut), thin, feature scope, selected contours | todo |
| 08_applied_features.md | Fillet (all types, FilletXpert), Chamfer, Hole Wizard, Simple Hole, Shell, Draft, Rib, Dome, Thread, Wrap | todo |
| 09_patterns_mirror.md | Linear, Circular, Curve-driven, Sketch-driven, Table-driven, Fill, Variable patterns, Mirror | todo |
| 10_reference_geometry.md | Plane, Axis, Coordinate System, Point, Mate Reference, Center of Mass | todo |
| 11_multibody_direct.md | Combine, Split, Move/Copy Body, Delete Body, Move/Delete/Offset Face, Intersect | todo |
| 12_evaluate.md | Mass Properties, Measure, Section Properties, Interference/Clearance, Check, Equations | todo |
| 13_configurations.md | ConfigurationManager, suppression, design tables, global variables, equations | todo |
| 14_assembly.md | Insert Component, mates (standard/advanced/mechanical), SmartMates, Quick Mates, Move/Rotate Component, collision, interference, patterns, mirror, replace, subassemblies, in-context, exploded view | todo |
| 15_drawings.md | sheets, view types, annotations, dimensions (CSWA drafting questions) | todo |
| 16_options.md | System Options and Document Properties pages relevant to the owner | todo |
| 17_files.md | New/Open/Save/Save As, templates, import/export, recent docs, Pack and Go | todo |
| 18_visual_style.md | colours, highlight, preview colours, cursors, icons, fonts | todo |
| 90_hidden_interactions.md | "tips and tricks" behaviour only found by using SOLIDWORKS: drags, double-clicks, keyboard, context menus | todo |
| 91_release_changes.md | What's New 2019–2026 items that change behaviour | todo |

## Research log
- 2026-11-08: help.solidworks.com now serves a JavaScript shell (WebFetch sees "Loading JS…");
  nexthelp.solidworks.com serves the same topics as static HTML and is the readable source.
  The shell in this workspace cannot reach either site, so pages are read through WebFetch.
