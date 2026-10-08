"""Guard the clay primitives against unresolved palette names.

Passing a palette key such as "sand" straight into an SVG fill attribute emits
an invalid colour and the shape silently renders black. That bug shipped three
times while building this system, so it is now checked rather than noticed.
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay as C  # noqa: E402

HEX_RE = re.compile(r'#[0-9a-f]{6}\b|#[0-9a-f]{3}\b|"none"|rgba?\([^)]*\)', re.I)

ATTR_RE = re.compile(
    r'(?:fill|stroke|stop-color|fill-rule)\s*=\s*"([^"]*)"', re.I)

# Attributes whose value is a keyword rather than a colour.
NON_COLOR = {"none", "evenodd", "nonzero", "round", "butt", "miter", "freeze"}


def rendered() -> dict[str, str]:
    """Every primitive, called with a palette key name on purpose."""
    return {
        "clay_box": C.clay_box(10, 40, 60, 40, 12, "sand", r=8),
        "clay_box_nojoin": C.clay_box(10, 40, 60, 40, 12, "adobe", r=8, round_join=0),
        "clay_cylinder": C.clay_cylinder(10, 40, 44, 60, "terracotta"),
        "clay_arch": C.clay_arch(10, 40, 120, 110, "beige"),
        "clay_cone": C.clay_cone(60, 100, 40, 60, "cactus"),
        "clay_tree": C.clay_tree(60, 100, 40, 70, "cactus"),
        "clay_cactus": C.clay_cactus(60, 100, 40, 70, "sage"),
        "clay_mesa": C.clay_mesa(10, 40, 90, 60, 3, "clay_red"),
        "clay_sphere": C.clay_sphere(50, 50, 20, "turquoise"),
        "clay_sun": C.clay_sun(50, 50, 20),
        "clay_cloud": C.clay_cloud(50, 50, 30, "cream"),
        "ground": C.ground(200, 120, 40, "sand"),
        "ground_shadow": C.ground_shadow(50, 50, 30, 8),
        "label": C.label(10, 20, "X", "cream", 14),
        "plaque": C.plaque(10, 10, 80, 30, "dusk_deep"),
        "bar": C.bar(10, 10, 40, 8, "sun", r=4),
        "dot": C.dot(20, 20, 5, "ember"),
        "sky": C.sky(200, 120, "dusk_mid"),
    }


def main() -> int:
    problems: list[str] = []
    for fn, svg in rendered().items():
        for value in ATTR_RE.findall(svg):
            v = value.strip()
            if not v or v in NON_COLOR or v.startswith("url("):
                continue
            if not HEX_RE.fullmatch(v):
                problems.append(f"{fn}: attribute colour {v!r} is not a valid colour")
        # stop-color inside gradients is the other place names leak
        for value in re.findall(r'stop-color="([^"]*)"', svg):
            if not HEX_RE.fullmatch(value.strip()):
                problems.append(f"{fn}: stop-color {value!r} is not a valid colour")

    if problems:
        print(f"  clay colour guard: {len(problems)} problem(s)")
        for p in problems:
            print(f"    - {p}")
        return 1
    print(f"  clay colour guard: {len(rendered())} primitives resolve every colour")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
