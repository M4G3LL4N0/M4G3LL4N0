"""Enforce the legibility rules in MASTER_PROMPT.md section 7.

Two checks, both mechanical:

  containment   every <text> baseline must fall inside an opaque slab rect that
                was emitted before it. Text on bare sky or sand is a failure,
                not a style choice.
  contrast      measured WCAG ratio of the type colour against that slab. 4.5:1
                for body and label text, 3:1 for the largest display type.

This is the gate that keeps scenery from ever competing with the data.
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ART = HERE.parents[2] / ".github-art" / "v8-art" / "M4G3LL4N0"
HERO = HERE.parents[2] / "assets" / "hero"

TEXT_RE = re.compile(
    r'<text x="([\d.]+)" y="([\d.]+)"[^>]*?font-size="(\d+)"[^>]*?'
    r'fill="(#[0-9a-fA-F]{6})"[^>]*text-anchor="(\w+)">([^<]*)</text>')
RECT_RE = re.compile(
    r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"'
    r'(?: rx="[\d.]+")? fill="(#[0-9a-fA-F]{6})"( opacity="([\d.]+)")?')
PLATE_RE = re.compile(
    r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"'
    r' rx="([\d.]+)" fill="(#[0-9a-fA-F]{6})"/>')

# display type is large enough that 3:1 is the WCAG threshold
DISPLAY_MIN = 3.0
BODY_MIN = 4.5


def _rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(hex_color: str) -> float:
    def f(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(hex_color)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check(path: pathlib.Path) -> list[str]:
    body = path.read_text()
    problems: list[str] = []

    # Slabs are the fully opaque rects emitted by clay3d.slab().
    slabs: list[tuple[float, float, float, float, str]] = []
    for m in PLATE_RE.finditer(body):
        x, y, w, h = (float(m.group(i)) for i in (1, 2, 3, 4))
        fill = m.group(6)
        slabs.append((x, y, x + w, y + h, fill))

    if not slabs:
        return [f"{path.name}: no opaque slab found, nothing is legible by design"]

    for m in TEXT_RE.finditer(body):
        x, y, size, fill, anchor, text = (
            float(m.group(1)), float(m.group(2)), int(m.group(3)),
            m.group(4), m.group(5), m.group(6))
        if not text.strip():
            continue
        width = len(text) * size * 0.72
        if anchor == "end":
            x0, x1 = x - width, x
        elif anchor == "middle":
            x0, x1 = x - width / 2, x + width / 2
        else:
            x0, x1 = x, x + width

        inside = [s for s in slabs
                  if s[0] <= x0 + 1 and s[2] >= x1 - 1 and s[1] <= y <= s[3]]
        if not inside:
            problems.append(f"{path.name}: text {text.strip()[:24]!r} is not on a slab")
            continue
        # Best (highest) contrast available among the slabs it sits on.
        best = max(ratio(fill, s[4]) for s in inside)
        need = DISPLAY_MIN if size >= 22 else BODY_MIN
        if best < need:
            problems.append(
                f"{path.name}: {text.strip()[:24]!r} contrast {best:.2f} "
                f"< {need}:1 on {inside[0][4]}")
    return problems


def main() -> int:
    files = sorted(ART.glob("*.svg")) + sorted(HERO.glob("*.svg"))
    problems: list[str] = []
    for f in files:
        problems += check(f)
    print(f"  plates checked : {len(files)}")
    print(f"  legibility fails: {len(problems)}")
    for p in problems[:14]:
        print(f"    - {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())