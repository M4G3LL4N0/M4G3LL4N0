"""Architectural depth primitives.

The reference renders read as three-dimensional because of four specific things,
none of which the earlier profile plates had:

  1. recessed windows with warm emissive interiors -- an inset shadow plus a
     glowing pane is the single strongest depth cue available in flat shading;
  2. stacked storeys with ledges, balcony slabs and railings, so the mass has
     horizontal rhythm instead of being one tall box;
  3. street-level architecture -- curb, sidewalk, crosswalk, bollards, lamp
     posts with light pools on the ground;
  4. atmospheric haze between depth layers, so distance is visible as contrast
     loss rather than as a drawn horizon line.

Characters are included because a figure at the right scale does more for depth
per polygon than any amount of shading.
"""

from __future__ import annotations

import math

from clay import _f, alpha, col, tint
from clay import PALETTE as P

from clay3d import cast_shadow


# ---------------------------------------------------------------------------
# buildings
# ---------------------------------------------------------------------------
def window_box(x: float, y: float, w: float, h: float, wall: str,
               pane: str | None = "sun", gid: str = "win",
               frame: bool = True) -> str:
    """A recessed window: dark reveal, warm pane, optional lit spill below.

    The reveal is what sells it. A flat rectangle of colour on a wall reads as
    paint; the same rectangle inset with a shadowed top and left edge reads as a
    hole in a wall.
    """
    wall = col(wall)
    out = [
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(min(w, h) * 0.14)}" fill="{tint(wall, -0.46)}"/>',
        f'<rect x="{_f(x + w * 0.10)}" y="{_f(y + h * 0.12)}" '
        f'width="{_f(w * 0.80)}" height="{_f(h * 0.76)}" '
        f'fill="{tint(wall, -0.30)}"/>',
    ]
    if pane:
        pane_c = col(pane)
        out += [
            f'<rect x="{_f(x + w * 0.16)}" y="{_f(y + h * 0.18)}" '
            f'width="{_f(w * 0.68)}" height="{_f(h * 0.64)}" '
            f'fill="{tint(pane_c, -0.06)}"/>',
            # the glow inside the pane
            f'<circle cx="{_f(x + w * 0.5)}" cy="{_f(y + h * 0.5)}" '
            f'r="{_f(w * 0.9)}" fill="url(#lampg{gid})" opacity="0.85"/>',
            f'<rect x="{_f(x + w * 0.46)}" y="{_f(y + h * 0.18)}" '
            f'width="{_f(max(w * 0.06, 1.2))}" height="{_f(h * 0.64)}" '
            f'fill="{tint(pane_c, -0.42)}"/>',
        ]
    else:
        out.append(f'<rect x="{_f(x + w * 0.16)}" y="{_f(y + h * 0.18)}" '
                   f'width="{_f(w * 0.68)}" height="{_f(h * 0.64)}" '
                   f'fill="{tint("dusk_soft", 0.42)}" opacity="0.5"/>')
    if frame:
        out.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" '
                   f'height="{_f(max(h * 0.08, 2))}" rx="1" '
                   f'fill="{tint(wall, 0.26)}"/>')
    return "".join(out)


def balcony(x: float, y: float, w: float, fill: str, posts: int = 5,
            rail: str | None = None) -> str:
    """A projecting balcony slab with a railed edge."""
    fill = col(fill)
    rail_c = col(rail or fill)
    d = 9.0
    out = [
        # slab: top face and front face
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(d)}" '
        f'fill="{tint(fill, 0.24)}"/>',
        f'<rect x="{_f(x)}" y="{_f(y + d)}" width="{_f(w)}" height="{_f(d * 0.8)}" '
        f'fill="{fill}"/>',
    ]
    ry = y - 22
    out.append(f'<rect x="{_f(x)}" y="{_f(ry + 16)}" width="{_f(w)}" '
               f'height="{_f(4)}" rx="2" fill="{rail_c}"/>')
    step = w / max(posts, 1)
    for i in range(posts + 1):
        bx = x + i * step
        out.append(f'<rect x="{_f(bx)}" y="{_f(ry)}" width="{_f(3.4)}" '
                   f'height="{_f(20)}" rx="1.6" fill="{rail_c}"/>')
    return "".join(out)


