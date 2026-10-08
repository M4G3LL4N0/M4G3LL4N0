"""Diorama primitives for the profile plates.

Implements DIORAMA_BRIEF.md: bright-day red-rock canyon scenery with one hero
device per plate, and rounded trail-sign boards for every string. Nothing here
invents beyond the ten reference images.

Determinism: placement jitter uses a seeded RNG (`rng_for`), never hash(),
time, or the global random module.
"""

from __future__ import annotations

import hashlib
import math
import random

# ---------------------------------------------------------------------------
# palette: the reference images, sampled
# ---------------------------------------------------------------------------
DAY_SKY = "#2e7bd6"
DAY_SKY_LOW = "#7db4ea"
GOLD_SKY = "#e8915a"
GOLD_SKY_LOW = "#f4c063"
NIGHT_SKY = "#0b1c3f"
NIGHT_LOW = "#1e3a6e"
ROCK = "#d65a3c"
ROCK_DARK = "#a8402a"
STRATA_A = "#e88a5c"
STRATA_B = "#c74f33"
SAND = "#e8c88a"
SAND_WET = "#c9a86f"
WATER = "#2aa3d8"
WATER_DEEP = "#1b7fb0"
FOAM = "#f4fafd"
LEAF = "#6faf4a"
LEAF_DARK = "#2e6b2a"
TRUNK = "#7a4a2e"
CACTUS = "#4f9138"
FLOWER_RED = "#e84a5f"
FLOWER_PINK = "#f2768c"
FLOWER_ORANGE = "#f5a623"
FLOWER_YELLOW = "#ffd23f"
SUN = "#ffd966"
CLOUD = "#f6e7ce"
BODY = "#f2e8d8"
SCREEN_BG = "#123"
SIGN_BG = "#f7ecd4"
SIGN_INK = "#4a3226"
SIGN_NUM = "#a8402a"
SIGN_NIGHT = "#3a2a1e"
POST = "#3a2a1e"


def _f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def rng_for(*parts: str) -> random.Random:
    seed = int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:12], 16)
    return random.Random(seed)


def _mix(a: str, b: str, t: float) -> str:
    def ch(h: str):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    ra, ga, ba = ch(a)
    rb, gb, bb = ch(b)
    return "#%02x%02x%02x" % (
        round(ra + (rb - ra) * t), round(ga + (gb - ga) * t),
        round(ba + (bb - ba) * t))


def shade(hex_color: str, t: float) -> str:
    """t>0 toward white, t<0 toward deep blue-black."""
    return _mix(hex_color, "#f6e7ce" if t >= 0 else "#0b1c3f", abs(t))


def lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a: str, b: str) -> float:
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------------------
# gradient defs, one id-family per plate
# ---------------------------------------------------------------------------
def defs_sky(gid: str, mode: str = "day") -> str:
    if mode == "night":
        top, mid, low = NIGHT_SKY, "#14294f", NIGHT_LOW
    elif mode == "gold":
        top, mid, low = "#3f6fc4", GOLD_SKY, GOLD_SKY_LOW
    else:
        top, mid, low = DAY_SKY, "#4f96dd", DAY_SKY_LOW
    return (
        f'<linearGradient id="sky{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/>'
        f'<stop offset="0.62" stop-color="{mid}"/>'
        f'<stop offset="1" stop-color="{low}"/>'
        f'</linearGradient>'
        f'<radialGradient id="halo{gid}">'
        f'<stop offset="0.3" stop-color="{SUN}" stop-opacity="0.5"/>'
        f'<stop offset="1" stop-color="{SUN}" stop-opacity="0"/>'
        f'</radialGradient>'
        f'<linearGradient id="rock{gid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{shade(ROCK, 0.14)}"/>'
        f'<stop offset="0.55" stop-color="{ROCK}"/>'
        f'<stop offset="1" stop-color="{shade(ROCK, -0.22)}"/>'
        f'</linearGradient>'
        f'<radialGradient id="sh{gid}">'
        f'<stop offset="0" stop-color="#0b1c3f" stop-opacity="0.30"/>'
        f'<stop offset="1" stop-color="#0b1c3f" stop-opacity="0"/>'
        f'</radialGradient>'
    )


# ---------------------------------------------------------------------------
# motion: closed seamless loops on coprime periods
# ---------------------------------------------------------------------------
LOOP = (7.0, 9.0, 11.0, 13.0, 17.0, 19.0, 23.0)


def loop_dur(i: int) -> float:
    return LOOP[i % len(LOOP)]


def loop_begin(i: int) -> float:
    return (i * 2.718) % loop_dur(i)


def _ease() -> str:
    return ('calcMode="spline" keyTimes="0;0.5;1" '
            'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"')


def bob(amp: float, i: int) -> str:
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 {_f(-amp)};0 0" dur="{_f(loop_dur(i))}s" '
            f'begin="{_f(loop_begin(i))}s" repeatCount="indefinite" {_ease()}/>')


def drift(dx: float, i: int, dy: float = 0.0) -> str:
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{_f(dx)} {_f(-dy)};0 0" dur="{_f(loop_dur(i))}s" '
            f'begin="{_f(loop_begin(i))}s" repeatCount="indefinite" {_ease()}/>')


def glow(lo: float, hi: float, i: int) -> str:
    return (f'<animate attributeName="opacity" values="{lo};{hi};{lo}" '
            f'dur="{_f(loop_dur(i))}s" begin="{_f(loop_begin(i))}s" '
            f'repeatCount="indefinite" {_ease()}/>')


def spin(deg: float, i: int, cx: float, cy: float) -> str:
    return (f'<animateTransform attributeName="transform" type="rotate" '
            f'values="0 {_f(cx)} {_f(cy)};{_f(deg)} {_f(cx)} {_f(cy)};'
            f'0 {_f(cx)} {_f(cy)}" dur="{_f(loop_dur(i))}s" '
            f'begin="{_f(loop_begin(i))}s" repeatCount="indefinite" {_ease()}/>')


