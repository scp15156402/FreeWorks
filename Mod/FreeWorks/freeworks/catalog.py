"""The FreeWorks command catalog.

Every user-facing command is defined once here with its SolidWorks name,
icon, tooltip and search aliases, and mapped onto the FreeCAD (or FreeWorks)
command that implements it.  The CommandManager, menus, gestures, shortcut
bar and command search all read from this single table, which is what keeps
naming and iconography consistent across the whole application.

'cmd' may be a list: the first command that exists in this installation wins
(so add-on workbenches such as SheetMetal are used only when installed).
"""

C = {}


def add(key, label, cmd, icon=None, tip="", aliases=(), approx=False, optional=False):
    """optional=True: command only exists in newer FreeCAD versions or add-ons (hidden when missing)."""
    C[key] = dict(key=key, label=label, cmd=cmd if isinstance(cmd, (list, tuple)) else [cmd],
                  icon=icon, tip=tip or label, aliases=list(aliases), approx=approx, optional=optional)


# ------------------------------------------------------------------ Features
add("extrude", "Extruded Boss/Base", "FW_ExtrudedBoss", "extrude_boss", "Extrudes a sketch or selected sketch contours in one or two directions to create a solid feature.", ["pad", "extrude", "boss", "base"])
add("revolve", "Revolved Boss/Base", "PartDesign_Revolution", "revolve_boss", "Revolves a sketch or selected sketch contours around an axis to create a solid feature.", ["revolution", "revolve"])
add("sweep", "Swept Boss/Base", "PartDesign_AdditivePipe", "sweep_boss", "Sweeps a closed profile along an open or closed path to create a solid feature.", ["additive pipe", "sweep", "pipe"])
add("loft", "Lofted Boss/Base", "PartDesign_AdditiveLoft", "loft_boss", "Adds material between two or more profiles.", ["additive loft", "loft"])
add("boundary", "Boundary Boss/Base", ["Surface_Sections", "PartDesign_AdditiveLoft"], "boundary_boss", "Adds material between profiles in two directions (closest available: section surface / loft).", ["boundary"], approx=True)
add("helix_boss", "Helix Boss", "PartDesign_AdditiveHelix", "helix_boss", "Sweeps a profile along a helix (springs, threads).", ["additive helix", "spring", "coil"])
add("extrude_cut", "Extruded Cut", "FW_ExtrudedCut", "extrude_cut", "Cuts a solid model by extruding a sketched profile in one or two directions.", ["pocket", "cut extrude", "cut"])
add("hole_wizard", "Hole Wizard", "PartDesign_Hole", "hole_wizard", "Inserts holes with a pre-defined cross section (counterbore, countersink, tapped).", ["hole", "tapped hole", "counterbore", "countersink"])
add("revolve_cut", "Revolved Cut", "PartDesign_Groove", "revolve_cut", "Cuts a solid model by revolving a sketched profile around an axis.", ["groove", "revolve cut"])
add("sweep_cut", "Swept Cut", "PartDesign_SubtractivePipe", "sweep_cut", "Cuts a solid model by sweeping a closed profile along a path.", ["subtractive pipe"])
add("loft_cut", "Lofted Cut", "PartDesign_SubtractiveLoft", "loft_cut", "Cuts a solid model by removing material between two or more profiles.", ["subtractive loft"])
add("helix_cut", "Helix Cut", "PartDesign_SubtractiveHelix", "helix_cut", "Cuts material along a helix (threads).", ["subtractive helix", "thread"])
add("fillet", "Fillet", "PartDesign_Fillet", "fillet", "Creates a rounded internal or external face along one or more edges.", ["round", "blend", "radius"])
add("chamfer", "Chamfer", "PartDesign_Chamfer", "chamfer", "Creates a bevel feature on selected edges or a vertex.", ["bevel"])
add("shell", "Shell", "PartDesign_Thickness", "shell", "Removes material from a solid by hollowing it, leaving faces open.", ["thickness", "hollow"])
add("draft", "Draft", "PartDesign_Draft", "draft", "Tapers selected model faces by a specified angle.", ["taper"])
add("lpattern", "Linear Pattern", "PartDesign_LinearPattern", "linear_pattern", "Patterns features in one or two linear directions.", ["array", "rectangular pattern"])
add("cpattern", "Circular Pattern", "PartDesign_PolarPattern", "circular_pattern", "Patterns features around an axis.", ["polar pattern", "radial pattern"])
add("mirror", "Mirror", "PartDesign_Mirrored", "mirror", "Mirrors features about a face or a plane.", ["mirrored", "symmetry"])
add("multipattern", "Pattern Combination", "PartDesign_MultiTransform", "multi_transform", "Combines several patterns and mirrors into one feature (closest to Table/Sketch Driven Pattern).", ["multitransform", "table driven pattern", "sketch driven pattern"], approx=True)
add("combine", "Combine", "PartDesign_Boolean", "combine", "Combines bodies: Add, Subtract or Common.", ["boolean", "subtract", "union"])
add("intersect", "Intersect", "Part_Common", "intersect", "Keeps the volume common to the selected bodies.", ["common"])
add("split", "Split", "Part_SliceApart", "split", "Splits a body into multiple bodies with a plane or surface.", ["slice", "split bodies"])
add("move_copy_body", "Move/Copy Bodies", "Std_TransformManip", "move_body", "Moves, rotates or copies a body using the triad.", ["transform", "move body", "placement"])
add("scale", "Scale", "Part_Scale", "scale", "Scales a body uniformly or non-uniformly.", ["resize"])
add("thicken", "Thicken", "Part_Thickness", "thicken", "Creates a solid by thickening a surface.", [], approx=True)
add("offset_surface", "Offset Surface", "Part_Offset", "offset_surface", "Offsets faces or a body.", ["offset"])
add("delete_face", "Delete Face", ["Part_Defeaturing"], "delete_face", "Deletes faces from a body and heals the result (Defeaturing).", ["defeature", "remove face"])
add("check", "Check", "Part_CheckGeometry", "check", "Checks the model for geometry errors.", ["check geometry", "validate"])

