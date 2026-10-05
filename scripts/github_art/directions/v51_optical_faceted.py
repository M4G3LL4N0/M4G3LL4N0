"""V5.1 — HYPERREAL GEOMETRIC, built on the V5 skeleton.

Internal name: OPTICAL TOPOLOGY / FACETED ARCHITECTURE.

Nothing here resets the V5 system. Crispness, semantic primitives, the tick
rail, the recursive module, the CONTROL strata, the evidence discipline, the
measurable validators, and the verified motion architecture all carry forward.
V5.1 adds dimensionality and the geometric vocabulary on top of that skeleton,
because the skeleton is what keeps the addition from becoming wallpaper.

What is new:

    isometric architecture   stacked cubes, stepped progression, lattice
    faceted aperture         the master motif (see the honest renaming note)
    split ring               a circuit that trips, for guardrail surfaces
    impossible frame         depth through occlusion only
    memphis punctuation      capped at MEMPHIS_SHARE of surface
    soft counterpoint        arches and petals against the crystalline forms

What is deliberately unchanged:

    the wordmark is never distorted or overlapped
    approximately 70% of every hero surface stays calm
    no JavaScript, no foreignObject, no webfonts, no blur under type
    reduced motion is gated at the README layer, where it was verified to work
    every drawn relationship still resolves to system-map-evidence.json
"""
from __future__ import annotations

import math

from .. import geometry as G5
from .. import geometry_v51 as G
from .. import materials as M
from .. import project_identity as P
from .. import tokens as T
from .. import typography as TY

NAME = "OPTICAL TOPOLOGY / FACETED ARCHITECTURE"
SLUG = "v51-optical-faceted"
SUPERSEDES = "v5-optical-recursive"
VERSION = "5.1"

INTENSITY = {
    "profile_hero": 0.78,
    "profile_body": 0.34,
    "flagship_hero": 0.58,
    "system_map": 0.62,
    "build_signal": 0.48,
    "legacy_artifact": 0.58,
}

DENSITY = "D4_SHOWCASE"  # hero; see tokens.DENSITY_TARGET for the full ladder


def _defs(theme: str, *materials: str) -> str:
    return "".join(M.definitions(theme, m) for m in materials)


def _calm_grid(W: int, H: int, theme: str, opacity: float = 0.26) -> str:
    """The recursive substrate. Quiet, so the sculpture has something to sit on."""
    return f'<g opacity="{opacity}">{G5.micro_grid(W, H, theme, step=40)}</g>'


