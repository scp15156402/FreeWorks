#!/usr/bin/env python3
"""FreeWorks icon generator.

Draws an ORIGINAL icon set in a SolidWorks-like visual language:
isometric amber solids for "add material", cool grey solids with amber
highlights for "remove/modify", blue sketch geometry, green direction arrows,
dashed blue reference geometry.  No SolidWorks artwork is copied.

Output: one 24x24-viewBox SVG per icon key in ../Mod/FreeWorks/Resources/icons
"""
import math, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "Mod", "FreeWorks", "Resources", "icons")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette
AMB = dict(top="#FFE08A", left="#F2B53C", right="#D18E1E", edge="#7A4B06")
GRY = dict(top="#EEF1F5", left="#C4CAD3", right="#9AA2AE", edge="#4A515C")
BLU = dict(top="#CFE2FF", left="#8DB8F5", right="#5E93E0", edge="#1D4FA8")
SK = "#1F5FD1"        # sketch blue
SKD = "#0B3C99"       # dark sketch blue
GRN = "#2EA043"       # arrows
GRND = "#1B6E2C"
RED = "#D93B2B"
INK = "#2B2F36"
PLANE_F = "#E9C9A0"   # reference plane fill (tan, like classic CAD planes)
PLANE_E = "#9C6B2E"

COS30, SIN30 = math.cos(math.radians(30)), 0.5


def iso(x, y, z, ox=12, oy=14, s=1.0):
    return (ox + (x - y) * COS30 * s, oy + (x + y) * SIN30 * s - z * s)


def pts(seq):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in seq)


def poly(p, fill, stroke, sw=0.6, extra=""):
    return f'<polygon points="{pts(p)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'


def line(a, b, col=SK, w=1.4, dash=None, cap="round"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{col}" stroke-width="{w}" stroke-linecap="{cap}"{d}/>'


def path(d, fill="none", stroke=SK, w=1.4, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def circ(c, r, fill="none", stroke=SK, w=1.4, extra=""):
    return f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="{r:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" {extra}/>'


def dot(c, r=1.3, col=SKD):
    return f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="{r}" fill="{col}"/>'


def box(x0, y0, z0, dx, dy, dz, pal=AMB, **k):
    """Isometric box: draws left (x=const... y-face), right and top faces."""
    P = lambda x, y, z: iso(x, y, z, **k)
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
    left = [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)]   # front-left face (y = y1)
    right = [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)]  # front-right face (x = x1)
    top = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
    return poly(left, pal["left"], pal["edge"]) + poly(right, pal["right"], pal["edge"]) + poly(top, pal["top"], pal["edge"])


def arrow(a, b, col=GRN, w=1.6, head=3.0):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    h1 = (b[0] - head * math.cos(ang - 0.45), b[1] - head * math.sin(ang - 0.45))
    h2 = (b[0] - head * math.cos(ang + 0.45), b[1] - head * math.sin(ang + 0.45))
    bb = (b[0] - head * 0.6 * math.cos(ang), b[1] - head * 0.6 * math.sin(ang))
    return line(a, bb, col, w) + poly([b, h1, h2], col, col, 0.5)


def cyl(cx, cy, rx, ry, h, pal=AMB):
    """Upright cylinder (screen space): ellipse top at cy-h, bottom at cy."""
    body = (f'<path d="M{cx-rx:.2f},{cy-h:.2f} L{cx-rx:.2f},{cy:.2f} A{rx},{ry} 0 0 0 {cx+rx:.2f},{cy:.2f} '
            f'L{cx+rx:.2f},{cy-h:.2f} Z" fill="url(#cg{pal["left"][1:]})" stroke="{pal["edge"]}" stroke-width="0.6"/>')
    top = f'<ellipse cx="{cx}" cy="{cy-h}" rx="{rx}" ry="{ry}" fill="{pal["top"]}" stroke="{pal["edge"]}" stroke-width="0.6"/>'
    return body + top


def grad_defs():
    out = []
    for pal in (AMB, GRY, BLU):
        out.append(f'<linearGradient id="cg{pal["left"][1:]}" x1="0" x2="1" y1="0" y2="0">'
                   f'<stop offset="0" stop-color="{pal["left"]}"/><stop offset="0.55" stop-color="{pal["top"]}"/>'
                   f'<stop offset="1" stop-color="{pal["right"]}"/></linearGradient>')
    return "<defs>" + "".join(out) + "</defs>"


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
            + grad_defs() + body + "</svg>")


def pencil(x=15.5, y=3.5, s=1.0):
    # small pencil, used on sketch icons
    return (f'<g transform="translate({x},{y}) rotate(45) scale({s})">'
            f'<rect x="0" y="-1.4" width="7" height="2.8" fill="#F5C542" stroke="{INK}" stroke-width="0.5"/>'
            f'<rect x="-1.4" y="-1.4" width="1.6" height="2.8" fill="#E57373" stroke="{INK}" stroke-width="0.5"/>'
            f'<polygon points="7,-1.4 9.6,0 7,1.4" fill="#F3E0C0" stroke="{INK}" stroke-width="0.5"/>'
            f'<polygon points="8.9,-0.4 9.6,0 8.9,0.4" fill="{INK}"/></g>')


def plane_shape(ox=12, oy=12, w=8, h=5, fill=PLANE_F, edge=PLANE_E, op=0.9):
    p = [(ox - w, oy + 1), (ox + 2, oy - h + 1), (ox + w, oy - 1), (ox - 2, oy + h - 1)]
    return poly(p, fill, edge, 0.8, f'fill-opacity="{op}"')


def plus(c, col=GRN, r=3.2):
    x, y = c
    return (circ(c, r, "#FFFFFF", col, 0.8) + line((x - r * 0.6, y), (x + r * 0.6, y), col, 1.3)
            + line((x, y - r * 0.6), (x, y + r * 0.6), col, 1.3))


# ---------------------------------------------------------------- icons
I = {}

# ---- features: boss/base
I["extrude_boss"] = svg(
    poly([iso(0, 0, 0), iso(9, 0, 0), iso(9, 9, 0), iso(0, 9, 0)], "none", SK, 1.2, 'stroke-dasharray="1.6,1"')
    + box(1, 1, 0, 7, 7, 7) + arrow(iso(4.5, 4.5, 7.2), (iso(4.5, 4.5, 7)[0], 1.2)))
I["extrude_cut"] = svg(
    box(0, 0, 0, 10, 10, 6, GRY)
    + poly([iso(3, 3, 6), iso(7, 3, 6), iso(7, 7, 6), iso(3, 7, 6)], "#FFF4D6", AMB["edge"], 0.7)
    + poly([iso(3, 7, 6), iso(7, 7, 6), iso(7, 7, 2.5), iso(3, 7, 2.5)], AMB["right"], AMB["edge"], 0.5, 'opacity="0.55"')
    + arrow((iso(5, 5, 6)[0], 1.5), (iso(5, 5, 6)[0], iso(5, 5, 6)[1] - 0.6), RED))
I["revolve_boss"] = svg(
    line((12, 1.5), (12, 22.5), SK, 1.0, "2,1.2") + cyl(12, 19, 7, 2.6, 11)
    + path("M17,4.5 A6,2 0 1 1 9.5,3.6", stroke=GRN, w=1.3) + poly([(9.5, 3.6), (11.6, 2.4), (11.4, 4.8)], GRN, GRN, 0.4))
I["revolve_cut"] = svg(
    cyl(12, 19, 8, 2.8, 11, GRY)
    + '<ellipse cx="12" cy="8" rx="4" ry="1.4" fill="#FFF4D6" stroke="%s" stroke-width="0.7"/>' % AMB["edge"]
    + line((12, 1.5), (12, 22.5), SK, 1.0, "2,1.2")
    + path("M16,4 A4.5,1.5 0 1 1 9,3.4", stroke=RED, w=1.2) + poly([(9, 3.4), (11, 2.2), (10.8, 4.6)], RED, RED, 0.4))
