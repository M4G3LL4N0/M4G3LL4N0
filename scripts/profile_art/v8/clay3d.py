"""Deeper clay volume and seamless looping motion for the profile surfaces.

This is the profile-only upgrade over clay.py. Two additions:

Volume
    Chamfered edges, an ambient-occlusion gradient where a mass meets the
    ground, cast shadows on the floor plane, a receding paver floor, and
    layered distant mesas. All of it is still flat-shaded and block-like; the
    depth comes from stacking a few honest planes rather than from gradients
    pretending to be a renderer.

Motion
    Every animation returns to its starting value, so each surface loops
    seamlessly with no visible seam. The earlier settle() froze after one pass,
    which reads as a still image rather than as a loop.
"""

from __future__ import annotations

import clay as C
from clay import _f, alpha, col, esc, tint

P = __import__("clay").PALETTE


# ---------------------------------------------------------------------------
# loop motion -- every value list starts and ends on the same value
# ---------------------------------------------------------------------------
def _mix_hex(a: str, b: str, t: float) -> str:
    """Blend two colours; used so light mode stays warm instead of going grey."""
    from clay import _rgb, _hex
    ra, ga, ba = _rgb(col(a))
    rb, gb, bb = _rgb(col(b))
    return _hex(ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t)


def _loop(attr: str, values: str, dur: float, begin: float = 0.0,
          type_: str | None = None, extra: str = "") -> str:
    kind = f' type="{type_}"' if type_ else ""
    return (f'<animate attributeName="{attr}" values="{values}" dur="{_f(dur)}s" '
            f'begin="{_f(begin)}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="0;0.5;1" '
            f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"{kind}{extra}/>')


def hover_loop(amp: float = 7.0, dur: float = 7.0, begin: float = 0.0) -> str:
    """A slow vertical breath. Returns exactly to its start, so it loops."""
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 {_f(-amp)};0 0" dur="{_f(dur)}s" begin="{_f(begin)}s" '
            f'repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
            f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>')


def drift_loop(dx: float, dur: float, begin: float = 0.0, dy: float = 0.0) -> str:
    """A lazy sideways wander that closes on itself."""
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{_f(dx)} {_f(-dy)};0 0" dur="{_f(dur)}s" '
            f'begin="{_f(begin)}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;0.5;1" keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>')