def shimmer(w: float, i: int) -> str:
    """A highlight bar travelling along a river, then returning."""
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{_f(w)} 0;0 0" dur="{_f(loop_dur(i))}s" '
            f'begin="{_f(loop_begin(i))}s" repeatCount="indefinite" {_ease()}/>')


# ---------------------------------------------------------------------------
# sky
# ---------------------------------------------------------------------------
def sky_block(w: int, h: int, gid: str, mode: str = "day") -> str:
    return f'<rect width="{w}" height="{h}" fill="url(#sky{gid})"/>'


def sun_disc(cx: float, cy: float, r: float, gid: str, i: int = 0) -> str:
    return (f'<g><circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 2.2)}" '
            f'fill="url(#halo{gid})"/>'
            f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{SUN}">'
            f'{glow(0.85, 1.0, i)}</circle></g>')


def moon_disc(cx: float, cy: float, r: float) -> str:
    return (f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 1.9)}" '
            f'fill="{CLOUD}" opacity="0.16"/>'
            f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{CLOUD}"/>'
            f'<circle cx="{_f(cx - r * 0.3)}" cy="{_f(cy - r * 0.2)}" '
            f'r="{_f(r * 0.22)}" fill="{shade(CLOUD, -0.08)}" opacity="0.55"/>')


def stars(w: int, h: int) -> str:
    out = []
    for i in range(60):
        x = (i * 173) % w
        y = (i * 97) % int(h * 0.55)
        r = 1.0 + ((i * 7) % 5) * 0.3
        out.append(f'<circle cx="{x}" cy="{y}" r="{_f(r)}" fill="{CLOUD}" '
                   f'opacity="{0.25 + ((i * 13) % 6) * 0.1:.2f}"/>')
    return "".join(out)


def milky_way(w: int) -> str:
    pts = " ".join(f"{_f(w * 0.52 + (i - 6) * 26)},{_f(40 + abs(i - 6) * 9)}"
                   for i in range(13))
    return (f'<polyline points="{pts}" fill="none" stroke="{CLOUD}" '
            f'stroke-width="26" stroke-linecap="round" opacity="0.14"/>'
            f'<polyline points="{pts}" fill="none" stroke="{CLOUD}" '
            f'stroke-width="10" stroke-linecap="round" opacity="0.12"/>')


def block_cloud(cx: float, cy: float, s: float, i: int = 0) -> str:
    body = "".join([
        f'<rect x="{_f(cx - s * 0.75)}" y="{_f(cy - s * 0.12)}" '
        f'width="{_f(s * 1.5)}" height="{_f(s * 0.42)}" rx="{_f(s * 0.2)}" '
        f'fill="{CLOUD}"/>',
        f'<rect x="{_f(cx - s * 0.42)}" y="{_f(cy - s * 0.48)}" '
        f'width="{_f(s * 0.84)}" height="{_f(s * 0.5)}" rx="{_f(s * 0.2)}" '
        f'fill="{CLOUD}"/>',
        f'<rect x="{_f(cx + s * 0.10)}" y="{_f(cy - s * 0.36)}" '
        f'width="{_f(s * 0.52)}" height="{_f(s * 0.38)}" rx="{_f(s * 0.18)}" '
        f'fill="{CLOUD}"/>',
    ])
    return f"<g>{body}{drift(s * 0.22, i)}</g>"


# ---------------------------------------------------------------------------
# red rock with strata
# ---------------------------------------------------------------------------
def strata_cliff(x: float, y: float, w: float, h: float, gid: str,
                 bands: int = 6, seed: int = 0, d: float = 0.0) -> str:
    """A sandstone face: alternating lighter/darker courses with a chamfered
    lit edge. The strata are what read as geology rather than architecture."""
    out = [f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
           f'fill="url(#rock{gid})"/>']
    bh = h / max(bands, 1)
    r = rng_for("strata", str(seed))
    for b in range(bands):
        tone = STRATA_A if (b + seed) % 2 == 0 else STRATA_B
        y0 = y + b * bh
        jit = r.uniform(-bh * 0.08, bh * 0.08)
        out.append(f'<rect x="{_f(x)}" y="{_f(y0 + jit)}" width="{_f(w)}" '
                   f'height="{_f(bh * 0.46)}" fill="{tone}"/>')
        out.append(f'<rect x="{_f(x)}" y="{_f(y0 + jit + bh * 0.46)}" '
                   f'width="{_f(w)}" height="2" fill="{shade(ROCK_DARK, -0.1)}" '
                   f'opacity="0.55"/>')
    out.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="5" '
               f'fill="{STRATA_A}"/>')
    if d:
        out.append(f'<path d="M{_f(x + w)},{_f(y)} L{_f(x + w + d)},{_f(y - d)} '
                   f'L{_f(x + w + d)},{_f(y + h - d)} L{_f(x + w)},{_f(y + h)} Z" '
                   f'fill="{shade(ROCK, -0.26)}"/>')
    return "".join(out)


def mesa(x: float, y: float, w: float, h: float, steps: int, gid: str,
         seed: int = 0) -> str:
    """A stepped butte: each terrace narrower, with a sand cap."""
    out = []
    sh = h / max(steps, 1)
    for i in range(steps):
        inset = i * w * 0.10
        bw, bh = w - inset * 2, sh + 2
        bx, by = x + inset, y + (steps - i - 1) * sh
        out.append(f'<rect x="{_f(bx)}" y="{_f(by)}" width="{_f(bw)}" '
                   f'height="{_f(bh)}" fill="url(#rock{gid})"/>')
        out.append(f'<rect x="{_f(bx)}" y="{_f(by)}" width="{_f(bw)}" '
                   f'height="{_f(bh * 0.3)}" fill="{STRATA_A}"/>')
    tx, tw = x + (steps - 1) * w * 0.10, w - (steps - 1) * w * 0.10 * 2
    out.append(f'<rect x="{_f(tx)}" y="{_f(y - 6)}" width="{_f(tw)}" '
               f'height="8" rx="3" fill="{SAND}"/>')
    return "".join(out)


