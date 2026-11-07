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
ADVANCED = ["width", "limit_distance", "limit_angle"]
MECHANICAL = ["hinge", "gear", "rack_pinion", "screw"]
LABEL = {"coincident": "Coincident", "parallel": "Parallel", "perpendicular": "Perpendicular",
         "tangent": "Tangent", "concentric": "Concentric", "lock": "Lock", "distance": "Distance",
         "angle": "Angle", "hinge": "Hinge", "gear": "Gear", "rack_pinion": "RackPinion", "screw": "Screw",
         "width": "Width", "limit_distance": "LimitDistance", "limit_angle": "LimitAngle"}
JOINT = {"coincident": "Distance", "tangent": "Distance", "distance": "Distance", "concentric": "Cylindrical",
         "parallel": "Parallel", "perpendicular": "Perpendicular", "angle": "Angle", "lock": "Fixed",
         "hinge": "Revolute", "gear": "Gears", "rack_pinion": "RackPinion", "screw": "Screw", "width": "Distance"}
FLIPPABLE = {"coincident", "tangent", "distance", "concentric", "parallel", "hinge", "gear"}
VALUE = {"distance": ("Distance", " mm", 10.0), "angle": ("Angle", " deg", 90.0), "gear": ("Ratio", "", 1.0),
         "rack_pinion": ("Pinion pitch diameter", " mm", 20.0), "screw": ("Distance/revolution", " mm", 1.0)}
LIMIT_JOINTS = {"limit_distance": ("Cylindrical", "Slider"), "limit_angle": ("Revolute", "Cylindrical")}
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
        out += ["hinge", "gear", "screw"]
    if ks & {"cylinder", "circle"} and ks & {"line", "plane"}:
        out.append("rack_pinion")
    return [t for t in STANDARD + ADVANCED + MECHANICAL if t in out]


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


# ------------------------------------------------------------------ geometry helpers
def radius(ref):
    s = element(ref)
    try:
        if s.ShapeType == "Edge":
            return float(s.Curve.Radius)
        if s.ShapeType == "Face":
            return float(s.Surface.Radius)
    except Exception:
        pass
    return None


def point(ref):
    s = element(ref)
    if s is None:
        return ref[0].Placement.Base
    if s.ShapeType == "Vertex":
        return s.Point
    return s.CenterOfMass if hasattr(s, "CenterOfMass") else s.BoundBox.Center


def normal(ref):
    s = element(ref)
    if s is None or s.ShapeType != "Face":
        return None
    u0, u1, v0, v1 = s.ParameterRange
    return s.normalAt((u0 + u1) / 2.0, (v0 + v1) / 2.0)


def joint_comps(j):
    out = []
    for p in ("Reference1", "Reference2"):
        r = getattr(j, p, None)
        out.append(r[0] if r else None)
    return out


def motion_joint(asm, c1, c2, types):
    """Existing joint between two components whose FreeCAD type is in `types`."""
    _, U = _asm_modules()
    for j in U.getJointGroup(asm).Group:
        if getattr(j, "JointType", "") in types and set(joint_comps(j)) == {c1, c2}:
            return j
    return None


def width_pair(refs):
    """Width mate: refs = [groove face 1, groove face 2, tab face 1, tab face 2].
    Returns (groove face ref, facing tab face ref, gap) so that a Distance joint centres the tab."""
    g1, g2, t1, t2 = refs
    n_g, n_t = normal(g1), normal(t1)
    if n_g is None or n_t is None:
        raise ValueError("Width needs planar faces")
    wg = abs((point(g2) - point(g1)).dot(n_g))
    wt = abs((point(t2) - point(t1)).dot(n_t))
    facing = t1 if n_t.dot(n_g) < 0 else t2
    return g1, facing, (wg - wt) / 2.0


def _signed_angle(a, b, axis):
    import math
    return math.degrees(math.atan2(a.cross(b).dot(axis), a.dot(b)))


def set_limits(asm, mate, refs, vmin, vmax):
    """Limit Distance / Limit Angle: limits on the motion joint between the two components, expressed
    so that SOLIDWORKS' face distance / face angle values apply (FreeCAD enforces them while dragging)."""
    _, U = _asm_modules()
    c1, c2 = component(refs[0]), component(refs[1])
    j = motion_joint(asm, c1, c2, LIMIT_JOINTS[mate])
    if j is None:
        raise ValueError("needs a %s mate between these components first" %
                         (" or ".join({"Cylindrical": "Concentric", "Slider": "Slot", "Revolute": "Hinge"}[t] for t in LIMIT_JOINTS[mate])))
    if joint_comps(j)[0] != c1:
        refs = [refs[1], refs[0]]
    g1 = U.getJcsGlobalPlc(j.Placement1, j.Reference1)
    g2 = U.getJcsGlobalPlc(j.Placement2, j.Reference2)
    z = g1.Rotation.multVec(App.Vector(0, 0, 1))
    if mate == "limit_distance":
        d = (point(refs[1]) - point(refs[0])).dot(z)
        t = (g2.Base - g1.Base).dot(z)
        c = d - t
        lo, hi = (vmin, vmax) if d >= 0 else (-vmax, -vmin)
        j.EnableLengthMin, j.EnableLengthMax = True, True
        j.LengthMin, j.LengthMax = lo - c, hi - c
    else:
        n1, n2 = normal(refs[0]), normal(refs[1])
        if n1 is None or n2 is None:
            raise ValueError("Limit Angle needs two planar faces")
        x = App.Vector(1, 0, 0)
        th = _signed_angle(g1.Rotation.multVec(x), g2.Rotation.multVec(x), z)
        ph = _signed_angle(n1 - z * n1.dot(z), n2 - z * n2.dot(z), z)
        c = ph - th
        j.EnableAngleMin, j.EnableAngleMax = True, True
        j.AngleMin, j.AngleMax = vmin - c, vmax - c
    if not hasattr(j, "LimitMates"):
        j.addProperty("App::PropertyStringList", "LimitMates", "FreeWorks", "SOLIDWORKS limit mates applied")
    j.LimitMates = list(j.LimitMates) + ["%s %g..%g" % (LABEL[mate], vmin, vmax)]
    asm.Document.recompute()
    return j


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


