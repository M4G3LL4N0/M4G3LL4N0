"""Direction A - OPTICAL TOPOLOGY.

Premise: the profile is an optical instrument. Structure is carried by precise
line work, nested frames, and refracted edges; interior surfaces stay almost
empty so the geometry reads clearly. Depth comes from occlusion and edge light,
never from blur.

Character: exact, cool, measured. Closest to a scientific instrument or an
optical bench. Highest information density per pixel; lowest material richness.
"""
from __future__ import annotations

from .. import geometry as G
from .. import materials as M
from .. import tokens as T
from .. import typography as TY

NAME = "OPTICAL TOPOLOGY"
SLUG = "a-optical-topology"
INTENSITY = {
    "profile_hero": 0.70,
    "flagship_hero": 0.50,
    "system_map": 0.58,
    "easter_egg": 0.52,
}


def _defs(theme: str) -> str:
    return (M.definitions(theme, "optical_glass")
            + M.definitions(theme, "spectral_glass")
            + M.definitions(theme, "deep_glass"))


def hero(theme_name: str = "dark", compact: bool = False) -> str:
    t = T.PALETTES[theme_name]
    W, H = (460, 400) if compact else (1200, 420)
    dense = T.TYPE_SCALE if not compact else {
        "micro": 9, "annotation": 9, "caption": 11, "body": 12, "lead": 15,
        "subhead": 19, "headline": 26, "display": 34, "wordmark": 54, "monolith": 70}

    defs = _defs(theme_name)
    bg = (f'<g opacity="0.42">{G.micro_grid(W, H, theme_name, step=32)}</g>')

    if compact:
        body = [
            TY.text(44, 172, T.PRIMARY_NAME, theme_name, size=dense["wordmark"],
                    weight=700, tracking=3),
            TY.text(44, 206, "Build systems.", theme_name, size=dense["lead"],
                    fill=t["text_secondary"]),
            TY.text(44, 230, "Prove them.", theme_name, size=dense["lead"],
                    fill=t["text_secondary"]),
            TY.text(44, 254, "Compound what works.", theme_name, size=dense["lead"],
                    fill=t["text_secondary"]),
            f'<rect x="44" y="86" width="2.5" height="74" fill="{M.prism_fill(theme_name, "optical_glass")}"/>',
            G.nested_frames(250, 96, 150, 150, theme_name, depth=3, accent=t["mint"]),
        ]
        foot = [
            TY.label(44, 300, "NOAERTH // SYSTEMS LAB", theme_name, size=9.5),
            TY.label(44, 322, T.OWNER, theme_name, size=9.5, opacity=0.4),
        ]
    else:
        body = [
            f'<rect x="72" y="112" width="2.5" height="132" fill="{M.prism_fill(theme_name, "optical_glass")}"/>',
            TY.label(96, 136, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}", theme_name,
                     size=13, tracking=4.4),
            TY.text(96, 228, T.PRIMARY_NAME, theme_name, size=dense["wordmark"],
                    weight=700, tracking=8),
            TY.text(96, 268, "Build systems. Prove them. Compound what works.",
                    theme_name, size=24, fill=t["text_secondary"]),
            G.nested_frames(742, 92, 340, 236, theme_name, depth=4, accent=t["mint"]),
            G.tick_rail(96, 330, 470, theme_name),
            TY.label(96, 356, f"NOAERTH.COM   ·   GITHUB {T.HANDLE}", theme_name,
                     size=11.5, opacity=0.5),
        ]
        foot = []

    return (
        TY.document(
            W, H,
            f"{T.PRIMARY_NAME} — {T.STUDIO_NAME} {T.STUDIO_SUBTITLE}",
            f"Identity plate for {T.PRIMARY_NAME}. Nested optical frames carry the "
            f"studio mark. Reads: build systems, prove them, compound what works. "
            f"Handle {T.HANDLE}, site noaerth.com.",
            theme_name, extra_defs=defs)
        + bg + "".join(body) + "".join(foot) + TY.close()
    )


