# "Let's get it up to date" – update protocol

Run this when the owner says **"Let's get it up to date"** (or similar). Goal: FreeWorks
works on the newest stable FreeCAD, uses current add-ons, and reflects the newest
SOLIDWORKS UI/workflows. Work in ≤ 30-minute parts; record progress in `dev/TRACKER.md`
(add a part "Uxx – Update to FreeCAD <version>" if the work is larger than one part).

## 1. What is new? (≈5 min)
- `python3 dev/check_updates.py` → prints pinned vs latest:
  FreeCAD stable release (GitHub `FreeCAD/FreeCAD` releases, excluding pre-releases),
  Windows asset names + SHA-256 digests, add-on repos (latest commit / tags).
  *(Script is added in P4. Until then: `git ls-remote --tags https://github.com/FreeCAD/FreeCAD.git`
  and check the release page.)*
- Web research (search, read the sources, cite them in the commit/notes):
  - FreeCAD release notes for every version since the pinned one
    (`wiki.freecad.org/Release_notes_<x.y>`, `blog.freecad.org`): UI changes (themes,
    overlay docks, menus), renamed/removed commands, Sketcher, PartDesign, Assembly,
    TechDraw, Measure, Materials.
  - Latest SOLIDWORKS "What's New" (version year): UI, CommandManager, PropertyManager,
    mates, drawings, sketching. Record relevant changes in `docs/SOLIDWORKS_REFERENCE.md`.
  - CSWA/CSWP exam updates (`docs/CSWA_CSWP_SCOPE.md`).

## 2. Test FreeWorks against the new FreeCAD (≈10 min)
- `dev/fetch_freecad.sh <version>` (P4) downloads and extracts the Linux AppImage.
- `dev/run_tests.sh` (P4): startup without errors, every catalog command resolves,
  contexts (part/sketch/assembly/drawing), docks/overlay, shortcuts, gestures, screenshots.
- Fix what broke: `catalog.py` command names, `prefs.py` parameter names
  (`strings libFreeCADGui.so | grep <Name>` helps), `shell.py` dock/overlay handling,
  theme tokens (`Stylesheets/parameters/*.yaml` of the new FreeCAD), icon overrides.
- Record any new FreeCAD internals in `dev/DEV_NOTES.md`.

## 3. Adopt new capabilities (time-boxed)
- New FreeCAD features that match a SOLIDWORKS command → add to `catalog.py`
  (name, icon, tab, aliases), remove "approximate" flags where parity improved.
- New SOLIDWORKS UI behaviour → add parts to `dev/TRACKER.md` backlog.

## 4. Pin and release (≈5 min)
- Update `versions.json` (FreeCAD version, asset names, SHA-256, add-on refs).
- Bump version in `versions.json`, `Mod/FreeWorks/package.xml`, `freeworks/__init__.py`;
  add a `CHANGELOG.md` entry.
- `dev/make_release.sh` → `dist/FreeWorks.zip`; commit, tag, push; GitHub release with the zip.
- Installed copies pick the release up through the in-app update check / `Update.cmd`.

## Rollback
If a new FreeCAD breaks FreeWorks and cannot be fixed quickly, keep the old pin in
`versions.json`, note the blocker in the tracker, and release only FreeWorks fixes.
