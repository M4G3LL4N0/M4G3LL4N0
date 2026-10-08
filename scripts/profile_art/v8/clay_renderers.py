"""Render the ten repository surfaces in the New Mexico clay language.

Each slot keeps its evidence contract from the previous system -- the counts,
names and entry points are still measured, not invented -- but the visual
grammar is entirely different: chunky adobe masses, rounded gateways, low-poly
vegetation, matte flat-shaded volumes, and a dusk sky with warm light.

Motion is restrained by design. Each element settles once into place and then
rests; only the sun breathes and the clouds drift. A screensaver would fight
the calm, architectural feel the system is built on.
"""

from __future__ import annotations

import sys

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay as C  # noqa: E402

P = C.PALETTE

# Slot canvases. Wide enough for a 16:9 README plate, short enough to stay
# legible as a thumbnail.
SLOT_VIEW = {
    "hero": (900, 470),
    "terminal": (900, 470),
    "architecture": (900, 470),
    "state_machine": (900, 470),
    "data_flow": (900, 470),
    "component_map": (900, 470),
    "build": (900, 470),
    "workflow": (900, 470),
    "domain": (900, 470),
    "footer": (900, 210),
}

ROLE_TITLE = {
    "hero": "identity",
    "terminal": "how it is operated",
    "architecture": "how it is built",
    "state_machine": "how it behaves",
    "data_flow": "how data moves",
    "component_map": "how it is composed",
    "build": "how it is verified",
    "workflow": "how it is used",
    "domain": "the problem it addresses",
    "footer": "identity object",
}

GROUND_Y = 352


def seed_of(name: str, slot: str) -> int:
    return C.rng_for(name, slot).randint(0, 10_000_000)


def palette(name: str) -> dict:
    """Colourway resolved into a flat dictionary the scene helpers use."""
    return dict(C.CLAY_PALETTES.get(name, C.CLAY_PALETTES["adobe_dusk"]))


def esc_text(s: str) -> str:
    return C.esc(s)


def _scene(d: dict, gid: str, light: bool = False, sun: bool = True,
           clouds: bool = True) -> tuple[int, int, list[str]]:
    """Shared backdrop: dusk sky, warm ground, sun and drifting clouds."""
    w, h = SLOT_VIEW[d["_slot"]]
    p = palette(d["palette"])
    # Light mode is a genuinely pale warm sky, not a slightly lighter dusk.
    # A mid-tone sky left the dark-ink title unreadable in GitHub's light theme.
    sky_col = p["sky"] if not light else C.tint(p["sky"], 0.68)
    out = [C.sky(w, h, sky_col, f"sky{gid}")]
    if sun:
        out.append(C.clay_sun(w - 148, 92, 40, f"sun{gid}"))
    if clouds:
        out.append(f'<g>{C.clay_cloud(524, 66, 42, P["cream"])}{C.drift(24, 36)}</g>')
        out.append(f'<g>{C.clay_cloud(660, 40, 30, P["cream"])}{C.drift(-18, 46, 3)}</g>')
    ground_fill = P["sand"] if not light else C.tint("sand", 0.34)
    out.append(C.ground(w, h, GROUND_Y, ground_fill))
    return w, h, out


def _header(d: dict, title: str, note: str, light: bool, w: int = 900) -> list[str]:
    ink = P["cream"] if not light else C.PALETTE["dusk_deep"]
    sub = P["sand"] if not light else C.tint("clay_red", -0.22)
    # The note sits on the header rule, not top-right: top-right is where the
    # sun and its glow live, and the text was unreadable over the halo.
    return [
        C.label(44, 62, d["canonical_name"][:26], ink, 30),
        C.label(46, 88, title.upper(), sub, 14),
        C.bar(44, 106, 74, 4, P["sun"], r=2),
    ] + ([C.label(132, 112, note[:46], sub, 13)] if note else [])


def _footer_strip(d: dict, light: bool, y: int, h: int) -> list[str]:
    """A quiet plinth that carries the provenance line."""
    ink = P["cream"] if not light else C.PALETTE["dusk_deep"]
    p = palette(d["palette"])
    out = [C.plaque(0, y, h * 0 + 900, h - y, C.tint(p["mass"], -0.3 if not light else 0.2), r=0)]
    out.append(C.label(44, y + 42, f"DUNG30N5 x NOAERTH  /  {d['project_category'].replace('_', ' ').title()}",
                       ink, 15))
    right = f"{d['status']}  -  evidence {d['confidence']}"
    out.append(C.label(856, y + 42, right, ink, 13, anchor="end"))
    return out


