# Changelog

## v1.1.0 - unreleased
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
