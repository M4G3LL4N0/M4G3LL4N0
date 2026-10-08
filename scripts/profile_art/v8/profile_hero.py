"""The profile hero banner: laptop in the red rocks (reference photo #1)."""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diorama as M  # noqa: E402
import evidence as E  # noqa: E402

PROFILE = HERE.parents[2]
OUT = PROFILE / "assets" / "hero"
W, H = 1200, 560
HORIZON = 400

VARIANTS = (("motion", False, True), ("light", True, True), ("reduced", False, False))


def figures(index: dict, manifest: dict) -> list[tuple[str, str]]:
    routes = sum(len(r.get("routes") or []) for r in index.values())
    files = sum(r.get("files") or 0 for r in index.values())
    return [
        (f"{len(index)}", "repositories"),
        (f"{routes:,}", "routes"),
        (f"{files:,}", "files"),
        (f"{sum(len(v['files']) for v in manifest.values()):,}", "surfaces"),
    ]


def strip(body: str) -> str:
    import re
    body = re.sub(r"<animate[^>]*/>", "", body)
    return re.sub(r"<animateTransform[^>]*/>", "", body)


def render(tiles: list[tuple[str, str]], light: bool, motion: bool) -> str:
    g = "ph" + ("l" if light else "d")
    mode = "gold" if light else "day"
    o = [M.defs_sky(g, mode), f'<rect width="{W}" height="{H}" fill="url(#sky{g})"/>']
    o.append(M.sun_disc(1004, 92, 40, g, 0))
    o.append(M.block_cloud(560, 66, 46, 1))
    o.append(M.block_cloud(820, 44, 32, 2))
    # canyon walls left and right, river between
    o.append(M.strata_cliff(0, 170, 190, 230, g, 1))
    o.append(M.strata_cliff(1010, 160, 190, 240, g, 2))
    o.append(M.mesa(880, 230, 150, 170, 3, g, 3))
    o.append(M.shadow_ellipse(600, HORIZON + 8, 220, 14, g))
    o.append(M.sand_floor(W, HORIZON, H, 4))
    o.append(M.river(190, HORIZON + 26, 820, 90, g, 3))
    o.append(M.waterfall(300, 250, 40, 150, g))
    o.append(M.mesa(890, 250, 130, 150, 3, g, 5))
    # treeline and blooms
    for cx, w, h, i in ((180, 54, 130, 5), (250, 62, 150, 6), (330, 50, 120, 7),
                        (420, 58, 138, 8), (500, 56, 132, 9)):
        o.append(M.conifer(cx, HORIZON + 4, w, h, i))
    o.append(M.cactus(610, HORIZON + 10, 46, 100, 10))
    o.append(M.flower_patch(40, HORIZON + 60, 200, 14, 11))
    o.append(M.flower_patch(880, HORIZON + 64, 260, 14, 12))
    o.append(M.rock_block(660, HORIZON + 70, 24, 13))
    # the laptop, big, planted on the right bank clear of the tiles
    o.append(M.shadow_ellipse(935, HORIZON + 44, 130, 11, g))
    o.append(M.laptop(810, HORIZON + 40, 250, 14))
    # information on trail signs
    o.append(M.posts(72, 236, 150, 92, 480))
    o.append(M.sign_board(72, 150, 470, 86, night=False, r=12))
    o.append(M.sign_text(96, 192, "DUNG30N5 x NOAERTH", 30))
    o.append(M.sign_text(97, 218, "COMPUTE IN THE WILD", 15))
    pitch, tw, th = 178, 162, 86
    for i, (value, label) in enumerate(tiles[:4]):
        tx = 72 + i * pitch
        o.append(M.posts(tx, 344, 258, tx + 16, tx + tw - 26))
        o.append(M.sign_board(tx, 258, tw, th, night=False, r=12))
        o.append(M.sign_figure(tx + 16, 296, value[:9], 25))
        o.append(M.sign_text(tx + 17, 320, label[:18], 13))
    o.append(M.footer_band(W, H - 64, 64, "DUNG30N5 x NOAERTH / portfolio",
                           "noaerth.com"))
    body = "".join(o)
    if not motion:
        body = strip(body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="DUNG30N5, technologist and founder of NOAERTH">'
            f'{body}</svg>')


def main() -> int:
    import json
    index = E.load_index()
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


if __name__ == "__main__":
    raise SystemExit(main())