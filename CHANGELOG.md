# Changelog

## v1.1.4 - 2026-11-07
Assembly FeatureManager.
- Components are named like SOLIDWORKS instances: `Bracket<1>`, `Bracket<2>`; a fixed component
  shows `(f) Bracket<1>`, and loses the prefix when you float it.
- FreeCAD's "Joints" folder is the **Mates** folder; joints made with FreeCAD's own joint tools get
  SOLIDWORKS mate names too (`Hinge1 (Shaft<1>,Base<1>)`).
- **Edit Mate** (right-click a mate): opens the Mate PropertyManager on that mate; change its type,
  distance/angle or alignment in place, or cancel to leave it as it was.
- Smoother: the command search list is built once in idle time, and the CommandManager tabs of
  parts, assemblies and drawings are prepared in the background after start-up.

## v1.1.3 - 2026-11-07
More mates in the Mate PropertyManager.
- **Advanced Mates:** Width (pick two groove faces, then two tab faces - the tab is centred),
  Limit Distance and Limit Angle (applied to the Concentric / Hinge mate between the same two
  components; FreeCAD enforces limits while you drag).
- **Mechanical Mates:** Hinge, Gear (ratio taken from the two diameters, flip reverses the
  direction), Rack Pinion (pinion pitch diameter) and Screw (distance per revolution), all inside
  the Mate PropertyManager.
- Selected mate type is highlighted; new icons.
- Not available with FreeCAD 1.1 joints: Symmetric, Profile Center, Path, Linear Coupler, Cam, Slot,
  Universal Joint. The Width mate is computed from the current face positions, so re-create it
  if the groove or tab width changes.

## v1.1.2 - 2026-11-07
SOLIDWORKS-style mating.
- **Mate** (Assembly tab) now opens a **Mate PropertyManager**: pick two faces, edges or vertices
  on two components and FreeWorks applies the right mate straight away - two planar faces
  Coincident, two cylinders Concentric, a cylinder and a plane Tangent - with a **pop-up mate
  toolbar** at the cursor to switch type, enter a distance or angle, flip the alignment, accept or
  undo.
- Standard mates: Coincident, Parallel, Perpendicular, Tangent, Concentric, Lock, Distance, Angle;
  mechanical: Hinge, plus Gear / Rack Pinion / Screw through FreeCAD's joint panel.
- Mate alignment (Aligned / Anti-Aligned), Flip dimension, a Mates list, and each mate is its own
  undo step. Mates are named like SOLIDWORKS: `Coincident1 (Plate,Block)`.
- New original icons for every mate type.

## v1.1.1 - 2026-11-07
CSWA essentials: materials and Mass Properties.
- **Edit Material** (right-click a body, or Tools/Evaluate): a library with SOLIDWORKS material
  names and densities - AISI 1020, Alloy Steel, Plain Carbon Steel, AISI 304, 6061 Alloy, 1060 Alloy,
  Copper, Brass, ABS and more (36 cards) - plus FreeCAD's own materials and a **custom density**
  for "Density = 0.0079 g/mm^3" style questions. The body takes the material's colour.
- **Mass Properties** dialog rebuilt: report relative to any coordinate system, MMGS / CGS / MKS /
  IPS, decimal places, include hidden bodies/components, selected items, principal axes, moments at
  the centre of mass and at the output coordinate system (positive tensor notation), Copy to
  Clipboard.
- Assemblies: every component counts once with its own material, sub-assembly placements included,
  hidden components optional. Mixed materials work.

## v1.1.0 - 2026-11-07
Milestone release: everything from 1.0.1 to 1.0.5 plus the research that drives v1.2+.
- One-line install, update, rollback and uninstall for Windows (see README).
- "Let's get it up to date" protocol and tools for Claude / developers (`CLAUDE.md`, `dev/`).
- Stability: guarded UI code, freeze watchdog, safe mode, crash recovery, stress-tested.
- Research documents: `docs/CSWA_CSWP_SCOPE.md` (what a CSWA/CSWP user needs),
  `docs/GAP_ANALYSIS.md` (what FreeCAD 1.1.4 does and does not do), `docs/COMMUNITY.md`
  (which community add-ons FreeWorks uses). Roadmap: v1.2 materials, Mass Properties and
  SOLIDWORKS-style mates; v1.3 equations and configurations; v1.4 drawings.

## v1.0.5 - 2026-11-07
Safe mode, recovery and long-session smoothness.
- **Safe mode**: start FreeWorks with Shift held, the "FreeWorks (Safe Mode)" Start-menu shortcut or
  `FreeWorks.exe --safe` to get plain FreeCAD menus and toolbars with your files untouched.
- If FreeWorks did not finish starting last time, it starts in safe mode automatically and explains
  what happened, with one click to reset FreeWorks settings.
- **Tools → Reset FreeWorks Settings** restores FreeWorks' defaults (projects are not touched).
- **View → Large Model Mode** (SOLIDWORKS "Large Design Review" style): coarser display tessellation,
  no anti-aliasing, no view animations. Suggested automatically for documents with 600+ objects.
