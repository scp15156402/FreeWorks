"""SOLIDWORKS-style assembly FeatureManager names.

* Components are named by part and instance: ``Bracket<1>``, ``Bracket<2>``.
* A fixed (grounded) component gets the ``(f) `` prefix, removed again when it floats.
* FreeCAD's "Joints" group is called "Mates"; joints created with FreeCAD's own joint tools get
  SOLIDWORKS mate names (``Concentric2 (Shaft<1>,Base<1>)``).

Runs after a document recompute (cheap: walks the assembly's direct children only) and never
while a task panel is open, so FreeCAD's own panels keep the labels they manage.
"""
import re

import FreeCAD as App

from . import log, params

FIXED = "(f) "
_INST = re.compile(r"^(.*)<(\d+)>$")


def _is_link(o):
    return o.TypeId == "App::Link" or o.isDerivedFrom("App::Link")


def clean(label):
    """Component label without the (f) prefix."""
    return label[len(FIXED):] if label.startswith(FIXED) else label


def assemblies(doc):
    return [o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject"]


def _base(link):
    t = link.getLinkedObject(True)
    if t is None:
        return None
    if t.Document is not link.Document:
        return t.Document.Label
    return t.Label


def _is_default_label(link, base):
    lab = clean(link.Label)
    if _INST.match(lab):
        return False
    stems = {re.sub(r"\d+$", "", link.Name)}
    t = link.getLinkedObject(True)
    for s in (base, t.Label if t is not None else None):
        if s:
            stems.add(re.sub(r"\d+$", "", s))
    return re.sub(r"\d+$", "", lab) in stems


def _grounded(asm):
    out = set()
    try:
        import UtilsAssembly
        for j in UtilsAssembly.getJointGroup(asm).Group:
            g = getattr(j, "ObjectToGround", None)
            if g is not None:
                out.add(g)
    except Exception:
        pass
    return out


def sweep(doc):
    """Bring every assembly in the document to SOLIDWORKS naming. Returns number of labels changed."""
    if not params().GetBool("AutoRenameFeatures", True):
        return 0
    n = 0
    for asm in assemblies(doc):
        n += _sweep_assembly(asm)
    return n


def _set(o, label):
    if o.Label != label:
        o.Label = label
        return 1
    return 0


def _sweep_assembly(asm):
    n = 0
    comps = [o for o in asm.Group if _is_link(o)]
    used = {}
    for c in comps:
        m = _INST.match(clean(c.Label))
        if m:
            used.setdefault(m.group(1), set()).add(int(m.group(2)))
    for c in comps:
        base = _base(c)
        if base and _is_default_label(c, base):
            nums = used.setdefault(base, set())
            k = 1
            while k in nums:
                k += 1
            nums.add(k)
            n += _set(c, "%s%s<%d>" % (FIXED if c.Label.startswith(FIXED) else "", base, k))
    grounded = _grounded(asm)
    for c in comps:
        want = (FIXED + clean(c.Label)) if c in grounded else clean(c.Label)
        n += _set(c, want)
    try:
        import UtilsAssembly
        jg = UtilsAssembly.getJointGroup(asm)
        if jg.Label in ("Joints", "Joint"):
            n += _set(jg, "Mates")
        n += _name_joints(asm, jg)
    except Exception as e:
        log("assembly names: %s" % e)
    return n


def _name_joints(asm, jg):
    from . import mates
    try:
        from JointObject import TranslatedJointTypes, JointTypes
        fc_names = set(TranslatedJointTypes) | set(JointTypes) | {"Joint", "Temporary joint"}
    except Exception:
        fc_names = {"Joint"}
    n = 0
    for j in jg.Group:
        if not hasattr(j, "JointType") or getattr(j, "MateType", ""):
            continue
        ref2 = getattr(j, "Reference2", None)
        if not ref2:
            continue
        stem = re.sub(r"\d+$", "", j.Label)
        if stem not in fc_names:
            continue                                    # renamed by the user
        mate = mates.mate_of(j)
        if not mate:
            continue
        c1, c2 = mates.joint_comps(j)
        lab = mates.next_label(asm, mate)
        if c1 is not None and c2 is not None:
            lab += " (%s,%s)" % (clean(c1.Label), clean(c2.Label))
        n += _set(j, lab)
    return n


class _Observer:
    def slotRecomputedDocument(self, doc):
        try:
            import FreeCADGui as Gui
            if Gui.Control.activeDialog():
                return
            if assemblies(doc):
                sweep(doc)
        except Exception as e:
            log("assembly naming: %s" % e)


_obs = {"o": None}


def install():
    if _obs["o"] is None:
        from . import harden
        _obs["o"] = harden(_Observer)()
        App.addDocumentObserver(_obs["o"])
