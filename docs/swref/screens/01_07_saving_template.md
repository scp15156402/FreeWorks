# 01 07 Saving template  (x4euSF0iJgE, 6:39)
SOLIDWORKS version seen: 2020 (template path shows "SolidWorks 2020\templates").

## Panels seen (literal)
### Document Properties – Drafting Standard
- Dialog shell as in 01.06 (tabs System Options | Document Properties, Search Options, OK / Cancel / Help bottom right).
- Group **Overall drafting standard**: combo (ISO selected; open list shows ISO, GB (others scroll)). Buttons right: **Rename**, **Copy**, **Delete** (greyed until a modified standard), **Load From External File…**, **Save to External File…** (greyed).
- Group **Uppercase**: checkboxes "All uppercase for notes", "All uppercase for tables", "All uppercase for dimensions and hole callouts"; **Exclusion list** text box with default text `m;mm;cm;km;um;nm;ε;Hz;Pa;`.
### System Options – File Locations
- Left tree (System Options tab) in order: General, MBD, Drawings (children: Display Style, Area Hatch/Fill, Performance), Colors, Sketch (child Relations/Snaps), Display, Selection, Performance, Assemblies, External References, Default Templates, **File Locations**, FeatureManager, Spin Box Increments, View, Backup/Recover, Touch, Hole Wizard/Toolbox, File Explorer, Search, Collaboration, Messages/Errors/Warnings, Synchronize Settings, Import, Export; **Reset…** button under the tree.
- Right: "Show folders for:" combo (**Document Templates**); "Folders:" list showing `C:\ProgramData\SolidWorks\SOLIDWORKS 2020\templates\` and a second path under Program Files (…\lang\english\Tutorial…) highlighted; buttons **Edit All**, **Add…**, **Delete**, **Move Up**, **Move Down** (greyed).
- **Add…** opens the Windows "Select Folder" dialog (title "Select Folder", Documents folder listing, "Folder:" box, Select Folder / Cancel). A progress ring cursor shows while System Options – General loads (the dialog first opens on General).

## Interactions observed (transcript)
- Changing the overall standard cascades to Annotations/Dimensions/Tables; editing a value renames it "ISO-MODIFIED".
- Save As type "Part Templates (*.prtdot)" jumps to the default template folder; New dialog then shows a tab named after the added folder.

## Corrections/additions to the catalogue
- 16_18_options_files_visual: System Options page order (2020), Drafting Standard layout, File Locations controls.

## Not shown
- Save As dialog, New dialog with the new tab (transcript only).