- Lower memory use in long sessions: line smoothing instead of 4x multisampling by default (each
  sketch edit with multisampling kept ~8 MB). Multisampling is an option in FreeWorks Options.
- FreeWorks styles only its own panels, so FreeCAD dialogs open faster; layout self-healing and the
  status bar do less work.
- New stress test (`dev/run_tests.sh --stress`): 69 checks incl. leak, memory plateau and freeze tests.

## v1.0.4 - 2026-11-07
Stability and smoothness.
- Every FreeWorks UI class and callback is guarded: an error inside FreeWorks is logged, never passed
  on to FreeCAD.
- Removed two background costs: the sketch helper no longer listens to every change in every document
  (only while the Centerline tool runs), and FreeWorks no longer filters every main-window event.
- Right-click is replayed after FreeWorks' event handling returns, so closing a document from the
  context menu is safe.
- FreeCAD's Ctrl+Arrow overlay shortcuts are disabled; FeatureManager/PropertyManager layout and hidden
  toolbars heal themselves within 2 seconds if something changes them.
- CommandManager tabs are built in idle time after startup, so the first tab switch never stutters.
- New UI-freeze watchdog and slow-callback detector; **Help → FreeWorks Diagnostics** shows freezes,
  slow callbacks and caught errors, ready to copy into a bug report. Log: UserData\FreeWorks.log.
- Test suite: 44 checks, including deliberate errors/freezes and "no slow callbacks".

## v1.0.3 - 2026-11-07
- **Fix: Mass Properties** used FreeCAD's placeholder "Default" material (1 kg/m³) and reported masses
  1000× too low. Unassigned material now means 1000 kg/m³, exactly like SOLIDWORKS.
- Developer/AI tooling: `dev/run_tests.sh` automated test suite (33 checks incl. performance budgets),
  `dev/check_updates.py` (upstream FreeCAD/add-on versions, `--apply`), `dev/fetch_freecad.sh`.
- The sketch Text tool appears automatically once FreeCAD provides it (1.2+).

## v1.0.2 - 2026-11-07
- **Rollback:** every update keeps the previous FreeWorks, add-ons and (if it changed) FreeCAD.
  Help → *Roll Back to Previous Version*, or
  `& ([scriptblock]::Create((irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1))) -Rollback`.
  Projects and settings are kept; running the normal one-liner updates again. The update check
  does not keep offering a version you rolled back from.
- **What's New** dialog after each update (also in the Help menu); the update offer shows the release notes.
- Add-ons are pinned to tested commits in versions.json (identical installs everywhere); if an add-on
  download fails during an update, the installed copy is kept.

## v1.0.1 - 2026-11-07
- **One line to install or update** (`irm …/get.ps1 | iex`) on any Windows 10/11 PC: picks D:\FreeWorks
  or %LOCALAPPDATA%\Programs\FreeWorks, updates in place when already installed, waits for FreeWorks to be
  closed, starts FreeWorks after a fresh install. Released version = the `stable` branch.
- **One line to uninstall** (`irm …/uninstall.ps1 | iex`) with a single confirmation; also in Settings → Apps.
- Projects and macros default to Documents\FreeWorks and are never touched by updates or uninstall;
  FreeWorks prevents File > Save from defaulting into the program or temp folder.
- Installer v2: versions.json-driven, SHA-256 check when GitHub publishes a digest, resumable downloads
  (curl), install.log, preflight checks, side-by-side FreeCAD upgrade, Windows "Apps" registration.
- In-app update check reads the version on the `stable` branch.
- New FreeWorks logo: app icon (vector, sharp at 16 px), Windows .ico, splash screen, Welcome dialog, README.
- Project tracker (dev/TRACKER.md), AI/developer entry point (CLAUDE.md, AGENTS.md) with "continue" and
  "Let's get it up to date" protocols, version manifest (versions.json), FreeCAD internals notes.

## v1.0.0 - 2026-11-07
First release, for FreeCAD 1.1.4.
- SolidWorks-style shell: top bar with menus, quick access, command search; context-sensitive CommandManager (Part, Sketch, Surfaces, Sheet Metal, Evaluate, Assembly, Mates, Drawing tabs); FeatureManager / PropertyManager tabs; heads-up View toolbar; status bar with sketch state and units.
- ~240 commands with SolidWorks names; SolidWorks feature naming in the tree; 155 original icons.
- Context-aware SolidWorks keyboard shortcuts, mouse gestures, reordered context menus, view selector, shortcut bar, magnifier.
- Mass Properties, Section Properties, Interference Detection, Bounding Box reports.
- SolidWorks look: theme tokens, sketch colours, selection colours, lighting, anti-aliasing, tessellation.
- Windows installer to D:\FreeWorks with SheetMetal, Fasteners and Curves add-ons and FreeWorks branding.
- One-line install from GitHub (get.ps1), daily update check with one-click update, Update.cmd fetches the latest release.
