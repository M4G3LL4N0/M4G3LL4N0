"""Clay-and-adobe 3D primitives for the New Mexico visual system.

Every solid is three flat-shaded faces: a lit top, a mid front, and a shaded
side, all derived from one base colour. That is enough to read as sculpted
volume at GitHub thumbnail size, and it keeps each surface small enough to
render 3,500 times deterministically.

The visual grammar is deliberately reduced: chunky masses, generous corner
radii, shallow extrusions, and no surface detail. Rounded joins on the extruded
quads are what sell the clay read without a single gradient.
"""

from __future__ import annotations

import random

# ---------------------------------------------------------------------------
# New Mexico palette: adobe, terracotta, sand and cactus against dusk blue.
# ---------------------------------------------------------------------------
PALETTE = {
    "dusk_deep": "#1b2a4a",
    "dusk_mid": "#2e4a6b",
    "dusk_soft": "#4a6b8a",
    "adobe": "#e2725b",
    "terracotta": "#c1683f",
    "clay_red": "#a8543c",
    "ember": "#e2573b",
    "sand": "#e3c08d",
    "cream": "#f6e7ce",
    "beige": "#d9b98c",
    "peach": "#f2a07b",
    "coral": "#e08467",
    "turquoise": "#5b9a97",
    "cactus": "#7a9a5c",
    "sage": "#9bb07a",
    "sun": "#f5c95c",
    "shadow": "#8a5a44",
}

# Per-repository colourways. Each is a cohesive New Mexico triad: one clay mass
# colour, one supporting mass, one cool accent, plus the shared sky. Cohesion
# across the portfolio matters more than maximum variety, so every entry stays
# inside the adobe-to-cactus family.
CLAY_PALETTES: dict[str, dict] = {
    "adobe_dusk":      {"sky": "dusk_deep",   "mass": "adobe",      "alt": "sand",      "cool": "turquoise", "trim": "cream"},
    "terracotta_rose": {"sky": "dusk_mid",    "mass": "terracotta", "alt": "peach",     "cool": "cactus",    "trim": "cream"},
    "clay_sand":       {"sky": "dusk_deep",   "mass": "clay_red",   "alt": "beige",     "cool": "turquoise", "trim": "sand"},
    "peach_dusk":      {"sky": "dusk_soft",   "mass": "coral",      "alt": "cream",     "cool": "sage",      "trim": "sun"},
    "cactus_clay":     {"sky": "dusk_mid",    "mass": "cactus",     "alt": "sand",      "cool": "turquoise", "trim": "cream"},
    "sunset_adobe":    {"sky": "dusk_deep",   "mass": "ember",      "alt": "peach",     "cool": "sage",      "trim": "cream"},
    "sand_turquoise":  {"sky": "dusk_soft",   "mass": "beige",      "alt": "coral",     "cool": "turquoise", "trim": "cream"},
    "mesa_terracotta": {"sky": "dusk_deep",   "mass": "terracotta", "alt": "sand",      "cool": "sage",      "trim": "sun"},
    "rose_clay":       {"sky": "dusk_mid",    "mass": "coral",      "alt": "beige",     "cool": "turquoise", "trim": "cream"},
    "sun_dusk":        {"sky": "dusk_deep",   "mass": "sun",        "alt": "adobe",     "cool": "turquoise", "trim": "cream"},
    "sage_beige":      {"sky": "dusk_soft",   "mass": "sage",       "alt": "cream",     "cool": "terracotta", "trim": "sand"},
    "ember_cactus":    {"sky": "dusk_deep",   "mass": "ember",      "alt": "cactus",    "cool": "turquoise", "trim": "sand"},
}

CLAY_PALETTE_NAMES = sorted(CLAY_PALETTES)


# ---------------------------------------------------------------------------
# colour maths
# ---------------------------------------------------------------------------
def _rgb(c: str) -> tuple[int, int, int]:
    c = PALETTE.get(c, c).lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _hex(r: float, g: float, b: float) -> str:
    return "#%02x%02x%02x" % (
        max(0, min(255, round(r))),
        max(0, min(255, round(g))),
        max(0, min(255, round(b))),
    )


