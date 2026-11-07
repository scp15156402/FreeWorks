# 91 — Behaviour changes in recent releases (the owner runs SOLIDWORKS 2026 SP1.1 [O])

Tags: [H] help/What's New, [B] blog. Only items that change how things look or behave for a
CSWA/CSWP user. Older milestones are noted where they explain current behaviour.

## Milestones that define today's behaviour
| Version | Change |
|---|---|
| 2008 | Context toolbars introduced (drawings 2010). [B] |
| 2009 | Reference triad became clickable. [B] |
| 2010 | Mouse gestures; Normal To with nothing selected → closest orthogonal view. [B] |
| 2013 | Mass Properties dialog: Override Mass Properties button; "Report coordinate values relative to". [H] |
| 2015 | Asymmetric fillets (elliptic/conic). [H][B] |
| 2016 | Bidirectional sweep, Circular Profile sweep; Convert Entities "Select all inner loops"; Make first selection transparent (mates); shortcut-bar command search; UI refresh (flat icons; blue active selection boxes). [H][B] |
| 2017 | Chamfer PM aligned with Fillet (Offset Face, Face Face, convert chamfer ↔ fillet). [H] |
| 2018 | Auto-rotate normal on sketch **edit** (not only creation); Reverse mouse wheel zoom option. [H][B] |
| 2019 | Partial edge fillets/chamfers; Hole callout values in Hole Wizard. [H] |
| 2020 | Fillet/chamfer API reworked (FeatureFillet3 obsolete for constant/face/full round …). [H] |
| 2024 FD | (see below) |
| 2025 SP1 | **Flip Endpoint Tangent** for tangent arcs. [B SolidProfessor] |
| 2025 SP2 | **Shift while sketching a rectangle → square.** [B SOLIDWORKS blog] |
| 2025 FD04 | **Simplified Interface** (View > Workspace) — abridged CommandManager etc.; the owner uses it [O]. |

## SOLIDWORKS 2026 (SP0–SP5) — UI and modelling items [H What's New 2026 TOC, B GoEngineer, SolidProfessor, SOLIDWORKS blog]
- **Hide/Show Manager Pane tabs**: right-click any tab > Customize; collapsed tabs reachable from
  an **ellipsis (…) button**. [H][B]
- **Viewing Dismissed Messages**: status-bar icon (*Show dismissed messages icon in status bar*,
  on by default). [B GoEngineer]
- **Selection filters**: new **Feature filter** (select/delete features such as cut extrudes,
  fillets, holes directly in the graphics area) and **Component filter** (top-level parts and
  subassemblies only — an alternative to breadcrumbs/flyout tree); keyboard shortcuts can be
  assigned to Filter Surface Bodies, Solid Bodies, Midpoints, Center Marks, Centerlines. [B]
- **Modify Dimension dialog** changed (dialog positioned so it does not cover the dimension —
  from earlier research; details to confirm). [B GoEngineer heading]
- **Pin (Keep Visible) for Fillet and Chamfer** to create several features back to back. [B]
- **Smarter command search** — understands terminology from other CAD programs. [B]
- **Warning on unintentionally large component moves** in assemblies. [B]
- **Esc cancels lengthy part operations**; the status bar says Esc can be pressed while
  calculating (SP3: exiting processes with Esc). [H][B]
- **Relation Groups** (2026 SP1): apply one relation to many sketch entities at once and manage it
  as a group. [H][B]
- **Converting images to sketches** (SP1, beta) / to mechanisms (SP4).
- **Reference points by XYZ values**; **Select Bodies by Size** (dynamic selection preview,
  *Select Parent Features*); **Bounding box from a coordinate system**; **Automatic geometry
  pattern activation** (SP2); **Hole Wizard retains sketch options** for repeated use. [H][B]
- **Rebuild requirements for cosmetic changes** (system option). [B]
- **Import Model task pane tab / background import** of neutral files. [B]
- **DSPBR appearances**, flatten floor in scenes, DS ISO font.
- Drawings: auto-generate drawings, magnetic lines for annotations, slot dimensions, breaks in
  dimension lines around text, list button for sheets/tabs.

## Implication
FreeWorks targets the **2026 SP1** behaviour set (the owner's version): Shift-square rectangles,
Fillet/Chamfer pin, relation groups, Manager Pane tab customisation, feature/component selection
filters, Esc to cancel, Simplified Interface layout.
