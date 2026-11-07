"""Equations, Global Variables and Dimensions - the SOLIDWORKS Equations dialog on FreeCAD expressions.

SOLIDWORKS syntax is accepted and shown:   "D1@Sketch1" = "A" * 2 + 5
FreeCAD stores it as an expression:         <<Sketch1>>.Constraints.D1 = GlobalVariables.A * 2 + 5

* Global variables live in one App::VarSet named "GlobalVariables" (label "Global Variables").
* "D<n>@<Sketch>" is the n-th driving dimension of the sketch (SOLIDWORKS numbering); FreeWorks names
  that constraint "D<n>" the first time an equation uses it.
* "D<n>@<Feature>" maps to the feature's own value (Boss-Extrude: D1 Length, D2 Length2; Revolve:
  D1 Angle; Fillet: D1 Radius; Chamfer: D1 Size; Hole: D1 Diameter, D2 Depth; patterns: D1 Length or
  Angle, D2 Occurrences); "<Property>@<Feature>" uses the property directly.
"""
import re

import FreeCAD as App

VARSET = "GlobalVariables"
VARSET_LABEL = "Global Variables"
PFX = "GV_"     # stored as GV_A: FreeCAD's expression parser reads a bare "A" as the unit ampere
DIMENSIONAL = ("Distance", "DistanceX", "DistanceY", "Radius", "Diameter", "Angle")
FEATURE_DIMS = {
    "PartDesign::Pad": ["Length", "Length2"], "PartDesign::Pocket": ["Length", "Length2"],
    "PartDesign::Revolution": ["Angle", "Angle2"], "PartDesign::Groove": ["Angle", "Angle2"],
    "PartDesign::Fillet": ["Radius"], "PartDesign::Chamfer": ["Size", "Size2"],
    "PartDesign::Thickness": ["Value"], "PartDesign::Draft": ["Angle"],
    "PartDesign::Hole": ["Diameter", "Depth"],
    "PartDesign::LinearPattern": ["Length", "Occurrences"], "PartDesign::PolarPattern": ["Angle", "Occurrences"],
    "PartDesign::AdditiveBox": ["Length", "Width", "Height"], "PartDesign::AdditiveCylinder": ["Radius", "Height"],
}
_SW_REF = re.compile(r'"([^"@]+)(?:@([^"]+))?"')


# ------------------------------------------------------------------ global variables
def varset(doc, create=False):
    o = doc.getObject(VARSET)
    if o is None and create:
        o = doc.addObject("App::VarSet", VARSET)
        o.Label = VARSET_LABEL
    return o


def variables(doc):
    """[(name, value, expression or None)]"""
    vs = varset(doc)
    if vs is None:
        return []
    ex = dict(vs.ExpressionEngine)
    out = []
    for p in vs.PropertiesList:
        if vs.getGroupOfProperty(p) != "Variables" or not p.startswith(PFX):
            continue
        v = getattr(vs, p)
        out.append((p[len(PFX):], float(getattr(v, "Value", v)), ex.get(p)))
    return out


def set_variable(doc, name, text):
    """Create/update a global variable from a number or an (SOLIDWORKS-style) expression."""
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError("Variable names use letters, digits and _ and start with a letter: %r" % name)
    vs = varset(doc, create=True)
    prop = PFX + name
    if not hasattr(vs, prop):
        vs.addProperty("App::PropertyFloat", prop, "Variables", "Global variable %s (FreeWorks Equations)" % name)
    text = text.strip().lstrip("=").strip()
    try:
        val = float(text)
    except ValueError:
        vs.setExpression(prop, to_freecad(doc, text))
        return
    if prop in dict(vs.ExpressionEngine):
        vs.setExpression(prop, None)
    setattr(vs, prop, val)


def delete_variable(doc, name):
    vs = varset(doc)
    prop = PFX + name
    if vs is not None and hasattr(vs, prop):
        if prop in dict(vs.ExpressionEngine):
            vs.setExpression(prop, None)
        vs.removeProperty(prop)


# ------------------------------------------------------------------ dimension names
def _by_label(doc, label):
    objs = doc.getObjectsByLabel(label)
    return objs[0] if objs else doc.getObject(label)


def sketch_dims(sk):
    """Indices of the driving dimensional constraints, in SOLIDWORKS D1, D2 ... order."""
    return [i for i, c in enumerate(sk.Constraints) if c.Type in DIMENSIONAL and c.Driving]


