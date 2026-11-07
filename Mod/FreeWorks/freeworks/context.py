"""Work out which SolidWorks-style environment the user is in."""
import FreeCAD as App
import FreeCADGui as Gui


def mdi_area():
    from PySide import QtWidgets
    return Gui.getMainWindow().findChild(QtWidgets.QMdiArea)


def active_view_class():
    try:
        sw = mdi_area().activeSubWindow()
        return sw.widget().metaObject().className() if sw else ""
    except Exception:
        return ""


def edited_object():
    gd = Gui.ActiveDocument
    if not gd:
        return None
    try:
        vp = gd.getInEdit()
        return vp.Object if vp else None
    except Exception:
        return None


def edited_sketch():
    o = edited_object()
    if o is not None and o.isDerivedFrom("Sketcher::SketchObject"):
        return o
    return None


def doc_type(doc=None):
    doc = doc or App.ActiveDocument
    if doc is None:
        return None
    try:
        t = doc.Meta.get("FreeWorksType")
        if t:
            return t
    except Exception:
        pass
    for o in doc.Objects:
        if o.TypeId == "Assembly::AssemblyObject":
            return "assembly"
    if any(o.isDerivedFrom("TechDraw::DrawPage") for o in doc.Objects) and not any(
            o.isDerivedFrom("PartDesign::Body") or o.isDerivedFrom("Part::Feature") for o in doc.Objects
            if not o.isDerivedFrom("TechDraw::DrawView")):
        return "drawing"
    return "part"


def current():
    """'sketch' | 'drawing' | 'assembly' | 'part' | 'none'"""
    if App.ActiveDocument is None:
        return "none"
    if edited_sketch() is not None:
        return "sketch"
    cls = active_view_class()
    if "MDIViewPage" in cls or "TechDraw" in cls:
        return "drawing"
    return doc_type() or "part"


def label(ctx=None):
    ctx = ctx or current()
    return {"sketch": "Editing Sketch", "drawing": "Editing Drawing", "assembly": "Editing Assembly",
            "part": "Editing Part", "none": ""}.get(ctx, "")
