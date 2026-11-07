# Changelog

## v1.0.1 - 2026-11-07
- **One line to install or update** (`irm …/get.ps1 | iex`) on any Windows 10/11 PC: picks D:\FreeWorks
  or %LOCALAPPDATA%\Programs\FreeWorks, updates in place when already installed, waits for FreeWorks to be
  closed, starts FreeWorks after a fresh install. Newest version = highest `vX.Y.Z` git tag.
- **One line to uninstall** (`irm …/uninstall.ps1 | iex`) with a single confirmation; also in Settings → Apps.
- Projects and macros default to Documents\FreeWorks and are never touched by updates or uninstall;
  FreeWorks prevents File > Save from defaulting into the program or temp folder.
- Installer v2: versions.json-driven, SHA-256 check when GitHub publishes a digest, resumable downloads
  (curl), install.log, preflight checks, side-by-side FreeCAD upgrade, Windows "Apps" registration.
- In-app update check uses version tags.
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
