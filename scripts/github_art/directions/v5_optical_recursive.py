"""Direction A, amended - the V5 system.

Council outcome for Part 1:

    A OPTICAL TOPOLOGY        selected as the base
    B DEEP COMPUTATIONAL GLASS rejected as a base; one idea grafted
    C RECURSIVE SYSTEM MATERIAL rejected as a base; one idea grafted

Why A won. Crispness is the first requirement in the standard and A was the
only direction whose hairline rules and tick rails stayed sharp. It is also the
cheapest, which matters when the payload budget is a real constraint rather than
an aspiration, and its primitives are semantic: nested frames, signal paths,
branching, closed topology. The other two directions leaned on atmosphere.

Two defects in A were real and are fixed here rather than tolerated:

  1. The hero motif rendered as an empty rectangle. It was semantically
     correct for CONTROL and visually inert as an identity. It is now a
     recursive module set inside an optical frame, which is C's strongest idea
     used to repair A's weakest surface. Three of four quadrants recurse, so
     the pattern is directional rather than merely busy.
  2. Depth was the one thing A lacked. It now takes B's strata, but only for
     the CONTROL layer, where a surface that governs should read as containing
     space. B's concentric-circle motif is not used anywhere: it is the most
     generic shape available and identity is the one thing this system cannot
     afford to be generic about.

Rejected on the record:

    B - drifts toward the glassmorphism the standard explicitly refuses, and
        concentric circles would have made every flagship interchangeable.
    C - the best identity idea of the three and the heaviest by 3.2x. Its
        module is kept; its habit of filling every surface with recursion is not.
"""
from __future__ import annotations

from .. import geometry as G
from .. import materials as M
from .. import project_identity as P
from .. import tokens as T
from .. import typography as TY

NAME = "OPTICAL TOPOLOGY, RECURSIVE"
SLUG = "v5-optical-recursive"
DIRECTION_A = "a-optical-topology"
GRAFTED_FROM_C = "recursive module motif"
GRAFTED_FROM_B = "strata, CONTROL layer only"

INTENSITY = {
    "general_content": 0.32,
    "cards_diagrams": 0.44,
    "profile_hero": 0.74,
    "system_graphic": 0.62,
    "easter_egg": 0.56,
}

_MATERIALS = ("optical_glass", "spectral_glass", "deep_glass",
              "obsidian_compute", "liquid_crystal", "computational_material",
              "luminous_ceramic")


# Evidenced relationships. Each key must resolve to an entry in
# system-map-evidence.json, and the validator fails generation if the two
# disagree in either direction. A map that draws no relationships at all would
# make the evidence file decorative, and an invented edge would be undetectable.
RELATIONSHIPS = {
    "grokbot-office": "sits above AgentOS",
    "grokmax": "adapts to OpenCode",
    "opencode-watchdog": "observes an OpenCode session",
}


def _defs(theme: str, *materials: str) -> str:
    return "".join(M.definitions(theme, m) for m in materials)


def module(x, y, size, theme_name: str, depth: int = 4,
           accent_key: str = "mint") -> str:
    """The recursive unit: one square whose quadrants repeat it smaller.

    Fractal organisation, not fractal decoration. Each level is a quarter the
    size of the last and fainter, so the eye reads structure rather than
    texture, and three of four quadrants recurse so the field has a direction.
    """
    t = T.PALETTES[theme_name]
    accent = t[accent_key]
    if depth <= 0 or size < 12:
        return ""
    out = [f'<rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" '
           f'fill="none" stroke="{accent}" stroke-width="1" '
           f'opacity="{0.14 + depth * 0.13:.2f}"/>']
    for i in range(1, 4):
        tx = x + size * i / 4
        out.append(f'<line x1="{tx:.2f}" y1="{y:.2f}" x2="{tx:.2f}" '
                   f'y2="{y + size * 0.10:.2f}" stroke="{t["edge"]}" '
                   f'stroke-width="1" opacity="0.45"/>')
    half = size / 2
    for qx, qy in ((0, 0), (1, 0), (0, 1)):
        out.append(module(x + qx * half, y + qy * half, half, theme_name,
                          depth - 1, accent_key))
    return "".join(out)