def flagship_hero(theme_name: str = "dark", slug: str = "agentos") -> str:
    from .. import project_identity as P
    t = T.PALETTES[theme_name]
    ident = P.identity(slug)
    accent = t[ident["accent"]]
    W, H = 1200, 300
    material = ident["material"]
    defs = _defs(theme_name) + M.definitions(theme_name, material)

    motif = {
        "nested_frames": G.nested_frames(980, 70, 160, 160, theme_name, 4, accent),
        "signal_path": G.signal_path([(980, 200), (1030, 120), (1080, 175), (1130, 96)],
                                     theme_name, accent=accent),
        "branching": G.branching(1055, 150, theme_name, 4, 72, accent=accent),
        "closed_topology": G.closed_topology(1055, 150, 76, theme_name, accent=accent),
        "layered_evidence": G.layered_evidence(980, 96, 150, 116, theme_name, 4, accent),
        "generative_field": G.generative_field(980, 96, 150, 116, theme_name, 18, accent),
    }[ident["motif"]]

    body = [
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{M.body_fill(theme_name, material)}" opacity="0.5"/>',
        f'<rect x="64" y="86" width="2.5" height="84" fill="{M.prism_fill(theme_name, material)}"/>',
        TY.label(88, 108, ident["label"].upper(), theme_name, size=12, tracking=4),
        TY.text(88, 164, ident["headline"], theme_name,
                size=30, weight=650),
        G.tick_rail(88, 208, 520, theme_name),
        TY.label(88, 236, T.PRIMARY_NAME + " // " + T.STUDIO_NAME, theme_name,
                 size=10.5, opacity=0.45),
        motif,
    ]
    return (
        TY.document(
            W, H,
            f"{ident['label']} — {T.STUDIO_NAME}",
            f"{ident['label']}: {ident['statement']}",
            theme_name, extra_defs=defs)
        + "".join(body) + TY.close()
    )


def system_map(theme_name: str = "dark") -> str:
    """Same truth as every other direction: only evidence-backed edges."""
    t = T.PALETTES[theme_name]
    W = 1200
    rows = [
        ("CONTROL", "nested_frames", "violet",
         [("Portfolio OS", "queue · locks · review · allowlisted publish"),
          ("GrokBot Office", "workforce configuration")]),
        ("EXECUTE", "signal_path", "mint",
         [("AgentOS", "objective in, verified outcome out")]),
        ("ECONOMY", "branching", "indigo",
         [("GrokMax", "route · five-layer cache · ledger"),
          ("GrokInstall", "smallest useful capability")]),
        ("GUARD", "closed_topology", "fail",
         [("OpenCode Watchdog", "deterministic repetition circuit")]),
        ("SURFACE", "layered_evidence", "text_secondary",
         [("gh0st", "local-first encrypted client"),
          ("SEAI Mind", "layered memory kernel"),
          ("GrokBot Society", "persistent actors")]),
    ]
    row_h, gap = 78, 16
    band = 34
    y = 84
    H = y + len(rows) * (row_h + gap + band) + 40
    defs = _defs(theme_name)

    parts = [
        TY.document(
            W, H, f"{T.STUDIO_NAME} operating stack",
            "Five layers over the published systems: control, execution, economy, "
            "guardrails, surfaces. A relationship is drawn only where one "
            "repository's source or documentation names the other.",
            theme_name, extra_defs=defs),
        f'<g opacity="0.4">{G.micro_grid(W, H, theme_name, step=40)}</g>',
    ]
    for name, motif_name, accent_key, items in rows:
        accent = t[accent_key]
        # A layer name is a word, not a rule: it takes the AA-checked variant.
        parts.append(TY.label(64, y, name, theme_name, size=11, tracking=4,
                              fill=T.readable(theme_name, accent_key),
                              opacity=0.85))
        parts.append(f'<line x1="64" y1="{y + 12}" x2="{W - 64}" y2="{y + 12}" '
                     f'stroke="{t["edge"]}" stroke-width="1"/>')
        y += band
        for title, note in items:
            parts.append(
                f'<rect x="64" y="{y}" width="{W - 128}" height="{row_h}" rx="{T.RADIUS["card"]}" '
                f'fill="{M.body_fill(theme_name, "deep_glass")}" '
                f'stroke="{t["edge"]}" stroke-width="1"/>')
            parts.append(TY.text(96, y + 34, title, theme_name, size=19, weight=620))
            parts.append(TY.label(96, y + 56, note, theme_name, size=10.5,
                                  tracking=0.6, opacity=0.5))
            cy = y + row_h / 2
            if motif_name == "nested_frames":
                parts.append(G.nested_frames(W - 250, y + 12, 56, 54, theme_name, 3, accent))
            elif motif_name == "signal_path":
                parts.append(G.signal_path([(W - 250, cy + 18), (W - 214, cy - 12),
                                            (W - 178, cy + 10)], theme_name, accent=accent))
            elif motif_name == "branching":
                parts.append(G.branching(W - 214, cy, theme_name, 4, 26, accent=accent))
            elif motif_name == "closed_topology":
                parts.append(G.closed_topology(W - 214, cy, 26, theme_name,
                                               accent=accent, nodes=6))
            elif motif_name == "layered_evidence":
                parts.append(G.layered_evidence(W - 250, y + 18, 72, 42, theme_name, 3, accent))
            y += row_h + gap
        y += 8
    parts.append(TY.label(64, H - 18,
                          "relationships drawn only where source or docs cite the other system",
                          theme_name, size=10, opacity=0.4))
    parts.append(TY.label(W - 64, H - 18, f"{T.STUDIO_NAME} // {T.PRIMARY_NAME}",
                          theme_name, size=10, tracking=2, opacity=0.4, anchor="end"))
    parts.append(TY.close())
    return "".join(parts)
