"""The profile hero banner: desert scene behind, information on solid slabs.

Same slab system as the ten plates, so the banner and the plates read as one
system. assets/profile/** belongs to generate.py and stays art-locked; this file
does not touch it.
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

PROFILE = HERE.parents[2]
OUT = PROFILE / "assets" / "hero"
W, H = 1200, 560
HORIZON = 418
PAL = C.CLAY_PALETTES["mesa_terracotta"]

VARIANTS = (("motion", False, True), ("light", True, True), ("reduced", False, False))


def figures(index: dict, manifest: dict) -> list[tuple[str, str]]:
    routes = sum(len(r.get("routes") or []) for r in index.values())
    files = sum(r.get("files") or 0 for r in index.values())
    tests = sum(r.get("test_count") or 0 for r in index.values())
    surfaces = sum(len(v["files"]) for v in manifest.values())
    return [
        (f"{len(index)}", "repositories"),
        (f"{routes:,}", "http routes"),
        (f"{files:,}", "files analysed"),
        (f"{surfaces:,}", "surfaces"),
    ]


def strip_animations(body: str) -> str:
    import re
    body = re.sub(r"<animate[^>]*/>", "", body)
    return re.sub(r"<animateTransform[^>]*/>", "", body)


def render(tiles: list[tuple[str, str]], light: bool, motion: bool) -> str:
    g = "ph" + ("l" if light else "d")
    ink = X.slab_ink(light)
    sub = X.slab_sub(light)
    fills = X.SLAB_LIGHT if light else X.SLAB_DARK

    o = [X.defs(g, PAL, light)]
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>')
    sx, sy, sr = W - 168, 104, 46
    o.append(f'<g><circle cx="{sx}" cy="{sy}" r="{_sr(sr * 2.5)}" fill="url(#halo{g})">'
             f'{X.halo_loop(sr * 2.2, sr * 2.8, 16)}</circle>'
             f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{C.PALETTE["sun"]}"/>'
             f'</g>')
    o.append(N.cloud(596, 84, 44, 28) if hasattr(N, "cloud") else "")
    o.append(f'<rect x="0" y="{HORIZON - 40}" width="{W}" height="40" '
             f'fill="{C.alpha(C.PALETTE["peach"], 0.15)}"/>')
    o.append(N.ridges(W, HORIZON))

    # Pavement with converging seams, then the roadway and its crosswalk.
    o.append(f'<rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" '
             f'fill="url(#floor{g})"/>')
    vx = W * 0.5
    for k in range(-11, 12):
        o.append(f'<path d="M{_sr(vx)},{HORIZON} L{_sr(vx + k * 200)},{H}" '
                 f'stroke="{C.alpha(C.PALETTE["beige"], 0.20)}" stroke-width="2"/>')
    y, step = HORIZON + 5, 6.0
    while y < H + 60:
        o.append(f'<rect x="0" y="{_sr(y)}" width="{W}" height="{_sr(step * 0.30)}" '
                 f'fill="{C.alpha(C.PALETTE["beige"], 0.40)}"/>')
        y += step
        step *= 1.36
    o.append(D.curb(W, HORIZON, 22, "sand", "beige"))
    road = C.tint(C.PALETTE["dusk_soft"], -0.34)
    o.append(f'<rect x="0" y="{HORIZON + 22}" width="{W}" height="{H - HORIZON - 22}" '
             f'fill="{road}"/>')
    o.append(D.crosswalk(W, HORIZON + 22, H - HORIZON - 22, 9))

    # Architecture on the right half, so the figure tiles own the left over open
    # sky. Receding masses are pushed back with opacity, which is what makes the
    # street read as deep rather than as a row of boxes.
    STREET = HORIZON
    o.append(D.haze(214, 92, W, C.PALETTE["peach"], 0.15))
    o.append(D.depth_fade(D.building(700, 116, 128, 302, 5, "clay_red", g, 0.55, 2, 2), 0.88))
    o.append(D.depth_fade(D.building(822, 148, 112, 270, 5, "terracotta", g, 0.48, 5, 0), 0.74))
    o.append(D.depth_fade(D.building(928, 178, 104, 240, 4, "coral", g, 0.42, 7, 0), 0.58))
    o.append(D.building(560, 76, 146, 342, 7, "adobe", g, 0.68, 1, 2))
    o.append(D.awning(560, 320, 146, 18, "coral", "cream", 6))
    o.append(D.sign_board(572, 292, 122, 24, "cream", "clay_red"))
    o.append(f"<g>{N.crt(574, 322, 76, 66, 'beige', 'dusk_deep', g)}"
             f'{X.hover_loop(3.0, X.loop_dur(2), X.loop_begin(2))}</g>')
    o.append(D.festoon(560, 268, 706, 252, 12, 15, g))
    o.append(f'<g>{D.lamp_post(524, STREET, 78, g)}'
             f'{X.glow_loop(0.86, 1.0, X.loop_dur(3), X.loop_begin(3))}</g>')
    o.append(D.bollard(500, STREET))
    o.append(D.bollard(900, STREET))
    o.append(f"<g>{D.figure(646, STREET, 60, 'turquoise', 'clay_red', g)}"
             f'{D_drift(4)}</g>')
    o.append(f"<g>{D.figure(700, STREET, 56, 'ember', 'dusk_deep', g)}"
             f'{D_drift(5)}</g>')
    o.append(f"<g>{N.satellite(470, 138, 36, 'coral', 'turquoise')}"
             f'{X.drift_loop(16, X.loop_dur(1), X.loop_begin(1))}</g>')
    o.append(N.agave(452, STREET, 48, 66, "sage"))
    o.append(X.conifer(408, STREET, 54, 128, PAL["cool"], X.loop_dur(4), X.loop_begin(4)))
    o.append(N.boulder(348, STREET, 62, 26, "beige"))

    # Information: title slab, four figure tiles, footer slab.
    o.append(X.slab(72, 150, 470, 82, fills["title"], light=light, r=14))
    o.append(X.label(96, 190, "DUNG30N5", ink, 40))
    o.append(X.label(97, 216, "TECHNOLOGIST AND FOUNDER OF NOAERTH", sub, 15))

    pitch, tw, th = 178, 162, 88
    for i, (value, label) in enumerate(tiles[:4]):
        tx = 72 + i * pitch
        o.append(X.slab(tx, 258, tw, th, fills["tile"], light=light, r=13))
        o.append(f"<g>{X.label(tx + 16, 296, value[:9], ink, 26)}"
                 f'{X.hover_loop(2.6, 7.6 + i * 0.7, i * 0.6)}</g>')
        o.append(X.label(tx + 17, 322, label[:18], sub, 13))

    o.append(X.slab(0, H - 84, W, 84, fills["foot"], light=light, r=0, shadow=False))
    o.append(X.label(72, H - 34,
                     "DUNG30N5 x NOAERTH  /  portfolio  /  evidence E3", ink, 16))
    o.append(X.label(1128, H - 34, "noaerth.com", sub, 16, anchor="end"))

    body = "".join(o)
    if not motion:
        body = strip_animations(body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="DUNG30N5, technologist and founder of NOAERTH">'
            f'{body}</svg>')


def D_drift(i: int) -> str:
    return X.drift_loop(7, X.loop_dur(i), X.loop_begin(i))


def _sr(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def main() -> int:
    import json
    index = E_load_index()
    mpath = PROFILE / ".github-art" / "v8-art" / "manifest.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    tiles = figures(index, manifest)

    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, light, motion in VARIANTS:
        svg = render(tiles, light, motion)
        (OUT / f"hero-{suffix}.svg").write_text(svg)
        print(f"  hero-{suffix}.svg  {len(svg):,} bytes  "
              f"loops={svg.count('repeatCount=')}")
    return 0


def E_load_index():
    import evidence
    return evidence.load_index()


if __name__ == "__main__":
    raise SystemExit(main())