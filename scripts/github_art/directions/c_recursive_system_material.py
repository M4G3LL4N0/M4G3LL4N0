"""Direction C - RECURSIVE SYSTEM MATERIAL.

Premise: one module generates every scale. The hero lattice, a card glyph, a
diagram node, and a status tick are all the same construction at different
zooms, so a viewer who looks closely finds new structure instead of filler.

Character: intricate, self-similar, quietly alive. Highest reward under
inspection; the greatest risk of reading as fractal wallpaper, which the
standard explicitly rejects. The recursion has to stay subordinate to content,
which is why every plate keeps a quiet band around its text.
"""
from __future__ import annotations

from .. import geometry as G
from .. import materials as M
from .. import tokens as T
from .. import typography as TY

NAME = "RECURSIVE SYSTEM MATERIAL"
SLUG = "c-recursive-system-material"
INTENSITY = {
    "profile_hero": 0.78,
    "flagship_hero": 0.52,
    "system_map": 0.66,
    "easter_egg": 0.66,
}


def _defs(theme: str) -> str:
    return (M.definitions(theme, "computational_material")
            + M.definitions(theme, "deep_glass")
            + M.definitions(theme, "spectral_glass")
            + M.definitions(theme, "liquid_crystal"))


def _module(x, y, size, theme_name: str, depth: int = 4,
            accent_key: str = "mint", seed: int = 7) -> str:
    """The recursive unit: a square whose quadrants repeat it smaller.

    Fractal ORGANISATION, not fractal decoration. Every level is a quarter the
    size of the last and carries less opacity, so the eye reads structure rather
    than texture.
    """
    t = T.PALETTES[theme_name]
    accent = t[accent_key]
    out = []
    if depth <= 0 or size < 14:
        return ""
    out.append(
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" '
        f'fill="none" stroke="{accent}" stroke-width="1" '
        f'opacity="{0.16 + depth * 0.12:.2f}"/>'
    )
    # tick marks on two edges: the measurement detail that makes recursion read
    # as an instrument rather than a fractal
    for i in range(1, 4):
        tx = x + size * i / 4
        out.append(f'<line x1="{tx:.2f}" y1="{y:.2f}" x2="{tx:.2f}" y2="{y + size * 0.12:.2f}" '
                   f'stroke="{t["edge"]}" stroke-width="1" opacity="0.5"/>')
    half = size / 2
    # three of four quadrants recurse; the fourth stays empty, which is what
    # keeps the pattern directional instead of merely busy
    for qx, qy in ((0, 0), (1, 0), (0, 1)):
        out.append(_module(x + qx * half, y + qy * half, half, theme_name,
                           depth - 1, accent_key, seed + qx + qy))
    return "".join(out)


def _module_field(x, y, w, h, theme_name: str, accent_key: str = "mint") -> str:
    t = T.PALETTES[theme_name]
    return (
        f'<g opacity="0.55">{_module(x, y, min(w, h), theme_name, 4, accent_key)}</g>'
        f'<g opacity="0.30">{_module(x + w * 0.52, y + h * 0.30, min(w, h) * 0.42, theme_name, 3, "indigo")}</g>'
        f'<g opacity="0.22">{_module(x + w * 0.16, y + h * 0.58, min(w, h) * 0.30, theme_name, 3, "violet")}</g>'
    )


