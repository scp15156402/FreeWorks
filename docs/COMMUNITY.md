# Community projects survey — what FreeWorks reuses

Part P10, 2026-11-07. Rule from the owner: use community work where it is good, write our own
code where it is weak or missing. Licence check: FreeWorks is LGPL-2.1+; we only *bundle* code
with a compatible licence, and we prefer installing add-ons side by side (pinned in
`versions.json`) over copying their code.

## Already part of FreeWorks
| Project | Licence | Used for | Notes |
|---|---|---|---|
| FreeCAD built-in **Assembly** workbench (Ondsel solver) | LGPL | Mates (joints), exploded views, BOM, simulation | Official and maintained; the only assembly engine FreeWorks targets |
| **SheetMetal** (shaise) | LGPL | Sheet Metal tab | pinned commit |
| **Fasteners** (shaise) | LGPL | Toolbox / Hardware equivalent | pinned commit |
| **Curves** (tomate44) | LGPL | Zebra, draft analysis, curvature, surfacing helpers | pinned commit |
| **Render** (FreeCAD) | LGPL | optional PhotoView-like rendering | `-WithRender` |

## Reviewed, decision per project
| Project | What it offers | Decision | Why |
|---|---|---|---|
| **FreeCAD Ribbon** (Paul Ebbers) | Ribbon UI replacing toolbars, JSON layout | ✗ not bundled; ideas only | GPL-3.0; it replaces the same toolbars FreeWorks' CommandManager owns, so both together would fight. Our CommandManager is already SW-structured |
| **PieMenu** (triplus → Grubuntu "Improved" → imadnyc fork) | Key-invoked pie menus, per-workbench pies, gesture-to-command | ✗ not bundled; ideas only | FreeWorks has SOLIDWORKS-style RMB-drag gestures (S-key Shortcut Bar too). Idea taken for later: per-context gesture sets, tap-vs-hold |
| **Assembly4**, **A2plus**, **Assembly3** | Alternative assembly workbenches | ✗ not used | Incompatible with each other and with the built-in Assembly; built-in has BOM, exploded views, simulation and is where FreeCAD development goes |
| **BillOfMaterials WB** (Paul Ebbers) | BOM types (total, summary, parts-only, first level) for every assembly type | ⏸ revisit in P20 | LGPL; built-in `Assembly_CreateBom` is enough for v1.2. If drawing BOMs need "parts only / top level" like SW, install side by side |
| **Supplemental-Materials** (FreeCAD org) | Extra .FCMat material cards | ✔ source of truth for extra cards; FreeWorks ships its own **SW-named** cards in P12 | CC-BY-SA / LGPL. CSWA needs exact SW names and densities (AISI 1020 7900, 6061 Alloy 2700, 1060 Alloy 2700, Copper 8900, Alloy Steel 7700, Brass 8500 kg/m³ …) which no library provides under those names |
| **Vars** (mnesarco) | Variables as document objects, manager GUI | ✗ (alpha) — use built-in **VarSet** | P26 Equations dialog builds on `Std_VarSet` + expressions, which are core and stable |
| **DynamicData** | Edit VarSet properties | ✗ | covered by our Equations dialog later |
| **Macro TemplateHelper** (FBXL5) | Generates ISO/ANSI/Arch templates with title block + BOM area | ◐ reference only | ANSI formats "need tweaking" per its own page; P18 generates SW-style SVG sheet formats using TechDraw's 1.0 autofill fields |
| **TechDrawTemp** (tjarkdoering) | ISO 7200 title blocks | ◐ reference | MIT; useful field list for ISO formats |
| **KicadStepUp** collision tool | Pairwise collision check | ✗ | ECAD-oriented; FreeWorks already has Interference Detection; P17 adds drag-time collision detection itself (OCC distance/boolean on the moving component only) |
| **freecad.gears** (looooo) | Involute/cycloid/bevel/worm gears | ⏸ optional Toolbox entry later | LGPL; nice for gear mates, not CSWA/CSWP scope |
| **Design456** (direct modeling) | Move/push-pull faces | ✗ | early alpha (0.00.1) |
| **SearchBar**, **SaveAndRestore**, **OpenTheme** | command search, settings backup, themes | ✗ | FreeWorks has its own search (W/I/H), Reset Settings and theme |

## Consequences for the backlog
- **P12** ships `Resources/Materials/FreeWorks/*.FCMat` (SW names + densities) and registers the
  folder as a FreeCAD material library — no add-on needed.
- **P13–P17** build on the built-in Assembly only; collision detection is FreeWorks code.
- **P18** writes FreeWorks sheet formats; TemplateHelper/TechDrawTemp only as references.
- **P26** uses VarSet; **P27** uses the spreadsheet configuration table (core).
- Re-check this list during every "Let's get it up to date" run (`dev/UPDATE_PROTOCOL.md`).

## Sources
- [FreeCAD add-on catalogue](https://www.freecad.org/addons.php)
- [FreeCAD Ribbon (APEbbers, via forks)](https://github.com/albertorm95/FreeCAD-Ribbon)
- [PieMenu fork (imadnyc)](https://github.com/imadnyc/PieMenu) · [PieMenu (triplus)](https://github.com/triplus/PieMenu/)
- [External workbenches (FreeCAD wiki)](https://wiki.freecad.org/External_workbench)
- [BillOfMaterials WB](https://zff.dev/apebbers/BillOfMaterials-WB)
- [Supplemental-Materials](https://github.com/FreeCAD/Supplemental-Materials)
- [Vars add-on](https://github.com/mnesarco/Vars/wiki/) · [Std VarSet](https://wiki.freecad.org/Std_VarSet/en)
- [TechDraw templates](https://wiki.freecad.org/TechDraw_Templates) · [Macro TemplateHelper](https://wiki.freecad.org/Macro_TemplateHelper)
- [TechDrawTemp](https://github.com/tjarkdoering/techdrawtemp)