# ------------------------------------------------------------- Reference geom
add("plane", "Plane", "PartDesign_Plane", "plane", "Adds a reference plane.", ["datum plane", "work plane"])
add("axis", "Axis", "PartDesign_Line", "axis", "Adds a reference axis.", ["datum line", "reference line"])
add("point", "Point", "PartDesign_Point", "point", "Adds a reference point.", ["datum point"])
add("csys", "Coordinate System", "PartDesign_CoordinateSystem", "coordinate_system", "Defines a coordinate system for a part or assembly.", ["local coordinate system", "lcs"])
add("shapebinder", "Reference Surface/Curve", "PartDesign_SubShapeBinder", "ref_geometry", "References faces or edges from other bodies (closest to reference curve / surface).", ["shape binder", "reference curve", "reference surface"], approx=True)

# ------------------------------------------------------------------- Sketch
add("sketch", "Sketch", "FW_Sketch", "sketch", "Sketches a new sketch or edits an existing one.", ["new sketch", "edit sketch"])
add("edit_sketch", "Edit Sketch", "FW_EditSketch", "sketch", "Edits the sketch of the selected feature.", ["open sketch"])
add("edit_feature", "Edit Feature", "Std_Edit", "options", "Edits the parameters of the selected feature.", ["edit definition"])
add("exit_sketch", "Exit Sketch", "FW_ExitSketch", "exit_sketch", "Exits the sketch and saves changes.", ["leave sketch", "close sketch"])
add("smart_dim", "Smart Dimension", ["Sketcher_Dimension"], "smart_dimension", "Creates a dimension for one or more selected entities.", ["dimension", "constrain distance", "constraint"])
add("line", "Line", "Sketcher_CreatePolyline", "line", "Sketches a line (continuous; Esc or double-click to end).", ["polyline", "create line"])
add("line_single", "Single Line", "Sketcher_CreateLine", "line", "Sketches a single line segment.", ["create line"])
add("centerline", "Centerline", "FW_Centerline", "centerline", "Sketches a construction centerline.", ["construction line"])
add("corner_rect", "Corner Rectangle", "Sketcher_CreateRectangle", "corner_rectangle", "Sketches a rectangle by two corners.", ["rectangle"])
add("center_rect", "Center Rectangle", "Sketcher_CreateRectangle_Center", "center_rectangle", "Sketches a rectangle from its center.", ["center rectangle"])
add("rounded_rect", "Rounded Rectangle", "Sketcher_CreateOblong", "slot_rectangle", "Sketches a rectangle with rounded corners.", ["oblong"])
add("parallelogram", "Parallelogram", ["Sketcher_Create3PointRectangle", "Sketcher_CreateRectangle"], "corner_rectangle", "Sketches a rectangle by three points.", [], approx=True)
add("circle", "Circle", "Sketcher_CreateCircle", "circle", "Sketches a circle by center and radius.", ["center circle"])
add("perimeter_circle", "Perimeter Circle", "Sketcher_Create3PointCircle", "perimeter_circle", "Sketches a circle through three points.", ["3 point circle"])
add("center_arc", "Centerpoint Arc", "Sketcher_CreateArc", "arc", "Sketches an arc from a center point, start and end.", ["arc"])
add("tangent_arc", "Tangent Arc", "FW_TangentArc", "tangent_arc", "Sketches an arc tangent to a sketch entity (polyline arc mode).", [], approx=True)
add("3pt_arc", "3 Point Arc", "Sketcher_Create3PointArc", "three_point_arc", "Sketches an arc through start, end and mid points.", ["three point arc"])
add("ellipse", "Ellipse", "Sketcher_CreateEllipseByCenter", "ellipse", "Sketches a complete ellipse.", [])
add("partial_ellipse", "Partial Ellipse", "Sketcher_CreateArcOfEllipse", "partial_ellipse", "Sketches an elliptical arc.", ["arc of ellipse"])
add("parabola", "Parabola", "Sketcher_CreateArcOfParabola", "parabola", "Sketches a parabolic curve.", [])
add("spline", "Spline", "Sketcher_CreateBSplineByInterpolation", "spline", "Sketches a spline through points.", ["bspline", "interpolation"])
add("style_spline", "Style Spline", "Sketcher_CreateBSpline", "style_spline", "Sketches a spline by control polygon.", ["bezier", "control point spline"])
add("slot", "Straight Slot", "Sketcher_CreateSlot", "slot_rectangle", "Sketches a straight slot.", ["slot", "obround"])
add("arc_slot", "Centerpoint Arc Slot", "Sketcher_CreateArcSlot", "slot_rectangle", "Sketches an arc slot.", ["arc slot"])
add("polygon", "Polygon", "Sketcher_CreateRegularPolygon", "polygon", "Sketches a regular polygon.", ["hexagon"])
add("skpoint", "Point", "Sketcher_CreatePoint", "sketch_point", "Sketches a point.", ["sketch point"])
add("sk_fillet", "Sketch Fillet", "Sketcher_CreateFillet", "sketch_fillet", "Rounds the corner at the intersection of two sketch entities.", [])
add("sk_chamfer", "Sketch Chamfer", "Sketcher_CreateChamfer", "sketch_chamfer", "Bevels the corner at the intersection of two sketch entities.", [])
add("text", "Text", ["Sketcher_CreateText"], "sketch_text", "Sketches text (FreeCAD 1.2 and later).", [], optional=True)
add("trim", "Trim Entities", "Sketcher_Trimming", "trim", "Trims a sketch entity.", ["trimming", "power trim"])
add("extend", "Extend Entities", "Sketcher_Extend", "extend", "Extends a sketch entity.", [])
add("split_ent", "Split Entities", "Sketcher_Split", "split_entities", "Splits a sketch entity at a point.", [])
add("offset", "Offset Entities", "Sketcher_Offset", "offset_entities", "Offsets sketch entities by a distance.", ["offset"])
add("convert", "Convert Entities", "Sketcher_Projection", "convert_entities", "Projects selected model edges onto the sketch plane.", ["external geometry", "projection", "use edges"])
add("intersection", "Intersection Curve", "Sketcher_Intersection", "intersection_curve", "Creates sketch geometry where the sketch plane intersects the model.", ["intersection"])
add("carbon", "Copy Sketch", "Sketcher_CarbonCopy", "copy_entities", "Copies all geometry from another sketch.", ["carbon copy", "derived sketch"])
add("sk_mirror", "Mirror Entities", "Sketcher_Symmetry", "mirror_entities", "Mirrors selected entities about a centerline.", ["symmetry", "mirror"])
add("sk_lpattern", "Linear Sketch Pattern", "Sketcher_RectangularArray", "linear_sketch_pattern", "Creates a linear pattern of sketch entities.", ["rectangular array"])
add("sk_cpattern", "Circular Sketch Pattern", "Sketcher_Rotate", "circular_sketch_pattern", "Creates a circular pattern of sketch entities (Rotate with copies).", ["polar array"])
add("sk_move", "Move Entities", "Sketcher_Translate", "move_entities", "Moves sketch entities (set copies to 0).", ["translate", "move"])
add("sk_copy", "Copy Entities", "Sketcher_Translate", "copy_entities", "Copies sketch entities.", ["copy"])
add("sk_rotate", "Rotate Entities", "Sketcher_Rotate", "rotate_entities", "Rotates sketch entities.", ["rotate"])
add("sk_scale", "Scale Entities", "Sketcher_Scale", "scale_entities", "Scales sketch entities.", ["scale"])
add("construction", "Construction Geometry", "Sketcher_ToggleConstruction", "construction", "Toggles selected entities between sketch and construction geometry.", ["toggle construction", "for construction"])
add("relations", "Add Relation", "FW_AddRelation", "relations", "Adds a geometric relation between the selected entities.", ["constraint", "relation"])
add("delete_relations", "Delete All Relations", "Sketcher_DeleteAllConstraints", "delete_relations", "Deletes all relations in the active sketch.", ["delete constraints"])
add("repair_sketch", "Repair Sketch", "Sketcher_ValidateSketch", "repair_sketch", "Finds and fixes sketch errors.", ["validate sketch"])
add("normal_sketch", "Normal To Sketch", "Sketcher_ViewSketch", "normal_to_sketch", "Rotates the view normal to the sketch plane.", ["view sketch"])
add("section_sketch", "Section View (Sketch)", "Sketcher_ViewSection", "section_view", "Shows a section through the sketch plane.", [])
add("grid", "Grid", "Sketcher_Grid", "options", "Toggles the sketch grid.", ["snap grid"])
add("snap", "Sketch Snaps", "Sketcher_Snap", "options", "Toggles sketch snapping.", ["snap"])