def shadow_ellipse(cx: float, cy: float, rx: float, ry: float,
                   gid: str) -> str:
    return (f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" ry="{_f(ry)}" '
            f'fill="url(#sh{gid})"/>')


# ---------------------------------------------------------------------------
# water
# ---------------------------------------------------------------------------
def river(x: float, y: float, w: float, h: float, gid: str, i: int = 0) -> str:
    out = [f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
           f'fill="{WATER}"/>',
           f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h * 0.3)}" '
           f'fill="{shade(WATER, 0.22)}"/>']
    for k, frac in enumerate((0.24, 0.55, 0.80)):
        bw = w * (0.30 - k * 0.05)
        y0 = y + h * frac
        out.append(f'<g><rect x="{_f(x + w * 0.08)}" y="{_f(y0)}" '
                   f'width="{_f(bw)}" height="{_f(max(h * 0.09, 3))}" rx="3" '
                   f'fill="{FOAM}" opacity="0.75"/>'
                   f'{shimmer(w * 0.25, i + k)}</g>')
    return "".join(out)


def waterfall(x: float, y: float, w: float, h: float, gid: str) -> str:
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'fill="{shade(WATER, 0.12)}"/>',
        f'<rect x="{_f(x + w * 0.22)}" y="{_f(y)}" width="{_f(w * 0.30)}" '
        f'height="{_f(h)}" fill="{FOAM}" opacity="0.9"/>',
        f'<rect x="{_f(x + w * 0.58)}" y="{_f(y)}" width="{_f(w * 0.16)}" '
        f'height="{_f(h)}" fill="{FOAM}" opacity="0.7"/>',
        f'<ellipse cx="{_f(x + w / 2)}" cy="{_f(y + h)}" rx="{_f(w * 0.75)}" '
        f'ry="{_f(max(h * 0.10, 6))}" fill="{FOAM}" opacity="0.85"/>',
    ])


def pool(x: float, y: float, w: float, h: float) -> str:
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(h * 0.5)}" fill="{WATER}"/>',
        f'<rect x="{_f(x + w * 0.18)}" y="{_f(y + h * 0.3)}" '
        f'width="{_f(w * 0.4)}" height="{_f(h * 0.12)}" rx="3" '
        f'fill="{FOAM}" opacity="0.6"/>',
    ])


# ---------------------------------------------------------------------------
# flora
# ---------------------------------------------------------------------------
def conifer(cx: float, base_y: float, w: float, h: float, i: int = 0,
            tiers: int = 6) -> str:
    """Lush two-tone conifer. More, narrower tiers than the sparse desert tree."""
    out = [f'<rect x="{_f(cx - w * 0.07)}" y="{_f(base_y - h * 0.14)}" '
           f'width="{_f(w * 0.14)}" height="{_f(h * 0.14)}" fill="{TRUNK}"/>']
    for t in range(tiers):
        f = t / max(tiers - 1, 1)
        ty = base_y - h * 0.14 - t * (h * 0.82) / tiers
        tw = w * (1.0 - 0.13 * t)
        th = (h * 0.82) / tiers * 2.05
        out.append(f'<g><path d="M{_f(cx)},{_f(ty - th)} '
                   f'L{_f(cx + tw / 2)},{_f(ty)} L{_f(cx - tw / 2)},{_f(ty)} Z" '
                   f'fill="{LEAF}"/>'
                   f'<path d="M{_f(cx)},{_f(ty - th)} '
                   f'L{_f(cx + tw / 2)},{_f(ty)} L{_f(cx + tw * 0.08)},{_f(ty)} '
                   f'L{_f(cx + tw * 0.08)},{_f(ty - th * 0.4)} Z" '
                   f'fill="{LEAF_DARK}"/>'
                   f'{bob(1.4 + t * 0.3, i + t)}</g>')
    return "".join(out)


def cactus(cx: float, base_y: float, w: float, h: float, i: int = 0) -> str:
    bw = w * 0.34
    body = "".join([
        f'<rect x="{_f(cx - bw / 2)}" y="{_f(base_y - h)}" width="{_f(bw)}" '
        f'height="{_f(h)}" rx="{_f(bw / 2)}" fill="{CACTUS}"/>',
        f'<rect x="{_f(cx - bw * 0.30)}" y="{_f(base_y - h * 0.94)}" '
        f'width="{_f(bw * 0.32)}" height="{_f(h * 0.84)}" rx="{_f(bw * 0.16)}" '
        f'fill="{shade(CACTUS, 0.30)}"/>',
        f'<rect x="{_f(cx - w * 0.60)}" y="{_f(base_y - h * 0.62)}" '
        f'width="{_f(w * 0.28)}" height="{_f(h * 0.32)}" rx="{_f(w * 0.14)}" '
        f'fill="{CACTUS}"/>',
        f'<rect x="{_f(cx + w * 0.32)}" y="{_f(base_y - h * 0.76)}" '
        f'width="{_f(w * 0.28)}" height="{_f(h * 0.32)}" rx="{_f(w * 0.14)}" '
        f'fill="{CACTUS}"/>',
    ])
    return f"<g>{body}{bob(1.2, i)}</g>"


def bloom(cx: float, cy: float, r: float, color: str) -> str:
    out = []
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        out.append(f'<circle cx="{_f(cx + math.cos(a) * r)}" '
                   f'cy="{_f(cy + math.sin(a) * r)}" r="{_f(r * 0.72)}" '
                   f'fill="{color}"/>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.5)}" '
               f'fill="{FLOWER_YELLOW}"/>')
    return "".join(out)


