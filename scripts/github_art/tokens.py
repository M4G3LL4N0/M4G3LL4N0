"""Single source of truth for every literal value in the DUNG30N5 x NOAERTH
visual system.

Nothing in this package may hardcode a colour, radius, font size, duration, or
coordinate. If a value is not in this file it does not exist, and
``validators.py`` fails the build when an SVG contains a stray hex literal.

Two palettes are maintained, not one inverted. Dark is obsidian; light is pearl.
Both are tuned against their own canvas, because a value that reads well on
graphite routinely turns to mud on white.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# identity
# --------------------------------------------------------------------------
PRIMARY_NAME = "DUNG30N5"
HANDLE = "@M4G3LL4N0"
STUDIO_NAME = "NOAERTH"
STUDIO_SUBTITLE = "SYSTEMS LAB"
OWNER = "M4G3LL4N0"
REPO = "M4G3LL4N0/M4G3LL4N0"

TAGLINES = (
    ("BUILD SYSTEMS.", "PROVE THEM.", "COMPOUND WHAT WORKS."),
    ("BUILD THE LAYER UNDERNEATH.", "THEN MEASURE IT.", "THEN COMPOUND IT."),
    ("ENGINEERING YOU CAN REPRODUCE.", "NOT PROMISE.", "NOT PRESENTATION."),
)
PRIMARY_TAGLINE = TAGLINES[0]

POSITIONING = "systems builder · hacker · creative technologist"
SUBSTACK = ("autonomous systems · developer infrastructure · "
            "research tooling · experimental technology")

# Public vocabulary. These words describe the finished artefact. The internal
# design process uses different language entirely and it never ships.
PUBLIC_VOCABULARY = (
    "hyperreal computational design",
    "optical computing",
    "dimensional systems",
    "computational material",
    "generative system geometry",
)
FORBIDDEN_PUBLIC_VOCABULARY = (
    "dmt", "psychedelic", "altered state", "hallucination", "trip",
    "acid", "shroom",
)

# --------------------------------------------------------------------------
# spectral DNA - carried forward from the Noaerth identity, not invented here
# --------------------------------------------------------------------------
SPECTRAL_MINT = "#5EE7D0"
SPECTRAL_INDIGO = "#7C8CFF"
SPECTRAL_VIOLET = "#C084FC"

# --------------------------------------------------------------------------
# palettes
# --------------------------------------------------------------------------
# Every *_TEXT value is verified at or above WCAG AA against that theme's own
# canvas by tests/test_profile_assets.py. mint_text exists because the vivid
# spectral mint is unreadable as small text on white: 3.07:1. The rule is that
# mint is for 2px rules and geometry, never for a sentence.
DARK = {
    "canvas": "#0A0E14",          # deep graphite, never pure black
    "canvas_deep": "#070A0F",     # occlusion floor
    "glass": "#121821",
    "glass_hi": "#1A2231",
    "glass_lo": "#0D121A",
    "text_primary": "#E8EEF6",
    "text_secondary": "#93A0B4",
    "text_faint": "#5C6779",
    "text_micro": "#7C8899",
    "edge": "#26303E",
    "edge_specular": "#9FB4D0",
    "edge_link": "#8296B8",
    "grid": "#161D28",
    "grid_strong": "#1E2836",
    "shadow": "#000000",
    "mint": SPECTRAL_MINT,
    "mint_text": SPECTRAL_MINT,
    "indigo": SPECTRAL_INDIGO,
    "violet": SPECTRAL_VIOLET,
    "warn": "#F0B429",
    "fail": "#F2777A",
}

LIGHT = {
    "canvas": "#FCFDFE",
    "canvas_deep": "#F2F5F9",
    "glass": "#F4F7FB",
    "glass_hi": "#EAF0F8",
    "glass_lo": "#FAFBFD",
    "text_primary": "#0A0E14",
    "text_secondary": "#4A5567",
    "text_faint": "#8A94A6",
    "text_micro": "#6B7688",
    "edge": "#D2DBE7",
    "edge_specular": "#FFFFFF",
    "edge_link": "#54637A",
    "grid": "#E9EEF5",
    "grid_strong": "#D9E2EE",
    "shadow": "#1B2430",
    "mint": "#0E9E8C",
    "mint_text": "#0B7A6E",
    "indigo": "#3D4BC4",
    "violet": "#7C3AED",
    "warn": "#8A6100",
    "fail": "#B3261E",
}

PALETTES = {"dark": DARK, "light": LIGHT}

# Semantic accents. Colour encodes layer and status, never decoration.
# A rainbow across unrelated panels is explicitly forbidden by the standard.
SEMANTIC = {
    "control": "violet",     # governance: nested, enclosing
    "execute": "mint",       # execution: directed, live
    "economy": "indigo",     # routing: branching, prismatic
    "guard": "fail",         # safety: closed, protective
    "surface": "text_secondary",  # outputs: quiet, receding
    "verified": "mint",
    "unverified": "text_faint",
    "attention": "warn",
}

# --------------------------------------------------------------------------
# typography
# --------------------------------------------------------------------------
# No webfonts. A profile that depends on a font request renders as Times on any
# machine that has not cached it, and an SVG in an <img> cannot load one anyway.
# Single quotes inside the family names are required: this value is interpolated
# into a double-quoted XML attribute, and a nested double quote produces a file
# that does not parse.
FONT_DISPLAY = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, "
                "Helvetica, Arial, sans-serif")
FONT_MONO = ("ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "
             "'Liberation Mono', monospace")

# A modular scale. Every size in the system is one of these multiplied by a
# density factor, which is what keeps a card and a hero feeling like one thing.
TYPE_SCALE = {
    "micro": 9,
    "annotation": 10.5,
    "caption": 12,
    "body": 14,
    "lead": 18,
    "subhead": 24,
    "headline": 34,
    "display": 56,
    "wordmark": 88,
    "monolith": 128,
}

TRACKING = {
    "tight": -0.6,
    "none": 0,
    "wide": 1.2,
    "label": 2.6,
    "shell": 4.4,
}

# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------
# A small set of radii and a single repeating measurement. Recursive structure
# comes from the module, not from decoration.
RADIUS = {
    "chip": 14,
    "card": 18,
    "panel": 22,
    "plate": 28,
}

UNIT = 8
GRID_STEP = 40
TICK_STEP = 10
HAIRLINE = 1
RULE = 2

# Stroke weights stay hairline-to-thin. Crispness is a requirement; heavy
# strokes read as illustration rather than instrument.
STROKE = {
    "hairline": 1,
    "fine": 1.25,
    "signal": 2,
    "emphasis": 2.5,
}

# --------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------
# Materials are recipes, not adjectives. Each resolves to concrete SVG defs for
# a given theme, so a material can be swapped without touching geometry.
MATERIALS = ("optical_glass", "spectral_glass", "deep_glass",
             "obsidian_compute", "luminous_ceramic", "liquid_crystal",
             "computational_material")

# How each material is allowed to behave. A security surface does not get the
# luminous material; that would be decoration overriding meaning.
MATERIAL_ROLE = {
    "optical_glass": ("control", "governance, queue, ordering"),
    "spectral_glass": ("economy", "routing, cost paths, caching"),
    "deep_glass": ("execute", "execution, capability, verification"),
    "obsidian_compute": ("guard", "containment, safety, failure handling"),
    "luminous_ceramic": ("surface", "human-facing output"),
    "liquid_crystal": ("research", "layered evidence, memory, recursion"),
    "computational_material": ("experimental", "generative, not yet settled"),
}

# --------------------------------------------------------------------------
# motion
# --------------------------------------------------------------------------
# Ambient only. Nothing here loops faster than 1s, and nothing moves a large
# area quickly. Reduced-motion equivalents are supplied at the README layer via
# <source media="(prefers-reduced-motion: reduce)">; GitHub's sanitizer
# preserves those, which was verified. The same query does NOT reach an SVG
# loaded through <img> in Chrome, which was also verified, so no motion logic
# lives inside the SVG.
MOTION = {
    "loop_seconds": 12.0,
    "travel_seconds": 7.5,
    "pulse_seconds": 4.0,
    "caret_seconds": 1.6,      # ~0.6Hz, an order of magnitude below 3Hz
    "sweep_opacity": 0.32,
    "breath_low": 0.60,
    "breath_high": 1.0,
}

# --------------------------------------------------------------------------
# visual intensity
# --------------------------------------------------------------------------
# The standard asks for contrast between sections, not uniform intensity. These
# are the target intensities; generators assert against them.
INTENSITY = {
    "general_content": (0.25, 0.45),
    "cards_diagrams": (0.35, 0.55),
    "profile_hero": (0.65, 0.80),
    "system_graphic": (0.55, 0.70),
    "easter_egg": (0.50, 0.70),
}

# --------------------------------------------------------------------------
# performance budget
# --------------------------------------------------------------------------
BUDGET = {
    "readme_kb": 75,
    "svg_kb": 200,
    "animation_kb": 2048,
    "animated_payload_kb": 5120,
    "single_plate_kb": 48,
    "card_kb": 24,
}


# --------------------------------------------------------------------------
# readable accents
# --------------------------------------------------------------------------
# The vivid spectral accents are for geometry: 2px rules, node fills, traces.
# Several of them fall below AA as small text on their own canvas, so asking for
# "mint as text" has to be a different request than "mint as a rule". Generators
# call readable() whenever a colour is destined for a glyph rather than a fill.


def readable(theme_name: str, key: str) -> str:
    """Return a variant of ``key`` that is verified at or above AA as text."""
    palette = PALETTES[theme_name]
    if key == "mint":
        return palette["mint_text"]
    if key in ("warn", "fail"):
        # Both are already dark enough on light and bright enough on dark;
        # mint_text is the only accent that needed a split.
        return palette[key]
    return palette.get(key, key)