def building(x: float, y: float, w: float, h: float, floors: int,
             wall: str, gid: str = "win", lit: float = 0.7,
             seed: int = 0, balcony_every: int = 2) -> str:
    """A storeyed mass with recessed windows, ledges and balconies.

    `lit` is the fraction of windows that glow, so a run of buildings reads as a
    populated street rather than as a repeated stamp.
    """
    wall = col(wall)
    out = [cast_shadow(x + w * 0.5 + 12, y + h + 4, w * 0.56, 9, gid, skew=-4)]
    # mass: three flat planes
    d = 15.0
    out += [
        f'<path d="M{_f(x)},{_f(y)} L{_f(x + w)},{_f(y)} '
        f'L{_f(x + w + d)},{_f(y - d)} L{_f(x + d)},{_f(y - d)} Z" '
        f'fill="{tint(wall, 0.26)}"/>',
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'fill="{wall}"/>',
        f'<rect x="{_f(x + w)}" y="{_f(y)}" width="{_f(d)}" '
        f'height="{_f(h)}" fill="{tint(wall, -0.22)}"/>',
    ]
    fh = h / max(floors, 1)
    cols = max(2, int(w / 46))
    cw = w / cols
    for f in range(floors):
        fy = y + fh * f
        # storey ledge
        out.append(f'<rect x="{_f(x)}" y="{_f(fy)}" width="{_f(w)}" '
                   f'height="{_f(4)}" fill="{tint(wall, 0.18)}" opacity="0.7"/>')
        out.append(f'<rect x="{_f(x)}" y="{_f(fy + fh - 5)}" width="{_f(w)}" '
                   f'height="{_f(5)}" fill="{tint(wall, -0.16)}" opacity="0.6"/>')
        for c in range(cols):
            key = (f * 7 + c * 13 + seed * 5) % 10
            on = (key / 10.0) < lit
            wx = x + cw * c + cw * 0.22
            wy = fy + fh * 0.22
            out.append(window_box(wx, wy, cw * 0.56, fh * 0.46, wall,
                                  "sun" if on else None, gid))
        if balcony_every and f % balcony_every == 0 and f > 0 and cols >= 2:
            bx = x + cw * 0.5
            out.append(balcony(bx, fy + fh * 0.80, cw * (cols - 1), "cream", posts=4))
    return "".join(out)


# ---------------------------------------------------------------------------
# street level
# ---------------------------------------------------------------------------
def curb(w: int, y: float, h: int, fill: str, edge: str | None = None) -> str:
    """Sidewalk with a raised curb and a chamfered nose."""
    fill = col(fill)
    edge_c = col(edge or fill)
    return "".join([
        f'<rect x="0" y="{_f(y)}" width="{w}" height="{_f(h)}" fill="{fill}"/>',
        f'<rect x="0" y="{_f(y + h)}" width="{w}" height="4" '
        f'fill="{tint(edge_c, 0.26)}"/>',
        f'<rect x="0" y="{_f(y + h + 4)}" width="{w}" height="3" '
        f'fill="{tint(edge_c, -0.18)}"/>',
    ])


def crosswalk(w: int, y: float, h: int, bars: int = 7) -> str:
    """Zebra bars on the roadway, receding."""
    out = []
    gap = w / (bars * 2 - 1)
    for i in range(bars):
        bw = gap * 1.35
        bh = h * (0.62 + i * 0.055)
        x = w * 0.06 + i * gap * 2
        out.append(f'<rect x="{_f(x)}" y="{_f(y + h - bh)}" width="{_f(bw)}" '
                   f'height="{_f(bh)}" rx="3" fill="{P["cream"]}" opacity="0.82"/>')
    return "".join(out)


def bollard(x: float, base_y: float, h: float = 30.0, fill: str = "coral") -> str:
    fill = col(fill)
    return "".join([
        cast_shadow(x + 3, base_y + 1, 9, 3, "castb"),
        f'<rect x="{_f(x - 5)}" y="{_f(base_y - h)}" width="10" '
        f'height="{_f(h)}" rx="5" fill="{fill}"/>',
        f'<rect x="{_f(x - 5)}" y="{_f(base_y - h)}" width="10" height="7" '
        f'rx="3.5" fill="{tint(fill, 0.28)}"/>',
    ])


def lamp_post(x: float, base_y: float, h: float, gid: str,
              head: float = 15.0) -> str:
    """A street lamp with a warm head and a light pool on the pavement."""
    return "".join([
        f'<ellipse cx="{_f(x)}" cy="{_f(base_y + 2)}" rx="{_f(h * 0.42)}" '
        f'ry="7" fill="{alpha(P["sun"], 0.16)}"/>',
        f'<rect x="{_f(x - 2.6)}" y="{_f(base_y - h)}" width="5.2" '
        f'height="{_f(h)}" rx="2.6" fill="{P["dusk_mid"]}"/>',
        f'<circle cx="{_f(x)}" cy="{_f(base_y - h - head * 0.4)}" '
        f'r="{_f(head)}" fill="url(#lampg{gid})"/>',
        f'<circle cx="{_f(x)}" cy="{_f(base_y - h - head * 0.4)}" '
        f'r="{_f(head * 0.62)}" fill="{P["sun"]}"/>',
        f'<rect x="{_f(x - head * 0.5)}" y="{_f(base_y - h - head * 1.1)}" '
        f'width="{_f(head)}" height="4" rx="2" fill="{P["dusk_deep"]}"/>',
    ])


