# 01 05 Starting a command  (5n_Xg-30358, 9:22)
SOLIDWORKS version seen: 2020 (Search Commands box top right; new part titled Part4).

## Panels seen (literal)
### Edit Sketch PropertyManager (Sketch tool with nothing selected), ~0:14
- Left pane switches to PropertyManager tab. Title **Edit Sketch** with help "?" at right; red ✕ (cancel) under title (no green check yet).
- Group **Message** (yellow note box): "Select a plane or planar face to create a sketch for the entity" (exact wording approximate: "Select a plane on which to create a sketch for the entity.").
- Graphics: Front, Top, Right planes shown as translucent blue rectangles with blue italic name labels; cursor shows sketch-plane glyph. Fly-out FeatureManager tree appears at the top left of the graphics area (Part4 (Default<<Default>…)) and can be used to pick a plane.
- After the pick the view rotates normal to the plane (transcript 0:31).

### Shortcut bar (S key), ~2:35 and 3:30
- Small floating palette at the cursor, title "Sketch Short…" (truncated) in Customize, two columns of icon buttons with small dropdown arrows: Select (selected), Smart Dimension-like/Line, Rectangle, Circle/Slot…, Arc, Spline, Point, Mirror/Offset, Convert, Trim, etc.; ≈14 buttons. Appears at the cursor position.
### Customize ▸ Shortcut Bars tab, ~3:36
- Tabs: Toolbars, **Shortcut Bars**, Commands, Menus, Keyboard, Mouse Gestures, Customization. Title bar "?" and ✕.
- "Toolbar:" combo (shows "Flyout Toolbars"); "Select a Shortcut Toolbar to Customize" with four icon buttons (Part, Assembly, Drawing, Sketch – the Sketch one pressed); "Buttons" grid of command icons (drag source); preview of the shortcut bar at right; label text "Select a toolbar, then click a button to see its description. Drag the button to any toolbar."; **Description** box; group **Command Search**: checkbox "Activate Command Search when the shortcut bar is launched" (checked); OK, Cancel, Help.
### Boss-Extrude PropertyManager (Feature ▸ Extruded Boss/Base), ~5:46
- Tab strip shows PropertyManager tab active. Title **Boss-Extrude**, "?"; buttons ✔ ✕ and an eye (preview) icon.
- Group **From** (collapsible): combo "Sketch Plane".
- Group **Direction 1**: reverse-direction button + combo "Blind"; blue-highlighted selection box (direction vector, empty); depth spinner **10.00mm** (selected/highlighted text) with D1 icon; draft button + spin box (disabled) and checkbox "Draft outward" (disabled).
- Collapsed groups: **Direction 2** (checkbox in header), **Thin Feature** (checkbox in header).
- Group **Selected Contours** with selection box (shows "Sketch-Contour<1>" style entry).
- Graphics: orange arrow handle on the cylinder preview (shaded yellow, outline blue); a rectangular plane outline visible.

## Interactions observed (transcript)
- Esc ends the tool but stays in sketch; Exit Sketch via confirmation corner or CommandManager.
- Window-select then Delete; right-click tree item ▸ Rename tree item.
- Extrude contour pick: clicking an edge selects only that contour (a line when open) vs picking the sketch in the fly-out tree selects the whole sketch.

## Corrections/additions to the catalogue
- 07_boss_cut_features: Boss-Extrude PM literal layout (From / Direction 1 / Direction 2 / Thin Feature / Selected Contours); default depth 10.00mm.
- 03_selection: shortcut bar contents and Customize ▸ Shortcut Bars layout.

## Not shown
- Rename tree item dialog; confirmation corner frame (transcript only).