I["sweep_boss"] = svg(
    path("M3,20 C3,12 10,12 12,8 S19,3 21,3", stroke=SK, w=1.0, extra='stroke-dasharray="1.6,1"')
    + path("M3,20 C3,12 10,12 12,8 S19,3 21,3", stroke=AMB["edge"], w=6.2)
    + path("M3,20 C3,12 10,12 12,8 S19,3 21,3", stroke=AMB["left"], w=5)
    + path("M3,20 C3,12 10,12 12,8 S19,3 21,3", stroke=AMB["top"], w=2)
    + '<ellipse cx="3" cy="20" rx="2.6" ry="1.2" fill="%s" stroke="%s" stroke-width="0.6"/>' % (AMB["top"], AMB["edge"])
    + circ((21, 3), 2.4, "none", SK, 1.0))
I["sweep_cut"] = svg(
    box(0, 0, 0, 11, 11, 5, GRY)
    + path("M5,15.5 C8,12 13,15 16,11.5", stroke=AMB["edge"], w=4) + path("M5,15.5 C8,12 13,15 16,11.5", stroke="#FFF4D6", w=2.8)
    + path("M5,15.5 C8,12 13,15 16,11.5", stroke=SK, w=0.8, extra='stroke-dasharray="1.4,0.9"'))
I["loft_boss"] = svg(
    poly([(4, 19), (11, 21.5), (20, 18), (13, 15.5)], AMB["right"], AMB["edge"], 0.6)
    + poly([(4, 19), (7, 6), (12, 7), (11, 21.5)], AMB["left"], AMB["edge"], 0.6)
    + poly([(11, 21.5), (12, 7), (17, 5.5), (20, 18)], AMB["right"], AMB["edge"], 0.6)
    + '<ellipse cx="12" cy="5.6" rx="5" ry="1.8" fill="%s" stroke="%s" stroke-width="0.6"/>' % (AMB["top"], AMB["edge"])
    + poly([(4, 19), (11, 21.5), (20, 18), (13, 15.5)], "none", SK, 1.1)
    + '<ellipse cx="12" cy="5.6" rx="5" ry="1.8" fill="none" stroke="%s" stroke-width="1.1"/>' % SK)
I["loft_cut"] = svg(
    box(0, 0, 0, 11, 11, 6, GRY)
    + poly([iso(2.5, 2.5, 6), iso(8.5, 2.5, 6), iso(8.5, 8.5, 6), iso(2.5, 8.5, 6)], "#FFF4D6", AMB["edge"], 0.7)
    + '<ellipse cx="%.2f" cy="%.2f" rx="2.2" ry="1" fill="none" stroke="%s" stroke-width="1"/>' % (iso(5.5, 5.5, 6)[0], iso(5.5, 5.5, 6)[1] + 1.2, SK)
    + poly([iso(2.5, 2.5, 6), iso(8.5, 2.5, 6), iso(8.5, 8.5, 6), iso(2.5, 8.5, 6)], "none", SK, 0.9))
I["boundary_boss"] = svg(
    path("M4,18 C8,10 16,10 20,18", fill=AMB["left"], stroke=AMB["edge"], w=0.7)
    + path("M4,18 C8,10 16,10 20,18 L20,18 C16,21 8,21 4,18 Z", fill=AMB["right"], stroke=AMB["edge"], w=0.7)
    + path("M4,18 C8,10 16,10 20,18", stroke=SK, w=1.2) + path("M6,9 C9,4 15,4 18,9", stroke=SK, w=1.2)
    + line((4, 18), (6, 9), GRN, 1.0) + line((20, 18), (18, 9), GRN, 1.0))
I["helix_boss"] = svg(
    "".join(path(f"M5,{19-4*i} C5,{21-4*i} 19,{17-4*i} 19,{15-4*i}", stroke=AMB["edge"], w=3.4) +
            path(f"M5,{19-4*i} C5,{21-4*i} 19,{17-4*i} 19,{15-4*i}", stroke=AMB["left"], w=2.3) for i in range(4))
    + line((12, 1.5), (12, 22.5), SK, 0.9, "2,1.2"))
I["helix_cut"] = svg(
    cyl(12, 20, 7.5, 2.6, 15, GRY)
    + "".join(path(f"M4.5,{18-4*i} C6,{20-4*i} 18,{16-4*i} 19.5,{14-4*i}", stroke="#FFF4D6", w=1.6) for i in range(3))
    + "".join(path(f"M4.5,{18-4*i} C6,{20-4*i} 18,{16-4*i} 19.5,{14-4*i}", stroke=AMB["edge"], w=0.6) for i in range(3)))

# ---- features: modify
I["fillet"] = svg(
    poly([iso(0, 0, 0), iso(10, 0, 0), iso(10, 10, 0), iso(0, 10, 0)], GRY["right"], GRY["edge"], 0.5)
    + box(0, 0, 0, 10, 10, 5, GRY)
    + path(f"M{iso(10,0,5)[0]:.2f},{iso(10,0,5)[1]:.2f} L{iso(10,10,5)[0]:.2f},{iso(10,10,5)[1]:.2f}", stroke=AMB["edge"], w=3.6)
    + path(f"M{iso(10,0,5)[0]:.2f},{iso(10,0,5)[1]:.2f} L{iso(10,10,5)[0]:.2f},{iso(10,10,5)[1]:.2f}", stroke=AMB["top"], w=2.4)
    + path("M3,6 Q3,3 6,3", stroke=RED, w=1.2) + arrow((7.5, 3.0), (iso(10, 3, 5)[0] - 0.5, iso(10, 3, 5)[1] - 0.6), RED, 1.0, 2.2))
I["chamfer"] = svg(
    box(0, 0, 0, 10, 10, 5, GRY)
    + poly([iso(8, 0, 5), iso(8, 10, 5), iso(10, 10, 3), iso(10, 0, 3)], AMB["top"], AMB["edge"], 0.6)
    + poly([iso(10, 10, 3), iso(8, 10, 5), iso(8, 10, 5.01)], AMB["left"], AMB["edge"], 0.6)
    + line((3.5, 3.5), (7, 6.5), RED, 1.1) + poly([(7.6, 7.1), (5.4, 6.9), (7.0, 5.2)], RED, RED, 0.3))
I["shell"] = svg(
    box(0, 0, 0, 10, 10, 6, AMB)
    + poly([iso(1.6, 1.6, 6), iso(8.4, 1.6, 6), iso(8.4, 8.4, 6), iso(1.6, 8.4, 6)], "#8A5A10", AMB["edge"], 0.5)
    + poly([iso(1.6, 1.6, 6), iso(8.4, 1.6, 6), iso(8.4, 1.6, 1.6), iso(1.6, 1.6, 1.6)], AMB["right"], AMB["edge"], 0.4)
    + poly([iso(1.6, 1.6, 6), iso(1.6, 8.4, 6), iso(1.6, 8.4, 1.6), iso(1.6, 1.6, 1.6)], AMB["left"], AMB["edge"], 0.4)
    + poly([iso(1.6, 1.6, 1.6), iso(8.4, 1.6, 1.6), iso(8.4, 8.4, 1.6), iso(1.6, 8.4, 1.6)], AMB["top"], AMB["edge"], 0.4))
I["draft"] = svg(
    poly([(4, 20), (12, 22.5), (20, 20), (12, 17.5)], GRY["right"], GRY["edge"], 0.5)
    + poly([(4, 20), (7, 7), (12, 8.6), (12, 22.5)], AMB["left"], AMB["edge"], 0.6)
    + poly([(12, 22.5), (12, 8.6), (17, 7), (20, 20)], AMB["right"], AMB["edge"], 0.6)
    + poly([(7, 7), (12, 5.4), (17, 7), (12, 8.6)], AMB["top"], AMB["edge"], 0.6)
    + line((20, 20), (20, 5), SK, 0.8, "1.5,1") + path("M20,9 A4,4 0 0 0 17.8,8.2", stroke=RED, w=1.0))
