"""Validators.

These run as part of generation, not as an optional later pass. An artwork
system that can emit an invalid file is a system that will eventually ship one.

Each check exists because the corresponding failure is silent: the SVG still
renders, the page still loads, and the defect is only visible to someone who
looks closely or uses assistive technology.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from . import tokens as T

SVG_NS = "{http://www.w3.org/2000/svg}"
ANIMATION_TAGS = {"animate", "animateTransform", "animateMotion", "set"}

RESOURCE_REF = re.compile(r'(?:xlink:)?href\s*=\s*"([^"]*)"|url\(\s*([^)]*)\)', re.I)
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _lin(channel: float) -> float:
    channel /= 255
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


class ValidationError(AssertionError):
    pass


def check_parses(content: str, name: str = "") -> None:
    try:
        ET.fromstring(content)
    except ET.ParseError as exc:
        raise ValidationError(f"{name}: XML does not parse: {exc}") from exc


def check_orphan_animation(content: str, name: str = "") -> None:
    """SMIL must be a child of the element it targets.

    An orphaned <animate> parses cleanly, renders nothing, and reports no
    error anywhere. This exact defect shipped once: a string-replace looked for
    a y-coordinate that had moved, missed silently, and left the caret blinking
    in nobody's browser.
    """
    root = ET.fromstring(content)
    orphans = []

    def walk(node, parent):
        tag = node.tag.replace(SVG_NS, "")
        if tag in ANIMATION_TAGS:
            parent_tag = parent.tag.replace(SVG_NS, "") if parent is not None else ""
            if parent is None or parent_tag in ANIMATION_TAGS | {"defs", "svg"}:
                orphans.append(f"<{tag}> under <{parent_tag or 'none'}>")
        for child in node:
            walk(child, node)

    for child in root:
        walk(child, root)
    if orphans:
        raise ValidationError(f"{name}: orphan animation: {', '.join(orphans)}")


def check_no_external_resources(content: str, name: str = "") -> None:
    """Nothing may be fetched. href and url() may only point inward."""
    offenders = []
    for match in RESOURCE_REF.finditer(content):
        value = (match.group(1) or match.group(2) or "").strip()
        if not value or value.startswith("#"):
            continue
        offenders.append(value[:60])
    if offenders:
        raise ValidationError(f"{name}: external resource reference: {offenders}")


def check_accessible_name(content: str, name: str = "") -> None:
    root = ET.fromstring(content)
    if root.find(f"{SVG_NS}title") is None:
        raise ValidationError(f"{name}: no <title>")
    if root.find(f"{SVG_NS}desc") is None:
        raise ValidationError(f"{name}: no <desc>")


def check_opaque_canvas(content: str, name: str = "") -> None:
    """The first painted rect must cover the viewBox opaquely.

    Without this, the light variant inherits the host page background and dark
    ink lands on a dark page.
    """
    root = ET.fromstring(content)
    view = root.get("viewBox", "").replace(",", " ").split()
    if len(view) != 4:
        raise ValidationError(f"{name}: missing or malformed viewBox")
    _, _, vw, vh = (float(v) for v in view)
    for node in root.iter(f"{SVG_NS}rect"):
        x = float(node.get("x", 0))
        y = float(node.get("y", 0))
        w = float(node.get("width", 0))
        h = float(node.get("height", 0))
        fill = node.get("fill", "")
        if x <= 0.5 and y <= 0.5 and w >= vw - 1 and h >= vh - 1 and fill != "none":
            return
    raise ValidationError(
        f"{name}: no opaque full-bleed background rect; contrast would depend on "
        f"the host page")


def check_text_contrast(content: str, name: str = "", threshold: float = 4.5) -> None:
    """Every text fill must clear AA against the background it is painted on."""
    canvas = re.search(
        r'<rect x="0(?:\.5)?" y="0(?:\.5)?"[^>]*fill="(#[0-9A-Fa-f]{6})"', content)
    if not canvas:
        return
    background = canvas.group(1)
    failures = []
    for fill in set(re.findall(r'<text[^>]*fill="(#[0-9A-Fa-f]{6})"', content)):
        ratio = contrast(fill, background)
        if ratio < threshold:
            failures.append(f"{fill} on {background} = {ratio:.2f}:1")
    if failures:
        raise ValidationError(f"{name}: text below AA: {failures}")


def check_budget(size_bytes: int, name: str = "", limit_kb: float | None = None) -> None:
    limit = limit_kb if limit_kb is not None else T.BUDGET["single_plate_kb"]
    kb = size_bytes / 1024
    if kb > limit:
        raise ValidationError(f"{name}: {kb:.1f}KB exceeds the {limit:.0f}KB budget")


def check_no_stray_literals(content: str, name: str = "",
                            allowed: set | None = None) -> None:
    """No hex colour may appear unless it is declared in tokens.py.

    This is the mechanism that makes "one token source" real rather than
    aspirational: a hardcoded colour in one SVG would otherwise spread and the
    palette would drift within a single release.
    """
    allowed = allowed if allowed is not None else declared_colours()
    stray = {c for c in HEX.findall(content) if c.upper() not in allowed}
    if stray:
        raise ValidationError(
            f"{name}: colours not declared in tokens.py: {sorted(stray)}")


def declared_colours() -> set:
    colours = set()
    for theme in T.PALETTES.values():
        for value in theme.values():
            if isinstance(value, str) and value.startswith("#"):
                colours.add(value.upper())
    colours.add(T.SPECTRAL_MINT.upper())
    colours.add(T.SPECTRAL_INDIGO.upper())
    colours.add(T.SPECTRAL_VIOLET.upper())
    return colours


def check_forbidden_vocabulary(content: str, name: str = "") -> None:
    """The internal design language must never appear in public output."""
    lowered = content.lower()
    hits = [w for w in T.FORBIDDEN_PUBLIC_VOCABULARY
            if re.search(rf"\b{re.escape(w)}\b", lowered)]
    if hits:
        raise ValidationError(f"{name}: internal vocabulary leaked: {hits}")


def validate(content: str, name: str = "", budget_kb: float | None = None) -> int:
    """Run every check. Returns the encoded size."""
    check_parses(content, name)
    check_orphan_animation(content, name)
    check_no_external_resources(content, name)
    check_accessible_name(content, name)
    check_opaque_canvas(content, name)
    check_text_contrast(content, name)
    check_no_stray_literals(content, name)
    check_forbidden_vocabulary(content, name)
    size = len(content.encode("utf-8"))
    check_budget(size, name, budget_kb)
    return size


def check_motion_is_ambient(content: str, name: str = "") -> None:
    """Nothing loops faster than 1s and nothing flashes."""
    for dur in re.findall(r'dur="([\d.]+)s"', content):
        seconds = float(dur)
        if seconds <= 0:
            raise ValidationError(f"{name}: non-positive duration")
        if seconds < 1.0:
            raise ValidationError(
                f"{name}: {seconds}s loop is faster than the 1s floor")
