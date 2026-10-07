#!/usr/bin/env python3
"""V8 geometry grammar and motion vocabulary.

One construction language, many compositions. Every visual in this portfolio
is assembled from the primitives below; none is hand-drawn per repository.
That is the primary speed mechanism and the primary duplication defence: if
two projects look alike, it is because they were given the same grammar
inputs, not because a template was copied.

The grammar is deliberately mixed -- isometric architecture, geometric
abstraction, dimensional sculpture, Memphis graphics, modular tiles,
retro-futurism -- and the tension is preserved rather than flattened. Hard
shapes sit against soft ones, flat plates against extruded blocks.

Determinism is a hard requirement. The same project and slot must always
produce byte-identical SVG, or the reproducibility gate fails and the Art Lock
becomes meaningless. Randomness comes only from a seeded generator derived
from project name and slot.
"""

from __future__ import annotations

import hashlib
import math
import random

# --------------------------------------------------------------------------
# Density
# --------------------------------------------------------------------------
# D1 minimal, D2 refined, D3 expressive, D4 showcase, D5 poster.
# README reading copy stays D1-D2; heroes run D3-D4; footer D2-D3.
DENSITY = {
    "D1": {"elements": 0.45, "detail": 0.4, "motion": 1},
    "D2": {"elements": 0.7, "detail": 0.7, "motion": 1},
    "D3": {"elements": 1.0, "detail": 1.0, "motion": 1},
    "D4": {"elements": 1.35, "detail": 1.3, "motion": 1},
    "D5": {"elements": 1.8, "detail": 1.6, "motion": 1},
}

# --------------------------------------------------------------------------
# Colour
# --------------------------------------------------------------------------
# Families are named, not random, so a project's palette carries meaning and
# two projects can be told apart by family alone. "coral + teal" is a
# different statement from "navy + lavender", and the pairing is chosen from
# the project's semantics rather than from its alphabetical position.
#
# Each family is (dark_bg, ink, accents[], soft, deep).
PALETTES = {
    "coral_teal":     ("#10141c", "#f2f5f9", ["#ff6b5a", "#2ec4b6", "#ffd166"], "#ffe8d6", "#0b3d4a"),
    "navy_lavender":  ("#0c1024", "#eef0fb", ["#7c83ff", "#b794f4", "#4cc9f0"], "#e6e1ff", "#1b1f4b"),
    "peach_cyan":     ("#1a1214", "#fdf4f0", ["#ffb4a2", "#48cae4", "#f9c74f"], "#ffe0d6", "#073b4c"),
    "cream_orange":   ("#1b1712", "#fdf6e9", ["#f4a261", "#e76f51", "#8ab17d"], "#fdecd3", "#4a2c1a"),
    "mint_violet":    ("#0f1714", "#f0f8f4", ["#95d5b2", "#b8a1e6", "#ffd6a5"], "#dcf5e8", "#1f3d33"),
    "slate_amber":    ("#141821", "#eef1f6", ["#ffb703", "#8d99ae", "#06d6a0"], "#fdf0d5", "#2b2f3a"),
    "indigo_lime":    ("#101228", "#f2f2ff", ["#8093f1", "#a7c957", "#ff8fab"], "#e3e7ff", "#25274d"),
    "rust_teal":      ("#17110f", "#f6efe9", ["#d97706", "#14b8a6", "#84cc16"], "#fae3cd", "#3b2a1c"),
    "plum_azure":     ("#140d1a", "#f4eef8", ["#9d4edd", "#48cae4", "#ffcb69"], "#efdcf7", "#2c1a3d"),
    "graphite_coral": ("#0f1113", "#f1f3f5", ["#ff7a5c", "#9aa5b1", "#ffd8b1"], "#ffe9e1", "#2b2f36"),
}

# Categories bias toward a family so colour also encodes meaning.
CATEGORY_PALETTE = {
    "SECURITY": "graphite_coral", "AGENT": "indigo_lime",
    "INFRASTRUCTURE": "slate_amber", "QUANT_DATA": "navy_lavender",
    "DEVELOPER_TOOLS": "mint_violet", "SIMULATION": "plum_azure",
    "MEDIA": "coral_teal", "RESEARCH": "cream_orange",
    "COMMERCE": "rust_teal", "PRODUCT": "peach_cyan",
}