I["hole_wizard"] = svg(
    box(0, 0, 0, 11, 11, 6, GRY)
    + '<ellipse cx="%.2f" cy="%.2f" rx="4.6" ry="2.6" fill="#FFF4D6" stroke="%s" stroke-width="0.7"/>' % (iso(5.5, 5.5, 6)[0], iso(5.5, 5.5, 6)[1], AMB["edge"])
    + '<ellipse cx="%.2f" cy="%.2f" rx="2.6" ry="1.5" fill="%s" stroke="%s" stroke-width="0.6"/>' % (iso(5.5, 5.5, 6)[0], iso(5.5, 5.5, 6)[1] + 0.6, AMB["right"], AMB["edge"])
    + '<ellipse cx="%.2f" cy="%.2f" rx="1.3" ry="0.75" fill="#5A3A05"/>' % (iso(5.5, 5.5, 6)[0], iso(5.5, 5.5, 6)[1] + 1.0)
    + '<path d="M18.5,2.5 l0.9,1.9 2.1,0.3 -1.5,1.5 0.4,2.1 -1.9,-1 -1.9,1 0.4,-2.1 -1.5,-1.5 2.1,-0.3 z" fill="#FFD43B" stroke="#B07D00" stroke-width="0.5"/>')
I["rib"] = svg(
    box(0, 0, 0, 12, 3, 3, GRY) + box(0, 0, 0, 3, 12, 3, GRY, oy=14)
    + poly([iso(3, 3, 3), iso(9, 3, 3), iso(3, 3, 9)], AMB["right"], AMB["edge"], 0.6)
    + poly([iso(3, 3, 3), iso(3, 9, 3), iso(3, 3, 9)], AMB["left"], AMB["edge"], 0.6))
I["thicken"] = svg(
    path("M3,14 C8,8 16,8 21,14", stroke=SK, w=1.2) + path("M3,18 C8,12 16,12 21,18 L21,14 C16,8 8,8 3,14 Z", fill=AMB["left"], stroke=AMB["edge"], w=0.6)
    + arrow((12, 10), (12, 3.5)))
I["offset_surface"] = svg(
    path("M3,18 C8,12 16,12 21,18", stroke=BLU["edge"], w=2) + path("M3,12 C8,6 16,6 21,12", stroke=GRN, w=1.2, extra='stroke-dasharray="2,1"')
    + arrow((12, 14), (12, 9.5)))
I["scale"] = svg(box(0, 0, 0, 5, 5, 5, GRY, ox=8, oy=18) + box(0, 0, 0, 9, 9, 9, AMB, ox=13, oy=16).replace('fill="#', 'fill-opacity="0.55" fill="#') + arrow((9, 15), (17, 6)))
I["split"] = svg(box(0, 0, 0, 10, 10, 6, AMB) + plane_shape(12, 11, 10, 6, "#BFD7FF", BLU["edge"], 0.75))
I["combine"] = svg(box(0, 0, 0, 7, 7, 7, AMB, ox=9, oy=13) + box(0, 0, 0, 7, 7, 5, GRY, ox=15, oy=18) + plus((19, 5)))
I["intersect"] = svg(
    circ((9, 12), 6, AMB["top"], AMB["edge"], 0.7, 'fill-opacity="0.7"') + circ((15, 12), 6, GRY["top"], GRY["edge"], 0.7, 'fill-opacity="0.7"')
    + path("M12,7.0 A6,6 0 0 1 12,17.0 A6,6 0 0 1 12,7.0 Z", fill=AMB["left"], stroke=AMB["edge"], w=0.7))
I["move_body"] = svg(box(0, 0, 0, 7, 7, 7, AMB, ox=12, oy=15) + arrow((12, 12), (20.5, 12)) + arrow((12, 12), (12, 2)) + arrow((12, 12), (5, 18.5)))
I["delete_face"] = svg(box(0, 0, 0, 10, 10, 6, GRY) + poly([iso(0, 0, 6), iso(10, 0, 6), iso(10, 10, 6), iso(0, 10, 6)], "#FFFFFF", RED, 0.9, 'stroke-dasharray="1.4,0.9"') + line((16, 2), (22, 8), RED, 1.6) + line((22, 2), (16, 8), RED, 1.6))

# ---- patterns / mirror
I["linear_pattern"] = svg(
    "".join(box(0, 0, 0, 4, 4, 4, AMB if i == 0 else dict(AMB, top="#FFF0C2", left="#F7D388", right="#E6B45C"), ox=5 + 6 * i, oy=15 - 0.0) for i in range(3))
    + arrow((3, 21), (21, 21), GRN, 1.2, 2.6))
I["circular_pattern"] = svg(
    circ((12, 12), 7.5, "none", SK, 0.8, 'stroke-dasharray="1.5,1"') + line((12, 2), (12, 22), SK, 0.8, "2,1")
    + "".join(box(0, 0, 0, 3, 3, 3, AMB, ox=12 + 7.5 * math.cos(a), oy=13.5 + 7.5 * math.sin(a)) for a in [math.radians(d) for d in (-90, -18, 54, 126, 198)]))
I["mirror"] = svg(
    plane_shape(12, 12, 3, 9, "#BFD7FF", BLU["edge"], 0.6)
    + box(0, 0, 0, 4, 4, 5, AMB, ox=6, oy=16) + box(0, 0, 0, 4, 4, 5, dict(AMB, top="#FFF0C2", left="#F7D388", right="#E6B45C"), ox=18, oy=16)
    + path("M7,4 C10,1.5 14,1.5 17,4", stroke=GRN, w=1.1) + poly([(17.8, 4.8), (15.6, 4.5), (17.2, 2.6)], GRN, GRN, 0.3))
I["multi_transform"] = svg(
    "".join(box(0, 0, 0, 3.5, 3.5, 3.5, AMB, ox=6 + 6 * i, oy=10 + 7 * j) for i in range(2) for j in range(2))
    + arrow((3, 22), (21, 22), GRN, 1.1, 2.4) + arrow((2, 22), (2, 3), GRN, 1.1, 2.4))
I["curve_pattern"] = svg(path("M3,20 C6,6 18,6 21,20", stroke=SK, w=1.0, extra='stroke-dasharray="1.5,1"')
                         + "".join(box(0, 0, 0, 3, 3, 3, AMB, ox=x, oy=y) for x, y in [(4.5, 17), (9, 10.2), (15, 10.2), (19.5, 17)]))

# ---- reference geometry
I["plane"] = svg(plane_shape(12, 12, 10, 7))
I["axis"] = svg(plane_shape(12, 13, 9, 6, "#E9EEF5", "#8C96A3", 0.7) + line((3, 21), (21, 3), SKD, 1.4, "3,1.4,0.8,1.4"))
I["point"] = svg(plane_shape(12, 13, 9, 6, "#E9EEF5", "#8C96A3", 0.7)
                 + '<path d="M12,6.5 l1.5,3.8 4,0.3 -3.1,2.6 1,3.9 -3.4,-2.1 -3.4,2.1 1,-3.9 -3.1,-2.6 4,-0.3z" fill="#FF6A3D" stroke="#9E2A0B" stroke-width="0.6"/>')
I["coordinate_system"] = svg(arrow((8, 16), (20, 16), RED, 1.6) + arrow((8, 16), (8, 3), "#2E9E3A", 1.6) + arrow((8, 16), (3, 21.5), "#1F5FD1", 1.6) + dot((8, 16), 1.6, INK))
I["ref_geometry"] = svg(plane_shape(12, 14, 10, 6) + line((12, 2), (12, 22), SKD, 1.1, "3,1.2,0.8,1.2")
                        + '<path d="M18,4 l1,2.3 2.4,0.2 -1.8,1.5 0.6,2.3 -2.2,-1.3 -2.2,1.3 0.6,-2.3 -1.8,-1.5 2.4,-0.2z" fill="#FF6A3D" stroke="#9E2A0B" stroke-width="0.5"/>')
I["mate_reference"] = svg(plane_shape(12, 14, 10, 6) + dot((12, 12), 2.0, RED))

# ---- sketch tools
SKBG = '<rect x="2.5" y="4.5" width="15" height="15" rx="1" fill="#FFFFFF" stroke="#9FB6DA" stroke-width="0.8"/>'
I["sketch"] = svg(SKBG + path("M5,16 L5,9 L10,9 A4,4 0 0 1 14,13 L14,16 Z", stroke=SK, w=1.4) + pencil(14, 2.5))
I["exit_sketch"] = svg(SKBG + path("M5,16 L5,9 L13,9 L13,16 Z", stroke=SK, w=1.3) + path("M14,12 L22,12", stroke=GRN, w=2) + poly([(22.8, 12), (19, 9.2), (19, 14.8)], GRN, GRN, 0.3))
I["smart_dimension"] = svg(
    line((3, 19), (21, 5), INK, 1.0)
    + line((2.5, 13.5), (8.5, 21.5), INK, 0.8) + line((15.5, 2.5), (21.5, 10.5), INK, 0.8)
    + poly([(3, 19), (6.6, 17.5), (5.1, 15.6)], INK, INK, 0.2) + poly([(21, 5), (17.4, 6.5), (18.9, 8.4)], INK, INK, 0.2)
    + '<path d="M15,15 l4,0 l-2,4 z" fill="#E8A317" stroke="#8A5A00" stroke-width="0.5"/>'
    + '<text x="8.6" y="10.8" font-family="Arial" font-weight="bold" font-size="6.2" fill="%s" transform="rotate(-38 10 10)">D</text>' % SKD)