def _doc(body: str, w: int, h: int, d: dict, slot: str, motion: bool) -> str:
    if not motion:
        # Reduced motion is an accessibility requirement, not an optional variant.
        import re
        body = re.sub(r"<animate[^>]*/>", "", body)
        body = re.sub(r"<animateTransform[^>]*/>", "", body)
        body = re.sub(r'<g opacity="0">', "<g>", body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{C.esc(d["canonical_name"])} - {C.esc(ROLE_TITLE.get(slot, slot))}">'
            f'{body}</svg>')


# ---------------------------------------------------------------------------
# 01 HERO -- identity as an adobe settlement whose massing encodes the repo
# ---------------------------------------------------------------------------
def render_hero(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "hero"
    w, h, out = _scene(d, "h", light)
    out += _header(d, "identity", f"{len(d.get('routes') or [])} routes", light, w)
    p = palette(d["palette"])
    rng = C.rng_for(name, "hero")

    # A stepped settlement: three massing blocks sized from the measured shape.
    routes = len(d.get("routes") or [])
    modules = len(d.get("major_modules") or [])
    tiers = 3 + min(routes % 4, 2)
    bx = 96
    out.append(C.ground_shadow(bx + 120, GROUND_Y + 6, 150, 22))
    for i in range(tiers):
        wdt = 250 - i * 46
        y = GROUND_Y - (i + 1) * 46
        colr = C.tint(p["mass"], 0.06 * i)
        grp = C.clay_box(bx + i * 23, y, wdt, 48, 16, colr, r=8)
        if motion:
            grp = f'<g>{grp}{C.settle(bx + i * 23, y, bx + i * 23, y, 0.9, i * 0.28)}</g>'
        out.append(grp)

    # The gateway carries the route count as visible mass.
    gw = 132 + min(routes, 12) * 6
    out.append(C.clay_arch(392, GROUND_Y - 150, gw, 150, p["alt"], d=18))
    # Always draw the sphere. An earlier version appended it only under
    # "if motion:", which deleted it from every reduced-motion and static
    # rendering -- and a README image is always rendered statically.
    mark = C.clay_sphere(392 + gw / 2, GROUND_Y - 96, 13, p["cool"])
    if motion:
        mark = f'<g>{mark}{C.breathe("0.78;1;0.78", 5.2)}</g>'
    out.append(mark)

    out.append(C.clay_tree(632, GROUND_Y, 60, 146, p["cool"]))
    out.append(C.clay_cactus(772, GROUND_Y, 46, 104, p["cool"]))
    if modules:
        # Foreground plinths sit below the horizon line and are drawn last, so
        # they read as being nearer the viewer than the settlement.
        # Warm mass colour, not sand-on-sand: the plinths were invisible
        # against the ground.
        for i, m in enumerate(d["major_modules"][:3]):
            out.append(C.ground_shadow(200 + i * 106, 404, 42, 7, 0.15))
            grp = C.clay_box(160 + i * 106, 366, 82, 34, 12,
                             p["mass"] if i % 2 == 0 else C.tint(p["mass"], 0.14), r=8)
            if motion:
                grp = f'<g>{grp}{C.settle(160 + i * 106, 366, 160 + i * 106, 366, 0.7, 0.8 + i * 0.15)}</g>'
            out.append(grp)
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "hero", motion)


# ---------------------------------------------------------------------------
# 02 TERMINAL -- a clay console block with a lit screen
# ---------------------------------------------------------------------------
def render_terminal(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "terminal"
    w, h, out = _scene(d, "t", light)
    tid = seed_of(name, "lamp") % 100000
    out += _header(d, "entry points", None, light, w)
    p = palette(d["palette"])

    sx, sy, sw, sh = 96, 150, 470, 190
    out.append(C.ground_shadow(sx + sw / 2, GROUND_Y + 8, sw * 0.56, 20))
    out.append(C.clay_box(sx - 18, sy - 18, sw + 36, sh + 46, 20, p["mass"], r=18))
    out.append(C.plaque(sx, sy, sw, sh, C.tint(p["sky"], -0.28 if not light else 0.5), r=12))
    # A warm lamp glow inside the screen.
    out.append(C.lamp(sx + sw - 74, sy + 48, 78, f"lamp{tid}"))

    lines = [str(x) for x in (d.get("terminal_lines") or [])][:5]
    if not lines:
        lines = ["(no executable entry point detected)"]
    for i, line in enumerate(lines):
        yy = sy + 44 + i * 30
        out.append(C.bar(sx + 20, yy - 13, 12, 12, P["cactus"], r=4))
        out.append(C.label(sx + 44, yy, line[:44],
                           P["cream"] if not light else C.PALETTE["dusk_deep"], 14))
        if motion and i < 3:
            out[-1] = f'<g>{out[-1]}{C.settle(sx + 44, yy, sx + 44, yy, 0.7, 0.4 + i * 0.3)}</g>'

    # Entry points stand as small clay plinths beside the console.
    for i in range(min(len(lines), 4)):
        out.append(C.clay_box(624 + i * 62, GROUND_Y - 34 - i * 8, 48, 34 + i * 8, 12,
                              p["alt"], r=8))
    out.append(C.clay_cactus(846, GROUND_Y, 44, 96, p["cool"]))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "terminal", motion)


