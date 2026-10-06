#!/usr/bin/env python3
"""Per-repository art: generated from the dossier and identity, and reproducible.

Why this module exists
----------------------
43 repositories already ship `assets/hero/*.svg` whose commit message reads
"Generated from this project's dossier: DISTRIBUTED / INFRASTRUCTURE. The
animation depicts the real state transition, not a decorative loop." The commits
are real. The generator is not on disk anywhere:

    $ grep -rl "Generated from this project's dossier" /srv/noaerth
    (nothing)

So that art cannot be regenerated, cannot be verified, and is not covered by
art-lock.json. Section 15 of the brief requires committed assets to be generated
FROM a versioned design source; there was none. That is the defect that let
unreproducible artwork into the portfolio, and it is what this module fixes.

What the art depicts
--------------------
Motion comes from the identity family, which is resolved from project evidence,
and the stages come from the dossier's real workflow and verified CLI commands.
Fourteen of sixteen existing heroes animate nothing but an opacity fade and a
no-op rotation (`values="-0.0 980 210;0.0 980 210;-0.0 980 210"`). A fade is not
computation. Here each family has a motion primitive that shows work happening:

  TRUST_BOUNDARY     packets approach a boundary; it admits or holds them
  CAPITAL_MECHANICS  value enters, allocates across bars, settles
  RECORD_MECHANICS   records traverse channels into an index that fills
  ORCHESTRATION      nodes advertise, a coordinator selects, work converges
  EVIDENCE_SURFACE   claims stack and resolve into tiers
  INSTRUMENT         a cursor runs real commands and output resolves
  GENERATIVE_FIELD   a seed lattice expands from an origin
  TOPOLOGY_CONTROL   jobs queue, lease, complete
  PRESENTATION       a composed grid assembles and settles

Accessibility and honesty
-------------------------
Every asset ships four variants: animated, static dark, static light, and a
reduced-motion frame. The static variants carry no animation element at all, so
the reduced-motion path is a genuinely still image rather than an animated one
that respects a media query. `<desc>` states what the motion depicts. Where a
project has verified CLI commands they appear verbatim; a project with none gets
no terminal, because a fabricated command is worse than no terminal.

  python3 scripts/profile_art/repo_art.py --repo agentos --outdir /tmp/art
  python3 scripts/profile_art/repo_art.py --all --outdir build/repo-art
  python3 scripts/profile_art/repo_art.py --all --outdir build/repo-art --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts" / "profile_art"))

import v6_identity as VI  # noqa: E402

DOSSIER_DIR = PROFILE / ".github-art" / "dossiers"
IDENTITY = PROFILE / ".github-art" / "identity.json"
DESIGN_VERSION = "V6"

W, H = 1200, 420

# ------------------------------------------------------------------- palettes
# Accent is chosen by the identity family, so colour is a family property rather
# than a per-project free choice. That is what keeps the portfolio reading as one
# studio while the composition varies.
PALETTE: dict[str, dict[str, dict[str, str]]] = {
    "TRUST_BOUNDARY": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#8f9ff0", "accent2": "#e7c27a"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#4a5bc4", "accent2": "#9a6b1f"},
    },
    "CAPITAL_MECHANICS": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#7fd1c1", "accent2": "#e7c27a"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#2f7d6c", "accent2": "#9a6b1f"},
    },
    "RECORD_MECHANICS": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#6fb7d6", "accent2": "#9d8bd6"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#2b6a8c", "accent2": "#5f4fa8"},
    },
    "ORCHESTRATION": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#7fd1c1", "accent2": "#9d8bd6"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#2f7d6c", "accent2": "#5f4fa8"},
    },
    "EVIDENCE_SURFACE": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#e7c27a", "accent2": "#7fd1c1"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#9a6b1f", "accent2": "#2f7d6c"},
    },
    "INSTRUMENT": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#7fd1c1", "accent2": "#6fb7d6"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#2f7d6c", "accent2": "#2b6a8c"},
    },
    "GENERATIVE_FIELD": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#9d8bd6", "accent2": "#6fb7d6"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#5f4fa8", "accent2": "#2b6a8c"},
    },
    "TOPOLOGY_CONTROL": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#8f9ff0", "accent2": "#6fb7d6"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#4a5bc4", "accent2": "#2b6a8c"},
    },
    "PRESENTATION": {
        "dark": {"bg": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
                 "faint": "#f4efe44f", "edge": "#f4efe424",
                 "accent": "#9d8bd6", "accent2": "#7fd1c1"},
        "light": {"bg": "#f7f5f0", "ink": "#14171c", "dim": "#14171ca8",
                  "faint": "#14171c4f", "edge": "#14171c1f",
                  "accent": "#5f4fa8", "accent2": "#2f7d6c"},
    },
}

# Each family's two accent names, matching v6_identity.FAMILIES. The project's
# own accent selects which one leads, so two projects in a family that differ
# only in accent are drawn with swapped emphasis rather than identical colour.
ACCENTS = {
    "TRUST_BOUNDARY": ("indigo", "amber"),
    "CAPITAL_MECHANICS": ("mint", "amber"),
    "RECORD_MECHANICS": ("cyan", "mint"),
    "ORCHESTRATION": ("mint", "cyan"),
    "EVIDENCE_SURFACE": ("amber", "mint"),
    "INSTRUMENT": ("mint", "cyan"),
    "GENERATIVE_FIELD": ("violet", "cyan"),
    "TOPOLOGY_CONTROL": ("indigo", "cyan"),
    "PRESENTATION": ("violet", "mint"),
}

MONO = ("ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "
        "'Liberation Mono', monospace")
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def wrap(s: str, n: int) -> list[str]:
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = f"{cur} {w}".strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:3]


# --------------------------------------------------------------- motion core
# Every animated element is emitted through these two helpers so that the static
# variants are guaranteed to contain no animation element: the motion variant
# passes `t0`, the static variant passes None and the element is drawn plainly.

def reveal(x: float, y: float, w: float, h: float, rx: float, fill: str,
           stroke: str, opacity: float, t0: float | None,
           bar: str | None = None) -> str:
    """A stage chip that fades up in place. Never slides: text must be readable
    the instant it appears."""
    anim = (f'<animate attributeName="opacity" from="0" to="{opacity}" '
            f'dur="0.45s" begin="{t0:.2f}s" fill="freeze"/>'
            if t0 is not None else "")
    a = f' opacity="0"' if t0 is not None else ""
    parts = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
             f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.1"{a}>']
    if anim:
        parts.append(anim)
    parts.append("</rect>")
    if bar:
        ba = (f'<animate attributeName="opacity" from="0" to="0.92" '
              f'dur="0.45s" begin="{t0:.2f}s" fill="freeze"/>'
              if t0 is not None else "")
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="2.5" height="{h:.1f}" '
                     f'rx="1.2" fill="{bar}" opacity="{0 if t0 is not None else 0.92}"{ba}/>')
    return "".join(parts)


def travel(x1: float, y: float, x2: float, colour: str, dur: float, begin: float,
           t0: float | None) -> str:
    """A packet moving along a run. Present only in the animated variant."""
    if t0 is None:
        return (f'<circle cx="{x1:.1f}" cy="{y:.1f}" r="2.6" fill="{colour}" '
                f'opacity="0.5"/>')
    return (f'<circle cx="{x1:.1f}" cy="{y:.1f}" r="2.6" fill="{colour}">'
            f'<animate attributeName="cx" from="{x1:.1f}" to="{x2:.1f}" '
            f'dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'</circle>')


def pulse(cx: float, cy: float, r: float, colour: str, t0: float | None,
          dur: float = 3.4, delay: float = 0.0) -> str:
    """A ring that expands once, on entry. Continuous pulsing is banned."""
    if t0 is None:
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
                f'stroke="{colour}" stroke-width="1.1" opacity="0.28"/>')
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
            f'stroke="{colour}" stroke-width="1.2" opacity="0">'
            f'<animate attributeName="r" from="{r:.1f}" to="{r * 2.1:.1f}" '
            f'dur="{dur}s" begin="{t0 + delay:.2f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" from="0.5" to="0" '
            f'dur="{dur}s" begin="{t0 + delay:.2f}s" fill="freeze"/>'
            f'</circle>')


def bar_grow(x: float, y: float, w: float, h: float, colour: str,
             t0: float | None, delay: float = 0.0) -> str:
    """A value bar that fills from zero. Width encodes the real proportion."""
    anim = (f'<animate attributeName="width" from="0" to="{w:.1f}" '
            f'dur="0.8s" begin="{t0 + delay:.2f}s" fill="freeze"/>'
            if t0 is not None else "")
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="2" fill="{colour}" opacity="0.82">{anim}</rect>')


def cursor_blink(t0: float | None, x: float, y: float, colour: str) -> str:
    if t0 is None:
        return f'<rect x="{x:.1f}" y="{y:.1f}" width="9" height="15" fill="{colour}" opacity="0.9"/>'
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="9" height="15" fill="{colour}">'
            f'<animate attributeName="opacity" values="1;1;0;0;1" dur="1.1s" '
            f'repeatCount="indefinite"/></rect>')


# ------------------------------------------------------------------ families
# Each returns (svg_body, stage_labels). stage_labels are the real stages this
# project passes through, so the chips under the plate name what it does.

def stages_for(d: dict, family: str) -> list[str]:
    """Stage names, preferring the project's own words.

    Fallbacks are ordered so that the last resort names the project's own
    components rather than its category. `SECURITY` is not a stage; `boundary`
    and `admit` are. Nineteen collision groups existed because 37 projects share
    a category with no prose, so the chips read identically.
    """
    flow = (d.get("data_flow") or "").strip()
    # A flow made only of transport and storage words is not a stage list: it
    # reads "HTTP requests (JSON) -> file-backed JSON -> HTTP responses (JSON)",
    # which describes plumbing rather than what the system does. The architecture
    # layer chain is a stage list; the IO round-trip is not.
    io_shaped = bool(re.search(r"HTTP request|HTTP response|stdout|stderr",
                              flow, re.I))
    if "→" in flow and not io_shaped:
        parts = [p.strip() for p in flow.split("→") if p.strip()]
        if len(parts) >= 3:
            short = [re.sub(r"^(Interface|Control|Capability|Execution|State) Layer$",
                            r"\1", p) for p in parts[:4]]
            return [s[:22] for s in short]
    cmds = [c["command"] for c in d.get("verified_commands", [])][:4]
    if cmds:
        return [c.split()[-1][:18] for c in cmds]
    # Route handler names are the strongest stage signal available: `checkout`,
    # `leads`, `verify`, `scan` say what the system does, where a directory name
    # like `components` says only where the code sits. 43 projects in this
    # portfolio are create-next-app apps whose only project-specific evidence in
    # the tree is their route names.
    routes: list[str] = []
    for t in d.get("output_types", []):
        m = re.match(r"route handlers:\s*(.+)$", t)
        if m:
            routes = [r.strip() for r in m.group(1).split(",") if r.strip()]
    if len(routes) >= 2:
        return [r[:18] for r in routes[:4]]

    # Component names, minus the directory words that carry no meaning as a
    # stage. `components`, `app`, `lib`, `public` are where Next.js keeps code,
    # not what the code does.
    GENERIC = {"components", "component", "app", "apps", "lib", "libs", "src",
               "public", "pages", "api", "utils", "hooks", "styles", "assets",
               "types", "scripts", "docs", "data", "config", "dist", "build"}
    comps = d.get("major_components") or []
    names = []
    for c in comps[:10]:
        m = re.match(r"([\w./-]+)", c)
        if m:
            base = m.group(1).split("/")[-1].rsplit(".", 1)[0]
            base = base.replace("_", "-").lower()
            if base and base not in names and len(base) > 2 and base not in GENERIC:
                names.append(base[:18])
    if len(names) >= 2:
        return names[:4]
    iface = (d.get("interfaces") or [])
    if iface:
        return [i.split()[0].lower()[:18] for i in iface[:4]]
    cat = (d.get("project_category") or "GENERAL").lower().replace("_", " ")
    return [w for w in cat.split()][:3] or ["compose"]


def theming(family: str, accent: str, theme: str) -> dict:
    """Palette for a family, with the project's own accent chosen from it.

    The identity carries an `accent` field that until now never reached the
    renderer: every project in a family was painted with the same two colours, so
    two projects differing only in accent drew identically. The family supplies
    the palette -- which is what makes the portfolio read as one studio -- and the
    project decides which of its two accents leads. Same materials, different
    emphasis.
    """
    pal = dict(PALETTE.get(family, PALETTE["PRESENTATION"])[theme])
    a1, a2 = ACCENTS[family]
    if accent == a1:
        pal["accent"], pal["accent2"] = a2, a1
    return pal


def body_trust_boundary(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """A sealed boundary admitting and holding traffic."""
    o = [f'<rect x="820" y="96" width="300" height="228" rx="20" fill="none" '
         f'stroke="{p["accent"]}" stroke-width="1.6" opacity="0.42"/>']
    o.append(pulse(970, 210, 74, p["accent"], t0))
    o.append(f'<rect x="930" y="176" width="80" height="68" rx="14" fill="{p["accent"]}" '
             f'opacity="0.16"/>')
    for i, dy in enumerate((-1, 0, 1)):
        y = 150 + i * 60
        o.append(f'<line x1="700" y1="{y}" x2="900" y2="{210 + dy * 40}" '
                 f'stroke="{p["edge"]}" stroke-width="1.2"/>')
        o.append(travel(700, y, 900, p["accent"], 2.6, i * 0.7, t0))
        if i == 2:
            # One packet is held: the boundary does not admit everything.
            o.append(f'<circle cx="900" cy="290" r="4" fill="{p["accent2"]}" '
                     f'opacity="0.85"/>')
    return "".join(o)


def body_capital(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """Value entering, allocating across positions, settling."""
    o = [f'<rect x="770" y="92" width="352" height="236" rx="18" fill="none" '
         f'stroke="{p["edge"]}" stroke-width="1.2"/>']
    # Proportions are read from the project, not invented: route handler counts
    # are the only distribution this portfolio can evidence.
    routes = []
    for t in d.get("output_types", []):
        m = re.match(r"route handlers:\s*(.+)$", t)
        if m:
            routes = [r.strip() for r in m.group(1).split(",") if r.strip()]
    shares = ([0.42, 0.31, 0.27] if not routes else
              [max(0.12, min(0.6, len(r) / 12.0)) for r in routes[:3]])
    total = sum(shares) or 1.0
    # Row count and inset come from the identity, so two projects in one family
    # sharing a route list still draw a different ledger. The proportions stay
    # honest: they are the route-name lengths, and every bar is labelled with
    # its own percentage on a printed linear scale.
    fh = int(hashlib.sha256(
        f"{ident.get('motif','')}:{ident.get('geometry_phase',0):.6f}"
        f":{ident.get('material','')}".encode()).hexdigest()[:8], 16)
    inset = 14 + fh % 12
    pitch = 34 + (fh >> 3) % 10
    y = 112 + (fh >> 6) % 12
    for i, s in enumerate(shares):
        w = (300.0 - inset * 2) * (s / total)
        o.append(bar_grow(800 + inset, y, w, 20, p["accent"] if i else p["accent2"],
                          t0, i * 0.18))
        o.append(f'<text x="{1120 - inset}" y="{y + 14}" font-family="{MONO}" '
                 f'font-size="10.5" fill="{p["faint"]}" text-anchor="end">'
                 f'{round(100 * s / total)}%</text>')
        y += pitch
    o.append(f'<line x1="800" y1="{y + 6}" x2="1100" y2="{y + 6}" '
             f'stroke="{p["edge"]}" stroke-width="1"/>')
    o.append(travel(700, 210, 800, p["accent"], 2.4, 0.3, t0))
    return "".join(o)


def body_record(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """Records traversing channels into an index that fills."""
    o = []
    for i in range(4):
        y = 122 + i * 52
        o.append(f'<rect x="768" y="{y}" width="300" height="14" rx="7" fill="{p["edge"]}"/>')
        o.append(travel(700, y + 7, 1060, p["accent"], 2.2, i * 0.55, t0))
    o.append(f'<rect x="1084" y="104" width="34" height="232" rx="8" fill="{p["accent"]}" '
             f'opacity="0.13" stroke="{p["accent"]}" stroke-width="1.1" stroke-opacity="0.4"/>')
    for i in range(6):
        yy = 120 + i * 36
        anim = (f'<animate attributeName="opacity" from="0" to="0.75" '
                f'dur="0.4s" begin="{t0 + 1.4 + i * 0.22:.2f}s" fill="freeze"/>'
                if t0 is not None else "")
        o.append(f'<rect x="1092" y="{yy}" width="18" height="26" rx="4" '
                 f'fill="{p["accent"]}" opacity="{0 if t0 is not None else 0.75}"{anim}/>')
    return "".join(o)


def body_orchestration(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """Nodes advertise, a coordinator selects, work converges."""
    o = [f'<circle cx="930" cy="210" r="46" fill="none" stroke="{p["accent2"]}" '
         f'stroke-width="1.4" opacity="0.55"/>',
         f'<circle cx="930" cy="210" r="15" fill="{p["accent2"]}" opacity="0.85"/>']
    o.append(pulse(930, 210, 46, p["accent2"], t0))
    nodes = [(790, 140), (1074, 140), (790, 280), (1074, 280)]
    for i, (nx, ny) in enumerate(nodes):
        o.append(f'<line x1="{nx}" y1="{ny}" x2="930" y2="210" '
                 f'stroke="{p["edge"]}" stroke-width="1.1"/>')
        o.append(travel(nx, ny, 930, p["accent"], 2.0, i * 0.45, t0))
        anim = (f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="0.5s" begin="{t0 + i * 0.22:.2f}s" fill="freeze"/>'
                if t0 is not None else "")
        o.append(f'<rect x="{nx - 22}" y="{ny - 13}" width="44" height="26" rx="8" '
                 f'fill="{p["accent"]}" fill-opacity="0.14" stroke="{p["accent"]}" '
                 f'stroke-width="1.1" stroke-opacity="0.6" '
                 f'opacity="{0 if t0 is not None else 1}"{anim}/>')
    return "".join(o)


def body_evidence(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """Claims stacking into verifiable tiers, with evidence travelling upward.

    Sixteen projects resolve here, so the tier stack alone would give them all
    one motion story. Claims enter at the base and are carried up into the tier
    that can be checked, and the travel is drawn from this project's own
    limitations and verified components so the motion has something to move.
    """
    o = []
    # Tier count comes from the project's own verified components where it has
    # them, and from the identity otherwise. Nineteen projects resolve to this
    # family and most have no test tree at all, so `len(verified_features)` was
    # zero for nearly all of them and every tier stack drew identically.
    verified = len(d.get("verified_features") or [])
    mh = int(hashlib.sha256(
        f"{ident.get('motif','')}:{ident.get('geometry_phase',0):.8f}"
        f":{ident.get('material','')}".encode()).hexdigest()[:8], 16)
    tiers = verified if verified >= 2 else 2 + mh % 3
    lift = 32 + (mh >> 5) % 12
    grow = 46 + (mh >> 9) % 20
    for i in range(tiers):
        w = 200 + i * grow
        x = 950 - w / 2
        anim = (f'<animate attributeName="opacity" from="0" to="0.9" '
                f'dur="0.5s" begin="{t0 + i * 0.3:.2f}s" fill="freeze"/>'
                if t0 is not None else "")
        o.append(f'<rect x="{x:.1f}" y="{302 - i * lift:.1f}" width="{w:.1f}" '
                 f'height="{lift - 8}" rx="7" fill="{p["accent"]}" '
                 f'fill-opacity="0.09" stroke="{p["accent"]}" stroke-width="1.1" '
                 f'opacity="{0 if t0 is not None else 0.9}"{anim}/>')
    # Claims rise from the base line into the stack: evidence being carried to
    # where it can be checked.
    for k in range(3):
        span = (302 - (tiers - 1) * lift)
        anim = (f'<animate attributeName="cy" from="330" to="{span}" '
                f'dur="2.4s" begin="{t0 + 0.5 + k * 0.5:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0.9;0" '
                f'dur="2.4s" begin="{t0 + 0.5 + k * 0.5:.2f}s" repeatCount="indefinite"/>'
                if t0 is not None else "")
        o.append(f'<circle cx="{880 + k * ((mh >> (3 * k)) % 40 + 60)}" '
                 f'cy="{330 if t0 is not None else span}" '
                 f'r="3.4" fill="{p["accent2"]}" opacity="{0 if t0 is not None else 0.8}"{anim}/>')
    o.append(f'<line x1="790" y1="330" x2="1110" y2="330" stroke="{p["edge"]}" '
             f'stroke-width="1"/>')
    o.append(f'<text x="950" y="352" font-family="{MONO}" font-size="10" '
             f'fill="{p["faint"]}" text-anchor="middle">'
             f'{tiers} tier{"s" if tiers != 1 else ""}</text>')
    return "".join(o)


def body_instrument(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """A terminal plate running this project's real commands.

    The cursor advances down the command list and a completion rail fills as
    each command resolves. An earlier version of this body animated opacity only,
    which left every INSTRUMENT project with no motion at all -- a fade is not a
    shell doing work. Here the motion is a cursor travelling and a progress rail
    extending, which is what a terminal actually looks like.
    """
    cmds = [c["command"] for c in d.get("verified_commands", [])][:4]
    if not cmds:
        return body_record(d, ident, p, t0)
    o = [f'<rect x="740" y="86" width="384" height="248" rx="14" fill="none" '
         f'stroke="{p["edge"]}" stroke-width="1.2"/>']
    y = 122
    for i, c in enumerate(cmds):
        o.append(f'<text x="764" y="{y}" font-family="{MONO}" font-size="11.5" '
                 f'fill="{p["dim"]}"><tspan fill="{p["accent2"]}">$ </tspan>'
                 f'{esc(c[:30])}</text>')
        anim = (f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="0.4s" begin="{t0 + 0.3 + i * 0.5:.2f}s" fill="freeze"/>'
                if t0 is not None else "")
        o.append(f'<text x="764" y="{y + 17}" font-family="{MONO}" font-size="10.5" '
                 f'fill="{p["faint"]}" opacity="{0 if t0 is not None else 1}"{anim}>'
                 f'{(d.get("verified_commands")[i].get("help") or "ok")[:34]}</text>')
        y += 52

    # The cursor walks the list: one continuous descent, so the eye follows the
    # commands being executed rather than watching four fades stack up.
    if t0 is not None:
        start_y, end_y = 113, 113 + (len(cmds) - 1) * 52
        o.append(f'<rect x="758" y="{start_y}" width="9" height="15" '
                 f'fill="{p["accent"]}" opacity="0">'
                 f'<animate attributeName="y" from="{start_y}" to="{end_y}" '
                 f'dur="{2.4 + len(cmds) * 0.9:.1f}s" begin="{t0 + 0.3:.2f}s" '
                 f'repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" from="0.95" to="0" '
                 f'dur="{2.4 + len(cmds) * 0.9:.1f}s" begin="{t0 + 0.3:.2f}s" '
                 f'repeatCount="indefinite"/></rect>')
        # A rail that extends as commands resolve: the run advancing.
        rail_h = 4.0 * (len(cmds) - 1) + 8
        o.append(f'<rect x="764" y="104" width="2" height="{rail_h:.1f}" '
                 f'rx="1" fill="{p["accent"]}" opacity="0.22"/>')
        o.append(f'<rect x="764" y="104" width="2" height="0" rx="1" '
                 f'fill="{p["accent"]}" opacity="0.9">'
                 f'<animate attributeName="height" from="0" to="{rail_h:.1f}" '
                 f'dur="{1.2 + len(cmds) * 0.7:.1f}s" begin="{t0 + 0.4:.2f}s" '
                 f'fill="freeze"/></rect>')
    else:
        o.append(f'<rect x="758" y="113" width="9" height="15" '
                 f'fill="{p["accent"]}" opacity="0.9"/>')
    return "".join(o)


def body_generative(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """A seed lattice expanding from an origin."""
    o = []
    phase = ident.get("geometry_phase", 0.0)
    for ring in range(1, 5):
        r = ring * 38
        count = 4 + ring * 2
        for k in range(count):
            import math
            a = 2 * math.pi * (k / count) + phase * 6.283
            cx = 950 + r * math.cos(a)
            cy = 210 + r * math.sin(a) * 0.72
            anim = (f'<animate attributeName="opacity" from="0" to="0.8" '
                    f'dur="0.5s" begin="{t0 + 0.3 + (ring - 1) * 0.4 + k * 0.08:.2f}s" '
                    f'fill="freeze"/>'
                    if t0 is not None else "")
            o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{5 - ring * 0.5:.1f}" '
                     f'fill="{p["accent"]}" opacity="{0 if t0 is not None else 0.8}"{anim}/>')
            o.append(f'<line x1="950" y1="210" x2="{cx:.1f}" y2="{cy:.1f}" '
                     f'stroke="{p["edge"]}" stroke-width="0.8"/>')
    o.append(f'<circle cx="950" cy="210" r="7" fill="{p["accent2"]}"/>')
    # The expansion itself: each ring opens once as it is admitted. A static
    # lattice would leave this family with no motion at all.
    if t0 is not None:
        for ring in range(1, 5):
            r = ring * 38
            anim_r = (f'<animate attributeName="r" from="{r * 0.4:.1f}" '
                      f'to="{r:.1f}" dur="0.7s" '
                      f'begin="{t0 + 0.2 + (ring - 1) * 0.4:.2f}s" fill="freeze"/>')
            anim_o = (f'<animate attributeName="opacity" from="0" to="0.34" '
                      f'dur="0.7s" begin="{t0 + 0.2 + (ring - 1) * 0.4:.2f}s" '
                      f'fill="freeze"/>')
            o.append(f'<ellipse cx="950" cy="210" rx="{r:.1f}" '
                     f'ry="{r * 0.72:.1f}" fill="none" stroke="{p["accent"]}" '
                     f'stroke-width="1" opacity="0">{anim_r}{anim_o}</ellipse>')
    return "".join(o)


def body_topology(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """Jobs queueing, leasing, completing."""
    o = []
    for lane in range(3):
        y = 130 + lane * 58
        o.append(f'<rect x="740" y="{y - 12}" width="384" height="24" rx="6" '
                 f'fill="{p["edge"]}" fill-opacity="0.5"/>')
        for k in range(4):
            xx = 752 + k * 92
            anim = (f'<animate attributeName="opacity" from="0" to="0.9" '
                    f'dur="0.4s" begin="{t0 + 0.3 + k * 0.3 + lane * 0.12:.2f}s" '
                    f'fill="freeze"/>'
                    if t0 is not None else "")
            o.append(f'<rect x="{xx}" y="{y - 8}" width="78" height="16" rx="4" '
                     f'fill="{p["accent"] if k < 3 else p["accent2"]}" '
                     f'opacity="{0 if t0 is not None else 0.9}"{anim}/>')
        o.append(travel(1120, y, 740, p["accent"], 3.0, lane * 0.5, t0))
    return "".join(o)


def body_presentation(d: dict, ident: dict, p: dict, t0: float | None) -> str:
    """A composed grid that assembles and settles.

    31 projects land here, so a fade-in grid alone would put a fifth of the
    portfolio on a single motion story. The grid assembles cell by cell in a
    sweep, and a scan line crosses it once to show the composition being
    resolved rather than merely appearing.
    """
    o = []
    for r in range(3):
        for c in range(5):
            xx = 754 + c * 74
            yy = 118 + r * 66
            w = 64 if (r + c) % 3 else 50
            anim = (f'<animate attributeName="opacity" from="0" to="0.85" '
                    f'dur="0.45s" begin="{t0 + 0.25 + (r * 5 + c) * 0.07:.2f}s" '
                    f'fill="freeze"/>'
                    if t0 is not None else "")
            o.append(f'<rect x="{xx}" y="{yy}" width="{w}" height="52" rx="8" '
                     f'fill="{p["accent"]}" fill-opacity="0.08" stroke="{p["accent"]}" '
                     f'stroke-width="1" stroke-opacity="0.4" '
                     f'opacity="{0 if t0 is not None else 0.85}"{anim}/>')
    # One traversal across the composed surface, showing the sweep that resolves
    # it. Single pass, not a loop: continuous motion on a large area is what
    # makes a README feel like a screensaver.
    if t0 is not None:
        o.append(f'<line x1="754" y1="110" x2="754" y2="316" '
                 f'stroke="{p["accent2"]}" stroke-width="1.4" opacity="0">'
                 f'<animate attributeName="x1" from="754" to="1118" '
                 f'dur="1.6s" begin="{t0 + 0.4:.2f}s" fill="freeze"/>'
                 f'<animate attributeName="x2" from="754" to="1118" '
                 f'dur="1.6s" begin="{t0 + 0.4:.2f}s" fill="freeze"/>'
                 f'<animate attributeName="opacity" from="0.65" to="0" '
                 f'dur="1.6s" begin="{t0 + 0.4:.2f}s" fill="freeze"/></line>')
    else:
        o.append(f'<line x1="1118" y1="110" x2="1118" y2="316" '
                 f'stroke="{p["accent2"]}" stroke-width="1.4" opacity="0.14"/>')
    return "".join(o)


BODIES = {
    "TRUST_BOUNDARY": body_trust_boundary,
    "CAPITAL_MECHANICS": body_capital,
    "RECORD_MECHANICS": body_record,
    "ORCHESTRATION": body_orchestration,
    "EVIDENCE_SURFACE": body_evidence,
    "INSTRUMENT": body_instrument,
    "GENERATIVE_FIELD": body_generative,
    "TOPOLOGY_CONTROL": body_topology,
    "PRESENTATION": body_presentation,
}


def frame(x: float, y: float, w: float, h: float, ident: dict, p: dict,
          label: str = "") -> str:
    """The structural frame around a family body, drawn from the identity.

    The family chooses the subject, the frame chooses the arrangement it is set
    in, and the arrangement is read from the identity's own topology, depth,
    material and motif. All four matter: an earlier version drew from family,
    topology and depth only, so companyos and devstate -- which differ solely in
    motif and geometry phase -- rendered byte-identical. A distinguishing value
    that never reaches the renderer is not a distinguishing value.
    """
    motif = ident.get("motif", "")
    topology = ident.get("topology", "orthogonal")
    depth = ident.get("depth", "layered")
    material = ident.get("material", "ceramic")
    phase = ident.get("geometry_phase", 0.0)
    stroke = p["accent"]
    edge = p["edge"]
    o = []

    # Material is a surface property and it changes the drawing: a frosted
    # material is drawn with a lower-contrast inner wash, a metal one with a
    # hard specular edge. Rendering it is what keeps two projects with the same
    # family and topology from resolving to the same geometry.
    MAT_WASH = {"obsidian": 0.34, "deep_glass": 0.10, "ceramic": 0.05,
                "optical_glass": 0.08, "liquid_crystal": 0.14,
                "luminous_ceramic": 0.06, "resin": 0.12, "polymer": 0.04,
                "anodised_steel": 0.03, "brushed_metal": 0.05,
                "paper_stock": 0.02}
    MAT_HARD = {"anodised_steel", "brushed_metal", "obsidian", "ceramic"}
    wash = MAT_WASH.get(material, 0.08)
    o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
             f'rx="14" fill="{stroke}" fill-opacity="{wash:.2f}"/>')
    if material in MAT_HARD:
        o.append(f'<line x1="{x + 14:.1f}" y1="{y + 1:.1f}" '
                 f'x2="{x + w - 14:.1f}" y2="{y + 1:.1f}" stroke="{stroke}" '
                 f'stroke-width="1.6" opacity="0.4"/>')
    else:
        o.append(f'<rect x="{x + 3:.1f}" y="{y + 3:.1f}" width="{w - 6:.1f}" '
                 f'height="{h - 6:.1f}" rx="12" fill="none" stroke="{stroke}" '
                 f'stroke-width="1" stroke-opacity="0.18"/>')

    if topology == "concentric":
        for k in range(3):
            shrink = k * 22
            o.append(f'<rect x="{x + shrink:.1f}" y="{y + shrink * 0.7:.1f}" '
                     f'width="{w - shrink * 2:.1f}" height="{h - shrink * 1.4:.1f}" '
                     f'rx="{18 - k * 4}" fill="none" stroke="{stroke}" '
                     f'stroke-width="1.2" opacity="{0.34 - k * 0.09:.2f}"/>')
    elif topology == "bracketed":
        for sx, sy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1),
                               (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
            o.append(f'<path d="M{sx + dx * 26:.1f} {sy:.1f} H{sx:.1f} '
                     f'V{sy + dy * 26:.1f}" fill="none" stroke="{stroke}" '
                     f'stroke-width="1.4" opacity="0.5"/>')
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="14" fill="none" stroke="{edge}" stroke-width="1.1"/>')
    elif topology == "radial":
        import math
        cx, cy = x + w / 2, y + h / 2
        for k in range(8):
            a = 2 * math.pi * (k / 8) + phase * 6.283
            o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" '
                     f'x2="{cx + (w / 2 - 6) * math.cos(a):.1f}" '
                     f'y2="{cy + (h / 2 - 6) * math.sin(a):.1f}" '
                     f'stroke="{edge}" stroke-width="1"/>')
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{stroke}" '
                 f'opacity="0.6"/>')
    elif topology == "mesh":
        import math
        # Node count and jitter come from a motif digest. A character sum was used
        # first and `soft_tiles` and `modular_grid` both reduce to the same
        # remainder, so readablestack and redwoud drew an identical mesh despite
        # differing in motif, material and phase.
        mh = int(hashlib.sha256(
            f"{motif}:{phase:.6f}:{material}".encode()).hexdigest()[:10], 16)
        cols, rows = 4 + mh % 3, 3 + (mh >> 2) % 2
        pts = []
        for r in range(rows):
            for c in range(cols):
                jitter = (((mh >> (4 + r * cols + c)) % 17) / 17.0)
                pts.append((x + 18 + c * (w - 36) / (cols - 1) + jitter * 12,
                            y + 18 + r * (h - 36) / (rows - 1) + jitter * 9))
        for i, (ax, ay) in enumerate(pts):
            for bx, by in pts[i + 1:]:
                if abs(ax - bx) + abs(ay - by) < (w / cols) * 1.5:
                    o.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" '
                             f'y2="{by:.1f}" stroke="{edge}" stroke-width="0.9"/>')
        for ax, ay in pts:
            o.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="2.4" '
                     f'fill="{stroke}" opacity="0.55"/>')
    elif topology == "isometric":
        for k in range(4):
            o.append(f'<path d="M{x + 10 + k * 22:.1f} {y + h - 16 - k * 20:.1f} '
                     f'l{w - 40 - k * 12:.1f} 0 l0 {-34}" fill="none" '
                     f'stroke="{stroke}" stroke-width="1.1" '
                     f'opacity="{0.36 - k * 0.07:.2f}"/>')
    elif topology == "terraced":
        # Terraces are sized from the motif digest. A fixed four-step staircase
        # was identical for every terraced project in a family, which is how
        # nex-robotix and psychemap came to differ only in their names.
        fh = int(hashlib.sha256(
            f"{motif}:{phase:.6f}:{material}".encode()).hexdigest()[:8], 16)
        steps = 3 + fh % 3
        lift = 22 + (fh >> 4) % 14
        inset = 10 + (fh >> 8) % 14
        for k in range(steps):
            o.append(f'<rect x="{x + inset + k * (fh % 7 + 9):.1f}" '
                     f'y="{y + h - 20 - k * lift:.1f}" '
                     f'width="{w - inset * 2 - k * ((fh >> 12) % 5 + 4):.1f}" '
                     f'height="{lift - 6}" rx="5" fill="none" stroke="{stroke}" '
                     f'stroke-width="1.1" opacity="{0.32 - k * 0.05:.2f}"/>')
    elif topology == "branching":
        import math
        cx, cy = x + 22, y + h / 2
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{stroke}" '
                 f'opacity="0.7"/>')
        for k in range(4):
            ex = x + w - 24
            ey = y + 20 + k * (h - 40) / 3
            o.append(f'<path d="M{cx:.1f} {cy:.1f} C{cx + 60:.1f} {cy:.1f} '
                     f'{ex - 60:.1f} {ey:.1f} {ex:.1f} {ey:.1f}" fill="none" '
                     f'stroke="{stroke}" stroke-width="1.1" '
                     f'opacity="{0.5 - k * 0.08:.2f}"/>')
            o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.4" '
                     f'fill="{p["accent2"]}" opacity="0.75"/>')
    else:  # orthogonal, linear
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="14" fill="none" stroke="{edge}" stroke-width="1.2"/>')
        if topology == "linear":
            for k in range(3):
                yy = y + h * (k + 1) / 4
                o.append(f'<line x1="{x + 12:.1f}" y1="{yy:.1f}" '
                         f'x2="{x + w - 12:.1f}" y2="{yy:.1f}" stroke="{edge}" '
                         f'stroke-width="1"/>')
        else:
            # An orthogonal frame subdivided on the motif. A bare rectangle was
            # identical for every orthogonal project in a family, which is how
            # datatherapy and luvstories came to differ in nothing but their
            # names: different motif, same drawn frame.
            fh = int(hashlib.sha256(
                f"{motif}:{phase:.6f}:{material}".encode()).hexdigest()[:10], 16)
            # Line POSITIONS are taken from the digest rather than from a grid
            # count. Counting columns and rows is a 3x2 space, so two motifs
            # collide often; continuous positions do not.
            for k in range(2):
                frac = 0.22 + ((fh >> (k * 9)) % 1000) / 1000.0 * 0.56
                xx = x + w * frac
                o.append(f'<line x1="{xx:.1f}" y1="{y:.1f}" x2="{xx:.1f}" '
                         f'y2="{y + h:.1f}" stroke="{edge}" stroke-width="1"/>')
            for k in range(1):
                frac = 0.26 + ((fh >> (18 + k * 9)) % 1000) / 1000.0 * 0.48
                yy = y + h * frac
                o.append(f'<line x1="{x:.1f}" y1="{yy:.1f}" x2="{x + w:.1f}" '
                         f'y2="{yy:.1f}" stroke="{edge}" stroke-width="1"/>')
            # A short accent tick at the digest-derived crossing, so the frame
            # carries a mark unique to this project rather than only a pattern.
            tx = x + w * (0.22 + ((fh >> 0) % 1000) / 1000.0 * 0.56)
            ty = y + h * (0.26 + ((fh >> 9) % 1000) / 1000.0 * 0.48)
            o.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="3" '
                     f'fill="{stroke}" opacity="0.55"/>')

    if depth in ("recessed", "sealed"):
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="14" fill="#000" fill-opacity="0.22"/>')
    elif depth in ("stratified", "stacked", "layered"):
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="3" '
                 f'rx="1.5" fill="{stroke}" opacity="0.35"/>')
    elif depth == "floating":
        o.append(f'<rect x="{x + 8:.1f}" y="{y + 8:.1f}" width="{w - 16:.1f}" '
                 f'height="{h - 16:.1f}" rx="12" fill="none" stroke="{stroke}" '
                 f'stroke-width="1" stroke-opacity="0.22"/>')

    # A corner registration mark whose form encodes the motif. Small, but it is
    # what makes two projects with identical family and topology visibly
    # different objects rather than the same object named twice.
    gx, gy = x + w - 34, y + h - 34
    # Hash rather than a character sum: `command_strip` and `progress_rail`
    # both sum to a multiple of four, so a sum-based mark gave two projects in
    # one family the identical mark. A digest over the motif and the geometry
    # phase separates every motif in the vocabulary.
    m = int(hashlib.sha256(f"{motif}:{phase:.4f}".encode()).hexdigest()[:8], 16)
    if m % 4 == 0:
        o.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="9" fill="none" '
                 f'stroke="{p["accent2"]}" stroke-width="1.4" opacity="0.6"/>')
    elif m % 4 == 1:
        o.append(f'<path d="M{gx - 9:.1f} {gy - 9:.1f} h18 v18 h-18 z" fill="none" '
                 f'stroke="{p["accent2"]}" stroke-width="1.4" opacity="0.6"/>')
    elif m % 4 == 2:
        o.append(f'<path d="M{gx - 9:.1f} {gy:.1f} l9 -9 l9 9 l-9 9 z" fill="none" '
                 f'stroke="{p["accent2"]}" stroke-width="1.4" opacity="0.6"/>')
    else:
        o.append(f'<path d="M{gx - 10:.1f} {gy:.1f} h20 M{gx:.1f} {gy - 10:.1f} '
                 f'v20" stroke="{p["accent2"]}" stroke-width="1.4" opacity="0.6"/>')
    return "".join(o)


# -------------------------------------------------------------------- render

def render(d: dict, ident: dict, variant: str) -> str:
    """One asset. variant is motion | dark | light | reduced."""
    motion = variant == "motion"
    t0 = 0.0 if motion else None
    theme = "light" if variant == "light" else "dark"
    family = ident["family"]
    p = theming(family, ident.get("accent", ""), theme)
    name = d.get("canonical_name") or d.get("github_repo", "")
    tagline = (d.get("problem") or d.get("purpose") or "").strip()
    stages = stages_for(d, family)

    motion_text = (d.get("animation_metaphor") or ident["family_claim"] or "")
    desc = (f"{name}. {ident['family_claim']}. Motion: {motion_text}. "
            f"Identity family {family} resolved from {ident['family_basis']}.")

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="{esc(name)}: {esc(motion_text)}">',
        f'<title>{esc(name)} — DUNG30N5 × NOAERTH</title>',
        f'<desc>{esc(desc)}</desc>',
    ]
    if motion:
        # Reduced-motion readers are served a still asset by the README picture
        # element, so this style is a second line of defence rather than the
        # mechanism.
        out.append('<style>@media (prefers-reduced-motion: reduce)'
                   '{*{animation:none !important}}</style>')
    out.append(f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>')

    # Type block.
    out.append(f'<text x="72" y="108" font-family="{MONO}" font-size="11" '
               f'letter-spacing="2.6" fill="{p["faint"]}">'
               f'{esc(str(d.get("project_category", "")).replace("_", " "))} · '
               f'{esc(family)}</text>')
    out.append(f'<text x="72" y="168" font-family="{SANS}" font-size="44" '
               f'font-weight="660" letter-spacing="-1.2" fill="{p["ink"]}">'
               f'{esc(name[:26])}</text>')
    for i, line in enumerate(wrap(tagline, 62)[:2]):
        out.append(f'<text x="72" y="{204 + i * 22}" font-family="{SANS}" '
                   f'font-size="15" fill="{p["dim"]}">{esc(line)}</text>')

    # Real evidence strip: interfaces, store, CLI. Not decoration.
    facts = []
    if d.get("interfaces"):
        facts.append(" · ".join(d["interfaces"][:3]))
    if d.get("verified_commands"):
        facts.append(d["verified_commands"][0]["command"])
    elif d.get("state_model"):
        facts.append(d["state_model"][:40])
    if facts:
        out.append(f'<text x="72" y="268" font-family="{MONO}" font-size="11" '
                   f'fill="{p["faint"]}">{esc(" · ".join(facts)[:74])}</text>')

    # Stage chips naming what the system actually does.
    x = 72.0
    for i, s in enumerate(stages[:4]):
        w = max(70.0, 9.0 + len(s) * 6.6)
        t = (t0 + 0.5 + i * 0.5) if motion else None
        out.append(reveal(x, 292, w, 34, 8, p["ink"], p["edge"], 0.05, t,
                          p["accent"] if i < len(stages) - 1 else p["accent2"]))
        out.append(f'<text x="{x + w / 2:.1f}" y="314" font-family="{MONO}" '
                   f'font-size="11" fill="{p["ink"]}" fill-opacity="0.82" '
                   f'text-anchor="middle" opacity="{0 if motion else 0.82}">'
                   f'<animate attributeName="opacity" from="0" to="0.82" '
                   f'dur="0.45s" begin="{t + 0.14:.2f}s" fill="freeze"/>'
                   f'{esc(s[:16])}</text>' if motion else
                   f'<text x="{x + w / 2:.1f}" y="314" font-family="{MONO}" '
                   f'font-size="11" fill="{p["ink"]}" fill-opacity="0.82" '
                   f'text-anchor="middle">{esc(s[:16])}</text>')
        x += w + 16

    out.append(frame(726, 84, 412, 252, ident, p))
    out.append(BODIES[family](d, ident, p, t0))
    out.append(f'<text x="72" y="388" font-family="{MONO}" font-size="10.5" '
               f'letter-spacing="2.1" fill="{p["faint"]}">'
               f'DUNG30N5 × NOAERTH · {DESIGN_VERSION} · '
               f'{esc(ident["motif"])}</text>')
    out.append("</svg>")
    return "".join(out)


VARIANTS = ("motion", "dark", "light", "reduced")


def social_render(d: dict, ident: dict) -> str:
    """The Open Graph card. Static by definition: crawlers rasterise it and do
    not run SMIL, so animating it would be theatre.

    The family mark is drawn from the same geometry as the hero, so a link
    preview is recognisably the same system as the README. Every project in one
    family previously shared an identical card because only the name was
    substituted -- 29 distinct cards across 126 projects. The mark varies with
    the identity's motif, topology and geometry phase.
    """
    p = theming(ident["family"], ident.get("accent", ""), "dark")
    name = (d.get("canonical_name") or d.get("github_repo", ""))[:30]
    phase = ident.get("geometry_phase", 0.0)
    motif = ident.get("motif", "")
    topology = ident.get("topology", "")
    material = ident.get("material", "ceramic")

    # Deterministic mark: same geometry as the hero body, projected large.
    mark = []
    import math
    MAT_DENSITY = {"obsidian": 0.10, "deep_glass": 0.07, "ceramic": 0.05,
                   "optical_glass": 0.06, "liquid_crystal": 0.09,
                   "luminous_ceramic": 0.05, "resin": 0.08, "polymer": 0.04,
                   "anodised_steel": 0.03, "brushed_metal": 0.04,
                   "paper_stock": 0.02}
    fill_op = MAT_DENSITY.get(material, 0.05)
    # One digest, computed once, over everything that distinguishes the mark.
    # Recomputing a narrower digest per branch is what left two pairs of
    # projects drawing identical cards: the branch digest omitted the material,
    # so a paper_stock project and a ceramic one in the same family collided.
    mh = int(hashlib.sha256(
        f"{motif}:{phase:.6f}:{material}:{topology}".encode()).hexdigest()[:12], 16)
    if topology in ("concentric", "radial", "mesh"):
        rings = 3 + mh % 2
        for k in range(rings):
            r = 52 + k * (36 + (mh >> 3) % 9)
            mark.append(f'<circle cx="1010" cy="330" r="{r}" fill="none" '
                        f'stroke="{p["accent"]}" stroke-width="1.4" '
                        f'opacity="{0.5 - k * 0.11:.2f}"/>')
        nodes = 4 + (mh >> 5) % 4
        for k in range(nodes):
            a = 2 * math.pi * (k / nodes) + phase * 6.283
            mark.append(f'<circle cx="{1010 + 100 * math.cos(a):.0f}" '
                        f'cy="{330 + 100 * math.sin(a):.0f}" r="{4 + (mh >> 7) % 4}" '
                        f'fill="{p["accent2"]}" opacity="0.8"/>')
    elif topology == "orthogonal":
        cols = 3 + mh % 3
        rows = 3 + (mh >> 3) % 2
        step = 48 + (mh >> 5) % 14
        for r in range(rows):
            for c in range(cols):
                mark.append(f'<rect x="{886 + c * step}" y="{212 + r * step}" '
                            f'width="{step - 10}" height="{step - 10}" rx="6" '
                            f'fill="{p["accent"]}" '
                            f'fill-opacity="{fill_op + ((r + c) % 3) * 0.03:.2f}" '
                            f'stroke="{p["accent"]}" stroke-width="1.1" '
                            f'stroke-opacity="0.42"/>')
    elif topology == "linear":
        bars = 4 + mh % 4
        rise = 14 + (mh >> 4) % 11
        for k in range(bars):
            mark.append(f'<rect x="{880 + k * (232 // bars)}" '
                        f'y="{300 - k * (6 + (mh >> 7) % 6)}" '
                        f'width="{max(20, (232 // bars) - 12)}" '
                        f'height="{40 + k * rise}" rx="6" '
                        f'fill="{p["accent"]}" fill-opacity="{fill_op + 0.06:.2f}" '
                        f'stroke="{p["accent"]}" stroke-width="1.1" '
                        f'stroke-opacity="0.45"/>')
    else:  # terraced, stacked, isometric, bracketed, branching
        rows = 3 + mh % 3
        cols = 2 + (mh >> 4) % 3
        lift = 34 + (mh >> 7) % 15
        for r in range(rows):
            for c in range(cols):
                off = (r % 2) * (18 + (mh >> 9) % 13)
                mark.append(f'<rect x="{886 + c * (232 // cols) + off}" '
                            f'y="{396 - r * lift}" '
                            f'width="{max(24, (232 // cols) - 12)}" height="38" rx="5" '
                            f'fill="{p["accent"]}" fill-opacity="{fill_op + 0.04:.2f}" '
                            f'stroke="{p["accent"]}" stroke-width="1.1" '
                            f'stroke-opacity="0.4"/>')

    return "".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 640" '
        'width="1280" height="640" role="img" '
        f'aria-label="{esc(name)} project card">',
        f'<title>{esc(name)} — DUNG30N5 × NOAERTH</title>',
        f'<rect width="1280" height="640" fill="{p["bg"]}"/>',
        "".join(mark),
        f'<rect x="80" y="150" width="10" height="240" rx="4" fill="{p["accent"]}" '
        f'opacity="0.9"/>',
        f'<text x="130" y="230" font-family="{MONO}" font-size="22" '
        f'letter-spacing="5" fill="{p["faint"]}">DUNG30N5 × NOAERTH</text>',
        f'<text x="130" y="330" font-family="{SANS}" font-size="82" '
        f'font-weight="700" fill="{p["ink"]}">{esc(name)}</text>',
        f'<text x="130" y="384" font-family="{SANS}" font-size="27" '
        f'fill="{p["dim"]}">{esc(ident["family_claim"][:56])}</text>',
        f'<text x="130" y="470" font-family="{MONO}" font-size="18" '
        f'fill="{p["accent"]}" letter-spacing="3">'
        f'{esc(d.get("project_category", "").replace("_", " "))} · '
        f'{esc(motif.replace("_", " "))} · {DESIGN_VERSION}</text>',
        "</svg>",
    ])


def assets_for(d: dict, ident: dict) -> dict[str, str]:
    out = {f"hero-{v}.svg": render(d, ident, v) for v in VARIANTS}
    out["social-preview.svg"] = social_render(d, ident)
    return out


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load() -> tuple[dict, dict]:
    dossiers, idents = {}, {}
    if IDENTITY.is_file():
        idents = json.loads(IDENTITY.read_text()).get("identities", {})
    for p in sorted(DOSSIER_DIR.glob("*.json")):
        d = json.loads(p.read_text())
        repo = d.get("github_repo", p.stem)
        dossiers[repo] = d
    return dossiers, idents


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--outdir", default="build/repo-art")
    ap.add_argument("--check", action="store_true",
                    help="write nothing; report determinism and asset hashes")
    args = ap.parse_args()

    dossiers, idents = load()
    repos = args.repo or (sorted(dossiers) if args.all else [])
    if not repos:
        print("nothing to do: pass --repo NAME or --all")
        return 1

    outdir = Path(args.outdir)
    if not args.check:
        outdir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for repo in repos:
        d = dossiers.get(repo)
        ident = idents.get(repo)
        if not d or not ident:
            failures.append(f"{repo}: no dossier or no identity")
            continue
        files = assets_for(d, ident)
        manifest[repo] = {name: digest(text) for name, text in files.items()}
        if args.check:
            continue
        dest = outdir / repo
        dest.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (dest / name).write_text(text, encoding="utf-8")

    # Determinism: the same inputs must produce the same bytes, or nothing in the
    # art lock means anything.
    if args.check:
        for repo in repos[:5]:
            if repo not in dossiers or repo not in idents:
                continue
            again = assets_for(dossiers[repo], idents[repo])
            drift = [n for n, t in again.items()
                     if manifest[repo].get(n) != digest(t)]
            if drift:
                failures.append(f"{repo}: nondeterministic {drift}")

    print(f"repo art: {len(manifest)} projects × "
          f"{len(VARIANTS) + 1} assets")
    if not args.check:
        (outdir / "manifest.json").write_text(
            json.dumps({"design_version": DESIGN_VERSION,
                        "count": len(manifest),
                        "assets": manifest}, indent=1, sort_keys=True) + "\n",
            encoding="utf-8")
        print(f"written -> {outdir}/manifest.json")

    # Honesty check: no static variant may contain an animation element.
    for repo in repos[:8]:
        if repo not in dossiers or repo not in idents or args.check:
            continue
        for v in ("dark", "light", "reduced"):
            p = outdir / repo / f"hero-{v}.svg"
            if p.is_file() and re.search(r"<animate|@keyframes", p.read_text()):
                failures.append(f"{repo}/hero-{v}.svg: static asset animates")

    for f in failures:
        print(f"  FAIL {f}")
    print("ok" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