def sway_loop(deg: float = 1.6, dur: float = 9.0, begin: float = 0.0,
              origin: str = "0 0") -> str:
    """A very small rotation, for vegetation and hanging marks."""
    return (f'<animateTransform attributeName="transform" type="rotate" '
            f'values="0 {origin};{_f(deg)} {origin};0 {origin}" '
            f'dur="{_f(dur)}s" begin="{_f(begin)}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="0;0.5;1" '
            f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>')


def glow_loop(lo: float, hi: float, dur: float, begin: float = 0.0) -> str:
    """Opacity breathing that never fully vanishes, and returns to its start."""
    return _loop("opacity", f"{lo};{hi};{lo}", dur, begin)


def halo_loop(lo: float, hi: float, dur: float, begin: float = 0.0) -> str:
    """The sun halo swelling and settling, seamlessly."""
    return (f'<animate attributeName="r" values="{_f(lo)};{_f(hi)};{_f(lo)}" '
            f'dur="{_f(dur)}s" begin="{_f(begin)}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="0;0.5;1" '
            f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>')


def flicker_loop(dur: float, begin: float = 0.0, a: float = 0.55,
                 b: float = 0.95) -> str:
    """Warm interior light with a gentle, closed-loop shimmer."""
    return _loop("opacity", f"{a};{b};{a}", dur, begin)


def roll_loop(deg: float, dur: float, begin: float = 0.0,
              cx: float = 0, cy: float = 0) -> str:
    """Slow full rotation for the sun mark and other radial objects."""
    return (f'<animateTransform attributeName="transform" type="rotate" '
            f'values="0 {_f(cx)} {_f(cy)};{_f(deg)} {_f(cx)} {_f(cy)};'
            f'0 {_f(cx)} {_f(cy)}" dur="{_f(dur)}s" begin="{_f(begin)}s" '
            f'repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
            f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>')


# ---------------------------------------------------------------------------
# defs
# ---------------------------------------------------------------------------
def defs(gid: str, p: dict, light: bool = False) -> str:
    """Gradients that do the soft work: sky, halo, occlusion, cast shadow.

    The sky gradient lives here, not in backdrop(), so it has to know about the
    light variant. Without this the light plates kept the dusk sky and put dark
    ink on top of it, which is unreadable.
    """
    sky = col(p["sky"])
    if light:
        sky = _mix_hex(sky, P["cream"], 0.90)
        halo_op = 0.30
    else:
        halo_op = 0.42
    return (
        f'<linearGradient id="sky{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{tint(sky, -0.22)}"/>'
        f'<stop offset="0.55" stop-color="{sky}"/>'
        f'<stop offset="0.88" stop-color="{tint(P["peach"], 0.30)}"/>'
        f'<stop offset="1" stop-color="{tint(P["peach"], 0.52)}"/>'
        f'</linearGradient>'
        f'<radialGradient id="halo{gid}">'
        f'<stop offset="0.30" stop-color="{P["sun"]}" stop-opacity="{halo_op}"/>'
        f'<stop offset="1" stop-color="{P["sun"]}" stop-opacity="0"/>'
        f'</radialGradient>'
        # Ambient occlusion: the darkening where a mass meets the ground.
        f'<linearGradient id="ao{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{P["dusk_deep"]}" stop-opacity="0.20"/>'
        f'<stop offset="1" stop-color="{P["dusk_deep"]}" stop-opacity="0"/>'
        f'</linearGradient>'
        f'<radialGradient id="cast{gid}">'
        f'<stop offset="0" stop-color="{P["shadow"]}" stop-opacity="0.34"/>'
        f'<stop offset="0.7" stop-color="{P["shadow"]}" stop-opacity="0.10"/>'
        f'<stop offset="1" stop-color="{P["shadow"]}" stop-opacity="0"/>'
        f'</radialGradient>'
        f'<linearGradient id="floor{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{tint(P["sand"], 0.18)}"/>'
        f'<stop offset="0.35" stop-color="{P["sand"]}"/>'
        f'<stop offset="1" stop-color="{tint(P["sand"], -0.16)}"/>'
        f'</linearGradient>'
        f'<radialGradient id="lampg{gid}">'
        f'<stop offset="0.15" stop-color="{P["sun"]}" stop-opacity="0.62"/>'
        f'<stop offset="1" stop-color="{P["sun"]}" stop-opacity="0"/>'
        f'</radialGradient>'
    )


# ---------------------------------------------------------------------------
# environment
# ---------------------------------------------------------------------------
def backdrop(w: int, h: int, horizon: float, p: dict, gid: str,
             light: bool = False) -> str:
    """Sky, halo sun, horizon haze, distant mesas and a receding paver floor.

    The distant ridges are the main depth cue: three layers at falling contrast
    read as kilometres of air between the viewer and the settlement.
    """
    out = [f'<rect width="{w}" height="{h}" fill="url(#sky{gid})"/>']

    # Sun with a slow breathing halo.
    sx, sy, sr = w - 168, 118, 52
    out.append(f'<g>'
               f'<circle cx="{sx}" cy="{sy}" r="{_f(sr * 2.5)}" fill="url(#halo{gid})">'
               f'{halo_loop(sr * 2.2, sr * 2.8, 15)}</circle>'
               f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{P["sun"]}"/>'
               f'<circle cx="{_f(sx - sr * 0.24)}" cy="{_f(sy - sr * 0.28)}" '
               f'r="{_f(sr * 0.58)}" fill="{tint("sun", 0.32)}" opacity="0.45"/>'
               f'</g>')

    # Horizon haze, which separates ground from sky without a hard edge.
    out.append(f'<rect x="0" y="{_f(horizon - 46)}" width="{w}" height="46" '
               f'fill="{alpha(P["peach"], 0.16)}"/>')

    # Two soft ridge layers. Three jagged ones read as horizontal stripes
    # behind the ground instead of as distance.
    for lift, tone, a in ((58, tint(p["sky"], 0.16), 0.42),
                          (30, P["shadow"], 0.20)):
        base = horizon - lift
        rh = 34
        pts = [f"0,{_f(base)}"]
        peaks = [0.55, 1.0, 0.7, 0.9, 0.5]
        for i, pk in enumerate(peaks):
            x0 = w * i / len(peaks)
            x1 = w * (i + 1) / len(peaks)
            pts.append(f"{_f(x0)},{_f(base - rh * pk * 0.55)}")
            pts.append(f"{_f((x0 + x1) / 2)},{_f(base - rh * pk)}")
            pts.append(f"{_f(x1)},{_f(base - rh * pk * 0.5)}")
        pts.append(f"{w},{_f(base)}")
        out.append(f'<polygon points="{" ".join(pts)}" fill="{tone}" opacity="{a}"/>')

    # Receding paver floor. The first pass used bands too faint to see and no
    # seams at all, so the ground read as flat paper.
    out.append(f'<rect x="0" y="{_f(horizon)}" width="{w}" height="{_f(h - horizon)}" '
               f'fill="url(#floor{gid})"/>')
    vx = w * 0.5
    for k in range(-9, 10):
        out.append(f'<path d="M{_f(vx)},{_f(horizon)} L{_f(vx + k * 190)},{_f(h)}" '
                   f'stroke="{alpha(P["beige"], 0.22)}" stroke-width="2"/>')
    y = horizon + 5
    step = 6.0
    while y < h:
        out.append(f'<rect x="0" y="{_f(y)}" width="{w}" height="{_f(step * 0.30)}" '
                   f'fill="{alpha(P["beige"], 0.42)}"/>')
        y += step
        step *= 1.36
    out.append(f'<rect x="0" y="{_f(horizon)}" width="{w}" height="3" '
               f'fill="{tint(P["sand"], 0.30)}"/>')
    return "".join(out)


def cloud(cx: float, cy: float, s: float, dur: float, begin: float = 0.0,
          dy: float = 6.0) -> str:
    """A soft cream cloud on a closed drift loop."""
    body = "".join([
        f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(s * 0.42)}" fill="{P["cream"]}"/>',
        f'<circle cx="{_f(cx - s * 0.42)}" cy="{_f(cy + s * 0.12)}" '
        f'r="{_f(s * 0.32)}" fill="{P["cream"]}"/>',
        f'<circle cx="{_f(cx + s * 0.44)}" cy="{_f(cy + s * 0.1)}" '
        f'r="{_f(s * 0.3)}" fill="{P["cream"]}"/>',
        f'<rect x="{_f(cx - s * 0.72)}" y="{_f(cy + s * 0.08)}" '
        f'width="{_f(s * 1.48)}" height="{_f(s * 0.26)}" rx="{_f(s * 0.13)}" '
        f'fill="{P["cream"]}"/>',
    ])
    return f'<g>{body}{drift_loop(s * 0.34, dur, begin, dy)}</g>'


# ---------------------------------------------------------------------------
# higher-volume solids
# ---------------------------------------------------------------------------
def ao(x: float, y: float, w: float, h: float, gid: str) -> str:
    """The darkening band at the foot of a mass: the single strongest cue."""
    return (f'<rect x="{_f(x)}" y="{_f(y + h - 13)}" width="{_f(w)}" height="13" '
            f'fill="url(#ao{gid})" rx="5"/>')


def cast_shadow(cx: float, cy: float, rx: float, ry: float, gid: str,
                skew: float = 0.0) -> str:
    """A soft cast shadow on the floor, optionally skewed away from the sun."""
    tr = f' transform="skewX({_f(skew)})"' if skew else ""
    return (f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" ry="{_f(ry)}" '
            f'fill="url(#cast{gid})"{tr}/>')


def block(x: float, y: float, w: float, h: float, d: float, fill: str,
          r: float = 10.0, gid: str | None = None, shadow: bool = True) -> str:
    """A chamfered block: five planes instead of three.

    The chamfer is a narrow lit strip along the top front edge plus a shaded
    strip on the right. Flat shading plus one beveled edge reads as a sculpted
    object rather than a folded flat shape.
    """
    fill = col(fill)
    top = tint(fill, 0.28)
    side = tint(fill, -0.20)
    ch_w = max(min(w * 0.22, 16.0), 5.0)
    j = (f' stroke="{fill}" stroke-width="6" stroke-linejoin="round"'
         if fill else "")
    out = []
    if shadow:
        out.append(cast_shadow(x + w / 2 + d * 0.6, y + h + 5, w * 0.62, 13,
                               gid) if gid else "")
    out += [
        f'<path d="M{_f(x)},{_f(y)} L{_f(x + w)},{_f(y)} '
        f'L{_f(x + w + d)},{_f(y - d)} L{_f(x + d)},{_f(y - d)} Z" fill="{top}"{j}/>',
        f'<path d="M{_f(x + w)},{_f(y)} L{_f(x + w + d)},{_f(y - d)} '
        f'L{_f(x + w + d)},{_f(y + h - d)} L{_f(x + w)},{_f(y + h)} Z" '
        f'fill="{side}"{j}/>',
        # Chamfer: lit top strip and shaded right strip.
        f'<path d="M{_f(x)},{_f(y)} L{_f(x + w)},{_f(y)} '
        f'L{_f(x + w - ch_w)},{_f(y + ch_w * 0.62)} '
        f'L{_f(x + ch_w)},{_f(y + ch_w * 0.62)} Z" '
        f'fill="{tint(fill, 0.46)}" opacity="0.85"/>',
        f'<path d="M{_f(x + w)},{_f(y)} L{_f(x + w - ch_w * 0.62)},'
        f'{_f(y + ch_w * 0.62)} L{_f(x + w - ch_w * 0.62)},{_f(y + h)} '
        f'L{_f(x + w)},{_f(y + h)} Z" fill="{tint(fill, -0.34)}" opacity="0.7"/>',
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(r)}" fill="{fill}"/>',
    ]
    if gid:
        out.append(ao(x, y, w, h, gid))
    return "".join(o for o in out if o)


def mesa(x: float, y: float, w: float, h: float, steps: int, fill: str,
         d: float = 20.0, gid: str | None = None) -> str:
    """Stepped adobe massing with volume, hover and staggered looping."""
    fill = col(fill)
    out = []
    sh = h / steps
    for i in range(steps):
        inset = i * w * 0.075
        bw = w - inset * 2
        bx = x + inset
        by = y + (steps - i - 1) * sh
        grp = block(bx, by, bw, sh + 2, d, tint(fill, 0.06 * (steps - i)),
                    r=8, gid=None)
        # Each terrace breathes on its own phase so the stack never pulses as
        # one rigid object.
        out.append(f'<g>{grp}{hover_loop(3.0 + i * 0.5, 8.5 + i * 0.7, i * 0.55)}</g>')
    return "".join(out)


def gateway(x: float, y: float, w: float, h: float, fill: str,
            gid: str, dur: float = 10.0) -> str:
    """The adobe arch: cut-out opening, lit rim, base occlusion, looping depth."""
    fill = col(fill)
    leg = 0.24
    lw = w * leg
    r = (w - 2 * lw) / 2
    spring = y + r
    outer = (f"M{_f(x)},{_f(y + h)} L{_f(x)},{_f(spring)} "
             f"A{_f(r + lw)},{_f(r + lw)} 0 0 1 {_f(x + w)},{_f(spring)} "
             f"L{_f(x + w)},{_f(y + h)} Z")
    inner = (f"M{_f(x + lw)},{_f(y + h - 6)} L{_f(x + lw)},{_f(y + r * 0.9)} "
             f"A{_f(r)},{_f(r)} 0 0 1 {_f(x + w - lw)},{_f(y + r * 0.9)} "
             f"L{_f(x + w - lw)},{_f(y + h - 6)} Z")
    body = "".join([
        # A recessed interior wall, so the opening has depth instead of showing sky.
        f'<path d="{inner}" fill="{tint(P["dusk_deep"], -0.18)}"/>',
        f'<path d="{outer} {inner}" fill="{fill}" fill-rule="evenodd" '
        f'stroke="{fill}" stroke-width="7" stroke-linejoin="round"/>',
        f'<path d="{outer}" fill="none" stroke="{tint(fill, 0.34)}" '
        f'stroke-width="9" stroke-linecap="round" opacity="0.9"/>',
        f'<rect x="{_f(x + w * 0.06)}" y="{_f(spring)}" width="{_f(w * 0.055)}" '
        f'height="{_f(h - r)}" fill="{tint(fill, -0.18)}"/>',
        ao(x, y, w, h, gid),
    ])
    return f'<g>{body}{hover_loop(3.5, dur, 1.2)}</g>'


def cactus(cx: float, base_y: float, w: float, h: float, fill: str,
           dur: float = 11.0, begin: float = 0.0) -> str:
    """Saguaro with volume and a slow sway about its base."""
    fill = col(fill)
    bw = w * 0.34
    arm_h = h * 0.34
    body = "".join([
        cast_shadow(cx + 10, base_y + 3, w * 0.5, 8, "cast2"),
        f'<rect x="{_f(cx - bw / 2)}" y="{_f(base_y - h)}" width="{_f(bw)}" '
        f'height="{_f(h)}" rx="{_f(bw / 2)}" fill="{fill}"/>',
        f'<rect x="{_f(cx - bw * 0.34)}" y="{_f(base_y - h * 0.97)}" '
        f'width="{_f(bw * 0.3)}" height="{_f(h * 0.9)}" rx="{_f(bw * 0.15)}" '
        f'fill="{tint(fill, 0.26)}"/>',
        f'<rect x="{_f(cx - w * 0.62)}" y="{_f(base_y - h * 0.66)}" '
        f'width="{_f(w * 0.3)}" height="{_f(arm_h)}" rx="{_f(w * 0.15)}" fill="{fill}"/>',
        f'<rect x="{_f(cx + w * 0.32)}" y="{_f(base_y - h * 0.8)}" '
        f'width="{_f(w * 0.3)}" height="{_f(arm_h)}" rx="{_f(w * 0.15)}" fill="{fill}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(base_y - h + bw * 0.5)}" '
        f'r="{_f(bw * 0.5)}" fill="{tint(fill, 0.30)}"/>',
    ])
    return f'<g>{body}{sway_loop(1.1, dur, begin, f"{_f(cx)} {_f(base_y)}")}</g>'


def conifer(cx: float, base_y: float, w: float, h: float, fill: str,
            dur: float = 12.0, begin: float = 0.0) -> str:
    """Low-poly conifer, tiers on staggered phases."""
    fill = col(fill)
    trunk = h * 0.16
    tiers = "".join(
        f'<g>{_cone(cx, base_y - trunk - i * (h - trunk) / 3,
                    w * (1 - 0.26 * i), (h - trunk) / 3 * 1.5,
                    tint(fill, 0.16 - 0.1 * i))}'
        f'{hover_loop(2.2 + i * 0.6, 7.6 + i * 0.8, begin + i * 0.7)}</g>'
        for i in range(3))
    body = (f'<rect x="{_f(cx - w * 0.09)}" y="{_f(base_y - trunk)}" '
            f'width="{_f(w * 0.18)}" height="{_f(trunk)}" rx="{_f(w * 0.05)}" '
            f'fill="{tint(P["clay_red"], 0.05)}"/>')
    return f'<g>{body}{tiers}{sway_loop(0.8, dur + 3, begin, f"{_f(cx)} {_f(base_y)}")}</g>'


