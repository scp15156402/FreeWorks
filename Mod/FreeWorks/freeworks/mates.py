"""SOLIDWORKS mates on top of FreeCAD Assembly joints.

SOLIDWORKS mates are geometric (two selections + a relation); FreeCAD joints are kinematic. Verified
in FreeCAD 1.1.4 (dev/DEV_NOTES.md "Assembly joints"):
  Coincident  -> Distance joint, distance 0 (plane/plane face-to-face, point/plane, line/line ...)
  Tangent     -> Distance joint, distance 0 between a round face and a plane/round face
  Concentric  -> Cylindrical joint (cylinders, circular edges, axes)
  Parallel / Perpendicular / Angle / Distance -> joints of the same name
  Lock        -> Fixed joint between the two components with an offset that keeps them where they are
  Hinge       -> Revolute joint
Mate alignment (Aligned / Anti-Aligned) = FreeCAD's "flip one part" on the pending joint.
"""
import FreeCAD as App

from . import log

STANDARD = ["coincident", "parallel", "perpendicular", "tangent", "concentric", "lock", "distance", "angle"]
MECHANICAL = ["hinge"]
LABEL = {"coincident": "Coincident", "parallel": "Parallel", "perpendicular": "Perpendicular",
         "tangent": "Tangent", "concentric": "Concentric", "lock": "Lock", "distance": "Distance",
         "angle": "Angle", "hinge": "Hinge"}
JOINT = {"coincident": "Distance", "tangent": "Distance", "distance": "Distance", "concentric": "Cylindrical",
         "parallel": "Parallel", "perpendicular": "Perpendicular", "angle": "Angle", "lock": "Fixed",
         "hinge": "Revolute"}
FLIPPABLE = {"coincident", "tangent", "distance", "concentric", "parallel", "hinge"}
ROUND = {"cylinder", "circle", "cone", "sphere", "torus"}
AXIAL = {"cylinder", "circle", "cone", "line"}


def _asm_modules():
    import JointObject
    import UtilsAssembly
    return JointObject, UtilsAssembly


# ------------------------------------------------------------------ assembly
def assembly_of(doc=None):
    doc = doc or App.ActiveDocument
    if doc is None:
        return None
    try:
        _, U = _asm_modules()
        a = U.activeAssembly()
        if a is not None and a.Document == doc:
            return a
    except Exception:
        pass
    for o in doc.RootObjects:
        if o.TypeId == "Assembly::AssemblyObject":
            return o
    return None


def activate(asm):
    """Make the assembly the active (edited) one, as FreeCAD's joint tools require."""
    try:
        import FreeCADGui as Gui
        _, U = _asm_modules()
        if U.activeAssembly() is not asm:
            Gui.ActiveDocument.setEdit(asm)
    except Exception as e:
        log("activate assembly: %s" % e)


# ------------------------------------------------------------------ references
def make_ref(asm, root, sub, pos=None):
    """Selection (root object + subname + 3D pick point) -> FreeCAD joint reference or None."""
    _, U = _asm_modules()
    try:
        sub = root.resolveSubElement(sub, True)[2]
    except Exception:
        pass
    sub = U.fixBodyExtraFeatureInSub(root.Document.Name, sub)
    comp, new_sub = U.getComponentReference(asm, root, sub)
    if not comp:
        return None
    ref = [comp, [new_sub]]
    if pos is not None:
        v = U.findElementClosestVertex(ref, App.Vector(*pos) if not isinstance(pos, App.Vector) else pos)
        if v:
            ref = U.addVertexToReference(ref, v)
    if len(ref[1]) < 2:
        ref = [comp, [new_sub, new_sub]]
    return ref


def component(ref):
    return ref[0] if ref else None


def element(ref):
    """The selected sub-shape (Face/Edge/Vertex) in document coordinates, or None."""
    try:
        import Part
        s = Part.getShape(ref[0], ref[1][0], needSubElement=True)
        return s if s is not None and not s.isNull() else None
    except Exception:
        return None


def kind(ref):
    """plane | cylinder | cone | sphere | torus | surface | line | circle | curve | vertex | part"""
    s = element(ref)
    if s is None:
        return "part"
    import Part
    t = s.ShapeType
    if t == "Vertex":
        return "vertex"
    if t == "Edge":
        c = s.Curve
        if isinstance(c, (Part.Line, Part.LineSegment)):
            return "line"
        if isinstance(c, (Part.Circle, Part.ArcOfCircle)):
            return "circle"
        return "curve"
    if t == "Face":
        f = s.Surface
        for cls, name in ((Part.Plane, "plane"), (Part.Cylinder, "cylinder"), (Part.Cone, "cone"),
                          (Part.Sphere, "sphere"), (Part.Toroid, "torus")):
            if isinstance(f, cls):
                return name
        try:
            if s.findPlane() is not None:
                return "plane"
        except Exception:
            pass
        return "surface"
    return "part"