def _hero_field(x, y, size, theme_name: str) -> str:
    """The module at three scales: macro structure echoed in micro detail."""
    return (
        f'<g opacity="0.85">{module(x, y, size, theme_name, 4, "mint")}</g>'
        f'<g opacity="0.42">{module(x + size * 0.56, y + size * 0.52, size * 0.34, theme_name, 3, "indigo")}</g>'
        f'<g opacity="0.30">{module(x + size * 0.18, y + size * 0.62, size * 0.24, theme_name, 3, "violet")}</g>'
    )


def _strata(x, y, w, h, theme_name: str, layers: int = 4) -> str:
    """B's depth, used only where a surface governs and should contain space."""
    t = T.PALETTES[theme_name]
    out = []
    for i in range(layers):
        depth = i / max(layers - 1, 1)
        inset_x = x + depth * w * 0.14
        inset_y = y + depth * h * 0.18
        out.append(
            f'<rect x="{inset_x:.2f}" y="{inset_y:.2f}" '
            f'width="{w - depth * w * 0.28:.2f}" height="{h - depth * h * 0.26:.2f}" '
            f'rx="{T.RADIUS["panel"] - i}" fill="{t["glass"]}" '
            f'fill-opacity="{0.55 - depth * 0.34:.2f}" stroke="{t["edge"]}" '
            f'stroke-width="1" stroke-opacity="{0.8 - depth * 0.45:.2f}"/>'
        )
    return "".join(out)


# --------------------------------------------------------------------------
# hero family
# --------------------------------------------------------------------------
def hero(theme_name: str = "dark", compact: bool = False, motion: bool = False) -> str:
    t = T.PALETTES[theme_name]
    # One treatment for the whole line. Casing only the first fragment produced
    # "Build Systems. PROVE THEM. COMPOUND WHAT WORKS.", which reads as a typo.
    tagline = tuple(f.rstrip(".")[0].upper() + f.rstrip(".")[1:].lower()
                    for f in T.PRIMARY_TAGLINE)
    W, H = (460, 430) if compact else (1200, 420)
    defs = _defs(theme_name, "optical_glass", "spectral_glass", "deep_glass")

    anim = ""
    if motion:
        L = T.MOTION["loop_seconds"]
        # Two moving elements only. A reader who never sees the motion loses
        # nothing, because both are duplicated as static twins in the README.
        anim = (
            f'<g><animate attributeName="opacity" '
            f'values="{T.MOTION["breath_low"]};{T.MOTION["breath_high"]};'
            f'{T.MOTION["breath_low"]}" dur="{L}s" repeatCount="indefinite"/>'
            f'<rect x="780" y="70" width="120" height="270" '
            f'fill="url(#m-optical_glass-{theme_name}-core)" '
            f'opacity="{T.MOTION["sweep_opacity"]}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; 340 0" dur="{T.MOTION["travel_seconds"]}s" '
            f'repeatCount="indefinite"/></rect></g>'
        )

    if compact:
        body = [
            f'<g opacity="0.34">{G.micro_grid(W, H, theme_name, step=32)}</g>',
            f'<rect x="44" y="92" width="2.5" height="120" '
            f'fill="{M.prism_fill(theme_name, "optical_glass")}"/>',
            TY.label(62, 112, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}", theme_name,
                     size=9.5, tracking=3.0),
            TY.text(62, 162, T.PRIMARY_NAME, theme_name, size=52, weight=700,
                    tracking=3),
            TY.text(62, 200, tagline[0], theme_name, size=15,
                    fill=t["text_secondary"]),
            TY.text(62, 222, tagline[1], theme_name, size=15, fill=t["text_secondary"]),
            TY.text(62, 244, tagline[2], theme_name, size=15,
                    fill=t["text_secondary"]),
            f'<g opacity="0.8">{module(266, 286, 132, theme_name, 4, "mint")}</g>',
            G.tick_rail(62, 274, 300, theme_name),
            TY.label(62, 306, "NOAERTH.COM", theme_name, size=9.5, opacity=0.55),
            TY.label(62, 326, f"GITHUB {T.HANDLE}", theme_name, size=9.5, opacity=0.55),
            TY.label(62, 360, T.POSITIONING.upper(), theme_name, size=8.5,
                     tracking=1.6, opacity=0.34),
            anim,
        ]
    else:
        body = [
            f'<g opacity="0.30">{G.micro_grid(W, H, theme_name, step=40)}</g>',
            f'<rect x="72" y="106" width="2.5" height="146" '
            f'fill="{M.prism_fill(theme_name, "optical_glass")}"/>',
            TY.label(98, 132, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}", theme_name,
                     size=12.5, tracking=4.4),
            TY.text(98, 224, T.PRIMARY_NAME, theme_name, size=88, weight=700,
                    tracking=8),
            TY.text(98, 264, f"{tagline[0]}. {tagline[1]}. {tagline[2]}.",
                    theme_name, size=24, fill=t["text_secondary"]),
            TY.label(98, 296, T.POSITIONING.upper(), theme_name, size=10.5,
                     tracking=2.2, opacity=0.42),
            G.tick_rail(98, 330, 470, theme_name),
            TY.label(98, 356, f"NOAERTH.COM   ·   GITHUB {T.HANDLE}", theme_name,
                     size=11.5, opacity=0.5),
            anim,
            # Strata sit behind as one faint containment frame. Previously they
            # were drawn over the module and the two interfered.
            _strata(672, 54, 428, 320, theme_name, 2),
            f'<g opacity="0.92">{_hero_field(716, 104, 300, theme_name)}</g>',
        ]

    return (
        TY.document(
            W, H, f"{T.PRIMARY_NAME} — {T.STUDIO_NAME} {T.STUDIO_SUBTITLE}",
            f"Identity plate for {T.PRIMARY_NAME}, Noaerth systems lab. A recursive "
            f"module repeats at three scales behind the wordmark. Reads: build "
            f"systems, prove them, compound what works. Handle {T.HANDLE}, "
            f"site noaerth.com.",
            theme_name, extra_defs=defs)
        + "".join(body) + TY.close()
    )


