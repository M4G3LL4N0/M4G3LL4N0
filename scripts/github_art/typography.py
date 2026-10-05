"""Typography and the SVG document scaffold.

Typography is the most stable object in the system. Everything else moves,
scales, glows and refracts; type stays put and stays readable. So this module is
deliberately the least interesting one: fixed sizes from the modular scale,
tracked labels, and a scaffold that guarantees every generated file is valid,
accessible, and self-contained.
"""
from __future__ import annotations

import xml.sax.saxutils as su

from . import tokens as T

SVG_NS = "http://www.w3.org/2000/svg"


def esc(value: str) -> str:
    return su.escape(str(value))


def text(x, y, content: str, theme_name: str, size: float | None = None,
         weight: int = 400, fill: str | None = None, anchor: str | None = None,
         tracking: float = 0.0, opacity: float | None = None,
         family: str | None = None, upper: bool = False) -> str:
    """A single line of type. Never a tspan, never auto-wrapped: both are
    unpredictable inside an <img>-loaded SVG."""
    t = T.PALETTES[theme_name]
    size = size if size is not None else T.TYPE_SCALE["body"]
    family = family or T.FONT_DISPLAY
    if upper:
        content = content.upper()
    parts = [
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill or t["text_primary"]}"'
    ]
    if anchor:
        parts.append(f' text-anchor="{anchor}"')
    if tracking:
        parts.append(f' letter-spacing="{tracking}"')
    if opacity is not None:
        parts.append(f' opacity="{opacity}"')
    parts.append(f">{esc(content)}</text>")
    return "".join(parts)


def label(x, y, content: str, theme_name: str, size: float | None = None,
          tracking: float | None = None, opacity: float = 0.6,
          fill: str | None = None, anchor: str | None = None,
          upper: bool = True, mono: bool = False) -> str:
    """Tracked microtype: the annotation layer.

    This is decorative-adjacent, so it is allowed to sit below body contrast,
    but it must never carry information that exists nowhere else. Every value
    rendered here is also present in the README's text layer.
    """
    t = T.PALETTES[theme_name]
    size = size if size is not None else T.TYPE_SCALE["annotation"]
    tracking = tracking if tracking is not None else T.TRACKING["label"]
    return text(x, y, content, theme_name, size=size, weight=500,
                fill=fill or t["text_micro"], anchor=anchor,
                tracking=tracking, opacity=opacity, upper=upper,
                family=T.FONT_MONO if mono else T.FONT_DISPLAY)


def scale(size_key: str, density: float = 1.0) -> float:
    """The only sanctioned way to get a font size."""
    return T.TYPE_SCALE[size_key] * density


# --------------------------------------------------------------------------
# document scaffold
# --------------------------------------------------------------------------
def document(width: int, height: int, title: str, desc: str,
             theme_name: str, extra_defs: str = "",
             background: bool = True) -> str:
    """Open an SVG with its accessible name and opaque ground.

    Two non-negotiables are enforced here rather than trusted to each caller:

    1. <title> and <desc> always exist. An image with no accessible name is
       announced as "image" and conveys nothing.
    2. The canvas is opaque. A transparent SVG inherits whatever the host page
       paints, which means the light variant on a dark theme would put dark ink
       on a dark page. Contrast would depend on someone else's CSS.
    """
    t = T.PALETTES[theme_name]
    head = (
        f'<svg xmlns="{SVG_NS}" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        f'aria-labelledby="art-title art-desc">'
        f'<title id="art-title">{esc(title)}</title>'
        f'<desc id="art-desc">{esc(desc)}</desc>'
        + extra_defs
        + (f'<rect x="0" y="0" width="{width}" height="{height}" fill="{t["canvas"]}"/>'
           if background else "")
    )
    return head


def close() -> str:
    return "</svg>"


def write(path, content: str) -> int:
    """Write a generated asset and report its size in bytes."""
    from pathlib import Path
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = content.encode("utf-8")
    path.write_bytes(data)
    return len(data)