I["line"] = svg(line((4, 19), (20, 5), SK, 1.8) + dot((4, 19), 1.7) + dot((20, 5), 1.7))
I["centerline"] = svg(line((3, 20), (21, 4), SK, 1.3, "4,1.5,1,1.5") + dot((3, 20), 1.5) + dot((21, 4), 1.5))
I["polyline"] = svg(path("M3,19 L8,6 L15,15 L21,4", stroke=SK, w=1.6) + "".join(dot(p, 1.4) for p in [(3, 19), (8, 6), (15, 15), (21, 4)]))
I["corner_rectangle"] = svg(path("M4,6 L20,6 L20,18 L4,18 Z", stroke=SK, w=1.6) + dot((4, 18), 1.6) + dot((20, 6), 1.6))
I["center_rectangle"] = svg(path("M4,6 L20,6 L20,18 L4,18 Z", stroke=SK, w=1.6) + line((4, 18), (20, 6), SK, 0.8, "1.6,1") + dot((12, 12), 1.6) + dot((20, 6), 1.6))
I["slot_rectangle"] = svg(path("M7,7 L17,7 A5,5 0 0 1 17,17 L7,17 A5,5 0 0 1 7,7 Z", stroke=SK, w=1.6) + line((7, 12), (17, 12), SK, 0.8, "1.6,1") + dot((7, 12), 1.4) + dot((17, 12), 1.4))
I["circle"] = svg(circ((12, 12), 8, "none", SK, 1.7) + dot((12, 12), 1.5) + line((12, 12), (17.6, 6.4), SK, 0.8, "1.4,1"))
I["perimeter_circle"] = svg(circ((12, 12), 8, "none", SK, 1.7) + dot((4.2, 13.8), 1.5) + dot((17, 5.8), 1.5) + dot((15.5, 19.2), 1.5))
I["arc"] = svg(path("M4,17 A8,8 0 0 1 20,17", stroke=SK, w=1.8) + dot((12, 17), 1.5) + dot((4, 17), 1.5) + dot((20, 17), 1.5) + line((12, 17), (4, 17), SK, 0.7, "1.4,1"))
I["three_point_arc"] = svg(path("M4,17 A8,8 0 0 1 20,17", stroke=SK, w=1.8) + dot((4, 17), 1.5) + dot((20, 17), 1.5) + dot((12, 9), 1.5))
I["tangent_arc"] = svg(line((3, 19), (11, 19), SK, 1.6) + path("M11,19 A5,5 0 0 0 11,9", stroke=SK, w=1.8) + dot((11, 19), 1.5) + dot((11, 9), 1.5))
I["ellipse"] = svg('<ellipse cx="12" cy="12" rx="9" ry="5.5" fill="none" stroke="%s" stroke-width="1.7"/>' % SK + dot((12, 12), 1.5) + line((12, 12), (21, 12), SK, 0.7, "1.4,1"))
I["partial_ellipse"] = svg(path("M3,13 A9,5.5 0 0 1 19,8", stroke=SK, w=1.7) + dot((12, 13), 1.5) + dot((3, 13), 1.4) + dot((19, 8), 1.4))
I["parabola"] = svg(path("M4,4 Q12,30 20,4", stroke=SK, w=1.7) + dot((12, 13), 1.4))
I["spline"] = svg(path("M3,17 C7,3 13,21 21,6", stroke=SK, w=1.7) + "".join(dot(p, 1.4) for p in [(3, 17), (12, 12.5), (21, 6)]))
I["style_spline"] = svg(path("M3,17 C7,3 13,21 21,6", stroke=SK, w=1.7) + path("M3,17 L7,3 L13,21 L21,6", stroke="#8C96A3", w=0.7, extra='stroke-dasharray="1.2,0.9"') + "".join(dot(p, 1.3, "#6B7280") for p in [(7, 3), (13, 21)]))
I["polygon"] = svg(poly([(12, 3.5), (19.5, 8), (19.5, 16), (12, 20.5), (4.5, 16), (4.5, 8)], "none", SK, 1.7) + circ((12, 12), 8.5, "none", SK, 0.6, 'stroke-dasharray="1.4,1"') + dot((12, 12), 1.4))
I["sketch_point"] = svg(dot((12, 12), 2.6) + line((5, 12), (9, 12), SK, 0.8) + line((15, 12), (19, 12), SK, 0.8) + line((12, 5), (12, 9), SK, 0.8) + line((12, 15), (12, 19), SK, 0.8))
I["sketch_fillet"] = svg(path("M4,20 L4,11 A7,7 0 0 1 11,4 L20,4", stroke=SK, w=1.7) + path("M4,8 L4,4 L8,4", stroke="#8C96A3", w=0.8, extra='stroke-dasharray="1.2,0.9"'))
I["sketch_chamfer"] = svg(path("M4,20 L4,10 L10,4 L20,4", stroke=SK, w=1.7) + path("M4,8 L4,4 L8,4", stroke="#8C96A3", w=0.8, extra='stroke-dasharray="1.2,0.9"'))
I["trim"] = svg(line((3, 12), (21, 12), SK, 1.6) + line((8, 4), (8, 20), SK, 1.6) + line((16, 4), (16, 20), SK, 1.6)
                + line((8.8, 12), (15.2, 12), "#FFFFFF", 2.6) + line((8.8, 12), (15.2, 12), RED, 1.0, "1.4,1")
                + '<path d="M11,15 l2,6 M13,15 l-2,6" stroke="%s" stroke-width="1"/>' % INK + circ((10.6, 21.4), 1.0, "none", INK, 0.8) + circ((13.4, 21.4), 1.0, "none", INK, 0.8))