def flower_patch(x: float, y: float, w: float, n: int, seed: int) -> str:
    r = rng_for("blooms", str(seed))
    colors = (FLOWER_RED, FLOWER_PINK, FLOWER_ORANGE, FLOWER_RED,
              FLOWER_PINK, FLOWER_YELLOW)
    out = []
    for k in range(n):
        bx = x + r.uniform(0, w)
        by = y + r.uniform(-8, 10)
        out.append(bloom(bx, by, 4.6 + r.uniform(0, 1.8), colors[k % len(colors)]))
        out.append(f'<rect x="{_f(bx - 1)}" y="{_f(by)}" width="2" '
                   f'height="{_f(9 + r.uniform(0, 5))}" fill="{LEAF_DARK}"/>')
    return "".join(out)


def rock_block(x: float, y: float, s: float, seed: int = 0) -> str:
    r = rng_for("rock", str(seed), str(int(x)), str(int(y)))
    t = r.uniform(-0.1, 0.12)
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(s)}" height="{_f(s * 0.72)}" '
            f'rx="{_f(s * 0.22)}" fill="{shade(SAND, t)}"/>')


def sand_floor(w: int, horizon: float, h: int, seed: int = 0) -> str:
    r = rng_for("floor", str(seed))
    out = [f'<rect x="0" y="{_f(horizon)}" width="{w}" '
           f'height="{_f(h - horizon)}" fill="{SAND}"/>',
           f'<rect x="0" y="{_f(horizon)}" width="{w}" height="3" '
           f'fill="{shade(SAND, 0.16)}"/>']
    for _ in range(14):
        out.append(rock_block(r.uniform(0, w - 26), horizon + r.uniform(6, h - horizon - 14),
                              r.uniform(9, 24), seed))
    return "".join(out)


# ---------------------------------------------------------------------------
# devices (heroes)
# ---------------------------------------------------------------------------
def face_plate(x: float, y: float, w: float, h: float, r: float = 6.0) -> str:
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
            f'rx="{_f(r)}" fill="{BODY}"/>')


def vent_row(x: float, y: float, n: int, pitch: float, w: float, h: float,
             color: str) -> str:
    return "".join(
        f'<rect x="{_f(x + i * pitch)}" y="{_f(y)}" width="{_f(w)}" '
        f'height="{_f(h)}" rx="1.5" fill="{color}"/>' for i in range(n))


def tiny_mesa_lake(x: float, y: float, w: float, h: float) -> str:
    """The laptop wallpaper: a mesa over a lake at sunset, miniaturised."""
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'fill="#e8915a"/>',
        f'<circle cx="{_f(x + w * 0.62)}" cy="{_f(y + h * 0.34)}" '
        f'r="{_f(h * 0.16)}" fill="{SUN}"/>',
        f'<path d="M{_f(x + w * 0.18)},{_f(y + h * 0.62)} '
        f'L{_f(x + w * 0.30)},{_f(y + h * 0.34)} '
        f'L{_f(x + w * 0.56)},{_f(y + h * 0.34)} '
        f'L{_f(x + w * 0.68)},{_f(y + h * 0.62)} Z" fill="{ROCK}"/>',
        f'<rect x="{_f(x)}" y="{_f(y + h * 0.62)}" width="{_f(w)}" '
        f'height="{_f(h * 0.38)}" fill="{WATER_DEEP}"/>',
        f'<rect x="{_f(x + w * 0.3)}" y="{_f(y + h * 0.72)}" '
        f'width="{_f(w * 0.4)}" height="2" fill="{FOAM}" opacity="0.7"/>',
    ])


def tiny_mesa(x: float, y: float, w: float, h: float) -> str:
    """The phone wallpaper: a lone mesa at golden hour."""
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'fill="#f4c063"/>',
        f'<circle cx="{_f(x + w * 0.5)}" cy="{_f(y + h * 0.42)}" '
        f'r="{_f(h * 0.18)}" fill="{SUN}"/>',
        f'<path d="M{_f(x + w * 0.28)},{_f(y + h * 0.78)} '
        f'L{_f(x + w * 0.38)},{_f(y + h * 0.48)} '
        f'L{_f(x + w * 0.62)},{_f(y + h * 0.48)} '
        f'L{_f(x + w * 0.72)},{_f(y + h * 0.78)} Z" fill="{ROCK}"/>',
        f'<rect x="{_f(x)}" y="{_f(y + h * 0.78)}" width="{_f(w)}" '
        f'height="{_f(h * 0.22)}" fill="{WATER_DEEP}"/>',
    ])


def tiny_canyon(x: float, y: float, w: float, h: float) -> str:
    """The desktop wallpaper: canyon walls over a river."""
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'fill="{DAY_SKY_LOW}"/>',
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w * 0.3)}" '
        f'height="{_f(h * 0.7)}" fill="{ROCK}"/>',
        f'<rect x="{_f(x + w * 0.7)}" y="{_f(y)}" width="{_f(w * 0.3)}" '
        f'height="{_f(h * 0.7)}" fill="{shade(ROCK, -0.12)}"/>',
        f'<rect x="{_f(x)}" y="{_f(y + h * 0.7)}" width="{_f(w)}" '
        f'height="{_f(h * 0.3)}" fill="{WATER}"/>',
    ])


