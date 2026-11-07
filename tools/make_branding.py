#!/usr/bin/env python3
"""Build all FreeWorks branding from the owner's logo (docs/assets/logo_source.png).

Outputs
  Mod/FreeWorks/Resources/icons/freeworks.svg   vector app mark (UI logo button, workbench icon)
  branding/freeworks.png  (256 px window icon)   branding/freeworks.ico (16-256 px)
  branding/splash.png     (FreeCAD splash, full logo)
  docs/assets/logo.png    (trimmed full logo for README)  docs/assets/mark.svg

Requires: Pillow, rsvg-convert, ImageMagick `convert` (for .ico).
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "docs", "assets", "logo_source.png")

# Vector redraw of the logo mark (coordinates measured on the source logo, crop origin 60,270).
# Faces: light top, darker top strip, front of the top arm, navy stem side, middle bar.
MARK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">
<defs>
 <linearGradient id="stem" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E3A82"/><stop offset="1" stop-color="#0A2A63"/></linearGradient>
 <linearGradient id="arm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1667C9"/><stop offset="1" stop-color="#0F56B3"/></linearGradient>
 <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1767CC"/><stop offset="1" stop-color="#0D58B8"/></linearGradient>
</defs>
{crosshair}
<polygon points="88,162 180,205 180,407 88,357" fill="url(#stem)"/>
<polygon points="88,162 230,90 330,134 180,205" fill="#55AEF5"/>
<polygon points="330,134 397,161 180,205" fill="#1F74D6"/>
<polygon points="180,205 397,161 180,257" fill="url(#arm)"/>
<polygon points="220,282 350,225 350,290 220,345" fill="url(#bar)"/>
</svg>"""

CROSSHAIR = """<g fill="none" stroke="#7D8796" stroke-width="2.4" stroke-linecap="round">
 <path d="M 92,355 A 175 175 0 0 1 216,56"/>
 <path d="M 236,56 A 175 175 0 0 1 352,110" stroke-dasharray="9,8"/>
 <path d="M 120,378 A 175 175 0 0 0 232,404"/>
 <path d="M 60,372 A 175 175 0 0 1 48,300" stroke-dasharray="9,8"/>
 <line x1="215" y1="10" x2="215" y2="100"/>
 <line x1="5" y1="229" x2="88" y2="229"/>
 <line x1="222" y1="345" x2="222" y2="430"/>
 <line x1="198" y1="402" x2="262" y2="402"/>
</g>"""


def run(*cmd):
    subprocess.run(cmd, check=True)


def write_mark(path, size, crosshair=False):
    vb = "0 0 440 440" if crosshair else "80 80 330 330"
    with open(path, "w") as f:
        f.write(MARK.format(vb=vb, w=size, h=size, crosshair=CROSSHAIR if crosshair else ""))


def main():
    icons = os.path.join(ROOT, "Mod", "FreeWorks", "Resources", "icons")
    brand = os.path.join(ROOT, "branding")
    assets = os.path.join(ROOT, "docs", "assets")
    os.makedirs(brand, exist_ok=True)

    write_mark(os.path.join(icons, "freeworks.svg"), 24)
    write_mark(os.path.join(assets, "mark.svg"), 440, crosshair=True)

    tmp = "/tmp/fw_brand"
    os.makedirs(tmp, exist_ok=True)
    big = os.path.join(tmp, "mark.svg")
    write_mark(big, 256)
    pngs = []
    for s in (16, 20, 24, 32, 40, 48, 64, 128, 256):
        p = os.path.join(tmp, "m%d.png" % s)
        run("rsvg-convert", "-w", str(s), "-h", str(s), big, "-o", p)
        pngs.append(p)
    Image.open(os.path.join(tmp, "m256.png")).save(os.path.join(brand, "freeworks.png"))
    run("convert", *pngs, os.path.join(brand, "freeworks.ico"))

    # full logo, trimmed to its visible pixels
    logo = Image.open(SRC).convert("RGBA")
    bbox = logo.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    logo = logo.crop(bbox)
    w = 900
    logo.resize((w, int(logo.height * w / logo.width)), Image.LANCZOS).save(os.path.join(assets, "logo.png"))
    w2 = 420   # in-app copy (Welcome dialog, About)
    logo.resize((w2, int(logo.height * w2 / logo.width)), Image.LANCZOS).save(
        os.path.join(ROOT, "Mod", "FreeWorks", "Resources", "logo.png"))

    # splash 640x380: white card, logo, tagline, thin blue bar
    W, H = 640, 380
    sp = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(sp)
    for y in range(H):   # subtle vertical gradient
        t = y / H
        c = tuple(int(255 - t * (255 - v)) for v in (232, 238, 247))
        d.line([(0, y), (W, y)], fill=c)
    lw = 560
    lg = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    sp.paste(lg, ((W - lw) // 2, 70), lg)
    d.rectangle([0, 0, W, 5], fill="#0A4AA8")
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 12)
    except Exception:
        font = ImageFont.load_default()
    d.text((W - 20, H - 22), "powered by FreeCAD 1.1  ·  LGPL", fill="#6B7280", font=font, anchor="rs")
    sp.save(os.path.join(brand, "splash.png"))
    print("branding written")


if __name__ == "__main__":
    main()
