<p align="center"><img src="docs/assets/logo.png" alt="FreeWorks - open-source CAD software" width="560"></p>

# FreeWorks

**A SolidWorks-style user experience on top of FreeCAD 1.1.4.** Same parametric FreeCAD engine underneath, with a SolidWorks-like interface on top: the CommandManager, FeatureManager, PropertyManager, SolidWorks names, icons, keyboard shortcuts, mouse gestures and view tools.

## Install, update, uninstall (Windows 10/11) - one line each

Open **PowerShell** (Start menu → type *PowerShell*) and paste:

| | Command |
|---|---|
| **Install or update** | `irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1 \| iex` |
| **Uninstall** | `irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/uninstall.ps1 \| iex` |

**Install or update**
- The same line does both. On a new PC it installs FreeWorks and starts it. If FreeWorks is already there, it updates it in place.
- Your **projects** live in `Documents\FreeWorks` (the default save folder), outside the program folder. Updates and uninstall never touch them.
- Your **settings** are kept across updates.
- If FreeWorks is open, the update waits until you have saved and closed it.

**Where it installs**
- `D:\FreeWorks` if the PC has a D: drive with room, otherwise `%LOCALAPPDATA%\Programs\FreeWorks`.
- To choose the folder yourself, run `$env:FREEWORKS_DIR = "E:\FreeWorks"` first.
- No administrator rights are needed, and any other FreeCAD on the PC is left alone.

**Uninstall** asks one question (`y`) and removes the program, its settings and its shortcuts. It is also listed in **Settings → Apps → FreeWorks**. Your projects are kept.

**Roll back** to the version you had before the last update with Help → *Roll Back to Previous Version*. Your projects and settings are kept.

**Updating from inside FreeWorks**
- FreeWorks checks GitHub once a day and offers **Update now**.
- You can also check manually under Help → *Check for FreeWorks Updates*.

**What gets installed**
- The official portable FreeCAD (version pinned in `versions.json`), with its checksum verified when one is published.
- Downloads resume if interrupted, and an install log is written to `install.log`.
- Three community add-ons, which FreeWorks integrates into its tabs:

| Add-on | Gives you |
|---|---|
| SheetMetal (shaise) | the **Sheet Metal** tab |
| Fasteners (shaise) | **Toolbox**: bolts, screws, nuts, washers |
| Curves (tomate44) | **Zebra Stripes**, **Curvature**, **Draft Analysis**, advanced surfaces |

Offline / manual: download the repository ZIP, extract it, and double-click `Install.cmd`.

```
<install folder>\         (D:\FreeWorks or %LOCALAPPDATA%\Programs\FreeWorks)
  FreeWorks.exe     launcher (keeps all settings inside UserData)
  FreeCAD\          official FreeCAD 1.1.4, portable, with FreeWorks branding
  UserData\         settings, add-ons (Mod\), icon theme
Documents\FreeWorks\   your projects and macros (never touched by updates/uninstall)
```

## What you get

**Window layout**
- **Top bar**
  - FreeWorks button, File / Edit / View / Insert / Tools / Window / Help menus laid out like SolidWorks.
  - Quick-access buttons (New, Open, Save, Print, Undo, Redo, Select, Rebuild, Options).
  - Document title, and the command **search box** (`W`).
- **CommandManager**: tabbed and context-sensitive.
  - Part: *Features, Sketch, Surfaces, Sheet Metal, Evaluate*.
  - Assembly: *Assembly, Mates, Sketch, Evaluate*.
  - Drawing: *View Layout, Annotation, Sheet Format*.
  - Large buttons with flyouts and stacked small buttons, as in SolidWorks.
  - Entering a sketch switches to the Sketch tab automatically and returns afterwards.
- **FeatureManager / PropertyManager** tabs on the left. The PropertyManager opens by itself when a feature dialog is active.
- **Heads-up View toolbar** over the graphics area: Zoom to Fit, Zoom to Area, Previous View, Section View, View Orientation, Display Style, Hide/Show Items, Edit Appearance and Apply Scene.
- **Status bar**: *Editing Part / Sketch / Assembly / Drawing*, the sketch state (*Under Defined (n DOF)*, *Fully Defined*, *Over Defined*), and the unit system (MMGS / MKS / IPS).

