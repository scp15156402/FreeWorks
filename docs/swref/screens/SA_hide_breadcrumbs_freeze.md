# S-A hide/show/isolate, breadcrumbs, freeze bar  (jYKADdl2bic, TSLlpGiV2jI, LKOwvun2oAo, KCTeEzLYwHs, Jk0PPItsSpU) — from transcripts
Source [id m:ss]. Breadcrumbs exist since ≈2020 per the speaker, so they may be absent from the course UI: check in step H whether 2020 SP3 shows them (they do not appear in 01.03/01.05 frames).

## Hide / Show / Isolate
- Right-click a body/component in graphics or tree ▸ Hide / Show (with mixed selection both "Show Components" and "Hide Components" are offered) [jYKA 0:20–0:37; TSLl 0:31].
- **Tab** (hover) hides the component under the cursor; holding Tab and sweeping over parts hides each; **Shift+Tab** shows; **Ctrl+Shift+Tab (hold)** shows all hidden components as transparent so a hidden one can be clicked to restore [TSLl 1:36–2:20; jYKA 0:45–1:13].
- Folder icon turns **blue/white** when it holds both shown and hidden components [TSLl 0:56]; the Display Pane (expanded tree) has a per-row part icon to toggle hidden state [TSLl 1:03].
- CommandManager **Show Hidden Components**: only hidden parts are displayed; clicking one makes it show on exit [TSLl 1:10–1:36].
- **Flyout FeatureManager / pop-up context toolbar** offers hide, transparency, colour, appearance; items save into display states [jYKA 1:21–1:52].
- **Isolate**: select bodies ▸ Isolate; save as a display state; switch states in ConfigurationManager or right-click DisplayManager [jYKA 1:52–2:40].

## Breadcrumbs  [LKOw, KCTe]
- On selecting a face/part etc. a breadcrumb bar shows (top of graphics area by default): face ▸ feature ▸ sketch ▸ body ▸ part ▸ assembly (also primary planes/origin, bounding box, and related mates for a component) [LKOw 0:30; KCTe 0:25–1:21].
- Each crumb: click or **right-click** gives that entity's context menu (Edit Feature, body display properties, Edit Sketch, Edit Mate/Delete …) [LKOw 0:44; KCTe 0:57].
- **D key** puts the breadcrumb bar at the cursor; Options ▸ search "breadcrumbs" ▸ "show breadcrumbs at mouse pointer" makes it permanent [LKOw 1:08–1:35].
- A bad mate appears as a crumb; clicking it shows the issue text; right-click ▸ Edit / **Auto Repair** (new in recent versions) [LKOw 1:39–2:19].
- In assemblies a **Mates** subfolder under the component lists its mates [KCTe 1:52].

## Rollback / Freeze bars  [Jk0P]
- Freeze bar: **not on by default**; System Options (General page) checklist at the bottom ▸ **Enable Freeze Bar** ▸ gold bar appears under the top-level part name [0:45–1:08].
- Dragging it down ghosts features as in rollback but with **lock icons** beside them; frozen features are not rebuilt [2:15–2:53]. Rebuild time 10.88 s → 4.98 s in the demo; Performance Evaluation tool updates live [1:24, 3:27].
- Rollback bar is the blue bar at the bottom; dragging up makes features look suppressed [0:21–0:37].

## Corrections/additions to the catalogue
- 04_featuremanager: freeze-bar option location + lock icon; folder blue/white indicator.
- 03_selection / 90_hidden_interactions: Tab, Shift+Tab, Ctrl+Shift+Tab, D-key breadcrumbs.
- 16_18_options_files_visual: General page ▸ "Enable Freeze Bar", "show breadcrumbs at mouse pointer".

## Not shown (no frames)
- Display pane layout, breadcrumb bar appearance, lock icon appearance.