def festoon(x0: float, y0: float, x1: float, y1: float, bulbs: int,
            sag: float = 16.0, gid: str = "win") -> str:
    """String lights. Two catenaries of cable with warm bulbs hanging off them."""
    out = []
    for k in range(2):
        sag_k = sag * (0.6 + k * 0.55)
        pts = []
        for i in range(21):
            t = i / 20
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + math.sin(t * math.pi) * sag_k
            pts.append(f"{'M' if i == 0 else 'L'}{_f(x)},{_f(y)}")
        out.append(f'<path d="{" ".join(pts)}" fill="none" '
                   f'stroke="{P["dusk_deep"]}" stroke-width="1.6"/>')
    n = max(bulbs // 2, 3)
    for k in range(2):
        sag_k = sag * (0.6 + k * 0.55)
        for i in range(1, n):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + math.sin(t * math.pi) * sag_k
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y + 5)}" r="6" '
                       f'fill="url(#lampg{gid})" opacity="0.8"/>')
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y + 5)}" r="2.6" '
                       f'fill="{P["sun"]}"/>')
    return "".join(out)


def awning(x: float, y: float, w: float, drop: float, a: str, b: str,
           stripes: int = 6) -> str:
    """A scalloped shop awning."""
    a, b = col(a), col(b)
    out = []
    sw = w / stripes
    for i in range(stripes):
        c = a if i % 2 == 0 else b
        out.append(f'<path d="M{_f(x + i * sw)},{_f(y)} '
                   f'L{_f(x + (i + 1) * sw)},{_f(y)} '
                   f'L{_f(x + (i + 1) * sw)},{_f(y + drop)} '
                   f'Q{_f(x + (i + 0.5) * sw)},{_f(y + drop + 7)} {_f(x + i * sw)},{_f(y + drop)} Z" '
                   f'fill="{c}"/>')
    out.append(f'<rect x="{_f(x)}" y="{_f(y - 3)}" width="{_f(w)}" height="4" '
               f'rx="2" fill="{tint(a, -0.3)}"/>')
    return "".join(out)


def sign_board(x: float, y: float, w: float, h: float, face: str,
               border: str | None = None, radius: float = 6.0) -> str:
    face = col(face)
    out = [f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
           f'rx="{_f(radius)}" fill="{tint(face, -0.22)}"/>']
    out.append(f'<rect x="{_f(x + 3)}" y="{_f(y + 3)}" width="{_f(w - 6)}" '
               f'height="{_f(h - 6)}" rx="{_f(max(radius - 2, 2))}" fill="{face}"/>')
    if border:
        b = col(border)
        out.append(f'<rect x="{_f(x + 3)}" y="{_f(y + 3)}" width="{_f(w - 6)}" '
                   f'height="{_f(h - 6)}" rx="{_f(max(radius - 2, 2))}" '
                   f'fill="none" stroke="{b}" stroke-width="2.5"/>')
    return "".join(out)


def railing(x: float, y: float, w: float, h: float, fill: str,
            posts: int = 7) -> str:
    fill = col(fill)
    out = [f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="4.5" rx="2" '
           f'fill="{tint(fill, 0.22)}"/>',
           f'<rect x="{_f(x)}" y="{_f(y + h * 0.52)}" width="{_f(w)}" '
           f'height="3.4" rx="1.6" fill="{fill}"/>']
    step = w / max(posts, 1)
    for i in range(posts + 1):
        bx = x + i * step
        out.append(f'<rect x="{_f(bx)}" y="{_f(y)}" width="{_f(4)}" '
                   f'height="{_f(h)}" rx="2" fill="{fill}"/>')
    return "".join(out)