def palette_for(category: str, seed: int) -> str:
    """Pick a palette from project semantics, not from a hash of the name."""
    if category in CATEGORY_PALETTE:
        return CATEGORY_PALETTE[category]
    names = sorted(PALETTES)
    return names[seed % len(names)]


def palette(name: str) -> dict:
    bg, ink, accents, soft, deep = PALETTES[name]
    return {"bg": bg, "ink": ink, "accents": accents, "soft": soft, "deep": deep}


def palette_light(name: str) -> dict:
    """Light variant.

    Not an inversion. The dark palette carries saturated accents on near-black;
    the light one keeps the same hues but lifts the ground to a tinted paper
    and darkens the accents so contrast survives.
    """
    p = palette(name)
    accents = [darken(a, 0.22) for a in p["accents"]]
    return {"bg": mix(p["soft"], "#ffffff", 0.55), "ink": darken(p["deep"], 0.15),
            "accents": accents, "soft": mix(p["soft"], "#ffffff", 0.2),
            "deep": darken(p["deep"], 0.3)}


# --------------------------------------------------------------------------
# Colour helpers
# --------------------------------------------------------------------------
def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix(a: str, b: str, t: float) -> str:
    ra, ga, ba = _rgb(a)
    rb, gb, bb = _rgb(b)
    return "#%02x%02x%02x" % (round(ra + (rb - ra) * t),
                             round(ga + (gb - ga) * t),
                             round(ba + (bb - ba) * t))


def darken(c: str, t: float) -> str:
    return mix(c, "#000000", t)


def lighten(c: str, t: float) -> str:
    return mix(c, "#ffffff", t)


def rgba(c: str, a: float) -> str:
    r, g, b = _rgb(c)
    return f"rgba({r},{g},{b},{a:.3f})"


# --------------------------------------------------------------------------
# Seeded determinism
# --------------------------------------------------------------------------
def rng_for(*parts: str) -> random.Random:
    """A generator whose state depends only on its inputs."""
    h = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


# --------------------------------------------------------------------------
# Motion vocabulary
# --------------------------------------------------------------------------
# Motion explains state. Each entry is a verb describing what the system does,
# and each maps to a duration band so a page of ten surfaces does not pulse in
# unison -- a portfolio that synchronises reads as a screensaver.
MOTION = {
    "tile_assemble":     {"dur": (12, 18), "desc": "tiles lock into a grid as structure forms"},
    "facet_unfold":      {"dur": (10, 16), "desc": "facets rotate open, exposing the interior"},
    "grid_snap":         {"dur": (9, 14),  "desc": "nodes snap to grid coordinates"},
    "dot_propagate":     {"dur": (11, 17), "desc": "signal propagates outward from a source node"},
    "plane_slide":       {"dur": (14, 22), "desc": "layers slide past, showing depth"},
    "tessellate":        {"dur": (13, 19), "desc": "shapes tessellate a plane edge to edge"},
    "layer_separate":    {"dur": (12, 18), "desc": "layers separate and recombine"},
    "graph_resolve":     {"dur": (15, 24), "desc": "a dependency graph resolves toward its roots"},
    "queue_advance":     {"dur": (10, 16), "desc": "queued work advances through stages"},
    "tree_traverse":     {"dur": (16, 26), "desc": "a traversal walks the structure"},
    "packet_route":      {"dur": (8, 13),  "desc": "packets route along edges"},
    "test_progress":     {"dur": (11, 18), "desc": "tests advance and results resolve"},
    "state_change":      {"dur": (9, 15),  "desc": "a state machine advances one transition"},
    "terminal_exec":     {"dur": (16, 30), "desc": "a command executes and output resolves"},
    "index_probe":       {"dur": (10, 17), "desc": "an index probe walks a sorted key space"},
    "pool_churn":        {"dur": (12, 19), "desc": "a worker pool claims and releases work"},
    "ring_pulse":        {"dur": (12, 20), "desc": "concentric rings pulse from a centre"},
    "bar_sweep":         {"dur": (7, 12),  "desc": "an ordered sweep crosses the field"},
}

