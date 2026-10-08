"""Render the profile hero in the New Mexico clay language.

assets/hero/hero-{motion,light,reduced}.svg is the first thing a visitor sees
on the profile repository and is referenced directly by the README banner, so it
is rendered here rather than by the per-repository pipeline. assets/profile/**
belongs to generate.py and stays art-locked; this file does not touch it.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay as C  # noqa: E402
import clay_renderers as R  # noqa: E402
import evidence as E  # noqa: E402

PROFILE = HERE.parents[2]
OUT = PROFILE / "assets" / "hero"
W, H = 1200, 560

VARIANTS = (("motion", False, True), ("light", True, True), ("reduced", False, False))


def payload(index: dict, manifest: dict) -> dict:
    routes = sum(len(r.get("routes") or []) for r in index.values())
    files = sum(r.get("files") or 0 for r in index.values())
    tests = sum(r.get("test_count") or 0 for r in index.values())
    surfaces = sum(len(v["files"]) for v in manifest.values())
    p = C.CLAY_PALETTES["mesa_terracotta"]

    return {
        "canonical_name": "DUNG30N5",
        "repo": E.OWNER,
        "palette": "mesa_terracotta",
        "project_category": "PORTFOLIO",
        "status": "PORTFOLIO",
        "confidence": "E3",
        "domain": "Venture operating company",
        "routes": [],
        "major_modules": [],
        "cs_primitives": [],
        "frameworks": [],
        "terminal_lines": [
            f"{len(index)} public repositories",
            f"{files:,} files analysed",
            f"{routes:,} HTTP routes",
            f"{tests:,} test files",
            f"{surfaces:,} generated surfaces",
        ],
        "testing": {"count": tests},
        "evidence": {"ci_workflows": []},
        "problem": ("Building the operating layer for venture creation: "
                    "measurable, inspectable software instead of claims."),
        "_p": p,
    }


def render_hero(d: dict, light: bool, motion: bool) -> str:
    p = d["_p"]
    sky = p["sky"] if not light else C.tint(p["sky"], 0.68)
    ground = C.PALETTE["sand"] if not light else C.tint("sand", 0.34)
    ink = C.PALETTE["cream"] if not light else C.PALETTE["dusk_deep"]
    sub = C.PALETTE["sand"] if not light else C.tint("clay_red", -0.22)
    gid = "ph" + ("l" if light else "d")
    gy = 430

    o = [C.sky(W, H, sky, f"sky{gid}"), C.clay_sun(1010, 118, 52, f"sun{gid}")]
    o.append(f'<g>{C.clay_cloud(560, 84, 50, C.PALETTE["cream"])}{C.drift(28, 40)}</g>')
    o.append(f'<g>{C.clay_cloud(742, 52, 34, C.PALETTE["cream"])}{C.drift(-20, 52, 3)}</g>')
    o.append(C.ground(W, H, gy, ground))

    # Wordmark, set in the blocky system type.
    o.append(C.label(72, 150, "DUNG30N5", ink, 78, spacing=2.2))
    o.append(C.label(76, 196, "TECHNOLOGIST AND FOUNDER OF NOAERTH", sub, 22, spacing=3.0))
    o.append(C.bar(76, 220, 150, 7, C.PALETTE["sun"], r=4))

    # The measured ledger, as clay plinths rather than a data table.
    rows = d["terminal_lines"]
    # Four plinths must end before the settlement starts at x=700; the previous
    # 196px pitch ran the fourth one underneath the mesa and clipped its label.
    for i, row in enumerate(rows[:3]):
        x = 72 + i * 158
        head, _, tail = row.partition(" ")
        grp = C.clay_box(x, 268, 138, 64, 13,
                         p["mass"] if i % 2 == 0 else C.tint(p["mass"], 0.14), r=9)
        if motion:
            grp = f'<g>{grp}{C.settle(x, 268, x, 268, 0.8, 0.3 + i * 0.2)}</g>'
        o.append(grp)
        o.append(C.label(x + 13, 294, head[:9],
                         C.PALETTE["cream"] if not light else C.PALETTE["dusk_deep"], 19))
        o.append(C.label(x + 13, 318, tail[:14], sub, 13))

    # The settlement: the portfolio as an adobe massing.
    o.append(C.ground_shadow(880, gy + 6, 210, 26))
    for i in range(4):
        wdt = 300 - i * 54
        x = 700 + i * 28
        y = gy - (i + 1) * 52
        grp = C.clay_box(x, y, wdt, 54, 18, C.tint(p["mass"], 0.05 * i), r=9)
        if motion:
            grp = f'<g>{grp}{C.settle(x, y, x, y, 0.9, i * 0.3)}</g>'
        o.append(grp)
    o.append(C.clay_arch(1010, 250, 132, 180, p["alt"], d=18))
    mark = C.clay_sphere(1076, 306, 14, p["cool"])
    if motion:
        mark = f'<g>{mark}{C.breathe("0.8;1;0.8", 5.4)}</g>'
    o.append(mark)
    # Vegetation lives in the gap between the ledger plinths and the
    # settlement; drawn after the plinths it was covering the fourth one.
    o.append(C.clay_cactus(566, gy, 48, 108, p["cool"]))
    o.append(C.clay_tree(648, gy, 58, 142, p["cool"]))

    if not motion:
        import re
        body = "".join(o)
        body = re.sub(r"<animate[^>]*/>", "", body)
        body = re.sub(r"<animateTransform[^>]*/>", "", body)
        return _wrap(body, light, ink)
    return _wrap("".join(o), light, ink)


def _wrap(body: str, light: bool, ink: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="DUNG30N5, technologist and founder of NOAERTH">'
            f'{body}</svg>')


def main() -> int:
    import json
    index = E.load_index()
    mpath = PROFILE / ".github-art" / "v8-art" / "manifest.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    d = payload(index, manifest)

    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, light, motion in VARIANTS:
        svg = render_hero(d, light, motion)
        (OUT / f"hero-{suffix}.svg").write_text(svg)
        print(f"  hero-{suffix}.svg  {len(svg):,} bytes  "
              f"animate={svg.count('<animate')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
