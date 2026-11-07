# 01 — UI framework

Confidence tags: **[H]** official help, **[B]** reseller blog / training material, **[F]** forum,
**[O]** the owner's own SOLIDWORKS 2026 settings export, **[K]** known SOLIDWORKS behaviour not
yet confirmed by a fetched source (verify before building).

## 1.1 PropertyManager (PM) anatomy

Where: the **PropertyManager tab** of the Manager Pane (left panel), replacing the
FeatureManager tab while a command runs. Opens automatically for commands that use it; whether it
also opens on plain selection is set in Tools > Options > System Options > General. [H]
(help r_pm_overview, 2013–2022)

Top to bottom:

| Part | What it is |
|---|---|
| Title bar | Feature icon + feature name, e.g. "Boss-Extrude1" (read-only). **Clicking the title bar shows the flyout FeatureManager design tree** in the graphics area (top-left, transparent, expandable) so tree items can be picked while the PM covers the tree. [H] |
| Buttons row | **OK** (green check: accept, execute, close), **Cancel** (red X: ignore, close), **Detailed Preview** (some PMs; older name Preview), **Help** (opens the help topic), **Keep Visible** (pushpin: PM stays open after OK for the next feature of the same type). Wizard PMs add **Back**, **Next**, **Undo**. [H] |
| Message box | Yellow box with an (i) icon at the top: what to select next, or errors/warnings. Collapsible. [H][K] |
| Group boxes | Titled groups (e.g. "Direction 1") with an expand/collapse chevron; some have a **checkbox in the title** that turns the whole group on (Direction 2, Thin Feature, Draft …). Unchecked → collapsed. [H] |
| Selection boxes | List boxes that receive picks from the graphics area or tree. **The active box is coloured** (pink in ≤2015 help; light blue in 2016+ UI — TriMech 2018 calls it "the blue selection box"). Picked items highlight in the graphics area when selected in the box. Right-click in a box: **Delete** (one item), **Clear Selections** (all). The box grows as items are added; drag its bottom handle to resize; right-click **Autosize** or double-click the handle to restore. [H][B] |
| Controls | Spin boxes (with up/down arrows, accept units and `=` equations with global variables/functions/file properties from a drop-down), combos, radio buttons, checkboxes, push buttons. [H] |

Keyboard inside a PM: **Tab** moves between controls, **Space** toggles checkboxes and presses
buttons, **arrow keys** move between radio buttons. **Enter = OK, Esc = Cancel.** [H]

Layout: the PM opens at "optimum width"; drag the divider to resize — it **snaps** to the optimum
width. A **split bar** at the top of the Manager Pane splits it into two panels showing any
combination of PropertyManager / FeatureManager / ConfigurationManager / add-in tabs; double-click
the split bar to return to one panel. **Floating:** drag the title bar off; docking icons appear
(dock upper-left as a tab, upper-left in the graphics area, lower-left, lower-right);
double-click a floating PM's title bar to return it to its last dock. [H]

"The PropertyManager remembers its last used state" — e.g. Fillet reopens with the last type,
radius and options. [H] (Fillet help 2012–2025)

## 1.2 Accepting and cancelling (all PMs and sketches)

[H] help "Accepting Features" (2011–2020), [B] Javelin 2012, TriMech 2018:

- **OK / Cancel** buttons in the PM; **Enter / Esc**.
- **Confirmation Corner** (top-right of the graphics area): OK / Cancel while a PM is open;
  **Exit Sketch / Cancel Sketch** (discard changes) while a sketch is open. Can be turned off:
  System Options > General > Enable Confirmation Corner.
- **D** moves the Confirmation Corner buttons to the pointer (press D again to send them back);
  with no PM/sketch open, D moves the **selection breadcrumbs** to the pointer. D is the default
  key unless D is assigned to another command (the owner assigned **D = Smart Dimension** [O],
  so in the owner's setup D does *not* do this).
- **Right-click → OK / Cancel** at the top of the graphics-area shortcut menu.
- **Right-mouse-button cue:** right after a pick, a small mouse icon appears next to the pointer
  with a symbol over the right button. **Green check = right-click accepts (OK). "Enter" arrow =
  right-click moves to the next selection box** (e.g. Mirror: pick entities → right-click → the
  next box ("Mirror about") becomes active → pick centerline → right-click = OK). The cue only
  shows while the pointer stays **within a small radius of the last pick**; moving away hides it
  and right-click then opens the normal menu. [B]
- After a preview: "Right-click when the pointer changes to [OK cue] to accept the preview, or
  click [cue] to return to the preview without accepting". [H]