**Terminology and icons**
- About 240 commands carry SolidWorks names: Extruded Boss/Base, Extruded Cut, Hole Wizard, Revolved Cut, Convert Entities, Offset Entities, Trim Entities, Smart Dimension, Linear Pattern, Mirror, Shell, Mass Properties, Interference Detection, Mate and so on.
- The names apply in menus, tooltips, search and FreeCAD's Customize dialog.
- The FeatureManager names features like SolidWorks: *Sketch1, Boss-Extrude1, Cut-Extrude1, Fillet1, LPattern1, CirPattern1, Front Plane / Top Plane / Right Plane*.
- An **original icon set** (about 155 icons) uses SolidWorks' visual language:
  - amber solids for adding material, grey for cutting
  - blue sketch geometry, green arrows, tan reference planes
- The icons are used in the CommandManager, menus and the feature tree. SolidWorks' own icons are copyrighted, so none are copied.

**Command search (`W`)** recognises SolidWorks names and common aliases. Typing *pad*, *pocket*, *boss*, *hole*, *use edges*, *convert* or *mate* all find the right command. `I` searches recent files and `H` searches FreeCAD help.

**Mouse**
- SolidWorks navigation:
  - middle-drag rotates, Ctrl+middle-drag pans, the wheel zooms at the cursor
  - the wheel direction is set to SolidWorks' default; change it in FreeWorks Options
- **Mouse gestures:** hold the right button and drag toward a command. There are 8 directions, with separate sets for part, sketch, assembly and drawing.
  - Part: N Top, NE Isometric, E Right, SE Normal To, S Bottom, SW Zoom to Fit, W Left, NW Front
  - Sketch: Line, Rectangle, Circle, Arc, Trim, Exit Sketch, Smart Dimension, Centerline
- A plain right-click still opens the context menu. The menu is reordered SolidWorks-style:
  - commands that fit the selection come first (Edit Feature, Edit Sketch, Fillet on an edge, Sketch on a face...)
  - common items next
  - FreeCAD extras under **More**

**Keyboard** (the full list is under Help → FreeWorks Keyboard Shortcuts)

| Key | Command |
|---|---|
| E / F | Extruded Boss/Base / Fillet (Sketch Fillet in a sketch) |
| L / R / C | Line / Corner Rectangle / Circle (in a part they start a sketch first) |
| T / X / D | Trim Entities / Construction Geometry / Smart Dimension |
| A (in Line tool) | switch Line ↔ Tangent Arc |
| M / G | Measure / Magnified Selection |
| W / I / H | Search Commands / Files / Help |
| S | Shortcut Bar (context toolbar at the pointer) |
| Space | Orientation (view selector) |
| Ctrl+1…8 | Front, Back, Left, Right, Top, Bottom, Isometric, Normal To |
| Ctrl+B / Ctrl+Q | Rebuild / Force Rebuild |
| Ctrl+Shift+Z | Previous View |
| F6 / V | Selection Filter bar / Filter Vertices |
| Z / Shift+Z | Zoom Out / Zoom In |
| Ctrl+N / Ctrl+Y | New document / Redo |

**Evaluate**
- **Mass Properties** (Evaluate tab): mass, volume, surface area, centre of mass, principal axes and moments, and moments of inertia at the centre of mass and at the output coordinate system, laid out like SolidWorks' report. You can report relative to any coordinate system, in MMGS, CGS, MKS or IPS, with your choice of decimal places, and include or leave out hidden bodies. It works for parts, assemblies (sub-assemblies included, each component with its own material) and selections.
- **Edit Material** (right-click a body): a material library with SolidWorks names and densities (AISI 1020, Alloy Steel, 6061 Alloy, 1060 Alloy, Copper, Brass, ABS and more), or a custom density taken from the drawing. With no material assigned, the density is 1000 kg/m³, the same default as SolidWorks.
- **Section Properties**.
- **Interference Detection**: lists the clashes and highlights the interference volume in red.
- **Bounding Box**, **Check**.
- **Curvature**, **Zebra Stripes** and **Draft Analysis** from the Curves add-on.
- Section View and Measure.

**Look and performance**
- A light, SolidWorks-style theme: light grey panels, blue accents, a gradient background, and orange hover / blue selection highlights.
- Sketch colours follow SolidWorks: blue = under defined, black = fully defined, red = over defined, green relation symbols.
- Graphics settings:
  - 4× anti-aliasing and GPU vertex buffers
  - finer tessellation for smooth round faces
  - animated view changes
  - a balanced 3-light setup
