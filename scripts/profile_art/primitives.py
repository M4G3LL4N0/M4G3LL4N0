"""Shared SVG primitives for the DUNG30N5 x NOAERTH art system.

Everything visual is built from these, so a change to the glass recipe changes
every asset at once. No rasterisation, no external fonts, no filter bloat.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

from tokens import DARK, FONT_DISPLAY, FONT_MONO, GLASS, LIGHT


def esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def header(width: int, height: int, title: str, desc: str) -> str:
    """Accessible, self-describing SVG root. The <title> is not decoration —
    GitHub renders it as the image's accessible name in some contexts."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>')


def defs_common(theme: dict, uid: str) -> str:
    """Glass recipe: interior gradient, bright top edge, dark bottom edge."""
    return f"""
  <defs>
    <linearGradient id="{uid}-sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{theme['mint']}" stop-opacity="0"/>
      <stop offset="45%" stop-color="{theme['mint']}" stop-opacity="0.9"/>
      <stop offset="60%" stop-color="{theme['indigo']}" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="{theme['violet']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="{uid}-body" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="{theme['glass_hi']}" stop-opacity="{GLASS['body_opacity_raised']}"/>
      <stop offset="55%" stop-color="{theme['glass']}" stop-opacity="{GLASS['body_opacity']}"/>
      <stop offset="100%" stop-color="{theme['glass']}" stop-opacity="{GLASS['body_opacity'] * 0.6}"/>
    </linearGradient>
    <linearGradient id="{uid}-edge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme['edge_specular']}" stop-opacity="{GLASS['specular_opacity']}"/>
      <stop offset="42%" stop-color="{theme['edge']}" stop-opacity="{GLASS['edge_opacity']}"/>
      <stop offset="100%" stop-color="{theme['edge']}" stop-opacity="{GLASS['edge_opacity'] * 1.5}"/>
    </linearGradient>
    <linearGradient id="{uid}-prism" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['mint']}"/>
      <stop offset="52%" stop-color="{theme['indigo']}"/>
      <stop offset="100%" stop-color="{theme['violet']}"/>
    </linearGradient>
    <radialGradient id="{uid}-bloom" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="{theme['indigo']}" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="{theme['indigo']}" stop-opacity="0"/>
    </radialGradient>
  </defs>"""


def background_grid(width: int, height: int, theme: dict, step: int = 32) -> str:
    """Hairline lattice. Sparse on purpose — a full grid reads as graph paper."""
    parts = []
    for x in range(step, width, step * 2):
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" '
                     f'stroke="{theme["grid"]}" stroke-width="1"/>')
    for y in range(step, height, step * 2):
        parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" '
                     f'stroke="{theme["grid"]}" stroke-width="1"/>')
    return "\n  ".join(parts)


def glass_panel(x: float, y: float, w: float, h: float, uid: str, *,
                radius: int | None = None, raised: bool = False,
                stroke_opacity: float | None = None) -> str:
    """A frosted optical slab: interior gradient plus a lit edge."""
    r = radius if radius is not None else GLASS["radius"]
    stroke = stroke_opacity if stroke_opacity is not None else 1
    fill = f"url(#{uid}-body)"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
            f'stroke="url(#{uid}-edge)" stroke-width="{GLASS["stroke"]}" '
            f'opacity="{stroke}"/>')


def specular_top(x: float, y: float, w: float, r: int) -> str:
    """The bright hairline along a panel's top edge — the strongest single cue
    that a surface is glass rather than a filled rectangle."""
    return (f'<path d="M{x + r} {y} H{x + w - r}" stroke="#FFFFFF" '
            f'stroke-opacity="0.20" stroke-width="1" stroke-linecap="round"/>')


def text(x: float, y: float, content: str, *, size: float, theme: dict,
         family: str = FONT_DISPLAY, weight: int = 400, tracking: float = 0,
         opacity: float = 1.0, anchor: str = "start") -> str:
    track = f' letter-spacing="{tracking}"' if tracking else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{theme["text_primary"]}" '
            f'opacity="{opacity}" text-anchor="{anchor}"{track}>{esc(content)}</text>')


def label(x: float, y: float, content: str, theme: dict, *, size: float = 11,
          tracking: float = 3.4, opacity: float = 0.75, anchor: str = "start") -> str:
    """Instrument-panel microtext. Always monospace, always tracked out."""
    return text(x, y, content, size=size, theme=theme, family=FONT_MONO,
                weight=500, tracking=tracking, opacity=opacity, anchor=anchor)


def node(cx: float, cy: float, r: float, theme: dict, *, active: bool = False,
         uid: str = "") -> str:
    if active:
        return (f'<circle cx="{cx}" cy="{cy}" r="{r + 5}" fill="{theme["mint"]}" '
                f'opacity="0.16"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{theme["mint"]}"/>')
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{theme["canvas"]}" '
            f'stroke="{theme["mint"]}" stroke-width="1.25" stroke-opacity="0.75"/>')


def connector(x1: float, y1: float, x2: float, y2: float, theme: dict, *,
              opacity: float = 0.34, dash: str | None = None) -> str:
    """Stroke colour comes from `edge_link`, never `edge_specular`.

    A specular highlight is near-white by definition; using it for a hairline
    connector makes the line invisible on a light canvas.
    """
    d = f' stroke-dasharray="{dash}"' if dash else ""
    stroke = theme.get("edge_link") or theme["edge_specular"]
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="1" '
            f'stroke-opacity="{opacity}"{d}/>')


def svg_end() -> str:
    return "</svg>"


__all__ = [
    "background_grid", "connector", "defs_common", "esc", "glass_panel", "header",
    "label", "node", "specular_top", "svg_end", "text",
]