def dim_path(doc, name, owner_label):
    """'D1', 'Sketch1' -> (object, property path) for setExpression / reading."""
    o = _by_label(doc, owner_label)
    if o is None:
        raise ValueError("No feature or sketch called %r" % owner_label)
    m = re.match(r"^D(\d+)$", name)
    if o.isDerivedFrom("Sketcher::SketchObject"):
        if not m:
            raise ValueError("Sketch dimensions are named D1, D2 ...: %r" % name)
        n = int(m.group(1))
        for i, c in enumerate(o.Constraints):
            if c.Name == name:
                return o, "Constraints.%s" % name
        dims = sketch_dims(o)
        if n < 1 or n > len(dims):
            raise ValueError("%s has %d driving dimensions" % (owner_label, len(dims)))
        idx = dims[n - 1]
        if o.Constraints[idx].Name:
            return o, "Constraints.%s" % o.Constraints[idx].Name
        o.renameConstraint(idx, name)
        return o, "Constraints.%s" % name
    if m:
        props = FEATURE_DIMS.get(o.TypeId, [])
        n = int(m.group(1))
        if n < 1 or n > len(props):
            raise ValueError("%s has no %s" % (owner_label, name))
        return o, props[n - 1]
    if name not in o.PropertiesList:
        raise ValueError("%s has no property %r" % (owner_label, name))
    return o, name


# ------------------------------------------------------------------ syntax
def to_freecad(doc, expr):
    """SOLIDWORKS-style expression -> FreeCAD expression."""
    def sub(m):
        name, owner = m.group(1), m.group(2)
        if owner is None:
            vs = varset(doc)
            if vs is not None and hasattr(vs, PFX + name):
                return "%s.%s%s" % (VARSET, PFX, name)
            raise ValueError("Unknown global variable %r" % name)
        o, path = dim_path(doc, name, owner)
        return "<<%s>>.%s" % (o.Label, path)
    return _SW_REF.sub(sub, expr.strip().lstrip("=").strip())


_FC_VAR = re.compile(r"(?:\b%s\.|<<%s>>\.)?\b%s([A-Za-z_]\w*)" % (VARSET, VARSET_LABEL, PFX))
_FC_REF = re.compile(r"<<([^>]+)>>\.(Constraints\.)?([A-Za-z_]\w*)")


def to_solidworks(expr):
    """FreeCAD expression -> SOLIDWORKS-style text for display."""
    e = _FC_VAR.sub(lambda m: '"%s"' % m.group(1), expr)
    return _FC_REF.sub(lambda m: '"%s@%s"' % (m.group(3), m.group(1)), e)


# ------------------------------------------------------------------ equations
def equations(doc):
    """[(sw name, object, property path, expression, value)] for every expression in the document
    except global variables (shown separately)."""
    out = []
    for o in doc.Objects:
        if o.Name == VARSET:
            continue
        for path, ex in o.ExpressionEngine:
            path = path.lstrip(".")          # FreeCAD stores ".Constraints.D1"
            out.append((sw_name(o, path), o, path, ex, read(o, path)))
    return out


def sw_name(o, path):
    if path.startswith("Constraints."):
        return "%s@%s" % (path.split(".", 1)[1], o.Label)
    props = FEATURE_DIMS.get(o.TypeId, [])
    if path in props:
        return "D%d@%s" % (props.index(path) + 1, o.Label)
    return "%s@%s" % (path, o.Label)


def read(o, path):
    try:
        if path.startswith("Constraints."):
            nm = path.split(".", 1)[1]
            for c in o.Constraints:
                if c.Name == nm:
                    v = c.Value
                    if c.Type == "Angle":
                        import math
                        return math.degrees(v)
                    return v
            return None
        v = getattr(o, path)
        return float(getattr(v, "Value", v))
    except Exception:
        return None


def set_equation(doc, target, expr):
    """target 'D1@Sketch1' / 'Length@Boss-Extrude1'; expr SOLIDWORKS or FreeCAD syntax (None = remove)."""
    t = target.strip().strip('"')
    if "@" not in t:
        raise ValueError('Use the SOLIDWORKS form "D1@Sketch1" for the dimension')
    name, owner = t.split("@", 1)
    o, path = dim_path(doc, name, owner)
    if expr:
        o.setExpression(path, to_freecad(doc, expr))
    elif path in dict(o.ExpressionEngine):
        o.setExpression(path, None)
    return o, path


def dimension_names(doc):
    """Every dimension an equation can drive, SOLIDWORKS-named (for the Add equation picker)."""
    out = []
    for o in doc.Objects:
        if o.isDerivedFrom("Sketcher::SketchObject"):
            for n in range(1, len(sketch_dims(o)) + 1):
                out.append("D%d@%s" % (n, o.Label))
        for n, p in enumerate(FEATURE_DIMS.get(o.TypeId, []), 1):
            if p in o.PropertiesList:
                out.append("D%d@%s" % (n, o.Label))
    return out
