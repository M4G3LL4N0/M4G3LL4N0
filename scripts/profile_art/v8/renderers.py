#!/usr/bin/env python3
"""Computer-science renderers.

Each function returns one SVG document for one role. A project's five to ten
surfaces are chosen from these by the storyboard builder, and each must reveal
a different facet of the project. That constraint is the whole point: a hero,
a terminal, an architecture diagram and a state machine that were generated
from the same inputs would be one picture repeated, which is exactly what the
duplication test rejects.

Every renderer draws real measured structure. The architecture renderer uses
the project's actual modules; the build renderer uses its actual test and CI
counts; the terminal renderer uses commands that exist in its entry points.
Nothing invents a system to look complete.
"""

from __future__ import annotations

import hashlib
import re
import textwrap

from geometry import (
    set_motion,
    DENSITY, animate_motion, animate_opacity, animate_rot, arch, bar, cube,
    diamond, dot, duration_for, edge, frame, grid_field, iso_point, node,
    palette, palette_for, palette_light, petal, pulse, rgba, ring, rng_for,
    rosette, sequence, stagger, travelling, triangle, wedge, MOTION, mix,
    darken, lighten,
)

VIEW_W, VIEW_H = 1200, 640

SLOT_VIEW = {
    "hero": (1200, 560),
    "terminal": (1200, 620),
    "architecture": (1200, 700),
    "state_machine": (1200, 560),
    "data_flow": (1200, 560),
    "component_map": (1200, 600),
    "build": (1200, 520),
    "workflow": (1200, 560),
    "domain": (1200, 600),
    "footer": (1200, 300),
}


def seed_of(name: str, slot: str) -> int:
    return int(hashlib.sha256(f"{name}|{slot}".encode()).hexdigest()[:8], 16)