def _cone(cx: float, base_y: float, w: float, h: float, fill: str) -> str:
    fill = col(fill)
    return (f'<path d="M{_f(cx)},{_f(base_y - h)} '
            f'Q{_f(cx - w / 2)},{_f(base_y - h * 0.42)} {_f(cx - w / 2)},{_f(base_y - h * 0.18)} '
            f'Q{_f(cx - w / 2)},{_f(base_y)} {_f(cx - w / 2 + 6)},{_f(base_y)} '
            f'L{_f(cx + w / 2 - 6)},{_f(base_y)} '
            f'Q{_f(cx + w / 2)},{_f(base_y)} {_f(cx + w / 2)},{_f(base_y - h * 0.18)} '
            f'Q{_f(cx + w / 2)},{_f(base_y - h * 0.42)} {_f(cx)},{_f(base_y - h)} Z" '
            f'fill="{fill}"/>')


def column(x: float, y: float, w: float, h: float, fill: str,
           dur: float = 9.0, begin: float = 0.0) -> str:
    """A lathed clay column with a lit cap and a shadowed foot."""
    fill = col(fill)
    cap = min(w / 2.6, h / 5.0)
    body = "".join([
        cast_shadow(x + w / 2 + 8, y + h + 3, w * 0.72, 8, "cast3"),
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(min(w, h) / 3)}" fill="{fill}"/>',
        f'<rect x="{_f(x + w * 0.12)}" y="{_f(y + cap)}" width="{_f(w * 0.2)}" '
        f'height="{_f(h - cap * 2)}" rx="{_f(w * 0.1)}" fill="{tint(fill, 0.24)}"/>',
        f'<ellipse cx="{_f(x + w / 2)}" cy="{_f(y)}" rx="{_f(w / 2)}" '
        f'ry="{_f(cap)}" fill="{tint(fill, 0.30)}"/>',
        f'<rect x="{_f(x)}" y="{_f(y + h - cap)}" width="{_f(w)}" '
        f'height="{_f(cap)}" fill="{tint(fill, -0.18)}"/>',
    ])
    return f'<g>{body}{hover_loop(4.0, dur, begin)}</g>'


