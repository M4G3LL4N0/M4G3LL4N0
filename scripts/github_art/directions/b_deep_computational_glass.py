"""Direction B - DEEP COMPUTATIONAL GLASS.

Premise: the profile is a cross-section through a running system. Surfaces are
deep and translucent, each layer visibly containing the space behind it, with
occlusion and internal floor planes doing the work that A does with line.

Character: atmospheric, layered, recessive. Highest sense of depth; weakest
crispness, because translucent stacks invite softness. Risk of drifting toward
generic glassmorphism, which the standard explicitly rejects.
"""
from __future__ import annotations

from .. import geometry as G
from .. import materials as M
from .. import tokens as T
from .. import typography as TY

NAME = "DEEP COMPUTATIONAL GLASS"
SLUG = "b-deep-computational-glass"
INTENSITY = {
    "profile_hero": 0.74,
    "flagship_hero": 0.46,
    "system_map": 0.62,
    "easter_egg": 0.60,
}


def _defs(theme: str) -> str:
    return (M.definitions(theme, "deep_glass")
            + M.definitions(theme, "optical_glass")
            + M.definitions(theme, "liquid_crystal")
            + M.definitions(theme, "obsidian_compute"))


def _strata(x, y, w, h, theme_name: str, layers: int = 5) -> str:
    """Receding translucent planes. Depth by occlusion, not by blur."""
    out = []
    for i in range(layers):
        depth = i / max(layers - 1, 1)
        inset_x = x + depth * w * 0.16
        inset_y = y + depth * h * 0.20
        panel_w = w - depth * w * 0.32
        panel_h = h - depth * h * 0.30
        opacity = 0.90 - depth * 0.52
        out.append(
            f'<rect x="{inset_x:.2f}" y="{inset_y:.2f}" width="{panel_w:.2f}" '
            f'height="{panel_h:.2f}" rx="{T.RADIUS["panel"] - i}" '
            f'fill="{T.PALETTES[theme_name]["glass"]}" fill-opacity="{opacity:.2f}" '
            f'stroke="{T.PALETTES[theme_name]["edge"]}" stroke-width="1" '
            f'stroke-opacity="{0.85 - depth * 0.5:.2f}"/>'
        )
        # the lit top edge is what makes each plane read as a solid surface
        out.append(
            f'<line x1="{inset_x:.2f}" y1="{inset_y:.2f}" x2="{inset_x + panel_w:.2f}" '
            f'y2="{inset_y:.2f}" stroke="{T.PALETTES[theme_name]["edge_specular"]}" '
            f'stroke-width="1" stroke-opacity="{0.5 - depth * 0.3:.2f}"/>'
        )
    return "".join(out)


def hero(theme_name: str = "dark", compact: bool = False) -> str:
    t = T.PALETTES[theme_name]
    W, H = (460, 400) if compact else (1200, 420)
    scale_w = 54 if compact else 88
    scale_s = 15 if compact else 24
    defs = _defs(theme_name)

    if compact:
        body = [
            _strata(238, 92, 178, 150, theme_name, 4),
            TY.text(44, 176, T.PRIMARY_NAME, theme_name, size=scale_w, weight=700,
                    tracking=3),
            TY.text(44, 210, "Build systems.", theme_name, size=scale_s,
                    fill=t["text_secondary"]),
            TY.text(44, 234, "Prove them.", theme_name, size=scale_s,
                    fill=t["text_secondary"]),
            TY.text(44, 258, "Compound what works.", theme_name, size=scale_s,
                    fill=t["text_secondary"]),
            f'<rect x="44" y="88" width="2.5" height="86" fill="{M.prism_fill(theme_name, "deep_glass")}"/>',
            TY.label(44, 306, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}", theme_name,
                     size=9.5),
            TY.label(44, 328, T.OWNER, theme_name, size=9.5, opacity=0.4),
        ]
    else:
        body = [
            _strata(700, 78, 400, 268, theme_name, 5),
            f'<rect x="72" y="112" width="2.5" height="132" fill="{M.prism_fill(theme_name, "deep_glass")}"/>',
            TY.label(96, 136, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}", theme_name,
                     size=13, tracking=4.4),
            TY.text(96, 228, T.PRIMARY_NAME, theme_name, size=scale_w, weight=700,
                    tracking=8),
            TY.text(96, 268, "Build systems. Prove them. Compound what works.",
                    theme_name, size=scale_s, fill=t["text_secondary"]),
            G.tick_rail(96, 330, 470, theme_name),
            TY.label(96, 356, f"NOAERTH.COM   ·   GITHUB {T.HANDLE}", theme_name,
                     size=11.5, opacity=0.5),
        ]
    return (
        TY.document(
            W, H, f"{T.PRIMARY_NAME} — {T.STUDIO_NAME} {T.STUDIO_SUBTITLE}",
            f"Identity plate for {T.PRIMARY_NAME}. Receding glass strata carry the "
            f"studio mark. Reads: build systems, prove them, compound what works.",
            theme_name, extra_defs=defs)
        + "".join(body) + TY.close()
    )