def tint(c: str, t: float) -> str:
    """t > 0 toward cream light, t < 0 toward dusk shadow."""
    r, g, b = _rgb(c)
    if t >= 0:
        tr, tg, tb = _rgb("cream")
        return _hex(r + (tr - r) * t, g + (tg - g) * t, b + (tb - b) * t)
    tr, tg, tb = _rgb("dusk_deep")
    u = -t
    return _hex(r + (tr - r) * u, g + (tg - g) * u, b + (tb - b) * u)


def alpha(c: str, a: float) -> str:
    r, g, b = _rgb(c)
    return _hex(r, g, b) if a >= 1 else f"rgba({r},{g},{b},{a:.2f})"


def seed_of(name: str, slot: str) -> int:
    """Stable per (repository, slot) integer seed."""
    return rng_for(name, slot).randint(0, 10_000_000)


def rng_for(*parts: str) -> random.Random:
    """Deterministic across processes: never use hash() or time()."""
    import hashlib
    seed = int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:12], 16)
    return random.Random(seed)


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def col(c: str) -> str:
    """Resolve a palette key name to its hex.

    Callers pass colour names like "sand"; writing those straight into an SVG
    fill attribute produces an invalid colour and the shape renders black.
    """
    return PALETTE.get(c, c)


def _f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# soft ground shadow
# ---------------------------------------------------------------------------
def ground_shadow(cx: float, cy: float, rx: float, ry: float,
                  a: float = 0.11) -> str:
    return (f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" '
            f'ry="{_f(ry)}" fill="{alpha(PALETTE["shadow"], a)}"/>')


# ---------------------------------------------------------------------------
# solids: three flat faces, rounded joins
# ---------------------------------------------------------------------------
def clay_box(x: float, y: float, w: float, h: float, d: float, fill: str,
             r: float = 0.0, round_join: float = 5.0) -> str:
    """A chunky extruded block seen from slightly above and to the right."""
    fill = col(fill)
    top = tint(fill, 0.22)
    side = tint(fill, -0.17)
    j = f' stroke="{fill}" stroke-width="{_f(round_join)}" stroke-linejoin="round"' if round_join else ""
    r = min(r, w / 2.2, h / 2.2)
    # top face, then right face, then the rounded front. Same-colour strokes on
    # the quads round their corners, which is what makes them read as clay
    # rather than as hard vector facets.
    parts = [
        f'<path d="M{_f(x)},{_f(y)} L{_f(x + w)},{_f(y)} '
        f'L{_f(x + w + d)},{_f(y - d)} L{_f(x + d)},{_f(y - d)} Z" '
        f'fill="{top}"{j}/>',
        f'<path d="M{_f(x + w)},{_f(y)} L{_f(x + w + d)},{_f(y - d)} '
        f'L{_f(x + w + d)},{_f(y + h - d)} L{_f(x + w)},{_f(y + h)} Z" '
        f'fill="{side}"{j}/>',
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(r)}" fill="{fill}"/>',
    ]
    return "".join(parts)


def clay_cylinder(x: float, y: float, w: float, h: float, fill: str,
                  r: float = 0.0) -> str:
    """A soft column or drum: rounded body plus a lit elliptical cap."""
    fill = col(fill)
    cap = min(w / 2.6, h / 5.0)
    rx, ry = w / 2, cap
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(r if r else min(w, h) / 3)}" fill="{fill}"/>',
        f'<ellipse cx="{_f(x + w / 2)}" cy="{_f(y)}" rx="{_f(rx)}" ry="{_f(ry)}" '
        f'fill="{tint(fill, 0.22)}"/>',
        f'<rect x="{_f(x)}" y="{_f(y + h - cap)}" width="{_f(w)}" height="{_f(cap)}" '
        f'fill="{tint(fill, -0.14)}"/>',
    ])