# ---------------------------------------------------------------------------
# characters and props -- scale references
# ---------------------------------------------------------------------------
def figure(x: float, base_y: float, h: float, shirt: str = "turquoise",
           hair: str = "clay_red", gid: str = "win") -> str:
    """A simple blocky person. Six shapes, and the scene suddenly has scale."""
    shirt = col(shirt)
    hair = col(hair)
    hh = h * 0.30
    hw = h * 0.40
    return "".join([
        cast_shadow(x + 4, base_y + 1, hw * 0.7, 3.5, "castb"),
        # legs
        f'<rect x="{_f(x - hw * 0.30)}" y="{_f(base_y - h * 0.34)}" '
        f'width="{_f(hw * 0.24)}" height="{_f(h * 0.34)}" rx="2" '
        f'fill="{P["dusk_deep"]}"/>',
        f'<rect x="{_f(x + hw * 0.06)}" y="{_f(base_y - h * 0.34)}" '
        f'width="{_f(hw * 0.24)}" height="{_f(h * 0.34)}" rx="2" '
        f'fill="{P["dusk_deep"]}"/>',
        # torso
        f'<rect x="{_f(x - hw * 0.44)}" y="{_f(base_y - h * 0.68)}" '
        f'width="{_f(hw * 0.88)}" height="{_f(h * 0.38)}" rx="{_f(hw * 0.20)}" '
        f'fill="{shirt}"/>',
        # arms
        f'<rect x="{_f(x - hw * 0.60)}" y="{_f(base_y - h * 0.66)}" '
        f'width="{_f(hw * 0.17)}" height="{_f(h * 0.30)}" rx="{_f(hw * 0.08)}" '
        f'fill="{shirt}"/>',
        f'<rect x="{_f(x + hw * 0.43)}" y="{_f(base_y - h * 0.66)}" '
        f'width="{_f(hw * 0.17)}" height="{_f(h * 0.30)}" rx="{_f(hw * 0.08)}" '
        f'fill="{shirt}"/>',
        # head
        f'<rect x="{_f(x - hw * 0.32)}" y="{_f(base_y - h * 0.98)}" '
        f'width="{_f(hw * 0.64)}" height="{_f(hh)}" rx="{_f(hh * 0.28)}" '
        f'fill="{tint("beige", 0.10)}"/>',
        f'<rect x="{_f(x - hw * 0.34)}" y="{_f(base_y - h * 1.02)}" '
        f'width="{_f(hw * 0.68)}" height="{_f(hh * 0.46)}" rx="{_f(hh * 0.20)}" '
        f'fill="{hair}"/>',
    ])


def flame(x: float, base_y: float, w: float, h: float, gid: str = "win") -> str:
    """A faceted campfire flame: three stacked tongues, warm to white."""
    core = P["sun"]
    out = [
        f'<circle cx="{_f(x)}" cy="{_f(base_y - h * 0.42)}" '
        f'r="{_f(w * 1.5)}" fill="url(#lampg{gid})" opacity="0.9"/>',
        f'<path d="M{_f(x - w)},{_f(base_y)} L{_f(x - w * 0.30)},'
        f'{_f(base_y - h * 0.62)} L{_f(x + w * 0.22)},{_f(base_y - h * 0.30)} '
        f'L{_f(x + w)},{_f(base_y)} Z" fill="{P["ember"]}"/>',
        f'<path d="M{_f(x - w * 0.66)},{_f(base_y)} L{_f(x - w * 0.10)},'
        f'{_f(base_y - h)} L{_f(x + w * 0.42)},{_f(base_y - h * 0.34)} '
        f'L{_f(x + w * 0.66)},{_f(base_y)} Z" fill="{core}"/>',
        f'<path d="M{_f(x - w * 0.30)},{_f(base_y)} L{_f(x + w * 0.04)},'
        f'{_f(base_y - h * 0.72)} L{_f(x + w * 0.34)},{_f(base_y)} Z" '
        f'fill="{P["cream"]}"/>',
    ]
    return "".join(out)


def log_ring(x: float, base_y: float, r: float, n: int = 7,
             fill: str = "clay_red") -> str:
    fill = col(fill)
    out = []
    for i in range(n):
        a = (i / n) * math.tau
        lx = x + math.cos(a) * r
        ly = base_y + math.sin(a) * r * 0.34
        out.append(f'<rect x="{_f(lx - 7)}" y="{_f(ly - 5)}" width="15" '
                   f'height="11" rx="5" fill="{tint(fill, 0.08 * (i % 3))}"/>')
        out.append(f'<circle cx="{_f(lx - 4)}" cy="{_f(ly)}" r="3.4" '
                   f'fill="{tint("beige", 0.2)}" opacity="0.7"/>')
    return "".join(out)