# ==========================================================================
# HERO
# ==========================================================================
def hero(theme_name: str = "dark", compact: bool = False,
         motion: bool = False) -> str:
    t = T.PALETTES[theme_name]
    tagline = tuple(f.rstrip(".")[0].upper() + f.rstrip(".")[1:].lower()
                    for f in T.PRIMARY_TAGLINE)
    W, H = (460, 440) if compact else (1200, 440)
    defs = _defs(theme_name, "optical_glass", "deep_glass", "computational")

    # Ambient only, two moving elements, both duplicated as static twins.
    anim = ""
    if motion and not compact:
        L = T.MOTION["loop_seconds"]
        anim = (
            # one slow signal traversing the architecture
            f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0; 300 0" dur="{T.MOTION["travel_seconds"]}s" '
            f'repeatCount="indefinite"/>'
            f'<circle cx="700" cy="230" r="3.4" fill="{t["mint"]}"/></g>'
            # one breath on the aperture, opacity only
            f'<g><animate attributeName="opacity" '
            f'values="{T.MOTION["breath_low"]};{T.MOTION["breath_high"]};'
            f'{T.MOTION["breath_low"]}" dur="{L}s" repeatCount="indefinite"/>'
            f'<circle cx="1010" cy="228" r="150" fill="none" '
            f'stroke="{t["mint"]}" stroke-width="1" stroke-opacity="0.22"/>'
            f'</g>'
        )

    if compact:
        # recomposed, not scaled: secondary architecture removed, motif kept
        body = [
            _calm_grid(W, H, theme_name, 0.30),
            f'<rect x="44" y="92" width="2.5" height="128" '
            f'fill="{M.prism_fill(theme_name, "optical_glass")}"/>',
            TY.label(62, 112, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}",
                     theme_name, size=9.5, tracking=3.0),
            TY.text(62, 162, T.PRIMARY_NAME, theme_name, size=52, weight=700,
                    tracking=3),
            TY.text(62, 200, f"{tagline[0]}.", theme_name, size=15,
                    fill=t["text_secondary"]),
            TY.text(62, 222, f"{tagline[1]}.", theme_name, size=15,
                    fill=t["text_secondary"]),
            TY.text(62, 244, f"{tagline[2]}.", theme_name, size=15,
                    fill=t["text_secondary"]),
            f'<g opacity="0.9" transform="translate(300,318)">'
            f'{G.faceted_aperture(0, 0, 46, theme_name, "mint", levels=2)}</g>',
            G5.tick_rail(62, 274, 210, theme_name),
            TY.label(62, 306, "NOAERTH.COM", theme_name, size=9.5, opacity=0.55),
            TY.label(62, 326, f"GITHUB {T.HANDLE}", theme_name, size=9.5,
                     opacity=0.55),
            TY.label(62, 366, T.POSITIONING.upper(), theme_name, size=8.5,
                     tracking=1.6, opacity=0.34),
            anim,
        ]
    else:
        body = [
            _calm_grid(W, H, theme_name),
            f'<rect x="72" y="106" width="2.5" height="150" '
            f'fill="{M.prism_fill(theme_name, "optical_glass")}"/>',
            TY.label(98, 132, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}",
                     theme_name, size=12.5, tracking=4.4),
            # the wordmark stays the dominant element and nothing overlaps it
            TY.text(98, 228, T.PRIMARY_NAME, theme_name, size=88, weight=700,
                    tracking=8),
            TY.text(98, 268, f"{tagline[0]}. {tagline[1]}. {tagline[2]}.",
                    theme_name, size=24, fill=t["text_secondary"]),
            TY.label(98, 300, T.POSITIONING.upper(), theme_name, size=10.5,
                     tracking=2.2, opacity=0.42),
            G5.tick_rail(98, 334, 470, theme_name),
            TY.label(98, 360, f"NOAERTH.COM   ·   GITHUB {T.HANDLE}",
                     theme_name, size=11.5, opacity=0.5),
            anim,
            # the sculpture sits right of the type and never crosses it
            f'<g opacity="0.62" transform="translate(760,246)">'
            f'{G.stacked_cube(0, 0, 66, 3, theme_name, "indigo", gap=0.06)}</g>',
            f'<g opacity="0.85" transform="translate(1046,232)">'
            f'{G.faceted_aperture(0, 0, 132, theme_name, "mint", levels=3)}</g>',
            # Memphis punctuation: legible size, placed clear of the type
            G.memphis_cluster(700, 396, 150, 40, theme_name, "coral"),
        ]

    return (
        TY.document(
            W, H, f"{T.PRIMARY_NAME} — {T.STUDIO_NAME} {T.STUDIO_SUBTITLE}",
            f"Identity plate for {T.PRIMARY_NAME}, Noaerth systems lab. A stacked "
            f"isometric structure and a faceted aperture sit to the right of the "
            f"wordmark. Reads: build systems, prove them, compound what works. "
            f"Handle {T.HANDLE}, site noaerth.com.",
            theme_name, extra_defs=defs)
        + "".join(body) + TY.close()
    )