# At most one or two surfaces per project carry continuous high-frequency
# motion. Everything else loops slowly or pauses.
HIGH_FREQUENCY = {"packet_route", "test_progress", "bar_sweep", "dot_propagate"}


def duration_for(motion: str, seed: int) -> float:
    lo, hi = MOTION[motion]["dur"]
    return round(rng_for("dur", motion, str(seed)).uniform(lo, hi), 1)


def stagger(seed: int, n: int, step: float = 0.35) -> list[float]:
    """Deliberate offsets so surfaces never animate in lockstep."""
    r = rng_for("stagger", str(seed))
    base = r.uniform(0, 6)
    return [round(base + i * step + r.uniform(-0.12, 0.12), 2) for i in range(n)]


# --------------------------------------------------------------------------
# Isometric geometry
# --------------------------------------------------------------------------
ISO_X, ISO_Y = 0.8660254, 0.5  # 30-degree isometric projection


def iso_point(x: float, y: float, z: float) -> tuple[float, float]:
    return ((x - y) * ISO_X, (x + y) * ISO_Y - z)


def cube(x: float, y: float, z: float, s: float, top: str, left: str, right: str,
         opacity: float = 1.0) -> str:
    """An extruded isometric block: three visible faces, deliberately distinct.

    Flat and dimensional at once. The top face carries the accent, the sides
    are darkened versions of it, which is what keeps the composition reading
    as sculpture rather than as a flat Memphis pattern.
    """
    p = [iso_point(x, y, z + s), iso_point(x + s, y, z + s),
         iso_point(x + s, y + s, z + s), iso_point(x, y + s, z + s),
         iso_point(x, y, z), iso_point(x + s, y, z),
         iso_point(x + s, y + s, z), iso_point(x, y + s, z)]

    def poly(pts, fill, o=1.0):
        d = " ".join(f"{px:.2f},{py:.2f}" for px, py in pts)
        return (f'<polygon points="{d}" fill="{fill}" opacity="{o:.2f}"/>')

    return "".join([
        poly([p[4], p[5], p[1], p[0]], darken(right, 0.42), opacity),
        poly([p[7], p[6], p[2], p[3]], darken(left, 0.22), opacity),
        poly([p[0], p[1], p[2], p[3]], top, opacity),
    ])


def diamond(cx: float, cy: float, r: float, fill: str, opacity: float = 1.0,
            stroke: str | None = None, sw: float = 1.5) -> str:
    d = f"{cx:.2f},{cy - r:.2f} {cx + r:.2f},{cy:.2f} {cx:.2f},{cy + r:.2f} {cx - r:.2f},{cy:.2f}"
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<polygon points="{d}" fill="{fill}" opacity="{opacity:.2f}"{st}/>'


def wedge(cx: float, cy: float, r: float, angle: float, span: float,
          fill: str, opacity: float = 1.0) -> str:
    """A pie slice. Angles in degrees, clockwise from twelve o'clock."""
    a0 = math.radians(angle - span / 2)
    a1 = math.radians(angle + span / 2)
    x0, y0 = cx + r * math.sin(a0), cy - r * math.cos(a0)
    x1, y1 = cx + r * math.sin(a1), cy - r * math.cos(a1)
    large = 1 if span > 180 else 0
    return (f'<path d="M{cx:.2f},{cy:.2f} L{x0:.2f},{y0:.2f} '
            f'A{r:.2f},{r:.2f} 0 {large} 1 {x1:.2f},{y1:.2f} Z" '
            f'fill="{fill}" opacity="{opacity:.2f}"/>')


def arch(cx: float, base_y: float, w: float, h: float, fill: str,
         opacity: float = 1.0, stroke: str | None = None, sw: float = 1.4) -> str:
    r = w / 2
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (f'<path d="M{cx - r:.2f},{base_y:.2f} L{cx - r:.2f},{base_y - h + r:.2f} '
            f'A{r:.2f},{r:.2f} 0 0 1 {cx + r:.2f},{base_y - h + r:.2f} '
            f'L{cx + r:.2f},{base_y:.2f} Z" fill="{fill}" opacity="{opacity:.2f}"{st}/>')