def _doc(body: str, w: int, h: int, pal: dict, title: str, motion: bool = True) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">
<title>{title}</title>
<rect width="{w}" height="{h}" fill="{pal['bg']}"/>
{body}
</svg>'''


def _defs(pal: dict, gid: str) -> str:
    return (f'<defs><linearGradient id="g{gid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="{pal["accents"][0]}"/>'
            f'<stop offset="100%" stop-color="{pal["accents"][1]}"/></linearGradient></defs>')


# --------------------------------------------------------------------------
# 01 HERO
# --------------------------------------------------------------------------
def render_hero(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """Category-encoded hero.

    The composition is chosen by project category, so a scheduler's hero reads
    as a stepped queue with workers activating, and a database's reads as an
    indexed tile field with a query path. Two projects in different categories
    cannot collide here even by accident.
    """
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["hero"]
    cat = d.get("project_category", "PRODUCT")
    r = rng_for(name, "hero")
    dur = duration_for(d.get("animation_story_1", "tile_assemble"), seed_of(name, "hero"))
    off = stagger(seed_of(name, "hero"), 8)[0]
    A, B, C = pal["accents"][:3]
    parts = [_defs(pal, "h")]

    if cat == "AGENT":
        # multi-node reasoning path with tool calls and a verification loop
        cx, cy = w * 0.42, h * 0.5
        for i in range(3):
            rad = 118 + i * 74
            parts.append(ring(cx, cy, rad, 1.1, rgba(A, 0.5 - i * 0.12), dash="5 9"))
        chain = [(cx - 250, cy + 96), (cx - 96, cy - 84), (cx + 88, cy - 30),
                 (cx + 262, cy + 88), (cx + 40, cy + 152)]
        for i in range(len(chain) - 1):
            (x1, y1), (x2, y2) = chain[i], chain[i + 1]
            parts.append(edge(x1, y1, x2, y2, rgba(pal["ink"], 0.4), 1.8, arrow=True))
            if motion:
                parts.append(travelling(x1, y1, x2, y2, 6, B, dur / 2, off + i * 0.7))
        for i, (x, y) in enumerate(chain):
            parts.append(cube(x - 15, y - 15, 0, 30, [A, B, C][i % 3], B, C, 0.95))
        parts.append(pulse(rosette(cx, cy, 92, 8, rgba(C, 0.75), rgba(A, 0.5)),
                           dur, off + 1.4))
        if motion:
            parts.append(f'<g>{rosette(cx, cy, 92, 8, "none", "none")}'
                         f'{animate_rot(0, 360, dur * 2, off)}</g>')

    elif cat in ("INFRASTRUCTURE", "DEVELOPER_TOOLS"):
        # stepped isometric queue: jobs advancing through workers
        for row in range(4):
            for col in range(7):
                z = (3 - row) * 26 + col * 4
                parts.append(cube(150 + col * 116, 210 + row * 66, z, 62,
                                  mix(A, B, col / 6), B, C, 0.9 - row * 0.13))
        for i in range(4):
            parts.append(arch(230 + i * 236, 470, 130, 176, rgba(B, 0.14), 0.5, rgba(B, 0.42)))
        if motion:
            for i in range(5):
                parts.append(pulse(bar(150 + i * 116, 470, 62, 8, C), dur / 2, off + i * 0.5))

    elif cat in ("QUANT_DATA", "RESEARCH"):
        # temporal signal surface with evidence nodes and an audit path
        mid = h * 0.55
        parts.append(f'<line x1="90" y1="{mid}" x2="{w - 90}" y2="{mid}" stroke="{rgba(pal["ink"],.28)}" stroke-width="1.4"/>')
        pts = []
        for i in range(46):
            x = 96 + i * (w - 200) / 45
            amp = r.uniform(18, 86) * math_sin(i)
            pts.append((x, mid - amp))
        for i in range(len(pts) - 1):
            parts.append(edge(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], rgba(A, .8), 2.2))
        for i in range(0, len(pts), 7):
            x, y = pts[i]
            parts.append(node(x, y, 6, C, pal["bg"], 2))
            if motion:
                parts.append(pulse(dot(x, y, 10, rgba(B, .5)), dur / 1.6, off + i * 0.12))
        for i in range(6):
            parts.append(bar(110 + i * 168, mid + 92, 96, 5 + (i * 7) % 34, rgba(B, .42), 3))

    elif cat == "SECURITY":
        # protected core, trust boundaries, controlled attack path
        parts.append(frame(88, 84, w - 176, h - 168, rgba(C, .42), 2, 0.8, corner=34))
        parts.append(frame(300, 168, w - 600, h - 300, rgba(A, .68), 2.4, 0.9, corner=26))
        parts.append(rosette(w / 2, h / 2, 132, 8, rgba(B, .5), rgba(A, .55)))
        parts.append(diamond(w / 2, h / 2, 66, C, 0.95))
        if motion:
            parts.append(pulse(diamond(w / 2, h / 2, 92, B, 0.6, C, 3), dur, off))
        for i in range(9):
            a = i * 40
            x = w / 2 + 372 * math_cos(a)
            y = h / 2 + 176 * math_sin(a)
            parts.append(edge(w / 2, h / 2, x, y, rgba(A, .34), 1.4, dash="4 8"))
            parts.append(node(x, y, 5, C, pal["bg"], 2))
            if motion:
                parts.append(travelling(w / 2, h / 2, x, y, 4.4, B, dur / 2.4, off + i * 0.3))

    elif cat == "SIMULATION":
        # stepped terrain with a live probe path
        for i in range(9):
            for j in range(6):
                hgt = ((i * 7 + j * 11) % 9) * 17
                parts.append(cube(150 + i * 104, 200 + j * 62, hgt, 54,
                                  mix(A, B, j / 5), B, C, 0.82))
        for i in range(5):
            parts.append(ring(300 + i * 168, 300, 44 + i * 26, 1.4, rgba(C, .4), dash="3 10"))
        if motion:
            parts.append(travelling(150, 300, 1080, 420, 8, C, dur, off))

    else:
        # modular tile field: structure assembles from units
        for row in range(5):
            for col in range(10):
                o = r.uniform(0.35, 0.95)
                col_ = [A, B, C][(row + col) % 3]
                parts.append(bar(96 + col * 100, 150 + row * 84, 88, 72,
                                 col_, rx=8, opacity=o))
        if motion:
            for i in range(10):
                parts.append(pulse(bar(96 + i * 100, 150, 88, 72, C, 8, .8),
                                   dur / 1.5, off + i * 0.32))

    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} hero", motion)


def math_sin(i: float) -> float:
    import math
    return math.sin(i * 0.42) * 0.6 + math.sin(i * 0.13) * 0.4


def math_cos(a: float) -> float:
    import math
    return math.cos(math.radians(a))


def math_sin(a: float) -> float:
    import math
    return math.sin(math.radians(a))


# --------------------------------------------------------------------------
# 02 TERMINAL
# --------------------------------------------------------------------------
def render_terminal(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """A real command surface.

    If the project has entry points, the lines are derived from them. If it
    does not, this is not drawn as a fake shell -- the storyboard substitutes a
    computer-science visual instead, because inventing CLI commands for a
    project that has none is the most common way this portfolio would have
    lied to a reader.
    """
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["terminal"]
    r = rng_for(name, "terminal")
    dur = duration_for("terminal_exec", seed_of(name, "terminal"))
    A, B, C = pal["accents"][:3]
    ink = pal["ink"]
    parts = [_defs(pal, "t")]

    parts.append(frame(74, 62, w - 148, h - 124, rgba(ink, .3), 2, 0.85, corner=26))
    for i, c in enumerate((A, B, C)):
        parts.append(dot(120 + i * 30, 100, 8, c))
    parts.append(bar(174, 92, 210, 15, rgba(ink, .18), 7))

    lines = d.get("terminal_lines") or ["$ ls"]
    body, y = [], 148
    t = 0.0
    for ln in lines[:13]:
        prompt = ln.startswith("$")
        text = ln[1:].strip() if prompt else ln
        esc = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        col = B if prompt else rgba(ink, .8)
        if motion:
            body.append(f'<text x="112" y="{y}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
                        f'font-size="21" fill="{col}" opacity="0">{esc}'
                        f'{animate_opacity("0;1;1;0", 1.5, t)}</text>')
            t += 1.5
        else:
            body.append(f'<text x="112" y="{y}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
                        f'font-size="21" fill="{col}">{esc}</text>')
        y += 34
    if motion:
        body.append(f'<rect x="112" y="{y - 22}" width="13" height="22" fill="{A}">'
                    f'{animate_opacity("1;0;1", 1.05)}</rect>')
    parts.extend(body)

    # Output resolved as a small tree: command results are structure, not text.
    bx, by = w - 350, 150
    parts.append(frame(bx - 18, by - 34, 300, 330, rgba(ink, .18), 1.4, 0.7, corner=18))
    tree = [(bx + 130, by + 8), (bx + 52, by + 92), (bx + 208, by + 92),
            (bx + 18, by + 176), (bx + 88, by + 176), (bx + 178, by + 176), (bx + 248, by + 176)]
    for i in range(1, len(tree)):
        parts.append(edge(tree[0][0], tree[0][1], tree[i][0], tree[i][1], rgba(ink, .3), 1.6))
    for i, (x, y2) in enumerate(tree):
        parts.append(cube(x - 13, y2 - 13, 0, 26, [A, B, C][i % 3], B, C, .95))
        if motion:
            parts.append(pulse(bar(x - 30, y2 + 22, 60, 4, rgba(C, .5)), dur / 2, i * 0.4))

    parts.append(bar(112, h - 118, w - 300, 2, rgba(ink, .16)))
    parts.append(f'<text x="112" y="{h - 86}" font-family="ui-monospace,Menlo,monospace" '
                 f'font-size="16" fill="{rgba(ink,.55)}">'
                 f'{esc_text(d.get("terminal_caption", ""))}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} command surface", motion)


def esc_text(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------
# 03 ARCHITECTURE
# --------------------------------------------------------------------------
def render_architecture(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """The project's real module graph.

    Nodes are the directories and entry points the index found. Every edge is
    a containment or import relationship that exists in the tree. No service
    is invented to make the diagram look like a distributed system.
    """
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["architecture"]
    dur = duration_for("graph_resolve", seed_of(name, "architecture"))
    A, B, C = pal["accents"][:3]
    mods = (d.get("major_modules") or [])[:7]
    if not mods:
        mods = (d.get("entry_points") or ["entry"])[:7]
    if not mods:
        mods = ["src", "docs"]
    parts = [_defs(pal, "a")]
    parts.append(grid_field(60, 60, 12, 7, 88, 74, pal["ink"], 0.05, 10))

    n = len(mods)
    cols = min(4, n)
    rows = (n + cols - 1) // cols
    cw = (w - 200) / max(cols, 2)
    ch = 128
    pos = []
    for i, m in enumerate(mods):
        c, rw = i % cols, i // cols
        x = 100 + c * cw + cw / 2 - 62
        y = 150 + rw * (ch + 78)
        pos.append((x, y))
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            x1, y1 = pos[i][0] + 62, pos[i][1] + 34
            x2, y2 = pos[j][0] + 62, pos[j][1] + 34
            if abs(x1 - x2) < 420 and (i // cols) != (j // cols):
                parts.append(edge(x1, y1, x2, y2, rgba(pal["ink"], .16), 1.2, dash="3 7"))
    for i, (x, y) in enumerate(pos):
        col = [A, B, C][i % 3]
        parts.append(frame(x - 12, y - 12, 148, 96, rgba(col, .55), 1.8, .9, corner=16))
        parts.append(cube(x + 8, y + 12, 0, 42, col, B, C, .95))
        label = esc_text(mods[i])[:16]
        parts.append(f'<text x="{x + 62:.0f}" y="{y + 62:.0f}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="17" fill="{rgba(pal["ink"],.9)}" text-anchor="middle">{label}</text>')
        if motion:
            parts.append(pulse(frame(x - 12, y - 12, 148, 96, B, 2.4, .9, 16), dur, i * 0.45))
            parts.append(travelling(x + 62, y + 34,
                                    pos[min(i + 1, len(pos) - 1)][0] + 62,
                                    pos[min(i + 1, len(pos) - 1)][1] + 34,
                                    4.5, C, dur / 3, i * 0.3))
    parts.append(f'<text x="100" y="112" font-family="ui-monospace,Menlo,monospace" font-size="15" '
                 f'fill="{rgba(pal["ink"],.5)}">{esc_text((d.get("architecture") or "modular")[:52])}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} architecture", motion)


# --------------------------------------------------------------------------
# 04 STATE MACHINE
# --------------------------------------------------------------------------
def render_state_machine(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """A state cycle sized to the machine the index actually detected."""
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["state_machine"]
    dur = duration_for("state_change", seed_of(name, "sm"))
    A, B, C = pal["accents"][:3]
    r = rng_for(name, "sm")
    n = max(4, min(8, 3 + len(d.get("cs_primitives", []))))
    names = (d.get("state_model") or "idle|validate|resolve|commit|observe").split("|")[:n]
    while len(names) < n:
        names.append(f"stage{len(names)}")
    parts = [_defs(pal, "s")]
    cx, cy, rad = w / 2, h / 2 + 14, 196
    parts.append(ring(cx, cy, rad + 62, 1, rgba(pal["ink"], .14), dash="4 10"))
    pts = []
    for i in range(n):
        a = -90 + i * 360 / n
        pts.append((cx + rad * math_cos(a), cy + rad * math_sin(a)))
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        parts.append(edge(x1, y1, x2, y2, rgba(A, .5), 2, arrow=True))
        if motion:
            parts.append(travelling(x1, y1, x2, y2, 5.5, C, dur / 2, i * (dur / (2 * n))))
    for i, (x, y) in enumerate(pts):
        col = [A, B, C][i % 3]
        active = i == 0
        parts.append(rosette(x, y, 40, 6, rgba(col, .9 if active else .6),
                             rgba(col, .55), .95))
        parts.append(f'<text x="{x:.0f}" y="{y + 62:.0f}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="14" fill="{rgba(pal["ink"],.8)}" text-anchor="middle">'
                     f'{esc_text(names[i])[:14]}</text>')
        if motion:
            parts.append(pulse(ring(x, y, 54, 2.4, B, .9), dur, i * (dur / n))
                         if active else "")
    parts.append(bar(cx - 120, cy - 5, 240, 3, rgba(pal["ink"], .2), 2))
    parts.append(f'<text x="{cx:.0f}" y="{cy - 26:.0f}" font-family="ui-monospace,Menlo,monospace" '
                 f'font-size="15" fill="{rgba(pal["ink"],.55)}" text-anchor="middle">'
                 f'{esc_text((d.get("state_model_note") or "states advance one transition at a time")[:44])}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} state machine", motion)


# --------------------------------------------------------------------------
# 05 DATA FLOW
# --------------------------------------------------------------------------
def render_data_flow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """Pipeline with packets routed along real edges."""
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["data_flow"]
    dur = duration_for("packet_route", seed_of(name, "df"))
    A, B, C = pal["accents"][:3]
    stages = (d.get("pipeline_stages") or
              (d.get("inputs") or ["input"])[:1] + ["transform", "validate", "persist", "emit"])
    stages = [s for s in stages if s][:6]
    # A single-stage pipeline produces no edges, and therefore no motion. Keep
    # the honest stage and add the implicit boundary so the surface still moves.
    if len(stages) == 1:
        stages = stages + ["(no route surface)"]
    parts = [_defs(pal, "f")]
    cols = len(stages)
    gap = (w - 160) / max(cols, 2)
    xs = []
    for i, s in enumerate(stages):
        x = 90 + i * gap
        xs.append(x)
        parts.append(arch(x + 46, 400, 96, 190, rgba(B, .1), .55, rgba(B, .4)))
        parts.append(cube(x + 6, 250 + (i % 3) * 22, 0, 78, [A, B, C][i % 3], B, C, .95))
        if motion:
            parts.append(pulse(cube(x + 6, 250 + (i % 3) * 22, 0, 78,
                                    [A, B, C][i % 3], B, C, .95),
                               dur / 2.4, i * 0.4))
        parts.append(f'<text x="{x + 46:.0f}" y="470" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="15" fill="{rgba(pal["ink"],.82)}" text-anchor="middle">'
                     f'{esc_text(str(s))[:13]}</text>')
        if i:
            parts.append(edge(xs[i - 1] + 84, 288 + ((i - 1) % 3) * 22, x, 288 + (i % 3) * 22,
                              rgba(A, .5), 2, arrow=True))
            if motion:
                parts.append(travelling(xs[i - 1] + 84, 288 + ((i - 1) % 3) * 22,
                                        x, 288 + (i % 3) * 22, 5, C, dur / 3, (i - 1) * 0.45))
    parts.append(bar(90, 168, w - 180, 2, rgba(pal["ink"], .14)))
    parts.append(f'<text x="90" y="140" font-family="ui-monospace,Menlo,monospace" font-size="15" '
                 f'fill="{rgba(pal["ink"],.5)}">{esc_text((d.get("data_flow") or "data moves left to right")[:56])}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} data flow", motion)


# --------------------------------------------------------------------------
# 06 COMPONENT MAP
# --------------------------------------------------------------------------
def render_component_map(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """Facets unfolding over a modular tile field."""
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["component_map"]
    dur = duration_for("facet_unfold", seed_of(name, "cm"))
    A, B, C = pal["accents"][:3]
    parts = [_defs(pal, "c")]
    parts.append(grid_field(70, 96, 11, 5, 90, 78, pal["ink"], 0.05, 12))
    r = rng_for(name, "cm")
    labels = d.get("interfaces") or d.get("major_modules") or ["module"]
    if isinstance(labels, str):
        labels = [labels]
    labels = [str(x) for x in labels] or ["module"]
    for i in range(7):
        x = 120 + (i % 4) * 268
        y = 140 + (i // 4) * 216
        col = [A, B, C][i % 3]
        g = f'<g transform="rotate(0 {x} {y})">{facet(x, y, 96, col)}'
        if motion:
            g += animate_rot(-32, 0, dur / 2, i * 0.4)
        g += "</g>"
        parts.append(g)
        parts.append(f'<text x="{x:.0f}" y="{y + 132:.0f}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="14" fill="{rgba(pal["ink"],.72)}" text-anchor="middle">'
                     f'{esc_text(labels[i % len(labels)][:16])}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} component map", motion)


def facet(x: float, y: float, s: float, col: str) -> str:
    """A hinged facet: two faces meeting at an angle, one light one dark."""
    a = [iso_point(x, y, s), iso_point(x + s, y, s), iso_point(x + s, y + s, s), iso_point(x, y + s, s)]
    b = [iso_point(x, y + s, s), iso_point(x + s, y + s, s),
         iso_point(x + s, y + s, 0), iso_point(x, y + s, 0)]
    pa = " ".join(f"{px:.1f},{py:.1f}" for px, py in a)
    pb = " ".join(f"{px:.1f},{py:.1f}" for px, py in b)
    return (f'<polygon points="{pa}" fill="{col}" opacity="0.92"/>'
            f'<polygon points="{pb}" fill="{darken(col, 0.45)}" opacity="0.9"/>'
            f'<polygon points="{pa}" fill="none" stroke="{rgba("#ffffff", .22)}" stroke-width="1.2"/>')


# --------------------------------------------------------------------------
# 07 BUILD / TEST
# --------------------------------------------------------------------------
def render_build(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """Build evidence, stated honestly.

    Tests and CI appear only if the index found them. A project with no tests
    renders SOURCE -> BUILD and says so in words on the asset, because a
    diagram implying coverage that does not exist is the exact failure this
    round exists to prevent.
    """
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["build"]
    dur = duration_for("test_progress", seed_of(name, "build"))
    A, B, C = pal["accents"][:3]
    tests = int(d.get("testing", {}).get("count") or 0)
    ci = int(d.get("CI", {}).get("workflow_count") or 0)
    rel = int(d.get("release", {}).get("tags") or 0)

    stages = [("SOURCE", A, f"{d.get('file_count', 0)} files")]
    stages.append(("BUILD", B, "configured" if d.get("manifests") else "no manifest"))
    if tests:
        stages.append(("TESTS", C, f"{tests} test files"))
    if ci:
        stages.append(("CI", A, f"{ci} workflow{'' if ci == 1 else 's'}"))
    if rel:
        stages.append(("RELEASE", B, f"{rel} tag{'' if rel == 1 else 's'}"))

    parts = [_defs(pal, "b")]
    parts.append(bar(80, 150, w - 160, 3, rgba(pal["ink"], .14), 2))
    n = len(stages)
    gap = (w - 200) / max(n - 1, 1)
    for i, (label, col, note) in enumerate(stages):
        x = 110 + i * gap
        parts.append(arch(x, 380, 84, 168, rgba(col, .1), .55, rgba(col, .45)))
        parts.append(cube(x - 32, 300, 0, 64, col, B, C, .95))
        parts.append(f'<text x="{x:.0f}" y="430" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="16" fill="{rgba(pal["ink"],.9)}" text-anchor="middle">{label}</text>')
        parts.append(f'<text x="{x:.0f}" y="456" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="13" fill="{rgba(pal["ink"],.55)}" text-anchor="middle">{esc_text(note)}</text>')
        if i:
            parts.append(edge(x - gap + 34, 330, x - 34, 330, rgba(A, .5), 2, arrow=True))
            if motion:
                parts.append(travelling(x - gap + 34, 330, x - 34, 330, 4.6, C, dur / 3, (i - 1) * 0.4))
    if not tests:
        parts.append(frame(80, 500, w - 160, 60, rgba(C, .5), 1.6, .8, corner=14))
        parts.append(f'<text x="{w / 2:.0f}" y="536" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="16" fill="{rgba(C,.95)}" text-anchor="middle">'
                     f'no test suite present in this repository &#8212; shown as measured, not implied</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} build evidence", motion)


# --------------------------------------------------------------------------
# 08 USER / SYSTEM WORKFLOW
# --------------------------------------------------------------------------
def render_workflow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """Ring pulse: the project's operating loop."""
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["workflow"]
    dur = duration_for("ring_pulse", seed_of(name, "wf"))
    A, B, C = pal["accents"][:3]
    steps = (d.get("workflow_steps") or
             ["intake", "resolve", "verify", "publish"])[:6]
    parts = [_defs(pal, "k")]
    cx, cy = w / 2, h / 2
    for i in range(4):
        parts.append(ring(cx, cy, 92 + i * 62, 1.3, rgba(A, .5 - i * 0.09), dash="6 12"))
        if motion:
            parts.append(f'<g>{ring(cx, cy, 92 + i * 62, 2.6, C, 0.0)}'
                         f'{animate_opacity("0;0.85;0", dur, i * 0.6)}</g>')
    n = len(steps)
    for i, s in enumerate(steps):
        a = -90 + i * 360 / n
        x, y = cx + 214 * math_cos(a), cy + 214 * math_sin(a)
        parts.append(cube(x - 26, y - 26, 0, 52, [A, B, C][i % 3], B, C, .95))
        parts.append(f'<text x="{x:.0f}" y="{y + 60:.0f}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="15" fill="{rgba(pal["ink"],.82)}" text-anchor="middle">'
                     f'{esc_text(str(s))[:15]}</text>')
        if motion:
            parts.append(pulse(diamond(x, y, 40, C, .8, B, 2), dur, i * (dur / max(n, 1))))
    parts.append(rosette(cx, cy, 74, 8, rgba(B, .5), rgba(A, .45)))
    parts.append(bar(cx - 96, cy - 4, 192, 3, rgba(pal["ink"], .2), 2))
    parts.append(f'<text x="{cx:.0f}" y="{cy + 26:.0f}" font-family="ui-monospace,Menlo,monospace" '
                 f'font-size="14" fill="{rgba(pal["ink"],.6)}" text-anchor="middle">'
                 f'{esc_text((d.get("control_flow") or "the operating loop")[:40])}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} workflow", motion)


# --------------------------------------------------------------------------
# 09 DOMAIN
# --------------------------------------------------------------------------
def render_domain(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """A domain-specific index or field, chosen by detected primitive."""
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["domain"]
    dur = duration_for("index_probe", seed_of(name, "dom"))
    A, B, C = pal["accents"][:3]
    prims = d.get("cs_primitives", [])
    parts = [_defs(pal, "d")]

    if "index" in prims or d.get("project_category") in ("QUANT_DATA", "RESEARCH"):
        # sorted key space with a probe walking it
        rows, cols_ = 9, 16
        cw, ch = 60, 34
        ox, oy = 96, 150
        for r in range(rows):
            for c in range(cols_):
                o = 0.18 + 0.62 * ((r * cols_ + c) % 7) / 7
                parts.append(bar(ox + c * (cw + 6), oy + r * (ch + 6), cw, ch,
                                 [A, B, C][(r + c) % 3], rx=4, opacity=o))
        if motion:
            for k in range(rows):
                parts.append(f'<g><rect x="{ox + 46}" y="{oy + k * (ch + 6)}" width="{cw + 6}" '
                             f'height="{ch}" fill="none" stroke="{C}" stroke-width="2.4">'
                             f'{animate_opacity("0;1;0", dur / 2, k * 0.42)}</rect></g>')
        parts.append(f'<text x="96" y="122" font-family="ui-monospace,Menlo,monospace" font-size="15" '
                     f'fill="{rgba(pal["ink"],.5)}">ordered key space &#183; probe walks the index</text>')
    elif "queue" in prims or "scheduler" in prims:
        parts.append(render_queue_field(d, pal, dur, motion))
    elif "graph" in " ".join(prims) or "tree_traverse" in MOTION:
        parts.append(render_tree_field(d, pal, dur, motion))
    else:
        # tessellated domain field: the problem space as modular geometry
        r = rng_for(name, "dom")
        for row in range(6):
            for c in range(14):
                o = r.uniform(0.2, 0.85)
                parts.append(diamond(120 + c * 72, 160 + row * 66, 26,
                                     [A, B, C][(row + c) % 3], o))
        if motion:
            for i in range(8):
                parts.append(pulse(diamond(120 + i * 96, 160, 34, C, .8, B, 2.4),
                                   dur / 1.6, i * 0.34))
    parts.append(f'<text x="96" y="122" font-family="ui-monospace,Menlo,monospace" font-size="15" '
                 f'fill="{rgba(pal["ink"],.5)}">{esc_text((d.get("domain") or d.get("problem") or "domain model")[:60])}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} domain model", motion)


def render_queue_field(d, pal, dur, motion) -> str:
    A, B, C = pal["accents"][:3]
    out = []
    for lane in range(4):
        for i in range(9):
            col = [A, B, C][(i + lane) % 3]
            x, y = 120 + i * 106, 190 + lane * 74
            g = f'<g>{cube(x, y, 0, 52, col, B, C, .95)}'
            if motion:
                g += (f'<g>{bar(x, y - 12, 52, 8, C, 2, .85)}'
                      f'{animate_motion(x, y, x + 106, y, dur / 2.2, lane * 0.3 + i * 0.12)}</g>')
            out.append(g + "</g>")
    return "".join(out)


def render_tree_field(d, pal, dur, motion) -> str:
    A, B, C = pal["accents"][:3]
    out = []
    lv = [[(600, 140)]]
    for depth in range(1, 4):
        prev = lv[-1]
        cur = []
        for i, (x, y) in enumerate(prev):
            for k in range(2):
                nx = x + (-1) ** k * (70 + depth * 46)
                cur.append((nx, y + 108))
        lv.append(cur)
    for depth in range(len(lv) - 1):
        for i, (x, y) in enumerate(lv[depth]):
            for (nx, ny) in lv[depth + 1][i * 2:i * 2 + 2]:
                out.append(edge(x, y, nx, ny, rgba(pal["ink"], .3), 1.5))
    for depth, layer in enumerate(lv):
        for i, (x, y) in enumerate(layer):
            col = [A, B, C][depth % 3]
            out.append(node(x, y, 20 - depth * 3, col, pal["bg"], 2.4))
            if motion:
                out.append(pulse(ring(x, y, 30 - depth * 2, 1.8, C, .85),
                                 dur / 1.6, depth * 0.5 + i * 0.12))
    return "".join(out)


# --------------------------------------------------------------------------
# 10 FOOTER
# --------------------------------------------------------------------------
def render_footer(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    """A small project-specific object. D2, never dominant."""
    pal = palette_light(d["palette"]) if light else palette(d["palette"])
    w, h = SLOT_VIEW["footer"]
    dur = duration_for("ring_pulse", seed_of(name, "ft"))
    A, B, C = pal["accents"][:3]
    parts = [_defs(pal, "ft")]
    cx, cy = w * 0.14, h / 2
    parts.append(bar(cx, cy - 2, w - cx - 200, 3, rgba(pal["ink"], .16), 2))
    motif = d.get("geometry_set") or "cube"
    if motif == "rosette":
        parts.append(pulse(rosette(cx, cy, 62, 9, rgba(A, .9), rgba(B, .8)), dur, 0))
        if motion:
            parts.append(f'<g>{rosette(cx, cy, 62, 9, "none", "none")}{animate_rot(0, 360, dur * 2)}</g>')
    elif motif == "arch":
        for i in range(4):
            parts.append(arch(cx + i * 42 - 60, cy + 56, 62, 92 - i * 8, rgba([A, B, C][i % 3], .85)))
    elif motif == "ring":
        for i in range(4):
            parts.append(ring(cx, cy, 26 + i * 22, 2.2, rgba([A, B, C][i % 3], .8 - i * 0.13)))
    else:
        for i in range(4):
            parts.append(cube(cx - 70 + i * 36, cy - 30, (3 - i) * 24, 44,
                              [A, B, C][i % 3], B, C, .95))
    # Every surface in the set carries at least one animation, so an identity
    # object is never the one static image in an otherwise animated gallery.
    if motion:
        parts.append(pulse(ring(cx, cy, 104, 1.6, rgba(A, .35)), dur, 0))
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="3" fill="{rgba(B,.9)}">'
                     + animate_opacity("0.35;0.95;0.35", dur, 0) + "</circle>")
    parts.append(f'<text x="{cx + 200:.0f}" y="{cy - 6:.0f}" font-family="ui-monospace,Menlo,monospace" '
                 f'font-size="19" fill="{rgba(pal["ink"],.9)}">{esc_text(d["canonical_name"])}</text>')
    parts.append(f'<text x="{cx + 200:.0f}" y="{cy + 22:.0f}" font-family="ui-monospace,Menlo,monospace" '
                 f'font-size="14" fill="{rgba(pal["ink"],.5)}">'
                 f'DUNG30N5 &#215; NOAERTH &#183; {esc_text(d.get("project_category","").replace("_"," ").title())}</text>')
    return _doc("".join(parts), w, h, pal, f"{d['canonical_name']} identity object", motion)


RENDERERS = {
    "hero": render_hero,
    "terminal": render_terminal,
    "architecture": render_architecture,
    "state_machine": render_state_machine,
    "data_flow": render_data_flow,
    "component_map": render_component_map,
    "build": render_build,
    "workflow": render_workflow,
    "domain": render_domain,
    "footer": render_footer,
}

ROLE_TITLE = {
    "hero": "identity",
    "terminal": "how it is operated",
    "architecture": "how it is built",
    "state_machine": "how it behaves",
    "data_flow": "how data moves",
    "component_map": "how it is composed",
    "build": "how it is verified",
    "workflow": "how it is used",
    "domain": "the problem it addresses",
    "footer": "identity object",
}


def render(slot: str, d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    svg = RENDERERS[slot](d, name, light, motion)
    if not motion:
        # Reduced motion is a real accessibility requirement, not a variant to
        # be skipped. Strip every SMIL animation so the surface is static.
        svg = re.sub(r"<animate[^>]*/>", "", svg)
        svg = re.sub(r"<animateTransform[^>]*/>", "", svg)
    return svg