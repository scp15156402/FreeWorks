#!/usr/bin/env python3
"""Generate FreeWorks drawing sheet formats (TechDraw SVG templates).

Sheet sizes: ISO A0-A4 landscape (+ A4 portrait) and ANSI A-E landscape, border with zone
markings (numbers along the top/bottom, letters along the sides) and a title block laid out the
way SOLIDWORKS' default sheet formats are organised: tolerance notes, NAME / SIGNATURE / DATE grid
(DRAWN, CHK'D, APPV'D, MFG, Q.A), MATERIAL, FINISH, WEIGHT, TITLE, DWG NO., REV, SCALE, SHEET and the
size letter. The drawing is original. Fields are TechDraw editable texts; title, author, date,
scale and sheet use TechDraw's autofill, MATERIAL and WEIGHT are filled by FreeWorks from the part.

Run: python3 tools/make_templates.py  ->  Mod/FreeWorks/Resources/Templates/*.svg
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Mod", "FreeWorks", "Resources", "Templates")

SHEETS = [  # name, width, height (mm), standard, zones (columns, rows)
    ("A0 (ISO)", 1189, 841, "ISO", (16, 12)), ("A1 (ISO)", 841, 594, "ISO", (12, 8)),
    ("A2 (ISO)", 594, 420, "ISO", (8, 6)), ("A3 (ISO)", 420, 297, "ISO", (8, 6)),
    ("A4 (ISO)", 297, 210, "ISO", (6, 4)), ("A4 (ISO) Portrait", 210, 297, "ISO", (4, 6)),
    ("A (ANSI) Landscape", 279.4, 215.9, "ANSI", (4, 4)), ("B (ANSI) Landscape", 431.8, 279.4, "ANSI", (8, 4)),
    ("C (ANSI) Landscape", 558.8, 431.8, "ANSI", (8, 6)), ("D (ANSI) Landscape", 863.6, 558.8, "ANSI", (8, 6)),
    ("E (ANSI) Landscape", 1117.6, 863.6, "ANSI", (8, 6)),
]
FONT = "osifont"
LW = "stroke:#000000;fill:none;stroke-linecap:square"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=2.5, anchor="start", bold=False, edit=None, auto=None):
    attrs = ""
    if edit:
        attrs += ' freecad:editable="%s"' % edit
    if auto:
        attrs += ' freecad:autofill="%s"' % auto
    w = "font-weight:bold;" if bold else ""
    if edit and not s:
        s = "\u00a0"                 # keep an empty field clickable in TechDraw
    return ('<text x="%.2f" y="%.2f"%s style="font-size:%.2fpx;font-family:%s;%stext-anchor:%s;fill:#000000">'
            '<tspan>%s</tspan></text>' % (x, y, attrs, size, FONT, w, anchor, esc(s)))


def line(x1, y1, x2, y2, w=0.35):
    return '<path d="M %.2f,%.2f L %.2f,%.2f" style="%s;stroke-width:%.2f"/>' % (x1, y1, x2, y2, LW, w)


def rect(x, y, w, h, sw=0.35):
    return '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" style="%s;stroke-width:%.2f"/>' % (x, y, w, h, LW, sw)


def sheet(name, W, H, std, zones):
    m = 10.0                          # border margin
    small = W < 300 or H < 230
    out = []
    out.append(rect(m, m, W - 2 * m, H - 2 * m, 0.7))
    out.append(rect(m - 5, m - 5, W - 2 * m + 10, H - 2 * m + 10, 0.35))
    cols, rows = zones
    zw, zh = (W - 2 * m) / cols, (H - 2 * m) / rows
    for i in range(cols):
        x = m + zw * i
        if i:
            out += [line(x, m - 5, x, m), line(x, H - m, x, H - m + 5)]
        lab = str(cols - i)
        out += [txt(x + zw / 2, m - 1.3, lab, 3, "middle"), txt(x + zw / 2, H - m + 3.8, lab, 3, "middle")]
    letters = "ABCDEFGHJKLMNP"
    for j in range(rows):
        y = m + zh * j
        if j:
            out += [line(m - 5, y, m, y), line(W - m, y, W - m + 5, y)]
        lab = letters[rows - 1 - j]
        out += [txt(m - 2.5, y + zh / 2 + 1, lab, 3, "middle"), txt(W - m + 2.5, y + zh / 2 + 1, lab, 3, "middle")]
    # ---- title block (bottom right)
    tw = 170.0 if not small else min(170.0, W - 2 * m)
    th = 50.0
    x0, y0 = W - m - tw, H - m - th
    out.append(rect(x0, y0, tw, th, 0.5))
    # left: tolerances + name/signature/date grid (95 mm), right: material/title (75 mm)
    lw_ = 95.0
    xr = x0 + lw_
    out.append(line(xr, y0, xr, y0 + th, 0.5))
    # tolerance notes (top-left strip, 14 mm)
    out.append(line(x0, y0 + 14, xr, y0 + 14))
    unit = "MILLIMETERS" if std == "ISO" else "INCHES"
    out.append(txt(x0 + 1.5, y0 + 3.4, "UNLESS OTHERWISE SPECIFIED:", 2.2, bold=True))
    out.append(txt(x0 + 1.5, y0 + 6.4, "DIMENSIONS ARE IN %s" % unit, 2.1))
    out.append(txt(x0 + 1.5, y0 + 9.2, "SURFACE FINISH:", 2.1))
    out.append(txt(x0 + 1.5, y0 + 12.0, "TOLERANCES:  LINEAR:", 2.1))
    out.append(txt(x0 + 34, y0 + 12.0, "±0.1", 2.1, edit="tol_linear"))
    out.append(txt(x0 + 46, y0 + 12.0, "ANGULAR:", 2.1))
    out.append(txt(x0 + 60, y0 + 12.0, "±0.5°", 2.1, edit="tol_angular"))
    out.append(txt(x0 + 60, y0 + 3.4, "FINISH:", 2.1))
    out.append(txt(x0 + 60, y0 + 6.6, "", 2.6, edit="finish"))
    out.append(txt(x0 + 60, y0 + 9.4, "DEBUR AND BREAK SHARP EDGES", 2.0))
    out.append(line(x0 + 58, y0, x0 + 58, y0 + 14))
    # name / signature / date grid: 6 rows of 6 mm under a 0 mm header row
    gy = y0 + 14
    rh = 6.0
    c1, c2, c3 = x0 + 16, x0 + 44, x0 + 66
    out += [line(c1, gy, c1, y0 + th), line(c2, gy, c2, y0 + th), line(c3, gy, c3, y0 + th)]
    hdr = [("", 0), ("NAME", c1), ("SIGNATURE", c2), ("DATE", c3)]
    for lab, x in hdr[1:]:
        out.append(txt(x + 1.2, gy + 4.2, lab, 2.2, bold=True))
    roles = [("DRAWN", "drawn"), ("CHK'D", "checked"), ("APPV'D", "approved"), ("MFG", "mfg"), ("Q.A", "qa")]
    for k in range(1, 6):
        out.append(line(x0, gy + rh * k, xr, gy + rh * k))
    for k, (lab, key) in enumerate(roles):
        y = gy + rh * (k + 1)
        out.append(txt(x0 + 1.2, y + 4.2, lab, 2.2, bold=True))
        out.append(txt(c1 + 1.2, y + 4.4, "", 2.8, edit="%s_name" % key, auto="author" if key == "drawn" else None))
        out.append(txt(c3 + 1.2, y + 4.4, "", 2.6, edit="%s_date" % key, auto="date" if key == "drawn" else None))
    # right column: company, title, material/weight, dwg no, scale/sheet
    out.append(txt(xr + 1.5, y0 + 6, "", 3.0, bold=True, edit="company", auto="organization"))
    out.append(line(xr, y0 + 9, x0 + tw, y0 + 9))
    out.append(txt(xr + 1.5, y0 + 12.2, "TITLE:", 2.2, bold=True))
    out.append(txt(xr + 1.5, y0 + 18.5, "", 5.0, bold=True, edit="title", auto="title"))
    out.append(line(xr, y0 + 22, x0 + tw, y0 + 22))
    out.append(txt(xr + 1.5, y0 + 25.2, "MATERIAL:", 2.2, bold=True))
    out.append(txt(xr + 1.5, y0 + 29.5, "", 3.2, edit="material"))
    out.append(line(xr + 45, y0 + 22, xr + 45, y0 + 31))
    out.append(txt(xr + 46.5, y0 + 25.2, "WEIGHT:", 2.2, bold=True))
    out.append(txt(xr + 46.5, y0 + 29.5, "", 3.2, edit="weight"))
    out.append(line(xr, y0 + 31, x0 + tw, y0 + 31))
    out.append(txt(xr + 1.5, y0 + 34.2, "DWG NO.", 2.2, bold=True))
    out.append(txt(xr + 1.5, y0 + 39.5, "", 3.6, bold=True, edit="drawing_number"))
    out.append(line(xr + 52, y0 + 31, xr + 52, y0 + 42))
    out.append(txt(xr + 53.5, y0 + 34.2, "REV", 2.2, bold=True))
    out.append(txt(xr + 53.5, y0 + 39.5, "", 3.2, edit="revision"))
    out.append(line(xr + 64, y0 + 31, xr + 64, y0 + th))
    size = name.split(" ")[0]
    out.append(txt(xr + 69.5, y0 + 40.5, size, 6.0 if len(size) < 3 else 4.5, "middle", bold=True))
    out.append(line(xr, y0 + 42, xr + 64, y0 + 42))
    out.append(txt(xr + 1.5, y0 + 46.8, "SCALE:", 2.2, bold=True))
    out.append(txt(xr + 12, y0 + 46.9, "1:1", 3.0, edit="scale", auto="scale"))
    out.append(txt(xr + 30, y0 + 46.8, "SHEET", 2.2, bold=True))
    out.append(txt(xr + 41, y0 + 46.9, "1 OF 1", 3.0, edit="sheet", auto="sheet"))
    # projection symbol strip above the title block
    py = y0 - 9
    out.append(rect(x0 + tw - 32, py, 32, 9, 0.35))
    out.append(txt(x0 + tw - 30.5, py + 5.5, "FIRST ANGLE" if std == "ISO" else "THIRD ANGLE", 2.1))
    sx = x0 + tw - 9
    tr = '<path d="M %.2f,%.2f l -5,1.5 v 3 l 5,1.5 z" style="%s;stroke-width:0.3"/>' % (sx - (5 if std == "ISO" else -4), py + 1.5, LW)
    out.append(tr)
    out.append('<circle cx="%.2f" cy="%.2f" r="2.2" style="%s;stroke-width:0.3"/>' % (sx + (2.5 if std == "ISO" else -5), py + 4.5, LW))
    out.append('<circle cx="%.2f" cy="%.2f" r="1.1" style="%s;stroke-width:0.3"/>' % (sx + (2.5 if std == "ISO" else -5), py + 4.5, LW))
    out.append(txt(m + 2, H - m - 2, "DO NOT SCALE DRAWING", 2.0))
    body = "\n  ".join(out)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:freecad="https://www.freecad.org/wiki/index.php?title=Svg_Namespace"'
            ' width="%gmm" height="%gmm" viewBox="0 0 %g %g" version="1.1">\n'
            '  <title>FreeWorks sheet format %s</title>\n  %s\n</svg>\n' % (W, H, W, H, name, body))


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    for name, W, H, std, zones in SHEETS:
        fn = name.replace(" ", "_").replace("(", "").replace(")", "") + ".svg"
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(sheet(name, W, H, std, zones))
    print("wrote %d sheet formats to %s" % (len(SHEETS), OUT))


if __name__ == "__main__":
    main()