I["extend"] = svg(line((19, 3), (19, 21), SK, 1.6) + line((3, 12), (11, 12), SK, 1.6) + line((11, 12), (19, 12), GRN, 1.2, "1.6,1") + poly([(19, 12), (15.5, 9.8), (15.5, 14.2)], GRN, GRN, 0.3))
I["offset_entities"] = svg(path("M4,19 L4,9 A5,5 0 0 1 9,4 L19,4", stroke=SK, w=1.6) + path("M8,19 L8,10.5 A2.5,2.5 0 0 1 10.5,8 L19,8", stroke=GRN, w=1.3, extra='stroke-dasharray="1.8,1"') + arrow((14, 4.5), (14, 8.0), INK, 0.8, 1.8))
I["convert_entities"] = svg(box(0, 0, 0, 10, 10, 5, GRY) + poly([iso(0, 0, 5), iso(10, 0, 5), iso(10, 10, 5), iso(0, 10, 5)], "none", SK, 1.6) + path("M17,3 L21,3 L21,7", stroke=GRN, w=1.2) + line((21, 3), (16.5, 7.5), GRN, 1.2))
I["intersection_curve"] = svg(box(0, 0, 0, 10, 10, 5, GRY) + plane_shape(12, 12, 10, 6, "#BFD7FF", BLU["edge"], 0.45) + line(iso(0, 5, 5), iso(10, 5, 5), SK, 1.8))
I["mirror_entities"] = svg(line((12, 2), (12, 22), SK, 1.0, "3,1.2,0.8,1.2") + path("M3,18 L3,7 L9,7", stroke=SK, w=1.6) + path("M21,18 L21,7 L15,7", stroke=GRN, w=1.4, extra='stroke-dasharray="1.8,1"'))
I["linear_sketch_pattern"] = svg("".join(circ((5 + 7 * i, 8), 2.4, "none", SK if i == 0 else GRN, 1.4) for i in range(3)) + "".join(circ((5 + 7 * i, 16.5), 2.4, "none", GRN, 1.4) for i in range(3)) + arrow((2, 22.2), (22, 22.2), INK, 0.8, 1.8))
I["circular_sketch_pattern"] = svg(dot((12, 12), 1.3, INK) + "".join(circ((12 + 7 * math.cos(math.radians(a)), 12 + 7 * math.sin(math.radians(a))), 2.2, "none", SK if a == -90 else GRN, 1.4) for a in range(-90, 270, 60)))
I["move_entities"] = svg(path("M3,10 L9,10 L9,16 L3,16 Z", stroke="#8C96A3", w=1.0, extra='stroke-dasharray="1.4,1"') + path("M13,6 L20,6 L20,13 L13,13 Z", stroke=SK, w=1.6) + arrow((8, 13), (14, 9), GRN, 1.3, 2.4))
I["copy_entities"] = svg(path("M3,10 L9,10 L9,16 L3,16 Z", stroke=SK, w=1.6) + path("M13,6 L20,6 L20,13 L13,13 Z", stroke=SK, w=1.6) + plus((17, 19), GRN, 3))
I["rotate_entities"] = svg(path("M5,17 L13,17 L13,11 L5,11 Z", stroke="#8C96A3", w=1.0, extra='stroke-dasharray="1.4,1"') + poly([(9, 3), (16, 7), (13, 12.2), (6, 8.2)], "none", SK, 1.6) + path("M18,16 A7,7 0 0 0 17,8", stroke=GRN, w=1.3) + poly([(17, 7), (15.4, 9.4), (18.4, 9.6)], GRN, GRN, 0.3) + dot((5, 17), 1.4, INK))
I["scale_entities"] = svg(path("M3,13 L9,13 L9,19 L3,19 Z", stroke="#8C96A3", w=1.0, extra='stroke-dasharray="1.4,1"') + path("M3,4 L19,4 L19,19 L3,19 Z", stroke=SK, w=1.6) + arrow((9, 13), (16, 7), GRN, 1.2, 2.4))
I["stretch_entities"] = svg(path("M3,8 L12,8 L12,17 L3,17 Z", stroke="#8C96A3", w=1.0, extra='stroke-dasharray="1.4,1"') + path("M3,8 L20,8 L20,17 L3,17 Z", stroke=SK, w=1.6) + arrow((12, 12.5), (19.5, 12.5), GRN, 1.2, 2.2))
I["split_entities"] = svg(line((3, 12), (11, 12), SK, 1.7) + line((13, 12), (21, 12), SK, 1.7) + dot((12, 12), 2.0, RED))
I["construction"] = svg(line((3, 20), (21, 4), "#E07B00", 1.6, "3,1.6") + dot((3, 20), 1.5, "#B35F00") + dot((21, 4), 1.5, "#B35F00") + circ((7, 7), 3.6, "none", SK, 1.2))
I["sketch_text"] = svg('<text x="3" y="18" font-family="Arial" font-weight="bold" font-size="15" fill="none" stroke="%s" stroke-width="1">A</text>' % SK + line((3, 20.5), (21, 20.5), SK, 0.8, "1.4,1"))
I["relations"] = svg('<rect x="3" y="3" width="8" height="8" rx="1.2" fill="#2EA043" stroke="#1B6E2C" stroke-width="0.6"/>'
                     + line((5, 7), (9, 7), "#FFFFFF", 1.3) + '<rect x="13" y="13" width="8" height="8" rx="1.2" fill="#2EA043" stroke="#1B6E2C" stroke-width="0.6"/>'
                     + line((17, 15), (17, 19), "#FFFFFF", 1.3) + line((11, 11), (13, 13), INK, 0.8))
I["delete_relations"] = svg(I["relations"][I["relations"].index("</defs>") + 7:-6] .join(["", ""]) if False else
                            svg('<rect x="3" y="3" width="8" height="8" rx="1.2" fill="#2EA043" stroke="#1B6E2C" stroke-width="0.6"/>' + line((5, 7), (9, 7), "#FFFFFF", 1.3)
                                + line((13, 13), (21, 21), RED, 2) + line((21, 13), (13, 21), RED, 2))[0:])
I["fully_define"] = svg(path("M4,17 L4,7 L20,7 L20,17 Z", stroke=INK, w=1.6) + line((4, 4), (20, 4), INK, 0.7) + line((22, 7), (22, 17), INK, 0.7)
                        + '<rect x="9" y="14" width="6" height="6" rx="1" fill="#2EA043"/>' + path("M10.3,17 L11.8,18.5 L14,15.6", stroke="#FFFFFF", w=1.1))
I["repair_sketch"] = svg(SKBG + path("M5,16 L5,9 L13,9 L13,16", stroke=SK, w=1.3) + '<path d="M15,21 l6,-6 M19,13 a2.5,2.5 0 1 0 3,3" stroke="%s" stroke-width="1.6" fill="none" stroke-linecap="round"/>' % INK)
I["normal_to_sketch"] = svg(SKBG + path("M5,16 L5,9 L13,9 L13,16 Z", stroke=SK, w=1.3) + arrow((19.5, 21), (19.5, 6), GRN, 1.4, 2.6))

# ---- evaluate
I["measure"] = svg('<g transform="rotate(-35 12 12)"><rect x="1" y="8.5" width="22" height="7" rx="1" fill="#FFE08A" stroke="#8A5A00" stroke-width="0.7"/>'
                   + "".join(line((3 + 2.5 * i, 8.6), (3 + 2.5 * i, 11.2 if i % 2 else 12.6), "#5A3A05", 0.7) for i in range(8)) + "</g>")
I["mass_properties"] = svg(line((12, 4), (12, 20), INK, 1.4) + line((4, 7), (20, 7), INK, 1.4) + line((7, 21), (17, 21), INK, 1.8)
                           + path("M4,7 L1.5,13 L6.5,13 Z", fill="#CFE2FF", stroke=SKD, w=0.8) + path("M20,7 L17.5,13 L22.5,13 Z", fill="#FFE08A", stroke=AMB["edge"], w=0.8)
                           + circ((12, 4), 1.5, INK, INK, 0.5))
I["section_properties"] = svg(box(0, 0, 0, 10, 10, 6, GRY) + poly([iso(0, 5, 0), iso(10, 5, 0), iso(10, 5, 6), iso(0, 5, 6)], "#FFB8A8", RED, 0.8) + dot(iso(5, 5, 3), 1.2, RED))
I["interference"] = svg(box(0, 0, 0, 7, 7, 7, GRY, ox=9, oy=14) + box(0, 0, 0, 7, 7, 7, BLU, ox=15, oy=17) + '<circle cx="12.6" cy="12.6" r="3.2" fill="#FF3B30" fill-opacity="0.8" stroke="#8B0000" stroke-width="0.6"/>')
I["check"] = svg(box(0, 0, 0, 9, 9, 7, GRY) + circ((17.5, 6.5), 5, "#2EA043", "#1B6E2C", 0.7) + path("M15,6.6 L17,8.6 L20.3,4.6", stroke="#FFFFFF", w=1.5))
I["section_view"] = svg(box(0, 0, 0, 11, 11, 7, AMB) + poly([iso(5.5, 0, 0), iso(5.5, 11, 0), iso(5.5, 11, 7), iso(5.5, 0, 7)], "#BFD7FF", BLU["edge"], 0.8, 'fill-opacity="0.8"')
                       + poly([iso(5.5, 0, 7), iso(11, 0, 7), iso(11, 11, 7), iso(5.5, 11, 7)], "#FFFFFF", "#FFFFFF", 0.1, 'fill-opacity="0.0"'))
I["bounding_box"] = svg(box(1, 1, 0, 7, 7, 6, AMB) + poly([iso(0, 0, 7), iso(9, 0, 7), iso(9, 9, 7), iso(0, 9, 7)], "none", SK, 0.8, 'stroke-dasharray="1.4,0.9"')
                        + line(iso(9, 9, 0), iso(9, 9, 7), SK, 0.8, "1.4,0.9") + line(iso(0, 9, 0), iso(0, 9, 7), SK, 0.8, "1.4,0.9") + line(iso(9, 0, 0), iso(9, 0, 7), SK, 0.8, "1.4,0.9"))