# ==========================================================================
# FLAGSHIP WINDOW
# ==========================================================================
def flagship_window(theme_name: str, slug: str, metric: str = "",
                    ci_state: str = "", compact: bool = False) -> str:
    """A window into the project's geometry rather than a restyled card.

    Each carries: name, a distinct motif, one-sentence purpose, verified tests,
    release, and CI state as a word. CI is never a colour alone.
    """
    t = T.PALETTES[theme_name]
    ident = P.identity(slug)
    accent_key = ident["accent"]
    accent = t[accent_key]
    material = ident["material"]
    W = 1200
    H = 250 if not compact else 210
    defs = _defs(theme_name, material, "optical_glass", "computational")

    motif = {
        "nested_frames": G5.nested_frames(0, 0, 120, 120, theme_name, 3,
                                          accent=accent)
                           + G.stepped_progression(60, 60, 22, 3, theme_name,
                                                   accent_key),
        "signal_path": G5.signal_path([(4, 96), (44, 30), (84, 74), (116, 18)],
                                      theme_name, accent=accent),
        "branching": G5.branching(60, 60, theme_name, 4, 48, accent=accent),
        "closed_topology": G.split_ring(60, 60, 56, theme_name, accent_key),
        "layered_evidence": G5.layered_evidence(4, 26, 112, 68, theme_name, 4,
                                                accent=accent),
        "generative_field": G5.generative_field(4, 22, 112, 76, theme_name, 20,
                                                accent=accent),
    }[ident["motif"]]

    ci_colour = t["mint_text"] if ci_state == "green" else (
        t["fail"] if ci_state in ("failure", "timed out") else t["text_faint"])

    body = [
        f'<rect x="0" y="0" width="{W}" height="{H}" '
        f'fill="{M.body_fill(theme_name, material)}" opacity="0.40"/>',
        _calm_grid(W, H, theme_name, 0.20),
        f'<rect x="0" y="0" width="2.5" height="{H}" '
        f'fill="{M.prism_fill(theme_name, material)}"/>',
        TY.label(58, 52, ident["label"].upper(), theme_name, size=11.5,
                 tracking=4),
        TY.text(58, 100, ident["headline"], theme_name, size=27, weight=650),
        TY.label(58, 128, ident["statement"], theme_name, size=11,
                 tracking=0.2, opacity=0.52, upper=False),
        f'<line x1="58" y1="152" x2="{W - 40}" y2="152" stroke="{t["edge"]}" '
        f'stroke-width="1"/>',
    ]
    # the proof strip: numbers as text, never as decoration
    chips = [c for c in (metric, ci_state) if c]
    x = 58
    for chip in chips:
        width = 12 + len(chip) * 7.6
        body.append(f'<rect x="{x}" y="168" width="{width:.0f}" height="26" '
                    f'rx="13" fill="{t["glass_hi"]}" fill-opacity="0.75" '
                    f'stroke="{t["edge"]}" stroke-width="1"/>')
        fill = ci_colour if chip == ci_state and ci_state else t["text_secondary"]
        body.append(TY.label(x + width / 2, 185, chip, theme_name, size=11,
                             tracking=0.6, fill=fill, opacity=0.95, anchor="middle"))
        x += width + 10
    body.append(TY.label(58, 218, f"{T.STUDIO_NAME} // {T.PRIMARY_NAME}",
                         theme_name, size=10, opacity=0.38))
    body.append(f'<g transform="translate({W - 190},{(H - 150) / 2 + 12})">{motif}</g>')
    body.append(TY.close())
    return (
        TY.document(W, H, f"{ident['label']} — {T.STUDIO_NAME}",
                    f"{ident['label']}: {ident['statement']} "
                    f"{('Verified: ' + metric) if metric else ''} "
                    f"{('CI: ' + ci_state) if ci_state else ''}",
                    theme_name, extra_defs=defs)
        + "".join(body)
    )


# ==========================================================================
# BUILD SIGNAL — scientific, not a metric card wall
# ==========================================================================
def build_signal(theme_name: str, signal: dict) -> str:
    """A measured observability surface.

    Values are printed, never implied by area. The bars encode each metric's
    share of the largest value *in its own class*, and classes are labelled, so
    a bar can never imply a false quantitative relationship between, say, test
    count and release count.
    """
    t = T.PALETTES[theme_name]
    uid = f"sig51-{theme_name}"
    W, H = 1200, 250
    metrics = signal.get("metrics", [])
    defs = _defs(theme_name, "computational", "deep_glass", "spectral_glass")

    if not metrics:
        return (TY.document(W, H, "Build signal", "No signal generated yet.",
                            theme_name, extra_defs=defs)
                + TY.label(40, 120, "BUILD SIGNAL NOT GENERATED", theme_name,
                           size=15, opacity=0.4) + TY.close())

    parts = [
        TY.document(
            W, H, f"{T.STUDIO_NAME} build signal",
            "Measured engineering telemetry. "
            + "; ".join(f"{m['label']} {m['display']}" for m in metrics)
            + ". Values are recorded, not estimated.",
            theme_name, extra_defs=defs),
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>',
        _calm_grid(W, H, theme_name, 0.22),
        TY.label(40, 40, "BUILD SIGNAL", theme_name, size=11, tracking=4,
                 opacity=0.55),
        TY.label(W - 40, 40, "measured · not estimated", theme_name, size=10,
                 tracking=1.4, opacity=0.4, anchor="end"),
    ]

    span = (W - 80) / len(metrics)
    baseline = 190
    for i, m in enumerate(metrics):
        cx = 40 + span * i + span / 2
        value = m["value"] or 0
        # Every metric gets the SAME measure. Bar length proportional to value
        # implied that 2,235 tests was some multiple of 6 green pipelines, which
        # is a comparison between different units and therefore meaningless. The
        # metric's own note states what is counted; the type states the number.
        parts.append(TY.text(cx, baseline - 46, m["display"], theme_name,
                             size=30, weight=650, anchor="middle"))
        # a uniform measured tick: presence, not proportion
        parts.append(
            f'<rect x="{cx - 17:.1f}" y="{baseline - 8}" width="34" height="6" '
            f'rx="3" fill="{t["mint"]}" opacity="0.85"/>')
        parts.append(
            f'<rect x="{cx - 17:.1f}" y="{baseline + 4}" width="34" height="2" '
            f'rx="1" fill="{t["edge"]}" opacity="0.9"/>')
        parts.append(TY.label(cx, baseline + 26, m["label"], theme_name, size=10,
                              tracking=1.6, opacity=0.66, anchor="middle"))
        parts.append(TY.label(cx, baseline + 42, m.get("note", "measured"),
                              theme_name, size=8.5, tracking=0.6, opacity=0.32,
                              anchor="middle", upper=False))
    parts.append(f'<line x1="40" y1="{baseline}" x2="{W - 40}" y2="{baseline}" '
                 f'stroke="{t["edge"]}" stroke-width="1"/>')
    parts.append(TY.close())
    return "".join(parts)


