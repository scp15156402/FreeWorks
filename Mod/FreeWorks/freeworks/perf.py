"""Large Model Mode - SOLIDWORKS 'Large Assembly / Large Design' style performance switch.

Coarser tessellation, no anti-aliasing and no view animations. Applied to new views and,
for open documents, to every shape's display (re-tessellated once)."""
import FreeCAD as App
import FreeCADGui as Gui

from . import log, params, safe_slow

LARGE = {"MeshDeviation": 0.5, "MeshAngularDeflection": 28.5, "AntiAliasing": 0, "UseNavigationAnimations": False}
NORMAL = {"MeshDeviation": 0.1, "MeshAngularDeflection": 12.0, "AntiAliasing": 3, "UseNavigationAnimations": True}
SUGGEST_OBJECTS = 600          # suggest Large Model Mode above this many objects


def is_on():
    return params().GetBool("LargeModelMode", False)


@safe_slow
def set_mode(on):
    params().SetBool("LargeModelMode", bool(on))
    v = LARGE if on else NORMAL
    part = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part")
    view = App.ParamGet("User parameter:BaseApp/Preferences/View")
    part.SetFloat("MeshDeviation", v["MeshDeviation"])
    part.SetFloat("MeshAngularDeflection", v["MeshAngularDeflection"])
    view.SetInt("AntiAliasing", v["AntiAliasing"])
    view.SetBool("UseNavigationAnimations", v["UseNavigationAnimations"])
    n = 0
    for name in App.listDocuments():
        doc = App.getDocument(name)
        for o in doc.Objects:
            vo = getattr(o, "ViewObject", None)
            if vo is None or not hasattr(vo, "Deviation"):
                continue
            try:
                vo.Deviation = v["MeshDeviation"]
                if hasattr(vo, "AngularDeflection"):
                    vo.AngularDeflection = v["MeshAngularDeflection"]
                n += 1
            except Exception:
                pass
    try:
        Gui.getMainWindow().statusBar().showMessage(
            "Large Model Mode %s (%d shapes updated)" % ("ON" if on else "OFF", n), 5000)
    except Exception:
        pass
    log("large model mode %s" % on)


def toggle():
    set_mode(not is_on())


def suggest(doc):
    """Return a hint text when a big document is open and the mode is off."""
    if doc is None or is_on():
        return None
    if len(doc.Objects) >= SUGGEST_OBJECTS:
        return "Large model (%d objects): View > Large Model Mode makes it faster" % len(doc.Objects)
    return None
