# FreeWorks project tracker

**Next part:** P20 – Drawing annotations (model items, centre marks, hole callout, BOM)

Legend: ✅ done · 🔄 in progress · ⏳ next · ⬜ planned · ⛔ blocked
Each part is sized for ≤ 30 minutes of work. Say **"continue"** to run the next part.

## Owner priorities for v1.1 → v1.5 (2026-11-07)
1. Easy one-line installation and updates.
2. Easy entry point for Claude / other AI / developers to bring FreeWorks up to date with the
   newest FreeCAD and SOLIDWORKS ("Let's get it up to date").
3. Software: (a) no crashes or lag ever; (b) cover CSWA + CSWP scope, with assemblies, mates,
   drawings and their workflows/sub-features as close to SOLIDWORKS as possible;
   (c) GUI/UX as close to SOLIDWORKS as possible.
4. Research community projects first, then write our own code where they fall short.
5. New logo (docs/assets/logo_source.png).

## Release plan
| Version | Theme | Parts |
|---|---|---|
| v1.1 | Install/update, AI entry point, stability, research | P1–P11 |
| v1.2 | Materials + Mass Properties, assemblies & mates (SOLIDWORKS workflows) | P12–P17 |
| v1.3 | CSWP segments 1–2: equations, configurations + design tables, Extrude PM, Hole Wizard PM | P26, P27, P22, P24 |
| v1.4 | Drawings | P18–P21 |
| v1.5 | Remaining part PMs, sketching, GUI/UX polish | P23, P25, P28–P34 |

Order of work after P11 (from docs/GAP_ANALYSIS.md): P12 → P17, then P26, P27, P22, P24, then P18 → P21,
then P23, P25, P28 → P34.

