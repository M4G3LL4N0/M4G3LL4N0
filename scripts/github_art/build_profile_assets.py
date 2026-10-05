#!/usr/bin/env python3
"""Generate the shipped V5.1 profile assets into assets/profile/.

Writes only what the profile actually references, then prunes superseded V5
files so the repository never accumulates two generations of artwork. The
profile is the deliverable; the generator exists so it can be rebuilt and
proved reproducible.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts"))

from github_art import project_identity as P  # noqa: E402
from github_art import validators as V  # noqa: E402
from github_art.directions import v51_optical_faceted as D  # noqa: E402

OUT = PROFILE / "assets" / "profile"
SIGNAL = OUT / "build-signal.json"

FLAGS = {
    "agentos": ("710 tests", "green"),
    "grokinstall": ("486 tests", "failure"),
    "grokmax": ("287 tests", "green"),
    "gh0st": ("27 tests", "failure"),
    "opencode-watchdog": ("70 tests", "green"),
}
# Everything below is verified from the live API snapshot, never asserted here.
# The ledger in GITHUB_V5_CONTENT_LEDGER.json is the regression contract.


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    signal = json.loads(SIGNAL.read_text(encoding="utf-8"))
    written: list[Path] = []

    def emit(rel: str, content: str, name: str, budget: float | None = None) -> None:
        V.validate(content, name, budget_kb=budget)
        V.check_motion_is_ambient(content, name)
        path = PROFILE / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    for theme in ("dark", "light"):
        emit(f"assets/profile/hero-{theme}.svg", D.hero(theme), f"hero-{theme}")
        emit(f"assets/profile/hero-{theme}-compact.svg",
             D.hero(theme, compact=True), f"hero-{theme}-compact")
        emit(f"assets/profile/build-signal-{theme}.svg",
             D.build_signal(theme, signal), f"signal-{theme}")
        emit(f"assets/profile/system-map-{theme}.svg",
             D.system_map(theme), f"map-{theme}")
        emit(f"assets/profile/system-map-{theme}-compact.svg",
             D.system_map(theme, compact=True), f"map-{theme}-compact")
        emit(f"assets/profile/terminal-{theme}.svg", D.terminal(theme),
             f"terminal-{theme}")
        for slug, title, subtitle in D.NAV_ITEMS:
            emit(f"assets/profile/nav/{slug}-{theme}.svg",
                 D.nav_chip(slug, title, subtitle, theme),
                 f"nav-{slug}-{theme}")
    emit("assets/profile/hero-motion.svg", D.hero("dark", motion=True), "hero-motion")
    emit("assets/profile/terminal-motion.svg", D.terminal("dark", motion=True),
         "terminal-motion")
    emit("assets/profile/constellation-dark.svg", D.constellation("dark"),
         "constellation-dark", budget=64)
    emit("assets/social-preview.svg", D.social_preview("dark"), "social-preview")

    for slug, (metric, ci) in FLAGS.items():
        for theme in ("dark", "light"):
            emit(f"assets/profile/windows/{slug}-{theme}.svg",
                 D.flagship_window(theme, slug, metric, ci),
                 f"window-{slug}-{theme}")

    # prune superseded V5 art so two generations never coexist in public
    keep = {p.resolve() for p in written}
    pruned = []
    for path in sorted(OUT.rglob("*.svg")):
        if path.resolve() not in keep:
            path.unlink()
            pruned.append(path.relative_to(PROFILE))
    for stray in ("cards", "avatar"):
        d = OUT / stray
        if d.is_dir():
            for path in sorted(d.rglob("*.svg")):
                path.unlink()
            pruned.append(d.relative_to(PROFILE))

    total = sum(p.stat().st_size for p in written)
    print(f"{len(written)} assets, {total / 1024:.1f} KB total")
    print(f"largest: {max((p.stat().st_size / 1024, p.name) for p in written)[0]:.1f} KB")
    if pruned:
        print(f"pruned {len(pruned)} superseded file(s): "
              f"{', '.join(str(p) for p in pruned)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())