def ball(cx: float, cy: float, r: float, fill: str, dur: float = 8.0,
         begin: float = 0.0) -> str:
    """A matte sphere with volume, bobbing on a closed loop."""
    fill = col(fill)
    body = (f'<circle cx="{cx}" cy="{cy}" r="{_f(r)}" fill="{fill}"/>'
            f'<circle cx="{_f(cx - r * 0.32)}" cy="{_f(cy - r * 0.36)}" '
            f'r="{_f(r * 0.44)}" fill="{tint(fill, 0.26)}" opacity="0.6"/>'
            f'<circle cx="{_f(cx + r * 0.3)}" cy="{_f(cy + r * 0.34)}" '
            f'r="{_f(r * 0.3)}" fill="{tint(fill, -0.24)}" opacity="0.5"/>')
    return f'<g>{body}{hover_loop(5.0, dur, begin)}</g>'


# ---------------------------------------------------------------------------
# text and panels
# ---------------------------------------------------------------------------
def label(x: float, y: float, text: str, fill: str, size: int = 17,
          anchor: str = "start", weight: str = "700",
          spacing: float = 0.6) -> str:
    fill = col(fill)
    return (f'<text x="{_f(x)}" y="{_f(y)}" '
            f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{spacing}" fill="{fill}" '
            f'text-anchor="{anchor}">{esc(text)}</text>')


