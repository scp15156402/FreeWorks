# Test harness (Linux, headless)

Used during development to run FreeWorks inside the official FreeCAD 1.1.4 AppImage under Xvfb.

- `run_fc.sh <macro.py> [timeout]` - start FreeCAD with profile `$FCHOME`; `shot.py` runs `$PRE` after `$DELAY` ms and saves a screenshot to `$SHOT`.
- `model.py` - builds a sample part (sketch, Boss-Extrude, Cut-Extrude, Fillet).
- `run_inter.sh` + `drive.py` + `pre_inter.py` - real keyboard/mouse input via XTEST (shortcuts, gestures, context menu, search).
- `pre_env.py` - assembly, drawing and Welcome dialog screenshots.

Paths inside are from the build machine; adjust before use.
