# "Let's get it up to date" – update protocol

Run this when the owner says **"Let's get it up to date"** (or similar). Goal: FreeWorks
works on the newest stable FreeCAD, uses current add-ons, and reflects the newest
SOLIDWORKS UI/workflows. Work in ≤ 30-minute parts; record progress in `dev/TRACKER.md`
(add a part "Uxx – Update to FreeCAD <version>" if the work is larger than one part).

## 1. What is new? (≈5 min)
- `python3 dev/check_updates.py` → prints pinned vs latest:
  FreeCAD stable release (GitHub `FreeCAD/FreeCAD` releases, excluding pre-releases),
  Windows asset names (checked to exist) + SHA-256 digests, add-on branch heads vs pinned commits.
- Web research (search, read the sources, cite them in the commit/notes):
  - FreeCAD release notes for every version since the pinned one
    (`wiki.freecad.org/Release_notes_<x.y>`, `blog.freecad.org`): UI changes (themes,
    overlay docks, menus), renamed/removed commands, Sketcher, PartDesign, Assembly,
    TechDraw, Measure, Materials.
  - Latest SOLIDWORKS "What's New" (version year): UI, CommandManager, PropertyManager,
    mates, drawings, sketching. Record relevant changes in `docs/SOLIDWORKS_REFERENCE.md`.
  - CSWA/CSWP exam updates (`docs/CSWA_CSWP_SCOPE.md`).

## 2. Test FreeWorks against the new FreeCAD (≈10 min)
- `dev/fetch_freecad.sh <new version>` downloads and extracts the Linux AppImage
  (and points `dev/.freecad/current` at it).
- `dev/run_tests.sh`: must end with 0 failures. Also run `dev/tests/interactive/run_inter.sh`
  for gestures/shortcuts and look at the screenshots in `dev/tests/out/`.
- Add-on updates: `python3 dev/check_updates.py --apply` pins new commits; read the add-on
  changelogs / commits for renamed commands (catalog uses their command names).
- Fix what broke: `catalog.py` command names, `prefs.py` parameter names
  (`strings libFreeCADGui.so | grep <Name>` helps), `shell.py` dock/overlay handling,
  theme tokens (`Stylesheets/parameters/*.yaml` of the new FreeCAD), icon overrides.
- Record any new FreeCAD internals in `dev/DEV_NOTES.md`.

## 3. Adopt new capabilities (time-boxed)
- New FreeCAD features that match a SOLIDWORKS command → add to `catalog.py`
  (name, icon, tab, aliases), remove "approximate" flags where parity improved.
- New SOLIDWORKS UI behaviour → add parts to `dev/TRACKER.md` backlog.

## 4. Pin and release (≈5 min)
- `python3 dev/check_updates.py --apply` updates `versions.json` (FreeCAD version, asset names,
  SHA-256, add-on commits); review the diff.
- Bump version in `versions.json`, `Mod/FreeWorks/package.xml`, `freeworks/__init__.py`;
  add a `CHANGELOG.md` entry.
- `dev/run_tests.sh` green → commit → `git push origin main` → `git push origin main:stable`.
- Installed copies pick it up via the one-line command, the in-app daily check or `Update.cmd`.

## Rollback
If a new FreeCAD breaks FreeWorks and cannot be fixed quickly, keep the old pin in
`versions.json`, note the blocker in the tracker, and release only FreeWorks fixes.
