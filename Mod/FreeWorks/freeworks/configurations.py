"""Configurations and design tables (SOLIDWORKS ConfigurationManager) for FreeCAD documents.

Model: a small table - rows are configurations, columns are configured parameters, exactly like a
SOLIDWORKS design table. Everything not in the table is shared by all configurations.
Column keys use SOLIDWORKS design-table headers:
  D1@Sketch1, D2@Boss-Extrude1   dimension (see equations.py for the D<n> numbering)
  $STATE@Fillet1                 S = suppressed, U = unsuppressed
  A                              global variable (Equations)
  $DESCRIPTION, $PARTNUMBER      text only
Switching configuration first stores the current values of all columns into the active row (so a
change made "in this configuration" is kept), then applies the new row and rebuilds.
Stored in the document as a hidden App::VarSet "Configurations" (JSON table), so it travels with
the file and needs no add-on.
"""
import csv
import json
import os

import FreeCAD as App

from . import log
from . import equations as eq

OBJ = "Configurations"
TEXT_KEYS = ("$DESCRIPTION", "$PARTNUMBER", "$COMMENT")


# ------------------------------------------------------------------ storage
def store(doc, create=False):
    o = doc.getObject(OBJ)
    if o is None and create:
        o = doc.addObject("App::VarSet", OBJ)
        o.Label = "Configurations"
        o.addProperty("App::PropertyString", "Active", "Configurations", "Active configuration")
        o.addProperty("App::PropertyString", "Table", "Configurations", "Design table (JSON)")
        o.Active = "Default"
        o.Table = json.dumps({"order": ["Default"], "columns": [], "rows": {"Default": {}}})
        try:
            if o.ViewObject and hasattr(o.ViewObject, "ShowInTree"):
                o.ViewObject.ShowInTree = False
        except Exception:
            pass
    return o


def _load(doc):
    o = store(doc)
    if o is None:
        return {"order": ["Default"], "columns": [], "rows": {"Default": {}}}
    return json.loads(o.Table)


def _save(doc, t):
    store(doc, create=True).Table = json.dumps(t)


def names(doc):
    return list(_load(doc)["order"])


def active(doc):
    o = store(doc)
    return o.Active if o is not None else "Default"


def columns(doc):
    return list(_load(doc)["columns"])


def table(doc):
    """(order, columns, rows) - rows[config][column] = value (str)."""
    t = _load(doc)
    return t["order"], t["columns"], t["rows"]


# ------------------------------------------------------------------ model values
def _fmt(v):
    if isinstance(v, float):
        return ("%.6f" % v).rstrip("0").rstrip(".")
    return str(v)


def read_value(doc, key):
    if key in TEXT_KEYS:
        return ""
    if key.startswith("$STATE@"):
        o = eq._by_label(doc, key.split("@", 1)[1])
        return "S" if o is not None and getattr(o, "Suppressed", False) else "U"
    if "@" not in key:
        for n, v, _ in eq.variables(doc):
            if n == key:
                return _fmt(v)
        return ""
    name, owner = key.split("@", 1)
    o, path = eq.dim_path(doc, name, owner)
    v = eq.read(o, path)
    return "" if v is None else _fmt(float(v))


def apply_value(doc, key, val):
    if key in TEXT_KEYS or val in (None, ""):
        return
    if key.startswith("$STATE@"):
        o = eq._by_label(doc, key.split("@", 1)[1])
        if o is not None and hasattr(o, "Suppressed"):
            o.Suppressed = str(val).strip().upper().startswith("S")
        return
    if "@" not in key:
        eq.set_variable(doc, key, str(val))
        return
    name, owner = key.split("@", 1)
    o, path = eq.dim_path(doc, name, owner)
    if path.lstrip(".") in [p.lstrip(".") for p, _ in o.ExpressionEngine]:
        raise ValueError("%s is driven by an equation; configure the global variable instead" % key)
    v = float(val)
    if path.startswith("Constraints."):
        cname = path.split(".", 1)[1]
        idx = [c.Name for c in o.Constraints].index(cname)
        c = o.Constraints[idx]
        o.setDatum(idx, App.Units.Quantity("%s deg" % v) if c.Type == "Angle" else App.Units.Quantity("%s mm" % v))
    else:
        cur = getattr(o, path)
        setattr(o, path, int(round(v)) if isinstance(cur, int) else v)


