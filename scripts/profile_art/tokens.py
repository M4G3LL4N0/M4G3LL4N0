"""Design tokens for the DUNG30N5 x NOAERTH visual system.

One source of truth. Every generated asset imports from here so that a colour
or radius is never retyped across twenty SVGs.

Art direction: LIQUID COMPUTING — optical glass, frosted translucency,
prismatic refraction, spectral edges, technical topology.

Constraint that shapes the whole palette: the assets must sit on GitHub's
Markdown canvas, which is `#ffffff` in light mode and `#0d1117` in dark mode.
So the "background" token is a *canvas tint*, not an opaque fill — the glass
panels have to read as frosted on top of whatever the page already is. That is
also why every asset ships in two variants: opacity-based glass that survives
one background does not survive the other.
"""

from __future__ import annotations

# --- identity -------------------------------------------------------------
PRIMARY_NAME = "DUNG30N5"
STUDIO_NAME = "NOAERTH"
STUDIO_SUBTITLE = "SYSTEMS LAB"
HANDLE = "@M4G3LL4N0"
TAGLINE = "Build systems. Prove them. Compound what works."

# --- palette --------------------------------------------------------------
SPECTRAL_MINT = "#5EE7D0"
SPECTRAL_INDIGO = "#7C8CFF"
SPECTRAL_VIOLET = "#C084FC"

DARK = {
    "canvas": "#0D1117",          # GitHub dark canvas
    "glass": "#161B22",           # panel body
    "glass_hi": "#1C2330",        # raised glass
    "text_primary": "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_faint": "#5A6572",
    "edge": "#2A3441",            # base edge
    "edge_specular": "#8FA6C4",   # specular highlight
    "edge_link": "#7E93B4",       # connector strokes (must contrast on the canvas)
    "grid": "#1B222C",
    "shadow": "#000000",
    "mint": SPECTRAL_MINT,
    "indigo": SPECTRAL_INDIGO,
    "violet": SPECTRAL_VIOLET,
}

LIGHT = {
    "canvas": "#FFFFFF",          # GitHub light canvas
    "glass": "#F3F6FA",
    "glass_hi": "#E9EFF7",
    "text_primary": "#0D1117",
    "text_secondary": "#57606A",
    "text_faint": "#8C959F",
    "edge": "#D6DEE8",
    "edge_specular": "#FFFFFF",
    # On the light canvas, a specular (white) connector is white-on-white and
    # disappears. Link strokes need their own value, not the highlight value.
    "edge_link": "#5C6B84",
    "grid": "#E6ECF3",
    "shadow": "#1F2933",
    "mint": "#12A594",
    "indigo": "#4A5BE8",
    "violet": "#8B44D6",
}

# --- glass optics ---------------------------------------------------------
# Liquid glass reads as liquid because of three things together: a bright top
# edge, a dark bottom edge, and a soft interior gradient. Weighting only the
# highlight gives plastic; weighting only the shade gives a hole.
GLASS = {
    "body_opacity": 0.055,
    "body_opacity_raised": 0.085,
    "edge_opacity": 0.16,
    "specular_opacity": 0.34,
    "radius": 18,
    "radius_sm": 12,
    "stroke": 1,
    "blur": 0,          # SVG has no backdrop-filter; depth is faked with layering
}

# --- type -----------------------------------------------------------------
# No external fonts. These stacks must survive full font fallback on a machine
# that has neither Inter nor SF Pro.
FONT_DISPLAY = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, "
                "Helvetica, Arial, sans-serif")
FONT_MONO = ("ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "
             "'Liberation Mono', monospace")

# Letterspacing on the wordmark is the whole trick for "slightly alien":
# wide tracking on a grotesk reads as instrument-panel, not as a logo template.
TRACK_WORDMARK = "0.30em"
TRACK_LABEL = "0.24em"

# --- layout ---------------------------------------------------------------
GRID_STEP = 32
W_HERO = 1200
H_HERO = 420
W_WIDE = 1200
H_SYSTEM_MAP = 780
W_CARD = 560
H_CARD = 168
W_NAV = 260
H_NAV = 64
W_BUILD_SIGNAL = 1200
H_BUILD_SIGNAL = 200
W_TERMINAL = 620
H_TERMINAL = 190

# --- motion ---------------------------------------------------------------
# Restrained on purpose. Anything faster reads as decoration; the brief asks
# for a quiet instrument, not a screensaver.
MOTION = {
    "loop_seconds": 12,
    "travel_seconds": 12,
    "pulse_seconds": 4.8,
    "sweep_seconds": 9,
    # Longest single luminance transition. WCAG 2.3.1 has no numeric limit but
    # anything above ~3 flashes/sec is hazardous; we stay far below one change
    # per second, so every animation here is safe by a wide margin.
    "min_flash_interval_seconds": 2.5,
}


def theme(name: str) -> dict:
    if name == "light":
        return LIGHT
    if name == "dark":
        return DARK
    raise ValueError(f"unknown theme {name!r}; expected 'dark' or 'light'")


__all__ = [
    "DARK", "LIGHT", "GLASS", "MOTION", "PRIMARY_NAME", "STUDIO_NAME",
    "STUDIO_SUBTITLE", "HANDLE", "TAGLINE", "FONT_DISPLAY", "FONT_MONO",
    "TRACK_WORDMARK", "TRACK_LABEL", "theme",
]