def flagship_hero(theme_name: str = "dark", slug: str = "agentos") -> str:
    from .. import project_identity as P
    t = T.PALETTES[theme_name]
    ident = P.identity(slug)
    accent = t[ident["accent"]]
    W, H = 1200, 300
    material = ident["material"]
    defs = _defs(theme_name) + M.definitions(theme_name, material)

    body = [
        _strata(560, 44, 600, 212, theme_name, 4),
        f'<rect x="64" y="86" width="2.5" height="84" fill="{M.prism_fill(theme_name, material)}"/>',
        TY.label(88, 108, ident["label"].upper(), theme_name, size=12, tracking=4),
        TY.text(88, 164, ident["headline"], theme_name,
                size=30, weight=650),
        G.tick_rail(88, 208, 400, theme_name),
        TY.label(88, 236, T.PRIMARY_NAME + " // " + T.STUDIO_NAME, theme_name,
                 size=10.5, opacity=0.45),
        f'<circle cx="900" cy="150" r="54" fill="none" stroke="{accent}" '
        f'stroke-width="1.5" opacity="0.55"/>',
        f'<circle cx="900" cy="150" r="34" fill="none" stroke="{accent}" '
        f'stroke-width="1" opacity="0.35"/>',
        f'<circle cx="900" cy="150" r="6" fill="{accent}"/>',
    ]
    return (
        TY.document(W, H, f"{ident['label']} — {T.STUDIO_NAME}",
                    f"{ident['label']}: {ident['statement']}",
                    theme_name, extra_defs=defs)
        + "".join(body) + TY.close()
    )


def system_map(theme_name: str = "dark") -> str:
    t = T.PALETTES[theme_name]
    W = 1200
    bands = [
        ("CONTROL", "violet", 1),
        ("EXECUTE", "mint", 1),
        ("ECONOMY", "indigo", 2),
        ("GUARD", "fail", 1),
        ("SURFACE", "text_secondary", 3),
    ]
    names = {
        "CONTROL": [("Portfolio OS", "queue · locks · review · publish"),
                    ("GrokBot Office", "workforce configuration")],
        "EXECUTE": [("AgentOS", "objective in, verified outcome out")],
        "ECONOMY": [("GrokMax", "route · cache · ledger"),
                    ("GrokInstall", "smallest useful capability")],
        "GUARD": [("OpenCode Watchdog", "repetition circuit")],
        "SURFACE": [("gh0st", "encrypted local client"),
                    ("SEAI Mind", "layered memory"),
                    ("GrokBot Society", "persistent actors")],
    }
    y = 84
    H = 84 + len(bands) * 148 + 40
    defs = _defs(theme_name)
    parts = [
        TY.document(W, H, f"{T.STUDIO_NAME} operating stack",
                    "Five layers over the published systems. Depth encodes position "
                    "in the stack; a relationship is named only where one "
                    "repository's documentation names the other.",
                    theme_name, extra_defs=defs),
        f'<g opacity="0.3">{G.micro_grid(W, H, theme_name, step=48)}</g>',
    ]
    for band, key, count in bands:
        accent = t[key]
        parts.append(TY.label(64, y, band, theme_name, size=11, tracking=4,
                              fill=T.readable(theme_name, key), opacity=0.85))
        parts.append(f'<line x1="64" y1="{y + 12}" x2="{W - 64}" y2="{y + 12}" '
                     f'stroke="{t["edge"]}" stroke-width="1"/>')
        y += 30
        col_w = (W - 128 - 24 * (count - 1)) / count
        for i, (title, note) in enumerate(names[band]):
            px = 64 + i * (col_w + 24)
            parts.append(
                f'<rect x="{px:.1f}" y="{y}" width="{col_w:.1f}" height="96" '
                f'rx="{T.RADIUS["panel"]}" fill="{M.body_fill(theme_name, "deep_glass")}" '
                f'opacity="0.92" stroke="{t["edge"]}" stroke-width="1"/>')
            parts.append(
                f'<line x1="{px:.1f}" y1="{y}" x2="{px + col_w:.1f}" y2="{y}" '
                f'stroke="{accent}" stroke-width="2" stroke-opacity="0.7"/>')
            parts.append(TY.text(px + 24, y + 44, title, theme_name, size=19, weight=620))
            parts.append(TY.label(px + 24, y + 68, note, theme_name, size=10.5,
                                  tracking=0.6, opacity=0.5))
        y += 118
    parts.append(TY.label(64, H - 18,
                          "depth encodes stack position, not dependency",
                          theme_name, size=10, opacity=0.4))
    parts.append(TY.label(W - 64, H - 18, f"{T.STUDIO_NAME} // {T.PRIMARY_NAME}",
                          theme_name, size=10, tracking=2, opacity=0.4, anchor="end"))
    parts.append(TY.close())
    return "".join(parts)
