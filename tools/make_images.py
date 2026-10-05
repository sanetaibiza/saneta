"""
Genera las IMÁGENES PROVISIONALES de la web de SA NETA.

Son ilustraciones planas con la paleta del logo. Cada una lleva impreso el
texto "IMAGEN PROVISIONAL · nombre-del-archivo" para que sea evidente que
debe sustituirse por una fotografía real con el mismo nombre de archivo.

Uso:  python3 tools/make_images.py
"""
import math, random, pathlib, asyncio, io
from PIL import Image
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"
FONT = (ROOT / "assets" / "fonts" / "montserrat-latin.woff2").as_uri()
SERIF = (ROOT / "assets" / "fonts" / "playfair-display-latin.woff2").as_uri()

NAVY, NAVY2 = "#003469", "#0A2A52"
MED, MED2 = "#2E6CA8", "#5C92C8"
SUN, SKY, PALE = "#B7D7F3", "#EEF5FC", "#F6F9FD"
SHADE, SHADE2 = "#E4EDF7", "#D3E1F0"
GOLD = "#DDB05C"
WHITE = "#FFFFFF"


# ---------- primitivas ----------
def rect(x, y, w, h, fill, rx=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'

def circle(cx, cy, r, fill, extra=""):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" {extra}/>'

def arch_d(x, y, w, h):
    r = w / 2
    return f"M{x},{y+h} V{y+r} A{r},{r} 0 0 1 {x+w},{y+r} V{y+h} Z"

def arch(x, y, w, h, fill, extra=""):
    return f'<path d="{arch_d(x,y,w,h)}" fill="{fill}" {extra}/>'

def line(x1, y1, x2, y2, stroke, sw=2, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" {extra}/>'

def poly(pts, fill, extra=""):
    p = " ".join(f"{x},{y}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" {extra}/>'

def sky(w, h, top="#E3EEFA", bottom="#FBFDFF", gid="sky"):
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>'
            + rect(0, 0, w, h, f"url(#{gid})"))

def sea(x, y, w, h, gid="sea"):
    s = (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{MED}"/><stop offset="1" stop-color="#8DB7E0"/></linearGradient></defs>'
         + rect(x, y, w, h, f"url(#{gid})"))
    rnd = random.Random(int(x + y + w))
    for i in range(7):
        yy = y + h * (0.18 + 0.12 * i)
        xx = x + rnd.uniform(0.05, 0.7) * w
        ll = rnd.uniform(0.08, 0.2) * w
        s += line(xx, yy, min(xx + ll, x + w), yy, WHITE, 2, 'opacity=".55"')
    return s

def vedra(x, base, s=1.0, fill="#8FB6DE"):
    """Silueta de un islote rocoso en el horizonte."""
    pts = [(0, 0), (22, -38), (40, -52), (52, -96), (66, -120), (78, -104), (92, -92),
           (104, -58), (124, -40), (150, 0)]
    main = poly([(x + px * s, base + py * s) for px, py in pts], fill)
    pts2 = [(165, 0), (178, -20), (194, -30), (210, -14), (222, 0)]
    return main + poly([(x + px * s, base + py * s) for px, py in pts2], fill)

def sprig(x, y, ang, L, n, seed, col=NAVY, leaf=(20, 6.5), sw=2.2):
    rnd = random.Random(seed)
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    bend = rnd.uniform(-0.12, 0.12) * L
    out, prev = [], (x, y)
    pts = []
    for i in range(21):
        t = i / 20
        px = x + dx * L * t + nx * bend * math.sin(math.pi * t)
        py = y + dy * L * t + ny * bend * math.sin(math.pi * t)
        pts.append((px, py))
    d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>')
    for i in range(n):
        t = 0.22 + 0.78 * (i + 1) / n
        px, py = pts[min(20, int(t * 20))]
        side = 1 if i % 2 == 0 else -1
        la = ang + side * rnd.uniform(32, 52)
        if i == n - 1:
            la = ang + rnd.uniform(-8, 8)
        lr = math.radians(la)
        ll = leaf[0] * rnd.uniform(0.85, 1.2)
        cx, cy = px + math.cos(lr) * ll, py + math.sin(lr) * ll
        out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{ll:.1f}" ry="{leaf[1]}" fill="{col}" '
                   f'transform="rotate({la:.1f} {cx:.1f} {cy:.1f})"/>')
    return "".join(out)

def olive(x, y, s=1.0, seed=3, col=NAVY):
    """Olivo: (x,y) es la base del tronco."""
    rnd = random.Random(seed)
    top = (x + 14 * s, y - 210 * s)
    trunk = (f'<path d="M{x-26*s},{y} C{x-10*s},{y-70*s} {x-22*s},{y-120*s} {top[0]-9*s},{top[1]} '
             f'L{top[0]+9*s},{top[1]} C{x+16*s},{y-120*s} {x+22*s},{y-60*s} {x+30*s},{y} Z" fill="{col}"/>')
    out = [trunk]
    for i, ang in enumerate([-168, -146, -124, -104, -86, -66, -44, -22, -8]):
        L = rnd.uniform(150, 215) * s
        ox = top[0] + rnd.uniform(-8, 8) * s
        oy = top[1] + rnd.uniform(0, 34) * s
        out.append(sprig(ox, oy, ang + rnd.uniform(-6, 6), L, rnd.randint(8, 11), seed * 31 + i, col,
                         leaf=(19 * s, 6.2 * s), sw=2.4 * s))
    return "".join(out)

def pot(x, y, w, h, fill=WHITE, band=NAVY):
    """Maceta: (x,y) esquina superior izquierda."""
    t = w * 0.14
    body = poly([(x, y), (x + w, y), (x + w - t, y + h), (x + t, y + h)], fill, f'stroke="{SHADE2}" stroke-width="2"')
    rim = rect(x - 6, y - 10, w + 12, 16, fill, 4, f'stroke="{SHADE2}" stroke-width="2"')
    b = rect(x + t * 0.35, y + h * 0.36, w - t * 0.7, h * 0.12, band)
    return body + b + rim

def amphora(x, y, s=1.0, fill=NAVY):
    """Jarrón: (x,y) centro de la base."""
    return (f'<path d="M{x-26*s},{y} C{x-62*s},{y-40*s} {x-58*s},{y-110*s} {x-20*s},{y-136*s} '
            f'L{x-20*s},{y-166*s} L{x-28*s},{y-176*s} L{x+28*s},{y-176*s} L{x+20*s},{y-166*s} L{x+20*s},{y-136*s} '
            f'C{x+58*s},{y-110*s} {x+62*s},{y-40*s} {x+26*s},{y} Z" fill="{fill}"/>')

def sparkle(x, y, s, col=GOLD):
    return (f'<path d="M{x},{y-s} Q{x+s*.14},{y-s*.14} {x+s},{y} Q{x+s*.14},{y+s*.14} {x},{y+s} '
            f'Q{x-s*.14},{y+s*.14} {x-s},{y} Q{x-s*.14},{y-s*.14} {x},{y-s} Z" fill="{col}"/>')

def door(x, y, w, h, col=NAVY):
    s = arch(x - 12, y - 12, w + 24, h + 12, SHADE)
    s += arch(x, y, w, h, col)
    s += line(x + w / 2, y + 8, x + w / 2, y + h, "#1E4E86", 2)
    s += circle(x + w / 2 - 12, y + h * 0.62, 4, GOLD) + circle(x + w / 2 + 12, y + h * 0.62, 4, GOLD)
    return s

def window(x, y, w, h, col=NAVY):
    return rect(x - 7, y - 7, w + 14, h + 14, SHADE, 3) + rect(x, y, w, h, col, 2)

def pendant(x, y, r, drop):
    return (line(x, 0, x, y, NAVY, 2)
            + f'<path d="M{x-r},{y+r*0.9} A{r},{r} 0 0 1 {x+r},{y+r*0.9} Z" fill="{GOLD}"/>'
            + f'<path d="M{x-r*0.62},{y+r*0.9} A{r*.62},{r*.5} 0 0 0 {x+r*0.62},{y+r*0.9} Z" fill="#F6E7C4"/>')

def floor(y, w, h, col="#EEF3F9"):
    return rect(0, y, w, h - y, col) + line(0, y, w, y, SHADE2, 3)

def view(x, y, w, h, cid, horizon=0.66, sun=(0.62, 0.42, 0.2), island=True):
    """Vista exterior (cielo, sol, mar) recortada a un rectángulo."""
    hy = y + h * horizon
    s = f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#{cid})">'
    s += sky(0, 0, gid=cid + "s").replace('width="0" height="0"', f'width="{w}" height="{h}"').replace('x="0" y="0"', f'x="{x}" y="{y}"')
    s += circle(x + w * sun[0], y + h * sun[1], w * sun[2], SUN)
    if island:
        s += vedra(x + w * 0.12, hy, max(0.5, w / 520))
    s += sea(x, hy, w, y + h - hy, gid=cid + "m")
    s += "</g>"
    return s

def label(w, h, name):
    bw, bh = 330, 38
    x, y = (w - bw) / 2, h - bh - 22
    return (rect(x, y, bw, bh, WHITE, 19, 'opacity=".9"')
            + f'<text x="{w/2}" y="{y+25}" text-anchor="middle" font-family="Jost" font-size="12.5" font-weight="500" '
              f'letter-spacing="1.4" fill="{NAVY}">IMAGEN PROVISIONAL · {name}</text>')


# ---------- escenas verticales (800 x 1000) ----------
def hero():
    W, H = 800, 1000
    s = sky(W, H, "#D3E4F6", "#F4F8FD")
    s += circle(310, 380, 190, "#A9CDEF")
    s += vedra(40, 590, 1.15)
    s += sea(0, 590, W, 90)
    # terraza y murete
    s += rect(0, 680, W, 320, "#F3F7FB")
    for i in range(1, 6):
        s += line(-200 + i * 190, 1000, 250 + i * 60, 700, SHADE, 2)
    s += rect(0, 628, 500, 76, WHITE) + rect(0, 620, 500, 12, PALE) + line(0, 704, 500, 704, SHADE2, 3)
    # casa ibicenca
    s += rect(560, 150, 240, 180, WHITE) + rect(560, 150, 26, 180, SHADE)
    s += rect(650, 96, 54, 60, WHITE) + rect(650, 96, 12, 60, SHADE)
    s += rect(450, 300, 350, 560, WHITE) + rect(450, 300, 30, 560, SHADE)
    s += line(450, 300, 800, 300, SHADE2, 2) + line(560, 150, 800, 150, SHADE2, 2)
    s += window(640, 210, 46, 58) + window(700, 400, 50, 60)
    s += door(545, 500, 150, 320)
    # escalón
    s += rect(505, 820, 230, 22, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"') + rect(480, 842, 280, 24, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    # olivo en maceta
    s += f'<ellipse cx="190" cy="948" rx="130" ry="16" fill="{SHADE}"/>'
    s += olive(190, 830, 1.12, seed=5)
    s += pot(120, 826, 140, 120)
    return W, H, s

def viviendas():
    W, H = 800, 1000
    s = rect(0, 0, W, H, "#FBFDFF")
    s += floor(780, W, H)
    s += f'<ellipse cx="420" cy="880" rx="330" ry="62" fill="{SUN}" opacity=".45"/>'
    # ventanal en arco
    s += arch(92, 132, 316, 500, SHADE)
    s += f'<defs><clipPath id="va"><path d="{arch_d(110,150,280,470)}"/></clipPath></defs><g clip-path="url(#va)">'
    s += view(110, 150, 280, 470, "vv", 0.7, (0.6, 0.42, 0.3)) + "</g>"
    s += f'<path d="{arch_d(110,150,280,470)}" fill="none" stroke="{NAVY}" stroke-width="5"/>'
    s += line(250, 150, 250, 620, NAVY, 4) + line(110, 400, 390, 400, NAVY, 4)
    # cuadro
    s += rect(520, 300, 170, 210, WHITE, 2, f'stroke="{NAVY}" stroke-width="4"') + circle(605, 385, 44, GOLD, 'opacity=".85"') + line(548, 462, 662, 462, NAVY, 3)
    # sofá
    s += rect(440, 640, 330, 110, NAVY, 26) + rect(424, 690, 362, 86, NAVY2, 22)
    s += rect(470, 650, 120, 70, WHITE, 16) + rect(604, 650, 120, 70, SUN, 16)
    s += rect(452, 776, 14, 26, NAVY2) + rect(744, 776, 14, 26, NAVY2)
    # mesa auxiliar con jarrón
    s += rect(120, 760, 190, 12, NAVY, 6) + line(150, 772, 138, 880, NAVY, 5) + line(280, 772, 292, 880, NAVY, 5)
    s += sprig(215, 656, -108, 120, 7, 11) + sprig(215, 656, -72, 135, 8, 12) + sprig(215, 656, -92, 100, 6, 13)
    s += amphora(215, 760, 0.62, WHITE).replace("/>", f' stroke="{NAVY}" stroke-width="4"/>')
    s += pendant(605, 110, 62, 0)
    return W, H, s

def comunidades():
    W, H = 800, 1000
    s = sky(W, H, "#E6F0FB", "#FCFDFF")
    s += circle(170, 210, 150, SUN)
    # edificio
    s += rect(110, 110, 600, 890, WHITE) + rect(110, 110, 34, 890, SHADE) + line(110, 110, 710, 110, SHADE2, 3)
    s += rect(90, 92, 640, 22, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    for row in range(3):
        for col in range(3):
            x, y = 200 + col * 170, 170 + row * 170
            s += rect(x, y, 96, 112, NAVY, 2)
            s += line(x + 48, y, x + 48, y + 112, "#1E4E86", 2)
            s += rect(x - 16, y + 112, 128, 10, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
            for k in range(7):
                s += line(x - 12 + k * 20, y + 74, x - 12 + k * 20, y + 112, WHITE, 3)
            s += line(x - 16, y + 72, x + 112, y + 72, WHITE, 4)
    # portal
    s += arch(318, 668, 184, 250, SHADE)
    s += arch(334, 684, 152, 234, MED)
    s += poly([(334, 918), (334, 800), (420, 700), (486, 760), (486, 918)], "#8DB7E0", 'opacity=".45"')
    s += line(410, 690, 410, 918, WHITE, 4) + circle(398, 820, 5, GOLD)
    s += rect(280, 918, 260, 26, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"') + rect(250, 944, 320, 28, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    s += rect(0, 972, W, 28, "#EEF3F9") + line(0, 972, W, 972, SHADE2, 3)
    for px in (196, 590):
        s += sprig(px + 30, 880, -110, 96, 6, px) + sprig(px + 30, 880, -70, 104, 7, px + 1) + sprig(px + 30, 880, -90, 120, 8, px + 2)
        s += pot(px, 880, 60, 86)
    return W, H, s

def oficinas():
    W, H = 800, 1000
    s = rect(0, 0, W, H, "#FBFDFF")
    s += floor(800, W, H)
    # ventanal
    s += view(380, 130, 360, 430, "ov", 0.72, (0.55, 0.4, 0.26))
    s += rect(380, 130, 360, 430, "none", 0, f'stroke="{NAVY}" stroke-width="6"')
    s += line(500, 130, 500, 560, NAVY, 4) + line(620, 130, 620, 560, NAVY, 4) + line(380, 300, 740, 300, NAVY, 4)
    # estantería
    s += line(70, 260, 300, 260, NAVY, 6) + line(70, 400, 300, 400, NAVY, 6)
    for i, (c, hh) in enumerate([(NAVY, 86), (MED, 70), (SUN, 92), (NAVY2, 78), (WHITE, 84), (MED2, 66)]):
        s += rect(88 + i * 26, 260 - hh, 20, hh, c, 2, f'stroke="{NAVY}" stroke-width="2"')
    s += amphora(250, 400, 0.42, GOLD) + rect(90, 352, 96, 48, SUN, 3) + rect(98, 320, 80, 32, WHITE, 3, f'stroke="{NAVY}" stroke-width="2"')
    # mesa
    s += rect(90, 640, 560, 16, NAVY, 4) + line(130, 656, 110, 800, NAVY, 7) + line(610, 656, 630, 800, NAVY, 7)
    s += rect(250, 470, 230, 140, NAVY, 8) + rect(262, 482, 206, 116, "#DCEAF8", 3) + rect(352, 610, 26, 22, NAVY) + rect(318, 630, 94, 10, NAVY, 5)
    s += rect(520, 610, 96, 30, WHITE, 3, f'stroke="{NAVY}" stroke-width="3"') + rect(128, 626, 90, 14, SUN, 3)
    # silla
    s += rect(330, 700, 150, 18, MED, 9) + rect(350, 600, 110, 96, MED, 22, 'opacity="0"') + line(405, 718, 405, 800, NAVY, 6) + line(360, 800, 450, 800, NAVY, 6)
    # planta
    s += sprig(705, 720, -112, 150, 8, 41) + sprig(705, 720, -86, 190, 10, 42) + sprig(705, 720, -62, 140, 8, 43)
    s += pot(665, 720, 80, 96)
    s += pendant(200, 90, 54, 0) + pendant(560, 60, 44, 0)
    return W, H, s

def cristales():
    W, H = 800, 1000
    s = rect(0, 0, W, H, "#FBFDFF")
    s += rect(0, 840, W, 160, "#EEF3F9")
    s += view(70, 110, 660, 730, "cv", 0.68, (0.62, 0.36, 0.2))
    # reflejos
    s += f'<g clip-path="url(#cv)" opacity=".42">' + poly([(150, 840), (330, 110), (430, 110), (250, 840)], WHITE) + poly([(470, 840), (650, 110), (690, 110), (510, 840)], WHITE) + "</g>"
    s += rect(70, 110, 660, 730, "none", 0, f'stroke="{NAVY}" stroke-width="8"')
    s += line(290, 110, 290, 840, NAVY, 6) + line(510, 110, 510, 840, NAVY, 6)
    s += rect(276, 470, 8, 60, GOLD, 4) + rect(516, 470, 8, 60, GOLD, 4)
    s += line(0, 840, W, 840, SHADE2, 3)
    s += poly([(70, 840), (730, 840), (800, 1000), (0, 1000)], SUN, 'opacity=".28"')
    s += sparkle(210, 250, 30) + sparkle(606, 560, 22) + sparkle(430, 330, 14) + sparkle(160, 640, 14)
    return W, H, s

def sobre():
    W, H = 800, 1000
    s = rect(0, 0, W, H, PALE)
    s += circle(560, 330, 230, SUN)
    # muro encalado escalonado
    s += poly([(0, 1000), (0, 420), (180, 420), (180, 300), (420, 300), (420, 520), (620, 520), (620, 640), (800, 640), (800, 1000)], WHITE)
    s += f'<polyline points="0,420 180,420 180,300 420,300 420,520 620,520 620,640 800,640" fill="none" stroke="{SHADE2}" stroke-width="3"/>'
    # hornacina con jarrón
    s += arch(160, 520, 250, 330, SHADE) + arch(176, 540, 218, 310, "#EFF4FA")
    s += rect(150, 850, 270, 16, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    s += sprig(285, 700, -118, 150, 8, 71) + sprig(285, 700, -90, 185, 10, 72) + sprig(285, 700, -64, 150, 8, 73) + sprig(285, 700, -140, 110, 6, 74)
    s += amphora(285, 850, 0.86)
    # escalones
    for i in range(4):
        s += rect(520 + i * 60, 760 + i * 44, 280 - i * 60, 44, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    s += rect(0, 936, W, 64, "#EEF3F9") + line(0, 936, W, 936, SHADE2, 3)
    return W, H, s

def polo(front=True):
    W, H = 800, 1000
    s = rect(0, 0, W, H, PALE) + circle(400, 430, 330, SUN, 'opacity=".55"')
    body = (f'<path d="M270,190 L170,235 L80,430 L190,480 L225,400 L225,850 L575,850 L575,400 L610,480 L720,430 L630,235 L530,190 '
            f'C500,225 300,225 270,190 Z" fill="{NAVY}"/>')
    s += body
    s += line(225, 400, 215, 300, NAVY2, 3) + line(575, 400, 585, 300, NAVY2, 3)
    if front:
        s += f'<path d="M270,190 L400,300 L345,318 Z" fill="{NAVY2}"/><path d="M530,190 L400,300 L455,318 Z" fill="{NAVY2}"/>'
        s += line(400, 300, 400, 400, "#1E4E86", 3) + circle(400, 335, 4, SUN) + circle(400, 372, 4, SUN)
        s += (f'<text x="500" y="392" text-anchor="middle" font-family="Bodoni Moda" font-size="30" letter-spacing="3" '
              f'fill="{WHITE}">SA NETA</text>')
        cap = "POLO · PARTE DELANTERA"
    else:
        s += f'<path d="M290,196 C340,232 460,232 510,196 L498,188 C450,214 350,214 302,188 Z" fill="{NAVY2}"/>'
        s += rect(300, 330, 200, 180, "none", 10, f'stroke="{WHITE}" stroke-width="2" stroke-dasharray="7 7" opacity=".85"')
        s += (f'<text x="400" y="412" text-anchor="middle" font-family="Jost" font-size="17" letter-spacing="2" fill="{WHITE}">LOGO COMPLETO</text>'
              f'<text x="400" y="440" text-anchor="middle" font-family="Jost" font-size="17" letter-spacing="2" fill="{WHITE}">SA NETA</text>')
        cap = "POLO · PARTE TRASERA"
    s += (f'<text x="400" y="912" text-anchor="middle" font-family="Jost" font-size="17" letter-spacing="3" fill="{NAVY}">{cap}</text>')
    return W, H, s


# ---------- escenas horizontales (1200 x 900) ----------
def g_finca():
    W, H = 1200, 900
    s = sky(W, H, "#E6F0FB", "#FCFDFF")
    s += circle(820, 330, 210, SUN)
    s += vedra(880, 560, 1.1) + sea(0, 560, W, 70)
    s += rect(0, 630, W, 270, "#F3F7FB")
    s += rect(150, 300, 520, 400, WHITE) + rect(150, 300, 34, 400, SHADE)
    s += rect(250, 170, 260, 130, WHITE) + rect(250, 170, 26, 130, SHADE) + rect(330, 110, 60, 60, WHITE) + rect(330, 110, 12, 60, SHADE)
    for i in range(5):
        s += rect(670 + i * 46, 480 + i * 44, 46, 220 - i * 44, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    s += line(150, 300, 670, 300, SHADE2, 2) + line(250, 170, 510, 170, SHADE2, 2)
    s += window(350, 210, 44, 54) + window(240, 400, 50, 60) + window(560, 400, 50, 60)
    s += door(370, 440, 130, 260)
    s += f'<path d="M0,712 Q400,690 1200,716 L1200,726 Q400,702 0,724 Z" fill="{NAVY}"/>'
    s += olive(1000, 716, 1.25, seed=9)
    return W, H, s

def g_interior():
    W, H = 1200, 900
    s = rect(0, 0, W, H, "#FBFDFF") + floor(700, W, H)
    s += f'<ellipse cx="640" cy="800" rx="460" ry="60" fill="{SUN}" opacity=".45"/>'
    for i, x in enumerate((110, 380)):
        s += arch(x - 14, 126, 228, 440, SHADE)
        s += f'<defs><clipPath id="gi{i}"><path d="{arch_d(x,140,200,420)}"/></clipPath></defs><g clip-path="url(#gi{i})">'
        s += view(x, 140, 200, 420, f"giv{i}", 0.72, (0.5 + 0.3 * i, 0.42, 0.34), island=(i == 0)) + "</g>"
        s += f'<path d="{arch_d(x,140,200,420)}" fill="none" stroke="{NAVY}" stroke-width="5"/>' + line(x + 100, 140, x + 100, 560, NAVY, 4)
    s += rect(690, 560, 420, 110, NAVY, 26) + rect(670, 610, 460, 86, NAVY2, 22)
    s += rect(720, 570, 120, 70, WHITE, 16) + rect(852, 570, 120, 70, SUN, 16) + rect(984, 570, 110, 70, WHITE, 16)
    s += rect(700, 696, 14, 26, NAVY2) + rect(1086, 696, 14, 26, NAVY2)
    s += rect(430, 740, 250, 14, NAVY, 7) + line(470, 754, 460, 830, NAVY, 5) + line(640, 754, 650, 830, NAVY, 5)
    s += amphora(555, 740, 0.5, WHITE).replace("/>", f' stroke="{NAVY}" stroke-width="4"/>')
    s += sprig(555, 652, -105, 96, 6, 21) + sprig(555, 652, -75, 108, 7, 22)
    s += rect(760, 230, 150, 190, WHITE, 2, f'stroke="{NAVY}" stroke-width="4"') + circle(835, 310, 40, GOLD, 'opacity=".85"')
    s += rect(940, 270, 120, 150, WHITE, 2, f'stroke="{NAVY}" stroke-width="4"') + sprig(1000, 400, -90, 90, 6, 23)
    s += pendant(900, 80, 60, 0)
    return W, H, s

def g_oficina():
    W, H = 1200, 900
    s = rect(0, 0, W, H, "#FBFDFF") + floor(720, W, H)
    s += view(120, 120, 620, 400, "gov", 0.74, (0.7, 0.4, 0.2))
    s += rect(120, 120, 620, 400, "none", 0, f'stroke="{NAVY}" stroke-width="6"')
    for x in (275, 430, 585):
        s += line(x, 120, x, 520, NAVY, 4)
    s += rect(150, 590, 760, 16, NAVY, 4) + line(200, 606, 180, 720, NAVY, 7) + line(860, 606, 880, 720, NAVY, 7)
    for x in (260, 600):
        s += rect(x, 440, 210, 124, NAVY, 8) + rect(x + 11, 451, 188, 102, "#DCEAF8", 3) + rect(x + 92, 564, 26, 18, NAVY) + rect(x + 60, 580, 90, 10, NAVY, 5)
    s += line(840, 250, 1100, 250, NAVY, 6) + line(840, 400, 1100, 400, NAVY, 6)
    for i, (c, hh) in enumerate([(NAVY, 86), (MED, 70), (SUN, 92), (NAVY2, 78), (WHITE, 84), (MED2, 66), (GOLD, 74)]):
        s += rect(860 + i * 28, 250 - hh, 22, hh, c, 2, f'stroke="{NAVY}" stroke-width="2"')
    s += rect(862, 344, 110, 56, SUN, 3) + amphora(1040, 400, 0.44, NAVY)
    s += sprig(1060, 640, -112, 150, 8, 51) + sprig(1060, 640, -86, 190, 10, 52) + sprig(1060, 640, -62, 140, 8, 53) + pot(1020, 640, 80, 96)
    s += pendant(430, 40, 48, 0) + pendant(700, 60, 48, 0)
    return W, H, s

def g_comunidad():
    W, H = 1200, 900
    s = sky(W, H, "#E6F0FB", "#FCFDFF") + circle(980, 230, 150, SUN)
    s += rect(60, 150, 1080, 750, WHITE) + line(60, 150, 1140, 150, SHADE2, 3) + rect(40, 132, 1120, 22, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    for i in range(4):
        x = 130 + i * 250
        s += arch(x - 14, 286, 208, 474, SHADE) + arch(x, 300, 180, 460, "#DCE8F5")
        s += arch(x + 46, 470, 88, 290, NAVY if i != 1 else MED)
    s += line(60, 240, 1140, 240, SHADE2, 2)
    for i in range(3):
        s += rect(0 - i * 0, 760 + i * 36, W, 36, WHITE, 0, f'stroke="{SHADE2}" stroke-width="2"')
    s += rect(0, 868, W, 32, "#EEF3F9")
    for px in (86, 1056):
        s += sprig(px + 30, 690, -110, 110, 7, px) + sprig(px + 30, 690, -70, 118, 7, px + 1) + sprig(px + 30, 690, -90, 140, 9, px + 2) + pot(px, 690, 60, 74)
    return W, H, s

def g_cristalera():
    W, H = 1200, 900
    s = rect(0, 0, W, H, "#FBFDFF") + rect(0, 740, W, 160, "#EEF3F9")
    s += view(90, 100, 1020, 640, "gcv", 0.7, (0.3, 0.38, 0.14))
    s += '<g clip-path="url(#gcv)" opacity=".42">' + poly([(200, 740), (400, 100), (520, 100), (320, 740)], WHITE) + poly([(760, 740), (960, 100), (1010, 100), (810, 740)], WHITE) + "</g>"
    s += rect(90, 100, 1020, 640, "none", 0, f'stroke="{NAVY}" stroke-width="8"')
    for x in (345, 600, 855):
        s += line(x, 100, x, 740, NAVY, 6)
    s += line(0, 740, W, 740, SHADE2, 3) + poly([(90, 740), (1110, 740), (1200, 900), (0, 900)], SUN, 'opacity=".28"')
    s += sparkle(470, 250, 30) + sparkle(930, 470, 22) + sparkle(690, 330, 14) + sparkle(220, 560, 16)
    return W, H, s

def g_detalle():
    W, H = 1200, 900
    s = rect(0, 0, W, H, PALE) + circle(330, 380, 250, SUN, 'opacity=".8"')
    s += rect(0, 640, W, 26, NAVY, 0) + rect(0, 666, W, 234, "#EEF3F9")
    # toallas dobladas
    for i, c in enumerate([WHITE, WHITE, SUN, WHITE]):
        y = 584 - i * 58
        s += rect(560, y, 360, 56, c, 26, f'stroke="{SHADE2}" stroke-width="3"') + line(600, y + 28, 880, y + 28, SHADE2, 2)
    s += rect(560, 410, 360, 14, NAVY, 0, 'opacity="0"')
    s += rect(616, 344, 248, 66, WHITE, 30, f'stroke="{SHADE2}" stroke-width="3"') + rect(650, 366, 180, 8, NAVY, 4)
    s += sprig(270, 470, -112, 170, 9, 81) + sprig(270, 470, -84, 210, 11, 82) + sprig(270, 470, -60, 170, 9, 83) + sprig(270, 470, -136, 130, 7, 84)
    s += amphora(270, 640, 0.92)
    s += sparkle(1010, 300, 26) + sparkle(1070, 380, 12)
    return W, H, s


JOBS = {
    "galeria-1.webp": (g_finca, 1400),
    "galeria-2.webp": (g_interior, 1200),
    "galeria-3.webp": (g_oficina, 1200),
    "galeria-4.webp": (g_comunidad, 1200),
    "galeria-5.webp": (g_cristalera, 1200),
    "galeria-6.webp": (g_detalle, 1200),
}


async def main(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, (fn, outw) in JOBS.items():
            if only and name not in only:
                continue
            W, H, body = fn()
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{body}{label(W, H, name)}</svg>'
            html = (f'<style>@font-face{{font-family:Jost;src:url({FONT})}}@font-face{{font-family:"Bodoni Moda";src:url({SERIF})}}'
                    f'html,body{{margin:0}}svg{{display:block}}</style>{svg}')
            pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=outw / W)
            tmp = OUT / "_tmp.html"
            tmp.write_text(html, encoding="utf-8")
            await pg.goto(tmp.as_uri())
            tmp.unlink()
            await pg.evaluate("document.fonts.ready")
            png = await pg.screenshot(type="png")
            await pg.close()
            Image.open(io.BytesIO(png)).convert("RGB").save(OUT / name, "WEBP", quality=84, method=6)
            print(name, (OUT / name).stat().st_size // 1024, "KB")
        await b.close()

if __name__ == "__main__":
    import sys
    asyncio.run(main(set(sys.argv[1:]) or None))
