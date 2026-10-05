"""Semantic geometry.

Every primitive here encodes a claim. That is the difference between a diagram
and decoration:

    nested_frames   CONTROL     something governs, from the outside in
    signal_path     EXECUTE     directed flow, one way, with a terminus
    branching       ECONOMY     one input, several priced paths
    closed_topology GUARD       containment; nothing escapes the boundary
    layered_evidence RESEARCH   stacked strata you could peel apart
    generative_field EXPERIMENTAL unresolved, self-similar, unfinished

``GENERIC_SHAPES`` exists so that a generator which reaches for a plain grid or
a plain rectangle is caught by review rather than drifting into meaninglessness.
"""
from __future__ import annotations

import math

from . import tokens as T

SEMANTIC_PRIMITIVES = {
    "nested_frames": "CONTROL",
    "signal_path": "EXECUTE",
    "branching": "ECONOMY",
    "closed_topology": "GUARD",
    "layered_evidence": "RESEARCH",
    "generative_field": "EXPERIMENTAL",
}


def _t(theme_name: str):
    return T.PALETTES[theme_name]


# --------------------------------------------------------------------------
# CONTROL - nested frames
# --------------------------------------------------------------------------
def nested_frames(x, y, w, h, theme_name: str, depth: int = 3,
                  accent: str | None = None) -> str:
    """Concentric insets. Reads as governance: each layer narrows authority.

    The innermost frame is the only one that carries the accent, because the
    thing being governed is the only thing that acts.
    """
    t = _t(theme_name)
    accent = accent or t["violet"]
    out = []
    for i in range(depth):
        inset = i * (w * 0.055)
        out.append(
            f'<rect x="{x + inset:.2f}" y="{y + inset:.2f}" '
            f'width="{w - inset * 2:.2f}" height="{h - inset * 2:.2f}" rx="{T.RADIUS["card"] - i * 2}" '
            f'fill="none" stroke="{accent if i == depth - 1 else t["edge"]}" '
            f'stroke-width="{T.STROKE["hairline"]}" '
            f'opacity="{0.9 if i == depth - 1 else 0.5 - i * 0.1:.2f}"/>'
        )
        # corner ticks: the precision detail that survives close inspection
        if i == depth - 1:
            for cx, cy, dx, dy in ((x + inset, y + inset, 1, 1),
                                   (x + w - inset, y + inset, -1, 1),
                                   (x + inset, y + h - inset, 1, -1),
                                   (x + w - inset, y + h - inset, -1, -1)):
                out.append(
                    f'<path d="M{cx:.2f} {cy + dy * 10:.2f} L{cx:.2f} {cy:.2f} '
                    f'L{cx + dx * 10:.2f} {cy:.2f}" fill="none" stroke="{accent}" '
                    f'stroke-width="{T.STROKE["signal"]}" stroke-opacity="0.85"/>'
                )
    return "".join(out)


# --------------------------------------------------------------------------
# EXECUTE - directed signal path
# --------------------------------------------------------------------------
def signal_path(points, theme_name: str, accent: str | None = None,
                arrow: bool = True) -> str:
    """A single directed path with a terminus marker.

    Deliberately not a mesh. Execution has a direction and an end, and drawing
    it as a network would claim relationships that do not exist.
    """
    t = _t(theme_name)
    accent = accent or t["mint"]
    if len(points) < 2:
        return ""
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:.2f} {y:.2f}" for i, (x, y) in enumerate(points))
    out = [f'<path d="{d}" fill="none" stroke="{t["edge"]}" '
           f'stroke-width="{T.STROKE["fine"] + 1}" stroke-linecap="round"/>']
    if arrow:
        (x0, y0), (x1, y1) = points[-2], points[-1]
        angle = math.atan2(y1 - y0, x1 - x0)
        size = 7
        a1 = (x1 - size * math.cos(angle - math.pi / 7),
              y1 - size * math.sin(angle - math.pi / 7))
        a2 = (x1 - size * math.cos(angle + math.pi / 7),
              y1 - size * math.sin(angle + math.pi / 7))
        out.append(
            f'<path d="M{a1[0]:.2f} {a1[1]:.2f} L{x1:.2f} {y1:.2f} L{a2[0]:.2f} {a2[1]:.2f}" '
            f'fill="none" stroke="{accent}" stroke-width="{T.STROKE["signal"]}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    out.append(f'<circle cx="{points[0][0]:.2f}" cy="{points[0][1]:.2f}" r="3.5" '
               f'fill="{t["canvas"]}" stroke="{accent}" stroke-width="{T.STROKE["fine"]}"/>')
    return "".join(out)


