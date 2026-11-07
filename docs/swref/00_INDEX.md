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
| 01_ui_framework.md | PropertyManager anatomy, accept/cancel, RMB cue, window layout, CommandManager tab contents, context toolbars, shortcut menus, Select Other, breadcrumbs, shortcut bar, gestures, keyboard, heads-up toolbar | draft 1 |
| 02_view_navigation.md | MMB rules, exact wheel-zoom behaviour, keyboard view control, Normal To rules, triad, orientation, transitions | draft 1 (well sourced) |
| 03_selection.md | highlighting, box/cross/lasso colours, contextual selection, filters (incl. 2026), tree picks | draft 1 |
| 04_featuremanager.md | default tree, prefixes/icons, interactions, rollback, options, naming | draft 1 |
| 05_sketch_environment.md | entering/exiting, sketch on face, auto-rotate, inference & quick snaps, numeric input, Smart Dimension rules, Modify box, Dimension PM, relations PMs, Fully Define, SketchXpert, Check Sketch, sketch options | draft 1 |
| 06_sketch_tools.md | two-state PMs for every entity and tool (Line, Rectangle, Circle, Arc, Slot, Polygon, Ellipse, Spline, Point, Text, Trim, Extend, Offset, Convert, Mirror, Fillet/Chamfer, Patterns, Move/Copy/Rotate/Scale/Stretch) | draft 1 (most PMs verified) |
| 07_boss_cut_features.md | common sketch-finding behaviour, Extrude, Revolve, Sweep, Loft, Boundary, Rib | draft 1 (Extrude/Revolve/Sweep/Loft verified) |
| 08_applied_features.md | Fillet (all types, FilletXpert), Chamfer, Hole Wizard (+ Advanced Hole), Shell, Draft, Thicken, Thread, Dome, Wrap | draft 1 (Fillet/Chamfer/Hole/Shell/Draft verified) |
| 09_patterns_mirror.md | common pattern options, Linear, Circular, Mirror, Curve/Sketch/Table driven, Fill, Variable | draft 1 |
| 10_reference_geometry.md | Plane, Axis, Coordinate System, Point, COM, Bounding Box, Mate Reference | draft 1 (Plane verified) |
| 11_multibody_direct.md | bodies, Move/Copy Bodies, Combine/Intersect/Split/Delete Body, Move/Delete Face, Instant3D | draft 1 |
| 12_evaluate.md | Mass Properties, Measure, Section View, Interference, other analyses | draft 1 (Mass Props/Measure verified) |
| 13_configurations_equations.md | Equations dialog (4 views), Link Values, ConfigurationManager, Add Configuration, Modify Configurations, design tables | draft 1 (Equations verified) |
| 14_assembly.md | Begin Assembly/Insert Components, Mate PM + pop-up, Quick Mates, SmartMates, Move/Rotate Component incl. collision/dynamics/clearance, triad, Replace, sub-assemblies, patterns, mirror, in-context, exploded views | draft 1 (Mate/Move verified) |
| 15_drawings.md | new drawing, Model View PM, view types, Section View PM, annotations, sheets | draft 1 |
| 16_18_options_files_visual.md | System Options / Document Properties pages, New/Open/Save, visual style and colours | draft 1 (mostly K) |
| 90_hidden_interactions.md | Ctrl / Shift / Alt / Tab / RMB / double-click / drag behaviours, pointer cues | draft 1 (help "Time Saving Keyboard Shortcuts" + blogs) |
| 91_release_changes.md | milestones 2008–2025, SOLIDWORKS 2026 SP0–SP5 behaviour changes | draft 1 |

Verified after the first draft (2026-11-08): Mirror, Axis, Coordinate System, Begin Assembly /
Insert Components, Instant3D rulers, Design Table, Add Configuration / Configuration Table,
Interference Detection.

Remaining verification queue (items still tagged [K]): Replace Components; Exploded View;
Spline/Ellipse/Text/Point PMs; **per-selection context toolbar contents (needs owner
screenshots — V2_PLAN Q1)**; System Options page lists; Section View PM (parts); sketch status
colours for dangling/not solved/invalid; Revolve auto-axis from a single centerline; Extrude
preview colours and depth callout; FeatureManager rollback details; Shortcut-menu contents.

Also see `92_community_painpoints.md` (forum evidence) and `95_gap_matrix.md` (gaps and approach).

## Research log
- 2026-11-08: help.solidworks.com now serves a JavaScript shell (WebFetch sees "Loading JS…");
  nexthelp.solidworks.com serves the same topics as static HTML and is the readable source.
  The shell in this workspace cannot reach either site, so pages are read through WebFetch.
