# 13 — Equations, global variables, configurations, design tables (CSWP segments 1–2)

Tags: [H] help, [B] blog, [O] owner, [K] known, unconfirmed.

## 13.1 Equations, Global Variables, and Dimensions dialog  [H 2013–2018]
Open: Tools > Equations, right-click the **Equations** folder > Manage Equations, or the
Evaluate tab button. (Modify box `=` and PM numeric fields can also create equations — see 05.)
- **Four views** (buttons top-left): **Equation View** (all global variables + equations for
  dimensions and features — add/edit/delete, comments, **suppress features** to troubleshoot) ·
  **Sketch Equation View** (equations used in sketches; these solve immediately with the sketch,
  part equations update on rebuild) · **Dimension View** (every dimension, set or driven; rename
  dimensions and change values in bulk; set-value dimensions appear only here; sketch-equation
  dimensions marked with an icon) · **Ordered View** (solve order; reorder when *Automatic solve
  order* is off; only place to view/unsuppress suppressed equations).
- Table columns: **Name** · **Value / Equation** · **Evaluates to** · **Comments**. Sections:
  **Global Variables**, **Features**, **Equations** (each with an "Add …" row). Names of global
  variables, features and equations are in **quotes**; dimension names (`"D1@Sketch1"`) …; equation
  values start with `=`. [H 2017]
- Editing aids: **type-ahead drop-down** of global variables, functions, file properties after
  typing; click a dimension in the graphics area to insert its name; **syntax colour coding**
  (errors red); **circular references highlighted red with a warning**; **spin arrows** at the end
  of numeric cells; keyboard cell navigation (Tab/Enter/arrows); **Undo/Redo** buttons; multi-row
  select; **sorting and filtering** in all views; **Measure…** creates a driven/reference
  dimension from a measurement. [H]
- Options at the bottom: **Automatic solve order** · **Link to external file** (text file,
  ongoing link) · **Import…** / **Export…** · **Automatic rebuild** · **Angular equation units**
  (Degrees/Radians) · OK / Cancel / Help. [H/K]
- Functions: sin, cos, tan, sec, cosec, cotan, arcsin, arccos, atn, arcsec, arccosec, arccotan,
  abs, exp, log, sqr, int, sgn, **iif(cond, true, false)**, pi; configuration-specific values;
  suppression state equations (`"Feature@Part" = "suppressed"`). [K]
- Disabling/enabling equations in all configurations from Equation/Sketch Equation/Ordered views.
  [H 2018]
- The **Equations** folder appears in the tree once equations exist; dimensions driven by an
  equation show **Σ** in the graphics area. [K]

## 13.2 Link Values  [K]
Right-click a dimension > **Link Values** → Shared Values dialog: **Name** (new or existing
from the list) → linked dimensions show a 🔗 icon, change one and all change. Unlink via right-
click > Unlink Value.

## 13.3 ConfigurationManager  [K — verify]
- Third Manager Pane tab: tree `Part1 Configuration(s) (Default)` → configurations; active one
  bold/green check; **double-click to activate**. Right-click the part name > **Add
  Configuration…**; right-click a configuration > Show Configuration, **Properties**, Add Derived
  Configuration, Delete, Copy/Paste, **Configuration Publisher**.
- **Add Configuration PM**: **Configuration Properties** — Configuration name, Description, *Use
  in bill of materials*, Comment, Custom Properties…; **Bill of Materials Options** — Part number
  displayed when used in BOM: *Document Name / Configuration Name / Link to Parent Configuration /
  User Specified Name*; Child component display when used as subassembly; **Advanced Options** —
  *Suppress new features and mates*, *Hide new components*, *Suppress new components*, *Use
  configuration specific color* + Color…, *Add Rebuild/Save Mark*; **Parent/Child Options**
  (derived).
- **Configure Feature / Configure Dimension** (right-click): **Modify Configurations** table —
  rows = configurations, columns = parameters (dimensions, suppression), add parameters by
  clicking dimensions, save **table views**, *Add new configuration* row.
- Suppress/Unsuppress and dimension changes in a multi-config part ask **This configuration /
  All configurations / Specify configurations** (Modify box drop-down, feature properties).
- Configuration-specific values: in the dimension's Primary Value / Modify box drop-down.

## 13.4 Design tables  [K — verify]
Insert > Tables > **Design Table** PM:
- **Source**: *Blank* · *Auto-create* (from existing configurations/parameters) · *From file*
  (Browse…, **Link to file**).
- **Edit Control**: *Allow model edits to update the design table* · *Block model edits that
  would update the design table*.
- **Options**: *New parameters* · *New configurations* · *Warn when updating design table* ·
  *Enable cell drop-down lists*.
- OK → an **embedded Excel** sheet opens in the graphics area: row 1 title, row 2 headers
  (`D1@Sketch1`, `$STATE@Fillet1`, `$PARTNUMBER`, `$COLOR`, `$DESCRIPTION`, `$PRP@Name`,
  `$CONFIGURATION@Component<1>` …), column A configuration names; an **Add Rows and Columns**
  dialog may list new items; clicking outside Excel generates configurations ("The design table
  generated the following configurations: …").
- Tree: **Tables > Design Table** under the ConfigurationManager; right-click > Edit Table /
  Edit Table in New Window / Save Table / Delete.
- Configurations created by the table show a table icon.
- CSWP segment 2 relies on this: create configurations from a table, change cells, rebuild,
  read mass per configuration.