## Parts
| # | Track | Part | Status |
|---|---|---|---|
| P1 | Docs/AI | Tracker, CLAUDE.md/AGENTS.md entry point, versions.json, UPDATE_PROTOCOL, new logo (icon, splash, branding, README) | ✅ |
| P2 | Install | One-line install/update + one-line uninstall (owner request); installer v2: versions.json, SHA-256 (GitHub digest), resumable curl download, install.log, preflight, any-PC folder choice, FreeCAD side-by-side swap, Settings→Apps entry, projects in Documents\FreeWorks; released as v1.0.1 | ✅ |
| P3 | Install | Rollback (keeps previous FreeWorks/add-ons/FreeCAD, swap back and forth, in-app + one-liner), What's New dialog + notes in update offer, add-ons pinned to commits; released 1.0.2. Windows field-test fixes move to a new part when feedback arrives | ✅ |
| P4 | Dev/AI | dev/check_updates.py (+--apply), dev/fetch_freecad.sh, dev/run_tests.sh + suite.py (33 checks, perf budgets, report); found+fixed Mass Properties 1000x density bug; released 1.0.3 | ✅ |
| P5 | Stability | Audit of all hook points; @harden/@safe/@safe_slow guards, lazy sketch observer, no main-window filter, async right-click replay, overlay shortcuts disabled, layout self-heal, idle tab prebuild, UI-stall watchdog + slow-callback detector + Diagnostics; 44 tests; released 1.0.4 | ✅ |
| P6 | Stability | Safe mode (--safe, Shift at launch, Start-menu shortcut), crash sentinel → automatic safe start + notice, Reset FreeWorks Settings, Large Model Mode (+ suggestion for big documents); tests for all | ✅ |
| P7 | Stability | Stress test suite (`dev/run_tests.sh --stress`: 30 sketch edits, 300 tab switches, 200 shortcuts, 200 context menus, 25 gestures, 3×12 documents; leak/plateau/stall/slow checks). Findings fixed: MSAA 4x memory growth → line smoothing default (MSAA opt-in), styles scoped to FreeWorks widgets, faster dock healing, status bar restyle only on change; released 1.0.5 with P6 | ✅ |
| P8 | Research | CSWA + CSWP exam scope (official topic lists, sample exams) → docs/CSWA_CSWP_SCOPE.md (≈70 requirement IDs R-DOC/SK/PF/CF/AS/DR) | ✅ |
| P9 | Research | Gap analysis CSWA/CSWP vs FreeCAD 1.1.4 + FreeWorks → docs/GAP_ANALYSIS.md; backlog re-prioritised (equations + configurations moved to v1.3, drawings to v1.4) | ✅ |
| P10 | Research | Community projects survey → docs/COMMUNITY.md: keep built-in Assembly; Ribbon/PieMenu/Assembly4/A2plus/Vars not used; own SW-named material cards; BOM WB revisit in P20 | ✅ |
| P11 | Release | v1.1.0 released (stable branch): install/update/rollback, AI entry point, stability work, research docs | ✅ |
| P12 | Assembly | Materials + Mass Properties exactly like SW: 36-card SW-named library registered with FreeCAD's material system, Edit Material dialog (+ custom density), Mass Properties dialog (output CS, MMGS/CGS/MKS/IPS, decimals, hidden, selection, assemblies with per-component materials and sub-assembly placements); 16 new tests; released 1.1.1 | ✅ |
| P13 | Assembly | Mate PropertyManager (task panel): Mate Selections, Standard + Mechanical mates, distance/angle with flip, Mate alignment, Mates list, Add Mate; pop-up mate toolbar at the cursor; each mate its own undo step | ✅ |
| P14 | Assembly | Mate engine (mates.py): selection → FreeCAD reference, entity kinds, allowed + suggested mate, SW mate → joint mapping (coincident/tangent = Distance 0, concentric = Cylindrical, lock = Fixed with offset, hinge = Revolute), SW labels `Coincident1 (A,B)`; 11 tests. Editing existing mates moves to P16 | ✅ |
| P15 | Assembly | Advanced: Width (centred, computed from current geometry), Limit Distance / Limit Angle (limits on the Concentric/Slot/Hinge joint, offset to SW face distance/angle; enforced while dragging); Mechanical: Hinge, Gear (ratio from radii, flip = reverse), Rack Pinion (pitch diameter), Screw (distance/revolution). Symmetric, Cam, Slot, Universal Joint, Path: not possible with FreeCAD 1.1 joints (documented). 8 tests; released 1.1.3 | ✅ |
| P16 | Assembly | Assembly FeatureManager: instance names `Bracket<1>`, `(f)` for fixed components, Mates folder, FreeCAD joints renamed as SW mates, Edit Mate (context menu) in the Mate PM with in-place type/value changes; perf: command search model built once in idle time, CommandManager panels of all environments prebuilt, 2 s startup grace for the slow-callback rule. Not done: `(-)` under-defined prefix (solver gives no per-part DOF), own Insert Components PM (FreeCAD's is used) | ✅ |
| P17 | Assembly | Move / Rotate Component PM (By Delta XYZ, rotate About Entity / X / Y / Z) with Collision Detection (stop at first contact, bisection to 0.001 mm/deg, colliding component reported + selected), Free Drag hand-off; Replace Components with mated-entity re-attachment by geometry signature; Make Subassembly Rigid/Flexible (AssemblyLink.Rigid); v1.2.0 released. Exploded view stays FreeCAD's panel | ✅ |
| P18 | Drawing | 11 sheet formats (tools/make_templates.py: ISO A0–A4 + A4 portrait, ANSI A–E) with zone borders, projection symbol and a SW-organised title block (tolerances, NAME/SIGNATURE/DATE grid, MATERIAL, WEIGHT, TITLE, DWG NO., REV, SCALE, SHEET, size); TechDraw defaults; ISO = first angle, ANSI = third angle; MATERIAL/WEIGHT/DWG NO./TITLE filled from the part | ✅ |
| P19 | Drawing | Standard 3 View (Front/Top/Right laid out per projection at a standard scale; scripted TechDraw projection groups mis-place in 1.1.4 so three views are used) and Model View (part chooser + named orientations); projected/section/detail/break/crop stay FreeCAD's tools with SW names; released 1.4.0 | ✅ |
| P20 | Drawing | Annotations: model items, smart dimension, centre marks/lines, hole callout, notes with properties, balloons/auto balloon, BOM, revision table | ⬜ |
| P21 | Drawing | Display styles, tangent edges, line fonts, v1.3 release | ⬜ |
| P22 | Part | SOLIDWORKS terms inside FreeCAD's feature panels (pmskin.py, display-only relabel while a panel is open, 400 ms timer only then): Boss-Extrude/Cut-Extrude titles, Directions, End Condition (Blind, Through All, Up To Next, Up To Surface, Offset From Surface, Up To Body, Mid Plane), Depth, Draft angle, Reverse Direction; Revolve, Chamfer (Angle Distance / Distance Distance), Shell, Draft, patterns; green ✓ / red ✗ OK/Cancel; Options toggle. Not available in FreeCAD: From offset, Thin Feature, Selected Contours | ✅ |
| P23 | Part | Revolve, Fillet (constant/variable/face/full round), Chamfer types, Shell, Draft PMs | ⬜ |
| P24 | Part | Hole Wizard terms in FreeCAD's Hole panel (Hole Type, End Condition Blind/Through All, Fit Close/Normal/Loose, Hole diameter/depth, Counterbore/Countersink, Custom Sizing); released 1.3.0. Separate Type/Positions tabs: not done | ✅ |
| P25 | Part | Patterns (linear 2 directions, skip instances, circular) + Mirror + Reference geometry PMs | ⬜ |
| P26 | Part | Equations dialog (Tools > Equations): Global Variables (VarSet, stored GV_<name>), Equations with SOLIDWORKS syntax ("D1@Sketch1" = "A" * 2) translated to FreeCAD expressions and back, D<n> numbering for sketch and feature dimensions, Add rows, Delete, Rebuild, OK/Cancel as one undo step; 7 tests; released 1.2.1 | ✅ |
| P27 | Part | Configurations engine (configurations.py, table in a hidden VarSet, SW design-table headers D1@Sketch1 / $STATE@Feature / global vars / $DESCRIPTION), capture-on-switch = "this configuration" edits, shared unconfigured values; ConfigurationManager window (show/add/rename/delete, design table grid, add/remove column, CSV/XLSX import, CSV export); 8 tests; released 1.2.2. Docked ConfigurationManager tab: later (P30) | ✅ |
| P28 | Sketch | Smart Dimension behaviour + Modify box, Add Relations PM, Display/Delete relations, Fully Define Sketch | ⬜ |
| P29 | Sketch | Offset/Convert/Trim PM details, v1.4 release | ⬜ |
| P30 | GUI | FeatureManager tree SW structure (Annotations, Material, planes at root, Solid Bodies folder) + rollback bar | ⬜ |
| P31 | GUI | PropertyManager look (section headers, green ✓ / red ✗, pushpin) applied to all task panels | ⬜ |
| P32 | GUI | Confirmation corner in graphics area; selection context toolbar | ⬜ |
| P33 | GUI | Options dialog (System Options / Document Properties) mapping; document properties (units, drafting standard) | ⬜ |
| P34 | GUI | Polish pass + v1.5 release | ⬜ |

## Known issues / owner feedback
- GitHub: Claude sessions can push **branches** (`main`, `stable`) but not tags (403). Releases = push to `stable`.
- Installer scripts (get/install/uninstall.ps1) are structurally checked and reviewed but not yet run on a real Windows PC - owner to test the v1.0.1 one-liners.

## Session log
| Date (IST) | Part | Summary |
|---|---|---|
| 2026-11-07 | v1.0 | FreeWorks v1.0.0 built and tested headless on FreeCAD 1.1.4; installer + one-line installer + update check. |
| 2026-11-07 | P6 | Safe mode, crash sentinel, settings reset, large model mode; suite 57 checks. |
| 2026-11-07 | P18–P19 | Sheet formats, title block fill, Standard 3 View, Model View; **v1.4.0 released**. |
| 2026-11-07 | P22, P24 | SOLIDWORKS terms in feature panels (Extrude, Revolve, Hole Wizard ...); **v1.3.0 released**. |
| 2026-11-07 | P27 | Configurations + design tables; released 1.2.2. |
| 2026-11-07 | P26 | Equations dialog on VarSet + expressions; released 1.2.1. |
| 2026-11-07 | P17 | Collision detection, Replace Components, rigid/flexible; 106 checks; **v1.2.0 released**. |
| 2026-11-07 | P16 | Assembly naming (instances, (f), Mates), Edit Mate, perf fixes; 99 + 12 stress checks; released 1.1.4. |
| 2026-11-07 | P15 | Advanced + mechanical mates in the Mate PM; released 1.1.3. |
| 2026-11-07 | P13–P14 | Mate PropertyManager + mate engine on FreeCAD joints; pop-up mate toolbar; released 1.1.2. |
| 2026-11-07 | P12 | Materials + Mass Properties engine/dialogs; analytic inertia tests; released 1.1.1. |
| 2026-11-07 | P10–P11 | Community survey + reuse decisions; FreeWorks 1.1.0 released. |
| 2026-11-07 | P9 | Gap analysis from the FreeCAD 1.1.4 command list, joint types and material library; backlog re-ordered. |
| 2026-11-07 | P8 | CSWA/CSWP scope from official Dassault pages + sample exams; requirement IDs for gap analysis. |
| 2026-11-07 | P7 | Stress suite (69 checks with --stress); MSAA memory finding; scoped styles; released 1.0.5. |
| 2026-11-07 | P5 | Stability audit and fixes, watchdog, diagnostics; suite 44/44; released 1.0.4. |
| 2026-11-07 | P4 | Update checker, automated suite (33/33 pass), interactive tests made repo-relative; Mass Properties density fix; released 1.0.3. |
| 2026-11-07 | P3 | Rollback, What's New, add-on commit pins, dev/tests/pscheck.py (PowerShell structure check); released 1.0.2 to stable. |
| 2026-11-07 | P2 | One-line install/update/uninstall, installer v2, projects-folder guard, stable-branch releases (tags blocked for Claude sessions); released v1.0.1. |
| 2026-11-07 | P1 | Tracker, CLAUDE.md/AGENTS.md, UPDATE_PROTOCOL, DEV_NOTES rewrite, versions.json; new logo → vector mark, .ico, splash, Welcome dialog, README (tools/make_branding.py). |