def create(asm, mate, refs, value=None, flip_dim=False, vmin=0.0, vmax=0.0):
    """Create the joint for a SOLIDWORKS mate. Returns the joint object."""
    J, U = _asm_modules()
    if mate in LIMIT_JOINTS:
        return set_limits(asm, mate, refs, vmin, vmax)
    if mate == "width":
        g, t, gap = width_pair(refs)
        refs = [g, t]
        value = gap
    if mate == "rack_pinion" and kind(refs[0]) in ROUND:
        refs = [refs[1], refs[0]]
    jg = U.getJointGroup(asm)
    j = jg.newObject("App::FeaturePython", "Joint")
    J.Joint(j, J.JointTypes.index(JOINT[mate]))
    if App.GuiUp:
        J.ViewProviderJoint(j.ViewObject)
    j.addProperty("App::PropertyString", "MateType", "FreeWorks", "SOLIDWORKS mate type")
    j.MateType = mate
    c1, c2 = component(refs[0]), component(refs[1])
    from .asmtree import clean
    j.Label = "%s (%s,%s)" % (next_label(asm, mate), clean(c1.Label), clean(c2.Label))
    if mate in ("coincident", "tangent"):
        j.Distance = 0.0
    elif mate == "distance":
        j.Distance = -abs(value or 0.0) if flip_dim else abs(value or 0.0)
    elif mate == "angle":
        j.Angle = float(value or 0.0)
    elif mate == "width":
        j.Distance = float(value)
    elif mate == "gear":
        r1 = radius(refs[0]) or 1.0
        ratio = float(value) if value else (radius(refs[1]) or r1) / r1
        j.Distance, j.Distance2 = r1, max(r1 * ratio, 1e-6)
    elif mate == "rack_pinion":
        j.Distance = max(float(value or 2 * (radius(refs[1]) or 10.0)) / 2.0, 1e-6)
    elif mate == "screw":
        j.Distance = float(value or 1.0)
    if mate == "lock":
        # whole-component references, offset = current relative placement -> nothing moves
        p1, p2 = c1.Placement, c2.Placement
        j.Offset2 = p2.inverse().multiply(p1)
        refs = [[c1, ["", ""]], [c2, ["", ""]]]
    j.Proxy.setJointConnectors(j, refs)
    asm.Document.recompute()
    return j


def flip(asm, joint):
    """Mate alignment toggle (Aligned <-> Anti-Aligned); for gears: reverse the rotation direction."""
    if getattr(joint, "JointType", "") in ("Gears", "Belt"):
        joint.Proxy.setJointType(joint, "Belt" if joint.JointType == "Gears" else "Gears")
    else:
        joint.Proxy.flipOnePart(joint)
    solve(asm)


def set_value(asm, joint, mate, value, flip_dim=False):
    if mate == "distance":
        joint.Distance = -abs(value) if flip_dim else abs(value)
    elif mate == "angle":
        joint.Angle = float(value)
    elif mate == "gear":
        joint.Distance2 = max(_num(joint.Distance) * float(value), 1e-6)
    elif mate == "rack_pinion":
        joint.Distance = max(float(value) / 2.0, 1e-6)
    elif mate == "screw":
        joint.Distance = float(value)
    solve(asm)


def _num(q):
    return float(getattr(q, "Value", q))


def default_value(mate, refs):
    if mate == "gear" and len(refs) == 2:
        r1, r2 = radius(refs[0]), radius(refs[1])
        if r1 and r2:
            return r2 / r1
    if mate == "rack_pinion" and len(refs) == 2:
        r = radius(refs[0]) or radius(refs[1])
        if r:
            return 2 * r
    return VALUE.get(mate, ("", "", 0.0))[2]


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
           "Perpendicular": "perpendicular", "Angle": "angle", "Fixed": "lock", "Revolute": "hinge",
           "Gears": "gear", "Belt": "gear", "RackPinion": "rack_pinion", "Screw": "screw"}
    if t == "Distance" and abs(getattr(joint, "Distance", 1.0)) < 1e-9:
        return "coincident"
    return rev.get(t, "")