# --------------------------------------------------------------------------
# flagship hero
# --------------------------------------------------------------------------
def flagship_hero(theme_name: str = "dark", slug: str = "agentos") -> str:
    t = T.PALETTES[theme_name]
    ident = P.identity(slug)
    accent = t[ident["accent"]]
    W, H = 1200, 300
    material = ident["material"]
    defs = _defs(theme_name, *sorted({material, "optical_glass"}))

    body = [
        f'<rect x="0" y="0" width="{W}" height="{H}" '
        f'fill="{M.body_fill(theme_name, material)}" opacity="0.42"/>',
        f'<g opacity="0.34">{G.micro_grid(W, H, theme_name, step=40)}</g>',
        f'<rect x="64" y="82" width="2.5" height="92" '
        f'fill="{M.prism_fill(theme_name, material)}"/>',
        TY.label(88, 106, ident["label"].upper(), theme_name, size=12, tracking=4),
        TY.text(88, 156, ident["headline"], theme_name, size=30, weight=650),
        TY.label(88, 186, T.POSITIONING, theme_name, size=10.5, tracking=1.4,
                 opacity=0.4, upper=False),
        G.tick_rail(88, 214, 520, theme_name),
        TY.label(88, 244, f"{T.STUDIO_NAME} // {T.PRIMARY_NAME}", theme_name,
                 size=10.5, opacity=0.45),
        f'<g transform="translate(940,90)">{P.glyph(slug, theme_name, 110, 60, 120)}</g>',
        # state pips: the module reduced to its smallest expression
        "".join(
            f'<rect x="{1010 + i * 24}" y="236" width="13" height="5" rx="1" '
            f'fill="{accent if i < 3 else t["edge"]}" '
            f'opacity="{0.92 if i < 3 else 0.55}"/>' for i in range(5)),
    ]
    return (
        TY.document(W, H, f"{ident['label']} — {T.STUDIO_NAME}",
                    f"{ident['label']}: {ident['statement']}",
                    theme_name, extra_defs=defs)
        + "".join(body) + TY.close()
    )


# --------------------------------------------------------------------------
# system map
# --------------------------------------------------------------------------
LAYERS = [
    # The portfolio control plane is a private repository. It orchestrated these
    # systems and was named in this layer until it was made private; drawing or
    # naming it here would disclose a private repository in a public graphic.
    ("CONTROL", "violet", "decides what runs, and who approved it",
     [("grokbot-office", "GrokBot Office", "workforce configuration")]),
    ("EXECUTE", "mint", "turns an objective into a verified outcome",
     [("agentos", "AgentOS", "capability discovery · adapter execution")]),
    ("ECONOMISE", "indigo", "makes execution cheap and repeatable",
     [("grokmax", "GrokMax", "route · five-layer cache · ledger"),
      ("grokinstall", "GrokInstall", "smallest useful capability")]),
    ("GUARD", "fail", "stops degenerate work before it costs anything",
     [("opencode-watchdog", "OpenCode Watchdog", "deterministic repetition circuit")]),
    ("SURFACE", "text_secondary", "where the work becomes usable by a person",
     [("gh0st", "gh0st", "local-first encrypted client"),
      ("grokbot-society", "GrokBot Society", "persistent actors · governed spend"),
      ("seai-mind", "SEAI Mind", "self-evolving memory kernel")]),
]


