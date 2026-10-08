"""The profile plates: deep architecture behind, information on solid slabs.

Generated from MASTER_PROMPT.md. Layer order is enforced:

    LAYER 3  opaque clay slab      every string in the plate lives here
    LAYER 2  type                  cream on a dark slab, dusk on a light slab
    LAYER 1  furniture             the figures and labels that carry the meaning
    LAYER 0  scenery               buildings, street, machines, haze

Every motion track runs on a coprime period from clay3d.LOOP and starts and
ends on the same value, so each track is seamless and the composite period is
the product of seven primes -- a plate effectively never visibly repeats.

The 136 per-repository surfaces come from clay_renderers.py and are untouched.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay as C  # noqa: E402
import clay3d as X  # noqa: E402
import depth as D  # noqa: E402
import naturetech as N  # noqa: E402
from clay import _f  # noqa: E402

W, H = 900, 470
FOOT_Y = 424
HORIZON = 372          # where the sidewalk meets the buildings
STREET_Y = 396          # where the curb drops to the roadway
PAL = C.CLAY_PALETTES["mesa_terracotta"]

ROLE_TITLE = {
    "hero": "identity", "terminal": "how it is operated",
    "architecture": "how it is built", "state_machine": "how it behaves",
    "data_flow": "how data moves", "component_map": "how it is composed",
    "build": "how it is verified", "workflow": "how it is used",
    "domain": "the problem it addresses", "footer": "identity object",
}

# Plate identities from MASTER_PROMPT section 8.
PLATE = {
    "hero": ("Apartment block on a dusk street, shopfronts lit", "identity"),
    "terminal": ("Corner shop at night, awning and signboard", "entry points"),
    "architecture": ("Terraced blocks with servers in the windows", "module roots"),
    "data_flow": ("Night street, packets crossing the crosswalk", "routes"),
    "state_machine": ("Twilight skyline, moon and lit windows", "primitives"),
    "component_map": ("Morning block, long shadows, drive wall", "composition"),
    "build": ("Loading dock with crates and a lit instrument bay", "build and tests"),
    "workflow": ("Canyon steps of stacked blocks under a low sun", "workflow"),
    "domain": ("Campfire on the shore, tent and figures", "domain"),
}

_slot = "hero"


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
# information -- every string lives on a slab
# ---------------------------------------------------------------------------
def title_slab(d: dict, light: bool, note: str = "") -> str:
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    x, y, w, h = 34, 28, 356, 72
    o = [X.slab(x, y, w, h, PS_FILL(light)["title"], light=light, r=12)]
    o.append(X.label(x + 20, y + 40, d["canonical_name"][:22], ink, 25))
    o.append(X.label(x + 21, y + 62, PLATE.get(_slot, ("", ""))[1].upper(), sub, 13))
    if note:
        o.append(X.label(x + w - 18, y + 62, note[:18], sub, 13, anchor="end"))
    return "".join(o)


def data_slab(rows: list[tuple[str, str]], light: bool, x: float, y: float,
              w: float, h: float, heading: str = "") -> str:
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = [X.slab(x, y, w, h, PS_FILL(light)["data"], light=light, r=14)]
    top = y + 30
    if heading:
        o.append(X.label(x + 20, top, heading.upper(), sub, 13))
        top += 30
    room = int((y + h - 14 - top) // 30) + 1
    for i, (label, value) in enumerate(rows[:max(room, 0)]):
        ry = top + i * 30
        o.append(X.label(x + 20, ry, label[:24], sub, 14))
        o.append(X.label(x + w - 20, ry, value[:14], ink, 17, anchor="end"))
    return "".join(o)


def figure_tiles(items, light: bool, x: float, y: float, pitch: int = 150,
                 tile: int = 134, tile_h: int = 78) -> str:
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = []
    for i, (value, label) in enumerate(items[:3]):
        tx = x + i * pitch
        o.append(X.slab(tx, y, tile, tile_h, PS_FILL(light)["tile"],
                        light=light, r=12))
        o.append(f"<g>{X.label(tx + 14, y + 36, value[:9], ink, 22)}"
                 f'{X.hover_loop(3.0, X.loop_dur(i), X.loop_begin(i))}</g>')
        o.append(X.label(tx + 15, y + 60, label[:16], sub, 12))
    return "".join(o)


def footer_slab(d: dict, light: bool) -> str:
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = [X.slab(0, FOOT_Y, W, H - FOOT_Y, PS_FILL(light)["foot"], light=light,
                r=0, shadow=False)]
    o.append(X.label(34, FOOT_Y + 30,
                     f"DUNG30N5 x NOAERTH  /  {d['project_category'].replace('_', ' ').title()}",
                     ink, 14))
    o.append(X.label(866, FOOT_Y + 30,
                     f"{d['status']}  -  evidence {d['confidence']}", sub, 13,
                     anchor="end"))
    return "".join(o)


def PS_FILL(light: bool) -> dict:
    return X.SLAB_LIGHT if light else X.SLAB_DARK


# ---------------------------------------------------------------------------
# scenery
# ---------------------------------------------------------------------------
def sky_and_street(light: bool, g: str, night: bool = False,
                   road: bool = True) -> str:
    """Dusk sky, ridge haze, sidewalk, curb and roadway."""
    o = [X.defs(g, PAL, light)]
    o.append(N.night_sky(W, H, g) if night else
             f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>')
    if not night:
        sx, sy, sr = W - 150, 74, 34
        o.append(f'<g><circle cx="{sx}" cy="{sy}" r="{_f(sr * 2.5)}" '
                 f'fill="url(#halo{g})">{X.halo_loop(sr * 2.2, sr * 2.8, X.loop_dur(0))}'
                 f'</circle><circle cx="{sx}" cy="{sy}" r="{sr}" '
                 f'fill="{C.PALETTE["sun"]}"/></g>')
        o.append(N.cloud(560, 62, 38, X.loop_dur(1), X.loop_begin(1)) if hasattr(N, "cloud") else "")
    o.append(D.haze(HORIZON - 96, 96, W, C.PALETTE["peach"], 0.14 if not night else 0.06))
    if road:
        o.append(N.pixel_grid(W, HORIZON - 34, 30, 14, 3, C.PALETTE["turquoise"])
                 if not night else "")
        o.append(D.curb(W, HORIZON, STREET_Y - HORIZON, "sand", "beige"))
        road_fill = C.tint(C.PALETTE["dusk_soft"], -0.34)
        o.append(f'<rect x="0" y="{STREET_Y}" width="{W}" height="{H - STREET_Y}" '
                 f'fill="{road_fill}"/>')
        o.append(D.crosswalk(W, STREET_Y, H - STREET_Y, 7))
        o.append(D.haze(STREET_Y, 16, W, C.PALETTE["peach"], 0.10))
    return "".join(o)


def lamp(x: float, g: str, h: float = 66.0, i: int = 0) -> str:
    return (f"<g>{D.lamp_post(x, HORIZON, h, g)}"
            f'{X.glow_loop(0.86, 1.0, X.loop_dur(i), X.loop_begin(i))}</g>')


def figure(x: float, i: int = 0, h: float = 52.0, shirt: str = "turquoise",
           hair: str = "clay_red", g: str = "win") -> str:
    return (f'<g>{D.figure(x, HORIZON, h, shirt, hair, g)}'
            f'{X.drift_loop(7, X.loop_dur(i), X.loop_begin(i))}</g>')


# ---------------------------------------------------------------------------
# plates
# ---------------------------------------------------------------------------
def render_hero(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "hero"
    g = "h"
    o = [sky_and_street(light, g)]
    # A run of apartment blocks receding to the right.
    o.append(D.depth_fade(D.building(506, 96, 112, 276, 5, "clay_red", g, 0.5, 2, 2), 0.86))
    o.append(D.depth_fade(D.building(612, 122, 100, 250, 5, "terracotta", g, 0.45, 5, 0), 0.72))
    o.append(D.depth_fade(D.building(706, 150, 94, 222, 4, "coral", g, 0.4, 7, 0), 0.58))
    o.append(D.building(376, 70, 134, 302, 6, "adobe", g, 0.66, 1, 2))
    # shopfront under the block
    o.append(D.awning(376, 300, 134, 16, "coral", "cream", 6))
    o.append(D.sign_board(276, 274, 112, 22, "cream", "clay_red"))
    o.append(N.crt(384, 306, 62, 58, "beige", "dusk_deep", g))
    o.append(D.festoon(376, 250, 508, 238, 12, 14, g))
    # street
    o.append(lamp(342, g, 70, 2))
    o.append(D.bollard(322, HORIZON))
    o.append(D.bollard(866, HORIZON))
    o.append(figure(540, 3, 54, "turquoise", "clay_red", g))
    o.append(figure(578, 4, 50, "ember", "dusk_deep", g))
    o.append(D.railing(700, 300, 150, 60, "dusk_mid", 6))
    o.append(N.boulder(842, HORIZON, 46, 22, "beige"))
    o.append(D.haze(HORIZON - 40, 40, W, C.PALETTE["peach"], 0.10))
    # information
    o.append(title_slab(d, light, d["note_routes"] + " routes"))
    o.append(figure_tiles(d["tiles"], light, 34, 116))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "hero", d)


def render_terminal(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "terminal"
    g = "t"
    o = [sky_and_street(light, g)]
    o.append(D.building(600, 60, 250, 312, 7, "clay_red", g, 0.62, 3, 3))
    o.append(D.building(300, 96, 150, 276, 6, "adobe", g, 0.5, 6, 0))
    # corner shop
    o.append(D.awning(560, 268, 200, 18, "coral", "cream", 7))
    o.append(D.sign_board(578, 240, 166, 24, "cream", "clay_red"))
    o.append(f"<g>{N.crt(586, 288, 120, 74, 'beige', 'dusk_deep', g)}"
             f'{X.hover_loop(3.0, X.loop_dur(2), X.loop_begin(2))}</g>')
    o.append(f"<g>{N.keyboard(584, 366, 132, 22, 'terracotta')}"
             f'{X.hover_loop(3.0, X.loop_dur(2), X.loop_begin(2))}</g>')
    o.append(D.festoon(560, 214, 760, 198, 12, 15, g))
    o.append(lamp(252, g, 72, 1))
    o.append(figure(420, 5, 54, "cactus", "clay_red", g))
    o.append(figure(486, 6, 50, "turquoise", "beige", g))
    o.append(D.haze(HORIZON - 40, 40, W, C.PALETTE["peach"], 0.10))
    o.append(title_slab(d, light))
    o.append(data_slab(d["pairs"][:5], light, 34, 112, 392, 176,
                       "measured across the portfolio"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "terminal", d)


def render_architecture(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "architecture"
    g = "a"
    o = [sky_and_street(light, g)]
    o.append(D.depth_fade(D.building(600, 130, 110, 242, 5, "terracotta", g, 0.5, 4, 0), 0.70))
    o.append(D.building(330, 56, 150, 316, 7, "adobe", g, 0.7, 2, 3))
    # racks in the windows: the machine inside the architecture
    for fl in range(3):
        for c in range(2):
            o.append(f'<g>{N.rack(348 + c * 66, 108 + fl * 78, 52, 54, 2, "dusk_mid", g)}'
                     f'{X.glow_loop(0.88, 1.0, X.loop_dur(fl * 2 + c), X.loop_begin(fl * 2 + c))}</g>')
    o.append(lamp(250, g, 70, 3))
    o.append(X.cactus(830, HORIZON, 40, 92, PAL["cool"], X.loop_dur(4), X.loop_begin(4)))
    o.append(N.agave(872, HORIZON, 44, 60, "sage"))
    o.append(figure(500, 7, 52, "ember", "dusk_deep", g))
    o.append(D.haze(HORIZON - 40, 40, W, C.PALETTE["peach"], 0.10))
    o.append(title_slab(d, light, f"{d['modules_count']} roots"))
    o.append(data_slab([(m, f"module {i + 1}") for i, m in
                        enumerate(d["module_plinths"][:5])],
                       light, 34, 112, 330, 176, "module roots"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "architecture", d)


def render_data_flow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "data_flow"
    g = "d"
    o = [sky_and_street(light, g, night=True)]
    o.append(D.depth_fade(D.building(0, 130, 130, 242, 5, "clay_red", g, 0.55, 2, 0), 0.66))
    o.append(D.depth_fade(D.building(700, 110, 200, 262, 6, "adobe", g, 0.6, 5, 2), 0.74))
    stages = d["stages"][:5]
    # packets riding the crosswalk
    for i, s in enumerate(stages):
        x = 452 + i * 92
        blk = X.block(x, 322, 62, 44, 12, PAL["mass"] if i % 2 == 0 else PAL["alt"],
                      r=9, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(4.0, X.loop_dur(i), X.loop_begin(i))}</g>")
    o.append(lamp(392, g, 74, 5))
    o.append(lamp(806, g, 74, 6))
    o.append(figure(596, 0, 52, "turquoise", "clay_red", g))
    o.append(D.haze(HORIZON - 40, 40, W, C.PALETTE["dusk_mid"], 0.10))
    o.append(title_slab(d, light, d["note_routes"] + " routes"))
    o.append(data_slab([(s[:22], f"hop {i + 1}") for i, s in enumerate(stages)],
                       light, 34, 112, 368, 176, "endpoints in sequence"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "data_flow", d)


def render_state_machine(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "state_machine"
    g = "s"
    o = [sky_and_street(light, g, night=True)]
    prims = d["primitives"][:4]
    states = ["in", *prims[:3], "out"]
    # a skyline of lit blocks
    for i, (bx, bw, bf) in enumerate(((0, 150, 4), (146, 96, 6), (700, 200, 5))):
        o.append(D.depth_fade(D.building(bx, 150, bw, 222, bf, "clay_red" if i % 2 else "dusk_mid",
                                         g, 0.6, i + 1, 2), 0.62 + i * 0.14))
    o.append(X.gateway(346, 190, 120, 182, PAL["alt"], g, X.loop_dur(0)))
    gap = 600 / max(len(states) - 1, 1)
    for i, s in enumerate(states):
        x = 128 + i * gap
        fill = PAL["cool"] if i in (0, len(states) - 1) else PAL["mass"]
        o.append(X.ball(x, HORIZON - 44, 22, fill, X.loop_dur(i), X.loop_begin(i)))
    o.append(lamp(300, g, 72, 2))
    o.append(N.boulder(566, HORIZON, 62, 26, "beige"))
    o.append(title_slab(d, light, f"{len(prims)} detected"))
    o.append(data_slab([(s[:24], f"state {i + 1}") for i, s in enumerate(states)],
                       light, 34, 112, 368, 176, "transition order"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "state_machine", d)


def render_component_map(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "component_map"
    g = "c"
    o = [sky_and_street(light, g)]
    o.append(D.building(0, 40, 220, 332, 8, "terracotta", g, 0.4, 4, 3))
    # a wall of drives as the plate's furniture
    fw = d["frameworks"][:8]
    for i, f in enumerate(fw):
        cx = 268 + (i % 4) * 150
        cy = 118 + (i // 4) * 126
        blk = X.block(cx, cy, 130, 66, 14, PAL["mass"] if i % 3 else PAL["alt"],
                      r=11, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(3.0 + (i % 3), X.loop_dur(i), X.loop_begin(i))}</g>")
        o.append(D.railing(cx + 8, cy + 68, 114, 16, "dusk_mid", 4))
    o.append(lamp(868, g, 70, 4))
    o.append(X.cactus(846, HORIZON, 34, 84, PAL["cool"], X.loop_dur(5), X.loop_begin(5)))
    o.append(D.haze(HORIZON - 40, 40, W, C.PALETTE["peach"], 0.10))
    o.append(title_slab(d, light, f"{len(fw)} declared"))
    o.append(data_slab([(f[:24], f"dep {i + 1}") for i, f in enumerate(fw[:5])],
                       light, 34, 112, 328, 176, "declared dependencies"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "component_map", d)


def render_build(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "build"
    g = "b"
    o = [sky_and_street(light, g)]
    o.append(D.building(560, 84, 300, 288, 6, "adobe", g, 0.6, 3, 2))
    # loading dock: crates by real test count
    crates = max(1, min(6, d["crates"]))
    for i in range(crates):
        blk = X.block(280 + i * 22, HORIZON - 44 - i * 40, 96, 38, 13,
                      PAL["mass"] if i % 2 == 0 else PAL["alt"], r=8, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(3.0 + i, X.loop_dur(i), X.loop_begin(i))}</g>")
    o.append(f"<g>{N.scope(452, 236, 138, 118, 'coral', g)}"
             f'{X.hover_loop(3.0, X.loop_dur(2), X.loop_begin(2))}</g>')
    o.append(f"<g>{N.rack(600, 214, 84, 158, 5, 'dusk_mid', g)}"
             f'{X.glow_loop(0.88, 1.0, X.loop_dur(3), X.loop_begin(3))}</g>')
    o.append(D.awning(556, 208, 300, 16, "coral", "cream", 7))
    o.append(lamp(252, g, 72, 1))
    o.append(D.bollard(224, HORIZON))
    o.append(figure(330, 6, 52, "cactus", "clay_red", g))
    o.append(D.haze(HORIZON - 40, 40, W, C.PALETTE["peach"], 0.10))
    o.append(title_slab(d, light, f"{d['tests']} tests"))
    o.append(data_slab([("test files in trees", str(d["tests"])),
                        ("CI workflows", str(d["ci"])),
                        ("crates of tests", str(crates)),
                        ("repositories", "136"),
                        ("instruments lit", "yes" if d["ci"] else "no")],
                       light, 34, 112, 368, 176, "verification"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "build", d)


def render_workflow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "workflow"
    g = "w"
    o = [sky_and_street(light, g)]
    o.append(D.building(0, 96, 176, 276, 6, "coral", g, 0.55, 4, 2))
    steps = d["steps"][:5]
    for i, s in enumerate(steps):
        x = 300 + i * 118
        hh = 52 + i * 28
        fill = PAL["mass"] if i % 2 == 0 else PAL["alt"]
        blk = X.block(x, HORIZON - hh, 96, hh, 14, fill, r=10, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(3.2 + i, X.loop_dur(i), X.loop_begin(i))}</g>")
    o.append(D.building(720, 130, 180, 242, 5, "terracotta", g, 0.5, 6, 0))
    o.append(lamp(268, g, 70, 0))
    o.append(N.agave(690, HORIZON, 46, 62, "sage"))
    o.append(D.haze(HORIZON - 40, 40, W, C.PALETTE["peach"], 0.10))
    o.append(title_slab(d, light, f"{len(steps)} steps"))
    o.append(data_slab([(s[:24], f"step {i + 1}") for i, s in enumerate(steps)],
                       light, 34, 112, 328, 176, "ordered steps"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "workflow", d)


def render_domain(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global _slot
    _slot = "domain"
    g = "m"
    o = [X.defs(g, PAL, light)]
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>')
    sx, sy, sr = W - 140, 76, 36
    o.append(f'<g><circle cx="{sx}" cy="{sy}" r="{_f(sr * 2.5)}" fill="url(#halo{g})">'
             f'{X.halo_loop(sr * 2.2, sr * 2.8, X.loop_dur(0))}</circle>'
             f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{C.PALETTE["sun"]}"/></g>')
    o.append(D.haze(212, 76, W, C.PALETTE["peach"], 0.16))
    o.append(N.ridges(W, 248))
    # shoreline
    o.append(f'<rect x="0" y="300" width="{W}" height="52" '
             f'fill="{C.tint(C.PALETTE["turquoise"], -0.24)}"/>')
    o.append("".join(
        f'<rect x="{_f(20 + i * 118)}" y="{_f(312 + (i % 3) * 11)}" '
        f'width="70" height="5" rx="2.5" fill="{C.PALETTE["cream"]}" '
        f'opacity="{0.34 - (i % 3) * 0.07:.2f}"/>' for i in range(7)))
    o.append(f'<rect x="0" y="348" width="{W}" height="{H - 348}" '
             f'fill="url(#floor{g})"/>')
    # camp
    o.append(f"<g>{D.tent(596, 348, 118, 88, 'ember')}"
             f'{X.glow_loop(0.9, 1.0, X.loop_dur(1), X.loop_begin(1))}</g>')
    o.append(f'<g>{D.chair(478, 348, 44, "coral")}'
             f'{X.hover_loop(3.0, X.loop_dur(2), X.loop_begin(2))}</g>')
    o.append(D.cooler(556, 348, 34, 24))
    o.append(D.log_ring(392, 348, 30, 7, "clay_red"))
    o.append(f"<g>{D.flame(392, 352, 22, 56, g)}"
             f'{X.glow_loop(0.82, 1.0, X.loop_dur(0), 0)}'
             f'<animateTransform attributeName="transform" type="scale" '
             f'values="1 1;1.06 1.1;1 1" dur="{X.loop_dur(0)}s" '
             f'repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
             f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1" additive="sum"/></g>')
    o.append(figure(322, 352, 62, "turquoise", "clay_red", g))
    o.append(figure(462, 352, 58, "ember", "dusk_deep", g))
    o.append(D.umbrella(742, 348, 42, 68, "coral", "cream"))
    o.append(X.cactus(858, 352, 44, 112, PAL["cool"], X.loop_dur(5), X.loop_begin(5)))
    o.append(title_slab(d, light, "noaerth.com"))
    o.append(data_slab([("operating layer", "v1"), ("repositories", "136"),
                        ("surfaces", f"{d['surfaces']:,}"),
                        ("routes", d["note_routes"]),
                        ("camp", "one fire")],
                       light, 34, 112, 392, 176, "what this is"))
    o.append(footer_slab(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "domain", d)


def render_footer(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "f"
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    o = [X.defs(g, PAL, light)]
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>')
    o.append(f'<g><circle cx="{W - 122}" cy="88" r="42" '
             f'fill="{C.tint(PAL["sky"], 0.18)}">'
             f'{X.roll_loop(360, X.loop_dur(0) * 8, 0, W - 122, 88)}</circle></g>')
    o.append(D.building(0, 96, 260, 96, 3, "clay_red", g, 0.6, 1, 0))
    o.append(D.building(640, 108, 260, 84, 3, "dusk_mid", g, 0.5, 4, 0))
    o.append(D.haze(150, 40, W, C.PALETTE["peach"], 0.12))
    o.append(f"<g>{N.robot(120, 150, 44, 'cactus')}"
             f'{X.hover_loop(3.0, X.loop_dur(1), X.loop_begin(1))}</g>')
    o.append(X.cactus(770, 150, 38, 72, PAL["cool"], X.loop_dur(2), X.loop_begin(2)))
    o.append(X.slab(190, 40, 470, 80, PS_FILL(light)["title"], light=light, r=12))
    o.append(X.label(212, 78, d["canonical_name"][:26], ink, 25))
    o.append(X.label(213, 104, "DUNG30N5 x NOAERTH", sub, 14))
    o.append(X.slab(0, 190, W, H - 190, PS_FILL(light)["data"], light=light,
                    r=0, shadow=False))
    o.append(X.label(34, 228,
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