# relations (FreeCAD constraint icons are already relation-style; names are SW)
add("rel_coincident", "Coincident", "Sketcher_ConstrainCoincidentUnified", None, "Makes points coincident or a point lie on an entity.", ["on edge"])
add("rel_horizontal", "Horizontal", "Sketcher_ConstrainHorizontal", None, "Makes entities horizontal.", [])
add("rel_vertical", "Vertical", "Sketcher_ConstrainVertical", None, "Makes entities vertical.", [])
add("rel_parallel", "Parallel", "Sketcher_ConstrainParallel", None, "Makes lines parallel.", [])
add("rel_perpendicular", "Perpendicular", "Sketcher_ConstrainPerpendicular", None, "Makes lines perpendicular.", [])
add("rel_tangent", "Tangent", "Sketcher_ConstrainTangent", None, "Makes entities tangent.", [])
add("rel_equal", "Equal", "Sketcher_ConstrainEqual", None, "Makes entities equal length/radius.", [])
add("rel_symmetric", "Symmetric", "Sketcher_ConstrainSymmetric", None, "Makes entities symmetric about a line.", [])
add("rel_fix", "Fix", "Sketcher_ConstrainBlock", None, "Fixes the selected entity in place.", ["block", "lock"])
add("rel_midpoint", "Midpoint", "Sketcher_ConstrainSymmetric", None, "Places a point at the midpoint of a line (select the two end points and the point).", [], approx=True)
add("rel_hdist", "Horizontal Distance", "Sketcher_ConstrainDistanceX", None, "Horizontal dimension.", ["horizontal dimension"])
add("rel_vdist", "Vertical Distance", "Sketcher_ConstrainDistanceY", None, "Vertical dimension.", ["vertical dimension"])
add("rel_length", "Length", "Sketcher_ConstrainDistance", None, "Length/distance dimension.", [])
add("rel_radius", "Radius", "Sketcher_ConstrainRadius", None, "Radius dimension.", [])
add("rel_diameter", "Diameter", "Sketcher_ConstrainDiameter", None, "Diameter dimension.", [])
add("rel_angle", "Angular Dimension", "Sketcher_ConstrainAngle", None, "Angle dimension.", ["angle"])
add("rel_lock", "Lock Position", "Sketcher_ConstrainLock", None, "Locks a point with horizontal and vertical dimensions.", [])

# ------------------------------------------------------------------ Evaluate
add("measure", "Measure", "Std_Measure", "measure", "Measures distance, angle, radius and size of selected entities.", ["distance", "ruler"])
add("mass_props", "Mass Properties", "FW_MassProperties", "mass_properties", "Displays mass, volume, surface area, center of mass and moments of inertia.", ["volume", "center of mass", "inertia", "weight", "surface area"])
add("section_props", "Section Properties", "FW_SectionProperties", "section_properties", "Displays area, centroid and second moments of a selected planar face.", ["area moment"])
add("interference", "Interference Detection", "FW_Interference", "interference", "Detects interference between bodies or components.", ["collision", "clash"])
add("bbox", "Bounding Box", "FW_BoundingBox", "bounding_box", "Reports the bounding box of the selection or part.", ["size", "extents"])
add("section_view", "Section View", "Std_ToggleClipPlane", "section_view", "Displays a cutaway of the model using clipping planes.", ["clip plane", "cut view"])
add("section_cut", "Persistent Section", "Part_SectionCut", "section_properties", "Creates a section view that stays while you work.", ["section cut"])
add("curvature", "Curvature", ["Curves_SurfaceAnalysis", "Part_CheckGeometry"], "curvature", "Displays surface curvature analysis (Curves add-on).", ["curvature analysis", "surface analysis"])
add("zebra", "Zebra Stripes", ["ZebraTool"], "zebra", "Displays zebra stripes to check surface smoothness (Curves add-on).", ["zebra"])
add("draft_analysis", "Draft Analysis", ["Curves_DraftAnalysis"], "draft", "Colors faces by draft angle relative to a pull direction (Curves add-on).", ["draft check"])
add("clarify", "Select Other", "Std_ClarifySelection", "selection_filter", "Selects hidden or overlapping entities under the pointer.", ["clarify selection"])