def allowed(k1, k2):
    """Mate types that make sense for two selected entity kinds (SOLIDWORKS enables the same idea)."""
    ks = {k1, k2}
    out = ["coincident", "distance", "lock"]
    if ks <= {"plane", "line", "cylinder", "circle", "cone"}:
        out += ["parallel", "perpendicular"]
    if ks <= {"plane", "line"}:
        out.append("angle")
    if ks & ROUND and ks <= ROUND | {"plane", "line", "vertex"}:
        out.append("tangent")
    if ks <= AXIAL | {"sphere", "vertex"} and ks & (AXIAL | {"sphere"}):
        out.append("concentric")
    if ks <= {"cylinder", "circle"}:
        out.append("hinge")
    return [t for t in STANDARD + MECHANICAL if t in out]


def suggest(k1, k2):
    ks = {k1, k2}
    if "vertex" in ks:
        return "coincident"
    if ks <= {"cylinder", "circle", "cone"} or (ks & {"cylinder", "circle", "cone"} and "line" in ks):
        return "concentric"
    if ks & ROUND and "plane" in ks:
        return "tangent"
    if ks == {"sphere"}:
        return "concentric"
    return "coincident"


# ------------------------------------------------------------------ joints
def next_label(asm, mate):
    _, U = _asm_modules()
    base = LABEL[mate]
    n = 0
    for j in U.getJointGroup(asm).Group:
        lab = j.Label
        if lab.startswith(base):
            tail = lab[len(base):].split(" ")[0]
            if tail.isdigit():
                n = max(n, int(tail))
    return "%s%d" % (base, n + 1)


def create(asm, mate, refs, value=None, flip_dim=False):
    """Create the joint for a SOLIDWORKS mate. Returns the joint object."""
    J, U = _asm_modules()
    jg = U.getJointGroup(asm)
    j = jg.newObject("App::FeaturePython", "Joint")
    J.Joint(j, J.JointTypes.index(JOINT[mate]))
    if App.GuiUp:
        J.ViewProviderJoint(j.ViewObject)
    j.addProperty("App::PropertyString", "MateType", "FreeWorks", "SOLIDWORKS mate type")
    j.MateType = mate
    c1, c2 = component(refs[0]), component(refs[1])
    j.Label = "%s (%s,%s)" % (next_label(asm, mate), c1.Label, c2.Label)
    if mate in ("coincident", "tangent"):
        j.Distance = 0.0
    elif mate == "distance":
        j.Distance = -abs(value or 0.0) if flip_dim else abs(value or 0.0)
    elif mate == "angle":
        j.Angle = float(value or 0.0)
    if mate == "lock":
        # whole-component references, offset = current relative placement -> nothing moves
        p1, p2 = c1.Placement, c2.Placement
        j.Offset2 = p2.inverse().multiply(p1)
        refs = [[c1, ["", ""]], [c2, ["", ""]]]
    j.Proxy.setJointConnectors(j, refs)
    asm.Document.recompute()
    return j


def flip(asm, joint):
    """Mate alignment toggle (Aligned <-> Anti-Aligned)."""
    joint.Proxy.flipOnePart(joint)
    solve(asm)


def set_value(asm, joint, mate, value, flip_dim=False):
    if mate == "distance":
        joint.Distance = -abs(value) if flip_dim else abs(value)
    elif mate == "angle":
        joint.Angle = float(value)
    solve(asm)


def solve(asm):
    try:
        asm.solve()
    except Exception as e:
        log("assembly solve: %s" % e)
    asm.Document.recompute()


def mate_of(joint):
    """SOLIDWORKS mate type of a joint (MateType property, else derived from the FreeCAD joint type)."""
    m = getattr(joint, "MateType", "")
    if m:
        return m
    t = getattr(joint, "JointType", "")
    rev = {"Distance": "distance", "Cylindrical": "concentric", "Parallel": "parallel",
           "Perpendicular": "perpendicular", "Angle": "angle", "Fixed": "lock", "Revolute": "hinge"}
    if t == "Distance" and abs(getattr(joint, "Distance", 1.0)) < 1e-9:
        return "coincident"
    return rev.get(t, "")