# ==========================================================================
# SYSTEM MAP — isometric architecture, evidence intact
# ==========================================================================
LAYERS = [
    ("CONTROL ARCHITECTURE", "violet", "decides what runs, and who approved it",
     [("noaerth-portfolio-os", "Portfolio OS", "queue · locks · reviewer separation"),
      ("grokbot-office", "GrokBot Office", "workforce configuration")]),
    ("EXECUTION MACHINE", "mint", "turns an objective into a verified outcome",
     [("agentos", "AgentOS", "capability discovery · adapter execution")]),
    ("ECONOMY / ROUTING", "indigo", "makes execution cheap and repeatable",
     [("grokmax", "GrokMax", "route · five-layer cache · ledger"),
      ("grokinstall", "GrokInstall", "smallest useful capability")]),
    ("GUARDRAILS", "fail", "stops degenerate work before it costs anything",
     [("opencode-watchdog", "OpenCode Watchdog", "deterministic repetition circuit")]),
    ("SURFACES", "text_secondary", "where the work becomes usable by a person",
     [("gh0st", "gh0st", "local-first encrypted client"),
      ("grokbot-society", "GrokBot Society", "persistent actors · governed spend"),
      ("seai-mind", "SEAI Mind", "self-evolving memory kernel")]),
]

# Evidenced relationships. Every key must resolve in system-map-evidence.json;
# the safety suite fails if the map and the evidence disagree either way.
RELATIONSHIPS = {
    "grokbot-office": "sits above AgentOS",
    "grokmax": "adapts to OpenCode",
    "opencode-watchdog": "observes an OpenCode session",
}


