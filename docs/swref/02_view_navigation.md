# 02 — View navigation

Tags: [H] help, [B] blog/training (SOLIDWORKS corporate blog counts as B), [O] owner settings,
[K] known, unconfirmed. Main sources: SOLIDWORKS blog "How do I manipulate my model view; let me
count the ways" (fetched 2026-11-08), help "Middle Mouse Button Functions" / "Zoom In/Out"
2011–2021, help "View Options" 2010–2017, GoEngineer quick reference.

## 2.1 Middle mouse button

| Action | Behaviour |
|---|---|
| **MMB drag** — Rotate View | **If the whole model is on screen it rotates about the model centroid.** Otherwise SOLIDWORKS picks visible geometry, projects a point onto it and rotates about that point; **the entity and point are highlighted magenta during the rotation**. [B] (Parts and assemblies only.) |
| **MMB click an entity, then MMB drag** — Rotate about Entity | Single MMB click on a face, plane, edge, vertex or sketch entity → it highlights **magenta** and the pointer shows a **green line**; MMB-drag rotates about it; deselected on release. **Not available while editing a sketch.** No double-click timing needed. [B][H] |
| **Alt + MMB drag** — Roll View | Rotate parallel to the screen about the model centroid. [B] |
| **Ctrl + MMB drag** — Pan | In drawings a plain MMB drag pans (drawings can't rotate). [B] |
| **Shift + MMB drag** — Zoom | Drag up = zoom in, down = zoom out ("Zoom about Center" in GoEngineer's guide). [B][H] |
| **Ctrl + Alt + MMB drag** — Turn Camera | Camera views only (while editing the camera, or with camera lock off). [B] |
| **Double-click MMB** | Zoom to Fit. [B Essentials quick reference] |
| Mouse speed | System Options > View > View rotation > **Mouse speed** slider (applies to rotate, rotate about entity, roll, turn camera). [B][H] |

## 2.2 Mouse wheel zoom — exact behaviour

[B SOLIDWORKS blog; H 2011–2021 Zoom In/Out]
- **Zoom in (default): the point under the pointer moves toward the screen centre as you zoom
  in.** It is *not* a pure "zoom at cursor": SOLIDWORKS deliberately recentres, because pure
  zoom-at-cursor let the focus point drift off screen over several wheel clicks. Keep the pointer
  on the area you want to zoom into.
- **Zoom out: always about the screen centre, regardless of settings.**
- **View > Modify > Zoom About Screen Center** (toggle) → wheel always zooms about the centre.
- **Default direction: wheel away from you = zoom out, toward you = zoom in.** System Options >
  View > **Reverse mouse wheel zoom direction** (added 2018) flips it. [B Javelin 2017]
- **Accelerated zoom**: spinning the wheel fast accelerates zooming (requires *Display
  scrollbars in graphics view for parts and assemblies* cleared, System Options > Display). [H]
- The wheel zooms the viewport **under the pointer without clicking it first** (multiple
  viewports, or with a PM open). [H 2021]
- Help 2021 also lists **Shift + wheel** to zoom to the pointer position. [H]
- Owner: zoom about cursor, not about screen centre [O].

## 2.3 Keyboard view control  [B][H]

| Key | Action |
|---|---|
| **Space** | **View Orientation** dialog (standard views, save/recall named views, **Update Standard Views** to redefine Front/Top etc., pushpin to keep it open) — and in 2013+ also the **View Selector** cube in the graphics area [K] |
| Ctrl+Space | View Selector (GoEngineer calls it "View Cube") |
| **F** | Zoom to Fit |
| Z / Shift+Z | Zoom out / Zoom in |
| **G** | Magnifying glass (inspect/select detail without changing the view) |
| Ctrl+1 … Ctrl+7 | Front, Back, Left, Right, Top, Bottom, Isometric |
| **Ctrl+8** | **Normal To** (rules below) |
| **Ctrl+Shift+Z** | **Previous View** (undoes view changes only, not model edits) |
| Arrow keys | Rotate by the **Arrow keys increment** (default 15° [K]) about the model centroid, around the screen's horizontal/vertical axis |
| Shift+Arrow | Rotate 90° |
| Ctrl+Arrow | Pan |
| Alt+Left/Right | Roll by the increment |
| Ctrl+R | Redraw |
| Q | Temporarily show planes, origins, coordinate systems while held [B Javelin] |

## 2.4 Normal To rules  [B SOLIDWORKS blog]
- Active sketch, nothing selected → normal to the sketch.
- A feature defined by one sketch selected → normal to that sketch.
- Planar face or plane selected → normal to it.
- Cylindrical or conical face → look along its axis.
- **Ctrl+select a second planar face → that second face points up** in the view.
- Otherwise the rotation follows the face's "natural direction" (the Y axis a sketch on it would
  have).
- **Repeat Normal To → flips 180°** (look from the other side).
- Nothing selected outside a sketch → the **closest orthogonal view** (2010+).
- Normal To and **Zoom to Selection** are on the relevant context toolbars.

## 2.5 Reference triad (bottom-left)  [B SOLIDWORKS blog]
- Click an axis → look along it; clicking the axis already pointing at/away from you reverses.
- Alt+click → rotate about that axis by the arrow-key increment; Ctrl+Alt+click → opposite.
- Shift+click → rotate 90° about it; Ctrl+Shift+click → −90°.
- Owner: triad on, view cube off [O].

## 2.6 Standard views and orientation tools
- **View Orientation dialog** (Space): list of standard + named views, buttons **New View**,
  **Update Standard Views**, **Reset Standard Views**, pushpin; double-click a view to apply.
  [K + B]
- **View Selector**: a translucent cube around the model; click a face, edge or corner of the
  cube to look from there; toggled from the dialog or Ctrl+Space. [K]
- Heads-up flyout: Front/Back/Left/Right/Top/Bottom/Isometric/Trimetric/Dimetric/Normal To,
  **Single view, Two view horizontal/vertical, Four view**, **Link views**. [K]
- Owner default view for new parts: **Trimetric** [O]; FreeWorks 1.5.4 uses isometric — fix.
- **Zoom to fit when changing to standard views** (System Options > View). [H]
- **Transitions** (System Options > View): **View transition** (animate to standard/Normal To
  views, speed slider or Off), **Hide/show component**, **Isolate**, **View selector** speeds.
  [H][B]

## 2.7 Display styles and display aids
Heads-up **Display Style**: Shaded With Edges · Shaded · Hidden Lines Removed · Hidden Lines
Visible · Wireframe. **Section View** (PM: Section 1/2/3 planes or faces, offset, rotation,
triad drag, Section by body/component, Keep cap colour, Show section cap, Graphics-only section
(2024+)… — to detail in 12_evaluate). **View Settings**: RealView, Shadows in Shaded Mode,
Ambient Occlusion, **Perspective**, Cartoon. **Hide/Show Items** flyout. [K]

## 2.8 Implications for FreeWorks (to carry into the spec)
- Wheel zoom-in must **pull the point under the pointer toward the screen centre**; zoom-out must
  be about the centre. FreeCAD's ZoomAtCursor does pure cursor zoom for both — not the same.
- Rotation centre: whole model visible → centroid; otherwise a picked visible point, with a
  **magenta highlight** during the drag; MMB-click an entity → rotate about it with magenta
  highlight and green-line pointer.
- Wheel direction default is the opposite of many other CAD tools (away = zoom out).
- Normal To repeat flips; Ctrl-second-face sets up-direction; nothing selected → closest
  orthogonal view.
