"""Nature and retro-technology primitives for the profile plates.

Two families, drawn in the same clay language so they look cast by the same
hands: desert forms (mesa, ridge, boulder, agave, water, night sky) and 1970s-80s
machines (CRT, keyboard, floppy, rack, oscilloscope, satellite, rover, robot).

Everything returns SVG fragments and takes palette names, never raw hex, so an
unresolved name can never reach a paint attribute.
"""

from __future__ import annotations

from clay import _f, alpha, col, esc, tint
from clay import PALETTE as P

from clay3d import ao, block, cast_shadow, _mix_hex

# ---------------------------------------------------------------------------
# nature
# ---------------------------------------------------------------------------
def night_sky(w: int, h: int, gid: str) -> str:
    """Deep dusk with a scatter of stars and a moon, for the twilight plate."""
    out = [f'<linearGradient id="nsky{gid}" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="{P["dusk_deep"]}"/>'
           f'<stop offset="0.7" stop-color="{tint(P["dusk_mid"], -0.10)}"/>'
           f'<stop offset="1" stop-color="{tint(P["dusk_soft"], 0.20)}"/>'
           f'</linearGradient>'
           f'<rect width="{w}" height="{h}" fill="url(#nsky{gid})"/>']
    # Deterministic star field: fixed offsets, no RNG.
    for i in range(46):
        x = (i * 173) % w
        y = (i * 97) % int(h * 0.62)
        r = 1.1 + ((i * 7) % 5) * 0.32
        out.append(f'<circle cx="{x}" cy="{y}" r="{_f(r)}" '
                   f'fill="{P["cream"]}" opacity="{0.28 + ((i * 13) % 6) * 0.1:.2f}"/>')
    mx, my, mr = w - 150, 96, 34
    out.append(f'<g>'
               f'<circle cx="{mx}" cy="{my}" r="{_f(mr * 2.1)}" '
               f'fill="{alpha(P["cream"], 0.13)}"/>'
               f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="{P["cream"]}"/>'
               f'<circle cx="{mx + mr * 0.34}" cy="{my - mr * 0.2}" '
               f'r="{_f(mr * 0.24)}" fill="{tint("beige", -0.06)}" opacity="0.5"/>'
               f'<circle cx="{mx - mr * 0.3}" cy="{my + mr * 0.34}" '
               f'r="{_f(mr * 0.18)}" fill="{tint("beige", -0.04)}" opacity="0.4"/>'
               f'</g>')
    return "".join(out)


def ridges(w: int, horizon: float, seed: int = 0) -> str:
    """Two soft ridge layers for aerial distance. Never above 45% opacity."""
    out = []
    layers = ((62, tint(P["dusk_soft"], 0.14), 0.40), (34, P["shadow"], 0.20))
    for li, (lift, tone, a) in enumerate(layers):
        base = horizon - lift
        rh = 30 + li * 6
        peaks = [0.55, 1.0, 0.72, 0.9, 0.48]
        pts = [f"0,{_f(base)}"]
        for i, pk in enumerate(peaks):
            x0 = w * i / len(peaks)
            x1 = w * (i + 1) / len(peaks)
            pts += [f"{_f(x0)},{_f(base - rh * pk * 0.5)}",
                    f"{_f((x0 + x1) / 2)},{_f(base - rh * pk)}",
                    f"{_f(x1)},{_f(base - rh * pk * 0.5)}"]
        pts.append(f"{w},{_f(base)}")
        out.append(f'<polygon points="{" ".join(pts)}" fill="{tone}" opacity="{a}"/>')
    return "".join(out)


