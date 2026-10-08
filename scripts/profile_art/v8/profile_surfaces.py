"""The profile repository's own surfaces: deeper clay, seamless loops.

These are the ten plates shown in the M4G3LL4N0 profile README. They share the
subject matter of the per-repository renderer -- every figure is still the
measured portfolio total -- but the geometry is heavier and every animation is
a closed loop, because a profile banner is watched rather than glanced at.

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
from clay import _f  # noqa: E402

P = C.PALETTE
W, H = 900, 470
FOOT_Y = 418
HORIZON = 356

ROLE_TITLE = {
    "hero": "identity", "terminal": "how it is operated",
    "architecture": "how it is built", "state_machine": "how it behaves",
    "data_flow": "how data moves", "component_map": "how it is composed",
    "build": "how it is verified", "workflow": "how it is used",
    "domain": "the problem it addresses", "footer": "identity object",
}

PAL = C.CLAY_PALETTES["mesa_terracotta"]


def _doc(body: str, slot: str, d: dict) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{C.esc(d["canonical_name"])} - {ROLE_TITLE.get(slot, slot)}">'
            f'{body}</svg>')


def strip_animations(body: str) -> str:
    """Reduced motion: remove every loop so the plate is a still image."""
    import re
    body = re.sub(r"<animate[^>]*/>", "", body)
    return re.sub(r"<animateTransform[^>]*/>", "", body)


def header(d: dict, title: str, note: str, light: bool) -> str:
    ink = P["cream"] if not light else P["dusk_deep"]
    sub = P["sand"] if not light else C.tint("clay_red", -0.52)
    out = [X.label(44, 62, d["canonical_name"][:24], ink, 30),
           X.label(46, 88, title.upper(), sub, 14),
           X.plaque(44, 104, 74, 5, P["sun"], r=3)]
    if note:
        out.append(X.label(132, 112, note[:44], sub, 13))
    return "".join(out)


def footer(d: dict, light: bool) -> str:
    ink = P["cream"] if not light else P["dusk_deep"]
    fill = C.tint(PAL["mass"], -0.30) if not light else C.tint("beige", 0.30)
    return "".join([
        X.plaque(0, FOOT_Y, W, H - FOOT_Y, fill, r=0),
        X.label(44, FOOT_Y + 42,
                f"DUNG30N5 x NOAERTH  /  {d['project_category'].replace('_', ' ').title()}",
                ink, 15),
        X.label(856, FOOT_Y + 42, f"{d['status']}  -  evidence {d['confidence']}",
                ink, 13, anchor="end"),
    ])


def scene(d: dict, gid: str, light: bool, clouds: bool = True) -> str:
    o = [X.defs(gid, PAL, light), X.backdrop(W, H, HORIZON, PAL, gid, light)]
    if clouds:
        o.append(X.cloud(520, 74, 44, 26, 0))
        o.append(X.cloud(688, 46, 30, 34, 6, 4))
    return "".join(o)


# ---------------------------------------------------------------------------
# 01 HERO -- the portfolio as an adobe settlement
# ---------------------------------------------------------------------------
def render_hero(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "h"
    o = [scene(d, g, light)]
    o.append(header(d, "identity", f"{d['routes_count']} routes", light))
    o.append(X.cast_shadow(250, HORIZON + 8, 200, 20, g, skew=-6))
    o.append(X.mesa(104, 190, 262, 166, 4, PAL["mass"], d=22, gid=g))
    o.append(X.gateway(408, 214, 152, 142, PAL["alt"], g))
    o.append(f'<g>{X.ball(484, 288, 14, PAL["cool"], 8.5, 0.4)}</g>')
    o.append(X.cactus(654, HORIZON, 50, 116, PAL["cool"], 12, 0))
    o.append(X.conifer(730, HORIZON, 58, 138, PAL["cool"], 13, 2))
    for i, m in enumerate(d["module_plinths"]):
        x = 132 + i * 118
        fill = PAL["mass"] if i % 2 == 0 else C.tint(PAL["mass"], 0.14)
        blk = X.block(x, 392, 96, 24, 11, fill, r=8, gid=g)
        o.append(f'<g>{blk}{X.hover_loop(3.4, 7.6 + i * 0.6, i * 0.6)}</g>')
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "hero", d)


# ---------------------------------------------------------------------------
# 02 TERMINAL -- a clay console with a recessed lit screen
# ---------------------------------------------------------------------------
def render_terminal(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "t"
    o = [scene(d, g, light)]
    o.append(header(d, "entry points", None, light))
    sx, sy, sw, sh = 92, 154, 486, 188
    body = "".join([
        X.cast_shadow(sx + sw / 2, HORIZON + 10, sw * 0.6, 18, g, skew=-5),
        f'<g>{X.block(sx - 22, sy - 20, sw + 44, sh + 48, 24, PAL["mass"], r=20, gid=g)}'
        f'{X.hover_loop(3.0, 9.0, 0.5)}</g>',
        X.screen(sx, sy, sw, sh, C.tint(PAL["sky"], -0.30), g),
    ])
    o.append(body)
    lines = d["terminal_lines"][:5]
    for i, line in enumerate(lines):
        yy = sy + 44 + i * 30
        o.append(f'<g>'
                 f'{X.plaque(sx + 20, yy - 13, 12, 12, P["cactus"], r=4)}'
                 f'{X.label(sx + 44, yy, line[:42], P["cream"], 14)}'
                 f'{X.drift_loop(7, 8.5 + i * 0.7, i * 0.5)}</g>')
    for i in range(min(len(lines), 4)):
        blk = X.block(626 + i * 56, HORIZON - 34 - i * 9, 46, 34 + i * 9, 12,
                      PAL["alt"], r=9, gid=g)
        o.append(f'<g>{blk}'
                 f'{X.hover_loop(3.0 + i, 7.8 + i * 0.5, i * 0.45)}</g>')
    o.append(X.cactus(866, HORIZON, 38, 88, PAL["cool"], 11, 3))
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "terminal", d)


# ---------------------------------------------------------------------------
# 03 ARCHITECTURE -- module roots as a labelled terrace
# ---------------------------------------------------------------------------
def render_architecture(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "a"
    o = [scene(d, g, light)]
    o.append(header(d, "module roots", f"{d['modules_count']} modules", light))
    o.append(X.cast_shadow(248, HORIZON + 8, 190, 19, g, skew=-6))
    o.append(X.mesa(112, 176, 274, 180, max(d["modules_count"], 2), PAL["mass"],
                    d=22, gid=g))
    for i, m in enumerate(d["module_plinths"][:4]):
        yy = 202 + i * 38
        o.append(f'<g>{X.plaque(142, yy, 158, 26, C.alpha(P["cream"], 0.18), r=8)}'
                 f'{X.label(152, yy + 19, m[:20], P["cream"], 12)}'
                 f'{X.drift_loop(5, 8.0 + i * 0.6, i * 0.5)}</g>')
    o.append(X.gateway(432, 220, 144, 136, PAL["alt"], g, 11))
    o.append(X.conifer(636, HORIZON, 56, 136, PAL["cool"], 12, 1))
    o.append(X.column(712, HORIZON - 92, 46, 92, PAL["mass"], 9, 0.5))
    o.append(X.ball(806, HORIZON - 26, 25, PAL["cool"], 8, 2))
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "architecture", d)


# ---------------------------------------------------------------------------
# 04 DATA FLOW -- a road of pavers between masses
# ---------------------------------------------------------------------------
def render_data_flow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "d"
    o = [scene(d, g, light)]
    stages = d["stages"][:5]
    o.append(header(d, "routes", f"{d['routes_count']} endpoints", light))
    road_y = HORIZON - 6
    o.append(X.plaque(96, road_y, 700, 20, C.tint("beige", -0.16), r=10))
    n = len(stages)
    gap = 660 / max(n, 1)
    for i, s in enumerate(stages):
        x = 118 + i * gap
        hh = 64 + (i % 2) * 16
        fill = PAL["mass"] if i % 2 == 0 else PAL["alt"]
        o.append(f'<g>{X.block(x, road_y - hh, 88, hh, 15, fill, r=10, gid=g)}'
                 f'{X.hover_loop(4.0, 7.4 + i * 0.55, i * 0.5)}</g>')
        o.append(X.label(x + 44, HORIZON + 44, s[:15],
                         P["clay_red"] if not light else P["dusk_deep"], 11,
                         anchor="middle"))
        if i:
            px = 118 + (i - 1) * gap + 88
            seg = max(gap - 100, 14)
            # A traveller running the road, on a closed loop.
            o.append(f'<g>{X.plaque(px + 6, road_y - 3, seg, 6, P["sun"], r=3)}'
                     f'{X.plaque(px + 6, road_y - 3, 16, 6, P["cream"], r=3)}'
                     f'<animateTransform attributeName="transform" type="translate" '
                     f'values="0 0;{_f(seg)} 0;0 0" dur="{_f(6.5 + i * 1.1)}s" '
                     f'begin="{_f(i * 0.9)}s" repeatCount="indefinite" '
                     f'calcMode="spline" keyTimes="0;0.5;1" '
                     f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/></g>')
    o.append(X.gateway(742, 244, 118, 112, PAL["alt"], g, 10))
    o.append(X.conifer(866, HORIZON, 40, 100, PAL["cool"], 11, 1))
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "data_flow", d)


# ---------------------------------------------------------------------------
# 05 STATE MACHINE -- tokens crossing a threshold
# ---------------------------------------------------------------------------
def render_state_machine(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "s"
    o = [scene(d, g, light)]
    prims = d["primitives"][:4]
    o.append(header(d, "primitives", f"{len(prims)} detected", light))
    o.append(X.cast_shadow(470, HORIZON + 8, 150, 16, g))
    o.append(X.gateway(394, 176, 152, 180, PAL["alt"], g, 10.5))
    states = ["in", *prims[:3], "out"]
    gap = 716 / max(len(states) - 1, 1)
    for i, s in enumerate(states):
        x = 96 + i * gap
        fill = PAL["cool"] if i in (0, len(states) - 1) else PAL["mass"]
        o.append(X.ball(x, HORIZON - 52, 27, fill, 7.6 + i * 0.8, i * 0.7))
        o.append(X.label(x, HORIZON - 8, s[:15],
                         P["cream"] if not light else P["dusk_deep"], 11,
                         anchor="middle"))
    o.append(X.block(96, HORIZON + 22, 96, 28, 11, PAL["mass"], r=8, gid=g))
    o.append(X.cactus(826, HORIZON, 42, 96, PAL["cool"], 10.5, 2))
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "state_machine", d)


# ---------------------------------------------------------------------------
# 06 COMPONENT MAP -- a brick field of declared dependencies
# ---------------------------------------------------------------------------
def render_component_map(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "c"
    o = [scene(d, g, light)]
    fw = d["frameworks"][:8]
    o.append(header(d, "composition", f"{len(fw)} declared", light))
    for i, f in enumerate(fw):
        cx = 100 + (i % 4) * 178
        cy = 172 + (i // 4) * 98
        fill = PAL["mass"] if i % 3 else PAL["alt"]
        o.append(f'<g>{X.block(cx, cy, 152, 76, 15, fill, r=12, gid=g)}'
                 f'{X.hover_loop(3.0 + (i % 3) * 1.2, 7.6 + (i % 4) * 0.7, i * 0.42)}</g>')
        o.append(f'<g>{X.label(cx + 76, cy + 46, f[:18], P["cream"], 12, anchor="middle")}'
                 f'{X.drift_loop(4, 8.4 + i * 0.4, i * 0.6)}</g>')
    o.append(X.conifer(772, HORIZON, 52, 122, PAL["cool"], 11.5, 1))
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "component_map", d)


# ---------------------------------------------------------------------------
# 07 BUILD -- crates by test count, a lit CI bay
# ---------------------------------------------------------------------------
def render_build(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "b"
    o = [scene(d, g, light)]
    o.append(header(d, "build and tests", f"{d['tests']} test files", light))
    crates = max(1, min(6, d["crates"]))
    o.append(X.cast_shadow(206, HORIZON + 8, 132, 16, g, skew=-5))
    for i in range(crates):
        fill = PAL["mass"] if i % 2 == 0 else PAL["alt"]
        blk = X.block(138 + i * 14, HORIZON - 48 - i * 44, 134, 42, 13, fill,
                      r=8, gid=g)
        o.append(f'<g>{blk}'
                 f'{X.hover_loop(3.0 + i * 0.8, 7.0 + i * 0.6, 0.6 + i * 0.5)}</g>')
    o.append(X.label(138, HORIZON + 26, f"{d['tests']} test files",
                     P["clay_red"] if not light else P["dusk_deep"], 13))

    cx0, cy0 = 430, 236
    lit = d["ci"] > 0
    bay = X.cast_shadow(cx0 + 100, HORIZON + 8, 116, 15, g)
    bay += X.block(cx0, cy0, 204, 120, 17, PAL["alt"], r=14, gid=g)
    o.append(f'<g>{bay}{X.hover_loop(2.6, 8.6, 0.3)}</g>')
    bay_fill = P["sun"] if lit else C.tint(PAL["mass"], -0.2)
    bay_ink = P["dusk_deep"] if lit else P["cream"]
    bay = X.plaque(cx0 + 20, cy0 + 20, 164, 80, bay_fill, r=10)
    bay += X.label(cx0 + 102, cy0 + 62, f"{d['ci']} CI", bay_ink, 24, anchor="middle")
    if lit:
        bay += X.flicker_loop(5.4, 0)
    o.append(f"<g>{bay}</g>")
    o.append(X.label(cx0, HORIZON + 26, "workflows",
                     P["clay_red"] if not light else P["dusk_deep"], 13))
    o.append(X.column(700, HORIZON - 104, 50, 104, PAL["mass"], 9.5, 0.4))
    o.append(X.cactus(790, HORIZON, 46, 104, PAL["cool"], 11, 2))
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "build", d)


# ---------------------------------------------------------------------------
# 08 WORKFLOW -- clay steps
# ---------------------------------------------------------------------------
def render_workflow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "w"
    o = [scene(d, g, light)]
    steps = d["steps"][:5]
    o.append(header(d, "workflow", f"{len(steps)} steps", light))
    for i, s in enumerate(steps):
        x = 104 + i * 146
        hh = 42 + i * 28
        fill = PAL["mass"] if i % 2 == 0 else PAL["alt"]
        o.append(f'<g>{X.block(x, HORIZON - hh, 120, hh, 15, fill, r=10, gid=g)}'
                 f'{X.hover_loop(3.4 + i * 0.7, 7.2 + i * 0.55, i * 0.55)}</g>')
        o.append(X.label(x + 60, HORIZON + 30, s[:14],
                         P["clay_red"] if not light else P["dusk_deep"], 11,
                         anchor="middle"))
    o.append(X.conifer(832, HORIZON, 46, 112, PAL["cool"], 11, 1))
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "workflow", d)


# ---------------------------------------------------------------------------
# 09 DOMAIN -- the problem, as landscape
# ---------------------------------------------------------------------------
def render_domain(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "m"
    o = [scene(d, g, light)]
    o.append(header(d, "domain", (d.get("domain") or "")[:26], light))
    o.append(X.cast_shadow(268, HORIZON + 8, 190, 18, g, skew=-5))
    o.append(X.mesa(112, 206, 258, 150, 3, PAL["mass"], d=20, gid=g))
    o.append(X.gateway(414, 236, 130, 120, PAL["alt"], g, 10.5))
    o.append(X.ball(594, HORIZON - 32, 27, PAL["cool"], 8.4, 0.6))
    o.append(X.cactus(672, HORIZON, 48, 112, PAL["cool"], 12, 1))
    o.append(X.conifer(758, HORIZON, 56, 136, PAL["cool"], 13, 2.5))
    if d.get("problem"):
        o.append(X.plaque(104, 130, 540, 46, C.alpha(P["dusk_deep"], 0.44), r=12))
        o.append(f'<g>{X.label(120, 159, d["problem"][:60], P["cream"], 14)}'
                 f'{X.drift_loop(6, 11, 0)}</g>')
    o.append(footer(d, light))
    body = "".join(o)
    return _doc(strip_animations(body) if not motion else body, "domain", d)


# ---------------------------------------------------------------------------
# 10 FOOTER -- the mark
# ---------------------------------------------------------------------------
def render_footer(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    g = "f"
    ink = P["cream"] if not light else P["dusk_deep"]
    o = [X.defs(g, PAL, light)]
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>')
    o.append(f'<g><circle cx="{W - 150}" cy="96" r="46" fill="{C.tint(PAL["sky"], 0.2)}"/>'
             f'{X.roll_loop(360, 60, 0, W - 150, 96)}</g>')
    o.append(f'<g>{X.plaque(0, 132, W, H - 132, C.tint(PAL["mass"], -0.30), r=0)}</g>')
    o.append(X.cast_shadow(112, 118, 66, 11, g))
    mark = X.mesa(70, 40, 86, 78, 3, PAL["mass"], d=13, gid=g)
    o.append(f'<g>{mark}{X.hover_loop(3.4, 9, 0)}</g>')
    o.append(f'<g>{X.gateway(168, 52, 56, 66, PAL["alt"], g, 8)}</g>')
    o.append(X.label(252, 74, d["canonical_name"][:28], ink, 26))
    o.append(X.label(254, 102, "DUNG30N5 x NOAERTH",
                     P["sand"] if not light else C.tint("clay_red", -0.22), 15))
    o.append(X.label(254, 128,
                     f"{d['project_category'].replace('_', ' ').title()}  /  {d['status']}",
                     ink, 13))
    o.append(X.cactus(844, 120, 36, 70, PAL["cool"], 10, 1))
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