def plaque(x: float, y: float, w: float, h: float, fill: str,
           r: float = 14) -> str:
    fill = col(fill)
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
            f'rx="{_f(r)}" fill="{fill}" opacity="0.95"/>')


def screen(x: float, y: float, w: float, h: float, fill: str, gid: str,
           r: float = 12) -> str:
    """A recessed panel: dark well, inner shadow edge, warm interior lamp."""
    fill = col(fill)
    return "".join([
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(r)}" fill="{fill}"/>',
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="6" '
        f'rx="3" fill="{tint(fill, -0.4)}" opacity="0.8"/>',
        f'<rect x="{_f(x)}" y="{_f(y + h - 5)}" width="{_f(w)}" height="5" '
        f'fill="{tint(fill, 0.18)}" opacity="0.5"/>',
        f'<circle cx="{_f(x + w - 62)}" cy="{_f(y + 44)}" r="72" '
        f'fill="url(#lampg{gid})"/>',
    ])

# ---------------------------------------------------------------------------
# information slab -- the legibility mechanism
# ---------------------------------------------------------------------------
def slab(x: float, y: float, w: float, h: float, fill: str,
         light: bool = False, r: float = 14, shadow: bool = True) -> str:
    """An opaque clay card that carries text.

    Fully opaque by construction, with a lit top lip and a shaded right lip so it
    still reads as a sculpted object rather than as a flat sticker. Everything a
    reader must understand lives on one of these, so the scenery behind it can be
    as busy as it likes without ever competing with the data.
    """
    fill = col(fill)
    lip = C.tint(fill, -0.30) if light else C.tint(fill, 0.22)
    out = []
    if shadow:
        out.append(cast_shadow(x + w / 2 + 10, y + h + 6, w * 0.56, 14, "castsl"))
    out.append(
        f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
        f'rx="{_f(r)}" fill="{fill}"/>')
    # Top lip: a rounded strip hugging the upper edge.
    out.append(
        f'<path d="M{_f(x + r)},{_f(y)} L{_f(x + w - r)},{_f(y)} '
        f'Q{_f(x + w)},{_f(y)} {_f(x + w)},{_f(y + r)} '
        f'L{_f(x + w)},{_f(y + r * 0.42)} '
        f'L{_f(x)},{_f(y + r * 0.42)} L{_f(x)},{_f(y + r)} '
        f'Q{_f(x)},{_f(y)} {_f(x + r)},{_f(y)} Z" fill="{lip}" opacity="0.9"/>')
    # Right lip.
    out.append(
        f'<path d="M{_f(x + w - r * 0.42)},{_f(y)} '
        f'Q{_f(x + w)},{_f(y)} {_f(x + w)},{_f(y + r)} '
        f'L{_f(x + w)},{_f(y + h - r)} '
        f'Q{_f(x + w)},{_f(y + h)} {_f(x + w - r)},{_f(y + h)} '
        f'L{_f(x + w - r * 0.42)},{_f(y + h)} Z" '
        f'fill="{C.tint(fill, -0.24) if not light else C.tint(fill, 0.20)}" '
        f'opacity="0.85"/>')
    return "".join(out)


