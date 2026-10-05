#!/usr/bin/env python3
"""Build GITHUB_V5_ART_GALLERY.html - a local review surface.

Deliberately uncommitted. This exists so coherence can be judged across every
asset before anything is rolled out, and so design rejects never reach a public
repository.

Run:  python3 scripts/github_art/build_gallery.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from github_art import project_identity as P  # noqa: E402
from github_art import tokens as T  # noqa: E402
from github_art import validators as V  # noqa: E402
from github_art.directions import DIRECTIONS, CHOSEN  # noqa: E402

PROFILE = Path(__file__).resolve().parents[2]
OUT = PROFILE / "GITHUB_V5_ART_GALLERY.html"
BUILD = PROFILE / "build" / "v5-chosen"
REJECTS = PROFILE / "build" / "v5-prototypes"


def emit(build_dir: Path, slug: str, theme: str, name: str, generator) -> None:
    art = generator(theme) if name != "hero-compact" else generator(theme, compact=True)
    V.validate(art, f"{slug}/{name}")
    target = build_dir / slug / f"{name}-{theme}.svg"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(art, encoding="utf-8")


def chosen_assets() -> dict:
    """Render the chosen direction to build/v5-chosen."""
    if BUILD.exists():
        for path in BUILD.rglob("*.svg"):
            path.unlink()
    made = []
    for theme in ("dark", "light"):
        for name, fn in (("hero", lambda t: CHOSEN.hero(t)),
                         ("hero-compact", lambda t: CHOSEN.hero(t, compact=True)),
                         ("system-map", lambda t: CHOSEN.system_map(t)),
                         ("system-map-compact",
                          lambda t: CHOSEN.system_map(t, compact=True))):
            art = fn(theme)
            V.validate(art, f"chosen/{name}")
            path = BUILD / f"{name}-{theme}.svg"
            path.write_text(art, encoding="utf-8")
            made.append(path.name)
    for slug in P.IDENTITYS if hasattr(P, "IDENTITYS") else P.IDENTITIES:
        for theme in ("dark", "light"):
            art = CHOSEN.flagship_hero(theme, slug)
            V.validate(art, f"chosen/flagship-{slug}")
            path = BUILD / f"flagship-{slug}-{theme}.svg"
            path.write_text(art, encoding="utf-8")
            made.append(path.name)
    motion = CHOSEN.hero("dark", motion=True)
    V.validate(motion, "chosen/hero-motion")
    V.check_motion_is_ambient(motion, "chosen/hero-motion")
    (BUILD / "hero-motion-dark.svg").write_text(motion, encoding="utf-8")
    made.append("hero-motion-dark.svg")
    return {"count": len(made)}


def figure(src: str, caption: str, width: str = "100%") -> str:
    return (f'<figure><img src="{src}" style="width:{width}" alt="{caption}">'
            f'<figcaption>{caption}</figcaption></figure>')


def main() -> int:
    stats = chosen_assets()

    sections = []
    sections.append(
        "<h2>Chosen direction &mdash; OPTICAL TOPOLOGY, RECURSIVE</h2>"
        "<p class=note>Basis: direction A. Two grafts: the recursive module as the "
        "hero motif (from C, repairing A's empty frame) and strata on the CONTROL "
        "layer only (from B).</p>"
        + figure("build/v5-chosen/hero-dark.svg", "profile hero &mdash; dark")
        + figure("build/v5-chosen/hero-light.svg", "profile hero &mdash; light")
        + figure("build/v5-chosen/hero-compact-dark.svg",
                 "profile hero &mdash; compact dark (320px)")
        + figure("build/v5-chosen/hero-compact-light.svg",
                 "profile hero &mdash; compact light (320px)")
        + figure("build/v5-chosen/hero-motion-dark.svg",
                 "profile hero &mdash; motion (animated SVG, reduced-motion twin "
                 "exists as hero-dark.svg)"))

    sections.append("<h2>Operating stack</h2>"
                    + figure("build/v5-chosen/system-map-dark.svg",
                             "system map &mdash; dark")
                    + figure("build/v5-chosen/system-map-light.svg",
                             "system map &mdash; light")
                    + figure("build/v5-chosen/system-map-compact-dark.svg",
                             "system map &mdash; compact dark"))

    flags = []
    for slug in P.FLAGSHIP_ORDER:
        ident = P.identity(slug)
        flags.append(figure(f"build/v5-chosen/flagship-{slug}-dark.svg",
                            f"{ident['label']} &mdash; {ident['headline']} "
                            f"<span class=meta>[{ident['motif']} / "
                            f"{ident['material']}]</span>"))
    sections.append("<h2>Flagship identities</h2>"
                    "<p class=note>Each mark is a different semantic primitive. "
                    "Nine re-coloured cards would communicate nothing.</p>"
                    + "".join(flags))

    others = []
    for slug in ("grokbot-office", "grokbot-society", "seai-mind"):
        ident = P.identity(slug)
        others.append(figure(f"build/v5-chosen/flagship-{slug}-dark.svg",
                             f"{ident['label']} &mdash; {ident['headline']} "
                             f"<span class=meta>[{ident['motif']}]</span>"))
    sections.append("<h2>Public projects</h2>" + "".join(others))

    rejected = []
    for slug, mod in DIRECTIONS.items():
        for theme in ("dark",):
            for name in ("hero", "flagship-hero", "system-map"):
                path = REJECTS / slug / f"{name}-{theme}.svg"
                if not path.is_file():
                    continue
                rejected.append(figure(
                    str(path.relative_to(PROFILE)),
                    f"{mod.NAME} &mdash; {name} (rejected)"))
    sections.append("<h2>Rejected directions &mdash; local only, never published</h2>"
                    + "".join(rejected))

    payload = {
        "direction": CHOSEN.NAME,
        "slug": CHOSEN.SLUG,
        "basis": CHOSEN.DIRECTION_A,
        "grafted": [CHOSEN.GRAFTED_FROM_C, CHOSEN.GRAFTED_FROM_B],
        "materials": list(T.MATERIALS),
        "intensity": CHOSEN.INTENSITY,
        "budget": T.BUDGET,
    }

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DUNG30N5 &times; NOAERTH &mdash; V5 art gallery (local)</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; background:#05070a; color:#C9D4E2;
    font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:34px 24px 100px; }}
  h1 {{ font-size:26px; margin:0 0 4px; letter-spacing:-.2px; }}
  .sub {{ color:#7C8899; font:12px ui-monospace,Menlo,monospace; margin-bottom:26px; }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:2.4px;
    color:#5EE7D0; margin:38px 0 4px; padding-bottom:8px;
    border-bottom:1px solid #1E2836; }}
  .note {{ color:#7C8899; font:12.5px/1.6 ui-monospace,Menlo,monospace;
    max-width:70ch; margin:10px 0 16px; }}
  figure {{ margin:0 0 18px; }}
  img {{ display:block; border:1px solid #1E2836; border-radius:6px; background:#0A0E14; }}
  figcaption {{ color:#8A94A6; font:11.5px ui-monospace,Menlo,monospace;
    margin-top:6px; }}
  .meta {{ color:#5C6779; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr));
    gap:16px; }}
  .grid figure img {{ width:100%; }}
  @media (max-width:560px) {{ .wrap {{ padding:20px 14px 60px; }} }}
</style></head>
<body><div class="wrap">
<h1>DUNG30N5 &times; NOAERTH &mdash; V5 art gallery</h1>
<div class="sub">local review surface &middot; not published &middot;
{dict(payload).get('direction')} &middot; {stats['count']} chosen assets</div>
{"".join(sections)}
</div></body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.name} ({len(html) / 1024:.1f} KB, {stats['count']} chosen assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