def laptop(x: float, base_y: float, w: float, i: int = 0) -> str:
    h = w * 0.66
    sy = base_y - h
    sw, sh = w * 0.86, h * 0.72
    sx = x + w * 0.07
    body = "".join([
        f'<rect x="{_f(x)}" y="{_f(sy)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(w * 0.05)}" fill="{BODY}"/>',
        f'<rect x="{_f(sx)}" y="{_f(sy + h * 0.07)}" width="{_f(sw)}" '
        f'height="{_f(sh)}" fill="{SCREEN_BG}"/>',
        tiny_mesa_lake(sx + 3, sy + h * 0.07 + 3, sw - 6, sh - 6),
        f'<rect x="{_f(x - w * 0.06)}" y="{_f(base_y)}" width="{_f(w * 1.12)}" '
        f'height="{_f(h * 0.11)}" rx="{_f(h * 0.05)}" fill="{shade(BODY, -0.10)}"/>',
        "".join(f'<rect x="{_f(x + w * (0.08 + c * 0.075))}" y="{_f(base_y + h * 0.02)}" '
                f'width="{_f(w * 0.06)}" height="{_f(h * 0.05)}" rx="1" '
                f'fill="{shade(BODY, -0.28)}"/>' for c in range(11)),
    ])
    return f"<g>{body}{bob(3.0, i)}</g>"


def dish_station(cx: float, base_y: float, s: float, i: int = 0) -> str:
    """Satellite dish on a mesa platform: the photo-2 hero."""
    plat_w, plat_h = s * 1.5, s * 0.24
    return "".join([
        f'<rect x="{_f(cx - plat_w / 2)}" y="{_f(base_y - plat_h)}" '
        f'width="{_f(plat_w)}" height="{_f(plat_h)}" rx="4" fill="{STRATA_A}"/>',
        f'<rect x="{_f(cx - s * 0.10)}" y="{_f(base_y - plat_h - s * 0.42)}" '
        f'width="{_f(s * 0.20)}" height="{_f(s * 0.42)}" fill="{BODY}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(base_y - plat_h - s * 0.62)}" '
        f'r="{_f(s * 0.62)}" fill="{BODY}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(base_y - plat_h - s * 0.62)}" '
        f'r="{_f(s * 0.44)}" fill="{shade(BODY, -0.12)}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(base_y - plat_h - s * 0.62)}" '
        f'r="{_f(s * 0.12)}" fill="{SIGN_NUM}"/>',
        f'<rect x="{_f(cx - s * 0.52)}" y="{_f(base_y - plat_h - s * 1.12)}" '
        f'width="{_f(s * 0.16)}" height="{_f(s * 0.5)}" rx="4" '
        f'fill="{shade(BODY, -0.20)}"/>',
    ]) + (f'<g>{bob(2.0, i)}</g>' if False else "")


def server_tower(x: float, base_y: float, w: float, units: int,
                 i: int = 0) -> str:
    """Floor-standing rack with square vents and indicator lamps per unit."""
    uh = 34.0
    h = units * uh + 14
    y = base_y - h
    out = [f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
           f'rx="6" fill="{BODY}"/>',
           f'<rect x="{_f(x + w)}" y="{_f(y + 4)}" width="7" height="{_f(h - 8)}" '
           f'fill="{shade(BODY, -0.22)}"/>',
           f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="7" '
           f'fill="{shade(BODY, 0.10)}"/>']
    for u in range(units):
        uy = y + 10 + u * uh
        out.append(f'<rect x="{_f(x + 8)}" y="{_f(uy)}" width="{_f(w - 16)}" '
                   f'height="{_f(uh - 8)}" rx="3" fill="{shade(BODY, -0.06 if u % 2 else -0.14)}"/>')
        out.append(vent_row(x + 14, uy + 8, 4, 12, 7, 9, shade(BODY, -0.34)))
        out.append(f'<circle cx="{_f(x + w - 14)}" cy="{_f(uy + (uh - 8) / 2)}" '
                   f'r="3.4" fill="{SUN if u % 3 != 2 else CACTUS}">'
                   f'{glow(0.7, 1.0, i + u)}</circle>')
    return f"<g>{''.join(out)}{bob(1.6, i)}</g>"


def solar_panel(cx: float, base_y: float, w: float, i: int = 0) -> str:
    """Tilted panel on a mount post. Drawn flat in the panel's own tilted
    frame so no nested-rotation syntax is needed."""
    h = w * 0.52
    y = base_y - h - 30
    tilt = 0.24
    dx = h * tilt
    out = [
        f'<rect x="{_f(cx - 7)}" y="{_f(base_y - 30)}" width="14" '
        f'height="30" fill="{shade(BODY, -0.24)}"/>',
        f'<rect x="{_f(cx - w / 2 - 14)}" y="{_f(base_y - 8)}" '
        f'width="{_f(w + 28)}" height="8" rx="3" fill="{shade(BODY, -0.18)}"/>',
        # panel slab as a tilted quad
        f'<path d="M{_f(cx - w / 2)},{_f(y + h)} '
        f'L{_f(cx + w / 2)},{_f(y + h)} '
        f'L{_f(cx + w / 2 + dx)},{_f(y)} '
        f'L{_f(cx - w / 2 + dx)},{_f(y)} Z" fill="{shade(BODY, -0.06)}"/>',
        f'<path d="M{_f(cx - w / 2)},{_f(y + h)} '
        f'L{_f(cx + w / 2)},{_f(y + h)} '
        f'L{_f(cx + w / 2)},{_f(y + h - 4)} '
        f'L{_f(cx - w / 2)},{_f(y + h - 4)} Z" fill="{shade(BODY, -0.24)}"/>',
    ]
    # cell grid: rows follow the same tilt by construction
    for r in range(3):
        ry = y + 8 + r * (h - 16) / 3
        ox = dx * (1 - (ry - y) / h)
        for c in range(5):
            cw = (w - 16) / 5
            out.append(
                f'<path d="M{_f(cx - w / 2 + 8 + c * cw)},{_f(ry + (h - 16) / 3 - 3)} '
                f'L{_f(cx - w / 2 + 8 + (c + 1) * cw - 3)},{_f(ry + (h - 16) / 3 - 3)} '
                f'L{_f(cx - w / 2 + 8 + (c + 1) * cw - 3 + dx * 0.12)},{_f(ry + 3)} '
                f'L{_f(cx - w / 2 + 8 + c * cw + dx * 0.12)},{_f(ry + 3)} Z" '
                f'fill="#1d4e89"/>')
    return f"<g>{''.join(out)}{bob(1.8, i)}</g>"


