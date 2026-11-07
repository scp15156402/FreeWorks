"""Mass Properties, computed and reported the way SOLIDWORKS does.

Engine: every solid that belongs to the part / assembly (or to the selection) is collected with its
placement in the document, its own density (material per body, links resolved), then mass, volume,
area, centre of mass and the inertia tensor are combined (parallel-axis theorem) and expressed in
the chosen output coordinate system and unit system.

Tensor convention: OCC's MatrixOfInertia is the inertia tensor at each solid's centre of mass with
products of inertia stored negative (Ixy = -sum(x*y*dm)). SOLIDWORKS reports "positive tensor
notation" (Lxy = +sum(x*y*dm)); report() converts.
"""
import math

import FreeCAD as App

from . import log, params
from . import materials

UNITS = {   # name: (length unit -> mm factor, mass unit -> g factor, words)
    "MMGS": (1.0, 1.0, ("millimeters", "grams", "square millimeters", "cubic millimeters",
                        "grams per cubic millimeter", "grams *  square millimeters")),
    "CGS": (10.0, 1.0, ("centimeters", "grams", "square centimeters", "cubic centimeters",
                        "grams per cubic centimeter", "grams *  square centimeters")),
    "MKS": (1000.0, 1000.0, ("meters", "kilograms", "square meters", "cubic meters",
                             "kilograms per cubic meter", "kilograms *  square meters")),
    "IPS": (25.4, 453.59237, ("inches", "pounds", "square inches", "cubic inches",
                              "pounds per cubic inch", "pounds *  square inches")),
}


# ------------------------------------------------------------------ small linear algebra
def _vec(v):
    return [v.x, v.y, v.z]


def _mat(m):
    return [[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]]


def _add(a, b, k=1.0):
    return [[a[i][j] + k * b[i][j] for j in range(3)] for i in range(3)]


def _shift(m, d):
    """m * (|d|^2 E - d d^T)  (parallel-axis term, standard tensor sign)."""
    dd = sum(x * x for x in d)
    return [[(dd if i == j else 0.0) - d[i] * d[j] for j in range(3)] for i in range(3)]