def clay_arch(x: float, y: float, w: float, h: float, fill: str,
              leg: float = 0.22, d: float = 14.0) -> str:
    """The rounded adobe arch that gives the system its regional signature.

    The opening is a real cutout via fill-rule evenodd. A filled outline read
    as a tombstone slab rather than as a gateway.
    """
    fill = col(fill)
    lw = w * leg
    r = (w - 2 * lw) / 2
    spring = y + r
    outer = (f"M{_f(x)},{_f(y + h)} L{_f(x)},{_f(spring)} "
             f"A{_f(r + lw)},{_f(r + lw)} 0 0 1 {_f(x + w)},{_f(spring)} "
             f"L{_f(x + w)},{_f(y + h)} Z")
    inner_h = h - r * 1.1
    inner = (f"M{_f(x + lw)},{_f(y + h - 4)} L{_f(x + lw)},{_f(y + r * 0.92)} "
             f"A{_f(r)},{_f(r)} 0 0 1 {_f(x + w - lw)},{_f(y + r * 0.92)} "
             f"L{_f(x + w - lw)},{_f(y + h - 4)} Z")
    # No flat top quad: a straight extrusion across a curved arch detaches as a
    # floating wing. Depth comes from a lit rim instead.
    return "".join([
        f'<path d="{outer} {inner}" fill="{fill}" fill-rule="evenodd" '
        f'stroke="{fill}" stroke-width="5" stroke-linejoin="round"/>',
        f'<path d="{outer}" fill="none" stroke="{tint(fill, 0.24)}" '
        f'stroke-width="7" stroke-linecap="round" opacity="0.85"/>',
        f'<rect x="{_f(x + w * 0.05)}" y="{_f(y + r)}" width="{_f(w * 0.05)}" '
        f'height="{_f(h - r)}" fill="{tint(fill, -0.14)}"/>',
    ])


def clay_cone(cx: float, base_y: float, w: float, h: float, fill: str,
              r: float = 0.0) -> str:
    """A soft pyramid, used for conifers and roof forms."""
    fill = col(fill)
    return (f'<path d="M{_f(cx)},{_f(base_y - h)} '
            f'Q{_f(cx - w / 2)},{_f(base_y - h * 0.42)} {_f(cx - w / 2)},{_f(base_y - h * 0.18)} '
            f'Q{_f(cx - w / 2)},{_f(base_y)} {_f(cx - w / 2 + r)},{_f(base_y)} '
            f'L{_f(cx + w / 2 - r)},{_f(base_y)} '
            f'Q{_f(cx + w / 2)},{_f(base_y)} {_f(cx + w / 2)},{_f(base_y - h * 0.18)} '
            f'Q{_f(cx + w / 2)},{_f(base_y - h * 0.42)} {_f(cx)},{_f(base_y - h)} Z" '
            f'fill="{fill}"/>')


def clay_tree(cx: float, base_y: float, w: float, h: float, fill: str,
              tiers: int = 3) -> str:
    """Stacked rounded tiers, the low-poly conifer from the reference scenes."""
    fill = col(fill)
    trunk_h = h * 0.16
    out = [f'<rect x="{_f(cx - w * 0.09)}" y="{_f(base_y - trunk_h)}" '
           f'width="{_f(w * 0.18)}" height="{_f(trunk_h)}" rx="{_f(w * 0.05)}" '
           f'fill="{tint("clay_red", 0.05)}"/>']
    for i in range(tiers):
        t = i / max(tiers - 1, 1)
        ty = base_y - trunk_h - i * (h - trunk_h) / tiers
        tw = w * (1.0 - 0.26 * i)
        th = (h - trunk_h) / tiers * 1.5
        out.append(clay_cone(cx, ty, tw, th, tint(fill, 0.16 - 0.1 * i)))
    return "".join(out)


def clay_cactus(cx: float, base_y: float, w: float, h: float, fill: str) -> str:
    """A saguaro silhouette: one column and two stubby arms."""
    fill = col(fill)
    bw = w * 0.34
    arm_h = h * 0.34
    return "".join([
        f'<rect x="{_f(cx - bw / 2)}" y="{_f(base_y - h)}" width="{_f(bw)}" '
        f'height="{_f(h)}" rx="{_f(bw / 2)}" fill="{fill}"/>',
        f'<rect x="{_f(cx - w * 0.62)}" y="{_f(base_y - h * 0.66)}" '
        f'width="{_f(w * 0.3)}" height="{_f(arm_h)}" rx="{_f(w * 0.15)}" fill="{fill}"/>',
        f'<rect x="{_f(cx - w * 0.62)}" y="{_f(base_y - h * 0.66)}" '
        f'width="{_f(w * 0.3)}" height="{_f(h * 0.10)}" rx="{_f(w * 0.05)}" '
        f'fill="{fill}"/>',
        f'<rect x="{_f(cx + w * 0.32)}" y="{_f(base_y - h * 0.80)}" '
        f'width="{_f(w * 0.3)}" height="{_f(arm_h)}" rx="{_f(w * 0.15)}" fill="{fill}"/>',
        f'<rect x="{_f(cx + w * 0.32)}" y="{_f(base_y - h * 0.80)}" '
        f'width="{_f(w * 0.3)}" height="{_f(h * 0.10)}" rx="{_f(w * 0.05)}" '
        f'fill="{fill}"/>',
    ])