# ------------------------------------------------------------------ Assembly
add("new_assembly", "Assembly", "Assembly_CreateAssembly", "new_assembly", "Creates an assembly in the current document.", ["create assembly"])
add("insert_component", "Insert Components", "Assembly_InsertLink", "insert_component", "Adds a part or sub-assembly to the assembly.", ["insert", "add part", "component"])
add("new_component", "New Part", "Assembly_InsertNewPart", "new_part", "Creates a new part in the context of the assembly.", ["new component", "insert new part"])
add("mate_fixed", "Lock Mate", "Assembly_CreateJointFixed", "mate_fixed", "Locks two components together (also Coincident with aligned frames).", ["fixed joint", "coincident mate", "lock"])
add("mate_revolute", "Concentric + Coincident (Hinge)", "Assembly_CreateJointRevolute", "mate", "Hinge: one rotational degree of freedom.", ["revolute joint", "hinge", "pin"])
add("mate_concentric", "Concentric", "Assembly_CreateJointCylindrical", "mate", "Concentric mate: rotation and translation along the axis.", ["cylindrical joint"])
add("mate_slider", "Slot / Slider", "Assembly_CreateJointSlider", "mate", "Translation along one direction.", ["slider joint", "prismatic", "slot mate"])
add("mate_ball", "Coincident Point", "Assembly_CreateJointBall", "mate", "Point-to-point coincident (ball joint).", ["ball joint", "spherical"])
add("mate_distance", "Distance", "Assembly_CreateJointDistance", "mate", "Distance mate (also coincident at 0, tangent between round faces).", ["distance mate", "coincident", "tangent"])
add("mate_parallel", "Parallel", "Assembly_CreateJointParallel", "mate", "Parallel mate.", ["parallel joint"])
add("mate_perpendicular", "Perpendicular", "Assembly_CreateJointPerpendicular", "mate", "Perpendicular mate.", ["perpendicular joint"])
add("mate_angle", "Angle", "Assembly_CreateJointAngle", "mate", "Angle mate.", ["angle joint"])
add("mate_rack", "Rack Pinion", "Assembly_CreateJointRackPinion", "mate", "Rack and pinion mechanical mate.", ["rack and pinion"])
add("mate_screw", "Screw", "Assembly_CreateJointScrew", "mate", "Screw mechanical mate.", ["screw joint"])
add("mate_gear", "Gear", "Assembly_CreateJointGears", "mate", "Gear mechanical mate.", ["gears joint"])
add("mate_belt", "Belt/Chain", "Assembly_CreateJointBelt", "mate", "Belt / chain mechanical mate.", ["belt"])
add("mate", "Mate", "FW_Mate", "mate", "Positions two components relative to each other.", ["joint", "constraint", "mates"])
add("fix_component", "Fix", "Assembly_ToggleGrounded", "fix_component", "Fixes (grounds) the selected component.", ["ground", "grounded", "float"])
add("move_component", "Move Component", "Std_TransformManip", "move_component", "Moves a component within its degrees of freedom.", ["drag component"])
add("solve", "Rebuild Assembly", "Assembly_SolveAssembly", "solve_assembly", "Solves the assembly mates.", ["solve"])
add("exploded_view", "Exploded View", "Assembly_CreateView", "exploded_view", "Creates an exploded view.", ["explode"])
add("asm_bom", "Bill of Materials", "Assembly_CreateBom", "bom", "Inserts a bill of materials.", ["bom", "parts list"])
add("motion", "Motion Study", "Assembly_CreateSimulation", "rotate_component", "Creates a simple motion study (driven joints).", ["simulation", "animation"], approx=True)
add("fasteners", "Toolbox (Fasteners)", ["Fasteners_Search"], "hole_wizard", "Inserts standard hardware - bolts, screws, nuts, washers, pins (Fasteners add-on).", ["toolbox", "bolt", "screw", "nut", "washer"], approx=True)
add("fastener_bom", "Fastener BOM", ["Fasteners_BOM"], "bom", "Lists the fasteners used (Fasteners add-on).", [])

# ------------------------------------------------------------------- Drawing
add("new_sheet", "Drawing Sheet", "TechDraw_PageDefault", "new_drawing", "Inserts a new drawing sheet with the default sheet format.", ["page", "sheet"])
add("sheet_format", "Sheet Format...", "TechDraw_PageTemplate", "new_drawing", "Inserts a drawing sheet from a sheet format / template.", ["template", "title block"])
add("model_view", "Model View", "TechDraw_View", "model_view", "Inserts an orthographic or named view of a model.", ["view", "base view"])
add("std3view", "Standard 3 View", "TechDraw_ProjectionGroup", "standard_3view", "Creates three related default orthographic views.", ["projection group", "three view"])
add("projected_view", "Projected View", "TechDraw_ProjectionGroup", "projected_view", "Inserts a projected view from an existing view.", ["projection"])
add("section_dview", "Section View", "TechDraw_SectionView", "section_drawing_view", "Adds a section view by cutting the parent view with a section line.", ["section"])
add("aligned_section", "Aligned Section View", "TechDraw_ComplexSection", "section_drawing_view", "Adds a section along a multi-segment line.", ["complex section"])
add("detail_view", "Detail View", "TechDraw_DetailView", "detail_view", "Adds a detail view showing a portion of a view, usually at an enlarged scale.", ["detail"])
add("broken_view", "Break", "TechDraw_BrokenView", "broken_view", "Adds a broken-out break to a drawing view.", ["broken view"])
add("crop_view", "Crop View", "TechDraw_ClipGroup", "detail_view", "Crops a view using a clip group.", ["clip"], approx=True)
add("d_smart_dim", "Smart Dimension", "TechDraw_Dimension", "smart_dimension", "Creates a dimension for the selected entities.", ["dimension"])
add("d_hdim", "Horizontal Dimension", "TechDraw_HorizontalDimension", "dim_horizontal", "Horizontal dimension.", [])
add("d_vdim", "Vertical Dimension", "TechDraw_VerticalDimension", "dim_vertical", "Vertical dimension.", [])
add("note", "Note", "TechDraw_Annotation", "note", "Inserts a note.", ["text", "annotation"])
add("rich_note", "Note (formatted)", "TechDraw_RichTextAnnotation", "note", "Inserts a formatted note.", [])
add("balloon", "Balloon", "TechDraw_Balloon", "balloon", "Adds a balloon.", [])
add("center_mark", "Center Mark", "TechDraw_ExtensionCircleCenterLines", "center_mark", "Adds center marks to circles and arcs.", ["centermark"])
add("centerline_d", "Centerline", "TechDraw_FaceCenterLine", "centerline_drawing", "Adds centerlines to a face.", [])
add("centerline_2l", "Centerline (2 Lines)", "TechDraw_2LineCenterLine", "centerline_drawing", "Adds a centerline between two lines.", [])
add("leader", "Leader", "TechDraw_LeaderLine", "note", "Adds a leader line.", [])
add("hatch", "Area Hatch/Fill", "TechDraw_GeometricHatch", "hatch", "Adds a hatch pattern to a face.", ["hatch"])
add("weld_symbol", "Weld Symbol", "TechDraw_WeldSymbol", "weld_symbol", "Adds a weld symbol.", [])
add("surface_finish", "Surface Finish", "TechDraw_SurfaceFinishSymbols", "surface_finish", "Adds a surface finish symbol.", [])
add("hole_fit", "Hole/Shaft Fit", "TechDraw_HoleShaftFit", "dim_horizontal", "Adds a fit tolerance to a dimension.", ["tolerance"])
add("d_bom", "Bill of Materials", ["Assembly_CreateBom", "TechDraw_SpreadsheetView"], "bom", "Inserts a bill of materials table.", ["bom", "table"])
add("table", "Table", "TechDraw_SpreadsheetView", "bom", "Inserts a spreadsheet table into the sheet.", ["general table"])
add("export_dxf", "Save Sheet as DXF", "TechDraw_ExportPageDXF", "new_drawing", "Exports the active sheet to DXF.", ["dxf", "export"])
add("print_pdf", "Export PDF", "Std_PrintPdf", "new_drawing", "Saves the sheet as PDF.", ["pdf"])