# --------------------------------------------------------------------------
# ECONOMY - prismatic branching
# --------------------------------------------------------------------------
def branching(x, y, theme_name: str, arms: int = 4, length: float = 46,
              accent: str | None = None) -> str:
    """One input splitting into several paths, each a different cost tier.

    The branches are unequal on purpose: equal-cost paths are a fiction.
    """
    t = _t(theme_name)
    accent = accent or t["indigo"]
    out = [f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{accent}"/>']
    spread = [-0.95, -0.35, 0.35, 0.95, 1.5][:arms]
    weights = [1.0, 0.78, 0.6, 0.44, 0.3][:arms]
    for angle, weight in zip(spread, weights):
        ex = x + math.cos(angle) * length * weight
        ey = y + math.sin(angle) * length * weight
        out.append(
            f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" '
            f'stroke="{accent}" stroke-width="{T.STROKE["fine"]}" '
            f'opacity="{0.35 + weight * 0.5:.2f}"/>'
        )
        out.append(
            f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{2 + weight * 2.4:.2f}" '
            f'fill="none" stroke="{accent}" stroke-width="{T.STROKE["hairline"]}" '
            f'opacity="{0.4 + weight * 0.45:.2f}"/>'
        )
    return "".join(out)


# --------------------------------------------------------------------------
# GUARD - closed containment
# --------------------------------------------------------------------------
def closed_topology(cx, cy, r, theme_name: str, accent: str | None = None,
                    nodes: int = 8) -> str:
    """A closed ring with containment nodes. Nothing crosses the boundary.

    The ring is deliberately drawn as a continuous path rather than a set of
    chords: a guard that leaks is not a guard.
    """
    t = _t(theme_name)
    accent = accent or t["fail"]
    out = [f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" '
           f'stroke="{accent}" stroke-width="{T.STROKE["fine"]}" opacity="0.75"/>',
           f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * 0.62:.2f}" fill="none" '
           f'stroke="{t["edge"]}" stroke-width="{T.STROKE["hairline"]}" opacity="0.6"/>']
    for i in range(nodes):
        a = (2 * math.pi * i / nodes) - math.pi / 2
        nx, ny = cx + math.cos(a) * r, cy + math.sin(a) * r
        ix, iy = cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62
        out.append(f'<line x1="{ix:.2f}" y1="{iy:.2f}" x2="{nx:.2f}" y2="{ny:.2f}" '
                   f'stroke="{t["edge"]}" stroke-width="{T.STROKE["hairline"]}" '
                   f'opacity="0.5"/>')
        out.append(f'<circle cx="{nx:.2f}" cy="{ny:.2f}" r="2.6" fill="{accent}" '
                   f'opacity="0.9"/>')
    return "".join(out)


