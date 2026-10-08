"""The profile plates as device-in-the-wild dioramas.

Implements DIORAMA_BRIEF.md sections 3-5. Each plate is one reference photo's
setting with its story copy: the same measured portfolio figures, but the words
belong to the photo (routes read as tributaries, modules as racks, tests as
launch checks, steps as waypoints, dependencies as panels).

Layer order is fixed: trail-sign slabs carry every string, scenery carries
everything else. check_legibility.py enforces containment plus measured contrast.

The 136 per-repository surfaces come from clay_renderers.py and are untouched.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diorama as M  # noqa: E402

W, H = 900, 470
FOOT_Y = 424
GROUND_Y = 372
PALETTE = "mesa"
T = "DUNG30N5 x NOAERTH"

ROLE = {
    "hero": "compute in the wild",
    "terminal": "the workbench",
    "architecture": "machines in the rock",
    "data_flow": "data flows downhill",
    "state_machine": "watching the sky",
    "component_map": "every panel counts",
    "build": "cleared for launch",
    "workflow": "the flight path",
    "domain": "the link",
    "footer": "in your pocket",
}


def strip(body: str) -> str:
    import re
    body = re.sub(r"<animate[^>]*/>", "", body)
    return re.sub(r"<animateTransform[^>]*/>", "", body)


def doc(body: str, slot: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{T} - {ROLE.get(slot, slot)}">{body}</svg>')


def trees_back(y: float, seed: int, x0: float = 0, x1: float = 900,
               n: int = 7, s0: float = 44.0) -> str:
    """A treeline in front of a cliff wall: pines at jittered positions."""
    r = M.rng_for("treeline", str(seed))
    out = []
    for k in range(n):
        cx = x0 + (x1 - x0) * (k + r.uniform(-0.3, 0.3)) / n
        w = s0 * r.uniform(0.75, 1.1)
        out.append(M.conifer(cx, y + r.uniform(-6, 4), w, w * 2.1,
                             k + seed * 7))
    return "".join(out)


def cliff_band(x: float, y: float, w: float, h: float, gid: str,
               seed: int = 0, d: float = 0.0) -> str:
    return M.strata_cliff(x, y, w, h, gid, 6, seed, d)


# ---------------------------------------------------------------------------
# 01 HERO -- laptop in the red rocks, waterfall and river
# ---------------------------------------------------------------------------
def render_hero(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "h"
    day = "day" if not light else "day"
    _ = day
    o = [M.defs_sky(g, "gold" if light else "day"), M.sky_block(W, H, g, "gold" if light else "day")]
    o.append(M.sun_disc(752, 84, 30, g, 0))
    o.append(M.block_cloud(170, 66, 44, 1))
    o.append(M.block_cloud(560, 44, 30, 2))
    o.append(cliff_band(0, 150, 150, 190, g, 1))
    o.append(cliff_band(760, 132, 140, 208, g, 2))
    o.append(M.mesa(640, 210, 140, 130, 3, g, 3))
    o.append(M.shadow_ellipse(500, 348, 150, 12, g))
    o.append(M.sand_floor(W, 340, H, 11))
    o.append(M.river(0, 384, W, 86, g, 3))
    o.append(M.waterfall(238, 210, 36, 130, g))
    o.append(M.waterfall(690, 226, 30, 114, g))
    o.append(trees_back(348, 4, 330, 700, 8, 46))
    o.append(M.cactus(610, 372, 46, 100, 5))
    o.append(M.flower_patch(40, 400, 200, 12, 6))
    o.append(M.flower_patch(660, 404, 200, 12, 7))
    # the laptop, big, planted left of centre
    o.append(M.shadow_ellipse(232, 372, 96, 10, g))
    o.append(M.laptop(120, 368, 220, 8))
    o.append(M.rock_block(360, 392, 26, 9))
    # signage
    o.append(M.title_sign(34, 26, 372, T, ROLE["hero"], d["routes_line"]))
    o.append("".join(
        M.tile_sign(34 + i * 158, 112, v, lab)
        for i, (v, lab) in enumerate(d["hero_tiles"][:3])))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "hero")


# ---------------------------------------------------------------------------
# 02 TERMINAL -- desktop in the marigolds, screen shows the canyon
# ---------------------------------------------------------------------------
def render_terminal(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "t"
    o = [M.defs_sky(g), M.sky_block(W, H, g)]
    o.append(M.sun_disc(756, 80, 28, g, 0))
    o.append(M.block_cloud(620, 56, 32, 1))
    o.append(cliff_band(0, 130, 120, 220, g, 3))
    o.append(cliff_band(800, 118, 100, 232, g, 4))
    o.append(M.sand_floor(W, 350, H, 12))
    o.append(M.flower_patch(30, 396, 340, 22, 13))
    o.append(M.flower_patch(540, 400, 330, 22, 14))
    o.append(trees_back(352, 5, 650, 880, 6, 42))
    o.append(M.cactus(470, 386, 52, 118, 6))
    o.append(M.shadow_ellipse(700, 392, 104, 10, g))
    o.append(M.desktop(560, 388, 260, 7))
    o.append(M.rock_block(486, 398, 24, 8))
    o.append(M.title_sign(34, 26, 372, T, ROLE["terminal"], ""))
    o.append(M.data_sign(34, 112, 392, d["pairs"][:5], "the workbench", False))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "terminal")


# ---------------------------------------------------------------------------
# 03 ARCHITECTURE -- server rack standing in the cliff
# ---------------------------------------------------------------------------
def render_architecture(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    global_unit = "a"
    g = global_unit
    o = [M.defs_sky(g), M.sky_block(W, H, g)]
    o.append(M.sun_disc(748, 82, 28, g, 0))
    o.append(M.block_cloud(170, 60, 40, 1))
    o.append(cliff_band(0, 96, 118, 252, g, 5))
    o.append(cliff_band(596, 84, 304, 264, g, 6))
    o.append(M.sand_floor(W, 348, H, 13))
    o.append(M.river(0, 398, W, 72, g, 2))
    o.append(M.waterfall(150, 268, 34, 130, g))
    o.append(trees_back(354, 7, 60, 560, 8, 46))
    o.append(M.cactus(640, 372, 48, 108, 8))
    o.append(M.flower_patch(560, 386, 300, 14, 9))
    o.append(M.shadow_ellipse(470, 380, 72, 10, g))
    o.append(M.server_tower(430, 380, 96, d["racks"], 10))
    o.append(M.rock_block(548, 388, 26, 11))
    o.append(M.title_sign(34, 26, 372, T, ROLE["architecture"],
                          f"{d['modules_count']} racks"))
    o.append(M.data_sign(34, 112, 330, [(m, f"rack {i + 1}") for i, m in
                                        enumerate(d["module_plinths"][:5])],
                         "machines in the rock", False))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "architecture")


# ---------------------------------------------------------------------------
# 04 DATA FLOW -- the river and the waterfall do the moving
# ---------------------------------------------------------------------------
def render_data_flow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "d"
    o = [M.defs_sky(g), M.sky_block(W, H, g)]
    o.append(M.sun_disc(756, 80, 28, g, 0))
    o.append(M.block_cloud(180, 60, 40, 1))
    o.append(cliff_band(0, 140, 110, 210, g, 7))
    o.append(cliff_band(790, 130, 110, 220, g, 8))
    o.append(M.sand_floor(W, 350, H, 14))
    o.append(M.river(0, 296, W, 88, g, 2))
    o.append(M.waterfall(420, 170, 44, 150, g))
    o.append(M.pool(340, 400, 170, 34))
    o.append(trees_back(352, 9, 120, 780, 7, 44))
    o.append(M.title_sign(34, 26, 372, T, ROLE["data_flow"], d["routes_line"]))
    o.append(M.data_sign(34, 112, 372,
                         [(s[:22], f"trib {i + 1}") for i, s in enumerate(d["stages"][:5])],
                         "tributaries in order", False))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "data_flow")


# ---------------------------------------------------------------------------
# 05 STATE MACHINE -- observatory under the milky way
# ---------------------------------------------------------------------------
def render_state_machine(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "s"
    o = [M.defs_sky(g, "night"), M.sky_block(W, H, g, "night")]
    o.append(M.milky_way(W))
    o.append(M.stars(W, H))
    o.append(M.moon_disc(748, 88, 30))
    o.append(cliff_band(0, 210, 150, 160, g, 9))
    o.append(cliff_band(750, 200, 150, 170, g, 10))
    o.append(M.sand_floor(W, 370, H, 15))
    o.append(M.shadow_ellipse(450, 384, 150, 11, g))
    o.append(M.observatory(450, 384, 190, 11))
    o.append(trees_back(376, 12, 250, 660, 7, 40))
    o.append(M.title_sign(34, 26, 372, T, ROLE["state_machine"],
                          f"{len(d['primitives'])} bodies", night=True))
    o.append(M.data_sign(34, 112, 372,
                         [(s[:24], f"body {i + 1}") for i, s in enumerate(d["bodies"][:5])],
                         "the watched sky", True))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3", night=True))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "state_machine")


# ---------------------------------------------------------------------------
# 06 COMPONENT MAP -- solar panel in the cactus flat at sunset
# ---------------------------------------------------------------------------
def render_component_map(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "c"
    o = [M.defs_sky(g, "gold"), M.sky_block(W, H, g, "gold")]
    o.append(M.sun_disc(756, 120, 40, g, 0))
    o.append(M.block_cloud(180, 66, 40, 1))
    o.append(M.block_cloud(560, 46, 30, 2))
    o.append(cliff_band(0, 190, 110, 160, g, 11))
    o.append(cliff_band(800, 180, 100, 170, g, 12))
    o.append(M.sand_floor(W, 350, H, 16))
    o.append(M.shadow_ellipse(620, 390, 130, 11, g))
    o.append(M.solar_panel(620, 390, 230, 3))
    o.append(M.cactus(470, 384, 50, 118, 4))
    o.append(M.cactus(770, 388, 42, 96, 5))
    o.append(M.flower_patch(60, 396, 300, 16, 15))
    o.append(M.flower_patch(560, 402, 300, 12, 16))
    o.append(trees_back(354, 17, 100, 400, 5, 40))
    o.append(M.title_sign(34, 26, 372, T, ROLE["component_map"],
                          f"{len(d['frameworks'])} panels"))
    o.append(M.data_sign(34, 112, 330,
                         [(f[:24], f"panel {i + 1}") for i, f in enumerate(d["frameworks"][:5])],
                         "every panel counts", False))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return _doc_wrap(strip(body) if not motion else body, "component_map")


def _doc_wrap(body: str, slot: str) -> str:
    return doc(body, slot)


# ---------------------------------------------------------------------------
# 07 BUILD -- rocket on the pad at dusk, engines lit
# ---------------------------------------------------------------------------
def render_build(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "b"
    o = [M.defs_sky(g, "gold"), M.sky_block(W, H, g, "gold")]
    o.append(M.sun_disc(150, 300, 26, g, 0))
    o.append(cliff_band(0, 150, 96, 200, g, 18))
    o.append(cliff_band(760, 140, 140, 210, g, 19))
    o.append(M.sand_floor(W, 350, H, 17))
    o.append(M.shadow_ellipse(560, 392, 170, 12, g))
    o.append(M.rocket_pad(560, 392, 40, 4))
    pad_lights = "".join(
        f'<circle cx="{_f(478 + k * 56)}" cy="368" r="4" fill="{M.SUN}">'
        f'{M.glow(0.6, 1.0, k)}</circle>' for k in range(5))
    o.append(pad_lights)
    o.append(M.conifer(330, 372, 56, 150, 5))
    o.append(M.conifer(392, 376, 48, 128, 6))
    o.append(M.cactus(730, 376, 44, 100, 7))
    o.append(M.flower_patch(60, 398, 220, 12, 20))
    o.append(M.title_sign(34, 26, 372, T, ROLE["build"], f"{d['tests']} tests"))
    o.append(M.data_sign(34, 112, 368,
                         [("test files in trees", str(d["tests"])),
                          ("CI workflows", str(d["ci"])),
                          ("launch checks", str(d["crates"])),
                          ("repositories", "136"),
                          ("pad", "hot" if d["ci"] else "cold")],
                         "cleared for launch", False))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "build")


def _f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# 08 WORKFLOW -- drone over the canyon river
# ---------------------------------------------------------------------------
def render_workflow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "w"
    o = [M.defs_sky(g), M.sky_block(W, H, g)]
    o.append(M.sun_disc(752, 82, 28, g, 0))
    o.append(M.block_cloud(150, 60, 42, 1))
    o.append(M.block_cloud(560, 44, 30, 2))
    o.append(cliff_band(0, 150, 92, 200, g, 21))
    o.append(cliff_band(808, 150, 92, 200, g, 22))
    o.append(M.sand_floor(W, 350, H, 23))
    o.append(M.river(92, 328, 716, 64, g, 3))
    o.append(trees_back(352, 24, 130, 770, 7, 44))
    o.append(M.drone(450, 190, 58, 4))
    o.append(M.shadow_ellipse(450, 300, 70, 8, g))
    waypoints = d["steps"][:5]
    for i in range(len(waypoints) - 1):
        x0 = 200 + i * 120
        o.append(f'<circle cx="{x0}" cy="{174 + (i % 2) * 22}" r="4" '
                 f'fill="{M.SUN}"/>')
    o.append(M.title_sign(34, 26, 372, T, ROLE["workflow"],
                          f"{len(waypoints)} waypoints"))
    o.append(M.data_sign(34, 112, 330,
                         [(s[:24], f"wp {i + 1}") for i, s in enumerate(waypoints)],
                         "the flight path", False))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "workflow")


# ---------------------------------------------------------------------------
# 09 DOMAIN -- satellite and ground dish by the lake at dusk
# ---------------------------------------------------------------------------
def render_domain(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "m"
    o = [M.defs_sky(g, "gold"), M.sky_block(W, H, g, "gold")]
    o.append(M.sun_disc(724, 130, 36, g, 0))
    o.append(M.block_cloud(180, 60, 40, 1))
    o.append(cliff_band(0, 190, 96, 160, g, 25))
    o.append(M.sand_floor(W, 350, H, 26))
    o.append(M.pool(60, 372, 500, 60))
    o.append(trees_back(352, 27, 620, 880, 6, 42))
    o.append(M.shadow_ellipse(660, 386, 90, 9, g))
    o.append(M.ground_dish(660, 386, 52))
    o.append(M.orbiter(360, 170, 44, 5))
    o.append(M.flower_patch(60, 400, 420, 16, 28))
    o.append(M.cactus(830, 372, 42, 96, 6))
    o.append(M.title_sign(34, 26, 372, T, ROLE["domain"], "noaerth.com"))
    o.append(M.data_sign(34, 112, 392,
                         [("operating layer", "v1"), ("repositories", "136"),
                          ("surfaces", f"{d['surfaces']:,}"),
                          ("routes", d["routes_line"]),
                          ("the link", "up")],
                         "what this is for", False))
    o.append(M.footer_band(W, FOOT_Y, H - FOOT_Y, f"{T} / Portfolio",
                           "PORTFOLIO - E3"))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "domain")


# ---------------------------------------------------------------------------
# 10 FOOTER -- smartphone by the river at golden hour
# ---------------------------------------------------------------------------
def render_footer(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "f"
    o = [M.defs_sky(g, "gold"), M.sky_block(W, H, g, "gold")]
    o.append(M.sun_disc(752, 108, 34, g, 0))
    o.append(cliff_band(0, 60, 120, 100, g, 29))
    o.append(cliff_band(780, 52, 120, 108, g, 30))
    o.append(M.sand_floor(W, 160, H, 31))
    o.append(M.river(0, 190, W, 60, g, 1))
    o.append(trees_back(252, 32, 60, 420, 6, 40))
    o.append(trees_back(252, 33, 520, 860, 6, 40))
    o.append(M.shadow_ellipse(450, 280, 60, 7, g))
    o.append(M.phone(408, 148, 84, "9:41"))
    o.append(M.flower_patch(60, 262, 200, 10, 34))
    o.append(M.flower_patch(640, 262, 200, 10, 35))
    o.append(M.cactus(700, 280, 34, 76, 3))
    o.append(M.sign_board(180, 132, 480, 66, night=False, r=12))
    o.append(M.sign_text(202, 160, d["canonical_name"][:28], 21))
    o.append(M.sign_text(203, 184, "DUNG30N5 x NOAERTH", 13))
    body = "".join(o)
    return doc(strip(body) if not motion else body, "footer")


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