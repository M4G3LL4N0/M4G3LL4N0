"""The profile hero banner, in the deeper clay language with closed loops.

assets/hero/hero-{motion,light,reduced}.svg is the first thing a visitor sees
on the profile repository, so it is rendered here rather than by the
per-repository pipeline. assets/profile/** belongs to generate.py and stays
art-locked; this file does not touch it.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay as C  # noqa: E402
import clay3d as X  # noqa: E402
import evidence as E  # noqa: E402

PROFILE = HERE.parents[2]
OUT = PROFILE / "assets" / "hero"
W, H = 1200, 560
HORIZON = 430
PAL = C.CLAY_PALETTES["mesa_terracotta"]

VARIANTS = (("motion", False, True), ("light", True, True), ("reduced", False, False))


def metrics(index: dict, manifest: dict) -> list[str]:
    routes = sum(len(r.get("routes") or []) for r in index.values())
    files = sum(r.get("files") or 0 for r in index.values())
    tests = sum(r.get("test_count") or 0 for r in index.values())
    surfaces = sum(len(v["files"]) for v in manifest.values())
    return [
        f"{len(index)} public repositories",
        f"{files:,} files analysed",
        f"{routes:,} HTTP routes",
        f"{tests:,} test files",
        f"{surfaces:,} surfaces",
    ]


def render(rows: list[str], light: bool, motion: bool) -> str:
    g = "ph" + ("l" if light else "d")
    ink = C.PALETTE["cream"] if not light else C.PALETTE["dusk_deep"]
    sub = C.PALETTE["sand"] if not light else C.tint("clay_red", -0.52)

    o = [X.defs(g, PAL, light), X.backdrop(W, H, HORIZON, PAL, g, light)]
    o.append(X.cloud(560, 96, 46, 30, 0))
    o.append(X.cloud(742, 58, 32, 38, 7, 5))

    # Wordmark.
    o.append(X.label(72, 158, "DUNG30N5", ink, 78, spacing=2.4))
    o.append(X.label(76, 202, "TECHNOLOGIST AND FOUNDER OF NOAERTH", sub, 22, spacing=3.0))
    o.append(X.plaque(76, 224, 150, 7, C.PALETTE["sun"], r=4))

    # The measured ledger, as chamfered clay plinths.
    for i, row in enumerate(rows[:3]):
        head, _, tail = row.partition(" ")
        x = 72 + i * 158
        fill = PAL["mass"] if i % 2 == 0 else C.tint(PAL["mass"], 0.14)
        blk = X.block(x, 272, 138, 66, 14, fill, r=9, gid=g)
        o.append(f"<g>{blk}{X.hover_loop(3.4, 7.8 + i * 0.8, i * 0.7)}</g>")
        o.append(X.label(x + 13, 300, head[:9], ink, 19))
        o.append(X.label(x + 13, 324, tail[:14], sub, 13))

    # The settlement.
    o.append(X.cast_shadow(880, HORIZON + 10, 220, 24, g, skew=-6))
    tiers = "".join(
        X.block(700 + i * 30, HORIZON - (i + 1) * 56, 300 - i * 56, 58, 20,
                C.tint(PAL["mass"], 0.06 * i), r=10)
        for i in range(4))
    o.append(f'<g>{tiers}'
             + "".join(X.hover_loop(3.0 + i * 0.6, 8.4 + i * 0.8, i * 0.6)
                       for i in range(4)) + "</g>")
    o.append(X.gateway(1010, 250, 132, 180, PAL["alt"], g, 10))
    o.append(f'<g>{X.ball(1076, 306, 15, PAL["cool"], 8.5, 0.5)}</g>')
    o.append(X.cactus(566, HORIZON, 50, 112, PAL["cool"], 12, 0))
    o.append(X.conifer(650, HORIZON, 60, 144, PAL["cool"], 13, 2))

    body = "".join(o)
    if not motion:
        body = PS_strip(body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="DUNG30N5, technologist and founder of NOAERTH">'
            f'{body}</svg>')


def PS_strip(body: str) -> str:
    import re
    body = re.sub(r"<animate[^>]*/>", "", body)
    return re.sub(r"<animateTransform[^>]*/>", "", body)


def main() -> int:
    import json
    index = E.load_index()
    mpath = PROFILE / ".github-art" / "v8-art" / "manifest.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    rows = metrics(index, manifest)

    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, light, motion in VARIANTS:
        svg = render(rows, light, motion)
        (OUT / f"hero-{suffix}.svg").write_text(svg)
        print(f"  hero-{suffix}.svg  {len(svg):,} bytes  "
              f"loops={svg.count('repeatCount=')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())