# ---------------------------------------------------------------- Sheet metal
add("sm_base", "Base Flange/Tab", ["SheetMetal_AddBase", "SheetMetal_BaseShape"], "base_flange", "Creates a sheet metal part from a sketch.", ["base flange", "tab"])
add("sm_edge", "Edge Flange", "SheetMetal_AddWall", "edge_flange", "Adds a wall to a selected edge.", ["wall", "flange"])
add("sm_sketched_bend", "Sketched Bend", "SheetMetal_AddFoldWall", "sketched_bend", "Bends a sheet along a sketched line.", ["fold"])
add("sm_bend", "Insert Bends", "SheetMetal_AddBend", "sketched_bend", "Adds bends to sharp edges.", ["bend"])
add("sm_relief", "Corner Relief", "SheetMetal_AddCornerRelief", "corner_relief", "Adds corner reliefs.", ["relief"])
add("sm_rip", "Rip", "SheetMetal_AddJunction", "sheet_junction", "Creates a gap (rip) at an edge.", ["junction", "rip"])
add("sm_forming", "Forming Tool", "SheetMetal_Forming", "sketched_bend", "Applies a forming tool shape.", ["emboss", "louver"])
add("sm_unfold", "Flatten", "SheetMetal_Unfold", "unfold", "Creates a flat pattern.", ["unfold", "flat pattern"])
add("sm_sketch_on", "Cut on Sheet", "SheetMetal_SketchOnSheet", "extrude_cut", "Cuts a sketch through the folded sheet.", [])
add("sm_extend", "Extend Face", "SheetMetal_Extrude", "edge_flange", "Extends a sheet-metal face.", ["extend wall"])
add("sm_hem", "Hem", "SheetMetal_AddHem", "edge_flange", "Adds a hem to a selected edge.", [])
add("sm_convert", "Convert to Sheet Metal", "SheetMetal_FromSolid", "base_flange", "Converts a solid into a sheet-metal part.", ["from solid"])
add("sm_cutout", "Corner Cutout", "SheetMetal_AddCutout", "corner_relief", "Adds a cutout at a corner.", [])

# ------------------------------------------------------------------ Surfaces
add("s_fill", "Filled Surface", "Surface_Filling", "surface_fill", "Patches a surface within a boundary of edges.", ["fill"])
add("s_loft", "Lofted Surface", "Surface_Sections", "surface_loft", "Creates a surface through sections.", ["sections"])
add("s_boundary", "Boundary Surface", "Surface_GeomFillSurface", "surface_loft", "Creates a surface from boundary curves.", ["geomfill"])
add("s_extend", "Extend Surface", "Surface_ExtendFace", "surface_extend", "Extends a surface.", [])
add("s_blend", "Blend Curve", "Surface_BlendCurve", "surface_blend", "Creates a curvature-continuous curve between two edges.", [])
add("s_ruled", "Ruled Surface", "Part_RuledSurface", "ruled_surface", "Creates a surface between two edges.", [])
add("s_offset", "Offset Surface", "Part_Offset", "offset_surface", "Offsets a surface.", [])
add("s_thicken", "Thicken", "Part_Thickness", "thicken", "Thickens a surface into a solid.", [], approx=True)
add("s_knit", "Knit Surface", ["Part_MakeSolid", "Part_Builder"], "knit_surface", "Combines surfaces (Shape builder).", ["sew", "knit"], approx=True)
add("s_extrude", "Extruded Surface", "Part_Extrude", "surface_extend", "Extrudes a curve into a surface.", [])
add("s_revolve", "Revolved Surface", "Part_Revolve", "revolve_boss", "Revolves a curve into a surface.", [])
add("s_sweep", "Swept Surface", "Part_Sweep", "sweep_boss", "Sweeps a profile along a path.", [])

