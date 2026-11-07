# FreeWorks build - resume notes
Target FreeCAD 1.1.4. Windows assets on GitHub release 1.1.4 (probe exact names again: FreeCAD_1.1.4-Windows-x86_64-py311*.7z / installer.exe).
Test rig: /home/claude/run_fc.sh <macro> [timeout]  env: FCHOME (profile), SHOT (png), PRE (python run after DELAY ms), POST ms.
  harness /tmp/shot.py ; fresh profile: rm -rf /home/claude/fwhome; mkdir -p .../Mod; ln -s /home/claude/FreeWorks/Mod/FreeWorks .../Mod/FreeWorks
  /tmp/model.py builds sample part (sketch+pad+pocket+fillet). FREEWORKS_NO_WELCOME=1 skips welcome; FREEWORKS_DEBUG_LOG=/tmp/fw.log
  Auto-mode blocks running 3rd-party add-on code here -> test only our code.
DONE modules (Mod/FreeWorks/freeworks): __init__, catalog, context, commands, sketchmode, widgets, naming, prefs, shell, shortcuts, gestures, contextmenu, startup; InitGui.py, package.xml; Resources/icons (155, tools/make_icons.py), Resources/theme/FreeWorks.yaml (theme tokens for FreeCAD.qss, installed to UserData/Gui/Stylesheets/parameters).
VERIFIED: shell renders (top bar+menus+CM tabs+heads-up+status), SW labels (Boss-Extrude1, Front/Top/Right Plane), icon override via UserData/icons works (tree icons).
FIXES PENDING: Tasks dock is in FreeCAD overlay (param User parameter:BaseApp/MainWindow/DockWindows/OverlayRight Widgets="Tasks," -> set "" early / installer seeds). Verify tabify with Model dock.
STATUS: v1.0 packaged -> /home/claude/FreeWorks.zip (sent). Next ideas: level-1 upgrades (own PropertyManager panels, rollback bar, mate panel).
