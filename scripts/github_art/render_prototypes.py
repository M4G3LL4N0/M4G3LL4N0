#!/usr/bin/env python3
"""Render every direction prototype to a local, uncommitted preview directory.

Rejects are written here and nowhere else. The public repositories must not
accumulate design variants, so nothing in this script targets a tracked path.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from github_art import validators as V  # noqa: E402
from github_art.directions import DIRECTIONS  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "build" / "v5-prototypes"


def main() -> int:
    written = 0
    failures = []
    for slug, mod in DIRECTIONS.items():
        for theme in ("dark", "light"):
            artefacts = {
                "hero": mod.hero(theme),
                "hero-compact": mod.hero(theme, compact=True),
                "flagship-hero": mod.flagship_hero(theme),
                "system-map": mod.system_map(theme),
            }
            for name, content in artefacts.items():
                target = OUT / slug / f"{name}-{theme}.svg"
                try:
                    size = V.validate(content, f"{slug}/{name}")
                    V.check_motion_is_ambient(content, f"{slug}/{name}")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(content, encoding="utf-8")
                    written += 1
                    print(f"  {slug:<30} {name:<16} {theme:<6} {size / 1024:>6.1f} KB")
                except V.ValidationError as exc:
                    failures.append(f"{slug}/{name}/{theme}: {exc}")

    print(f"\n{written} prototypes written to {OUT.relative_to(Path.cwd())}")
    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