# ------------------------------------------------------------- View / general
add("zoom_fit", "Zoom to Fit", "Std_ViewFitAll", "zoom_fit", "Zooms the model to fit the window.", ["fit all"])
add("zoom_area", "Zoom to Area", "Std_ViewBoxZoom", "zoom_area", "Zooms to an area you select with a bounding box.", ["box zoom"])
add("zoom_sel", "Zoom to Selection", "Std_ViewFitSelection", "zoom_fit", "Zooms to the selected entities.", ["fit selection"])
add("zoom_in", "Zoom In", "Std_ViewZoomIn", "zoom_in_out", "Zooms in.", [])
add("zoom_out", "Zoom Out", "Std_ViewZoomOut", "zoom_in_out", "Zooms out.", [])
add("prev_view", "Previous View", "FW_PreviousView", "previous_view", "Displays the previous view.", ["undo view"])
add("v_front", "Front", "FW_ViewFront", "view_orientation", "Front view (Ctrl+1).", ["front view"])
add("v_back", "Back", "FW_ViewBack", "view_orientation", "Back view (Ctrl+2).", ["rear", "back view"])
add("v_left", "Left", "FW_ViewLeft", "view_orientation", "Left view (Ctrl+3).", ["left view"])
add("v_right", "Right", "FW_ViewRight", "view_orientation", "Right view (Ctrl+4).", ["right view"])
add("v_top", "Top", "FW_ViewTop", "view_orientation", "Top view (Ctrl+5).", ["top view", "plan"])
add("v_bottom", "Bottom", "FW_ViewBottom", "view_orientation", "Bottom view (Ctrl+6).", ["bottom view"])
add("v_iso", "Isometric", "FW_ViewIso", "view_orientation", "Isometric view (Ctrl+7).", ["iso"])
add("v_dimetric", "Dimetric", "Std_ViewDimetric", "view_orientation", "Dimetric view.", [])
add("v_trimetric", "Trimetric", "Std_ViewTrimetric", "view_orientation", "Trimetric view.", [])
add("normal_to", "Normal To", "FW_NormalTo", "normal_to", "Rotates the view normal to the selected plane or face (Ctrl+8).", ["align to selection", "look at"])
add("view_orient", "View Orientation", "FW_ViewOrientationMenu", "view_orientation", "Shows the view orientation menu (Spacebar).", ["view selector", "orientation"])
add("ds_edges", "Shaded With Edges", "FW_DisplayShadedEdges", "display_style", "Displays a shaded view of the model with its edges.", ["flat lines"])
add("ds_shaded", "Shaded", "FW_DisplayShaded", "display_shaded", "Displays a shaded view of the model.", [])
add("ds_hlr", "Hidden Lines Removed", "FW_DisplayHLR", "display_hlr", "Displays only edges visible from the current angle.", ["hidden line"])
add("ds_wire", "Wireframe", "FW_DisplayWireframe", "display_wireframe", "Displays all edges of the model.", [])
add("ds_points", "Points", "FW_DisplayPoints", "display_wireframe", "Displays vertices only.", [])
add("hide_show", "Hide/Show Items", "FW_HideShowItems", "hide_show", "Toggles visibility of planes, axes, origins and sketches.", ["view planes", "view origins", "view sketches"])
add("toggle_vis", "Hide/Show", "Std_ToggleVisibility", "hide_show", "Hides or shows the selected items.", ["visibility"])
add("appearance", "Edit Appearance", "Std_SetAppearance", "appearance", "Edits color, material and optical properties.", ["color", "colour", "material"])
add("material", "Edit Material", "FW_EditMaterial", "appearance", "Assigns a material (SOLIDWORKS names: AISI 1020, 6061 Alloy, ...) or a custom density to the part or selected bodies.", ["material", "density", "steel", "aluminum", "aluminium"])
add("scene", "Apply Scene", "FW_SceneMenu", "scene", "Changes the background scene.", ["background"])
add("perspective", "Perspective", "Std_PerspectiveCamera", "perspective", "Displays a perspective view.", [])
add("orthographic", "Orthographic", "Std_OrthographicCamera", "view_orientation", "Displays an orthographic view.", [])
add("rebuild", "Rebuild", "FW_Rebuild", "rebuild", "Rebuilds the model (Ctrl+B).", ["recompute", "refresh", "regenerate"])
add("force_rebuild", "Force Rebuild", "FW_ForceRebuild", "force_rebuild", "Rebuilds all features of the model (Ctrl+Q).", ["recompute all"])
add("options", "Options", "Std_DlgPreferences", "options", "Changes system options and document properties.", ["preferences", "settings", "system options"])
add("fw_options", "FreeWorks Options", "FW_Options", "freeworks", "FreeWorks interface options.", ["freeworks settings"])
add("customize", "Customize...", "Std_DlgCustomize", "options", "Customizes toolbars, shortcuts and macros.", ["keyboard", "shortcuts"])
add("search", "Search Commands", "FW_SearchCommands", "search", "Finds a command by its SolidWorks name (W).", ["find command"])
add("new_doc", "New...", "FW_New", "new_document", "Creates a new Part, Assembly or Drawing (Ctrl+N).", ["new part", "new document"])
add("sel_filter", "Selection Filter", "FW_ToggleFilterToolbar", "selection_filter", "Toggles the selection filter toolbar (F6).", ["filter"])
add("filter_vertex", "Filter Vertices", "Part_VertexSelection", "filter_vertex", "Allows selecting vertices only (V).", ["vertex filter"])
add("filter_edge", "Filter Edges", "Part_EdgeSelection", "filter_edge", "Allows selecting edges only.", ["edge filter"])
add("filter_face", "Filter Faces", "Part_FaceSelection", "filter_face", "Allows selecting faces only.", ["face filter"])
add("filter_clear", "Clear All Filters", "Part_RemoveSelectionGate", "clear_filters", "Removes the active selection filter.", [])
add("suppress", "Suppress", "FW_Suppress", "delete_face", "Suppresses the selected feature (Roll back/forward the tip).", ["suppress feature"], approx=True)
add("rollback", "Roll Back", "PartDesign_MoveTip", "rebuild", "Rolls the model back to the selected feature.", ["move tip", "rollback", "set tip"])
add("roll_end", "Roll to End", "FW_RollToEnd", "rebuild", "Rolls forward to the end of the FeatureManager tree.", ["roll forward"])
add("body", "Body", "PartDesign_Body", "insert_component", "Creates a new solid body.", ["new body", "solid body"])
add("large_mode", "Large Model Mode", "FW_LargeModelMode", "display_shaded", "Faster display for big parts and assemblies: coarser tessellation, no anti-aliasing, no view animations (like Large Assembly Mode).", ["large assembly mode", "large design review", "performance", "speed"])
add("reset_settings", "Reset FreeWorks Settings", "FW_ResetSettings", "options", "Restores the FreeWorks defaults (layout, colours, options). Projects are not affected.", ["reset", "restore defaults"])
add("magnify", "Magnified Selection", "FW_Magnify", "zoom_in_out", "Shows a magnifying glass at the pointer (G).", ["magnifier", "magnifying glass"])
add("shortcut_bar", "Shortcut Bar", "FW_ShortcutBar", "options", "Shows the context shortcut bar at the pointer (S).", ["s key"])


def first_existing(entry):
    """Name of the first command in entry['cmd'] that exists, or None."""
    import FreeCADGui as Gui
    for c in entry["cmd"]:
        if c.startswith("FW_"):
            return c
        if Gui.Command.get(c) is not None:
            return c
    return None