def rocket_pad(cx: float, base_y: float, s: float, i: int = 0) -> str:
    """Rocket on a gantry with engines lit and lit pad buildings."""
    rh = s * 2.5
    ry = base_y - rh
    body = "".join([
        f'<rect x="{_f(cx - s * 1.3)}" y="{_f(base_y - 22)}" '
        f'width="{_f(s * 2.6)}" height="22" fill="{STRATA_A}"/>',
        f'<rect x="{_f(cx + s * 0.55)}" y="{_f(base_y - s * 2.2)}" '
        f'width="{_f(s * 0.4)}" height="{_f(s * 2.2)}" fill="{shade(ROCK, -0.15)}"/>',
        "".join(f'<rect x="{_f(cx + s * 0.55)}" y="{_f(base_y - s * 2.2 + k * s * 0.5)}" '
                f'width="{_f(s * 0.4)}" height="4" fill="{shade(ROCK, 0.2)}"/>'
                for k in range(4)),
        f'<rect x="{_f(cx - s * 0.24)}" y="{_f(ry)}" width="{_f(s * 0.48)}" '
        f'height="{_f(rh)}" rx="{_f(s * 0.2)}" fill="{BODY}"/>',
        f'<path d="M{_f(cx - s * 0.24)},{_f(ry + s * 0.4)} '
        f'L{_f(cx)},{_f(ry - s * 0.42)} L{_f(cx + s * 0.24)},{_f(ry + s * 0.4)} Z" '
        f'fill="{BODY}"/>',
        f'<rect x="{_f(cx - s * 0.24)}" y="{_f(ry + s * 0.5)}" '
        f'width="{_f(s * 0.48)}" height="{_f(s * 0.3)}" fill="{SIGN_NUM}"/>',
        f'<path d="M{_f(cx - s * 0.24)},{_f(base_y)} L{_f(cx - s * 0.42)},'
        f'{_f(base_y - s * 0.5)} L{_f(cx - s * 0.10)},{_f(base_y - s * 0.3)} Z" '
        f'fill="{SIGN_NUM}"/>',
        f'<path d="M{_f(cx + s * 0.24)},{_f(base_y)} L{_f(cx + s * 0.42)},'
        f'{_f(base_y - s * 0.5)} L{_f(cx + s * 0.10)},{_f(base_y - s * 0.3)} Z" '
        f'fill="{SIGN_NUM}"/>',
        f'<g><path d="M{_f(cx - s * 0.16)},{_f(base_y)} L{_f(cx)},'
        f'{_f(base_y + s * 0.85)} L{_f(cx + s * 0.16)},{_f(base_y)} Z" '
        f'fill="{SUN}"/>'
        f'<circle cx="{_f(cx)}" cy="{_f(base_y + s * 0.5)}" r="{_f(s * 0.55)}" '
        f'fill="{SUN}" opacity="0.35">'
        f'{glow(0.55, 0.95, i)}</circle></g>',
        vent_row(cx - s * 1.1, base_y - 16, 3, 14, 8, 8, SUN),
    ])
    return f"<g>{body}{bob(1.2, i)}</g>"


def phone(x: float, y: float, w: float, time_text: str = "9:41") -> str:
    """Smartphone standing in the sand, screen showing a mesa at golden hour."""
    h = w * 2.02
    sx, sy, sw, sh = x + w * 0.08, y + h * 0.055, w * 0.84, h * 0.87
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(w * 0.14)}" fill="{BODY}"/>',
        f'<rect x="{_f(sx)}" y="{_f(sy)}" width="{_f(sw)}" height="{_f(sh)}" '
        f'rx="{_f(w * 0.08)}" fill="{SCREEN_BG}"/>',
        tiny_mesa(sx + 2, sy + 2, sw - 4, sh - 4),
        f'<text x="{_f(x + w / 2)}" y="{_f(sy + sh * 0.34)}" '
        f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="{_f(w * 0.24)}" '
        f'font-weight="700" fill="{CLOUD}" text-anchor="middle">'
        f'{esc(time_text)}</text>',
    ])


def drone(cx: float, cy: float, s: float, i: int = 0) -> str:
    """Quadcopter with spinning rotor discs and a camera eye."""
    arms = "".join(
        f'<rect x="{_f(cx + dx * s)}" y="{_f(cy - s * 0.05)}" '
        f'width="{_f(s * 0.5)}" height="{_f(s * 0.1)}" rx="{_f(s * 0.05)}" '
        f'fill="{BODY}"/>' for dx in (-1.05, 0.55))
    rotors = "".join(
        f'<g><ellipse cx="{_f(cx + dx * s)}" cy="{_f(cy - s * 0.12)}" '
        f'rx="{_f(s * 0.42)}" ry="{_f(s * 0.09)}" fill="{CLOUD}" '
        f'opacity="0.75">{spin_body(dx, cx, cy, s, i)}</ellipse></g>'
        for dx in (-0.8, 0.8))
    body = "".join([
        arms,
        f'<rect x="{_f(cx - s * 0.34)}" y="{_f(cy - s * 0.16)}" '
        f'width="{_f(s * 0.68)}" height="{_f(s * 0.34)}" rx="{_f(s * 0.12)}" '
        f'fill="{shade(BODY, -0.08)}"/>',
        f'<rect x="{_f(cx - s * 0.22)}" y="{_f(cy - s * 0.16)}" '
        f'width="{_f(s * 0.44)}" height="{_f(s * 0.16)}" rx="{_f(s * 0.06)}" '
        f'fill="{SUN}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(cy + s * 0.28)}" r="{_f(s * 0.13)}" '
        f'fill="{P_DUSK}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(cy + s * 0.28)}" r="{_f(s * 0.06)}" '
        f'fill="{shade(SUN, -0.1)}"/>',
        rotors,
    ])
    return f"<g>{body}{bob(5.0, i)}</g>"