def boulder(cx: float, base_y: float, w: float, h: float, fill: str) -> str:
    """A rounded scrub boulder, the desert equivalent of a chassis."""
    fill = col(fill)
    return "".join([
        cast_shadow(cx + w * 0.12, base_y + 2, w * 0.56, 7, "castb"),
        f'<path d="M{_f(cx - w / 2)},{_f(base_y)} '
        f'Q{_f(cx - w / 2)},{_f(base_y - h)} {_f(cx - w * 0.22)},{_f(base_y - h)} '
        f'L{_f(cx + w * 0.24)},{_f(base_y - h)} '
        f'Q{_f(cx + w / 2)},{_f(base_y - h)} {_f(cx + w / 2)},{_f(base_y)} Z" '
        f'fill="{fill}"/>',
        f'<path d="M{_f(cx - w * 0.22)},{_f(base_y - h)} '
        f'L{_f(cx + w * 0.24)},{_f(base_y - h)} '
        f'L{_f(cx + w * 0.1)},{_f(base_y - h * 0.55)} '
        f'L{_f(cx - w * 0.14)},{_f(base_y - h * 0.5)} Z" '
        f'fill="{tint(fill, 0.22)}"/>',
    ])


def agave(cx: float, base_y: float, w: float, h: float, fill: str) -> str:
    """Agave rosette: fat clay blades, a desert shrub in the same family."""
    fill = col(fill)
    out = []
    for i, (dx, sc) in enumerate(((-0.42, 0.8), (-0.22, 1.0), (0.0, 1.12),
                                  (0.24, 1.0), (0.44, 0.78))):
        bx = cx + w * dx
        bw = w * 0.2 * sc
        bh = h * sc
        out.append(
            f'<path d="M{_f(bx)},{_f(base_y)} '
            f'Q{_f(bx - bw)},{_f(base_y - bh * 0.7)} {_f(bx - bw * 0.2)},{_f(base_y - bh)} '
            f'Q{_f(bx + bw * 0.2)},{_f(base_y - bh)} {_f(bx + bw)},{_f(base_y - bh * 0.7)} '
            f'Q{_f(bx + bw * 0.6)},{_f(base_y)} {_f(bx)},{_f(base_y)} Z" '
            f'fill="{tint(fill, 0.06 * i)}"/>')
    return cast_shadow(cx, base_y + 2, w * 0.5, 6, "castb") + "".join(out)


def water(x: float, y: float, w: float, h: float, gid: str) -> str:
    """A still pool: flat turquoise with a few blocky highlight bars."""
    out = [f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
           f'rx="{_f(h * 0.22)}" fill="{tint(P["turquoise"], -0.14)}"/>']
    for i, k in enumerate((0.22, 0.5, 0.74)):
        bw = w * (0.42 - i * 0.09)
        out.append(f'<rect x="{_f(x + w * 0.16 + i * w * 0.13)}" '
                   f'y="{_f(y + h * k)}" width="{_f(bw)}" height="{_f(h * 0.07)}" '
                   f'rx="3" fill="{P["cream"]}" opacity="{0.34 - i * 0.07:.2f}"/>')
    return "".join(out)


def drift_sand(w: int, y: float, h: float) -> str:
    """A thin dust wisp across the ground plane."""
    return (f'<rect x="0" y="{_f(y)}" width="{w}" height="{_f(h)}" '
            f'fill="{alpha(P["sand"], 0.22)}" rx="{_f(h / 2)}"/>')