def _rot_tensor(T, R):
    """R^T T R, R = 3x3 with columns = output axes in document coordinates."""
    RT = [[R[j][i] for j in range(3)] for i in range(3)]
    TR = [[sum(T[i][k] * R[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return [[sum(RT[i][k] * TR[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _eig_sym(A):
    """Eigen-decomposition of a symmetric 3x3 matrix (cyclic Jacobi). Returns ([w], [[v]] columns)."""
    a = [row[:] for row in A]
    V = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]
    for _ in range(60):
        off = sum(a[i][j] ** 2 for i in range(3) for j in range(3) if i != j)
        if off < 1e-30 * (1.0 + sum(a[i][i] ** 2 for i in range(3))):
            break
        for p, q in ((0, 1), (0, 2), (1, 2)):
            if abs(a[p][q]) < 1e-300:
                continue
            th = (a[q][q] - a[p][p]) / (2.0 * a[p][q])
            t = (1.0 if th >= 0 else -1.0) / (abs(th) + math.sqrt(th * th + 1.0))
            c = 1.0 / math.sqrt(t * t + 1.0)
            s = t * c
            for k in range(3):
                akp, akq = a[k][p], a[k][q]
                a[k][p], a[k][q] = c * akp - s * akq, s * akp + c * akq
            for k in range(3):
                apk, aqk = a[p][k], a[q][k]
                a[p][k], a[q][k] = c * apk - s * aqk, s * apk + c * aqk
            for k in range(3):
                vkp, vkq = V[k][p], V[k][q]
                V[k][p], V[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    w = [a[i][i] for i in range(3)]
    order = sorted(range(3), key=lambda i: w[i])
    vecs = []
    for i in order:
        v = [V[0][i], V[1][i], V[2][i]]
        big = max(range(3), key=lambda k: abs(v[k]))
        if v[big] < 0:
            v = [-x for x in v]
        vecs.append(v)
    return [w[i] for i in order], vecs


# ------------------------------------------------------------------ collecting solids
def _is_assembly(o):
    return o.TypeId == "Assembly::AssemblyObject"


def _is_leaf(o):
    if o.isDerivedFrom("PartDesign::Body"):
        return True
    if o.isDerivedFrom("PartDesign::Feature") or not o.isDerivedFrom("Part::Feature"):
        return False
    shp = getattr(o, "Shape", None)
    return shp is not None and not shp.isNull() and bool(shp.Solids)


def _visible(parent, child):
    try:
        if parent is not None:
            v = parent.isElementVisible(child.Name)
            if v >= 0:
                return bool(v)
    except Exception:
        pass
    vo = getattr(child, "ViewObject", None)
    return bool(vo.Visibility) if vo is not None else bool(getattr(child, "Visibility", True))


def _walk(root, obj, path, parent, hidden, out, depth=0):
    if depth > 32:
        return
    if path and not hidden and not _visible(parent, obj):
        return
    if _is_leaf(obj):
        out.append((root, path, obj))
        return
    tgt = obj
    if obj.TypeId == "App::Link" or obj.isDerivedFrom("App::Link"):
        tgt = obj.getLinkedObject(True)
        if tgt is None:
            return
        if _is_leaf(tgt):
            out.append((root, path, tgt))
            return
    if hasattr(tgt, "Group") and (tgt.isDerivedFrom("App::Part") or tgt.isDerivedFrom("App::DocumentObjectGroup")):
        for ch in tgt.Group:
            _walk(root, ch, path + ch.Name + ".", tgt, hidden, out, depth + 1)


def collect(hidden=True, use_selection=True):
    """[(root, subname path, leaf object)] for the selection or the whole active document."""
    out = []
    if use_selection:
        try:
            import FreeCADGui as Gui
            for s in Gui.Selection.getSelectionEx("", 0):
                for name in (s.SubElementNames or ("",)):
                    path = name[:name.rfind(".") + 1] if "." in name else ""
                    _from_path(s.Object, path, hidden, out)
        except Exception as e:
            log("mass properties selection: %s" % e)
        if out:
            return _dedupe(out)
    doc = App.ActiveDocument
    if doc is None:
        return []
    asm = [o for o in doc.RootObjects if _is_assembly(o)]
    for r in (asm[:1] or doc.RootObjects):
        _walk(r, r, "", None, hidden, out)
    return _dedupe(out)


def _from_path(root, path, hidden, out):
    """Selection inside a part or assembly -> the component/body that contains it."""
    names = [n for n in path.split(".") if n]
    cur, sub = root, ""
    if _is_leaf(root):
        out.append((root, "", root))
        return
    for n in names:
        nxt = cur.getSubObject(n + ".", retType=1)
        nxt = nxt[0] if isinstance(nxt, tuple) else nxt
        if nxt is None:
            break
        sub += n + "."
        lt = nxt.getLinkedObject(True) if (nxt.TypeId == "App::Link" or nxt.isDerivedFrom("App::Link")) else nxt
        if _is_leaf(lt) or _is_leaf(nxt):
            out.append((root, sub, lt))
            return
        if nxt.isDerivedFrom("PartDesign::Feature"):
            break
        cur = lt
    # selected a container (assembly / sub-assembly / App::Part) or the root itself
    target = root if not sub else root.getSubObject(sub, retType=1)
    target = target[0] if isinstance(target, tuple) else target
    if target is not None:
        _walk(root, target, sub, None, hidden, out)


def _dedupe(items):
    seen, out = set(), []
    for r, p, o in items:
        k = (r.Document.Name, r.Name, p)
        if k not in seen:
            seen.add(k)
            out.append((r, p, o))
    return out


def _shape(root, path):
    import Part
    if not path:
        return Part.getShape(root, "", needSubElement=False, transform=True)
    return Part.getShape(root, path, needSubElement=False, transform=True)


def _label(root, path, leaf):
    parts = [root.Label]
    cur = root
    for n in [x for x in path.split(".") if x]:
        o = cur.getSubObject(n + ".", retType=1)
        o = o[0] if isinstance(o, tuple) else o
        if o is None:
            break
        parts.append(o.Label)
        cur = o.getLinkedObject(True) if o.TypeId == "App::Link" else o
    if len(parts) > 1:
        parts = parts[1:]
    return "/".join(parts)


# ------------------------------------------------------------------ compute
def compute(items):
    """Combine solids. Lengths mm, mass g. Returns dict or None when nothing solid was found."""
    M = V = A = 0.0
    sm = [0.0, 0.0, 0.0]
    parts = []
    for root, path, leaf in items:
        shp = _shape(root, path)
        if shp is None or shp.isNull() or not shp.Solids:
            continue
        mat, rho = materials.material_of(leaf)
        k = rho * 1e-6                      # kg/m^3 -> g/mm^3
        for s in shp.Solids:
            v = abs(s.Volume)
            if v <= 0:
                continue
            g = _vec(s.CenterOfMass)
            m = v * k
            M += m
            V += v
            A += s.Area
            sm = [sm[i] + m * g[i] for i in range(3)]
            J = _mat(s.MatrixOfInertia)
            if s.Volume < 0:
                J = [[-x for x in r] for r in J]
            parts.append((m, g, J, k, leaf, mat, rho, _label(root, path, leaf)))
    if M <= 0:
        return None
    G = [x / M for x in sm]
    T = [[0.0] * 3 for _ in range(3)]
    for m, g, J, k, *_ in parts:
        d = [g[i] - G[i] for i in range(3)]
        T = _add(T, J, k)
        T = _add(T, _shift(m, d), m)
    dens = {round(p[6], 6) for p in parts}
    comps = {}
    for m, g, J, k, leaf, mat, rho, lab in parts:
        c = comps.setdefault(lab, [0.0, mat, rho])
        c[0] += m
    return {"mass": M, "volume": V, "area": A, "com": G, "T": T,
            "density": (parts[0][6] if len(dens) == 1 else None),
            "components": [(lab, c[0], c[1], c[2]) for lab, c in comps.items()]}


def coordinate_systems(doc=None):
    """[(label, Placement)] - output coordinate systems available in the document."""
    doc = doc or App.ActiveDocument
    out = []
    if doc is None:
        return out
    for o in doc.Objects:
        tid = o.TypeId
        if tid == "App::Origin":
            continue
        if tid in ("PartDesign::CoordinateSystem", "Part::LocalCoordinateSystem", "App::LocalCoordinateSystem") \
                or o.isDerivedFrom("App::LocalCoordinateSystem"):
            try:
                plc = o.getGlobalPlacement()
            except Exception:
                plc = o.Placement
            out.append((o.Label, plc))
    return out


def express(res, plc=None):
    """Express a compute() result in an output coordinate system (Placement in document coords)."""
    if plc is None:
        plc = App.Placement()
    O = _vec(plc.Base)
    Rm = plc.Rotation.toMatrix()
    R = [[Rm.A11, Rm.A12, Rm.A13], [Rm.A21, Rm.A22, Rm.A23], [Rm.A31, Rm.A32, Rm.A33]]
    d = [res["com"][i] - O[i] for i in range(3)]
    g = [sum(R[k][i] * d[k] for k in range(3)) for i in range(3)]       # R^T d
    TG = _rot_tensor(res["T"], R)
    TO = _add(TG, _shift(res["mass"], g), res["mass"])
    w, vecs = _eig_sym(TG)
    return {"com": g, "TG": TG, "TO": TO, "principal": list(zip(w, vecs))}


# ------------------------------------------------------------------ report
def _pos(T):
    """Standard tensor -> SOLIDWORKS positive tensor notation (products of inertia sign flipped)."""
    return [[T[i][j] if i == j else -T[i][j] for j in range(3)] for i in range(3)]


def report(res, title, cs_label="-- default --", plc=None, units="MMGS", decimals=2):
    L, Mf, w = UNITS.get(units, UNITS["MMGS"])
    e = express(res, plc)
    f = "%%.%df" % decimals
    eps = 0.5 * 10 ** -decimals

    def z(v):                       # no "-0.00"
        return 0.0 if abs(v) < eps else v
    m = res["mass"] / Mf
    lines = ["Mass properties of %s" % title,
             "     Coordinate system: %s" % cs_label, ""]
    if res["density"] is not None:
        rho = res["density"] * 1e-6 / Mf * L ** 3          # in mass unit / length unit^3
        dd = max(decimals, 0 if rho == 0 else min(8, int(-math.floor(math.log10(abs(rho)))) + 1))
        lines.append(("Density = %%.%df %%s" % dd) % (rho, w[4]))
    else:
        lines.append("Density = (several materials)")
    lines += ["", ("Mass = " + f + " %s") % (m, w[1]), "",
              ("Volume = " + f + " %s") % (res["volume"] / L ** 3, w[3]), "",
              ("Surface area = " + f + " %s") % (res["area"] / L ** 2, w[2]), "",
              "Center of mass: ( %s )" % w[0]]
    for a, v in zip("XYZ", e["com"]):
        lines.append(("\t%s = " + f) % (a, z(v / L)))
    k = 1.0 / (Mf * L * L)
    lines += ["", "Principal axes of inertia and principal moments of inertia: ( %s )" % w[5],
              "Taken at the center of mass."]
    for n, (val, vec) in zip(("x", "y", "z"), e["principal"]):
        lines.append(("\t I%s = (" + f + ", " + f + ", " + f + ")   \tP%s = " + f) % (n, z(vec[0]), z(vec[1]), z(vec[2]), n, z(val * k)))
    for head, T, p in (("Taken at the center of mass and aligned with the output coordinate system. (Using positive tensor notation.)", e["TG"], "L"),
                       ("Taken at the output coordinate system. (Using positive tensor notation.)", e["TO"], "I")):
        P = _pos(T)
        lines += ["", "Moments of inertia: ( %s )" % w[5], head]
        for i, a in enumerate("xyz"):
            lines.append("\t" + "\t".join((("%s%s%s = " + f) % (p, a, b, z(P[i][j] * k))) for j, b in enumerate("xyz")))
    comps = res.get("components") or []
    if len(comps) > 1 or (comps and comps[0][2] == materials.NOT_SPECIFIED):
        lines += ["", "-" * 64, "Bodies / components included (FreeWorks):"]
        for lab, cm, mat, rho in comps:
            lines.append(("\t%s: " + f + " %s, %s (%.0f kg/m^3)") % (lab, cm / Mf, w[1], mat, rho))
        if any(c[2] == materials.NOT_SPECIFIED for c in comps):
            lines.append("\tNo material assigned = 1000 kg/m^3, as in SOLIDWORKS. Right-click the body -> Edit Material.")
    return "\n".join(lines)


def settings():
    p = params()
    return p.GetString("MassUnits", "MMGS"), p.GetInt("MassDecimals", 2), p.GetBool("MassIncludeHidden", True)


def run_text(cs_label=None, use_selection=True):
    """Convenience for scripts/tests: report text with saved settings, or None."""
    units, dec, hidden = settings()
    items = collect(hidden=hidden, use_selection=use_selection)
    res = compute(items)
    if res is None:
        return None
    plc = None
    if cs_label:
        plc = dict(coordinate_systems()).get(cs_label)
    doc = App.ActiveDocument
    return report(res, doc.Label if doc else "", cs_label or "-- default --", plc, units, dec)
