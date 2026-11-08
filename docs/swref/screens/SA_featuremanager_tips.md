# S-A FeatureManager tips  (ncsqQowfgYU, PDkKE4ePjO8, RLl33-K4ymA, tzx9ic8vvNQ) — from transcripts
SOLIDWORKS-channel videos (≈2023–25 UI). Mark: [2020?] = feature exists in 2020; unmarked = verify in H step. Source [id m:ss].

## Tree folders and tools
- **History** folder: expand to see the last features/sketches worked on [ncsq 0:47] (2020 has History; "recent" content per help).
- **Filter bar** at the very top of the tree: filter-as-you-type, finds features, components, mates; in assemblies option **Filter Graphics View** hides non-matching components; includes sub-assembly components; **✕** clears [ncsq 1:06–1:45]. Better with renamed features.
- **Sensors** folder: right-click ▸ add sensor types – parts: Simulation Data, Mass Properties, Dimension, Measurement, Costing, Sheet Metal; assemblies also Interference Detection and Proximity. Mass Properties sensor has an **alert** checkbox with threshold (e.g. > 2650 g); on rebuild the Sensors folder shows a warning, expanded sensor shows the message; fixing geometry clears it [ncsq 1:56–2:58].
- **Dynamic Reference Visualization**: right-click the top-level icon ▸ two toggles **Parent** and **Child**; hovering a feature/component for ~1 s draws arrows to parents (sketch plane, referenced solids, origin) / children (mirror, mates) [PDkK 0:39–1:32].
- **Design Binder**: hidden by default; shown via System Options ▸ FeatureManager (tree item list: Show/Hide/Automatic). Contains embedded Word "Design Journal"; right-click ▸ add attachments (images, spreadsheets, docs), optionally **linked** (updates on open) [PDkK 1:54–3:00].
- **Markups**: CommandManager Markup tab (enable via right-click Tabs); stored in a **Markups** folder; double-click restores the saved view orientation; Ctrl+select several then **Export Markup** → PDF [PDkK 3:05–4:20].
- **Rollback bar** (blue line at the bottom of the tree, "time machine"): roll back, insert features before others, roll forward; with option "Arrow key navigation" the Up/Down arrows move the bar when it is selected [RLl3 0:34–1:20, 3:54–4:10].
- **Freeze bar** (yellow line near the top of the tree): features above it are not rebuilt (6 s → 0.5 s in the demo); must be activated in Options if not shown [RLl3 1:21–2:29].
- **Comments**: right-click a feature/sketch ▸ **Comment** flyout ▸ new comment (text, images); feature gets a comment icon; hover shows a balloon; a **Comments** folder near the top lists all (right-click ▸ view all) [RLl3 2:29–3:20].
- **System Options ▸ FeatureManager** page: bottom list of tree items each with Show / Hide / **Automatic** (shown only if non-empty, e.g. Surface Bodies) [RLl3 3:26–3:54].

## Assembly tree [tzx9]
- Right-click top-level ▸ **Tree Display ▸ Component Name and Description…**: Primary / Secondary / Tertiary combos (Component Name kept; Configuration Name and Display State Name cleared), Apply and OK [0:29–0:50].
- Tree Display ▸ **Group Component Instances** (collapses identical instances; expand for each) [1:03].
- Right-click **Mates** folder ▸ **Group Mates ▸ Separate Fasteners** → new Fasteners folder [1:25].
- Right-click empty area ▸ **Collapse Items** [1:44] (also Shift+C).

## Corrections/additions to the catalogue
- 04_featuremanager: filter bar, Sensors, DRV, Design Binder, Markups, Comments, Freeze bar, Tree Display options, group mates.
- 16_18_options_files_visual: FeatureManager options page (tree item Show/Hide/Automatic, Arrow key navigation, Freeze bar option).

## Not shown (no frames)
- Exact dialog/PM layouts for Sensor, Tree Display, Comment; check in step H against 2019–2021 help.
