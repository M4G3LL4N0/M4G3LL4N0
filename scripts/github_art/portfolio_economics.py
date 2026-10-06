#!/usr/bin/env python3
"""Portfolio economics plate: animated primary, static dark, static light.

Geometry is honest by construction.

The three scenarios differ by roughly 12x from low to high. Anything that
encodes magnitude as volume, perspective or shadow distorts that ratio: a bar
drawn with depth reads larger than an equal bar without, so pseudo-3D would
make the high scenario look several times larger than it is. Every mark here is
a flat horizontal bar whose *length* is the value on a stated linear scale, and
the scale is printed on the plate so a reader can check it.

The animated variant reveals bars from zero and resolves gross into
risk-adjusted. No number changes: the animation only decides when a value
becomes visible, never what it is.

  python3 scripts/github_art/portfolio_economics.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts" / "github_art"))
DATA = PROFILE / "data" / "portfolio-economics-v0.2.json"
OUT = PROFILE / "assets" / "profile"

W, H = 1200, 620
PAD = 56
LABEL_W = 132
BAR_MAX = W - PAD - LABEL_W - 168

INK = "#f4efe4"
INK_DIM = "#f4efe4b0"
INK_FAINT = "#f4efe45c"
EDGE = "#f4efe42b"
CANVAS_DARK = "#0a0d12"
CANVAS_LIGHT = "#f7f5f0"
GROSS = "#e7c27a"
ADJUSTED = "#7fd1c1"


def fmt(v: float) -> str:
    return f"${v / 1e9:.2f}B" if v >= 1e9 else f"${v / 1e6:.1f}M"


def load() -> dict:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    g = d["scenarios"]["gross_venture_value"]
    r = d["scenarios"]["risk_adjusted"]
    return {"g": g, "r": r, "stages": d["venture_counts"]["by_stage"],
            "total": d["venture_counts"]["registered_ventures"],
            "haircut": d["scenarios"]["risk_adjusted"]["haircut"]}


def plate(theme: str, animated: bool) -> str:
    d = load()
    g, r = d["g"], d["r"]
    peak = g["high"]
    ink = INK if theme == "dark" else "#141a20"
    dim = INK_DIM if theme == "dark" else "#141a20b0"
    faint = INK_FAINT if theme == "dark" else "#141a205c"
    edge = EDGE if theme == "dark" else "#141a202b"
    canvas = CANVAS_DARK if theme == "dark" else CANVAS_LIGHT

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" '
         f'aria-label="Portfolio model: gross venture value low {fmt(g["low"])}, '
         f'base {fmt(g["base"])}, high {fmt(g["high"])}. Risk-adjusted after a 25 '
         f'percent haircut: low {fmt(r["low"])}, base {fmt(r["base"])}, '
         f'high {fmt(r["high"])}.">',
         '<title>Noaerth portfolio economics — management estimate, unaudited, '
         'not attributable parent NAV</title>',
         '<desc>Horizontal bar plate on a linear scale. Modeled gross venture '
         f'value: low {fmt(g["low"])}, base {fmt(g["base"])}, '
         f'high {fmt(g["high"])}. Risk-adjusted after a 25 percent portfolio '
         f'overlap haircut: low {fmt(r["low"])}, base {fmt(r["base"])}, '
         f'high {fmt(r["high"])}. Bar length is proportional to value; no volume '
         'or perspective encodes magnitude. 124 registered ventures: 16 Live, '
         '102 Building, 6 Research. Attributable parent NAV is not established.'
         '</desc>',
         f'<rect width="{W}" height="{H}" fill="{canvas}"/>']

    if animated:
        p.append(
            '<style>'
            '@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}'
            '@keyframes resolve{from{opacity:0}to{opacity:1}}'
            '@keyframes sweep{from{transform:translateX(0)}'
            'to{transform:translateX(640px)}}'
            '.b{transform-origin:' + f'{LABEL_W}px 0px' + '}'
            '.b1{animation:grow 1.5s cubic-bezier(.2,.8,.2,1) both}'
            '.b2{animation:grow 1.5s .3s cubic-bezier(.2,.8,.2,1) both}'
            '.b3{animation:grow 1.5s .6s cubic-bezier(.2,.8,.2,1) both}'
            '.a1{animation:resolve .9s 1.5s both}'
            '.a2{animation:resolve .9s 1.8s both}'
            '.a3{animation:resolve .9s 2.1s both}'
            '.sweep{animation:sweep 3.4s ease-in-out infinite alternate}'
            '@media (prefers-reduced-motion: reduce){'
            '.b,.sweep{animation:none !important}}'
            '</style>')

    # Header
    p.append(f'<text x="{PAD}" y="52" fill="{ink}" font-size="26" '
             f'font-weight="640" letter-spacing="-0.3">Portfolio economics</text>')
    p.append(f'<text x="{PAD}" y="80" fill="{dim}" font-size="13.5" '
             f'letter-spacing="0.5">MANAGEMENT ESTIMATE · UNAUDITED · '
             f'VENTURE-LEVEL MODEL · NOT AN INDEPENDENT APPRAISAL · '
             f'NOT ATTRIBUTABLE PARENT NAV</text>')

    stages = d["stages"]
    p.append(f'<text x="{PAD}" y="{112}" fill="{faint}" font-size="13" '
             f'letter-spacing="0.4">{d["total"]} registered ventures · '
             f'{stages["live"]} Live · {stages["building"]} Building · '
             f'{stages["research"]} Research</text>')

    # Scale is printed so the geometry is checkable rather than trusted.
    p.append(f'<text x="{W - PAD}" y="52" fill="{faint}" font-size="11.5" '
             f'text-anchor="end" letter-spacing="0.4">linear scale · '
             f'0 → {fmt(peak)} · bar length is proportional to value</text>')

    top = 150
    row = 62
    groups = [("Modeled gross", g, GROSS, ["b1", "b2", "b3"],
               ["a1", "a2", "a3"], 1.0),
              ("Risk-adjusted", r, ADJUSTED, ["b1", "b2", "b3"],
               ["a1", "a2", "a3"], 0.0)]

    for gi, (name, vals, colour, bg, fa, off) in enumerate(groups):
        y = top + gi * (row * 3 + 54)
        p.append(f'<text x="{PAD}" y="{y - 14}" fill="{ink}" font-size="14" '
                 f'font-weight="600" letter-spacing="0.6">{name.upper()}</text>')
        if gi == 1:
            p.append(f'<text x="{PAD + 190}" y="{y - 14}" fill="{faint}" '
                     f'font-size="12.5" letter-spacing="0.3">after '
                     f'{int(d["haircut"] * 100)}% portfolio overlap haircut</text>')
        for i, key in enumerate(("low", "base", "high")):
            v = vals[key]
            length = max(2.0, (v / peak) * BAR_MAX)
            by = y + i * row
            klass = f' class="{bg[i]}"' if animated else ""
            fade = f' class="{fa[i]}"' if animated else ""
            p.append(f'<g{fade}>')
            p.append(f'<text x="{PAD}" y="{by + 17}" fill="{dim}" '
                     f'font-size="12.5" letter-spacing="1.1" '
                     f'text-transform="uppercase">{key}</text>')
            p.append(f'<rect x="{LABEL_W}" y="{by + 5}" width="{BAR_MAX}" '
                     f'height="22" fill="{ink}" opacity="0.055"/>')
            p.append(f'<g{klass}><rect x="{LABEL_W}" y="{by + 5}" '
                     f'width="{length:.1f}" height="22" rx="4" '
                     f'fill="{colour}" opacity="0.92"/></g>')
            p.append(f'<text x="{LABEL_W + BAR_MAX + 16}" y="{by + 22}" '
                     f'fill="{ink}" font-size="16" font-weight="600" '
                     f'font-variant-numeric="tabular-nums">{fmt(v)}</text>')
            p.append('</g>')

    if animated:
        p.append(f'<rect class="sweep" x="{LABEL_W}" y="{top - 26}" '
                 f'width="120" height="8" rx="4" fill="{GROSS}" '
                 f'opacity="0.22"/>')

    foot = H - 40
    p.append(f'<line x1="{PAD}" y1="{foot - 22}" x2="{W - PAD}" y2="{foot - 22}" '
             f'stroke="{edge}" stroke-width="1"/>')
    p.append(f'<text x="{PAD}" y="{foot}" fill="{faint}" font-size="11.5" '
             f'letter-spacing="0.35">Figures are a portfolio model, not Noaerth '
             f'corporate value. Attributable parent NAV not established. '
             f'Methodology: PORTFOLIO_ECONOMICS.md</text>')
    p.append('</svg>')
    return "\n".join(p)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for theme in ("dark", "light"):
        path = OUT / f"portfolio-economics-{theme}.svg"
        path.write_text(plate(theme, animated=False), encoding="utf-8")
        written.append(path)
    anim = OUT / "portfolio-economics-motion.svg"
    anim.write_text(plate("dark", animated=True), encoding="utf-8")
    written.append(anim)
    # Reduced motion resolves to the static dark plate, which is the same
    # composition without the reveal. It is a real image, not a degradation.
    for p in written:
        print(f"  {p.name:<38}{p.stat().st_size / 1024:6.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())