# ---------------------------------------------------------------------------
# retro technology
# ---------------------------------------------------------------------------
def crt(x: float, y: float, w: float, h: float, bezel: str, screen: str,
        gid: str, lamp: bool = True) -> str:
    """A chunky CRT: bezel, recessed screen, vents, two knobs, a stand.

    This is the signature machine of the system, so it carries real volume:
    chamfered bezel, an inner lip catching the light, and a warm screen.
    """
    bezel = col(bezel)
    screen = col(screen)
    sx, sy = x + w * 0.11, y + h * 0.11
    sw, sh = w * 0.78, h * 0.66
    knobs = "".join(
        f'<circle cx="{_f(x + w * (0.845 + i * 0.075))}" cy="{_f(y + h * 0.845)}" '
        f'r="{_f(w * 0.035)}" fill="{tint(bezel, -0.30)}"/>'
        f'<circle cx="{_f(x + w * (0.845 + i * 0.075))}" cy="{_f(y + h * 0.845)}" '
        f'r="{_f(w * 0.035)}" fill="none" stroke="{tint(bezel, 0.24)}" '
        f'stroke-width="2"/>'
        for i in range(2))
    vents = "".join(
        f'<rect x="{_f(x + w * (0.13 + i * 0.052))}" y="{_f(y + h * 0.845)}" '
        f'width="{_f(w * 0.03)}" height="{_f(h * 0.075)}" '
        f'fill="{tint(bezel, -0.26)}"/>' for i in range(8))
    lamp_xml = (f'<circle cx="{_f(x + w * 0.955)}" cy="{_f(y + h * 0.845)}" '
                f'r="{_f(w * 0.022)}" fill="{P["sun"]}"/>') if lamp else ""
    return "".join([
        cast_shadow(x + w / 2 + 8, y + h + 4, w * 0.6, 8, gid),
        # stand
        f'<rect x="{_f(x + w * 0.34)}" y="{_f(y + h)}" width="{_f(w * 0.32)}" '
        f'height="{_f(h * 0.07)}" fill="{tint(bezel, -0.16)}"/>',
        f'<rect x="{_f(x + w * 0.26)}" y="{_f(y + h + h * 0.06)}" '
        f'width="{_f(w * 0.48)}" height="{_f(h * 0.05)}" rx="3" '
        f'fill="{tint(bezel, -0.24)}"/>',
        block(x, y, w, h, w * 0.09, bezel, r=w * 0.09, gid=None),
        # inner lip catching the light
        f'<rect x="{_f(sx - 4)}" y="{_f(sy - 4)}" width="{_f(sw + 8)}" '
        f'height="{_f(sh + 8)}" rx="{_f(sh * 0.14)}" fill="{tint(bezel, -0.34)}"/>',
        f'<rect x="{_f(sx)}" y="{_f(sy)}" width="{_f(sw)}" height="{_f(sh)}" '
        f'rx="{_f(sh * 0.11)}" fill="{screen}"/>',
        f'<circle cx="{_f(sx + sw - 26)}" cy="{_f(sy + 26)}" r="{_f(sh * 0.5)}" '
        f'fill="url(#lampg{gid})"/>' if lamp else "",
        f'<rect x="{_f(sx)}" y="{_f(sy)}" width="{_f(sw)}" height="4" rx="2" '
        f'fill="{tint(screen, -0.42)}" opacity="0.7"/>',
        vents, knobs, lamp_xml,
    ])


def keyboard(x: float, y: float, w: float, h: float, fill: str) -> str:
    """A thick keyboard of square keycaps. Square is what dates the era."""
    fill = col(fill)
    out = [cast_shadow(x + w / 2 + 4, y + h + 2, w * 0.54, 5, "castk"),
           block(x, y, w, h, w * 0.05, fill, r=6, gid=None)]
    cols, rows = 12, 4
    kw = w * 0.068
    for r in range(rows):
        for c in range(cols):
            kx = x + w * 0.055 + c * kw * 1.22
            ky = y + h * 0.14 + r * (h * 0.185)
            if kx + kw > x + w * 0.95:
                continue
            out.append(f'<rect x="{_f(kx)}" y="{_f(ky)}" width="{_f(kw)}" '
                       f'height="{_f(h * 0.14)}" rx="2" '
                       f'fill="{tint(fill, 0.20 if r == 0 else 0.08)}"/>')
    return "".join(out)


def floppy(x: float, y: float, w: float, h: float, fill: str,
           label: str = "", ink: str = "cream") -> str:
    """A chunky 3.5-inch floppy: shutter, label, chamfered shell."""
    fill = col(fill)
    out = [block(x, y, w, h, w * 0.07, fill, r=4, gid=None)]
    out.append(f'<rect x="{_f(x + w * 0.58)}" y="{_f(y + h * 0.06)}" '
               f'width="{_f(w * 0.32)}" height="{_f(h * 0.34)}" '
               f'fill="{tint("dusk_mid", 0.10)}"/>')
    out.append(f'<rect x="{_f(x + w * 0.08)}" y="{_f(y + h * 0.50)}" '
               f'width="{_f(w * 0.84)}" height="{_f(h * 0.40)}" '
               f'fill="{tint(P["cream"], 0.04)}"/>')
    if label:
        out.append(f'<text x="{_f(x + w * 0.12)}" y="{_f(y + h * 0.78)}" '
                   f'font-family="Verdana,DejaVu Sans,sans-serif" '
                   f'font-size="{_f(max(7, h * 0.22))}" font-weight="700" '
                   f'fill="{P["clay_red"]}">{esc(label[:8])}</text>')
    return "".join(out)