def umbrella(x: float, base_y: float, r: float, h: float,
             a: str = "coral", b: str = "cream") -> str:
    a, b = col(a), col(b)
    out = [f'<rect x="{_f(x - 2.4)}" y="{_f(base_y - h)}" width="4.8" '
           f'height="{_f(h)}" rx="2.4" fill="{P["beige"]}"/>']
    seg = 8
    for i in range(seg):
        c = a if i % 2 == 0 else b
        a0 = math.pi + i / seg * math.pi
        a1 = math.pi + (i + 1) / seg * math.pi
        x0, y0 = x + math.cos(a0) * r, base_y - h + math.sin(a0) * r * 0.42
        x1, y1 = x + math.cos(a1) * r, base_y - h + math.sin(a1) * r * 0.42
        out.append(f'<path d="M{_f(x)},{_f(base_y - h)} L{_f(x0)},{_f(y0)} '
                   f'L{_f(x1)},{_f(y1)} Z" fill="{c}"/>')
    return "".join(out)


def chair(x: float, base_y: float, s: float, fill: str = "coral") -> str:
    fill = col(fill)
    return "".join([
        cast_shadow(x + s * 0.2, base_y + 1, s * 0.6, 3.5, "castb"),
        f'<rect x="{_f(x - s * 0.46)}" y="{_f(base_y - s * 0.46)}" '
        f'width="{_f(s * 0.92)}" height="{_f(s * 0.16)}" rx="3" fill="{fill}"/>',
        f'<rect x="{_f(x + s * 0.24)}" y="{_f(base_y - s * 1.30)}" '
        f'width="{_f(s * 0.18)}" height="{_f(s * 0.9)}" rx="4" fill="{fill}"/>',
        f'<rect x="{_f(x - s * 0.36)}" y="{_f(base_y - s * 0.30)}" '
        f'width="{_f(s * 0.09)}" height="{_f(s * 0.30)}" rx="2" '
        f'fill="{tint(fill, -0.34)}"/>',
        f'<rect x="{_f(x + s * 0.27)}" y="{_f(base_y - s * 0.30)}" '
        f'width="{_f(s * 0.09)}" height="{_f(s * 0.30)}" rx="2" '
        f'fill="{tint(fill, -0.34)}"/>',
    ])


def tent(x: float, base_y: float, w: float, h: float, fill: str) -> str:
    fill = col(fill)
    d = w * 0.30
    return "".join([
        cast_shadow(x + w * 0.2, base_y + 1, w * 0.6, 5, "castb"),
        f'<path d="M{_f(x)},{_f(base_y)} L{_f(x + w * 0.5)},{_f(base_y - h)} '
        f'L{_f(x + w)},{_f(base_y)} Z" fill="{fill}"/>',
        f'<path d="M{_f(x + w)},{_f(base_y)} L{_f(x + w * 0.5)},{_f(base_y - h)} '
        f'L{_f(x + w + d)},{_f(base_y - d)} Z" fill="{tint(fill, -0.22)}"/>',
        f'<path d="M{_f(x + w * 0.34)},{_f(base_y)} L{_f(x + w * 0.5)},'
        f'{_f(base_y - h * 0.46)} L{_f(x + w * 0.66)},{_f(base_y)} Z" '
        f'fill="{tint(P["dusk_deep"], 0.10)}"/>',
    ])


def cooler(x: float, base_y: float, w: float, h: float) -> str:
    return "".join([
        cast_shadow(x + w * 0.2, base_y + 1, w * 0.6, 3, "castb"),
        f'<rect x="{_f(x)}" y="{_f(base_y - h)}" width="{_f(w)}" '
        f'height="{_f(h)}" rx="4" fill="{P["cactus"]}"/>',
        f'<rect x="{_f(x)}" y="{_f(base_y - h)}" width="{_f(w)}" '
        f'height="{_f(h * 0.34)}" rx="3" fill="{P["cream"]}"/>',
        f'<rect x="{_f(x + w * 0.3)}" y="{_f(base_y - h * 1.06)}" '
        f'width="{_f(w * 0.4)}" height="{_f(h * 0.1)}" rx="3" fill="{P["beige"]}"/>',
    ])


# ---------------------------------------------------------------------------
# atmosphere
# ---------------------------------------------------------------------------
def haze(y: float, h: float, w: int, color: str, a: float = 0.18) -> str:
    """Atmospheric perspective: distance as contrast loss, not a drawn line."""
    return (f'<rect x="0" y="{_f(y)}" width="{w}" height="{_f(h)}" '
            f'fill="{alpha(color, a)}"/>')


def depth_fade(body: str, a: float) -> str:
    """Push a whole group back by reducing its opacity."""
    return f'<g opacity="{a:.2f}">{body}</g>'


def street_lamp_pool(x: float, base_y: float, r: float) -> str:
    return (f'<ellipse cx="{_f(x)}" cy="{_f(base_y)}" rx="{_f(r)}" '
            f'ry="{_f(r * 0.24)}" fill="{alpha(P["sun"], 0.20)}"/>')