def system_map(theme_name: str = "dark", compact: bool = False) -> str:
    t = T.PALETTES[theme_name]
    if compact:
        W, row_h, band = 440, 74, 34
        name_size, note_size = 19, 12
        pad, gutter = 18, 0
    else:
        W, row_h, band = 1200, 74, 42
        name_size, note_size = 20, 11
        pad, gutter = 64, 0
    panel_w = W - pad * 2

    y = 66
    layout = []
    for layer, key, blurb, items in LAYERS:
        layout.append(("band", layer, key, blurb, y))
        y += band
        for slug, title, note in items:
            layout.append(("panel", slug, title, note, y))
            y += row_h + (8 if compact else 10)
        y += 14 if compact else 22
    H = y + 30
    defs = _defs(theme_name, "optical_glass", "deep_glass", "obsidian_compute")

    parts = [
        TY.document(
            W, H, f"{T.STUDIO_NAME} operating stack",
            "Five layers over the published systems: control, execution, economy, "
            "guardrails, and surfaces. A relationship is named only where one "
            "repository's source or documentation names the other; systems with no "
            "documented relationship are drawn without one.",
            theme_name, extra_defs=defs),
        f'<g opacity="{0.34 if compact else 0.26}">'
        f'{G.micro_grid(W, H, theme_name, step=32 if compact else 40)}</g>',
    ]

    for item in layout:
        if item[0] == "band":
            _, layer, key, blurb, by = item
            parts.append(TY.label(pad, by + 12, layer, theme_name,
                                  size=11 if compact else 11.5, tracking=3.4,
                                  fill=T.readable(theme_name, key), opacity=0.9))
            if not compact:
                parts.append(TY.label(pad + 120, by + 12, blurb, theme_name,
                                      size=10.5, tracking=0.5, opacity=0.34,
                                      upper=False))
            parts.append(f'<line x1="{pad}" y1="{by + 22}" x2="{W - pad}" '
                         f'y2="{by + 22}" stroke="{t["edge"]}" stroke-width="1" '
                         f'opacity="0.6"/>')
            continue

        _, slug, title, note, py = item
        if not P.has_identity(slug):
            # A public repository without a designed mark still belongs in the
            # map. It is drawn with the neutral material rather than skipped, so
            # the graphic never implies that undesigned systems are absent, and
            # the generator never crashes on an unmapped slug.
            material = P.DEFAULT_MATERIAL
        else:
            material = P.material_for(slug)
        relation = RELATIONSHIPS.get(slug)
        parts.append(
            f'<rect x="{pad}" y="{py}" width="{panel_w}" height="{row_h}" '
            f'rx="{T.RADIUS["card"]}" '
            f'fill="{M.body_fill(theme_name, material)}" opacity="0.85" '
            f'stroke="{t["edge"]}" stroke-width="1"/>')
        parts.append(
            f'<rect x="{pad}" y="{py}" width="2.5" height="{row_h}" '
            f'fill="{M.prism_fill(theme_name, material)}" opacity="0.85"/>')
        parts.append(TY.text(pad + 22, py + (32 if compact else 34), title,
                             theme_name, size=name_size, weight=620))
        parts.append(TY.label(pad + 22, py + (54 if compact else 58),
                              f"{note}  \u2192  {relation}" if relation else note,
                              theme_name, size=note_size, tracking=0.5,
                              opacity=0.62 if relation else 0.5))
        size = 52 if compact else 60
        parts.append(
            f'<g opacity="0.9" transform="translate({W - pad - size - 18},'
            f'{py + (row_h - size) / 2:.1f})">'
            f'{P.glyph(slug, theme_name, size / 2, size / 2, size)}</g>')

    parts.append(f'<line x1="{pad}" y1="{H - 20}" x2="{W - pad}" y2="{H - 20}" '
                 f'stroke="{t["edge"]}" stroke-width="1"/>')
    parts.append(TY.label(pad, H - 7,
                          "named only where source or docs cite the other system",
                          theme_name, size=9.5, opacity=0.4))
    parts.append(TY.close())
    return "".join(parts)