def rack(x: float, y: float, w: float, h: float, units: int, fill: str,
         gid: str = "castr") -> str:
    """A server rack: stacked units, vent slots and an indicator lamp each."""
    fill = col(fill)
    out = [cast_shadow(x + w / 2 + 5, y + h + 3, w * 0.56, 7, gid),
           f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" '
           f'rx="6" fill="{fill}"/>']
    uh = h / max(units, 1)
    for i in range(units):
        uy = y + i * uh + uh * 0.10
        out.append(f'<rect x="{_f(x + w * 0.06)}" y="{_f(uy)}" '
                   f'width="{_f(w * 0.88)}" height="{_f(uh * 0.80)}" rx="3" '
                   f'fill="{tint(fill, 0.12 if i % 2 else -0.08)}"/>')
        for k in range(6):
            out.append(f'<rect x="{_f(x + w * 0.10 + k * w * 0.052)}" '
                       f'y="{_f(uy + uh * 0.30)}" width="{_f(w * 0.032)}" '
                       f'height="{_f(uh * 0.24)}" fill="{tint(fill, -0.34)}"/>')
        out.append(f'<circle cx="{_f(x + w * 0.86)}" cy="{_f(uy + uh * 0.40)}" '
                   f'r="{_f(min(w, uh) * 0.11)}" '
                   f'fill="{P["sun"] if i % 3 else P["cactus"]}"/>')
    return "".join(out)


def scope(x: float, y: float, w: float, h: float, fill: str, gid: str) -> str:
    """An oscilloscope with a blocky trace: the retro 'signal' motif."""
    fill = col(fill)
    sx, sy = x + w * 0.1, y + h * 0.12
    sw, sh = w * 0.8, h * 0.6
    trace = []
    for i in range(9):
        tx = sx + sw * (i / 8)
        ty = sy + sh * (0.5 + (0.30 if i % 3 == 1 else -0.22) * (1 if i % 2 else 0.4))
        trace.append(f"{'M' if i == 0 else 'L'}{_f(tx)},{_f(ty)}")
    return "".join([
        cast_shadow(x + w / 2 + 5, y + h + 3, w * 0.55, 6, gid),
        block(x, y, w, h, w * 0.07, fill, r=8, gid=None),
        f'<rect x="{_f(sx)}" y="{_f(sy)}" width="{_f(sw)}" height="{_f(sh)}" '
        f'fill="{P["dusk_deep"]}"/>',
        # grid
        "".join(f'<line x1="{_f(sx + sw * i / 4)}" y1="{_f(sy)}" '
                f'x2="{_f(sx + sw * i / 4)}" y2="{_f(sy + sh)}" '
                f'stroke="{alpha(P["turquoise"], 0.24)}" stroke-width="1"/>'
                for i in range(5)),
        "".join(f'<line x1="{_f(sx)}" y1="{_f(sy + sh * i / 3)}" '
                f'x2="{_f(sx + sw)}" y2="{_f(sy + sh * i / 3)}" '
                f'stroke="{alpha(P["turquoise"], 0.24)}" stroke-width="1"/>'
                for i in range(4)),
        f'<path d="{" ".join(trace)}" fill="none" stroke="{P["sun"]}" '
        f'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>',
        f'<circle cx="{_f(x + w * 0.86)}" cy="{_f(y + h * 0.86)}" '
        f'r="{_f(w * 0.055)}" fill="{tint(fill, -0.26)}"/>',
        f'<circle cx="{_f(x + w * 0.86)}" cy="{_f(y + h * 0.86)}" '
        f'r="{_f(w * 0.055)}" fill="none" stroke="{P["cream"]}" '
        f'stroke-width="2"/>',
    ])