def hero(theme_name: str = "dark", compact: bool = False) -> str:
    t = T.PALETTES[theme_name]
    W, H = (460, 400) if compact else (1200, 420)
    scale_w = 54 if compact else 88
    scale_s = 15 if compact else 24
    defs = _defs(theme_name)

    if compact:
        field = (f'<g opacity="0.5">{_module(258, 108, 130, theme_name, 4, "mint")}</g>')
        body = [
            field,
            TY.text(44, 176, T.PRIMARY_NAME, theme_name, size=scale_w, weight=700,
                    tracking=3),
            TY.text(44, 210, "Build systems.", theme_name, size=scale_s,
                    fill=t["text_secondary"]),
            TY.text(44, 234, "Prove them.", theme_name, size=scale_s,
                    fill=t["text_secondary"]),
            TY.text(44, 258, "Compound what works.", theme_name, size=scale_s,
                    fill=t["text_secondary"]),
            f'<rect x="44" y="88" width="2.5" height="86" fill="{M.prism_fill(theme_name, "computational_material")}"/>',
            TY.label(44, 306, f"{T.STUDIO_NAME} // {T.STUDIO_SUBTITLE}", theme_name, size=9.5),
            TY.label(44, 328, T.OWNER, theme_name, size=9.5, opacity=0.4),
        ]
    else:
        body = [
            _module_field(700, 70, 420, 280, theme_name),
            f'<rect x="72" y="112" width="2.5" height="132" fill="{M.prism_fill(theme_name, "computational_material")}"/>',
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
            f"Identity plate for {T.PRIMARY_NAME}. A recursive module repeats at "
            f"three scales behind the wordmark. Reads: build systems, prove them, "
            f"compound what works.",
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
        f'<g opacity="0.45">{_module(700, 60, 190, theme_name, 4, ident["accent"])}</g>',
        f'<rect x="64" y="86" width="2.5" height="84" fill="{M.prism_fill(theme_name, material)}"/>',
        TY.label(88, 108, ident["label"].upper(), theme_name, size=12, tracking=4),
        TY.text(88, 164, ident["headline"], theme_name,
                size=30, weight=650),
        G.tick_rail(88, 208, 520, theme_name),
        TY.label(88, 236, T.PRIMARY_NAME + " // " + T.STUDIO_NAME, theme_name,
                 size=10.5, opacity=0.45),
        # state pips: the smallest expression of the same module
        "".join(
            f'<rect x="{990 + i * 26}" y="236" width="14" height="6" rx="1" '
            f'fill="{accent if i < 3 else t["edge"]}" '
            f'opacity="{0.9 if i < 3 else 0.6}"/>'
            for i in range(5)),
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
    rows = [
        ("CONTROL", "violet", [("Portfolio OS", "queue · locks · review"),
                               ("GrokBot Office", "workforce configuration")]),
        ("EXECUTE", "mint", [("AgentOS", "objective in, verified outcome out")]),
        ("ECONOMY", "indigo", [("GrokMax", "route · cache · ledger"),
                               ("GrokInstall", "smallest useful capability")]),
        ("GUARD", "fail", [("OpenCode Watchdog", "repetition circuit")]),
        ("SURFACE", "text_secondary", [("gh0st", "encrypted local client"),
                                       ("SEAI Mind", "layered memory"),
                                       ("GrokBot Society", "persistent actors")]),
    ]
    row_h, band = 74, 32
    y = 84
    H = y + len(rows) * (row_h * 2 + band + 14) + 40
    defs = _defs(theme_name)
    parts = [
        TY.document(W, H, f"{T.STUDIO_NAME} operating stack",
                    "Five layers over the published systems, each drawn with the "
                    "same recursive module used by the identity plate.",
                    theme_name, extra_defs=defs),
        f'<g opacity="0.22">{G.micro_grid(W, H, theme_name, step=48)}</g>',
    ]
    for name, key, items in rows:
        parts.append(TY.label(64, y, name, theme_name, size=11, tracking=4,
                              fill=T.readable(theme_name, key), opacity=0.85))
        parts.append(f'<line x1="64" y1="{y + 12}" x2="{W - 64}" y2="{y + 12}" '
                     f'stroke="{t["edge"]}" stroke-width="1"/>')
        y += band
        for i, (title, note) in enumerate(items):
            px = 64 + i * ((W - 128) / max(len(items), 1))
            pw = (W - 128) / max(len(items), 1) - 20
            parts.append(
                f'<rect x="{px:.1f}" y="{y}" width="{pw:.1f}" height="{row_h * 2 - 14}" '
                f'rx="{T.RADIUS["card"]}" fill="{M.body_fill(theme_name, "computational_material")}" '
                f'opacity="0.6" stroke="{t["edge"]}" stroke-width="1"/>')
            parts.append(f'<g opacity="0.32">{_module(px + pw - 66, y + 12, 52, theme_name, 3, key)}</g>')
            parts.append(TY.text(px + 22, y + 40, title, theme_name, size=18, weight=620))
            parts.append(TY.label(px + 22, y + 62, note, theme_name, size=10.5,
                                  tracking=0.6, opacity=0.5))
            parts.append(TY.label(px + 22, y + 92, f"layer {name.lower()}", theme_name,
                                  size=9, opacity=0.3))
        y += row_h * 2 + 14
    parts.append(TY.label(64, H - 18,
                          "one module, three scales; relationships named only where documented",
                          theme_name, size=10, opacity=0.4))
    parts.append(TY.label(W - 64, H - 18, f"{T.STUDIO_NAME} // {T.PRIMARY_NAME}",
                          theme_name, size=10, tracking=2, opacity=0.4, anchor="end"))
    parts.append(TY.close())
    return "".join(parts)