def system_map(theme_name: str, compact: bool = False) -> str:
    t = T.PALETTES[theme_name]
    if compact:
        W, row_h, band = 440, 78, 36
        name_size, note_size = 19, 12
        pad = 18
    else:
        W, row_h, band = 1200, 78, 44
        name_size, note_size = 20, 11
        pad = 64

    panel_w = W - pad * 2
    y = 70
    layout = []
    for layer, key, blurb, items in LAYERS:
        layout.append(("band", layer, key, blurb, y))
        y += band
        for slug, title, note in items:
            layout.append(("panel", slug, title, note, y))
            y += row_h + (8 if compact else 10)
        y += 14 if compact else 24
    H = y + 34
    defs = _defs(theme_name, "optical_glass", "deep_glass", "obsidian_compute")

    parts = [
        TY.document(
            W, H, f"{T.STUDIO_NAME} operating stack",
            "Five layers over the published systems: control architecture, "
            "execution machine, economy and routing, guardrails, and surfaces. "
            "A relationship is named only where one repository's source or "
            "documentation names the other; systems with no documented "
            "relationship are drawn without one.",
            theme_name, extra_defs=defs),
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>',
        _calm_grid(W, H, theme_name, 0.24 if compact else 0.20),
    ]

    for item in layout:
        if item[0] == "band":
            _, layer, key, blurb, by = item
            parts.append(TY.label(pad, by + 12, layer, theme_name,
                                  size=11 if compact else 11.5, tracking=3.4,
                                  fill=T.readable(theme_name, key), opacity=0.9))
            if not compact:
                parts.append(TY.label(pad + 190, by + 12, blurb, theme_name,
                                      size=10.5, tracking=0.5, opacity=0.32,
                                      upper=False))
            parts.append(f'<line x1="{pad}" y1="{by + 22}" x2="{W - pad}" '
                         f'y2="{by + 22}" stroke="{t["edge"]}" stroke-width="1" '
                         f'opacity="0.6"/>')
            continue

        _, slug, title, note, py = item
        material = P.material_for(slug)
        relation = RELATIONSHIPS.get(slug)
        parts.append(
            f'<rect x="{pad}" y="{py}" width="{panel_w}" height="{row_h}" '
            f'rx="{T.RADIUS["card"]}" fill="{M.body_fill(theme_name, material)}" '
            f'opacity="0.80" stroke="{t["edge"]}" stroke-width="1"/>')
        parts.append(
            f'<rect x="{pad}" y="{py}" width="2.5" height="{row_h}" '
            f'fill="{M.prism_fill(theme_name, material)}" opacity="0.85"/>')
        # isometric step: the plate reads as a block, not a table row
        step = G.cube(12, 0, 34, theme_name, top=t["mint"],
                      left=t["indigo"], right=t["violet"],
                      top_opacity=0.55, side_opacity=0.34)
        parts.append(f'<g opacity="0.55" transform="translate('
                     f'{pad + 20},{py + row_h / 2 - 12})">{step}</g>')
        parts.append(TY.text(pad + 68, py + (34 if compact else 36), title,
                             theme_name, size=name_size, weight=620))
        caption = f"{note}  →  {relation}" if relation else note
        parts.append(TY.label(pad + 68, py + (58 if compact else 60), caption,
                              theme_name, size=note_size, tracking=0.4,
                              opacity=0.62 if relation else 0.5))
        size = 44 if compact else 52
        parts.append(
            f'<g opacity="0.9" transform="translate({W - pad - size - 22},'
            f'{py + (row_h - size) / 2:.1f})">'
            f'{P.glyph(slug, theme_name, size / 2, size / 2, size)}</g>')

    parts.append(f'<line x1="{pad}" y1="{H - 24}" x2="{W - pad}" y2="{H - 24}" '
                 f'stroke="{t["edge"]}" stroke-width="1"/>')
    parts.append(TY.label(pad, H - 10,
                          "named only where source or docs cite the other system",
                          theme_name, size=9.5, opacity=0.4))
    parts.append(TY.close())
    return "".join(parts)


# ==========================================================================
# CONSTELLATION — semantic grouping, explicitly not dependency
# ==========================================================================
CONSTELLATION = [
    ("GOVERN", "violet", ["noaerth-portfolio-os", "grokbot-office"]),
    ("EXECUTE", "mint", ["agentos"]),
    ("ECONOMISE", "indigo", ["grokmax", "grokinstall"]),
    ("PROTECT", "fail", ["opencode-watchdog", "gh0st"]),
    ("EMERGENT", "text_secondary", ["grokbot-society", "seai-mind"]),
]