def slab_ink(light: bool = False) -> str:
    """Slab text colour, chosen from the far end of the palette."""
    return P["cream"] if not light else P["dusk_deep"]


def slab_sub(light: bool = False) -> str:
    """Secondary text.

    On a dark slab the secondary colour is the same cream as the primary: only
    pure cream clears 4.5:1 against a warm slab that is dark enough to carry
    cream text, so hierarchy comes from size and weight rather than from a dimmer
    colour. On light slabs there is room for a genuinely darker second level.
    """
    if not light:
        return P["cream"]
    return C.tint("clay_red", -0.44)


# Slab fills. Measured, not chosen by eye: cream ink only clears 4.5:1 against
# a slab at or below this darkness, so the warm fills are pushed down until they
# qualify. The scene stays bright and warm; the slabs read as dark signage on it.
SLAB_DARK = {
    "title": C.tint("terracotta", -0.28),
    "data": C.tint("clay_red", -0.10),
    "tile": C.tint("ember", -0.30),
    "foot": P["dusk_deep"],
}
SLAB_LIGHT = {
    "title": P["cream"],
    "data": P["beige"],
    "tile": P["sand"],
    "foot": P["cream"],
}


# ---------------------------------------------------------------------------
# endless-loop durations
# ---------------------------------------------------------------------------
# Coprime periods. If every track ran on a shared duration the whole plate would
# visibly repeat every few seconds; with coprime periods the composite period is
# the product, so a plate effectively never repeats. All values start and end on
# the same value, so every track is individually seamless.
LOOP = (7.0, 9.0, 11.0, 13.0, 17.0, 19.0, 23.0)


def loop_dur(i: int, scale: float = 1.0) -> float:
    """A coprime loop length for track i."""
    return LOOP[i % len(LOOP)] * scale


def loop_begin(i: int, scale: float = 1.0) -> float:
    """A stagger that is also a fraction of a different period, so the phases
    do not re-align on any short cycle."""
    return (i * 2.718) % loop_dur(i, scale)