def satellite(cx: float, cy: float, s: float, body: str, panel: str) -> str:
    """A blocky satellite with solar wings, tracking the same sun as the scene."""
    body = col(body)
    panel = col(panel)
    return "".join([
        f'<rect x="{_f(cx - s * 0.34)}" y="{_f(cy - s * 0.5)}" width="{_f(s * 0.68)}" '
        f'height="{_f(s)}" rx="{_f(s * 0.12)}" fill="{body}"/>',
        f'<rect x="{_f(cx - s * 0.34)}" y="{_f(cy - s * 0.5)}" width="{_f(s * 0.68)}" '
        f'height="{_f(s * 0.34)}" rx="{_f(s * 0.1)}" fill="{tint(body, 0.24)}"/>',
        "".join(
            f'<rect x="{_f(cx + sx * s)}" y="{_f(cy - s * 0.30)}" '
            f'width="{_f(s * 0.46)}" height="{_f(s * 0.60)}" rx="2" '
            f'fill="{panel}"/>'
            f'<rect x="{_f(cx + sx * s)}" y="{_f(cy - s * 0.30)}" '
            f'width="{_f(s * 0.46)}" height="{_f(s * 0.60)}" rx="2" '
            f'fill="none" stroke="{tint(panel, -0.34)}" stroke-width="1.5"/>'
            for sx in (-1.10, 0.64)),
        f'<path d="M{_f(cx)},{_f(cy - s * 0.5)} L{_f(cx - s * 0.1)},{_f(cy - s * 0.95)}" '
        f'stroke="{tint(body, 0.3)}" stroke-width="{_f(s * 0.06)}" '
        f'stroke-linecap="round"/>',
        f'<circle cx="{_f(cx - s * 0.1)}" cy="{_f(cy - s * 0.98)}" '
        f'r="{_f(s * 0.09)}" fill="{P["sun"]}"/>',
    ])


def rover(cx: float, base_y: float, w: float, h: float, fill: str,
          dish: bool = True) -> str:
    """A six-wheel blocky rover with an antenna, parked in the desert."""
    fill = col(fill)
    body_y = base_y - h * 0.34
    wheels = "".join(
        f'<rect x="{_f(cx + w * (0.04 + i * 0.34))}" y="{_f(base_y - h * 0.16)}" '
        f'width="{_f(w * 0.16)}" height="{_f(h * 0.16)}" rx="4" '
        f'fill="{tint("dusk_deep", 0.14)}"/>' for i in range(3))
    return "".join([
        cast_shadow(cx + w * 0.08, base_y + 2, w * 0.56, 7, "castv"),
        wheels,
        f'<rect x="{_f(cx + w * 0.06)}" y="{_f(body_y)}" width="{_f(w * 0.88)}" '
        f'height="{_f(h * 0.34)}" rx="{_f(h * 0.10)}" fill="{fill}"/>',
        f'<rect x="{_f(cx + w * 0.06)}" y="{_f(body_y)}" width="{_f(w * 0.88)}" '
        f'height="{_f(h * 0.14)}" rx="{_f(h * 0.06)}" fill="{tint(fill, 0.24)}"/>',
        f'<path d="M{_f(cx + w * 0.70)},{_f(body_y)} L{_f(cx + w * 0.80)},'
        f'{_f(body_y - h * 0.62)}" stroke="{tint(fill, -0.24)}" '
        f'stroke-width="{_f(h * 0.05)}" stroke-linecap="round"/>',
        (f'<circle cx="{_f(cx + w * 0.80)}" cy="{_f(body_y - h * 0.64)}" '
         f'r="{_f(h * 0.09)}" fill="{P["sun"]}"/>' if dish else ""),
        f'<rect x="{_f(cx + w * 0.16)}" y="{_f(body_y + h * 0.09)}" '
        f'width="{_f(w * 0.16)}" height="{_f(h * 0.10)}" rx="2" '
        f'fill="{tint("dusk_deep", 0.2)}"/>',
    ])