def constellation(theme_name: str = "dark") -> str:
    """Semantic ecosystem grouping.

    Deliberately NOT the operating stack. These are categories, not runtime
    dependencies, and the plate says so in its own caption because conflating
    the two is the specific error this system exists to avoid.
    """
    t = T.PALETTES[theme_name]
    W, H = 1200, 560
    defs = _defs(theme_name, "computational", "deep_glass")
    parts = [
        TY.document(
            W, H, f"{T.STUDIO_NAME} constellation",
            "Semantic grouping of the published systems into five families. "
            "These are categories of work, not runtime dependencies; the "
            "operating stack is the plate that shows documented relationships.",
            theme_name, extra_defs=defs),
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>',
    ]
    lattice = G.isometric_lattice(120, 90, 9, 5, 34, theme_name, "mint",
                                  occupancy=0.42)
    parts.append(f'<g opacity="0.9">{lattice}</g>')
    cols = 5
    col_w = (W - 160) / cols
    for i, (family, key, slugs) in enumerate(CONSTELLATION):
        cx = 80 + col_w * i + col_w / 2
        accent = t[key]
        parts.append(f'<circle cx="{cx:.1f}" cy="330" r="74" fill="none" '
                     f'stroke="{accent}" stroke-width="1" stroke-opacity="0.45"/>')
        parts.append(f'<circle cx="{cx:.1f}" cy="330" r="86" fill="none" '
                     f'stroke="{accent}" stroke-width="1" stroke-opacity="0.18"/>')
        for j, slug in enumerate(slugs):
            a = -math.pi / 2 + 2 * math.pi * j / max(len(slugs), 1)
            nx = cx + math.cos(a) * 40
            ny = 330 + math.sin(a) * 40
            parts.append(G5.node(nx, ny, 5, theme_name, active=True, accent=accent))
        parts.append(TY.label(cx, 448, family, theme_name, size=11, tracking=3.2,
                              fill=T.readable(theme_name, key), anchor="middle"))
    parts.append(TY.label(80, 512,
                          "categories of work — not runtime dependencies",
                          theme_name, size=11, opacity=0.5))
    parts.append(TY.label(W - 80, 512,
                          "documented relationships live in the operating stack",
                          theme_name, size=11, opacity=0.4, anchor="end"))
    parts.append(TY.close())
    return "".join(parts)



# ==========================================================================
# TERMINAL — the legacy artifact keeps its own sub-language
# ==========================================================================
def terminal(theme_name: str = "dark", motion: bool = False) -> str:
    """CRT shell.

    Not the V5.1 grammar. This is the one surface that stays retro on purpose:
    it exists because the account once had nothing public, and dressing it in the
    house style would erase why it is there. Scanlines and phosphor, nothing
    faceted.
    """
    t = T.PALETTES[theme_name]
    uid = f"term51-{theme_name}"
    W, H = 660, 224
    defs = _defs(theme_name, "obsidian_compute")

    caret = ""
    if motion:
        caret = ('<animate attributeName="opacity" values="1;1;0;0;1" '
                 'keyTimes="0;0.4;0.5;0.9;1" dur="1.6s" '
                 'repeatCount="indefinite"/>')

    lines = []
    body = [
        TY.document(
            W, H, "why are you here?",
            "A CRT shell fragment. Running whoami prints DUNG30N5. Asking why "
            "are you here prints a cursor and nothing else.",
            theme_name, extra_defs=defs),
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" '
        f'fill="{t["canvas"]}" stroke="{t["edge"]}" stroke-width="1"/>',
        f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="10" '
        f'fill="none" stroke="{t["edge"]}" stroke-width="1" opacity="0.5"/>',
        f'<circle cx="30" cy="30" r="3.5" fill="none" stroke="{t["text_faint"]}" stroke-width="1"/>',
        f'<circle cx="46" cy="30" r="3.5" fill="none" stroke="{t["text_faint"]}" stroke-width="1" opacity="0.6"/>',
        f'<circle cx="62" cy="30" r="3.5" fill="none" stroke="{t["text_faint"]}" stroke-width="1" opacity="0.35"/>',
        TY.label(W - 30, 34, f"{T.PRIMARY_NAME}://shell", theme_name, size=11,
                 tracking=1.6, opacity=0.45, anchor="end"),
        f'<line x1="14" y1="46" x2="{W - 14}" y2="46" stroke="{t["edge"]}" '
        f'stroke-width="1" opacity="0.45"/>',
    ]
    y = 78
    for cmd, out in (("whoami", "DUNG30N5"), ("why are you here?", "")):
        body.append(TY.text(32, y, ">", theme_name, size=14,
                            fill=t["mint_text"], family=T.FONT_MONO))
        body.append(TY.text(54, y, cmd, theme_name, size=14, fill=t["text_primary"],
                            family=T.FONT_MONO))
        y += 26
        if out:
            body.append(TY.text(54, y, out, theme_name, size=14,
                                fill=t["text_secondary"], family=T.FONT_MONO))
            y += 30
    body.append(TY.text(32, y, ">", theme_name, size=14, fill=t["mint_text"],
                        family=T.FONT_MONO))
    body.append(f'<text x="54" y="{y}" font-family="{T.FONT_MONO}" '
                f'font-size="14" fill="{t["mint_text"]}">{caret}█</text>')
    # scanlines: the one texture that survives as retro without being noise
    for sy in range(56, H - 14, 4):
        lines.append(f'<line x1="16" y1="{sy}" x2="{W - 16}" y2="{sy}" '
                     f'stroke="{t["grid"]}" stroke-width="1" '
                     f'opacity="0.30"/>')
    body.append(f'<g>{"".join(lines)}</g>')
    body.append(TY.close())
    return "".join(body)