# ---------------------------------------------------------------------------
# 03 ARCHITECTURE -- module roots as a stacked clay terrace
# ---------------------------------------------------------------------------
def render_architecture(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "architecture"
    w, h, out = _scene(d, "a", light)
    out += _header(d, "module roots", f"{len(d.get('major_modules') or [])} modules", light, w)
    p = palette(d["palette"])
    mods = [str(m) for m in (d.get("major_modules") or [])][:6]

    out.append(C.ground_shadow(250, GROUND_Y + 6, 170, 22))
    if mods:
        out.append(C.clay_mesa(112, 168, 268, 184, max(len(mods), 2), p["mass"], d=18))
        for i, m in enumerate(mods[:4]):
            yy = 196 + i * 38
            out.append(C.plaque(140, yy, 150, 26, C.alpha(P["cream"], 0.16), r=8))
            out.append(C.label(150, yy + 19, m[:20], P["cream"] if not light else C.PALETTE["dusk_deep"], 12))
            if motion:
                out[-1] = f'<g>{out[-1]}{C.settle(150, yy, 150, yy, 0.7, 0.3 + i * 0.2)}</g>'
    else:
        out.append(C.clay_box(150, 250, 190, 102, 16, p["mass"], r=14))
        out.append(C.label(178, 300, "flat layout", P["cream"] if not light else C.PALETTE["dusk_deep"], 16))

    out.append(C.clay_arch(430, 214, 138, 138, p["alt"], d=16))
    out.append(C.clay_tree(636, GROUND_Y, 58, 142, p["cool"]))
    out.append(C.clay_sphere(722, GROUND_Y - 22, 24, p["cool"]))
    out.append(C.clay_cylinder(778, GROUND_Y - 52, 46, 52, p["mass"]))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "architecture", motion)


# ---------------------------------------------------------------------------
# 04 DATA FLOW -- a road of clay pavers between two masses
# ---------------------------------------------------------------------------
def render_data_flow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "data_flow"
    w, h, out = _scene(d, "d", light)
    stages = [str(s) for s in (d.get("pipeline_stages") or [])][:5]
    out += _header(d, "routes", f"{len(d.get('routes') or [])} endpoints", light, w)
    p = palette(d["palette"])
    if not stages:
        stages = ["no route surface"]

    n = len(stages)
    gap = 640 / max(n, 1)
    # The road.
    out.append(C.bar(120, GROUND_Y - 12, 660, 16, C.tint("beige", -0.18), r=8))
    for i in range(n):
        x = 132 + i * gap
        grp = C.clay_box(x, GROUND_Y - 74 - (i % 2) * 14, 84, 62, 14,
                         p["mass"] if i % 2 == 0 else p["alt"], r=10)
        if motion:
            grp = f'<g>{grp}{C.settle(x, GROUND_Y - 74, x, GROUND_Y - 74, 0.8, i * 0.26)}</g>'
        out.append(grp)
        out.append(C.label(x + 42, GROUND_Y + 30, stages[i][:14],
                           P["clay_red"] if not light else C.PALETTE["dusk_deep"], 11,
                           anchor="middle"))
        if i:
            px = 132 + (i - 1) * gap + 84
            out.append(C.bar(px + 6, GROUND_Y - 6, max(gap - 96, 12), 5, P["sun"], r=3))
            if motion:
                out[-1] += C.animate("opacity", "0.3;1;0.3", 3.4, i * 0.5)
    out.append(C.clay_arch(742, 236, 118, 116, p["alt"], d=14))
    out.append(C.clay_tree(854, GROUND_Y, 42, 104, p["cool"]))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "data_flow", motion)