def robot(cx: float, base_y: float, s: float, fill: str) -> str:
    """A small box robot: antenna, two eye-lamps, stubby arms."""
    fill = col(fill)
    return "".join([
        cast_shadow(cx + s * 0.2, base_y + 2, s * 0.55, 5, "castb"),
        f'<rect x="{_f(cx - s * 0.12)}" y="{_f(base_y - s * 1.0)}" '
        f'width="{_f(s * 0.24)}" height="{_f(s * 0.2)}" '
        f'fill="{tint(fill, -0.22)}"/>',
        f'<circle cx="{_f(cx)}" cy="{_f(base_y - s * 1.12)}" r="{_f(s * 0.09)}" '
        f'fill="{P["sun"]}"/>',
        block(cx - s * 0.42, base_y - s * 0.82, s * 0.84, s * 0.56, s * 0.16,
              fill, r=s * 0.10, gid=None),
        f'<rect x="{_f(cx - s * 0.26)}" y="{_f(base_y - s * 0.68)}" '
        f'width="{_f(s * 0.16)}" height="{_f(s * 0.12)}" rx="2" '
        f'fill="{P["dusk_deep"]}"/>',
        f'<rect x="{_f(cx + s * 0.10)}" y="{_f(base_y - s * 0.68)}" '
        f'width="{_f(s * 0.16)}" height="{_f(s * 0.12)}" rx="2" '
        f'fill="{P["dusk_deep"]}"/>',
        f'<circle cx="{_f(cx - s * 0.18)}" cy="{_f(base_y - s * 0.62)}" '
        f'r="{_f(s * 0.045)}" fill="{P["sun"]}"/>',
        f'<circle cx="{_f(cx + s * 0.18)}" cy="{_f(base_y - s * 0.62)}" '
        f'r="{_f(s * 0.045)}" fill="{P["sun"]}"/>',
        f'<rect x="{_f(cx - s * 0.58)}" y="{_f(base_y - s * 0.62)}" '
        f'width="{_f(s * 0.14)}" height="{_f(s * 0.08)}" rx="2" '
        f'fill="{tint(fill, -0.20)}"/>',
        f'<rect x="{_f(cx + s * 0.44)}" y="{_f(base_y - s * 0.62)}" '
        f'width="{_f(s * 0.14)}" height="{_f(s * 0.08)}" rx="2" '
        f'fill="{tint(fill, -0.20)}"/>',
    ])


def punch_cards(x: float, y: float, w: float, h: float, count: int,
                fill: str) -> str:
    """Punch cards stacked into an adobe brick wall."""
    fill = col(fill)
    out = []
    rows = max(count // 4, 1)
    cw = w / 4
    ch = h / rows
    for i in range(min(count, 16)):
        cx = x + (i % 4) * cw
        cy = y + (i // 4) * ch
        out.append(f'<rect x="{_f(cx + 1)}" y="{_f(cy + 1)}" '
                   f'width="{_f(cw - 2)}" height="{_f(ch - 2)}" rx="2" '
                   f'fill="{tint(fill, 0.10 * (i % 3))}"/>')
        out.append(f'<rect x="{_f(cx + cw * 0.16)}" y="{_f(cy + ch * 0.28)}" '
                   f'width="{_f(cw * 0.2)}" height="{_f(ch * 0.16)}" rx="1" '
                   f'fill="{tint(fill, -0.40)}"/>')
    return "".join(out)


def pixel_grid(w: int, y: float, h: float, cols: int, rows: int,
               fill: str) -> str:
    """A blocky pixel grid fading into the dunes at the horizon."""
    fill = col(fill)
    out = []
    for r in range(rows):
        for c in range(cols):
            a = 0.10 + ((c * 5 + r * 3) % 7) * 0.03
            if r > rows * 0.6:
                a *= 0.5
            out.append(f'<rect x="{_f(w * 0.06 + c * w * 0.88 / cols)}" '
                       f'y="{_f(y + r * h / rows)}" '
                       f'width="{_f(w * 0.88 / cols * 0.72)}" '
                       f'height="{_f(h / rows * 0.7)}" '
                       f'fill="{fill}" opacity="{a:.2f}"/>')
    return "".join(out)