# ==========================================================================
# SOCIAL PREVIEW
# ==========================================================================
def social_preview(theme_name: str = "dark", subject: str = "",
                   subtitle: str = "") -> str:
    """1280x640 share card.

    Carries only what must survive an unpredictable crop: the name and one line.
    """
    t = T.PALETTES[theme_name]
    W, H = 1280, 640
    defs = _defs(theme_name, "optical_glass", "computational")
    subject = subject or T.PRIMARY_NAME
    body = [
        TY.document(W, H, f"{subject} — {T.STUDIO_NAME}",
                    subtitle or f"{T.PRIMARY_NAME}. {T.STUDIO_NAME}. Build systems.",
                    theme_name, extra_defs=defs),
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{t["canvas"]}"/>',
        _calm_grid(W, H, theme_name, 0.24),
        f'<rect x="110" y="212" width="3" height="188" '
        f'fill="{M.prism_fill(theme_name, "optical_glass")}"/>',
        TY.label(146, 240, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}",
                 theme_name, size=15, tracking=5, opacity=0.85),
        TY.text(146, 340, subject, theme_name, size=104, weight=700, tracking=10),
        TY.text(146, 396, subtitle or "BUILD SYSTEMS. PROVE THEM.", theme_name,
                size=30, fill=t["text_secondary"], tracking=2),
        TY.label(146, 448, f"NOAERTH.COM   ·   GITHUB {T.HANDLE}", theme_name,
                 size=13, tracking=2.6, opacity=0.55),
    ]
    field = G.isometric_lattice(-260, -190, 8, 5, 40, theme_name, "indigo", 0.40)
    aperture = G.faceted_aperture(0, 0, 128, theme_name, "mint", levels=2)
    body.append(f'<g opacity="0.6" transform="translate(980,300)">{field}</g>')
    body.append(f'<g opacity="0.9" transform="translate(1010,320)">{aperture}</g>')
    body.append(TY.close())
    return "".join(body)


# ==========================================================================
# DIVIDER
# ==========================================================================
def divider(theme_name: str = "dark", kind: str = "signal") -> str:
    """A section divider family, used sparingly.

    If a README reads better with plain whitespace, use whitespace. These exist
    for the cases where a rule earns its place.
    """
    t = T.PALETTES[theme_name]
    W, H = 1200, 48
    defs = _defs(theme_name, "optical_glass")
    mid = W / 2
    if kind == "signal":
        line = (f'<line x1="40" y1="24" x2="{mid - 24}" y2="24" '
                f'stroke="{t["edge"]}" stroke-width="1"/>'
                f'<line x1="{mid + 24}" y1="24" x2="{W - 40}" y2="24" '
                f'stroke="{t["edge"]}" stroke-width="1"/>'
                f'<path d="M{mid - 20} 24 L{mid - 8} 18 L{mid - 8} 30 Z" '
                f'fill="{t["mint"]}" opacity="0.8"/>'
                f'<circle cx="{mid}" cy="24" r="4" fill="{t["mint"]}"/>')
    elif kind == "faceted":
        left = "".join(
            G.diamond(40 + i * 22, 24, 7, 11, theme_name, t["indigo"],
                      0.5 - i * 0.05) for i in range(6))
        right = "".join(
            G.diamond(W - 40 - i * 22, 24, 7, 11, theme_name, t["violet"],
                      0.5 - i * 0.05) for i in range(6))
        line = left + right
    elif kind == "frames":
        line = "".join(
            f'<rect x="{40 + i * 16}" y="{24 - (6 - i)}" width="12" '
            f'height="{(6 - i) * 2}" fill="none" stroke="{t["edge"]}" '
            f'stroke-width="1" stroke-opacity="{0.8 - i * 0.1:.2f}"/>'
            for i in range(6))
    else:  # tiles
        line = "".join(
            G.arch_tile(40 + i * 20, 14, 14, 20, theme_name,
                        t["edge_link"], 0.28) for i in range(12))
    return (TY.document(W, H, "Section divider", "A technical rule between sections.",
                        theme_name, extra_defs=defs)
            + line + TY.close())