def ring(cx: float, cy: float, r: float, sw: float, stroke: str,
         opacity: float = 1.0, dash: str | None = None) -> str:
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw:.2f}" opacity="{opacity:.2f}"{da}/>')


def dot(cx: float, cy: float, r: float, fill: str, opacity: float = 1.0) -> str:
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" opacity="{opacity:.2f}"/>'


def bar(x: float, y: float, w: float, h: float, fill: str, rx: float = 0,
        opacity: float = 1.0) -> str:
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'rx="{rx:.2f}" fill="{fill}" opacity="{opacity:.2f}"/>')


def triangle(x: float, y: float, s: float, fill: str, opacity: float = 1.0,
             rot: float = 0) -> str:
    pts = [f"{x:.2f},{y - s:.2f}", f"{x + s * 0.866:.2f},{y + s * 0.5:.2f}",
           f"{x - s * 0.866:.2f},{y + s * 0.5:.2f}"]
    return (f'<polygon points="{" ".join(pts)}" fill="{fill}" opacity="{opacity:.2f}"'
            + (f' transform="rotate({rot:.1f} {x:.2f} {y:.2f})"' if rot else "") + "/>")


def petal(cx: float, cy: float, r: float, angle: float, w: float,
          fill: str, opacity: float = 1.0) -> str:
    a = math.radians(angle)
    x, y = cx + r * math.sin(a), cy - r * math.cos(a)
    return (f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{w:.2f}" ry="{r * 0.55:.2f}" '
            f'fill="{fill}" opacity="{opacity:.2f}" '
            f'transform="rotate({angle:.1f} {x:.2f} {y:.2f})"/>')


def rosette(cx: float, cy: float, r: float, n: int, fill: str, alt: str,
            opacity: float = 1.0) -> str:
    out = []
    for i in range(n):
        out.append(petal(cx, cy, r, i * 360 / n, r * 0.30,
                         fill if i % 2 == 0 else alt, opacity))
    out.append(ring(cx, cy, r * 0.42, max(1.0, r * 0.035), fill, opacity * 0.7))
    out.append(dot(cx, cy, r * 0.16, alt))
    return "".join(out)


def frame(x: float, y: float, w: float, h: float, stroke: str, sw: float = 1.2,
          opacity: float = 0.5, corner: float = 0) -> str:
    """A frame with optional cut corners -- retro-futurist, not a plain box."""
    c = corner
    if c <= 0:
        return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
                f'fill="none" stroke="{stroke}" stroke-width="{sw:.2f}" opacity="{opacity:.2f}"/>')
    d = (f"M{x + c:.2f},{y:.2f} H{x + w - c:.2f} L{x + w:.2f},{y + c:.2f} "
         f"V{y + h - c:.2f} L{x + w - c:.2f},{y + h:.2f} H{x + c:.2f} "
         f"L{x:.2f},{y + h - c:.2f} V{y + c:.2f} Z")
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw:.2f}" '
            f'opacity="{opacity:.2f}"/>')


def grid_field(x: float, y: float, cols: int, rows: int, cw: float, ch: float,
               fill: str, opacity: float = 0.16, gap: float = 1.5) -> str:
    out = []
    for r in range(rows):
        for c in range(cols):
            out.append(bar(x + c * (cw + gap), y + r * (ch + gap),
                           cw, ch, fill, rx=1.2, opacity=opacity))
    return "".join(out)


def node(x: float, y: float, r: float, fill: str, stroke: str | None = None,
         sw: float = 2.0, opacity: float = 1.0) -> str:
    st = f' stroke="{stroke}" stroke-width="{sw:.2f}"' if stroke else ""
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" opacity="{opacity:.2f}"{st}/>'


