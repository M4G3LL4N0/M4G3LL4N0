"""V5.1 geometry: isometric architecture, faceted sculpture, and the bloom.

Extends the V5 semantic primitives rather than replacing them. The rule from the
standard holds: geometry must mean something. A cube is hierarchy, a step is
progress, a lattice is topology, a closed ring is containment.

Everything is drawn from a small grammar on purpose. Complex forms are assembled
from primitives, never hand-placed, so the system stays coherent and a single
edit propagates.
"""
from __future__ import annotations

import math

from . import tokens as T


def _t(theme: str):
    return T.PALETTES[theme]


# Iso projection: 2:1 dimetric. True isometric would be 26.57 degrees; 2:1 is
# what tile grids and technical illustration actually use, and it keeps stroke
# weights even.
_ISO_X, _ISO_Y = 0.8660254, 0.5


def iso_point(x: float, y: float, z: float, ox: float, oy: float,
              scale: float) -> tuple[float, float]:
    """Project a lattice coordinate into screen space.

    x runs right-and-down, y runs left-and-down, z runs straight up. Height is
    scaled at full rate while the two ground axes are foreshortened, which is
    what makes stacked forms read as towers rather than a flat diamond.
    """
    sx = (x - y) * _ISO_X * scale
    sy = (x + y) * _ISO_Y * scale - z * scale
    return ox + sx, oy + sy


def _poly(points: list, fill: str, opacity: float, stroke: str | None = None,
          stroke_width: float = 1.0) -> str:
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:.2f} {y:.2f}" for i, (x, y) in enumerate(points))
    s = f' stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="round"' if stroke else ""
    return f'<path d="{d}Z" fill="{fill}" fill-opacity="{opacity:.2f}"{s}/>'


# ==========================================================================
# isometric architecture
# ==========================================================================
def cube(cx, cy, size, theme_name, depth: str = "faceted",
         top: str | None = None, left: str | None = None, right: str | None = None,
         top_opacity: float = 0.92, side_opacity: float = 0.62) -> str:
    """A single cube. Reads as hierarchy: one unit, three visible planes.

    Three-tone shading is what makes it solid rather than an outline. The top
    plane is lightest because it faces the light, the left plane midtones, and
    the right plane darkest.
    """
    t = _t(theme_name)
    top = top or t["mint"]
    left = left or t["indigo"]
    right = right or t["violet"]
    h = size * 0.62
    w = size * _ISO_X
    dy = size * _ISO_Y

    top_face = [(cx, cy - h), (cx + w, cy - h + dy), (cx, cy - h + dy * 2), (cx - w, cy - h + dy)]
    left_face = [(cx - w, cy - h + dy), (cx, cy - h + dy * 2), (cx, cy + dy * 2), (cx - w, cy + dy)]
    right_face = [(cx + w, cy - h + dy), (cx, cy - h + dy * 2), (cx, cy + dy * 2), (cx + w, cy + dy)]

    parts = [_poly(right_face, right, side_opacity * 0.7),
             _poly(left_face, left, side_opacity),
             _poly(top_face, top, top_opacity)]
    if depth in ("faceted", "sculptural", "impossible"):
        # the interior diagonal is the detail that reads on close inspection
        parts.append(
            f'<line x1="{cx - w:.2f}" y1="{cy - h + dy:.2f}" x2="{cx:.2f}" '
            f'y2="{cy - h + dy * 2:.2f}" stroke="{t["edge_specular"]}" '
            f'stroke-width="0.75" stroke-opacity="0.30"/>')
    return "".join(parts)


def stacked_cube(cx, cy, size, levels, theme_name, accent_key="mint",
                 gap: float = 0.0) -> str:
    """Nesting and containment: one cube containing another, stacked.

    Levels ascend and shift, so the form reads as progression rather than a
    solid block. Used for control surfaces, where authority stacks.
    """
    t = _t(theme_name)
    accent = t[accent_key]
    out = []
    step = size * (1.0 + gap)
    for i in range(levels):
        shrink = 1.0 - (i * 0.12)
        out.append(cube(cx, cy - i * step * 0.62, size * shrink, theme_name,
                        top=accent, left=accent, right=accent,
                        top_opacity=0.90 - i * 0.16,
                        side_opacity=0.58 - i * 0.12))
    return "".join(out)