def spin_body(dx: float, cx: float, cy: float, s: float, i: int) -> str:
    return (f'<animate attributeName="opacity" values="0.55;0.9;0.55" '
            f'dur="{_f(loop_dur(i + 3))}s" begin="{_f(loop_begin(i + 3))}s" '
            f'repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;0.5;1" '
            f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>')


P_DUSK = "#0b1c3f"


def observatory(cx: float, base_y: float, w: float, i: int = 0) -> str:
    """Round dome on a drum, slit open with a glowing telescope eye."""
    dw, dh = w, w * 0.72
    dy = base_y - dh
    drum_h = dh * 0.42
    return "".join([
        f'<rect x="{_f(cx - dw / 2)}" y="{_f(dy + dh - drum_h)}" '
        f'width="{_f(dw)}" height="{_f(drum_h)}" fill="{shade(ROCK, -0.06)}"/>',
        "".join(f'<rect x="{_f(cx - dw / 2 + 12 + k * (dw - 24) / 5)}" '
                f'y="{_f(dy + dh - drum_h + 10)}" width="10" height="16" '
                f'fill="{SUN}">{glow(0.7, 1.0, i + k)}</rect>' for k in range(5)),
        f'<path d="M{_f(cx - dw / 2)},{_f(dy + dh - drum_h)} '
        f'A{_f(dw / 2)},{_f(dw / 2)} 0 0 1 {_f(cx + dw / 2)},{_f(dy + dh - drum_h)} Z" '
        f'fill="{BODY}"/>',
        f'<path d="M{_f(cx - dw * 0.14)},{_f(dy + dh - drum_h)} '
        f'A{_f(dw * 0.14)},{_f(dw * 0.42)} 0 0 1 {_f(cx + dw * 0.14)},{_f(dy + dh - drum_h)} Z" '
        f'fill="{P_DUSK}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(dy + dh - drum_h - dw * 0.10)}" '
        f'r="7" fill="{SUN}">{glow(0.65, 1.0, i)}</circle>',
    ])


def desktop(x: float, base_y: float, w: float, i: int = 0) -> str:
    """Monitor with a canyon wallpaper, chunky keyboard, rounded mouse."""
    mh = w * 0.62
    my = base_y - mh - 16
    mx, mw, mh_s = x, w, mh * 0.80
    sx, sy = mx + w * 0.06, my + mh * 0.06
    sw, sh = w * 0.88, mh_s - mh * 0.12
    body = "".join([
        f'<rect x="{_f(mx + w * 0.36)}" y="{_f(my + mh)}" width="{_f(w * 0.28)}" '
        f'height="14" fill="{shade(BODY, -0.18)}"/>',
        f'<rect x="{_f(mx)}" y="{_f(my)}" width="{_f(w)}" height="{_f(mh)}" '
        f'rx="{_f(w * 0.05)}" fill="{BODY}"/>',
        f'<rect x="{_f(sx)}" y="{_f(sy)}" width="{_f(sw)}" height="{_f(sh)}" '
        f'fill="{SCREEN_BG}"/>',
        tiny_canyon(sx + 2, sy + 2, sw - 4, sh - 4),
        f'<rect x="{_f(x - w * 0.16)}" y="{_f(base_y - 12)}" '
        f'width="{_f(w * 1.32)}" height="12" rx="4" '
        f'fill="{shade(BODY, -0.12)}"/>',
        "".join(f'<rect x="{_f(x - w * 0.10 + c * w * 0.085)}" '
                f'y="{_f(base_y - 8)}" width="{_f(w * 0.068)}" height="6" '
                f'rx="1.5" fill="{shade(BODY, -0.30)}"/>' for c in range(12)),
        f'<ellipse cx="{_f(x + w * 1.32)}" cy="{_f(base_y - 5)}" rx="11" '
        f'ry="9" fill="{shade(BODY, -0.20)}"/>',
    ])
    return f"<g>{body}{bob(2.2, i)}</g>"


def orbiter(cx: float, cy: float, s: float, i: int = 0) -> str:
    """Blocky satellite with twin solar wings."""
    body = "".join([
        f'<rect x="{_f(cx - s * 1.30)}" y="{_f(cy - s * 0.22)}" '
        f'width="{_f(s * 0.84)}" height="{_f(s * 0.44)}" rx="2" '
        f'fill="#1d4e89"/>',
        f'<rect x="{_f(cx + s * 0.46)}" y="{_f(cy - s * 0.22)}" '
        f'width="{_f(s * 0.84)}" height="{_f(s * 0.44)}" rx="2" '
        f'fill="#1d4e89"/>',
        f'<rect x="{_f(cx - s * 0.46)}" y="{_f(cy - s * 0.34)}" '
        f'width="{_f(s * 0.92)}" height="{_f(s * 0.68)}" rx="{_f(s * 0.12)}" '
        f'fill="{BODY}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(s * 0.15)}" '
        f'fill="{P_DUSK}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(s * 0.07)}" '
        f'fill="{shade(SUN, -0.1)}">'
        f'{glow(0.6, 1.0, i)}</circle>',
    ])
    return f"<g>{body}{drift(s * 0.10, i)}</g>"


def ground_dish(cx: float, base_y: float, s: float, housing: bool = True) -> str:
    """White ground dish on a lit blockhouse, photo-10 style."""
    out = []
    if housing:
        out.append(f'<rect x="{_f(cx - s * 0.55)}" y="{_f(base_y - s * 0.9)}" '
                   f'width="{_f(s * 1.1)}" height="{_f(s * 0.9)}" '
                   f'fill="{BODY}"/>')
        out.append(f'<rect x="{_f(cx - s * 0.35)}" y="{_f(base_y - s * 0.72)}" '
                   f'width="{_f(s * 0.28)}" height="{_f(s * 0.5)}" '
                   f'fill="{SUN}">{glow(0.7, 1.0, 2)}</rect>')
        out.append(f'<rect x="{_f(cx + s * 0.05)}" y="{_f(base_y - s * 0.72)}" '
                   f'width="{_f(s * 0.28)}" height="{_f(s * 0.5)}" '
                   f'fill="{SUN}" opacity="0.75"/>')
    out.append(f'<rect x="{_f(cx - s * 0.09)}" y="{_f(base_y - s * 1.7)}" '
               f'width="{_f(s * 0.18)}" height="{_f(s * 0.9)}" '
               f'fill="{shade(BODY, -0.18)}"/>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(base_y - s * 1.75)}" '
               f'r="{_f(s * 0.52)}" fill="{BODY}"/>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(base_y - s * 1.75)}" '
               f'r="{_f(s * 0.36)}" fill="{shade(BODY, -0.14)}"/>')
    return "".join(out)


# ---------------------------------------------------------------------------
# trail signage -- every string in a plate lives on one of these
# ---------------------------------------------------------------------------
def posts(x: float, ground_y: float, top_y: float, left_x: float,
          right_x: float) -> str:
    return "".join([
        f'<rect x="{_f(left_x)}" y="{_f(top_y)}" width="10" '
        f'height="{_f(ground_y - top_y)}" fill="{POST}"/>',
        f'<rect x="{_f(right_x)}" y="{_f(top_y)}" width="10" '
        f'height="{_f(ground_y - top_y)}" fill="{POST}"/>',
    ])


def sign_board(x: float, y: float, w: float, h: float, night: bool = False,
               r: float = 10.0) -> str:
    bg = SIGN_NIGHT if night else SIGN_BG
    lip = shade(bg, -0.30 if night else -0.16)
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
            f'rx="{_f(r)}" fill="{bg}"/>'
            f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h * 0.16)}" '
            f'rx="{_f(r)}" fill="{lip}" opacity="0.8"/>')