def clay_mesa(x: float, y: float, w: float, h: float, steps: int, fill: str,
              d: float = 16.0) -> str:
    """Stepped adobe massing: a terrace stack, the signature Pueblo profile."""
    fill = col(fill)
    out = []
    sh = h / steps
    for i in range(steps):
        inset = i * w * 0.07
        out.append(clay_box(x + inset, y + (steps - i - 1) * sh,
                            w - inset * 2, sh + 2, d, tint(fill, 0.05 * (steps - i)),
                            r=6))
    return "".join(out)


def clay_sphere(cx: float, cy: float, r: float, fill: str) -> str:
    """A matte ball with one soft highlight, never a specular hotspot."""
    fill = col(fill)
    return "".join([
        f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}"/>',
        f'<circle cx="{_f(cx - r * 0.3)}" cy="{_f(cy - r * 0.34)}" '
        f'r="{_f(r * 0.42)}" fill="{tint(fill, 0.2)}" opacity="0.55"/>',
    ])


def clay_sun(cx: float, cy: float, r: float, gid: str = "sun") -> str:
    """A warm disc with a smooth falloff. Stepped rings produced a hard grey
    edge against the dusk sky, so the halo is a real radial gradient."""
    return (f'<radialGradient id="{gid}">'
            f'<stop offset="0.35" stop-color="{PALETTE["sun"]}" stop-opacity="0.34"/>'
            f'<stop offset="1" stop-color="{PALETTE["sun"]}" stop-opacity="0"/>'
            f'</radialGradient>'
            f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 2.6)}" fill="url(#{gid})"/>'
            f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{PALETTE["sun"]}"/>'
            f'<circle cx="{_f(cx - r * 0.22)}" cy="{_f(cy - r * 0.26)}" '
            f'r="{_f(r * 0.6)}" fill="{tint("sun", 0.3)}" opacity="0.5"/>')


def clay_cloud(cx: float, cy: float, s: float, fill: str) -> str:
    fill = col(fill)
    return "".join([
        f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(s * 0.42)}" fill="{fill}"/>',
        f'<circle cx="{_f(cx - s * 0.42)}" cy="{_f(cy + s * 0.12)}" '
        f'r="{_f(s * 0.32)}" fill="{fill}"/>',
        f'<circle cx="{_f(cx + s * 0.44)}" cy="{_f(cy + s * 0.1)}" '
        f'r="{_f(s * 0.3)}" fill="{fill}"/>',
        f'<rect x="{_f(cx - s * 0.72)}" y="{_f(cy + s * 0.08)}" '
        f'width="{_f(s * 1.48)}" height="{_f(s * 0.26)}" rx="{_f(s * 0.13)}" '
        f'fill="{fill}"/>',
    ])


# ---------------------------------------------------------------------------
# scene backdrop
# ---------------------------------------------------------------------------
def sky(w: int, h: int, sky_col: str, gid: str = "sky") -> str:
    """A two-stop dusk gradient, warm at the horizon."""
    sky_col = col(sky_col)
    top = tint(sky_col, -0.18)
    bottom = tint(PALETTE["peach"], 0.18)
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/>'
            f'<stop offset="0.62" stop-color="{sky_col}"/>'
            f'<stop offset="1" stop-color="{bottom}"/>'
            f'</linearGradient>'
            f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>')


def ground(w: int, h: int, y: float, fill: str) -> str:
    fill = col(fill)
    return (f'<rect x="0" y="{_f(y)}" width="{w}" height="{_f(h - y)}" '
            f'fill="{fill}"/>'
            f'<rect x="0" y="{_f(y)}" width="{w}" height="3" '
            f'fill="{tint(fill, 0.14)}"/>')


def label(x: float, y: float, text: str, fill: str, size: int = 17,
          anchor: str = "start", weight: str = "700", spacing: float = 0.6) -> str:
    """Blocky, sturdy type. Bold sans, wide tracking, no hairline weights."""
    fill = col(fill)
    return (f'<text x="{_f(x)}" y="{_f(y)}" font-family="Verdana,DejaVu Sans,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" '
            f'fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>')