# ------------------------------------------------------------------ layouts
# Groups: ("L", key)                    large button, text below
#         ("L", key, [flyout keys])     large button with flyout arrow
#         ("S", [k1, k2, k3])            stacked small buttons with text
#         ("|",)                        separator
TABS = {
    "part": [
        ("Features", [
            ("L", "extrude"), ("L", "revolve"), ("S", ["sweep", "loft", "boundary"]), ("|",),
            ("L", "extrude_cut"), ("L", "hole_wizard"), ("L", "revolve_cut"), ("S", ["sweep_cut", "loft_cut", "helix_cut"]), ("|",),
            ("L", "fillet", ["fillet", "chamfer"]), ("L", "lpattern", ["lpattern", "cpattern", "mirror", "multipattern"]),
            ("S", ["draft", "shell", "check"]), ("S", ["mirror", "combine", "intersect"]), ("|",),
            ("L", "plane", ["plane", "axis", "point", "csys", "shapebinder"]), ("L", "helix_boss", ["helix_boss", "helix_cut"]),
            ("S", ["split", "move_copy_body", "scale"]), ("|",), ("L", "rebuild"),
        ]),
        ("Sketch", "sketch"),
        ("Surfaces", [
            ("L", "s_extrude"), ("L", "s_revolve"), ("L", "s_sweep"), ("L", "s_loft"), ("L", "s_boundary"), ("L", "s_fill"), ("|",),
            ("S", ["s_ruled", "s_offset", "s_extend"]), ("S", ["s_knit", "s_thicken", "s_blend"]), ("|",), ("L", "delete_face"),
        ]),
        ("Sheet Metal", [
            ("L", "sm_base"), ("L", "sm_convert"), ("L", "sm_edge"), ("L", "sm_hem"), ("L", "sm_sketched_bend"), ("S", ["sm_bend", "sm_relief", "sm_rip"]),
            ("S", ["sm_extend", "sm_cutout"]), ("|",), ("L", "sm_forming"), ("L", "sm_sketch_on"), ("L", "sm_unfold"),
        ]),
        ("Evaluate", [
            ("L", "measure"), ("L", "mass_props"), ("L", "section_props"), ("|",), ("L", "interference"), ("L", "check"),
            ("L", "curvature"), ("L", "zebra"), ("L", "draft_analysis"), ("S", ["bbox", "section_view", "section_cut"]), ("|",), ("L", "clarify"),
        ]),
    ],
    "sketch": [
        ("Sketch", "sketch"),
        ("Features", "part:Features"),
        ("Evaluate", "part:Evaluate"),
    ],
    "assembly": [
        ("Assembly", [
            ("L", "insert_component", ["insert_component", "new_component", "fasteners"]), ("L", "mate"),
            ("S", ["fix_component", "move_component", "solve"]), ("|",),
            ("L", "exploded_view"), ("L", "asm_bom"), ("L", "motion"), ("|",),
            ("L", "interference"), ("L", "mass_props"), ("L", "measure"),
        ]),
        ("Mates", [
            ("L", "mate_fixed"), ("L", "mate_revolute"), ("L", "mate_concentric"), ("L", "mate_distance"), ("|",),
            ("S", ["mate_parallel", "mate_perpendicular", "mate_angle"]), ("S", ["mate_slider", "mate_ball"]), ("|",),
            ("S", ["mate_gear", "mate_rack", "mate_screw"]), ("S", ["mate_belt"]),
        ]),
        ("Sketch", "sketch"),
        ("Evaluate", "part:Evaluate"),
    ],
    "drawing": [
        ("View Layout", [
            ("L", "std3view"), ("L", "model_view"), ("L", "projected_view"), ("|",),
            ("L", "section_dview"), ("L", "detail_view"), ("S", ["aligned_section", "broken_view", "crop_view"]), ("|",),
            ("L", "new_sheet"), ("L", "sheet_format"),
        ]),
        ("Annotation", [
            ("L", "d_smart_dim", ["d_smart_dim", "d_hdim", "d_vdim", "hole_fit"]), ("L", "note"), ("L", "balloon"), ("|",),
            ("S", ["center_mark", "centerline_d", "centerline_2l"]), ("S", ["surface_finish", "weld_symbol", "leader"]), ("|",),
            ("L", "hatch"), ("L", "d_bom"), ("L", "table"),
        ]),
        ("Sheet Format", [("L", "sheet_format"), ("L", "new_sheet"), ("L", "export_dxf"), ("L", "print_pdf")]),
    ],
}

SKETCH_TAB = [
    ("L", "sketch"), ("L", "smart_dim"), ("|",),
    ("L", "line", ["line", "line_single", "centerline"]),
    ("L", "corner_rect", ["corner_rect", "center_rect", "rounded_rect", "parallelogram"]),
    ("L", "slot", ["slot", "arc_slot"]),
    ("L", "circle", ["circle", "perimeter_circle"]),
    ("L", "center_arc", ["center_arc", "tangent_arc", "3pt_arc"]),
    ("L", "polygon"), ("L", "spline", ["spline", "style_spline"]),
    ("S", ["ellipse", "partial_ellipse", "skpoint"]), ("S", ["sk_fillet", "sk_chamfer", "text"]), ("|",),
    ("L", "trim", ["trim", "extend", "split_ent"]), ("L", "convert", ["convert", "intersection", "carbon"]), ("L", "offset"),
    ("S", ["sk_mirror", "sk_lpattern", "sk_cpattern"]), ("S", ["sk_move", "sk_rotate", "sk_scale"]), ("|",),
    ("L", "relations", ["rel_coincident", "rel_horizontal", "rel_vertical", "rel_parallel", "rel_perpendicular", "rel_tangent",
                        "rel_equal", "rel_symmetric", "rel_fix", "rel_lock"]),
    ("S", ["construction", "repair_sketch", "delete_relations"]), ("S", ["grid", "snap", "normal_sketch"]),
]

# Mouse gestures: 8 directions, N first then clockwise (N, NE, E, SE, S, SW, W, NW)
GESTURES = {
    "part": ["v_top", "v_iso", "v_right", "normal_to", "v_bottom", "zoom_fit", "v_left", "v_front"],
    "sketch": ["line", "corner_rect", "circle", "center_arc", "trim", "exit_sketch", "smart_dim", "centerline"],
    "assembly": ["v_top", "insert_component", "mate", "move_component", "v_bottom", "zoom_fit", "v_left", "v_iso"],
    "drawing": ["note", "model_view", "section_dview", "detail_view", "balloon", "center_mark", "d_smart_dim", "projected_view"],
}