def sign_text(x: float, y: float, text: str, size: int = 15,
              anchor: str = "start", night: bool = False,
              weight: str = "700") -> str:
    return (f'<text x="{_f(x)}" y="{_f(y)}" '
            f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="0.8" '
            f'fill="{CLOUD if night else SIGN_INK}" text-anchor="{anchor}">'
            f'{esc(text)}</text>')


def sign_figure(x: float, y: float, text: str, size: int = 22,
                anchor: str = "start", night: bool = False) -> str:
    return (f'<text x="{_f(x)}" y="{_f(y)}" '
            f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="{size}" '
            f'font-weight="700" letter-spacing="0.4" '
            f'fill="{SUN if night else SIGN_NUM}" text-anchor="{anchor}">'
            f'{esc(text)}</text>')


def title_sign(x: float, y: float, w: float, title: str, role: str, note: str,
               night: bool = False) -> str:
    """The plate header: cream board on dark posts, name + role + note."""
    o = [posts(x, y + 74, y, x + 18, x + w - 28), sign_board(x, y, w, 74, night)]
    o.append(sign_text(x + 20, y + 38, title[:22], 24, night=night))
    o.append(sign_text(x + 21, y + 60, role.upper()[:26], 13, night=night))
    if note:
        o.append(sign_text(x + w - 18, y + 60, note[:20], 13, "end", night))
    return "".join(o)


def data_sign(x: float, y: float, w: float, rows: list[tuple[str, str]],
              heading: str = "", night: bool = False,
              row_h: int = 30) -> str:
    """Rows of label + right-aligned figure on one board."""
    top = y + 32
    h = top - y + len(rows[:5]) * row_h + 16 + (30 if heading else 0)
    o = [posts(x, y + h + 26, y, x + 18, x + w - 28),
         sign_board(x, y, w, h, night)]
    if heading:
        o.append(sign_text(x + 20, top, heading.upper()[:28], 13, night=night))
        top += 30
    for i, (label, value) in enumerate(rows[:5]):
        ry = top + i * row_h
        o.append(sign_text(x + 20, ry, label[:24], 14, night=night))
        o.append(sign_figure(x + w - 20, ry, value[:14], 18, "end", night))
    return "".join(o)


def tile_sign(x: float, y: float, value: str, label: str,
              night: bool = False, w: float = 140, h: float = 76) -> str:
    o = [posts(x, y + h + 20, y, x + 16, x + w - 26),
         sign_board(x, y, w, h, night, r=11)]
    o.append(sign_figure(x + 16, y + 38, value[:9], 24, night=night))
    o.append(sign_text(x + 17, y + 60, label[:16], 12, night=night))
    return "".join(o)


def footer_band(w: int, y: float, h: int, left: str, right: str,
                night: bool = False) -> str:
    bg = SIGN_NIGHT if night else SIGN_BG
    fg = CLOUD if night else SIGN_INK
    return "".join([
        f'<rect x="0" y="{_f(y)}" width="{w}" height="{_f(h)}" rx="0" fill="{bg}"/>',
        f'<text x="34" y="{_f(y + h * 0.64)}" '
        f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="14" '
        f'font-weight="700" letter-spacing="0.8" fill="{fg}">'
        f'{esc(left[:52])}</text>',
        f'<text x="{w - 34}" y="{_f(y + h * 0.64)}" '
        f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="13" '
        f'font-weight="700" letter-spacing="0.8" fill="{fg}" text-anchor="end">'
        f'{esc(right[:30])}</text>',
    ])