def edge(x1: float, y1: float, x2: float, y2: float, stroke: str, sw: float = 1.4,
         opacity: float = 0.55, dash: str | None = None, arrow: bool = False) -> str:
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = ""
    if arrow:
        import math as _m
        a = _m.atan2(y2 - y1, x2 - x1)
        L, S = sw * 3.4, sw * 1.9
        p1 = (x2 - L * _m.cos(a) + S * _m.sin(a), y2 - L * _m.sin(a) - S * _m.cos(a))
        p2 = (x2 - L * _m.cos(a) - S * _m.sin(a), y2 - L * _m.sin(a) + S * _m.cos(a))
        mk = (f'<polygon points="{x2:.2f},{y2:.2f} {p1[0]:.2f},{p1[1]:.2f} '
              f'{p2[0]:.2f},{p2[1]:.2f}" fill="{stroke}" opacity="{opacity:.2f}"/>')
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{sw:.2f}" opacity="{opacity:.2f}"{da}/>{mk}')


# --------------------------------------------------------------------------
# SMIL helpers
# --------------------------------------------------------------------------
_MOTION = True


def set_motion(enabled: bool) -> None:
    """Switch every animation helper on or off.

    Reduced-motion is not a smaller version of the same file: it is the same
    composition with no time in it. Leaving one unguarded call site meant the
    reduced-motion hero still animated, which is exactly the failure this
    variant exists to prevent.
    """
    global _MOTION
    _MOTION = enabled


def animate(attr: str, values: str, dur: float, begin: float = 0,
            repeat: str = "indefinite", extra: str = "") -> str:
    if not _MOTION:
        return ""
    return (f'<animate attributeName="{attr}" values="{values}" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="{repeat}" {extra}/>')


def animate_motion(x1: float, y1: float, x2: float, y2: float, dur: float,
                   begin: float = 0, extra: str = "") -> str:
    if not _MOTION:
        return ""
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="{x1:.2f},{y1:.2f} {x2:.2f},{y2:.2f}" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite" {extra}/>')


def animate_opacity(values: str, dur: float, begin: float = 0) -> str:
    return animate("opacity", values, dur, begin)


def animate_rot(a0: float, a1: float, dur: float, begin: float = 0,
                cx: float = 0, cy: float = 0) -> str:
    if not _MOTION:
        return ""
    return (f'<animateTransform attributeName="transform" type="rotate" '
            f'values="{a0:.1f} {cx:.2f} {cy:.2f} {a1:.1f} {cx:.2f} {cy:.2f}" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')


def pulse(node_xml: str, dur: float, begin: float, lo: float = 0.25,
          hi: float = 1.0) -> str:
    """Wrap a shape in a group so opacity can be animated independently."""
    if not _MOTION:
        return node_xml
    return (f'<g>{node_xml}{animate_opacity(f"{lo};{hi};{lo}", dur, begin)}</g>')


def travelling(x1: float, y1: float, x2: float, y2: float, r: float, fill: str,
               dur: float, begin: float = 0, back: bool = True) -> str:
    """A signal moving along an edge, with the trail it leaves."""
    if not _MOTION:
        return dot(x1, y1, r, fill)
    if not back:
        return dot(x1, y1, r, fill) + animate_motion(x1, y1, x2, y2, dur, begin)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    return (f'<g opacity="0.9">{dot(0, 0, r, fill)}'
            f'{animate_motion(x1, y1, x2, y2, dur, begin)}'
            f'{animate_motion(x2, y2, x1, y1, dur, begin + dur / 2)}</g>')


def sequence(values: list[str], times: list[float], dur: float,
             begin: float = 0, keytimes: str | None = None) -> str:
    """Discrete step animation, for state machines and staged pipelines."""
    if not _MOTION:
        return ""
    kt = keytimes or ";".join(f"{t / dur:.4f}" for t in times)
    return (f'<set attributeName="opacity" to="{values[0]}" begin="{begin}s" dur="{dur}s" '
            f'repeatCount="indefinite" values="{";".join(values)}" keyTimes="{kt}"/>')


def step_opacity(items: list[str], durs: list[float], begin: float = 0) -> str:
    """Reveal list items one after another, then hold.

    Used instead of continuous animation so the majority of surfaces are
    sparse rather than permanently in motion.
    """
    total = sum(durs)
    out, t = [], begin
    for i, d in enumerate(durs):
        vals = ["0"] * len(durs)
        vals[i] = "1"
        times = [0.0]
        for j in range(len(durs)):
            times.append(min(total, sum(durs[:j + 1])))
        out.append(sequence(vals, times, total, t))
        t += 0
    return "".join(out)