# ---------------------------------------------------------------------------
# 05 STATE MACHINE -- three clay tokens passing through a gateway
# ---------------------------------------------------------------------------
def render_state_machine(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "state_machine"
    w, h, out = _scene(d, "s", light)
    prims = [str(x) for x in (d.get("cs_primitives") or [])][:4]
    out += _header(d, "primitives", f"{len(prims)} detected", light, w)
    p = palette(d["palette"])
    prims = prims or ["no primitive matched"]

    out.append(C.clay_arch(388, 168, 160, 184, p["alt"], d=18))
    states = ["in", *prims[:3], "out"]
    gap = 720 / max(len(states) - 1, 1)
    for i, s in enumerate(states):
        x = 96 + i * gap
        colr = p["cool"] if i in (0, len(states) - 1) else p["mass"]
        if motion and 0 < i < len(states) - 1:
            out.append(f'<g>{C.clay_sphere(x, GROUND_Y - 46, 26, colr)}'
                       f'{C.breathe("0.8;1;0.8", 4.0 + i * 0.6)}</g>')
        else:
            out.append(C.clay_sphere(x, GROUND_Y - 46, 26, colr))
        out.append(C.label(x, GROUND_Y - 4, s[:15],
                           P["cream"] if not light else C.PALETTE["dusk_deep"], 11,
                           anchor="middle"))
    out.append(C.clay_box(96, GROUND_Y + 16, 90, 26, 10, p["mass"], r=8))
    out.append(C.clay_cactus(812, GROUND_Y, 42, 92, p["cool"]))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "state_machine", motion)


