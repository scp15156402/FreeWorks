# FreeWorks tests (Linux, headless)

## Automated suite – run after every change
```
dev/run_tests.sh
```
- Static checks: PowerShell structure (`pscheck.py`), Python syntax, version consistency
  (`package.xml` = `__init__.py` = `versions.json`).
- GUI suite (`suite.py`) inside the FreeCAD pinned in `versions.json` (downloaded by
  `dev/fetch_freecad.sh` on first run into `dev/.freecad/`), under Xvfb, fresh profile:
  startup + time budget, catalog commands/icons/references, shortcuts, hidden toolbars,
  PropertyManager docking, SOLIDWORKS naming, model build, Mass Properties numbers,
  sketch/assembly/drawing contexts and CommandManager tabs, **performance budgets**
  (controller tick, CommandManager refresh, context detection), no logged errors.
- Output: `dev/tests/out/report.md`, `results.json`, screenshots. Exit code 0 = all passed.
- Another FreeCAD: `FREECAD_APPRUN=/path/to/AppRun dev/run_tests.sh`, or
  `dev/fetch_freecad.sh 1.2.0 && dev/run_tests.sh` to test an upgrade.

Requirements: python3, curl, xvfb-run.

## Interactive tests (real keyboard/mouse) – `interactive/`
- `run_fc.sh <macro> [timeout]` – start FreeCAD with profile `$FCHOME`; `shot.py` runs `$PRE`
  after `$DELAY` ms and saves a screenshot to `$SHOT`.
- `run_inter.sh` + `drive.py` + `pre_inter.py` – XTEST input on Xvfb :77 (needs `python-xlib`):
  shortcuts, gestures, context menu, search; screenshots `/tmp/i_*.png`, log `/tmp/inter.log`.
- `pre_env.py` – assembly, drawing and Welcome dialog screenshots.
- `model.py` – sample part (sketch, Boss-Extrude, Cut-Extrude, Fillet).
Create the profile first: `mkdir -p $FCHOME/Mod && cp -r Mod/FreeWorks $FCHOME/Mod/`.

## Windows-only parts
`get.ps1`, `install.ps1`, `uninstall.ps1` cannot run here; they get the structure check and
code review. Ask the owner to run the one-liners and report `install.log`.
