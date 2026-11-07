# FreeWorks project tracker

**Next part:** P2 – Installer v2 (versions.json driven, verified downloads, logs, preflight)

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
| v1.2 | Assemblies & mates (SOLIDWORKS workflows) | P12–P17 |
| v1.3 | Drawings | P18–P21 |
| v1.4 | Part PropertyManagers, sketching, equations, configurations, materials | P22–P29 |
| v1.5 | GUI/UX polish: FeatureManager, PropertyManager look, confirmation corner, context toolbar | P30–P34 |

## Parts
| # | Track | Part | Status |
|---|---|---|---|
| P1 | Docs/AI | Tracker, CLAUDE.md/AGENTS.md entry point, versions.json, UPDATE_PROTOCOL, new logo (icon, splash, branding, README) | ✅ |
| P2 | Install | Installer v2: read versions.json; SHA-256 verification (GitHub asset digest); resumable download (BITS fallback); install log; preflight (Win10/11 x64, PS 5.1, disk, missing D: → ask); clearer progress | ⏳ |
| P3 | Install | Updates v2: FreeCAD upgrades side-by-side with swap + rollback; add-on refs pinned; Windows "Apps & features" uninstall entry; `FreeWorks.exe --update/--rollback`; release-notes dialog | ⬜ |
| P4 | Dev/AI | `dev/check_updates.py` (latest FreeCAD/add-ons vs pins, report), `dev/fetch_freecad.sh`, `dev/run_tests.sh` automated suite (catalog command existence, startup, contexts, screenshots) | ⬜ |
| P5 | Stability | Crash/lag audit of all FreeWorks code; global guard for Qt slots; event-loop latency watchdog (logs stalls); startup time budget | ⬜ |
| P6 | Stability | Safe mode (`FreeWorks.exe --safe`, Shift at start), crash sentinel → auto safe start, "Reset FreeWorks settings"; large-model mode (lighter tessellation, manual rebuild) | ⬜ |
| P7 | Stability | Stress test suite (open/close docs, context switching ×200, gestures, sketches); memory/time report | ⬜ |
| P8 | Research | CSWA + CSWP exam scope (official topic lists, sample exams) → docs/CSWA_CSWP_SCOPE.md | ⬜ |
| P9 | Research | Gap analysis CSWA/CSWP vs FreeCAD 1.1 + FreeWorks → prioritized backlog (may reorder P12+) | ⬜ |
| P10 | Research | Community projects survey (assembly add-ons, TechDraw extensions, SW-like macros/UI projects, materials libraries, BOM tools) → docs/COMMUNITY.md, reuse decisions | ⬜ |
| P11 | Release | v1.1 release: version bump, changelog, zip, push, GitHub release | ⬜ |
| P12 | Assembly | Materials + Mass Properties exactly like SW (material library names, output coordinate system, units, report) – CSWA critical | ⬜ |
| P13 | Assembly | Mate PropertyManager UI (Mate Selections, Standard/Advanced/Mechanical, alignment, flip, pop-up mate toolbar) | ⬜ |
| P14 | Assembly | Standard mates → FreeCAD joints mapping + auto-suggest from selection; edit existing mates | ⬜ |
| P15 | Assembly | Advanced (limit distance/angle, width, symmetric) and mechanical (gear, rack pinion, screw, hinge, slot) mates | ⬜ |
| P16 | Assembly | Assembly FeatureManager: Mates folder, (f)/(-) prefixes, instance names `Part<1>`, Insert Components PM, Fix/Float, move/rotate with DOF | ⬜ |
| P17 | Assembly | Exploded view PM, collision detection, replace components, subassemblies, v1.2 release | ⬜ |
| P18 | Drawing | Sheet formats ANSI A–E / ISO A4–A0 with SW-style title blocks; sheet properties (scale, 1st/3rd angle) | ⬜ |
| P19 | Drawing | View workflows: Model View PM, Standard 3 View, projected by drag direction, section, detail, aux, break, crop | ⬜ |
| P20 | Drawing | Annotations: model items, smart dimension, centre marks/lines, hole callout, notes with properties, balloons/auto balloon, BOM, revision table | ⬜ |
| P21 | Drawing | Display styles, tangent edges, line fonts, v1.3 release | ⬜ |
| P22 | Part | Extrude PropertyManager (From, Direction 1/2, end conditions, draft, thin feature, selected contours) | ⬜ |
| P23 | Part | Revolve, Fillet (constant/variable/face/full round), Chamfer types, Shell, Draft PMs | ⬜ |
| P24 | Part | Hole Wizard PM (types, ANSI/ISO sizes, positions) | ⬜ |
| P25 | Part | Patterns (linear 2 directions, skip instances, circular) + Mirror + Reference geometry PMs | ⬜ |
| P26 | Part | Equations & global variables manager | ⬜ |
| P27 | Part | Configurations (ConfigurationManager) + design tables | ⬜ |
| P28 | Sketch | Smart Dimension behaviour + Modify box, Add Relations PM, Display/Delete relations, Fully Define Sketch | ⬜ |
| P29 | Sketch | Offset/Convert/Trim PM details, v1.4 release | ⬜ |
| P30 | GUI | FeatureManager tree SW structure (Annotations, Material, planes at root, Solid Bodies folder) + rollback bar | ⬜ |
| P31 | GUI | PropertyManager look (section headers, green ✓ / red ✗, pushpin) applied to all task panels | ⬜ |
| P32 | GUI | Confirmation corner in graphics area; selection context toolbar | ⬜ |
| P33 | GUI | Options dialog (System Options / Document Properties) mapping; document properties (units, drafting standard) | ⬜ |
| P34 | GUI | Polish pass + v1.5 release | ⬜ |

## Known issues / owner feedback
- GitHub: Claude sessions can push to `scp15156402/FreeWorks` (working since 2026-11-07 P1). If a push is refused, fall back to `FreeWorks.bundle`.
- v1.0 installer not yet confirmed on a real Windows PC.

## Session log
| Date (IST) | Part | Summary |
|---|---|---|
| 2026-11-07 | v1.0 | FreeWorks v1.0.0 built and tested headless on FreeCAD 1.1.4; installer + one-line installer + update check. |
| 2026-11-07 | P1 | Tracker, CLAUDE.md/AGENTS.md, UPDATE_PROTOCOL, DEV_NOTES rewrite, versions.json; new logo → vector mark, .ico, splash, Welcome dialog, README (tools/make_branding.py). |
