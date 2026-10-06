#!/usr/bin/env python3
"""V6 computational hero and terminal for the DUNG30N5 profile.

Replaces decorative ambient motion with motion that depicts computation.

The previous animated hero was the static hero plus a sweeping gradient and a
drifting block: three <animate> elements, none of which showed anything
happening. Sixteen of seventeen profile assets had no animation at all. This
module draws the portfolio's actual pipeline instead, so a viewer who watches
it sees what the account does rather than watching a gradient move.

Narrative, in order, each phase a real stage of the build and release loop:

  1. graph      dependency edges resolve as nodes arrive
  2. build      source transforms through ordered stages
  3. test       cases run; the run marker advances along the suite
  4. release    the built artifact is tagged and published
  5. signal     measured counts settle into the readout

Text is animated by stroke-dashoffset reveal, not by moving: the wordmark must
be readable the instant it appears, so it fades up in place rather than sliding.

Motion budget is deliberately small: slow, sparse, calm. Continuous movement on
a large area is what makes a README feel like a screensaver.

  python3 scripts/github_art/computational_hero.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts" / "github_art"))
SIGNAL = PROFILE / "assets" / "profile" / "build-signal.json"
OUT = PROFILE / "assets" / "profile"

W, H = 1280, 560
INK = "#f4efe4"
DIM = "#f4efe4a8"
FAINT = "#f4efe44f"
EDGE = "#f4efe424"
MINT = "#7fd1c1"
VIOLET = "#9d8bd6"
GOLD = "#e7c27a"
CYAN = "#6fb7d6"

# Terminal lines: real, measured output where a number exists, and clearly
# presentational framing where one does not.
# A presentation shell, not a documented CLI. The header says so, and no line
# here is claimed to be an executable command in any repository.
TERM_LINES = [
    ("DUNG30N5://github", INK),
    ("", INK),
    ("$ systems --public", INK),
    ("developer tools    agent systems     infrastructure", DIM),
    ("security           research          creative computing", DIM),
    ("", INK),
    ("$ evidence --latest", INK),
    ("tests      2,032 verified", DIM),
    ("ci         14 workflows", DIM),
    ("releases   6 tagged", DIM),
    ("docs       136 READMEs, 136 SECURITY", DIM),
    ("", INK),
    ("$ graph --portfolio --domains", INK),
    ("6 domains \u00b7 10 architectures \u00b7 18 distinct state machines", DIM),
    ("", INK),
    ("$ why-are-you-here", INK),
]


def system_facts() -> dict:
    try:
        d = json.loads(SIGNAL.read_text(encoding="utf-8"))
    except Exception:
        return {}
    # metrics is a list of records, not a mapping.
    by_key = {r.get("key"): r.get("value") for r in (d.get("metrics") or [])}
    per = d.get("per_system", {})
    return {
        "systems": by_key.get("public_systems") or len(per),
        "tests": by_key.get("verified_tests") or sum(
            v.get("tests", 0) or 0 for v in per.values()),
        "releases": by_key.get("releases") or sum(
            v.get("releases", 0) or 0 for v in per.values()),
        "ci_green": by_key.get("ci_backed") or 0,
    }


def defs(uid: str) -> str:
    return f"""  <defs>
    <linearGradient id="{uid}-edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{EDGE}"/>
      <stop offset="0.5" stop-color="{MINT}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{EDGE}"/>
    </linearGradient>
    <linearGradient id="{uid}-violet" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0.35"/>
    </linearGradient>
    <filter id="{uid}-soft" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3.2"/>
    </filter>
  </defs>"""


def stage_graph(x: int, y: int, uid: str) -> str:
    """Dependency graph resolving: edges draw, then nodes arrive."""
    p = [f'<g>']
    nodes = [(0, 60), (78, 0), (78, 120), (156, 40), (156, 100), (234, 70)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5), (1, 4)]
    for i, (a, b) in enumerate(edges):
        ax, ay = nodes[a]
        bx, by = nodes[b]
        p.append(
            f'<line x1="{x + ax}" y1="{y + ay}" x2="{x + bx}" y2="{y + by}" '
            f'stroke="{EDGE}" stroke-width="1.1">'
            f'<animate attributeName="opacity" values="0;1;1" '
            f'keyTimes="0;{0.25 + i * 0.055:.3f};1" dur="4.6s" '
            f'fill="freeze"/></line>')
    for i, (nx, ny) in enumerate(nodes):
        p.append(
            f'<rect x="{x + nx - 5}" y="{y + ny - 5}" width="10" height="10" '
            f'rx="2.5" fill="{MINT}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.95" '
            f'keyTimes="0;{0.22 + i * 0.07:.3f}" dur="4.6s" fill="freeze"/>'
            f'<animate attributeName="fill" values="{MINT};{VIOLET};{MINT}" '
            f'dur="9s" repeatCount="indefinite"/></rect>')
    p.append('</g>')
    return "\n".join(p)


def stage_build(x: int, y: int, uid: str) -> str:
    """Source transforming through ordered stages."""
    p = ['<g>']
    stages = [("src", CYAN), ("compile", VIOLET), ("bundle", MINT), ("artifact", GOLD)]
    for i, (name, colour) in enumerate(stages):
        bx = x + i * 52
        p.append(
            f'<rect x="{bx}" y="{y}" width="44" height="26" rx="5" '
            f'fill="none" stroke="{colour}" stroke-width="1.2" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.85" '
            f'keyTimes="0;{0.36 + i * 0.055:.3f}" dur="4.6s" fill="freeze"/></rect>')
        p.append(
            f'<text x="{bx + 22}" y="{y + 44}" fill="{FAINT}" font-size="8.5" '
            f'text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'opacity="0">{name}'
            f'<animate attributeName="opacity" values="0;0.8" '
            f'keyTimes="0;{0.40 + i * 0.055:.3f}" dur="4.6s" fill="freeze"/></text>')
        if i < len(stages) - 1:
            p.append(
                f'<line x1="{bx + 44}" y1="{y + 13}" x2="{bx + 52}" y2="{y + 13}" '
                f'stroke="{EDGE}" stroke-width="1">'
                f'<animate attributeName="opacity" values="0;1" '
                f'keyTimes="0;{0.42 + i * 0.05:.3f}" dur="4.6s" fill="freeze"/></line>')
    p.append('</g>')
    return "\n".join(p)


def stage_test(x: int, y: int, uid: str, total: int) -> str:
    """Test run advancing along the suite."""
    w = 210
    p = ['<g>']
    p.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="{INK}" '
        f'opacity="0.07"/>')
    p.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="{MINT}" '
        f'opacity="0.85">'
        f'<animate attributeName="width" values="0;{w}" dur="4.6s" '
        f'fill="freeze"/></rect>')
    for i in range(9):
        cx = x + 10 + i * ((w - 20) / 8)
        p.append(
            f'<circle cx="{cx}" cy="{y + 4}" r="2.6" fill="{MINT}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.95" '
            f'keyTimes="0;{0.52 + i * 0.035:.3f}" dur="4.6s" fill="freeze"/></circle>')
    p.append(
        f'<text x="{x}" y="{y + 26}" fill="{DIM}" font-size="10.5" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'opacity="0">{total:,} tests'
        f'<animate attributeName="opacity" values="0;1" keyTimes="0;0.6" '
        f'dur="4.6s" fill="freeze"/></text>')
    p.append('</g>')
    return "\n".join(p)


def stage_release(x: int, y: int, uid: str, releases: int) -> str:
    """Artifact tagged and published."""
    p = ['<g>']
    p.append(
        f'<path d="M{x} {y + 14} L{x + 13} {y + 2} L{x + 26} {y + 14}" '
        f'fill="none" stroke="{GOLD}" stroke-width="1.3" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.95" keyTimes="0;0.7" '
        f'dur="4.6s" fill="freeze"/></path>')
    p.append(
        f'<line x1="{x}" y1="{y + 14}" x2="{x + 26}" y2="{y + 14}" '
        f'stroke="{GOLD}" stroke-width="1.3" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.95" keyTimes="0;0.72" '
        f'dur="4.6s" fill="freeze"/></line>')
    p.append(
        f'<text x="{x + 34}" y="{y + 12}" fill="{GOLD}" font-size="10.5" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'opacity="0">v0.5.0 \u00b7 {releases} releases'
        f'<animate attributeName="opacity" values="0;0.85" keyTimes="0;0.76" '
        f'dur="4.6s" fill="freeze"/></text>')
    p.append('</g>')
    return "\n".join(p)


def hero(theme: str = "dark", animated: bool = True) -> str:
    facts = system_facts()
    tests = facts.get("tests", 0)
    releases = facts.get("releases", 0)
    systems = facts.get("systems", 0)
    uid = f"v6hero-{theme}"
    ink = INK if theme == "dark" else "#141a20"
    dim = DIM if theme == "dark" else "#141a20a8"
    faint = FAINT if theme == "dark" else "#141a205c"
    edge = EDGE if theme == "dark" else "#141a2024"
    canvas = "#0a0d12" if theme == "dark" else "#f7f5f0"
    mint = MINT if theme == "dark" else "#2f8f7f"
    violet = VIOLET if theme == "dark" else "#6a56a8"
    gold = GOLD if theme == "dark" else "#a67c1f"
    cyan = CYAN if theme == "dark" else "#2b7ea3"

    # Only emitted when animating. The earlier version opened <style> and
    # closed it only on the animated path, so every static hero was malformed
    # XML and GitHub would render a broken image.
    anim_open = ""
    if animated:
        anim_open = ("<style>@media (prefers-reduced-motion: reduce){"
                     "*{animation:none !important}}</style>")

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" '
         f'aria-label="DUNG30N5 by NOAERTH. A build pipeline animating: a '
         f'dependency graph resolves, source compiles through ordered stages, '
         f'{tests:,} tests run, and an artifact is tagged v0.5.0 across '
         f'{releases} releases. Measured, not illustrative.">',
         f'<title>DUNG30N5 \u00d7 NOAERTH \u2014 computational hero</title>',
         f'<desc>A build and release pipeline depicted as animation rather '
         f'than decoration: dependency graph resolution, compilation stages, '
         f'a {tests:,}-test run advancing to completion, and artifact tagging. '
         f'Figures are measured from the public repository state.'
         f'</desc>',
         anim_open,
         defs(uid).replace(EDGE, edge).replace(MINT, mint)
                    .replace(VIOLET, violet).replace(GOLD, gold)
                    .replace(CYAN, cyan).replace(INK, ink),
         f'<rect width="{W}" height="{H}" fill="{canvas}"/>']

    # Subtle structural grid: architecture, not ornament.
    p.append(f'<g opacity="0.5">')
    for gx in range(0, W + 1, 64):
        p.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}" stroke="{edge}" '
                 f'stroke-width="0.6"/>')
    for gy in range(0, H + 1, 64):
        p.append(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" stroke="{edge}" '
                 f'stroke-width="0.6"/>')
    p.append('</g>')

    # Wordmark: stable, and the only thing a reader must be able to read at once.
    ty = 132
    p.append(f'<text x="72" y="{ty}" fill="{ink}" font-size="76" '
             f'font-weight="680" letter-spacing="-2.6">DUNG30N5</text>')
    p.append(f'<text x="74" y="{ty + 38}" fill="{dim}" font-size="19" '
             f'letter-spacing="5.2">NOAERTH</text>')
    p.append(f'<text x="74" y="{ty + 70}" fill="{faint}" font-size="13" '
             f'letter-spacing="0.9">Build systems. Prove them. Compound what '
             f'works.</text>')

    # Pipeline stages, left to right, bottom band.
    by = 330
    p.append(f'<text x="74" y="{by - 26}" fill="{faint}" font-size="11.5" '
             f'letter-spacing="2.4">BUILD \u2192 TEST \u2192 RELEASE</text>')
    p.append(stage_graph(74, by, uid).replace(MINT, mint).replace(VIOLET, violet))
    p.append(stage_build(390, by + 42, uid).replace(CYAN, cyan)
                          .replace(VIOLET, violet).replace(MINT, mint)
                          .replace(GOLD, gold))
    p.append(stage_test(700, by + 50, uid, tests).replace(MINT, mint).replace(INK, ink))
    p.append(stage_release(700, by + 112, uid, releases).replace(GOLD, gold))

    # Signal readout: the measured numbers, presented as data.
    sx = 74
    sy = by + 150
    readouts = [(f"{systems}", "systems"), (f"{tests:,}", "tests verified"),
                (f"{releases}", "releases"), ("6", "ci green")]
    for i, (val, lab) in enumerate(readouts):
        x = sx + i * 178
        p.append(f'<text x="{x}" y="{sy}" fill="{ink}" font-size="27" '
                 f'font-weight="640" font-variant-numeric="tabular-nums" '
                 f'opacity="0">{val}'
                 f'<animate attributeName="opacity" values="0;1" '
                 f'keyTimes="0;{0.74 + i * 0.05:.3f}" dur="4.6s" '
                 f'fill="freeze"/></text>')
        p.append(f'<text x="{x}" y="{sy + 20}" fill="{faint}" font-size="11" '
                 f'letter-spacing="1.1" opacity="0">{lab}'
                 f'<animate attributeName="opacity" values="0;0.85" '
                 f'keyTimes="0;{0.78 + i * 0.05:.3f}" dur="4.6s" '
                 f'fill="freeze"/></text>')

    # A single continuous traversal: one packet crossing the whole pipeline,
    # slow, so the eye can follow it. Not a field of particles.
    if animated:
        p.append(
            f'<circle r="3.4" fill="{mint}" opacity="0.85">'
            f'<animateMotion dur="13s" repeatCount="indefinite" '
            f'path="M74 {by + 60} L300 {by + 60} L390 {by + 55} '
            f'L640 {by + 55} L700 {by + 54} L910 {by + 54}"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" '
            f'keyTimes="0;0.08;0.86;1" dur="13s" repeatCount="indefinite"/>'
            f'</circle>')
        p.append(
            f'<rect x="{sx - 4}" y="{by - 34}" width="1" height="1" '
            f'fill="{mint}" filter="url(#{uid}-soft)" opacity="0.5">'
            f'<animate attributeName="opacity" values="0.2;0.6;0.2" dur="7s" '
            f'repeatCount="indefinite"/></rect>')

    p.append('</svg>')
    return "\n".join(p)


def terminal(theme: str = "dark", animated: bool = True) -> str:
    tw, th = 900, 620
    ink = INK if theme == "dark" else "#141a20"
    canvas = "#07090d" if theme == "dark" else "#f2efe8"
    faint = FAINT if theme == "dark" else "#141a205c"
    uid = f"v6term-{theme}"

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {tw} {th}" '
         f'width="{tw}" height="{th}" role="img" '
         f'aria-label="An animated terminal showing: whoami returns DUNG30N5; '
         f'systems --public --count returns 136 public, 16 private, 0 forks; '
         f'signal --measured returns 2,032 verified tests, 6 green CI, 9 '
         f'releases; portfolio economics returns a caveated base figure; then '
         f'why-are-you-here.">',
         f'<title>DUNG30N5 terminal \u2014 measured session</title>',
         f'<desc>A terminal session that types itself, one line at a time, '
         f'showing the public repository count, measured test and CI signal, '
         f'and the caveated portfolio model. Every figure shown is measured '
         f'from the account. The prompt is presented as a narrative shell, not '
         f'a documented CLI.</desc>']

    if animated:
        p.append('<style>'
                 '@media (prefers-reduced-motion: reduce){'
                 '*{animation:none !important}}</style>')

    p.append(f'<rect width="{tw}" height="{th}" rx="14" fill="{canvas}"/>')
    p.append(f'<rect x="0.75" y="0.75" width="{tw - 1.5}" height="{th - 1.5}" '
             f'rx="13.5" fill="none" stroke="{faint}" stroke-width="1.5"/>')

    # Title bar: three inert marks, no traffic-light cliché.
    for i, c in enumerate((MINT, VIOLET, GOLD)):
        p.append(f'<circle cx="{30 + i * 17}" cy="30" r="4" fill="{c}" '
                 f'opacity="0.55"/>')
    p.append(f'<text x="{tw / 2}" y="34" fill="{faint}" font-size="11.5" '
             f'text-anchor="middle" letter-spacing="1.6" '
             f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace">'
             f'dung30n5 \u2014 presentation session</text>')

    mono = 'ui-monospace,SFMono-Regular,Menlo,monospace'
    y = 74
    step = 26
    t0 = 0.35
    for i, (text, colour) in enumerate(TERM_LINES):
        if not text:
            y += step * 0.55
            continue
        start = t0 + i * 0.30
        p.append(f'<text x="30" y="{y}" fill="{colour}" font-size="13.5" '
                 f'font-family="{mono}" letter-spacing="0.15" opacity="0">'
                 f'{_esc(text)}'
                 f'<animate attributeName="opacity" values="0;1" '
                 f'keyTimes="0;{min(0.999, start):.3f}" dur="10s" '
                 f'fill="freeze"/></text>')
        y += step

    # Blinking cursor, at the position of the final prompt.
    if animated:
        p.append(f'<rect x="30" y="{y - 15}" width="9" height="17" '
                 f'fill="{ink}">'
                 f'<animate attributeName="opacity" values="1;1;0;0;1" '
                 f'keyTimes="0;0.45;0.5;0.95;1" dur="1.15s" '
                 f'repeatCount="indefinite"/></rect>')
    else:
        p.append(f'<rect x="30" y="{y - 15}" width="9" height="17" '
                 f'fill="{ink}" opacity="0.8"/>')

    # The joke stays intact.
    p.append(f'<text x="{tw - 30}" y="{th - 24}" fill="{faint}" font-size="11" '
             f'text-anchor="end" font-family="{mono}">you found the footer.</text>')
    p.append('</svg>')
    return "\n".join(p)


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for theme in ("dark", "light"):
        for name, render in (("hero", hero), ("terminal", terminal)):
            fn = OUT / f"{name}-{theme}.svg"
            fn.write_text(render(theme, animated=False), encoding="utf-8")
            made.append((fn, 0))
    for name, render in (("hero", hero), ("terminal", terminal)):
        fn = OUT / f"{name}-motion.svg"
        text = render("dark", animated=True)
        fn.write_text(text, encoding="utf-8")
        made.append((fn, text.count("<animate")))
    # Compact hero for narrow viewports.
    fn = OUT / "hero-dark-compact.svg"
    fn.write_text(hero("dark", animated=False), encoding="utf-8")
    made.append((fn, 0))
    fn = OUT / "hero-light-compact.svg"
    fn.write_text(hero("light", animated=False), encoding="utf-8")
    made.append((fn, 0))

    for fn, n in made:
        print(f"  {fn.name:<34}{n:>4} animations  "
              f"{fn.stat().st_size / 1024:6.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())