I["curvature"] = svg(path("M3,18 C8,4 16,4 21,18", stroke=INK, w=1.6) + "".join(line((x, y), (x + dx, y + dy), RED, 0.8) for x, y, dx, dy in [(5, 13.5, -2, -2), (8, 9, -1, -3.5), (12, 7.5, 0, -4.5), (16, 9, 1, -3.5), (19, 13.5, 2, -2)])
                     + path("M3,11.5 C6,5 8,4.5 12,3 C16,4.5 18,5 21,11.5", stroke=RED, w=0.9))
I["zebra"] = svg(path("M3,20 C8,6 16,6 21,20 Z", fill=INK, stroke=INK, w=0.6) + "".join(path(f"M{3+i*1.6},20 C{8+i*0.6},{8+i*1.3} {16-i*0.6},{8+i*1.3} {21-i*1.6},20", stroke="#FFFFFF", w=0.9) for i in range(0, 6, 2)))

# ---- assembly
I["insert_component"] = svg(box(0, 0, 0, 9, 9, 9, AMB, ox=11, oy=15) + plus((18.5, 5.5)))
I["new_part"] = svg(box(0, 0, 0, 9, 9, 9, GRY, ox=11, oy=15) + '<path d="M17,2 l1.1,2.6 2.8,0.2 -2.1,1.8 0.7,2.7 -2.5,-1.5 -2.5,1.5 0.7,-2.7 -2.1,-1.8 2.8,-0.2z" fill="#FFD43B" stroke="#B07D00" stroke-width="0.5"/>')
I["new_assembly"] = svg(box(0, 0, 0, 6, 6, 6, AMB, ox=8, oy=12) + box(0, 0, 0, 6, 6, 6, GRY, ox=15, oy=17) + plus((18.5, 5.5)))
I["mate"] = svg('<path d="M9,20 L9,7 A3.5,3.5 0 0 1 16,7 L16,17 A2,2 0 0 1 12,17 L12,8" fill="none" stroke="#5A6472" stroke-width="2.1" stroke-linecap="round"/>'
                '<path d="M9,20 L9,7 A3.5,3.5 0 0 1 16,7 L16,17 A2,2 0 0 1 12,17 L12,8" fill="none" stroke="#D6DCE4" stroke-width="0.9" stroke-linecap="round"/>')
I["mate_fixed"] = svg(I["mate"][I["mate"].index("</defs>") + 7:-6] if False else '<svg/>')  # replaced below
I["move_component"] = svg(box(0, 0, 0, 7, 7, 7, AMB, ox=12, oy=15) + arrow((12, 12), (21.5, 12), GRN, 1.3, 2.4) + arrow((12, 12), (2.5, 12), GRN, 1.3, 2.4) + arrow((12, 12), (12, 2), GRN, 1.3, 2.4) + arrow((12, 12), (12, 22), GRN, 1.3, 2.4))
I["rotate_component"] = svg(box(0, 0, 0, 7, 7, 7, AMB, ox=12, oy=15) + path("M4,15 A9,6 0 1 0 6,6", stroke=GRN, w=1.4) + poly([(6.6, 5.2), (4.2, 5.0), (5.4, 7.5)], GRN, GRN, 0.4))
I["fix_component"] = svg(box(0, 0, 0, 8, 8, 8, AMB, ox=12, oy=16) + '<rect x="14" y="13" width="8" height="6.5" rx="1" fill="#6B7280" stroke="#2B2F36" stroke-width="0.6"/>'
                         + path("M15.8,13 L15.8,10.8 A2.2,2.2 0 0 1 20.2,10.8 L20.2,13", stroke="#2B2F36", w=1.2))
I["exploded_view"] = svg(box(0, 0, 0, 5, 5, 3, AMB, ox=7, oy=20) + box(0, 0, 0, 5, 5, 3, GRY, ox=12, oy=12) + box(0, 0, 0, 5, 5, 3, BLU, ox=17, oy=5)
                         + line((9, 14), (12, 10), RED, 0.9, "1.2,0.9") + line((14, 6.5), (17, 3), RED, 0.9, "1.2,0.9"))
I["bom"] = svg('<rect x="3" y="3" width="18" height="18" rx="1" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + "".join(line((3, 3 + 4.5 * i), (21, 3 + 4.5 * i), INK, 0.7) for i in range(1, 4)) + line((8, 3), (8, 21), INK, 0.7)
               + '<rect x="3" y="3" width="18" height="4.5" fill="#CFE2FF" stroke="%s" stroke-width="0.7"/>' % INK)
I["solve_assembly"] = svg(box(0, 0, 0, 7, 7, 7, AMB, ox=10, oy=16) + path("M16,4 A6,6 0 1 1 10,10", stroke=GRN, w=1.6) + poly([(16.6, 1.8), (16.6, 6.4), (19.6, 4)], GRN, GRN, 0.3))

# ---- drawing
I["new_drawing"] = svg('<rect x="2.5" y="4" width="19" height="15" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + '<rect x="14" y="15" width="7.5" height="4" fill="none" stroke="%s" stroke-width="0.7"/>' % INK
                       + path("M5,15 L5,8 L11,8 L11,15 Z M7,8 L7,6 L13,6 L13,13 L11,13", stroke=SK, w=0.9))