# Shortcut bar (S key)
SHORTCUT_BAR = {
    "part": ["sketch", "extrude", "extrude_cut", "revolve", "fillet", "chamfer", "hole_wizard", "lpattern", "cpattern", "mirror", "shell", "plane", "axis", "measure", "rebuild"],
    "sketch": ["line", "centerline", "corner_rect", "circle", "center_arc", "slot", "spline", "smart_dim", "trim", "extend", "offset", "convert", "sk_mirror", "construction", "sk_fillet", "exit_sketch"],
    "assembly": ["insert_component", "mate", "move_component", "fix_component", "exploded_view", "interference", "measure", "rebuild"],
    "drawing": ["model_view", "projected_view", "section_dview", "detail_view", "d_smart_dim", "note", "balloon", "center_mark", "centerline_d"],
}

# Global rename of FreeCAD commands to SolidWorks wording (menus, tooltips,
# Customize dialog and FreeCAD's own toolbars).  Built from the catalog plus
# a few extras that are not CommandManager buttons.
EXTRA_RENAMES = {
    "PartDesign_Pad": ("Extruded Boss/Base", "extrude_boss"),
    "PartDesign_Pocket": ("Extruded Cut", "extrude_cut"),
    "PartDesign_NewSketch": ("Sketch", "sketch"),
    "Sketcher_NewSketch": ("Sketch", "sketch"),
    "Sketcher_LeaveSketch": ("Exit Sketch", "exit_sketch"),
    "Std_Refresh": ("Rebuild", "rebuild"),
    "Std_ViewFront": ("Front", None), "Std_ViewRear": ("Back", None), "Std_ViewLeft": ("Left", None),
    "Std_ViewRight": ("Right", None), "Std_ViewTop": ("Top", None), "Std_ViewBottom": ("Bottom", None),
    "Std_ViewIsometric": ("Isometric", None), "Std_AlignToSelection": ("Normal To", "normal_to"),
    "Std_ViewFitAll": ("Zoom to Fit", "zoom_fit"), "Std_ViewFitSelection": ("Zoom to Selection", "zoom_fit"),
    "Std_ViewBoxZoom": ("Zoom to Area", "zoom_area"), "Std_DlgPreferences": ("Options...", "options"),
    "Std_ToggleClipPlane": ("Section View", "section_view"), "Std_SetAppearance": ("Appearance...", "appearance"),
    "PartDesign_MoveTip": ("Roll Back", None), "PartDesign_Body": ("Insert Body", None),
    "Assembly_InsertLink": ("Insert Components", "insert_component"),
    "TechDraw_PageDefault": ("New Drawing Sheet", "new_drawing"),
}

# FreeCAD pixmap names (used by the FeatureManager tree for feature icons)
# that are re-skinned with FreeWorks icons.
PIXMAP_OVERRIDES = {
    "PartDesign_Pad": "extrude_boss", "PartDesign_Pocket": "extrude_cut", "PartDesign_Revolution": "revolve_boss",
    "PartDesign_Groove": "revolve_cut", "PartDesign_AdditivePipe": "sweep_boss", "PartDesign_SubtractivePipe": "sweep_cut",
    "PartDesign_AdditiveLoft": "loft_boss", "PartDesign_SubtractiveLoft": "loft_cut", "PartDesign_AdditiveHelix": "helix_boss",
    "PartDesign_SubtractiveHelix": "helix_cut", "PartDesign_Fillet": "fillet", "PartDesign_Chamfer": "chamfer",
    "PartDesign_Thickness": "shell", "PartDesign_Draft": "draft", "PartDesign_Hole": "hole_wizard",
    "PartDesign_LinearPattern": "linear_pattern", "PartDesign_PolarPattern": "circular_pattern", "PartDesign_Mirrored": "mirror",
    "PartDesign_MultiTransform": "multi_transform", "PartDesign_Boolean": "combine", "PartDesign_Plane": "plane",
    "PartDesign_Line": "axis", "PartDesign_Point": "point", "PartDesign_CoordinateSystem": "coordinate_system",
    "Sketcher_Sketch": "sketch", "Sketcher_NewSketch": "sketch", "Sketcher_LeaveSketch": "exit_sketch",
    "Std_Refresh": "rebuild", "Std_ViewFitAll": "zoom_fit", "Std_ViewBoxZoom": "zoom_area", "Std_ToggleClipPlane": "section_view",
    "Std_Measure": "measure", "umf-measurement": "measure", "Assembly_InsertLink": "insert_component",
    "Assembly_CreateJointFixed": "mate_fixed", "TechDraw_View": "model_view", "TechDraw_ProjectionGroup": "standard_3view",
    "TechDraw_SectionView": "section_drawing_view", "TechDraw_DetailView": "detail_view", "TechDraw_Balloon": "balloon",
    "Sketcher_Dimension": "smart_dimension", "Sketcher_CreatePolyline": "line", "Sketcher_CreateLine": "line",
    "Sketcher_CreateRectangle": "corner_rectangle", "Sketcher_CreateRectangle_Center": "center_rectangle",
    "Sketcher_CreateCircle": "circle", "Sketcher_Create3PointCircle": "perimeter_circle", "Sketcher_CreateArc": "arc",
    "Sketcher_Create3PointArc": "three_point_arc", "Sketcher_CreateSlot": "slot_rectangle", "Sketcher_Trimming": "trim",
    "Sketcher_Extend": "extend", "Sketcher_Offset": "offset_entities", "Sketcher_Projection": "convert_entities",
    "Sketcher_Symmetry": "mirror_entities", "Sketcher_ToggleConstruction": "construction",
    "Sketcher_CreateFillet": "sketch_fillet", "Sketcher_CreateChamfer": "sketch_chamfer", "Sketcher_CreateBSplineByInterpolation": "spline",
    "Sketcher_CreateRegularPolygon": "polygon", "Sketcher_CreatePoint": "sketch_point",
}


def search_index():
    """[(text, key)] used by command search, includes aliases."""
    out = []
    for k, e in C.items():
        out.append((e["label"].lower(), k))
        for a in e["aliases"]:
            out.append((a.lower(), k))
        for c in e["cmd"]:
            out.append((c.lower().replace("_", " "), k))
    return out