def stepped_progression(cx, cy, size, steps, theme_name, accent_key="mint") -> str:
    """Process progression. Each step is shorter than the last: work narrows."""
    t = _t(theme_name)
    accent = t[accent_key]
    out = []
    w = size * _ISO_X
    dy = size * _ISO_Y
    for i in range(steps):
        depth = size * (0.34 + i * 0.22)
        px = cx - (steps - i) * w * 0.62
        py = cy + i * dy * 1.15
        out.append(_poly([(px, py - depth), (px + w, py - depth + dy),
                          (px, py - depth + dy * 2), (px - w, py - depth + dy)],
                         accent, 0.34 + i * 0.16))
        out.append(f'<line x1="{px - w:.2f}" y1="{py - depth + dy:.2f}" '
                   f'x2="{px:.2f}" y2="{py - depth + dy * 2:.2f}" '
                   f'stroke="{t["edge_specular"]}" stroke-width="0.75" '
                   f'stroke-opacity="0.28"/>')
    return "".join(out)


def isometric_lattice(x, y, cols, rows, cell, theme_name, accent_key="mint",
                      occupancy: float = 0.55, seed: int = 99) -> str:
    """Distributed topology. Occupancy is deterministic, not random.

    A lattice with random occupancy would differ on every regeneration, and this
    repository commits its output, so a fixed LCG drives the fill instead.
    """
    t = _t(theme_name)
    accent = t[accent_key]
    out = []
    state = seed
    for cx_i in range(cols):
        for ry in range(rows):
            state = (1103515245 * state + 12345) % (1 << 31)
            if (state % 1000) / 1000.0 > occupancy:
                continue
            px = x + (cx_i - ry) * cell * _ISO_X
            py = y + (cx_i + ry) * cell * _ISO_Y
            # stacked height encodes presence: a taller cell is a busier node
            levels = 1 + ((state >> 10) % 3)
            for k in range(levels):
                out.append(cube(px, py - k * cell * 0.5, cell * 0.46, theme_name,
                                top=accent, left=accent, right=accent,
                                top_opacity=0.24 + k * 0.20,
                                side_opacity=0.14 + k * 0.10))
    return "".join(out)


def impossible_frame(cx, cy, size, theme_name, accent_key="violet") -> str:
    """An arch that cannot be built: two legs joined by a beam that reads as
    both nearer and further than the opening it spans.

    Depth through occlusion only. No blur, no perspective trickery.
    """
    t = _t(theme_name)
    accent = t[accent_key]
    r = size * 0.5
    out = [
        f'<path d="M{cx - r:.2f} {cy + r:.2f} L{cx - r:.2f} {cy:.2f} '
        f'A{r:.2f} {r:.2f} 0 0 1 {cx + r:.2f} {cy:.2f} '
        f'L{cx + r:.2f} {cy + r:.2f}" fill="none" stroke="{accent}" '
        f'stroke-width="{T.STROKE["signal"]}" stroke-opacity="0.85"/>',
        # inner offset arch: the shadow that gives the opening thickness
        f'<path d="M{cx - r * 0.72:.2f} {cy + r:.2f} L{cx - r * 0.72:.2f} {cy + r * 0.06:.2f} '
        f'A{r * 0.72:.2f} {r * 0.72:.2f} 0 0 1 {cx + r * 0.72:.2f} {cy + r * 0.06:.2f} '
        f'L{cx + r * 0.72:.2f} {cy + r:.2f}" fill="none" stroke="{t["edge"]}" '
        f'stroke-width="1" stroke-opacity="0.7"/>',
    ]
    ticks = 9
    for i in range(ticks):
        a = math.pi - math.pi * i / (ticks - 1)
        tx = cx + math.cos(a) * r
        ty = cy + math.sin(a) * r
        out.append(f'<circle cx="{tx:.2f}" cy="{ty:.2f}" r="1.8" '
                   f'fill="{t["edge_specular"]}" opacity="0.55"/>')
    return "".join(out)