# ---------------------------------------------------------------------------
# 06 COMPONENT MAP -- a brick field of declared dependencies
# ---------------------------------------------------------------------------
def render_component_map(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "component_map"
    w, h, out = _scene(d, "c", light)
    fw = [str(x) for x in (d.get("frameworks") or [])][:8]
    out += _header(d, "composition", f"{len(fw)} declared", light, w)
    p = palette(d["palette"])
    fw = fw or ["no dependency declared"]

    cols = 4
    for i, f in enumerate(fw):
        cx = 108 + (i % cols) * 176
        cy = 176 + (i // cols) * 96
        grp = C.clay_box(cx, cy, 150, 74, 14, p["mass"] if i % 3 else p["alt"], r=12)
        if motion:
            grp = f'<g>{grp}{C.settle(cx, cy, cx, cy, 0.75, i * 0.16)}</g>'
        out.append(grp)
        out.append(C.label(cx + 75, cy + 44, f[:18],
                           P["cream"] if not light else C.PALETTE["dusk_deep"], 12,
                           anchor="middle"))
    out.append(C.clay_tree(760, GROUND_Y, 54, 126, p["cool"]))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "component_map", motion)


# ---------------------------------------------------------------------------
# 07 BUILD -- crates stacked by real test and CI counts
# ---------------------------------------------------------------------------
def render_build(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "build"
    w, h, out = _scene(d, "b", light)
    testing = d.get("testing") or {}
    tests = int(testing.get("count") or 0)
    ci = len((d.get("evidence") or {}).get("ci_workflows") or [])
    out += _header(d, "build and tests", f"{tests} test files", light, w)
    p = palette(d["palette"])

    # One crate per ten test files, so the stack height is the measurement.
    crates = max(1, min(6, tests // 10 + (1 if tests % 10 else 0)))
    out.append(C.ground_shadow(210, GROUND_Y + 6, 130, 20))
    for i in range(crates):
        grp = C.clay_box(140 + i * 12, GROUND_Y - 46 - i * 42, 130, 40, 12,
                         p["mass"] if i % 2 == 0 else p["alt"], r=8)
        if motion:
            grp = f'<g>{grp}{C.settle(140 + i * 12, GROUND_Y - 46 - i * 42,
                                      140 + i * 12, GROUND_Y - 46 - i * 42,
                                      0.8, 0.5 - i * 0.16)}</g>'
        out.append(grp)
    out.append(C.label(140, GROUND_Y + 24, f"{tests} test files", P["clay_red"]
                       if not light else C.tint("dusk_deep", 0.2), 13))

    # The CI block, lit from within when workflows exist.
    cx0 = 430
    out.append(C.clay_box(cx0, 232, 200, 120, 16, p["alt"], r=14))
    lit = ci > 0
    out.append(C.plaque(cx0 + 20, 252, 160, 80,
                        P["sun"] if lit else C.tint(p["mass"], -0.2), r=10))
    out.append(C.label(cx0 + 100, 292, f"{ci} CI", C.PALETTE["dusk_deep"] if lit
                       else P["cream"], 24, anchor="middle"))
    out.append(C.label(cx0, 378, "workflows", P["clay_red"] if not light
                       else C.tint("dusk_deep", 0.2), 13))
    if lit and motion:
        out[-1] = f'<g>{out[-1]}{C.breathe("0.55;1;0.55", 4.6)}</g>'

    out.append(C.clay_cylinder(700, GROUND_Y - 96, 48, 96, p["mass"]))
    out.append(C.clay_cactus(786, GROUND_Y, 46, 104, p["cool"]))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "build", motion)


# ---------------------------------------------------------------------------
# 08 WORKFLOW -- clay steps, one per ordered step
# ---------------------------------------------------------------------------
def render_workflow(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "workflow"
    w, h, out = _scene(d, "w", light)
    steps = [str(s) for s in (d.get("workflow_steps") or [])][:5]
    out += _header(d, "workflow", f"{len(steps)} steps", light, w)
    p = palette(d["palette"])
    steps = steps or ["single step"]

    for i, s in enumerate(steps):
        x = 108 + i * 142
        hh = 40 + i * 26
        grp = C.clay_box(x, GROUND_Y - hh, 116, hh, 14,
                         p["mass"] if i % 2 == 0 else p["alt"], r=10)
        if motion:
            grp = f'<g>{grp}{C.settle(x, GROUND_Y - hh, x, GROUND_Y - hh, 0.8, i * 0.22)}</g>'
        out.append(grp)
        out.append(C.label(x + 58, GROUND_Y + 26, s[:14],
                           P["clay_red"] if not light else C.PALETTE["dusk_deep"], 11,
                           anchor="middle"))
    out.append(C.clay_tree(822, GROUND_Y, 46, 112, p["cool"]))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "workflow", motion)


# ---------------------------------------------------------------------------
# 09 DOMAIN -- the problem the repository addresses, as landscape
# ---------------------------------------------------------------------------
def render_domain(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "domain"
    w, h, out = _scene(d, "m", light)
    out += _header(d, "domain", str(d.get("domain") or "")[:26], light, w)
    p = palette(d["palette"])
    pos = str(d.get("problem") or d.get("public_positioning") or "")

    out.append(C.ground_shadow(300, GROUND_Y + 6, 200, 22))
    out.append(C.clay_mesa(120, 206, 250, 146, 3, p["mass"], d=18))
    out.append(C.clay_arch(408, 232, 128, 120, p["alt"], d=14))
    out.append(C.clay_sphere(586, GROUND_Y - 30, 26, p["cool"]))
    out.append(C.clay_cactus(664, GROUND_Y, 48, 108, p["cool"]))
    out.append(C.clay_tree(748, GROUND_Y, 58, 138, p["cool"]))
    if pos:
        out.append(C.plaque(108, 132, 520, 46, C.alpha(P["dusk_deep"], 0.42), r=12))
        out.append(C.label(124, 161, pos[:62], P["cream"], 14))
    out += _footer_strip(d, light, 418, h)
    return _doc("".join(out), w, h, d, "domain", motion)


# ---------------------------------------------------------------------------
# 10 FOOTER -- a small clay sun mark and the wordmark
# ---------------------------------------------------------------------------
def render_footer(d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    d["_slot"] = "footer"
    w, h, out = _scene(d, "f", light, sun=False, clouds=False)
    p = palette(d["palette"])
    ink = P["cream"] if not light else C.PALETTE["dusk_deep"]

    out.append(C.ground_shadow(112, 150, 62, 12))
    mark = C.clay_mesa(74, 74, 78, 76, 3, p["mass"], d=12)
    if motion:
        mark = f'<g>{mark}{C.breathe("0.72;1;0.72", 6.0)}</g>'
    out.append(mark)
    out.append(C.clay_arch(160, 84, 56, 66, p["alt"], d=10))
    out.append(C.label(246, 108, d["canonical_name"][:30], ink, 26))
    out.append(C.label(248, 136, "DUNG30N5 x NOAERTH", P["sand"] if not light
                       else C.tint("clay_red", 0.2), 15))
    out.append(C.label(248, 162,
                       f"{d['project_category'].replace('_', ' ').title()}  /  "
                       f"{d['status']}  /  evidence {d['confidence']}", ink, 13))
    out.append(C.clay_cactus(830, 152, 34, 66, p["cool"]))
    return _doc("".join(out), w, h, d, "footer", motion)


RENDERERS = {
    "hero": render_hero,
    "terminal": render_terminal,
    "architecture": render_architecture,
    "state_machine": render_state_machine,
    "data_flow": render_data_flow,
    "component_map": render_component_map,
    "build": render_build,
    "workflow": render_workflow,
    "domain": render_domain,
    "footer": render_footer,
}


def render(slot: str, d: dict, name: str, light: bool = False, motion: bool = True) -> str:
    return RENDERERS[slot](d, name, light, motion)
