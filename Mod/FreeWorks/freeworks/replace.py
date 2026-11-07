"""Replace Components (SOLIDWORKS: Assembly > Replace Components) with mated-entity re-attachment.

The component (an App::Link) is pointed at the new part. Every mate that referenced a face, edge or
vertex of the old part is re-attached to the most similar entity of the new part: same kind of
geometry (plane / cylinder / line / circle / point), nearest position and orientation, closest
radius. Mates that find no match are reported, like SOLIDWORKS' "Mated Entities" list.
"""
import os

import FreeCAD as App

from . import log
from . import mates


def _sig(shape):
    """Geometry signature of a sub-shape (in assembly coordinates)."""
    import Part
    t = shape.ShapeType
    if t == "Vertex":
        return ("vertex", shape.Point, None, 0.0)
    if t == "Edge":
        c = shape.Curve
        if isinstance(c, (Part.Circle, Part.ArcOfCircle)):
            return ("circle", c.Center, c.Axis, c.Radius)
        if isinstance(c, (Part.Line, Part.LineSegment)):
            d = shape.Vertexes[-1].Point - shape.Vertexes[0].Point
            return ("line", shape.CenterOfMass, d.normalize() if d.Length else d, 0.0)
        return ("edge", shape.CenterOfMass, None, 0.0)
    if t == "Face":
        s = shape.Surface
        u0, u1, v0, v1 = shape.ParameterRange
        n = shape.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
        if isinstance(s, Part.Plane):
            return ("plane", shape.CenterOfMass, n, 0.0)
        if isinstance(s, Part.Cylinder):
            return ("cylinder", s.Center, s.Axis, s.Radius)
        return ("face", shape.CenterOfMass, n, 0.0)
    return ("other", App.Vector(), None, 0.0)


def _score(a, b):
    if a[0] != b[0]:
        return None
    s = (a[1] - b[1]).Length
    if a[2] is not None and b[2] is not None and a[2].Length and b[2].Length:
        cosang = abs(a[2].dot(b[2]))
        s += 50.0 * (1.0 - min(1.0, cosang))
        if a[0] == "plane" and a[2].dot(b[2]) < 0:
            s += 25.0                          # a planar face's normal flipped: different face
    s += 5.0 * abs(a[3] - b[3])
    return s


def _elements(shape, kind):
    if kind == "vertex":
        return [("Vertex%d" % (i + 1), v) for i, v in enumerate(shape.Vertexes)]
    if kind in ("circle", "line", "edge"):
        return [("Edge%d" % (i + 1), e) for i, e in enumerate(shape.Edges)]
    return [("Face%d" % (i + 1), f) for i, f in enumerate(shape.Faces)]


def _prefix_for(target):
    """Subname prefix inside a component for its shape elements (Body -> its Tip feature)."""
    if target.isDerivedFrom("PartDesign::Body") and target.Tip is not None:
        return target.Tip.Name + "."
    return ""


def _joint_refs(asm, comp):
    out = []
    for j in mates._asm_modules()[1].getJointGroup(asm).Group:
        for p in ("Reference1", "Reference2"):
            r = getattr(j, p, None)
            if r and r[0] == comp:
                out.append((j, p, [r[0], list(r[1])]))
    return out


