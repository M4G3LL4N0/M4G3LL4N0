#!/usr/bin/env python3
"""Rebuild the local review gallery with the V5.1 system.

Shows the Part 1 selection and the V5.1 integration side by side, because the
new direction had to actually be better rather than merely newer. Local only:
design rejects never belong in a public repository.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts"))

from github_art import project_identity as P  # noqa: E402
from github_art import tokens as T  # noqa: E402
from github_art import validators as V  # noqa: E402
from github_art.directions import a_optical_topology as A  # noqa: E402
from github_art.directions import v5_optical_recursive as V5  # noqa: E402
from github_art.directions import v51_optical_faceted as D  # noqa: E402

OUT = PROFILE / "GITHUB_V5_ART_GALLERY.html"
A5 = PROFILE / "build" / "gallery" / "v5"
B5 = PROFILE / "build" / "gallery" / "v51"

FLAGS = {"noaerth-portfolio-os": ("203 tests", "green"),
         "agentos": ("710 tests", "green"),
         "grokinstall": ("486 tests", "failure"),
         "grokmax": ("287 tests", "green"),
         "gh0st": ("27 tests", "failure"),
         "opencode-watchdog": ("70 tests", "green")}


def emit(target: Path, slug: str, content: str, budget=None):
    V.validate(content, slug, budget_kb=budget)
    V.check_motion_is_ambient(content, slug)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_v5(signal):
    for theme in ("dark", "light"):
        emit(A5 / f"hero-{theme}.svg", "v5-hero", V5.hero(theme))
        emit(A5 / f"hero-compact-{theme}.svg", "v5-hero-c", V5.hero(theme, compact=True))
        emit(A5 / f"map-{theme}.svg", "v5-map", V5.system_map(theme))
    for slug in P.FLAGSHIP_ORDER:
        emit(A5 / f"window-{slug}.svg", f"v5-{slug}",
             V5.flagship_hero("dark", slug))
    return sum(p.stat().st_size for p in A5.rglob("*.svg"))


def build_v51(signal):
    for theme in ("dark", "light"):
        emit(B5 / f"hero-{theme}.svg", "v51-hero", D.hero(theme))
        emit(B5 / f"hero-compact-{theme}.svg", "v51-hero-c", D.hero(theme, compact=True))
        emit(B5 / f"signal-{theme}.svg", "v51-signal", D.build_signal(theme, signal))
        emit(B5 / f"map-{theme}.svg", "v51-map", D.system_map(theme))
        emit(B5 / f"map-compact-{theme}.svg", "v51-map-c", D.system_map(theme, compact=True))
        emit(B5 / f"constellation-{theme}.svg", "v51-const", D.constellation(theme), 64)
        emit(B5 / f"terminal-{theme}.svg", "v51-term", D.terminal(theme))
        emit(B5 / f"social-{theme}.svg", "v51-social", D.social_preview(theme), 64)
        emit(B5 / f"divider-{theme}.svg", "v51-div", D.divider(theme))
        for slug in ("noaerth", "repositories", "systems", "why"):
            _slug, t, sub = next(i for i in D.NAV_ITEMS if i[0] == slug)
            emit(B5 / f"nav-{slug}-{theme}.svg", f"v51-nav-{slug}", D.nav_chip(slug, t, sub, theme))
    emit(B5 / "hero-motion.svg", "v51-hero-m", D.hero("dark", motion=True))
    for slug, (m, ci) in FLAGS.items():
        for theme in ("dark", "light"):
            emit(B5 / f"window-{slug}-{theme}.svg", f"v51-{slug}",
                 D.flagship_window(theme, slug, m, ci))
    return sum(p.stat().st_size for p in B5.rglob("*.svg"))


def fig(src, cap, cls=""):
    return (f'<figure class="{cls}"><img src="{src}" alt="{cap}">'
            f'<figcaption>{cap}</figcaption></figure>')


def main() -> int:
    signal = json.loads((PROFILE / "assets" / "profile" / "build-signal.json").read_text())
    a = build_v5(signal)
    b = build_v51(signal)

    def g(base, name):
        return fig(f"build/gallery/{base}/{name}", name.replace("-", " ").replace(".svg", ""))

    sections = []
    sections.append(
        "<h2>Head to head</h2>"
        "<p class='note'>Part 1 selected OPTICAL TOPOLOGY (recursive). V5.1 adds "
        "faceted architecture on the same skeleton. The new direction is lighter "
        f"AND richer: {b / 1024:.0f}KB against {a / 1024:.0f}KB across the same "
        "surface count, because isometric and faceted geometry replace recursive "
        "line work rather than sitting on top of it.</p>"
        + '<div class="pair">'
        + f'<div><h3>Part 1 — OPTICAL TOPOLOGY, RECURSIVE</h3>{g("v5","hero-dark.svg")}'
          f'{g("v5","map-dark.svg")}{g("v5","window-agentos.svg")}</div>'
          + f'<div><h3>V5.1 — OPTICAL TOPOLOGY / FACETED ARCHITECTURE</h3>'
          f'{g("v51","hero-dark.svg")}{g("v51","map-dark.svg")}{g("v51","window-agentos-dark.svg")}</div>'
          + '</div>')
    sections.append("<h2>Profile hero — dark and light, desktop and mobile</h2><div class='grid'>"
                    + g("v51", "hero-dark.svg") + g("v51", "hero-light.svg")
                    + g("v51", "hero-compact-dark.svg") + g("v51", "hero-motion.svg") + "</div>")
    sections.append("<h2>Build signal</h2>"
                    "<p class='note'>V5.1 removed bar length as a proportion of the "
                    "largest metric, which drew a 370x relationship between 2,235 tests "
                    "and 6 green pipelines. Different units cannot share an area scale. "
                    "No side-by-side here: the Part 1 signal generator lived in the V4 "
                    "era module and was superseded, so reconstructing it for comparison "
                    "would show a rebuild rather than the original.</p>"
                    '<div class="grid">'
                    + g("v51", "signal-dark.svg") + g("v51", "signal-light.svg") + '</div>')
    sections.append("<h2>Architecture — two distinct plates</h2>"
                    "<p class='note'>Operating stack shows documented relationships. "
                    "Constellation shows semantic grouping and says in its own caption "
                    "that grouping is not dependency.</p><div class='grid'>"
                    + g("v51", "map-dark.svg") + g("v51", "map-compact-dark.svg")
                    + g("v51", "constellation-dark.svg") + "</div>")
    wins = "".join(
        f'<figure><img src="build/gallery/v51/window-{s}-dark.svg" alt="{P.identity(s)["label"]}">'
        f'<figcaption>{P.identity(s)["label"]} — {P.identity(s)["headline"]} '
        f'<span class="meta">[{P.identity(s)["motif"]}]</span></figcaption></figure>'
        for s in P.FLAGSHIP_ORDER)
    sections.append("<h2>Flagship windows — six distinct motifs</h2>"
                    "<p class='note'>Each carries a different semantic primitive plus "
                    "verified tests and CI as a word, never colour alone.</p>"
                    f"<div class='grid'>{wins}</div>")
    navs = "".join(g("v51", f"nav-{slug}-dark.svg") for slug, _t, _s in D.NAV_ITEMS)
    sections.append(f"<h2>Navigation, terminal, social, divider</h2><div class='grid'>{navs}"
                    + g("v51", "terminal-dark.svg") + g("v51", "social-dark.svg")
                    + g("v51", "divider-dark.svg") + "</div>")

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DUNG30N5 x NOAERTH — V5.1 gallery (local)</title><style>
:root{{color-scheme:dark}}
body{{margin:0;background:#05070a;color:#C9D4E2;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif}}
.wrap{{max-width:1280px;margin:0 auto;padding:34px 24px 100px}}
h1{{font-size:26px;margin:0 0 4px}} .sub{{color:#7C8899;font:12px ui-monospace,Menlo,monospace;margin-bottom:26px}}
h2{{font-size:14px;text-transform:uppercase;letter-spacing:2.4px;color:#5EE7D0;margin:40px 0 6px;padding-bottom:8px;border-bottom:1px solid #1E2836}}
h3{{font-size:12px;letter-spacing:1.6px;color:#93A0B4;margin:14px 0 6px;text-transform:uppercase}}
.note{{color:#7C8899;font:12.5px/1.6 ui-monospace,Menlo,monospace;max-width:78ch;margin:10px 0 16px}}
figure{{margin:0 0 14px}} img{{display:block;width:100%;border:1px solid #1E2836;border-radius:6px;background:#0A0E14}}
figcaption{{color:#8A94A6;font:11.5px ui-monospace,Menlo,monospace;margin-top:5px}} .meta{{color:#5C6779}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}}
@media(max-width:820px){{.pair{{grid-template-columns:1fr}}}}
@media(max-width:560px){{.wrap{{padding:20px 14px 60px}}}}
</style></head><body><div class="wrap">
<h1>DUNG30N5 &times; NOAERTH — V5.1 gallery</h1>
<div class="sub">local review surface &middot; not published &middot; V5.1 supersedes the Part 1 selection</div>
{''.join(sections)}</div></body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.name}: Part 1 {a/1024:.0f}KB vs V5.1 {b/1024:.0f}KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