def plaque(x: float, y: float, w: float, h: float, fill: str,
           r: float = 14) -> str:
    fill = col(fill)
    """A soft card panel that holds text, matching the clay language."""
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
            f'rx="{_f(r)}" fill="{fill}" opacity="0.94"/>')


def bar(x: float, y: float, w: float, h: float, fill: str, r: float = 0) -> str:
    fill = col(fill)
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
            f'rx="{_f(r)}" fill="{fill}"/>')


def dot(cx: float, cy: float, r: float, fill: str) -> str:
    fill = col(fill)
    return f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}"/>'


# ---------------------------------------------------------------------------
# motion
# ---------------------------------------------------------------------------
def set_motion(enabled: bool) -> None:
    import geometry
    geometry.set_motion(enabled)


def animate(attr: str, values: str, dur: float, begin: float = 0,
            extra: str = "") -> str:
    return (f'<animate attributeName="{attr}" values="{values}" dur="{_f(dur)}s" '
            f'begin="{_f(begin)}s" repeatCount="indefinite"{extra}/>')


def settle(x0: float, y0: float, x1: float, y1: float, dur: float,
           begin: float = 0.0) -> str:
    """The house motion: a block eases down into its place, then rests.

    The element must be fully opaque and in its final position at t=0. GitHub
    rasterises SVG in a README as a static image, so anything that starts at
    opacity 0 is simply invisible there; an earlier version did exactly that
    and every first-settling block disappeared from the rendered preview.
    Only the transform is animated, and it starts from a small offset.
    """
    lift = min(18.0, abs(y0 - y1) or 10.0)
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 {_f(lift)};0 0" dur="{_f(dur)}s" '
            f'begin="{_f(begin)}s" fill="freeze"/>')


def breathe(values: str, dur: float, begin: float = 0.0) -> str:
    """Opacity breathing that never dips far enough to vanish in a static frame."""
    return animate("opacity", values, dur, begin)


def lamp(cx: float, cy: float, r: float, gid: str) -> str:
    """A warm lamp glow. Flat rgba over dark navy read as an olive smudge, so
    the falloff is a real radial gradient."""
    return (f'<radialGradient id="{gid}">'
            f'<stop offset="0.2" stop-color="{PALETTE["sun"]}" stop-opacity="0.55"/>'
            f'<stop offset="1" stop-color="{PALETTE["sun"]}" stop-opacity="0"/>'
            f'</radialGradient>'
            f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="url(#{gid})"/>')


def drift(dx: float, dur: float, begin: float = 0.0) -> str:
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{_f(dx)} 0;0 0" dur="{_f(dur)}s" begin="{_f(begin)}s" '
            f'repeatCount="indefinite"/>')


# Technical category -> colourway. The mapping is semantic, so a security
# project and a data project never share a palette by accident, and it stays
# inside the New Mexico family so the portfolio reads as one system.
CATEGORY_CLAY = {
    "SECURITY": "clay_sand",
    "INFRASTRUCTURE": "mesa_terracotta",
    "DATA_BACKEND": "sand_turquoise",
    "DATA_STRUCTURE": "sand_turquoise",
    "CONCURRENCY": "ember_cactus",
    "AI_AGENT": "sunset_adobe",
    "SIMULATION": "rose_clay",
    "GRAPH_ALGORITHM": "rose_clay",
    "PIPELINE": "terra_rose",
    "PERFORMANCE": "sun_dusk",
    "SCHEDULER": "ember_cactus",
    "WEB_APPLICATION": "adobe_dusk",
    "DATA_VISUALIZATION": "peach_dusk",
    "SOFTWARE": "clay_sand",
    "SCAFFOLD": "sage_beige",
    "PORTFOLIO": "mesa_terracotta",
}
CATEGORY_CLAY["TERRACOTTA_ROSE"] = "terracotta_rose"


def clay_palette_for(category: str, seed: int) -> str:
    """Pick a New Mexico colourway for a technical category."""
    if category in CATEGORY_CLAY:
        return CATEGORY_CLAY[category]
    return CLAY_PALETTE_NAMES[seed % len(CLAY_PALETTE_NAMES)]