- **New / Welcome dialog** with Part, Assembly and Drawing, the same as SolidWorks' New Document.

## Where it differs from SolidWorks

FreeWorks changes what you see and how you work. It doesn't change FreeCAD's geometry engine. The main differences are:

- **Feature dialogs (PropertyManager content)** are FreeCAD's own panels, renamed and restyled. Fields and options are FreeCAD's: Pad "Length" instead of "D1", and so on.
- **Rollback:** use *Roll Back* (right-click a feature) and *Roll to End*. There is no draggable rollback bar.
- **Bodies:** FreeCAD needs a **Body** per solid. A new Part already contains one; insert more with Insert → Body. Combine, Intersect and Split work between bodies.
- **Mates:** the Mate PropertyManager works like SolidWorks' one: you pick two entities, it suggests a mate, and you use the pop-up mate toolbar. Behind the scenes each mate is a FreeCAD Assembly joint. Coincident and Tangent are a Distance joint at 0, Concentric is a Cylindrical joint, and Lock is a Fixed joint. Width, Symmetric, Cam, Slot and Universal Joint mates aren't available yet. Gear, Rack Pinion and Screw open FreeCAD's own joint panel.
- **Not available** (FreeCAD has no equivalent): Weldments, Rib, Wrap, Fill Pattern, Variable Pattern, DimXpert, SolidWorks Simulation / Motion. Items marked *(closest FreeCAD equivalent)* in their tooltip are approximations.
- **Sketcher:** FreeCAD shows on-screen value boxes while drawing, and some relations are inferred differently.
- **Speed:** rebuilds of large models depend on FreeCAD's geometry kernel and will usually be slower than SolidWorks.

## Settings and troubleshooting

- **Tools → FreeWorks Options** (or the red FreeWorks button):
  - turn gestures, shortcuts, the heads-up toolbar, the CommandManager, text labels and SolidWorks feature naming on or off
  - change the wheel direction and icon size
  - **Re-apply FreeWorks look & settings**
- **View → User Interface → Show FreeCAD Toolbars** brings back FreeCAD's own toolbars and menus, if you need a FreeCAD workbench FreeWorks doesn't cover. Tools → *FreeCAD Workbenches* lists them all.
- **Help → FreeWorks Command Map** shows every SolidWorks name, the FreeCAD command behind it, and whether it is approximate.
- **Safe mode:** hold **Shift** while starting FreeWorks, or use the *FreeWorks (Safe Mode)* shortcut. You get plain FreeCAD menus and toolbars, and your files are untouched. If FreeWorks didn't finish starting last time, it starts in safe mode by itself and explains why.
- **Tools → Reset FreeWorks Settings** puts FreeWorks' settings back to their defaults. Your projects aren't touched.
- **View → Large Model Mode** makes big models faster to display: coarser display, no anti-aliasing, no view animations. FreeWorks suggests it for documents with 600+ objects.
- **Help → FreeWorks Diagnostics** lists freezes, slow actions and caught errors, ready to paste into a bug report. The log is `FreeWorks.log` (Help → Open Log Folder).
- Messages and errors: View → User Interface → Report View.
- If FreeWorks fails to start, the reason is in `D:\FreeWorks\launcher-error.txt` or the Report View.

## Roadmap

FreeWorks aims to cover everything a CSWA/CSWP-certified SolidWorks user does.
- [What that scope is](docs/CSWA_CSWP_SCOPE.md), [what FreeCAD can and can't do today](docs/GAP_ANALYSIS.md), and [which community add-ons FreeWorks uses](docs/COMMUNITY.md).
- Next: **v1.2** SolidWorks-style mates and assembly tools (materials and Mass Properties are done). **v1.3** equations and configurations. **v1.4** drawings. Progress is tracked in [dev/TRACKER.md](dev/TRACKER.md).

## Credits and licences

- FreeCAD: LGPL-2.1+. SheetMetal, Fasteners, Curves and Render are community add-ons under their own licences (GPL/LGPL), downloaded from their official repositories.
- FreeWorks code and icons: LGPL-2.1+.
- SolidWorks is a trademark of Dassault Systèmes. FreeWorks is not affiliated with it. Its icons are original drawings.