# ==========================================================================
# faceted sculpture
# ==========================================================================
def diamond(cx, cy, w, h, theme_name, fill, opacity=0.8) -> str:
    return _poly([(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)],
                 fill, opacity)


def facet_ring(cx, cy, r_inner, r_outer, count, theme_name, fill,
               opacity=0.72, phase=0.0) -> str:
    """A ring of crystal facets tiling an annulus.

    The earlier version drew triangles from a small inner radius to a large
    outer one, which produced isolated spikes: a hexagram at level 1 and a
    spiky collar that turned to mush at 32px. Faceting reads as crystal only
    when the facets actually tile the band they occupy, so the inner radius
    sits close to the outer one and the count is high enough to close the ring.

    Alternating the outer radius by one facet gives the rim a faceted edge
    rather than a smooth circle.
    """
    out = []
    for i in range(count):
        a0 = phase + 2 * math.pi * i / count
        a1 = phase + 2 * math.pi * (i + 1) / count
        r_out = r_outer * (1.0 if i % 2 == 0 else 0.90)
        p0 = (cx + math.cos(a0) * r_inner, cy + math.sin(a0) * r_inner)
        p1 = (cx + math.cos(a1) * r_inner, cy + math.sin(a1) * r_inner)
        p2 = (cx + math.cos(a1) * r_out, cy + math.sin(a1) * r_out)
        p3 = (cx + math.cos(a0) * r_out, cy + math.sin(a0) * r_out)
        out.append(_poly([p0, p1, p2, p3], fill,
                         opacity if i % 2 == 0 else opacity * 0.72))
    return "".join(out)


def faceted_aperture(cx, cy, r, theme_name, accent_key="mint",
                     levels: int = 3, seed_phase: float = 0.0) -> str:
    """The V5.1 master motif: concentric bands of crystal facets.

    Named honestly. The brief proposed a "faceted bloom"; building it revealed
    that radial petal construction reads as a flower, which is exactly the soft
    ornamental register this system is supposed to avoid. Faceting an annulus
    instead produces an aperture: a precision iris with a solid core. It is
    more technical, more distinctive, and legible in silhouette at 32px, so the
    deviation is deliberate and recorded rather than papered over.

    Each level is a wide annulus of many small facets, decreasing in radius and
    increasing in count, so the form reads as a cut gemstone with depth rather
    than a star. Level count sets complexity: one level is a ringed mark, four
    is a sculpture.

    Legible in silhouette at 32px because the outermost band carries the shape
    on its own. Level 1 for marks and avatars, level 2 for plates, level 3 for
    hero scale.
    """
    t = _t(theme_name)
    accent = t[accent_key]
    out = []
    total = max(r, 1.0)
    for level in range(levels):
        r_out = total * (1.0 - level * 0.19)
        r_in = total * (1.0 - level * 0.19 - 0.085)
        count = 14 + level * 8
        # alternate a muted partner against the accent so the form has facets
        # instead of one flat colour
        fill = accent if level % 2 == 0 else t["indigo"]
        out.append(facet_ring(cx, cy, r_in, r_out, count, theme_name, fill,
                              opacity=0.88 - level * 0.16,
                              phase=seed_phase + level * 0.23))
    # the core: one saturated solid facet, the focal point of the form
    out.append(diamond(cx, cy, total * 0.115, total * 0.175, theme_name,
                       accent, 0.96))
    # radial spars: measurement detail, only visible on close inspection
    for i in range(levels * 4):
        a = seed_phase + 2 * math.pi * i / (levels * 4)
        out.append(
            f'<line x1="{cx + math.cos(a) * total * 0.30:.2f}" '
            f'y1="{cy + math.sin(a) * total * 0.30:.2f}" '
            f'x2="{cx + math.cos(a) * total * 1.02:.2f}" '
            f'y2="{cy + math.sin(a) * total * 1.02:.2f}" '
            f'stroke="{t["edge_specular"]}" stroke-width="0.6" '
            f'stroke-opacity="0.26"/>')
    return "".join(out)


