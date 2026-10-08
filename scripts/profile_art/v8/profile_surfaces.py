"""The profile plates: desert scenery behind, information on solid slabs.

Generated from MASTER_PROMPT.md. Layer order is fixed and enforced:

    LAYER 3  opaque clay slab      every string in the plate lives here
    LAYER 2  type                  cream on a dark slab, dusk on a light slab
    LAYER 1  furniture             the figures and labels that carry the meaning
    LAYER 0  scenery               nature + retro machines, low contrast

The 136 per-repository surfaces are produced by clay_renderers.py and are not
touched by this module.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay as C  # noqa: E402
import clay3d as X  # noqa: E402
import naturetech as N  # noqa: E402
from clay import _f  # noqa: E402

W, H = 900, 470
FOOT_Y = 424
HORIZON = 356
PAL = C.CLAY_PALETTES["mesa_terracotta"]

ROLE_TITLE = {
    "hero": "identity", "terminal": "how it is operated",
    "architecture": "how it is built", "state_machine": "how it behaves",
    "data_flow": "how data moves", "component_map": "how it is composed",
    "build": "how it is verified", "workflow": "how it is used",
    "domain": "the problem it addresses", "footer": "identity object",
}

# Plate identities from MASTER_PROMPT section 8: each one a different setting so
# the profile does not read as one template ten times.
# Slab fills per variant. Previously the light variant kept the dark clay fill
# and only swapped the ink to a dark colour, so light plates were dark-on-dark.
# The fill has to change with the ink, always from the opposite end of the
# palette.
SLAB = {False: X.SLAB_DARK, True: X.SLAB_LIGHT}


PLATE = {
    "hero": ("Mesa settlement at golden hour, a CRT planted on the terrace", "identity"),
    "terminal": ("Dusk over a scrub ridge, a CRT console and keyboard", "entry points"),
    "architecture": ("Terraced mesa with cacti, a stacked server rack", "module roots"),
    "data_flow": ("A dry wash road, packets travelling as lit blocks", "routes"),
    "state_machine": ("Twilight, stars and moon, tokens crossing a gate", "primitives"),
    "component_map": ("Pale morning, a wall of drives in long shadow", "composition"),
    "build": ("A quarry of boulders beside a lit instrument bay", "build and tests"),
    "workflow": ("Canyon steps under a low sun, stepped servers", "workflow"),
    "domain": ("A water pool at dusk with a rover parked beside it", "domain"),
}


def strip_animations(body: str) -> str:
    import re
    body = re.sub(r"<animate[^>]*/>", "", body)
    return re.sub(r"<animateTransform[^>]*/>", "", body)


def _doc(body: str, slot: str, d: dict) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{C.esc(d["canonical_name"])} - {ROLE_TITLE.get(slot, slot)}">'
            f'{body}</svg>')


# ---------------------------------------------------------------------------
# layout helpers -- all text is emitted inside a slab
# ---------------------------------------------------------------------------
def title_slab(d: dict, light: bool, note: str = "") -> str:
    """The identity slab: repository name, plate role, and an optional figure."""
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    x, y, w, h = 40, 34, 360, 74
    o = [X.slab(x, y, w, h, SLAB[light]["title"], light=light, r=12)]
    o.append(X.label(x + 20, y + 40, d["canonical_name"][:22], ink, 25))
    o.append(X.label(x + 21, y + 62, PLATE.get(_slot, ("", ""))[1].upper(), sub, 13))
    if note:
        o.append(X.label(x + w - 18, y + 62, note[:18], sub, 13, anchor="end"))
    return "".join(o)


def data_slab(rows: list[tuple[str, str]], light: bool, x: float, y: float,
              w: float, h: float, heading: str = "") -> str:
    """A one-message slab: a heading and label/figure rows that fit inside it.

    The row count is derived from the slab height. Trimming by hand clipped the
    last row out of the card, which is the one thing a data plate must never do.
    """
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = [X.slab(x, y, w, h, SLAB[light]["data"], light=light, r=14)]
    top = y + 30
    if heading:
        o.append(X.label(x + 20, top, heading.upper(), sub, 13))
        top += 30
    # Leave 14px of breathing room under the final baseline.
    room = int((y + h - 14 - top) // 30) + 1
    for i, (label, value) in enumerate(rows[:max(room, 0)]):
        ry = top + i * 30
        o.append(X.label(x + 20, ry, label[:24], sub, 14))
        o.append(X.label(x + w - 20, ry, value[:14], ink, 17, anchor="end"))
    return "".join(o)


def figure_tiles(items: list[tuple[str, str]], light: bool, x: float, y: float,
                 pitch: int = 150, tile: int = 134, tile_h: int = 78) -> str:
    """Headline figures get their own tiles, so no number is ever lost in a row."""
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = []
    for i, (value, label) in enumerate(items[:3]):
        tx = x + i * pitch
        o.append(X.slab(tx, y, tile, tile_h, SLAB[light]["tile"], light=light, r=12))
        o.append(X.label(tx + 14, y + 36, value[:9], ink, 22))
        o.append(X.label(tx + 15, y + 60, label[:16], sub, 12))
    return "".join(o)


def footer_slab(d: dict, light: bool) -> str:
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = [X.slab(0, FOOT_Y, W, H - FOOT_Y, SLAB[light]["foot"], light=light,
                r=0, shadow=False)]
    o.append(X.label(40, FOOT_Y + 30,
                     f"DUNG30N5 x NOAERTH  /  {d['project_category'].replace('_', ' ').title()}",
                     ink, 14))
    o.append(X.label(860, FOOT_Y + 30, f"{d['status']}  -  evidence {d['confidence']}",
                     sub, 13, anchor="end"))
    return "".join(o)


def ground(light: bool, g: str) -> str:
    """Sand plane with converging paver seams."""
    o = [f'<rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" '
         f'fill="url(#floor{g})"/>']
    vx = W * 0.5
    for k in range(-9, 10):
        o.append(f'<path d="M{_f(vx)},{_f(HORIZON)} L{_f(vx + k * 190)},{H}" '
                 f'stroke="{C.alpha(C.PALETTE["beige"], 0.20)}" stroke-width="2"/>')
    y, step = HORIZON + 5, 6.0
    while y < H:
        o.append(f'<rect x="0" y="{_f(y)}" width="{W}" height="{_f(step * 0.30)}" '
                 f'fill="{C.alpha(C.PALETTE["beige"], 0.40)}"/>')
        y += step
        step *= 1.36
    return "".join(o)


_slot = "hero"


def _scene(light: bool, g: str, night: bool = False) -> str:
    o = [X.defs(g, PAL, light)]
    o.append(N.night_sky(W, H, g) if night else
             f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>')
    if not night:
        sx, sy, sr = W - 158, 92, 40
        o.append(f'<g><circle cx="{sx}" cy="{sy}" r="{_f(sr * 2.5)}" '
                 f'fill="url(#halo{g})">{X.halo_loop(sr * 2.2, sr * 2.8, 15)}</circle>'
                 f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{C.PALETTE["sun"]}"/>'
                 f'</g>')
        o.append(N.cloud(556, 68, 40, 26) if hasattr(N, "cloud") else "")
    o.append(f'<rect x="0" y="{_f(HORIZON - 40)}" width="{W}" height="40" '
             f'fill="{C.alpha(C.PALETTE["peach"], 0.15)}"/>')
    o.append(N.ridges(W, HORIZON))
    o.append(ground(light, g))
    return "".join(o)


# ---------------------------------------------------------------------------
# the ten plates
# ---------------------------------------------------------------------------
def render_hero(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "hero"
    g = "h"
    o = [_scene(light, g)]
    o.append(X.cast_shadow(300, HORIZON + 8, 190, 18, g, skew=-6))
    o.append(X.mesa(96, 216, 214, 140, 4, PAL["mass"], d=22))
    # a CRT planted on the terrace, same scale as a cactus
    o.append(f'<g>{N.crt(300, 252, 118, 100, "coral", "dusk_deep", g)}'
             f'{X.hover_loop(4.0, 9.5, 0.4)}</g>')
    o.append(X.gateway(438, 226, 118, 130, PAL["alt"], g))
    o.append(N.boulder(614, HORIZON, 76, 34, "beige"))
    o.append(N.agave(676, HORIZON, 54, 74, "sage"))
    o.append(X.conifer(770, HORIZON, 56, 132, PAL["cool"], 13, 2))
    o.append(title_slab(d, light, f"{d['note_routes']} routes"))
    o.append(figure_tiles(d["tiles"], light, 40, 128))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "hero", d)


def render_terminal(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "terminal"
    g = "t"
    o = [_scene(light, g)]
    o.append(N.boulder(690, HORIZON, 90, 38, "beige"))
    o.append(f'<g>{N.crt(636, 214, 150, 128, "coral", "dusk_deep", g)}'
             f'{X.hover_loop(3.4, 10.0, 0.6)}</g>')
    o.append(f'<g>{N.keyboard(628, 344, 172, 30, "beige")}'
             f'{X.hover_loop(3.4, 10.0, 0.6)}</g>')
    o.append(X.cactus(842, HORIZON, 44, 104, PAL["cool"], 12, 1))
    o.append(N.drift_sand(W, 336, 8))
    o.append(title_slab(d, light))
    o.append(data_slab([(a, b) for a, b in d["pairs"][:5]], light, 40, 128, 396, 178,
                       "measured across the portfolio"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "terminal", d)


def render_architecture(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "architecture"
    g = "a"
    o = [_scene(light, g)]
    o.append(X.cast_shadow(250, HORIZON + 8, 180, 18, g, skew=-6))
    o.append(X.mesa(104, 190, 220, 166, 4, PAL["mass"], d=22))
    o.append(f'<g>{N.rack(342, 196, 96, 158, 5, "dusk_mid", g)}'
             f'{X.hover_loop(3.2, 9.0, 0.3)}</g>')
    o.append(X.cactus(478, HORIZON, 44, 106, PAL["cool"], 11, 1))
    o.append(N.agave(532, HORIZON, 48, 66, "sage"))
    o.append(f'<g>{N.satellite(700, 118, 34, "coral", "turquoise")}'
             f'{X.drift_loop(16, 18, 0)}</g>')
    o.append(N.boulder(818, HORIZON, 66, 30, "beige"))
    o.append(title_slab(d, light, f"{d['modules_count']} roots"))
    o.append(data_slab([(m, f"module {i + 1}") for i, m in
                        enumerate(d["module_plinths"][:5])], light, 40, 128, 330, 178,
                       "module roots"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "architecture", d)


def render_data_flow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "data_flow"
    g = "d"
    o = [_scene(light, g)]
    road = HORIZON - 4
    o.append(X.plaque(70, road, 700, 20, C.tint("beige", -0.14), r=10))
    stages = d["stages"][:5]
    n = len(stages)
    gap = 640 / max(n, 1)
    for i, s in enumerate(stages):
        x = 92 + i * gap
        fill = PAL["mass"] if i % 2 == 0 else PAL["alt"]
        blk = X.block(x, road - 58 - (i % 2) * 14, 82, 58, 14, fill, r=10, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(4.0, 7.6 + i * 0.55, i * 0.5)}</g>")
        if i:
            px = 92 + (i - 1) * gap + 82
            seg = max(gap - 94, 14)
            o.append(
                f'<g>{X.plaque(px + 6, road - 3, seg, 6, C.PALETTE["sun"], r=3)}'
                f'{X.plaque(px + 6, road - 3, 15, 6, C.PALETTE["cream"], r=3)}'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="0 0;{_f(seg)} 0;0 0" dur="{_f(6.8 + i * 1.1)}s" '
                f'begin="{_f(i * 0.9)}s" repeatCount="indefinite" '
                f'calcMode="spline" keyTimes="0;0.5;1" '
                f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/></g>')
    o.append(f'<g>{N.rack(792, 222, 74, 132, 4, "dusk_mid", g)}'
             f'{X.hover_loop(3.0, 9.5, 0.8)}</g>')
    o.append(N.boulder(120, HORIZON, 62, 26, "beige"))
    o.append(title_slab(d, light, f"{d['note_routes']} routes"))
    o.append(data_slab([(s[:22], f"hop {i + 1}") for i, s in enumerate(stages)],
                       light, 40, 128, 372, 178, "endpoints in sequence"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "data_flow", d)


def render_state_machine(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "state_machine"
    g = "s"
    o = [_scene(light, g, night=True)]
    o.append(X.gateway(360, 190, 132, 166, PAL["alt"], g, 10.5))
    prims = d["primitives"][:4]
    states = ["in", *prims[:3], "out"]
    gap = 620 / max(len(states) - 1, 1)
    for i, s in enumerate(states):
        x = 118 + i * gap
        fill = PAL["cool"] if i in (0, len(states) - 1) else PAL["mass"]
        o.append(X.ball(x, HORIZON - 46, 24, fill, 7.6 + i * 0.8, i * 0.7))
    o.append(N.boulder(742, HORIZON, 70, 30, "beige"))
    o.append(N.agave(806, HORIZON, 46, 62, "sage"))
    o.append(title_slab(d, light, f"{len(prims)} detected"))
    o.append(data_slab([(s[:24], f"state {i + 1}") for i, s in enumerate(states)],
                       light, 40, 128, 372, 178, "transition order"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "state_machine", d)


def render_component_map(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "component_map"
    g = "c"
    o = [_scene(light, g)]
    fw = d["frameworks"][:8]
    for i, f in enumerate(fw):
        cx = 396 + (i % 4) * 118
        cy = 176 + (i // 4) * 112
        blk = X.block(cx, cy, 104, 60, 13,
                      PAL["mass"] if i % 3 else PAL["alt"], r=10, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(3.0 + (i % 3) * 1.2, 7.8 + (i % 4) * 0.7, i * 0.42)}</g>")
    o.append(X.cactus(864, HORIZON, 38, 92, PAL["cool"], 11, 1))
    o.append(title_slab(d, light, f"{len(fw)} declared"))
    o.append(data_slab([(f[:24], f"dep {i + 1}") for i, f in enumerate(fw[:5])],
                       light, 40, 128, 330, 178, "declared dependencies"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "component_map", d)


def render_build(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "build"
    g = "b"
    o = [_scene(light, g)]
    o.append(N.boulder(300, HORIZON, 96, 42, "beige"))
    o.append(N.boulder(196, HORIZON, 66, 28, "beige"))
    o.append(f'<g>{N.scope(560, 218, 148, 126, "coral", g)}'
             f'{X.hover_loop(3.0, 9.0, 0.4)}</g>')
    o.append(f'<g>{N.rack(742, 206, 82, 148, 5, "dusk_mid", g)}'
             f'{X.hover_loop(3.0, 10.0, 1.0)}</g>')
    o.append(N.agave(866, HORIZON, 42, 58, "sage"))
    o.append(title_slab(d, light, f"{d['tests']} tests"))
    o.append(data_slab([("test files in trees", str(d["tests"])),
                        ("CI workflows", str(d["ci"])),
                        ("crates of tests", str(d["crates"])),
                        ("repositories", "136"),
                        ("instruments lit", "yes" if d["ci"] else "no")],
                       light, 40, 128, 372, 178, "verification"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "build", d)


def render_workflow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "workflow"
    g = "w"
    o = [_scene(light, g)]
    steps = d["steps"][:5]
    for i, s in enumerate(steps):
        x = 402 + i * 96
        hh = 44 + i * 24
        fill = PAL["mass"] if i % 2 == 0 else PAL["alt"]
        blk = X.block(x, HORIZON - hh, 78, hh, 13, fill, r=9, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(3.2 + i * 0.7, 7.4 + i * 0.55, i * 0.55)}</g>")
    o.append(f'<g>{N.satellite(842, 106, 28, "coral", "turquoise")}'
             f'{X.drift_loop(-14, 20, 2)}</g>')
    o.append(N.boulder(120, HORIZON, 84, 34, "beige"))
    o.append(N.agave(206, HORIZON, 46, 62, "sage"))
    o.append(title_slab(d, light, f"{len(steps)} steps"))
    o.append(data_slab([(s[:24], f"step {i + 1}") for i, s in enumerate(steps)],
                       light, 40, 128, 330, 178, "ordered steps"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "workflow", d)


def render_domain(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "domain"
    g = "m"
    o = [_scene(light, g)]
    o.append(N.water(430, HORIZON - 6, 300, 40, g))
    o.append(f'<g>{N.rover(500, HORIZON + 34, 116, 52, "coral")}'
             f'{X.hover_loop(3.0, 11.0, 0.5)}</g>')
    o.append(f'<g>{N.punch_cards(112, 208, 150, 74, 12, "cream")}'
             f'{X.hover_loop(3.0, 10.0, 0)}</g>')
    o.append(N.agave(790, HORIZON, 56, 78, "sage"))
    o.append(X.conifer(862, HORIZON, 50, 124, PAL["cool"], 12, 1))
    o.append(title_slab(d, light, "noaerth.com"))
    o.append(data_slab([("operating layer", "v1"), ("repositories", "136"),
                        ("surfaces", f"{d['surfaces']:,}"),
                        ("routes", f"{d['routes_count']:,}"),
                        ("next milestone", d["milestone"][:16] or "build")],
                       light, 40, 128, 396, 178, "what this is"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "domain", d)


def render_footer(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "f"
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = [X.defs(g, PAL, light)]
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>')
    o.append(f'<g><circle cx="{W - 128}" cy="92" r="44" '
             f'fill="{C.tint(PAL["sky"], 0.18)}">{X.roll_loop(360, 64, 0, W - 128, 92)}</circle></g>')
    o.append(N.ridges(W, 132))
    o.append(X.cactus(806, 122, 36, 68, PAL["cool"], 10, 1))
    o.append(f'<g>{N.robot(96, 122, 40, "cactus")}{X.hover_loop(3.0, 8.0, 0)}</g>')
    o.append(X.slab(160, 42, 470, 76, SLAB[light]["title"], light=light, r=12))
    o.append(X.label(182, 76, d["canonical_name"][:26], ink, 25))
    o.append(X.label(183, 100, "DUNG30N5 x NOAERTH", sub, 14))
    o.append(X.slab(0, 132, W, H - 132, SLAB[light]["data"], light=light, r=0, shadow=False))
    o.append(X.label(40, 168,
                     f"{d['project_category'].replace('_', ' ').title()}  /  {d['status']}"
                     f"  /  evidence {d['confidence']}", ink, 15))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "footer", d)


RENDERERS = {
    "hero": render_hero, "terminal": render_terminal,
    "architecture": render_architecture, "state_machine": render_state_machine,
    "data_flow": render_data_flow, "component_map": render_component_map,
    "build": render_build, "workflow": render_workflow,
    "domain": render_domain, "footer": render_footer,
}

VARIANTS = (("motion", False, True), ("light", True, True), ("reduced", False, False))


def render(slot: str, d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    return RENDERERS[slot](d, name, light, motion)