def replace(asm, comp, new_target):
    """Point component `comp` at `new_target` and re-attach mates. Returns (ok, failed) lists."""
    import Part
    refs = _joint_refs(asm, comp)
    sigs = []
    for j, p, r in refs:
        sub = r[1][0] if r[1] else ""
        el = sub.split(".")[-1] if sub else ""
        if not el:
            sigs.append(None)
            continue
        try:
            sigs.append(_sig(Part.getShape(comp, sub, needSubElement=True)))
        except Exception:
            sigs.append(None)
    comp.LinkedObject = new_target
    asm.Document.recompute()
    shape = Part.getShape(comp, "", needSubElement=False, transform=True)
    prefix = _prefix_for(new_target)
    ok, failed = [], []
    new_refs = {}
    for (j, p, r), sig in zip(refs, sigs):
        if sig is None:
            new_refs.setdefault(j, {})[p] = [comp, list(r[1])]
            continue
        best, best_s = None, None
        for name, el in _elements(shape, sig[0]):
            try:
                sc = _score(sig, _sig(el))
            except Exception:
                continue
            if sc is not None and (best_s is None or sc < best_s):
                best, best_s = name, sc
        if best is None:
            failed.append(j.Label)
            continue
        new_sub = prefix + best
        new_refs.setdefault(j, {})[p] = [comp, [new_sub, new_sub]]     # element itself as JCS anchor
        ok.append(j.Label)
    for j, d in new_refs.items():
        r1 = d.get("Reference1") or [j.Reference1[0], list(j.Reference1[1])]
        r2 = d.get("Reference2") or [j.Reference2[0], list(j.Reference2[1])]
        try:
            j.Proxy.setJointConnectors(j, [r1, r2])
        except Exception as e:
            log("re-attach %s: %s" % (j.Label, e))
            failed.append(j.Label)
    try:
        asm.solve()
    except Exception:
        pass
    asm.Document.recompute()
    try:
        from . import asmtree
        base = new_target.Document.Label if new_target.Document is not comp.Document else new_target.Label
        num = asmtree._INST.match(asmtree.clean(comp.Label))
        fixed = comp.Label.startswith(asmtree.FIXED)
        comp.Label = "%s%s<%s>" % (asmtree.FIXED if fixed else "", base, num.group(2) if num else "1")
    except Exception:
        pass
    return sorted(set(ok) - set(failed)), sorted(set(failed))


def main_object(doc):
    """The part/assembly object a file stands for (single root Body / App::Part / Assembly)."""
    roots = [o for o in doc.RootObjects if o.TypeId in ("PartDesign::Body", "App::Part", "Assembly::AssemblyObject")]
    if not roots:
        roots = [o for o in doc.RootObjects if o.isDerivedFrom("Part::Feature")]
    return roots[0] if roots else None


def start():
    """FW_ReplaceComponents: pick the new part file, replace the selected component(s)."""
    import FreeCADGui as Gui
    from PySide import QtWidgets
    doc = App.ActiveDocument
    asm = mates.assembly_of(doc)
    comps = []
    for s in Gui.Selection.getSelectionEx("", 0):
        for n in (s.SubElementNames or [""]):
            ref = mates.make_ref(asm, s.Object, n, None) if asm else None
            c = mates.component(ref) if ref else (s.Object if s.Object.TypeId == "App::Link" else None)
            if c is not None and c not in comps:
                comps.append(c)
    if asm is None or not comps:
        QtWidgets.QMessageBox.information(Gui.getMainWindow(), "Replace Components",
                                          "Select the component(s) to replace in an assembly first.")
        return
    from . import prefs
    path, _ = QtWidgets.QFileDialog.getOpenFileName(Gui.getMainWindow(), "Replace with", prefs.projects_dir(),
                                                    "FreeCAD parts (*.FCStd)")
    if not path:
        return
    names = {App.getDocument(n).FileName: n for n in App.listDocuments()}
    nd = App.getDocument(names[path]) if path in names else App.openDocument(path, True)
    tgt = main_object(nd)
    if tgt is None:
        QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "Replace Components", "No part found in %s." % os.path.basename(path))
        return
    doc.openTransaction("Replace Components")
    ok_all, bad_all = [], []
    try:
        for c in comps:
            ok, bad = replace(asm, c, tgt)
            ok_all += ok
            bad_all += bad
    finally:
        doc.commitTransaction()
    msg = "Replaced %d component(s) with %s.\nMates re-attached: %d." % (len(comps), tgt.Document.Label, len(ok_all))
    if bad_all:
        msg += "\n\nMated entities that need attention (edit these mates):\n  " + "\n  ".join(bad_all)
    QtWidgets.QMessageBox.information(Gui.getMainWindow(), "Replace Components", msg)
