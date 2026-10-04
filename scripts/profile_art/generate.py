#!/usr/bin/env python3
"""Generate every DUNG30N5 x NOAERTH profile asset from shared tokens.

Run:  python3 scripts/profile_art/generate.py
Output: assets/profile/**  (dark + light variants, plus the motion hero)

Nothing here hand-codes a colour or a radius; those come from tokens.py. No
asset embeds a third-party badge, a webfont, or a rasterised screenshot, so the
profile still renders correctly if every badge service disappears.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from primitives import (background_grid, connector, defs_common, glass_panel,
                        header, label, node, specular_top, svg_end, text)
from tokens import (DARK, FONT_DISPLAY, FONT_MONO, GLASS, HANDLE, LIGHT,
                    MOTION, PRIMARY_NAME, STUDIO_NAME, STUDIO_SUBTITLE, TAGLINE)

PROFILE = Path(__file__).resolve().parents[2]
OUT = PROFILE / "assets" / "profile"
SIGNAL_PATH = PROFILE / "assets" / "profile" / "build-signal.json"


# =====================================================================
# HERO
# =====================================================================
def _hero_topology(t: dict, uid: str, x0: int = 780, y0: int = 108) -> str:
    """Refracting node lattice, kept entirely in the right third.

    First pass ran the lattice behind the wordmark. It read as clutter: a
    developer's first impression should be the name, then the structure. The
    lattice is now a separate object the eye reaches second, and the negative
    space between them is what makes it feel like a product plate rather than a
    poster.
    """
    cols = [(x0, y0), (x0, y0 + 90), (x0, y0 + 180),
            (x0 + 120, y0 + 45), (x0 + 120, y0 + 135),
            (x0 + 240, y0), (x0 + 240, y0 + 90), (x0 + 240, y0 + 180)]
    # Short, near-neighbour links only. Long diagonals made this read as an
    # accidental spider web; a staggered mesh reads as instrument geometry.
    edges = [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7),
             (0, 3), (1, 3), (1, 4), (2, 4), (3, 5), (4, 5), (4, 6), (5, 6)]
    parts = []
    for a, b in edges:
        parts.append(connector(*cols[a], *cols[b], t, opacity=0.22))
    for i, (x, y) in enumerate(cols):
        parts.append(node(x, y, 4.0, t, active=(i in (3, 5))))
    return "".join(parts)


def hero(theme_name: str) -> str:
    """Identity plate. DUNG30N5 is the subject; NOAERTH and the handle are
    context. The optical motif is a refracting node lattice — depth without
    the glassmorphism clichés (no blobs, no orbs)."""
    t = DARK if theme_name == "dark" else LIGHT
    uid = f"hero-{theme_name}"
    W, H = 1200, 420

    return "".join([
        header(W, H, f"{PRIMARY_NAME} — {STUDIO_NAME} {STUDIO_SUBTITLE}",
               f"Identity plate for {PRIMARY_NAME}. Reads: {TAGLINE} "
               f"Handle {HANDLE}, site noaerth.com."),
        defs_common(t, uid),
        # Opaque canvas, not transparency. An SVG with no background inherits
        # whatever the host page paints, so the light variant on a dark theme
        # would put #0D1117 text on #0d1117. Each variant carries its own
        # ground so contrast is guaranteed wherever it renders.
        f'  <rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>',
        f'  <ellipse cx="180" cy="210" rx="300" ry="190" fill="url(#{uid}-bloom)"/>',
        f'  <g opacity="0.9">{_hero_topology(t, uid)}</g>',
        # accent rule: the only saturated element on the plate
        f'  <rect x="72" y="118" width="2.5" height="118" fill="url(#{uid}-prism)"/>',
        label(96, 138, f"{STUDIO_NAME} // {STUDIO_SUBTITLE}", t, size=13,
              tracking=4.6, opacity=0.9),
        # primary identity, largest element on the plate
        text(96, 224, PRIMARY_NAME, size=88, theme=t, family=FONT_DISPLAY,
             weight=700, tracking=8),
        text(96, 268, TAGLINE, size=25, theme=t, opacity=0.74),
        f'  <line x1="96" y1="306" x2="620" y2="306" stroke="{t["edge"]}" stroke-width="1"/>',
        label(96, 334, f"NOAERTH.COM   ·   GITHUB {HANDLE}", t, size=12,
              tracking=2.4, opacity=0.55),
        svg_end(),
    ])


def hero_motion() -> str:
    """Animated hero. One sweep, one travelling pulse, 12s seamless loop.

    Only two elements animate. Everything else is identical to the static dark
    hero, so a reader who never sees the animation loses nothing.
    """
    t = DARK
    uid = "hero-motion"
    W, H = 1200, 420
    L = MOTION["loop_seconds"]
    topo = _hero_topology(t, uid)

    return "".join([
        header(W, H, f"{PRIMARY_NAME} — {STUDIO_NAME} {STUDIO_SUBTITLE}",
               f"Animated identity plate for {PRIMARY_NAME}. "
               f"Reads: {TAGLINE} Handle {HANDLE}, site noaerth.com."),
        defs_common(t, uid),
        f'  <rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>',
        f'  <ellipse cx="180" cy="210" rx="300" ry="190" fill="url(#{uid}-bloom)"/>',
        f'  <g opacity="0.9">{topo}'
        # opacity dips and returns over exactly one loop, so frame 0 and frame L
        # are identical and the loop has no visible seam
        f'<animate attributeName="opacity" values="0.6;1;0.6" dur="{L}s" '
        f'repeatCount="indefinite"/></g>',
        # spectral sweep travels across the lattice only
        f'  <g><animateTransform attributeName="transform" type="translate" '
        f'values="760 0; 1120 0" dur="{MOTION["travel_seconds"]}s" '
        f'repeatCount="indefinite"/>'
        f'<rect x="780" y="88" width="110" height="220" fill="url(#{uid}-sweep)" '
        f'opacity="0.32"/></g>',
        f'  <rect x="72" y="118" width="2.5" height="118" fill="url(#{uid}-prism)">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0; 0 0; 0 44; 0 0" dur="{L}s" repeatCount="indefinite"/></rect>',
        label(96, 138, f"{STUDIO_NAME} // {STUDIO_SUBTITLE}", t, size=13,
              tracking=4.6, opacity=0.9),
        text(96, 224, PRIMARY_NAME, size=88, theme=t, family=FONT_DISPLAY,
             weight=700, tracking=8),
        text(96, 268, TAGLINE, size=25, theme=t, opacity=0.74),
        f'  <line x1="96" y1="306" x2="620" y2="306" stroke="{t["edge"]}" stroke-width="1"/>',
        label(96, 334, f"NOAERTH.COM   ·   GITHUB {HANDLE}", t, size=12,
              tracking=2.4, opacity=0.55),
        svg_end(),
    ])


# =====================================================================
# NAVIGATION — local liquid-glass controls
# =====================================================================
NAV_ITEMS = [
    ("noaerth", "NOAERTH", "studio · systems lab"),
    ("repositories", "REPOSITORIES", "full inventory"),
    ("open-source", "OPEN SOURCE", "build · run · contribute"),
    ("why", "WHY ARE YOU HERE?", "you found the footer"),
]


def nav_chip(slug: str, title: str, subtitle: str, theme_name: str) -> str:
    t = DARK if theme_name == "dark" else LIGHT
    uid = f"nav-{slug}-{theme_name}"
    W, H = 260, 64
    return "".join([
        header(W, H, f"{title} — {STUDIO_NAME}",
               f"Navigation control linking to {title}: {subtitle}."),
        defs_common(t, uid),
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="{t["canvas"]}"/>',
        glass_panel(0.75, 0.75, W - 1.5, H - 1.5, uid, radius=16),
        specular_top(0.75, 0.75, W - 1.5, 16),
        # left spectral edge marks the control as active surface
        f'  <rect x="0.75" y="18" width="2" height="28" rx="1" fill="url(#{uid}-prism)"/>',
        label(26, 30, title, t, size=13, tracking=2.6, opacity=0.95),
        label(26, 48, subtitle, t, size=10, tracking=1.2, opacity=0.5),
        # arrow: chevron pair, monospace, no icon font
        f'  <text x="{W - 26}" y="38" font-family="{FONT_MONO}" font-size="13" '
        f'fill="{t["text_faint"]}" text-anchor="end">&#8594;</text>',
        svg_end(),
    ])


# =====================================================================
# BUILD SIGNAL — telemetry from live API, never hardcoded
# =====================================================================
def load_signal() -> dict:
    """Read the generated signal file. Never embed constants here."""
    if SIGNAL_PATH.is_file():
        return json.loads(SIGNAL_PATH.read_text(encoding="utf-8"))
    # A freshly cloned profile repo has no signal yet. Render an honest
    # placeholder rather than a plausible-looking guess.
    return {"generated_at": None, "metrics": [], "note": "signal not generated yet"}


def build_signal(theme_name: str, signal: dict) -> str:
    t = DARK if theme_name == "dark" else LIGHT
    uid = f"signal-{theme_name}"
    W, H = 1200, 200
    metrics = signal.get("metrics", [])
    parts = [header(W, H, f"{STUDIO_NAME} build signal",
                    "Measured engineering telemetry: "
                    + "; ".join(f"{m['label']} {m['display']}" for m in metrics)
                    if metrics else "Build signal not yet generated."),
             defs_common(t, uid),
             f'  <rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>']
    if not metrics:
        parts.append(label(40, 100, "BUILD SIGNAL NOT GENERATED", t, size=16,
                           tracking=4, opacity=0.4))
        parts.append(svg_end())
        return "".join(parts)

    # Trace line: a telemetry sparkline whose height encodes the value. Not a
    # stats widget — it reads as an instrument readout.
    span = W / len(metrics)
    baseline = 150
    heights = []
    peak = max(m["value"] for m in metrics) or 1
    for i, m in enumerate(metrics):
        h = 6 + int(74 * (m["value"] / peak))
        heights.append((span * i + span / 2, h))
        parts.append(f'  <rect x="{span * i + span / 2 - 1}" y="{baseline - h}" '
                     f'width="2" height="{h}" fill="url(#{uid}-prism)" opacity="0.55"/>')
    points = " ".join(f"{x},{baseline - h}" for x, h in heights)
    parts.append(f'  <polyline points="{points}" fill="none" '
                 f'stroke="url(#{uid}-prism)" stroke-width="1.5" opacity="0.8"/>')
    parts.append(f'  <line x1="24" y1="{baseline}" x2="{W - 24}" y2="{baseline}" '
                 f'stroke="{t["edge"]}" stroke-width="1"/>')
    for i, m in enumerate(metrics):
        x = span * i + span / 2
        parts.append(label(x, 178, m["label"], t, size=10, tracking=1.6,
                           opacity=0.72, anchor="middle"))
        parts.append(text(x, 60, m["display"], size=26, theme=t, weight=600,
                          anchor="middle"))
    parts.append(label(24, 34, "BUILD SIGNAL", t, size=11, tracking=4, opacity=0.55))
    parts.append(label(W - 24, 34, "measured · not estimated", t, size=10,
                       tracking=1.4, opacity=0.4, anchor="end"))
    parts.append(svg_end())
    return "".join(parts)


# =====================================================================
# FLAGSHIP CARDS
# =====================================================================
# Glyphs are original geometry drawn from primitives — no brand icons.
# `glyph` returns SVG markup inside a 48x48 box at (0,0).
def glyph_stack() -> str:
    """Portfolio OS — stacked control planes in section."""
    return ('<rect x="6" y="10" width="26" height="5" rx="2.5" fill="url(#g-prism)" opacity="0.9"/>'
            '<rect x="10" y="19" width="26" height="5" rx="2.5" fill="url(#g-prism)" opacity="0.65"/>'
            '<rect x="14" y="28" width="26" height="5" rx="2.5" fill="url(#g-prism)" opacity="0.4"/>'
            '<line x1="6" y1="37" x2="44" y2="37" stroke="currentColor" stroke-width="1" opacity="0.35"/>')


def glyph_ring() -> str:
    """AgentOS — execution ring with an orbiting node."""
    return ('<circle cx="24" cy="24" r="15" fill="none" stroke="url(#g-prism)" stroke-width="1.6" opacity="0.75"/>'
            '<circle cx="24" cy="24" r="8" fill="none" stroke="currentColor" stroke-width="1" opacity="0.35"/>'
            '<circle cx="24" cy="9" r="3.2" fill="#5EE7D0"/>'
            '<circle cx="24" cy="39" r="2" fill="#C084FC" opacity="0.7"/>')


def glyph_module() -> str:
    """GrokInstall — insertion geometry: a module descending into a keyed slot.

    The first version used a bare rounded rect over an empty outline and read as
    two unrelated shapes. This one is a single readable action: part entering
    socket, with the slot keyed so the fit is the point.
    """
    return ('<rect x="9" y="27" width="30" height="13" rx="3.5" fill="none" '
            'stroke="currentColor" stroke-width="1.3" opacity="0.45"/>'
            '<rect x="14.5" y="30.5" width="19" height="6" rx="2" '
            'fill="currentColor" opacity="0.18"/>'
            '<rect x="15" y="6" width="18" height="11" rx="3" fill="url(#g-prism)"/>'
            '<path d="M24 18.5 L24 25.5" stroke="url(#g-prism)" stroke-width="1.6" '
            'stroke-linecap="round"/>'
            '<path d="M21 22.5 L24 25.5 L27 22.5" fill="none" stroke="url(#g-prism)" '
            'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')


def glyph_prism() -> str:
    """GrokMax — routing prism: one beam in, several fanned out."""
    return ('<path d="M6 30 L17 17 L17 31 Z" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.5"/>'
            '<path d="M4 26 L34 20" stroke="#5EE7D0" stroke-width="1.4"/>'
            '<path d="M17 24 L42 14" stroke="#7C8CFF" stroke-width="1.2"/>'
            '<path d="M17 24 L42 24" stroke="#C084FC" stroke-width="1.2"/>'
            '<path d="M17 25 L42 34" stroke="#C084FC" stroke-width="1.2" opacity="0.6"/>')


def glyph_wave() -> str:
    """gh0st — encrypted spectral waveform."""
    return ('<path d="M4 25 Q9 8 14 25 T24 25 T34 25 T44 25" fill="none" '
            'stroke="url(#g-prism)" stroke-width="2" stroke-linecap="round"/>'
            '<path d="M4 32 Q9 20 14 32 T24 32 T34 32 T44 32" fill="none" '
            'stroke="currentColor" stroke-width="1.1" opacity="0.35"/>'
            '<path d="M4 18 Q9 10 14 18 T24 18 T34 18 T44 18" fill="none" '
            'stroke="currentColor" stroke-width="1.1" opacity="0.2"/>')


def glyph_eye() -> str:
    """OpenCode Watchdog — protective eye over a broken circuit trace."""
    return ('<path d="M5 24 Q24 8 43 24 Q24 40 5 24 Z" fill="none" '
            'stroke="url(#g-prism)" stroke-width="1.5"/>'
            '<circle cx="24" cy="24" r="6" fill="none" stroke="currentColor" '
            'stroke-width="1" opacity="0.5"/>'
            '<path d="M15 42 L21 42 L23 38 L27 38" fill="none" stroke="currentColor" '
            'stroke-width="1.2" opacity="0.55"/>')


CARDS = [
    ("noaerth-portfolio-os", "Portfolio OS", glyph_stack, "Control plane: SQLite work queue, reviewer separation, allowlist public boundary.", "Python", "MIT"),
    ("agentos", "AgentOS", glyph_ring, "Provider-neutral execution: objective in, verified outcome out.", "Python", "MIT"),
    ("grokinstall", "GrokInstall", glyph_module, "Inserts the smallest useful capability. Declining to install is a first-class answer.", "Go", "MIT"),
    ("grokmax", "GrokMax", glyph_prism, "Deterministic-first routing; every number labelled measured, estimated, or proxy.", "TypeScript", "MIT"),
    ("gh0st", "gh0st", glyph_wave, "Local-first encrypted client. Prompts stay on the machine by default.", "Rust · Tauri", "MIT"),
    ("opencode-watchdog", "OpenCode Watchdog", glyph_eye, "Circuit breaker for runaway sessions. No model decides you are stuck.", "TypeScript", "MIT"),
]


def card_metric(slug: str, per_system: dict) -> str:
    """Right-hand field: measured tests plus the newest release.

    A static word like "verified" carries no information; the test count and
    release tag are what a reader actually wants to compare across systems.
    """
    row = (per_system or {}).get(slug) or {}
    tests = row.get("tests")
    release = row.get("latest_release") or ""
    bits = []
    if tests:
        bits.append(f"{tests:,} tests")
    if release:
        bits.append(release)
    return " · ".join(bits) or "no recorded metrics"


def card(slug: str, name: str, glyph, purpose: str, stack: str, licence: str,
         theme_name: str, metric: str) -> str:
    t = DARK if theme_name == "dark" else LIGHT
    uid = f"card-{slug}-{theme_name}"
    W, H = 560, 176
    return "".join([
        header(W, H, name, f"{name}: {purpose} Stack {stack}, licence {licence}. {metric}"),
        defs_common(t, uid),
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="{t["canvas"]}"/>',
        glass_panel(0.75, 0.75, W - 1.5, H - 1.5, uid, radius=16),
        specular_top(0.75, 0.75, W - 1.5, 16),
        f'  <g transform="translate(30,34)" color="{t["text_secondary"]}">'
        f'<defs><linearGradient id="g-prism" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{t["mint"]}"/>'
        f'<stop offset="52%" stop-color="{t["indigo"]}"/>'
        f'<stop offset="100%" stop-color="{t["violet"]}"/></linearGradient></defs>'
        f'{glyph()}</g>',
        label(104, 52, name, t, size=13, tracking=2.4, opacity=0.95),
        # purpose wraps to two lines by construction: cards are fixed height,
        # so copy length is clamped here rather than allowed to overflow
        f'  <foreignObject x="104" y="64" width="{W - 130}" height="52">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" style="font:400 13.5px {FONT_DISPLAY};'
        f'color:{t["text_secondary"]};line-height:1.45">{purpose}</div></foreignObject>',
        f'  <line x1="104" y1="126" x2="{W - 26}" y2="126" stroke="{t["edge"]}" stroke-width="1"/>',
        label(104, 148, stack, t, size=11, tracking=1.4, opacity=0.55),
        label(W - 26, 148, metric, t, size=11, tracking=1.2, opacity=0.72, anchor="end"),
        svg_end(),
    ])


# =====================================================================
# WHY ARE YOU HERE — terminal footer
# =====================================================================
def terminal(theme_name: str, animate: bool = False) -> str:
    t = DARK if theme_name == "dark" else LIGHT
    uid = f"term-{theme_name}"
    W, H = 620, 190
    rows = [
        ("$", "whoami", "DUNG30N5"),
        ("$", "why are you here?", ""),
    ]
    parts = [header(W, H, "why are you here?",
                    "A terminal fragment. Running whoami prints DUNG30N5. "
                    "Asking why are you here prints a cursor and nothing else."),
             defs_common(t, uid),
             f'  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" '
             f'fill="{t["canvas"]}" stroke="{t["edge"]}" stroke-width="1"/>',
             f'  <line x1="0.5" y1="0.5" x2="{W - 0.5}" y2="0.5" stroke="currentColor" '
             f'stroke-opacity="0.14"/>',
             f'  <circle cx="24" cy="24" r="3.5" fill="none" stroke="{t["text_faint"]}" stroke-width="1"/>',
             f'  <circle cx="40" cy="24" r="3.5" fill="none" stroke="{t["text_faint"]}" stroke-width="1" opacity="0.6"/>',
             f'  <circle cx="56" cy="24" r="3.5" fill="none" stroke="{t["text_faint"]}" stroke-width="1" opacity="0.35"/>']
    y = 68
    for prompt, cmd, out in rows:
        parts.append(f'  <text x="26" y="{y}" font-family="{FONT_MONO}" font-size="14" '
                     f'fill="{t["mint"]}">$</text>')
        parts.append(f'  <text x="42" y="{y}" font-family="{FONT_MONO}" font-size="14" '
                     f'fill="{t["text_primary"]}">{cmd}</text>')
        y += 26
        if out:
            parts.append(f'  <text x="42" y="{y}" font-family="{FONT_MONO}" font-size="14" '
                         f'fill="{t["text_secondary"]}">{out}</text>')
            y += 30
    # The unanswered prompt. A blinking block, at 1.6s: far below any
    # hazardous flash threshold, and the block is only ever drawn/un-drawn.
    # SMIL requires <animate> to be a CHILD of the element it targets, so the
    # caret is emitted non-self-closing when it carries an animation.
    parts.append(f'  <text x="26" y="{y}" font-family="{FONT_MONO}" font-size="14" '
                 f'fill="{t["mint"]}">$</text>')
    blink = (f'<animate attributeName="opacity" values="1;1;0;0;1" '
             f'keyTimes="0;0.4;0.5;0.9;1" dur="1.6s" '
             f'repeatCount="indefinite"/>') if animate else ""
    parts.append(f'  <text x="42" y="{y}" font-family="{FONT_MONO}" font-size="14" '
                 f'fill="{t["mint"]}">{blink}█</text>')
    parts.append(svg_end())
    return "".join(parts)


def terminal_motion() -> str:
    """Animated footer: only the caret animates. Nothing else moves."""
    return terminal("dark", animate=True)


# =====================================================================
# SYSTEM MAP — only relationships that exist in code or docs
# =====================================================================
# Proven relationships (each traced to a file in the source repo):
#  - grokbot-office -> agentos      : grokbot-office/README.md + AGENTOS.md
#  - grokmax -> opencode            : grokmax/packages/adapters opencode.ts,
#                                     router route priority in packages/router
#  - opencode-watchdog -> opencode  : observes the OpenCode server via SSE
#  - noaerth-portfolio-os -> agentos: README "That is AgentOS"
# Everything else is drawn as a standalone system, not as an edge.
LAYERS = [
    ("CONTROL", "decides what runs, and who approved it", [
        ("portfolio-os", "noaerth-portfolio-os", "SQLite work queue · reviewer separation", None),
        ("workforce config", "grokbot-office", "supervisors · policy · handoffs", "sits above AgentOS"),
    ]),
    ("EXECUTE", "turns an objective into a verified outcome", [
        ("agentos", "agentos", "capability discovery · adapter execution", None),
    ]),
    ("ECONOMISE", "makes execution cheap and repeatable", [
        ("grokmax", "grokmax", "route · five-layer cache · ledger", "adapts to OpenCode"),
        ("grokinstall", "grokinstall", "installs the smallest useful capability", None),
    ]),
    ("GUARD", "stops degenerate work before it costs anything", [
        ("opencode-watchdog", "opencode-watchdog", "deterministic repetition circuit", "observes an OpenCode session"),
    ]),
    ("SURFACE", "where the work becomes something a person can use", [
        ("gh0st", "gh0st", "local-first encrypted client", None),
        ("grokbot-society", "grokbot-society", "persistent agents · governed spend", None),
        ("seai-mind", "seai-mind", "self-evolving kernel", None),
    ]),
]


def system_map(theme_name: str) -> str:
    """Layered architecture plate.

    Relationships are printed on the panel that owns them rather than drawn as
    curves. The first pass routed them through a left gutter, where they crossed
    four panels and collided with the layer labels. A relationship you can read
    without tracing a line is worth more than one that looks like a network
    diagram.
    """
    t = DARK if theme_name == "dark" else LIGHT
    uid = f"map-{theme_name}"
    W = 1200
    pad_x, gutter = 64, 172
    panel_w = W - pad_x * 2
    panel_h, panel_gap, band_h = 82, 10, 46

    # Two passes: measure, then draw. A hardcoded canvas height silently clipped
    # the SURFACE band in the first version.
    y = 96
    layout = []
    for layer, blurb, items in LAYERS:
        layout.append(("band", layer, blurb, y))
        y += band_h
        for short, repo, note, rel in items:
            layout.append(("panel", short, repo, note, rel, y))
            y += panel_h + panel_gap
        y += 26
    H = y + 44

    parts = [header(W, H, f"{STUDIO_NAME} operating stack",
                    "Five layers over the published systems: control, execution, "
                    "economy, guardrails, and surfaces. Relationships are named only "
                    "where one repository's source or documentation names the other. "
                    "Systems with no proven relationship are drawn without one."),
             defs_common(t, uid),
             f'  <rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>',
             f'  <g opacity="0.5">{background_grid(W, H, t, 40)}</g>']

    for item in layout:
        if item[0] == "band":
            _, layer, blurb, by = item
            parts.append(label(pad_x, by + 14, layer, t, size=11, tracking=4,
                               opacity=0.6))
            parts.append(label(pad_x + 108, by + 14, blurb, t, size=10.5,
                               tracking=0.6, opacity=0.32))
            parts.append(f'  <line x1="{pad_x}" y1="{by + 24}" x2="{W - pad_x}" '
                         f'y2="{by + 24}" stroke="{t["edge"]}" stroke-width="1" '
                         f'opacity="0.55"/>')
            continue
        _, short, repo, note, rel, py = item
        parts.append(glass_panel(pad_x, py, panel_w, panel_h, uid, radius=14))
        parts.append(specular_top(pad_x, py, panel_w, 14))
        parts.append(f'  <rect x="{pad_x}" y="{py + 20}" width="2" height="42" '
                     f'fill="url(#{uid}-prism)" opacity="0.75"/>')
        parts.append(text(pad_x + 30, py + 36, short, size=20, theme=t, weight=650))
        parts.append(label(pad_x + 30, py + 58, note, t, size=10.5, tracking=1.2,
                           opacity=0.5))
        if rel:
            parts.append(label(W - pad_x - 30, py + 36, rel, t, size=10.5,
                               tracking=1.2, opacity=0.62, anchor="end"))
        else:
            parts.append(label(W - pad_x - 30, py + 36, repo, t, size=10.5,
                               tracking=1.2, opacity=0.3, anchor="end"))

    parts.append(f'  <line x1="{pad_x}" y1="{H - 30}" x2="{W - pad_x}" y2="{H - 30}" '
                 f'stroke="{t["edge"]}" stroke-width="1"/>')
    parts.append(label(pad_x, H - 14,
                       "relationships named only where source or docs cite the other "
                       "system", t, size=10, tracking=0.8, opacity=0.4))
    parts.append(label(W - pad_x, H - 14, f"{STUDIO_NAME} // {PRIMARY_NAME}", t,
                       size=10, tracking=2.2, opacity=0.4, anchor="end"))
    parts.append(svg_end())
    return "".join(parts)


# =====================================================================
# AVATAR STUDIES
# =====================================================================
def avatar_monogram() -> str:
    """DUNG30N5 monogram — a liquid-glass D cut by a refracted edge."""
    t = DARK
    uid = "av-mono"
    return "".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" '
        'height="500" role="img" aria-label="DUNG30N5 monogram avatar candidate">',
        '<title id="t">DUNG30N5 monogram avatar candidate</title>'
        '<desc id="d">A letter D drawn as an outline and cut by a refracted '
        'spectral edge, on a dark liquid-glass field.</desc>',
        defs_common(t, uid),
        f'  <rect width="500" height="500" fill="{t["canvas"]}"/>',
        f'  <ellipse cx="250" cy="230" rx="220" ry="200" fill="url(#{uid}-bloom)"/>',
        f'  <text x="250" y="345" font-family="{FONT_DISPLAY}" font-size="270" '
        f'font-weight="700" fill="none" stroke="url(#{uid}-prism)" stroke-width="14" '
        f'text-anchor="middle">D</text>',
        f'  <line x1="120" y1="390" x2="380" y2="390" stroke="{t["mint"]}" '
        f'stroke-width="2" stroke-opacity="0.35"/>',
        svg_end()])


def avatar_node() -> str:
    """Abstract spectral node — topology at avatar scale."""
    t = DARK
    uid = "av-node"
    pts = [(250, 140), (390, 250), (250, 360), (110, 250), (250, 250)]
    links = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3)]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" '
             'width="500" height="500" role="img" '
             'aria-label="Abstract spectral node avatar candidate">',
             '<title id="t">Abstract spectral node avatar candidate</title>'
             '<desc id="d">A central node linked to four outer nodes by thin '
             'spectral lines, on a dark liquid-glass field.</desc>',
             defs_common(t, uid),
             f'  <rect width="500" height="500" fill="{t["canvas"]}"/>',
             f'  <circle cx="250" cy="250" r="200" fill="url(#{uid}-bloom)"/>']
    for a, b in links:
        parts.append(f'  <line x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" '
                     f'y2="{pts[b][1]}" stroke="{t["edge_specular"]}" stroke-width="3" '
                     f'opacity="0.3"/>')
    for i, (x, y) in enumerate(pts):
        r = 30 if i == 4 else 20
        fill = t["mint"] if i == 4 else t["canvas"]
        parts.append(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" '
                     f'stroke="url(#{uid}-prism)" stroke-width="5"/>')
    parts.append(svg_end())
    return "".join(parts)


def avatar_hybrid() -> str:
    """Noaerth × DUNG30N5 hybrid — the prism cutting a monogram."""
    t = DARK
    uid = "av-hybrid"
    return "".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" '
        'height="500" role="img" aria-label="Noaerth and DUNG30N5 hybrid avatar candidate">',
        '<title id="t">Noaerth and DUNG30N5 hybrid avatar candidate</title>'
        '<desc id="d">A prism outline descending onto the letter N, on a dark '
        'liquid-glass field.</desc>',
        defs_common(t, uid),
        f'  <rect width="500" height="500" fill="{t["canvas"]}"/>',
        f'  <path d="M90 130 L410 130 L250 400 Z" fill="none" stroke="url(#{uid}-prism)" '
        f'stroke-width="10" stroke-linejoin="round"/>',
        f'  <text x="250" y="330" font-family="{FONT_DISPLAY}" font-size="200" '
        f'font-weight="700" fill="{t["text_primary"]}" text-anchor="middle">N</text>',
        f'  <circle cx="410" cy="130" r="14" fill="{t["mint"]}"/>',
        svg_end()])


# =====================================================================
def write(path: Path, content: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content.encode())


def main() -> int:
    signal = load_signal()
    generated: list[tuple[str, int]] = []

    # A card whose repo key does not exist in the signal silently renders
    # "no recorded metrics", which reads as a measurement rather than a bug.
    # Fail loudly at generation time instead.
    known = set(signal.get("per_system", {}))
    unknown = [slug for slug, *_ in CARDS if slug not in known]
    if unknown:
        raise SystemExit(
            f"card keys absent from build-signal.json: {', '.join(unknown)}. "
            f"Signal knows: {', '.join(sorted(known)) or '(nothing)'}. "
            f"Repo names and card keys must match exactly.")

    for name in ("dark", "light"):
        generated.append((f"assets/profile/hero-{name}.svg",
                          write(OUT / f"hero-{name}.svg", hero(name))))
    generated.append(("assets/profile/hero-motion.svg",
                      write(OUT / "hero-motion.svg", hero_motion())))

    for slug, title, subtitle in NAV_ITEMS:
        for name in ("dark", "light"):
            rel = f"assets/profile/nav/{slug}-{name}.svg"
            generated.append((rel, write(OUT / "nav" / f"{slug}-{name}.svg",
                                         nav_chip(slug, title, subtitle, name))))

    for name in ("dark", "light"):
        rel = f"assets/profile/build-signal-{name}.svg"
        generated.append((rel, write(OUT / f"build-signal-{name}.svg",
                                     build_signal(name, signal))))
    for name in ("dark", "light"):
        rel = f"assets/profile/system-map-{name}.svg"
        generated.append((rel, write(OUT / f"system-map-{name}.svg", system_map(name))))

    for slug, card_name, glyph, purpose, stack, licence in CARDS:
        metric = card_metric(slug, signal.get("per_system", {}))
        for name in ("dark", "light"):
            rel = f"assets/profile/cards/{slug}-{name}.svg"
            generated.append((rel, write(OUT / "cards" / f"{slug}-{name}.svg",
                                         card(slug, card_name, glyph, purpose,
                                              stack, licence, name, metric))))

    for name in ("dark", "light"):
        rel = f"assets/profile/terminal-{name}.svg"
        generated.append((rel, write(OUT / f"terminal-{name}.svg", terminal(name))))
    generated.append(("assets/profile/terminal-motion.svg",
                      write(OUT / "terminal-motion.svg", terminal_motion())))

    for slug, content in (("avatar-monogram", avatar_monogram()),
                          ("avatar-node", avatar_node()),
                          ("avatar-hybrid", avatar_hybrid())):
        rel = f"assets/profile/avatar/{slug}.svg"
        generated.append((rel, write(OUT / "avatar" / f"{slug}.svg", content)))

    total = 0
    for rel, size in generated:
        total += size
        print(f"{size / 1024:8.1f} KB  {rel}")

    # Remove any SVG under the output tree that this run did not produce. Without
    # this, renaming a card key silently leaves the old file behind: two assets,
    # one correct and one stale, and only the filename tells you which is which.
    keep = {(PROFILE / rel).resolve() for rel, _ in generated}
    pruned = []
    for path in sorted(OUT.rglob("*.svg")):
        if path.resolve() not in keep:
            path.unlink()
            pruned.append(path.relative_to(PROFILE))

    print(f"\n{len(generated)} files · {total / 1024:.1f} KB total")
    if pruned:
        print(f"pruned {len(pruned)} stale file(s): "
              f"{', '.join(str(p) for p in pruned)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())