# --------------------------------------------------------------------------
# RESEARCH - layered evidence
# --------------------------------------------------------------------------
def layered_evidence(x, y, w, h, theme_name: str, strata: int = 4,
                     accent: str | None = None) -> str:
    """Stacked translucent planes with a measurable tick rail.

    Reads as sediment: each layer was laid down later and can be interrogated
    separately. The tick rail is what makes it evidence rather than fog.
    """
    t = _t(theme_name)
    accent = accent or t["violet"]
    out = []
    step = h / strata
    for i in range(strata):
        oy = y + i * step * 0.55
        opacity = 0.10 + i * 0.07
        out.append(
            f'<path d="M{x:.2f} {oy:.2f} L{x + w * 0.18:.2f} {oy - step * 0.34:.2f} '
            f'L{x + w:.2f} {oy:.2f} L{x + w * 0.82:.2f} {oy + step * 0.34:.2f} Z" '
            f'fill="{accent}" fill-opacity="{opacity:.2f}" '
            f'stroke="{accent}" stroke-width="{T.STROKE["hairline"]}" '
            f'stroke-opacity="0.30"/>'
        )
    rail_y = y + h
    out.append(f'<line x1="{x:.2f}" y1="{rail_y:.2f}" x2="{x + w:.2f}" y2="{rail_y:.2f}" '
               f'stroke="{t["edge"]}" stroke-width="{T.STROKE["hairline"]}"/>')
    ticks = int(w // (T.TICK_STEP * 4))
    for i in range(ticks + 1):
        tx = x + i * (T.TICK_STEP * 4)
        major = i % 4 == 0
        out.append(
            f'<line x1="{tx:.2f}" y1="{rail_y:.2f}" x2="{tx:.2f}" '
            f'y2="{rail_y - (7 if major else 3):.2f}" stroke="{t["edge"]}" '
            f'stroke-width="{T.STROKE["hairline"]}" '
            f'opacity="{0.85 if major else 0.4:.2f}"/>'
        )
    return "".join(out)


# --------------------------------------------------------------------------
# EXPERIMENTAL - generative field
# --------------------------------------------------------------------------
def generative_field(x, y, w, h, theme_name: str, seed_points: int = 26,
                     accent: str | None = None) -> str:
    """A self-similar field that is explicitly unresolved.

    Uses a fixed LCG rather than random so the artwork is byte-reproducible.
    Non-deterministic art would make every regeneration a diff, and this
    repository commits its output.
    """
    t = _t(theme_name)
    accent = accent or t["mint"]
    state = 20251004
    out = []
    pts = []
    for _ in range(seed_points):
        state = (1103515245 * state + 12345) % (1 << 31)
        px = x + (state % 10000) / 10000 * w
        state = (1103515245 * state + 12345) % (1 << 31)
        py = y + (state % 10000) / 10000 * h
        pts.append((px, py))
    for i, (ax, ay) in enumerate(pts):
        # connect to the nearest neighbour: a mesh with a reason to exist
        best, best_d = None, 1e18
        for j, (bx, by) in enumerate(pts):
            if i == j:
                continue
            d = (ax - bx) ** 2 + (ay - by) ** 2
            if d < best_d:
                best, best_d = (bx, by), d
        if best and best_d < (w * 0.34) ** 2:
            out.append(
                f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{best[0]:.2f}" y2="{best[1]:.2f}" '
                f'stroke="{t["edge_link"]}" stroke-width="{T.STROKE["hairline"]}" '
                f'opacity="0.28"/>'
            )
        out.append(
            f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="{1.4 + (i % 3) * 0.5:.2f}" '
            f'fill="{accent}" opacity="{0.30 + (i % 4) * 0.12:.2f}"/>'
        )
    return "".join(out)


# --------------------------------------------------------------------------
# support geometry - structure, not meaning
# --------------------------------------------------------------------------
def micro_grid(w, h, theme_name: str, step: int | None = None,
               opacity: float = 0.5) -> str:
    """The recursive substrate. Quiet at arm's length, precise up close."""
    t = _t(theme_name)
    step = step or T.GRID_STEP
    out = []
    x = step
    while x < w:
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{t["grid"]}" '
                   f'stroke-width="{T.STROKE["hairline"]}"/>')
        x += step
    y = step
    while y < h:
        out.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{t["grid"]}" '
                   f'stroke-width="{T.STROKE["hairline"]}"/>')
        y += step
    return f'<g opacity="{opacity}">{"".join(out)}</g>'


def tick_rail(x, y, w, theme_name: str, major_every: int = 4) -> str:
    """Precision ticks. The detail that makes a plate read as an instrument."""
    t = _t(theme_name)
    out = [f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{t["edge"]}" '
           f'stroke-width="{T.STROKE["hairline"]}"/>']
    count = int(w // (T.TICK_STEP * 3))
    for i in range(count + 1):
        tx = x + i * T.TICK_STEP * 3
        major = i % major_every == 0
        out.append(
            f'<line x1="{tx:.1f}" y1="{y}" x2="{tx:.1f}" y2="{y - (6 if major else 2.5):.1f}" '
            f'stroke="{t["edge"]}" stroke-width="{T.STROKE["hairline"]}" '
            f'opacity="{0.8 if major else 0.35:.2f}"/>'
        )
    return "".join(out)


def node(x, y, r, theme_name: str, active: bool = False,
         accent: str | None = None) -> str:
    t = _t(theme_name)
    accent = accent or t["mint"]
    if active:
        return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{accent}" '
                f'fill-opacity="0.9"/>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r + 4:.2f}" fill="none" '
                f'stroke="{accent}" stroke-width="{T.STROKE["hairline"]}" '
                f'opacity="0.45"/>')
    return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{t["canvas"]}" '
            f'stroke="{t["edge_link"]}" stroke-width="{T.STROKE["fine"]}"/>')


def connector(x1, y1, x2, y2, theme_name: str, opacity: float = 0.3,
              accent: str | None = None) -> str:
    t = _t(theme_name)
    stroke = accent or t["edge_link"]
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{T.STROKE["hairline"]}" '
            f'opacity="{opacity}"/>')
