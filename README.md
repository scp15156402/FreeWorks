<p align="center"><img src="docs/assets/logo.png" alt="FreeWorks - open-source CAD software" width="560"></p>

# FreeWorks

**A SolidWorks-style user experience on top of FreeCAD 1.1.4.** Same parametric FreeCAD engine underneath, with a SolidWorks-like interface on top: the CommandManager, FeatureManager, PropertyManager, SolidWorks names, icons, keyboard shortcuts, mouse gestures and view tools.

## Install (Windows)

**Option A: one line.** Open **Windows PowerShell** and paste:

```powershell
irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1 | iex
```

**Option B: download.** Get `FreeWorks.zip` from [Releases](https://github.com/scp15156402/FreeWorks/releases/latest), or click **Code → Download ZIP**.
1. Right-click the zip → Properties → tick **Unblock** → OK.
2. Extract it and double-click **`Install.cmd`**.

Either way, the installer:
- downloads the official portable FreeCAD 1.1.4 (about 450 MB)
- installs everything into **`D:\FreeWorks`**, with no administrator rights needed
- leaves any other FreeCAD on the PC untouched

Start **FreeWorks** from the Desktop or Start Menu shortcut.

Requirements: Windows 10/11 64-bit, about 3 GB of free space, and internet during installation.

The installer also fetches three community add-ons, which FreeWorks integrates into its tabs:

| Add-on | Gives you |
|---|---|
| SheetMetal (shaise) | the **Sheet Metal** tab |
| Fasteners (shaise) | **Toolbox**: bolts, screws, nuts, washers |
| Curves (tomate44) | **Zebra Stripes**, **Curvature**, **Draft Analysis**, advanced surfaces |

**Options**
- Install into another folder:
  ```powershell
  & ([scriptblock]::Create((irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1))) -InstallDir "E:\FreeWorks"
  ```
- `-WithRender` also installs the Render workbench (photo-realistic rendering, which needs an external renderer).
- `-NoAddons` skips the add-ons.

**Updates**
- FreeWorks checks GitHub once a day and offers **Update now**. It closes, updates and restarts, and your settings are kept.
- You can also check manually under Help → *Check for FreeWorks Updates*, or run `D:\FreeWorks\Update.cmd`.

**Uninstall:** run `D:\FreeWorks\uninstall.ps1` (right-click → Run with PowerShell), or delete `D:\FreeWorks` and the two shortcuts.

```
D:\FreeWorks\
  FreeWorks.exe     launcher (keeps all settings inside D:\FreeWorks\UserData)
  FreeCAD\          official FreeCAD 1.1.4, portable, with FreeWorks branding
  UserData\         settings, add-ons (Mod\), macros, icon theme
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
- **Mass Properties**: mass, volume, surface area, centre of mass, principal axes and moments, laid out like SolidWorks' report. Density comes from the assigned material, with 1000 kg/m³ when none is set, the same default as SolidWorks.
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
- **Mates** are FreeCAD Assembly joints with SolidWorks names. Each joint usually equals one or two SolidWorks mates. For example, a Hinge is Concentric + Coincident, and Lock is Fixed. There are no Width, Cam or Symmetric mates.
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
- Messages and errors: View → User Interface → Report View.
- If FreeWorks fails to start, the reason is in `D:\FreeWorks\launcher-error.txt` or the Report View.

## Credits and licences

- FreeCAD: LGPL-2.1+. SheetMetal, Fasteners, Curves and Render are community add-ons under their own licences (GPL/LGPL), downloaded from their official repositories.
- FreeWorks code and icons: LGPL-2.1+.
- SolidWorks is a trademark of Dassault Systèmes. FreeWorks is not affiliated with it. Its icons are original drawings.
