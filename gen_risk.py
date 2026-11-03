"""Generates the progressive Risk = Exposure x Hazard slides (schematic, SVG) and swaps them into presentation.md."""
import math, re

W, H = 1080, 360
COL = {1: 90, 3: 430, 5: 880}          # centres of the three term columns (grid 180/50/400/50/400)
WHITE, AMBER, MUTED = "#fff", "#ffb000", "#8a8a8a"

def t(x, y, s, size=40, fill=WHITE, anchor="middle", weight=700, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" style="fill:{fill}" {extra}>{s}</text>'

def arrow_down(x, y0=10, y1=52):
    return (f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{AMBER}" stroke-width="5"/>'
            f'<polygon points="{x-11},{y1-4} {x+11},{y1-4} {x},{y1+14}" fill="{AMBER}"/>')

def caption(col, text):
    return arrow_down(COL[col]) + t(COL[col], 110, text, 42)

# ---- accelerogram + shaking building (column 5) ----
AX0, AX1, AYC = 810, 1070, 160            # accelerogram x-range and zero line
def accel():
    pts, best = [], (0, 0)
    n = 90
    for i in range(n + 1):
        u = i / n
        env = math.exp(-((u - 0.42) / 0.22) ** 2)
        v = env * (0.7 * math.sin(u * 46) + 0.3 * math.sin(u * 83 + 1))
        x, y = AX0 + u * (AX1 - AX0), AYC - v * 70
        pts.append(f"{x:.1f},{y:.1f}")
        if v > best[1]: best = (x, v)
    px, pv = best
    py = AYC - pv * 70
    s = f'<line x1="{AX0}" y1="{AYC}" x2="{AX1+8}" y2="{AYC}" stroke="{MUTED}" stroke-width="2"/>'
    s += f'<line x1="{AX0}" y1="{AYC-95}" x2="{AX0}" y2="{AYC+95}" stroke="{MUTED}" stroke-width="2"/>'
    s += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{WHITE}" stroke-width="3" stroke-linejoin="round"/>'
    s += f'<line x1="{AX0}" y1="{py:.1f}" x2="{AX1}" y2="{py:.1f}" stroke="{AMBER}" stroke-width="2" stroke-dasharray="6 6"/>'
    s += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{AMBER}"/>'
    s += t(AX1, AYC + 125, "time", 22, MUTED, "end", 400) + t(AX0 + 8, AYC - 104, "a(t)", 22, MUTED, "start", 400)
    return s, (px, py)

def building():
    bx, bw, gy = 690, 90, 255
    s = f'<line x1="{bx-30}" y1="{gy}" x2="{bx+bw+30}" y2="{gy}" stroke="{WHITE}" stroke-width="4"/>'
    for k in range(5): s += f'<line x1="{bx-26+k*30}" y1="{gy}" x2="{bx-36+k*30}" y2="{gy+12}" stroke="{WHITE}" stroke-width="3"/>'
    s += f'<rect x="{bx}" y="{gy-125}" width="{bw}" height="125" fill="none" stroke="{WHITE}" stroke-width="4"/>'
    for f in (1, 2): s += f'<line x1="{bx}" y1="{gy-f*125/3}" x2="{bx+bw}" y2="{gy-f*125/3}" stroke="{WHITE}" stroke-width="3"/>'
    for f in range(3):
        for c in range(2): s += f'<rect x="{bx+14+c*44}" y="{gy-110+f*41.7}" width="22" height="22" fill="{WHITE}" opacity=".55"/>'
    s += (f'<line x1="{bx-6}" y1="{gy+34}" x2="{bx+bw+6}" y2="{gy+34}" stroke="{AMBER}" stroke-width="4"/>'
          f'<polygon points="{bx-14},{gy+34} {bx+2},{gy+25} {bx+2},{gy+43}" fill="{AMBER}"/>'
          f'<polygon points="{bx+bw+14},{gy+34} {bx+bw-2},{gy+25} {bx+bw-2},{gy+43}" fill="{AMBER}"/>')
    return s

# ---- fragility curve (column 3) ----
CX0, CX1, CY0, CY1 = 300, 620, 255, 75   # axis x-range, y of 0 and of 100 %
MID, SC = 470, 36
def fy(x): return CY0 - (CY0 - CY1) / (1 + math.exp(-(x - MID) / SC))
def fragility(inputs=None):
    s = f'<line x1="{CX0}" y1="{CY0}" x2="{CX1+10}" y2="{CY0}" stroke="{WHITE}" stroke-width="3"/>'
    s += f'<line x1="{CX0}" y1="{CY0}" x2="{CX0}" y2="{CY1-14}" stroke="{WHITE}" stroke-width="3"/>'
    pts = " ".join(f"{x},{fy(x):.1f}" for x in range(CX0, CX1 + 1, 4))
    s += f'<polyline points="{pts}" fill="none" stroke="{AMBER}" stroke-width="6" stroke-linejoin="round"/>'
    s += t(CX0 + (CX1 - CX0) / 2, CY0 + 40, "acceleration", 24, MUTED, "middle", 400)
    s += t(CX0 - 16, (CY0 + CY1) / 2, "P(damage)", 24, MUTED, "middle", 400, f'transform="rotate(-90 {CX0-16} {(CY0+CY1)/2})"')
    s += t(424, CY1 - 26, "Fragility curve", 26, WHITE, "end")
    return s

def inputs(peak):
    px, py = peak
    xm = 438
    yc = fy(xm)
    top = 40
    s = (f'<polyline points="{px:.1f},{py:.1f} {px:.1f},{top} {xm},{top} {xm},{yc-12:.1f}" fill="none" stroke="{AMBER}" stroke-width="4" stroke-dasharray="9 7"/>'
         f'<polygon points="{xm-9},{yc-14:.1f} {xm+9},{yc-14:.1f} {xm},{yc:.1f}" fill="{AMBER}"/>'
         f'<circle cx="{xm}" cy="{yc:.1f}" r="8" fill="{WHITE}"/>'
         f'<line x1="{xm-10}" y1="{yc:.1f}" x2="{CX0+14}" y2="{yc:.1f}" stroke="{WHITE}" stroke-width="4" stroke-dasharray="9 7"/>'
         f'<polygon points="{CX0+16},{yc-9:.1f} {CX0+16},{yc+9:.1f} {CX0+2},{yc:.1f}" fill="{WHITE}"/>')
    pct = round((CY0 - yc) / (CY0 - CY1) * 100)
    s += t(CX0 + 22, yc - 14, f"{pct} %", 30, WHITE, "start")
    s += f'<line x1="{xm}" y1="{CY0}" x2="{xm}" y2="{CY0-8}" stroke="{AMBER}" stroke-width="4"/>'
    return s

def slide(terms, svg_body):
    names = [terms[0], "=", terms[1], "×", terms[2]]
    cells = ''.join(f'<div class="rt{" op" if n in ("=","×") else ""}{" a" if i>0 and n not in ("=","×") else ""}">{n}</div>' for i, n in enumerate(names))
    return (f'<!-- _class: risk -->\n\n<div class="body"><div class="riskbox"><div class="eqrow">{cells}</div>'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><g transform="translate(0,34)">{svg_body}</g></svg></div></div>\n')

acc, peak = accel()
shake = building() + acc
S = [
  slide(("Risk", "Exposure", "Hazard"), ""),
  slide(("Risk", "Exposure", "Hazard"), caption(1, "Damage") + caption(3, "Buildings") + caption(5, "Earthquake")),
  slide(("Risk", "Exposure", "Earthquake"), caption(1, "Damage") + caption(3, "Buildings") + shake),
  slide(("Risk", "Buildings", "Earthquake"), caption(1, "Damage") + fragility() + shake),
  slide(("Risk", "Buildings", "Earthquake"), caption(1, "Damage") + fragility() + shake + inputs(peak)),
]

md = open("presentation.md").read()
parts = md.split("\n---\n")
# parts: [front matter, title, eq slide 1, eq slide 2, ...]; replace the first two Risk slides, or the whole earlier generated block
risk_idx = [i for i, p in enumerate(parts) if "eqgrid" in p or "_class: risk" in p]
assert risk_idx, "risk slides not found"
first, last = risk_idx[0], risk_idx[-1]
parts[first:last + 1] = ["\n" + s for s in S]
open("presentation.md", "w").write("\n---\n".join(parts))
print("risk slides:", len(S), "replaced", last - first + 1)
