"""Project identity grammar.

Every flagship gets its own geometry, material, and accent, derived from what
the system actually does. Re-colouring one card nine times is the failure mode
this module exists to prevent: nine identical cards communicate nothing, and a
reader who cannot tell them apart learns nothing from the grid.

Each identity is built from the same primitives and the same module, so the
set reads as one system while every tile remains individually recognisable.
"""
from __future__ import annotations

from . import geometry as G
from . import tokens as T

# name -> identity
#   motif     which semantic primitive carries the idea
#   material  the substance the system is made of
#   accent    the one semantic colour it owns
#   statement the single sentence the tile has to communicate
IDENTITIES = {
    "agentos": {
        "label": "AgentOS",
        "motif": "signal_path",
        "material": "deep_glass",
        "accent": "mint",
        "statement": "Objective in, planning, execution, verification out. One direction, "
                     "one terminus.",
        "headline": "Objective in. Verified outcome out.",
        "kind": "FLAGSHIP",
    },
    "grokinstall": {
        "label": "GrokInstall",
        "motif": "branching",
        "material": "spectral_glass",
        "accent": "indigo",
        "statement": "Capability insertion. The smallest useful thing, or nothing at all.",
        "headline": "The smallest useful capability",
        "kind": "FLAGSHIP",
    },
    "grokmax": {
        "label": "GrokMax",
        "motif": "prism_fan",
        "material": "spectral_glass",
        "accent": "indigo",
        "statement": "Routing with priced paths: the cheapest sufficient executor wins, "
                     "and the ledger says which.",
        "headline": "The cheapest sufficient path",
        "kind": "FLAGSHIP",
    },
    "gh0st": {
        "label": "gh0st",
        "motif": "closed_topology",
        "material": "obsidian_compute",
        "accent": "fail",
        "statement": "Local-first encryption. The boundary holds, and it is visible.",
        "headline": "Local-first. Sealed by default",
        "kind": "FLAGSHIP",
    },
    "opencode-watchdog": {
        "label": "OpenCode Watchdog",
        "motif": "split_ring",
        "material": "obsidian_compute",
        "accent": "fail",
        "statement": "Circuit breaker for runaway sessions. Containment before cost.",
        "headline": "Containment before cost",
        "kind": "FLAGSHIP",
    },
    "grokbot-office": {
        "label": "GrokBot Office",
        "motif": "nested_frames",
        "material": "optical_glass",
        "accent": "violet",
        "statement": "Workforce topology: roles, policy, handoffs above the substrate.",
        "headline": "Workforce above the substrate",
        "kind": "PUBLIC_PROJECT",
    },
    "grokbot-society": {
        "label": "GrokBot Society",
        "motif": "generative_field",
        "material": "computational_material",
        "accent": "mint",
        "statement": "Persistent actors and the network between them.",
        "headline": "Persistent actors, governed",
        "kind": "PUBLIC_PROJECT",
    },
    "seai-mind": {
        "label": "SEAI Mind",
        "motif": "layered_evidence",
        "material": "liquid_crystal",
        "accent": "violet",
        "statement": "Memory and capability as layered, inspectable strata.",
        "headline": "Memory as inspectable strata",
        "kind": "PUBLIC_PROJECT",
    },
}

# The flagship set is an explicit list, never "whatever is public".
# Portfolio OS was removed from the public set: its name is on the publication
# denylist, so the repository is private. It keeps a place in the control plane
# that generates this profile, but it is no longer a public system and must not
# appear in artwork, pins, or the public inventory.
FLAGSHIP_ORDER = (
    "agentos",
    "grokinstall",
    "grokmax",
    "gh0st",
    "opencode-watchdog",
)

# Systems with no documented runtime relationship still need a visual identity;
# they are drawn as standalone plates rather than being given a false edge.
STANDALONE = ("grokbot-office", "grokbot-society", "seai-mind", "gh0st")


def identity(slug: str) -> dict:
    if slug not in IDENTITIES:
        raise KeyError(
            f"no identity defined for {slug!r}. Every public system needs one; "
            f"add it to IDENTITIES with a motif that matches what it does.")
    return IDENTITIES[slug]


def glyph(slug: str, theme_name: str, cx: float, cy: float, size: float = 30) -> str:
    """Render a project's motif as a standalone mark.

    Every mark is recognisable in silhouette alone, because a 28px tile cannot
    afford detail that only reads at 200px.
    """
    ident = identity(slug)
    accent = T.PALETTES[theme_name][ident["accent"]]
    half = size / 2
    motif = ident["motif"]

    if motif == "nested_frames":
        # Three concentric frames alone collapse to a plain rounded rectangle at
        # large sizes: the insets are proportional, so the inner frames land on
        # top of each other and the mark reads as empty. A governance surface
        # also needs to show what it governs, so the frames carry a queue.
        frames = G.nested_frames(cx - half, cy - half, size, size, theme_name,
                                 depth=3, accent=accent)
        bars = []
        inner_w = size * 0.42
        bar_h = max(size * 0.045, 2)
        for i in range(3):
            bx = cx - inner_w / 2
            by = cy - inner_w * 0.30 + i * (bar_h * 2.6)
            width = inner_w * (1.0 - i * 0.22)
            bars.append(
                f'<rect x="{bx:.2f}" y="{by:.2f}" width="{width:.2f}" '
                f'height="{bar_h:.2f}" rx="{bar_h / 2:.2f}" fill="{accent}" '
                f'opacity="{0.85 - i * 0.22:.2f}"/>'
            )
        return frames + "".join(bars)
    if motif == "signal_path":
        pts = [(cx - half, cy + half * 0.6), (cx - half * 0.15, cy - half * 0.1),
               (cx + half * 0.2, cy + half * 0.55), (cx + half, cy - half * 0.55)]
        return (G.signal_path(pts, theme_name, accent=accent)
                + G.node(cx + half, cy - half * 0.55, 3, theme_name, active=True,
                         accent=accent))
    if motif == "branching":
        return G.branching(cx, cy, theme_name, arms=4, length=half * 1.15,
                           accent=accent)
    if motif == "closed_topology":
        return G.closed_topology(cx, cy, half * 0.86, theme_name,
                                 accent=accent, nodes=7)
    if motif == "layered_evidence":
        return G.layered_evidence(cx - half, cy - half * 0.6, size, half * 1.1,
                                   theme_name, strata=4, accent=accent)
    if motif == "prism_fan":
        from . import geometry_v51 as G51
        return G51.prism_fan(cx, cy, size * 0.42, theme_name, ident["accent"],
                             blades=7)
    if motif == "split_ring":
        from . import geometry_v51 as G51
        return G51.split_ring(cx, cy, size * 0.44, theme_name, ident["accent"])
    if motif == "generative_field":
        return G.generative_field(cx - half, cy - half * 0.7, size, half * 1.4,
                                  theme_name, seed_points=18, accent=accent)
    raise KeyError(f"unhandled motif {motif!r}")


def signature_motifs() -> set:
    """Motifs in use, so validation can flag a grid of visually identical tiles."""
    return {i["motif"] for i in IDENTITIES.values()}


DEFAULT_MATERIAL = "optical_glass"


def has_identity(slug: str) -> bool:
    """Whether a designed identity exists for this slug."""
    return slug in IDENTITIES


def material_for(slug: str) -> str:
    return identity(slug)["material"]


def accent_for(slug: str) -> str:
    return identity(slug)["accent"]


def label_for(slug: str) -> str:
    return identity(slug)["label"]