# ------------------------------------------------------------------ operations
def capture(doc):
    """Store the model's current values of all columns into the active configuration."""
    t = _load(doc)
    a = active(doc)
    row = t["rows"].setdefault(a, {})
    for k in t["columns"]:
        if k in TEXT_KEYS:
            continue
        try:
            row[k] = read_value(doc, k)
        except Exception as e:
            log("configuration capture %s: %s" % (k, e))
    _save(doc, t)


def activate(doc, name, capture_current=True):
    t = _load(doc)
    if name not in t["rows"]:
        raise ValueError("No configuration %r" % name)
    if capture_current and store(doc) is not None:
        capture(doc)
        t = _load(doc)
    errors = []
    for k in t["columns"]:
        try:
            apply_value(doc, k, t["rows"][name].get(k))
        except Exception as e:
            errors.append("%s: %s" % (k, e))
    store(doc, create=True).Active = name
    doc.recompute()
    return errors


def add_column(doc, key):
    key = key.strip()
    if not key:
        return
    read_value(doc, key)                   # validates the key
    store(doc, create=True)
    t = _load(doc)
    if key in t["columns"]:
        return
    t["columns"].append(key)
    cur = read_value(doc, key)
    for r in t["rows"].values():
        r[key] = cur
    _save(doc, t)


def remove_column(doc, key):
    t = _load(doc)
    if key in t["columns"]:
        t["columns"].remove(key)
        for r in t["rows"].values():
            r.pop(key, None)
        _save(doc, t)


def add(doc, name, copy_from=None):
    store(doc, create=True)
    capture(doc)
    t = _load(doc)
    if name in t["rows"]:
        raise ValueError("Configuration %r exists" % name)
    src = copy_from or active(doc)
    t["rows"][name] = dict(t["rows"].get(src, {}))
    t["order"].append(name)
    _save(doc, t)


def rename(doc, old, new):
    t = _load(doc)
    if new in t["rows"] or old not in t["rows"]:
        raise ValueError("Can't rename %r to %r" % (old, new))
    t["rows"][new] = t["rows"].pop(old)
    t["order"][t["order"].index(old)] = new
    _save(doc, t)
    if active(doc) == old:
        store(doc).Active = new


def delete(doc, name):
    t = _load(doc)
    if name == active(doc):
        raise ValueError("Activate another configuration before deleting %r" % name)
    if name in t["rows"]:
        t["rows"].pop(name)
        t["order"].remove(name)
        _save(doc, t)


def set_cell(doc, config, key, value):
    t = _load(doc)
    t["rows"].setdefault(config, {})[key] = str(value)
    _save(doc, t)
    if config == active(doc):
        apply_value(doc, key, value)
        doc.recompute()


# ------------------------------------------------------------------ design tables
def import_table(doc, path):
    """CSV or XLSX design table: first column = configuration names, first row = column headers."""
    rows = []
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        for r in ws.iter_rows(values_only=True):
            rows.append(["" if c is None else str(c) for c in r])
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            sample = f.read(2048)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
            rows = [r for r in csv.reader(f, dialect)]
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        raise ValueError("Empty design table")
    head = [h.strip() for h in rows[0][1:]]
    store(doc, create=True)
    capture(doc)
    for k in head:
        if k:
            add_column(doc, k)
    t = _load(doc)
    first = None
    for r in rows[1:]:
        name = r[0].strip()
        if not name:
            continue
        first = first or name
        if name not in t["rows"]:
            t["rows"][name] = dict(t["rows"].get(active(doc), {}))
            t["order"].append(name)
        for k, v in zip(head, r[1:]):
            if k and v.strip() != "":
                t["rows"][name][k] = v.strip()
    _save(doc, t)
    return first


def export_table(doc, path):
    order, cols, rows = table(doc)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + cols)
        for n in order:
            w.writerow([n] + [rows.get(n, {}).get(c, "") for c in cols])
    return os.path.abspath(path)


def candidate_columns(doc):
    """Column keys offered in the ConfigurationManager's Add Column list."""
    out = list(eq.dimension_names(doc))
    for o in doc.Objects:
        if hasattr(o, "Suppressed") and (o.isDerivedFrom("PartDesign::Feature") and not o.isDerivedFrom("PartDesign::Body")):
            out.append("$STATE@" + o.Label)
    out += [n for n, _, _ in eq.variables(doc)]
    out += list(TEXT_KEYS[:2])
    return out
