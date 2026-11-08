# Course transcript triage and the research schedule (2026-11-08)

All 183 videos of the owner's course were triaged from their timestamped transcripts (182 have
captions; 05.05 *Section view* has none and is watched frames-only). For each video the playlist
file (`01.md` … `21.md`) gives a verdict, the time ranges to watch, and a list of **what to capture
at which timestamp** (panels, options, dialogs, mouse/keyboard behaviour). Watch steps seek straight
to those timestamps instead of scanning blind.

## Verdicts

| Verdict | Meaning | Videos | Minutes to watch |
|---|---|---|---|
| FULL | UI is on screen throughout; watch all of it | 168 | 1,217 |
| PARTIAL | Only the listed ranges show something new (rest is talk or exact repetition) | 11 | 53 |
| SKIP | Nothing on screen worth capturing (course admin, hardware talk, theory, outro) | 4 | 0 |
| **Course total** | | **183** | **1,270 of 1,305** |

SKIP: 01.01 course intro · 01.08 3D mouse · 14.01 top-down vs bottom-up theory · 21.08 final notes.
PARTIAL: 01.10, 01.11, 03.08, 05.06, 08.05, 11.06, 12.01, 19.03, 19.06, 20.06, 21.07.

Facts from the transcripts: the course is recorded in **SOLIDWORKS 2020 Professional SP3** (01.02);
19.06 alone shows SOLIDWORKS 2022 paths (Save Sheet Format moved under Publish).

## What the course does not cover

`COVERAGE.md` maps ~150 catalogue topics to the videos and timestamps where they come up and marks
the thin spots. The gaps that matter for the 2.x plan are filled with short supplementary videos
(`SUPPLEMENTARY.md`, 31 videos, ≈ 109 min, transcripts checked): keyboard and view keys, View
Orientation dialog, breadcrumbs, selection filters, box/lasso, Select Other / Partial Loop / Chain,
hide/isolate, FeatureManager tips, rollback/freeze bar, System Options, Display/Delete Relations,
SketchXpert, Fully Define, Check Sketch, Move Component with triad and collision detection.
Not in the course and **not in 2.x scope**: sheet metal, weldments, mold tools, advanced surfacing,
motion studies, simulation, rendering (v3 or later, owner decides).

## Research schedule (replaces R1–R11)

Ordered like the build stages (simple → complex). Each step is one fresh conversation started with
"continue". Method: `dev/research/VIDEO_METHOD.md`. Footage minutes are what will actually be watched.

| Step | Course videos | Supplementary | Footage | Feeds stage |
|---|---|---|---|---|
| **W1** UI, views, selection, tree, options | 01 (9 of 11) | S-A (23 videos) | ≈ 148 min | A, G |
| **W2** Sketch environment | 02 all, 11.07–11.09 | S-E (5) | ≈ 98 min | E |
| **W3** Sketch tools and curves | 03, 08 | — | ≈ 127 min | E, H |
| **W4** Basic features, reference geometry, appearance, mass | 04, 05 | — | ≈ 119 min | C, D |
| **W5** Patterns, bodies, sweep | 06, 07 | — | ≈ 118 min | C, H |
| **W6** Loft, boundary, solid features, draft, holes, threads | 09, 10, 11.01–11.06 | — | ≈ 143 min | C, D, H |
| **W7** Blocks, equations, configurations | 12, 13 | — | ≈ 90 min | I |
| **W8** Assemblies I (mates, analysis, Pack and Go) | 14 (9 of 10), 15 | S-I (3) | ≈ 145 min | I |
| **W9** Assemblies II + project modelling | 16, 21.01–21.05 | — | ≈ 124 min | I, F |
| **W10** Drawings I (views, dimensions, annotations) | 17, 18 | — | ≈ 151 min | J |
| **W11** Drawings II (layers, templates, BOM, print) + project drawing | 19, 20, 21.06–21.07 | — | ≈ 116 min | J |
| **H** Help fill (no video) | every PM seen: complete option lists from 2019–2021 help; Quick Snaps; Options pages; evaluate tools not shown | — | — | all |
| **C** Consolidate + owner sign-off | update catalogue, spec IDs, V2_PLAN parts from W/H findings; owner reviews | — | — | — |

Total footage ≈ 1,380 min (course 1,270 + supplementary 109). **No development until C is signed off.**

## Transcripts

Not committed (third-party text). They are cached in the owner's built-in browser
(`localStorage.fwTr` on youtube.com) and can be re-fetched for any video in seconds with
`fwFetchTr(id)` (`dev/research/VIDEO_METHOD.md` §3); the 183-video fetch takes under a minute.