def split_ring(cx, cy, r, theme_name, accent_key="fail", gap_deg=34) -> str:
    """A containment ring broken by a single gap.

    The gap is the meaning: this is a circuit that trips. Used for guardrail
    surfaces, where the interruption is the point rather than a style.
    """
    t = _t(theme_name)
    accent = t[accent_key]
    a0 = -gap_deg / 2
    a1 = 180 - gap_deg / 2
    large = 1 if (a1 - a0) > 180 else 0
    d = (f"M{cx + math.cos(math.radians(a0)) * r:.2f} "
         f"{cy + math.sin(math.radians(a0)) * r:.2f} "
         f"A{r:.2f} {r:.2f} 0 {large} 1 "
         f"{cx + math.cos(math.radians(a1)) * r:.2f} "
         f"{cy + math.sin(math.radians(a1)) * r:.2f}")
    out = [f'<path d="{d}" fill="none" stroke="{accent}" '
           f'stroke-width="{T.STROKE["signal"] + 0.5}" stroke-opacity="0.9"/>',
           f'<path d="{d}" fill="none" stroke="{t["edge_specular"]}" '
           f'stroke-width="4" stroke-opacity="0.10"/>']
    # trip markers on each side of the gap
    for a in (a0, a1):
        ax = cx + math.cos(math.radians(a)) * r
        ay = cy + math.sin(math.radians(a)) * r
        out.append(f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="2.6" '
                   f'fill="{accent}" opacity="0.95"/>')
    return "".join(out)


# ==========================================================================
# memphis punctuation — capped, never wallpaper
# ==========================================================================
def memphis_cluster(x, y, w, h, theme_name, accent_key="coral",
                    seed: int = 31) -> str:
    """A small punctuation cluster: dot matrix, diagonal stripes, one rod.

    Kept under MEMPHIS_SHARE of any surface. This exists so a plate has a bit of
    personality, not so a plate looks designed by a committee.
    """
    t = _t(theme_name)
    colours = [t["edge_specular"], t.get(accent_key, t["edge_specular"]),
               t["indigo"], t["mint"]]
    out = []
    state = seed

    def nxt(limit):
        nonlocal state
        state = (1103515245 * state + 12345) % (1 << 31)
        return (state % limit) / limit

    # dot matrix
    cols, rows = 4, 3
    for cxi in range(cols):
        for ryi in range(rows):
            if nxt(10) < 0.35:
                continue
            dx = x + cxi * 9
            dy = y + ryi * 9
            out.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="1.9" '
                       f'fill="{colours[0]}" opacity="0.55"/>')
    # diagonal stripes, one small patch
    sx = x + w * 0.52
    for i in range(4):
        off = i * 7
        out.append(f'<line x1="{sx + off:.1f}" y1="{y + h:.1f}" '
                   f'x2="{sx + off - h * 0.5:.1f}" y2="{y:.1f}" '
                   f'stroke="{colours[2]}" stroke-width="2.4" '
                   f'stroke-opacity="0.55"/>')
    # one rod
    out.append(f'<rect x="{x + w * 0.2:.1f}" y="{y + h * 0.6:.1f}" '
               f'width="30" height="5" rx="2.5" fill="{colours[1]}" '
               f'opacity="0.8"/>')
    return "".join(out)


# ==========================================================================
# soft counterpoint — the tension that keeps it human
# ==========================================================================
def arch_tile(x, y, w, h, theme_name, fill, opacity=0.7) -> str:
    """A rounded-top module. The soft partner to the crystalline forms."""
    r = w / 2
    return (f'<path d="M{x:.2f} {y + h:.2f} L{x:.2f} {y + r:.2f} '
            f'A{r:.2f} {r:.2f} 0 0 1 {x + w:.2f} {y + r:.2f} '
            f'L{x + w:.2f} {y + h:.2f}Z" fill="{fill}" '
            f'fill-opacity="{opacity:.2f}"/>')


def quarter_arc(cx, cy, r, theme_name, stroke, width=1.2, opacity=0.7) -> str:
    return (f'<path d="M{cx - r:.2f} {cy:.2f} A{r:.2f} {r:.2f} 0 0 1 '
            f'{cx:.2f} {cy - r:.2f}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-opacity="{opacity}"/>')

# The brief's name for this form, kept as an explicit alias so the vocabulary
# resolves without pretending the shape is botanical.
faceted_bloom = faceted_aperture