I["model_view"] = svg('<rect x="2.5" y="4" width="19" height="15" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + box(0, 0, 0, 6, 6, 5, AMB, ox=12, oy=13.5))
I["standard_3view"] = svg('<rect x="2.5" y="3" width="19" height="18" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK
                          + path("M5,11 L5,6 L10,6 L10,11 Z M5,19 L5,13 L10,13 L10,19 Z M13,19 L13,13 L19,13 L19,19 Z", stroke=SK, w=1.0))
I["projected_view"] = svg('<rect x="2.5" y="4" width="19" height="15" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + path("M5,16 L5,10 L10,10 L10,16 Z", stroke=SK, w=1.0)
                          + path("M14,16 L14,10 L19,10 L19,16 Z", stroke=GRN, w=1.0, extra='stroke-dasharray="1.4,0.9"') + arrow((10.5, 13), (13.5, 13), GRN, 0.9, 1.8))
I["section_drawing_view"] = svg('<rect x="2.5" y="4" width="19" height="15" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK
                                + '<rect x="6" y="8" width="12" height="7" fill="url(#hatch)" stroke="%s" stroke-width="0.9"/>' % SK
                                + "".join(line((6 + i * 2.2, 15), (8.5 + i * 2.2, 8), SK, 0.5) for i in range(5))
                                + line((12, 2), (12, 21), RED, 0.9, "3,1,0.8,1") + poly([(12, 2), (9.5, 3.3), (12, 4.6)], RED, RED, 0.2))
I["detail_view"] = svg('<rect x="2.5" y="4" width="19" height="15" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + path("M4,16 L9,16 L9,11", stroke=SK, w=1.0)
                       + circ((8.5, 13.5), 3.2, "none", INK, 0.8) + circ((16, 11.5), 5, "#FFFFFF", INK, 0.9) + path("M12.5,15.5 L19.5,15.5 L19.5,8", stroke=SK, w=1.4))
I["broken_view"] = svg('<rect x="2.5" y="4" width="19" height="15" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + path("M4,9 L9,9 M4,15 L9,15 M15,9 L20,9 M15,15 L20,15", stroke=SK, w=1.0)
                       + path("M9,7 C10,10 8,13 9,17 M15,7 C16,10 14,13 15,17", stroke=INK, w=0.9))
I["note"] = svg('<text x="4" y="18" font-family="Arial" font-weight="bold" font-size="16" fill="%s">A</text>' % INK + line((16, 6), (21, 2.5), INK, 0.8) + poly([(16, 6), (17.8, 5.4), (17.2, 4.5)], INK, INK, 0.2))
I["balloon"] = svg(circ((14, 9), 6, "#FFFFFF", INK, 1.0) + '<text x="11.6" y="12" font-family="Arial" font-weight="bold" font-size="8" fill="%s">1</text>' % INK + line((9.6, 13), (3, 20.5), INK, 0.9) + dot((3, 20.5), 1.2, INK))
I["center_mark"] = svg(circ((12, 12), 7, "none", SK, 1.0) + line((2, 12), (22, 12), INK, 0.8, "4,1,1,1") + line((12, 2), (12, 22), INK, 0.8, "4,1,1,1"))
I["centerline_drawing"] = svg(line((5, 4), (5, 20), SK, 1.0) + line((19, 4), (19, 20), SK, 1.0) + line((12, 2), (12, 22), INK, 0.9, "4,1,1,1"))
I["hatch"] = svg('<rect x="4" y="4" width="16" height="16" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % SK + "".join(line((4 + i * 3.2, 20), (4 + i * 3.2 + 6, 4), SK, 0.6) for i in range(-1, 5)))
I["weld_symbol"] = svg(line((3, 15), (21, 15), INK, 1.0) + poly([(9, 15), (13, 15), (11, 11.5)], INK, INK, 0.4) + line((3, 15), (1.5, 21), INK, 0.9))
I["surface_finish"] = svg(path("M4,13 L8,20 L16,4 L22,4", stroke=INK, w=1.2))
I["dim_horizontal"] = svg(line((4, 6), (4, 20), INK, 0.7) + line((20, 6), (20, 20), INK, 0.7) + line((4, 12), (20, 12), INK, 0.9) + poly([(4, 12), (7, 10.8), (7, 13.2)], INK, INK, 0.2) + poly([(20, 12), (17, 10.8), (17, 13.2)], INK, INK, 0.2))
I["dim_vertical"] = svg(line((6, 4), (20, 4), INK, 0.7) + line((6, 20), (20, 20), INK, 0.7) + line((12, 4), (12, 20), INK, 0.9) + poly([(12, 4), (10.8, 7), (13.2, 7)], INK, INK, 0.2) + poly([(12, 20), (10.8, 17), (13.2, 17)], INK, INK, 0.2))
I["model_items"] = svg('<rect x="2.5" y="4" width="19" height="15" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + path("M6,15 L6,9 L13,9 L13,15 Z", stroke=SK, w=1.0)
                       + line((6, 7), (13, 7), INK, 0.6) + poly([(6, 7), (7.5, 6.4), (7.5, 7.6)], INK, INK, 0.1) + poly([(13, 7), (11.5, 6.4), (11.5, 7.6)], INK, INK, 0.1)
                       + '<path d="M17,9 l1,2.3 2.4,0.2 -1.8,1.5 0.6,2.3 -2.2,-1.3 -2.2,1.3 0.6,-2.3 -1.8,-1.5 2.4,-0.2z" fill="#FFD43B" stroke="#B07D00" stroke-width="0.5"/>')

# ---- sheet metal
SM = dict(top="#D7E4F2", left="#A9BFD8", right="#86A2C2", edge="#3B5675")
I["base_flange"] = svg(box(0, 0, 0, 12, 10, 1.4, SM) + arrow((12, 12), (12, 4), GRN, 1.2, 2.4))
I["edge_flange"] = svg(box(0, 0, 0, 12, 10, 1.4, SM) + poly([iso(12, 0, 1.4), iso(12, 10, 1.4), iso(12, 10, 10), iso(12, 0, 10)], SM["right"], SM["edge"], 0.6)
                       + poly([iso(10.6, 0, 1.4), iso(12, 0, 1.4), iso(12, 0, 10), iso(10.6, 0, 10)], SM["top"], SM["edge"], 0.5))
I["sketched_bend"] = svg(box(0, 0, 0, 7, 10, 1.4, SM) + poly([iso(7, 0, 1.4), iso(7, 10, 1.4), iso(7, 10, 8), iso(7, 0, 8)], SM["right"], SM["edge"], 0.6) + line(iso(7, -1, 1.6), iso(7, 11, 1.6), SK, 1.2, "2,1"))
I["unfold"] = svg(box(0, 0, 0, 14, 10, 1.0, SM, ox=8, oy=12) + line(iso(7, 0, 1.0, 8, 12), iso(7, 10, 1.0, 8, 12), SK, 0.9, "1.8,1")
                  + path("M15,5 A5,5 0 0 1 21,10", stroke=GRN, w=1.3) + poly([(21.6, 11), (19.4, 9.6), (22.2, 8.8)], GRN, GRN, 0.3))
I["fold"] = svg(box(0, 0, 0, 14, 10, 1.0, SM, ox=8, oy=12) + line(iso(7, 0, 1.0, 8, 12), iso(7, 10, 1.0, 8, 12), SK, 0.9, "1.8,1")
                + path("M21,10 A5,5 0 0 0 15,5", stroke=GRN, w=1.3) + poly([(14.2, 4.6), (16.6, 3.6), (16.2, 6.4)], GRN, GRN, 0.3))
I["corner_relief"] = svg(box(0, 0, 0, 12, 12, 1.4, SM) + circ(iso(12, 12, 1.4), 2.0, "#FFFFFF", RED, 0.8))
I["sheet_junction"] = svg(box(0, 0, 0, 12, 12, 1.4, SM) + line(iso(6, 0, 1.4), iso(6, 12, 1.4), RED, 1.4))

# ---- surfaces
I["surface_fill"] = svg(path("M4,17 C6,8 12,6 20,9 C21,13 19,19 12,21 C8,21 5,19 4,17 Z", fill=BLU["top"], stroke=BLU["edge"], w=0.8)
                        + path("M4,17 C6,8 12,6 20,9", stroke=SK, w=1.4) + path("M20,9 C21,13 19,19 12,21", stroke=SK, w=1.4))
I["surface_loft"] = svg(path("M3,19 C8,15 16,15 21,19 L19,6 C15,3 9,3 5,6 Z", fill=BLU["top"], stroke=BLU["edge"], w=0.8) + path("M3,19 C8,15 16,15 21,19", stroke=SK, w=1.3) + path("M5,6 C9,3 15,3 19,6", stroke=SK, w=1.3))
I["surface_extend"] = svg(path("M3,19 C8,13 12,13 14,13 L14,5 C12,5 8,5 3,11 Z", fill=BLU["top"], stroke=BLU["edge"], w=0.8) + path("M14,13 L21,13 L21,5 L14,5", stroke=GRN, w=1.1, extra='stroke-dasharray="1.6,1"'))
I["surface_blend"] = svg(path("M2,18 L9,18", stroke=SK, w=1.7) + path("M15,6 L22,6", stroke=SK, w=1.7) + path("M9,18 C14,18 10,6 15,6", stroke=GRN, w=1.5))
I["knit_surface"] = svg(path("M3,18 L11,14 L11,5 L3,9 Z", fill=BLU["top"], stroke=BLU["edge"], w=0.8) + path("M11,14 L21,17 L21,8 L11,5 Z", fill=BLU["left"], stroke=BLU["edge"], w=0.8) + line((11, 14), (11, 5), RED, 1.6))
I["ruled_surface"] = svg(path("M3,19 C8,15 16,15 21,19 L21,7 C16,3 8,3 3,7 Z", fill=BLU["top"], stroke=BLU["edge"], w=0.8) + "".join(line((3 + 4.5 * i, 19 - (i in (1, 2, 3)) * 2.6), (3 + 4.5 * i, 7 - (i in (1, 2, 3)) * 2.6), BLU["edge"], 0.6) for i in range(5)))

# ---- heads-up / view
I["zoom_fit"] = svg('<rect x="2.5" y="2.5" width="12" height="12" rx="1" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="2,1"/>' % INK + circ((10, 10), 5.5, "#EAF2FF", INK, 1.5) + line((14, 14), (21, 21), INK, 2.6) + box(0, 0, 0, 3, 3, 3, AMB, ox=10, oy=11.5))
I["zoom_area"] = svg('<rect x="3" y="3" width="11" height="9" fill="#FFFFFF" fill-opacity="0.5" stroke="%s" stroke-width="1" stroke-dasharray="1.6,1"/>' % SK + circ((11, 11), 5, "#EAF2FF", INK, 1.5) + line((14.5, 14.5), (21, 21), INK, 2.6))
I["previous_view"] = svg(circ((10, 11), 5.5, "#EAF2FF", INK, 1.5) + line((14, 15), (20, 21), INK, 2.5) + path("M14,3.5 C19,3.5 21,6 21,9", stroke=GRN, w=1.4) + poly([(12, 3.5), (15, 1.5), (15, 5.5)], GRN, GRN, 0.3))
I["zoom_in_out"] = svg(circ((10, 10), 6.5, "#EAF2FF", INK, 1.5) + line((14.5, 14.5), (21, 21), INK, 2.6) + line((7, 10), (13, 10), INK, 1.3) + line((10, 7), (10, 13), INK, 1.3))
I["view_orientation"] = svg(box(0, 0, 0, 10, 10, 10, dict(top="#FFFFFF", left="#C7D9F3", right="#9DBBE6", edge="#2A5BAE"), oy=17)
                            + '<text x="%.1f" y="%.1f" font-family="Arial" font-size="4" font-weight="bold" fill="#2A5BAE">TOP</text>' % (8.5, 8.3))
I["display_style"] = svg(box(0, 0, 0, 10, 10, 10, dict(top="#E9EDF2", left="#AEB6C2", right="#8A93A1", edge="#141820"), oy=17))
I["display_shaded"] = svg(box(0, 0, 0, 10, 10, 10, dict(top="#E9EDF2", left="#AEB6C2", right="#8A93A1", edge="#AEB6C2"), oy=17))
I["display_hlr"] = svg(box(0, 0, 0, 10, 10, 10, dict(top="#FFFFFF", left="#FFFFFF", right="#FFFFFF", edge="#141820"), oy=17))
I["display_wireframe"] = svg(box(0, 0, 0, 10, 10, 10, dict(top="none", left="none", right="none", edge="#141820"), oy=17)
                             + line(iso(0, 0, 0, oy=17), iso(10, 0, 0, oy=17), "#141820", 0.6) + line(iso(0, 0, 0, oy=17), iso(0, 10, 0, oy=17), "#141820", 0.6) + line(iso(0, 0, 0, oy=17), iso(0, 0, 10, oy=17), "#141820", 0.6))
I["hide_show"] = svg(path("M2,12 C6,5 18,5 22,12 C18,19 6,19 2,12 Z", fill="#FFFFFF", stroke=INK, w=1.2) + circ((12, 12), 3.8, "#5E93E0", INK, 0.8) + dot((12, 12), 1.6, INK))
I["appearance"] = svg(circ((12, 12), 8.5, "url(#cg%s)" % BLU["left"][1:], BLU["edge"], 0.7) + circ((9, 9), 2.4, "#FFFFFF", "none", 0, 'fill-opacity="0.7"')
                      + '<path d="M15,21 L22,14 L20,12 L13,19 Z" fill="#F2B53C" stroke="#7A4B06" stroke-width="0.6"/>')
I["scene"] = svg('<rect x="2" y="4" width="20" height="16" rx="1.5" fill="url(#bgsc)" stroke="%s" stroke-width="0.8"/>' % INK
                 + '<defs><linearGradient id="bgsc" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#9DB6D6"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient></defs>'
                 + '<ellipse cx="12" cy="17.5" rx="7" ry="1.5" fill="#000" fill-opacity="0.2"/>' + circ((12, 12), 4.5, "url(#cg%s)" % AMB["left"][1:], AMB["edge"], 0.6))
I["perspective"] = svg(path("M3,20 L9,6 L15,6 L21,20 Z", fill="#EAF2FF", stroke=INK, w=1.0) + line((6, 13), (18, 13), INK, 0.6) + line((12, 6), (12, 20), INK, 0.6))
I["normal_to"] = svg(plane_shape(12, 15, 9, 5) + arrow((12, 14), (12, 2.5), GRN, 1.6, 3))
I["rebuild"] = svg('<rect x="8" y="1.5" width="8" height="21" rx="2.2" fill="#3A3F47" stroke="#1C1F24" stroke-width="0.6"/>'
                   + circ((12, 6), 2.3, "#FF4B3E", "#7A140C", 0.5) + circ((12, 12), 2.3, "#FFC531", "#7A5A00", 0.5) + circ((12, 18), 2.3, "#3DDC6F", "#0E6B2B", 0.5))
I["force_rebuild"] = svg(I["rebuild"][I["rebuild"].index("</defs>") + 7:-6] if False else
                         '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
                         '<rect x="5" y="1.5" width="8" height="21" rx="2.2" fill="#3A3F47" stroke="#1C1F24" stroke-width="0.6"/>'
                         '<circle cx="9" cy="6" r="2.3" fill="#FF4B3E"/><circle cx="9" cy="12" r="2.3" fill="#FFC531"/><circle cx="9" cy="18" r="2.3" fill="#3DDC6F"/>'
                         '<path d="M15,8 L21,8 L18,4 Z M15,16 L21,16 L18,20 Z" fill="#FF8A00"/></svg>')
I["options"] = svg('<path d="M12,3.5 l1.6,0.3 0.5,2.1 1.4,0.6 1.8,-1.1 1.3,1 -1,1.9 0.6,1.4 2.1,0.6 0.2,1.6 -2,0.8 -0.4,1.5 1.2,1.8 -1,1.3 -2,-0.9 -1.3,0.8 -0.4,2.1 -1.6,0.3 -0.8,-2 -1.5,-0.3 -1.6,1.4 -1.4,-0.8 0.6,-2.1 -0.9,-1.2 -2.2,0 -0.5,-1.5 1.8,-1.2 0,-1.5 -1.8,-1.2 0.5,-1.5 2.2,0 0.9,-1.2 -0.6,-2.1 1.4,-0.8 1.6,1.4 1.5,-0.3z" fill="#9AA2AE" stroke="#2B2F36" stroke-width="0.6"/>' + circ((12, 12), 3, "#FFFFFF", "#2B2F36", 0.7))
I["search"] = svg(circ((10, 10), 6.5, "#FFFFFF", INK, 1.7) + line((14.6, 14.6), (21, 21), INK, 2.8))
I["selection_filter"] = svg(path("M3,4 L21,4 L14,12 L14,20 L10,18 L10,12 Z", fill="#CFE2FF", stroke=SKD, w=1.1))
I["filter_vertex"] = svg(I["selection_filter"][I["selection_filter"].index("<path"):-6].join(["", ""]) if False else svg(path("M3,4 L21,4 L14,12 L14,20 L10,18 L10,12 Z", fill="#CFE2FF", stroke=SKD, w=1.1) + dot((18.5, 18.5), 2.6, RED)))
I["filter_edge"] = svg(path("M3,4 L21,4 L14,12 L14,20 L10,18 L10,12 Z", fill="#CFE2FF", stroke=SKD, w=1.1) + line((15, 22), (22, 15), RED, 2))
I["filter_face"] = svg(path("M3,4 L21,4 L14,12 L14,20 L10,18 L10,12 Z", fill="#CFE2FF", stroke=SKD, w=1.1) + '<rect x="15" y="15" width="7" height="7" fill="#FF8A80" stroke="%s" stroke-width="0.8"/>' % RED)
I["clear_filters"] = svg(path("M3,4 L21,4 L14,12 L14,20 L10,18 L10,12 Z", fill="#E5E7EB", stroke="#6B7280", w=1.1) + line((15, 15), (22, 22), RED, 1.8) + line((22, 15), (15, 22), RED, 1.8))
I["new_document"] = svg('<path d="M5,2.5 L14,2.5 L19,7.5 L19,21.5 L5,21.5 Z" fill="#FFFFFF" stroke="%s" stroke-width="1"/>' % INK + path("M14,2.5 L14,7.5 L19,7.5", stroke=INK, w=1) + plus((17.5, 18), GRN, 3.6))
# "freeworks" (app mark) is generated from the owner's logo by tools/make_branding.py

# fix placeholders that referenced each other
I["mate_fixed"] = I["fix_component"]
I["delete_relations"] = svg('<rect x="3" y="3" width="8" height="8" rx="1.2" fill="#2EA043" stroke="#1B6E2C" stroke-width="0.6"/>' + line((5, 7), (9, 7), "#FFFFFF", 1.3)
                            + line((13, 13), (21, 21), RED, 2) + line((21, 13), (13, 21), RED, 2))
I["force_rebuild"] = I["force_rebuild"]

for k, v in I.items():
    with open(os.path.join(OUT, k + ".svg"), "w") as f:
        f.write(v)
print(len(I), "icons ->", os.path.abspath(OUT))
