"""Computational materials.

A material is a recipe that resolves to concrete SVG defs for one theme. That
indirection is the point: geometry asks for ``deep_glass`` and gets the right
gradients, specular edges, and internal structure for obsidian or pearl without
knowing which palette it is drawing into.

Materials carry meaning. The mapping in ``tokens.MATERIAL_ROLE`` binds them to
layers, and ``role_for_material`` is how a generator asks the right question.
"""
from __future__ import annotations

from . import tokens as T


def _uid(theme: str, material: str, suffix: str = "") -> str:
    return f"m-{material}-{theme}{suffix}"


def definitions(theme_name: str, material: str) -> str:
    """Return the <defs> content for a material in a theme.

    Every material gets: an interior gradient, a lit top edge, a shaded bottom
    edge, and at least one internal structure layer. Optical realism comes from
    those four together. Weight only the highlight and it reads as plastic;
    weight only the shade and it reads as a hole.
    """
    t = T.PALETTES[theme_name]
    uid = _uid(theme_name, material)

    body_hi = t["glass_hi"]
    body = t["glass"]
    body_lo = t["glass_lo"]

    edge_top = t["edge_specular"]
    edge_mid = t["edge"]
    edge_low = t["edge"]

    # Material-specific interior character.
    interior = {
        "optical_glass": _optical_interior(t, uid),
        "spectral_glass": _spectral_interior(t, uid),
        "deep_glass": _deep_interior(t, uid),
        "obsidian_compute": _obsidian_interior(t, uid),
        "luminous_ceramic": _ceramic_interior(t, uid),
        "liquid_crystal": _crystal_interior(t, uid),
        "computational_material": _computational_interior(t, uid),
    }[material]

    spectral_ramp = (
        f'<linearGradient id="{uid}-prism" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{t["mint"]}"/>'
        f'<stop offset="52%" stop-color="{t["indigo"]}"/>'
        f'<stop offset="100%" stop-color="{t["violet"]}"/></linearGradient>'
    )
    edge_grad = (
        f'<linearGradient id="{uid}-edge" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{edge_top}" stop-opacity="0.85"/>'
        f'<stop offset="40%" stop-color="{edge_mid}" stop-opacity="1"/>'
        f'<stop offset="100%" stop-color="{edge_low}" stop-opacity="1"/>'
        f'</linearGradient>'
    )
    body_grad = (
        f'<linearGradient id="{uid}-body" x1="0.08" y1="0" x2="0.92" y2="1">'
        f'<stop offset="0%" stop-color="{body_hi}" stop-opacity="0.95"/>'
        f'<stop offset="52%" stop-color="{body}" stop-opacity="0.88"/>'
        f'<stop offset="100%" stop-color="{body_lo}" stop-opacity="0.92"/>'
        f'</linearGradient>'
    )

    return (
        f'<defs>{spectral_ramp}{edge_grad}{body_grad}{interior}</defs>'
    )


# --------------------------------------------------------------------------
# interiors - the part that makes each material a different substance
# --------------------------------------------------------------------------
def _optical_interior(t, uid):
    """Clear dimensional surface: one soft internal bloom, nothing else."""
    return (
        f'<radialGradient id="{uid}-core" cx="0.3" cy="0.12" r="0.9">'
        f'<stop offset="0%" stop-color="{t["edge_specular"]}" stop-opacity="0.20"/>'
        f'<stop offset="100%" stop-color="{t["glass_lo"]}" stop-opacity="0"/>'
        f'</radialGradient>'
    )


def _spectral_interior(t, uid):
    """Controlled edge iridescence: a narrow refracted band, not a rainbow wash."""
    return (
        f'<linearGradient id="{uid}-core" x1="0" y1="0" x2="1" y2="0.3">'
        f'<stop offset="0%" stop-color="{t["mint"]}" stop-opacity="0.00"/>'
        f'<stop offset="38%" stop-color="{t["mint"]}" stop-opacity="0.16"/>'
        f'<stop offset="62%" stop-color="{t["indigo"]}" stop-opacity="0.14"/>'
        f'<stop offset="100%" stop-color="{t["violet"]}" stop-opacity="0.00"/>'
        f'</linearGradient>'
    )


def _deep_interior(t, uid):
    """Appears to contain internal space: a receding well with its own floor."""
    return (
        f'<radialGradient id="{uid}-core" cx="0.5" cy="0.0" r="1.0">'
        f'<stop offset="0%" stop-color="{t["canvas_deep"]}" stop-opacity="0.85"/>'
        f'<stop offset="55%" stop-color="{t["glass_lo"]}" stop-opacity="0.35"/>'
        f'<stop offset="100%" stop-color="{t["edge_specular"]}" stop-opacity="0.10"/>'
        f'</radialGradient>'
        f'<linearGradient id="{uid}-floor" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{t["mint"]}" stop-opacity="0"/>'
        f'<stop offset="100%" stop-color="{t["mint"]}" stop-opacity="0.10"/>'
        f'</linearGradient>'
    )


def _obsidian_interior(t, uid):
    """Dark surface with precision highlights: near-black, hard specular line."""
    return (
        f'<linearGradient id="{uid}-core" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{t["canvas_deep"]}" stop-opacity="0.96"/>'
        f'<stop offset="70%" stop-color="{t["glass_lo"]}" stop-opacity="0.90"/>'
        f'<stop offset="100%" stop-color="{t["canvas"]}" stop-opacity="0.94"/>'
        f'</linearGradient>'
        f'<linearGradient id="{uid}-bevel" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{t["edge_specular"]}" stop-opacity="0.30"/>'
        f'<stop offset="100%" stop-color="{t["edge_specular"]}" stop-opacity="0"/>'
        f'</linearGradient>'
    )


def _ceramic_interior(t, uid):
    """Soft matte with internal illumination: low contrast, wide, gentle."""
    return (
        f'<radialGradient id="{uid}-core" cx="0.5" cy="1.0" r="1.1">'
        f'<stop offset="0%" stop-color="{t["indigo"]}" stop-opacity="0.10"/>'
        f'<stop offset="60%" stop-color="{t["glass_hi"]}" stop-opacity="0.30"/>'
        f'<stop offset="100%" stop-color="{t["glass"]}" stop-opacity="0"/>'
        f'</radialGradient>'
    )


def _crystal_interior(t, uid):
    """Very subtle structured interference: fine parallel banding."""
    return (
        f'<pattern id="{uid}-lattice" width="6" height="6" patternUnits="userSpaceOnUse" '
        f'patternTransform="rotate(24)">'
        f'<rect width="6" height="6" fill="none"/>'
        f'<line x1="0" y1="0" x2="0" y2="6" stroke="{t["indigo"]}" '
        f'stroke-width="0.5" stroke-opacity="0.10"/>'
        f'</pattern>'
        f'<linearGradient id="{uid}-core" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{t["violet"]}" stop-opacity="0.07"/>'
        f'<stop offset="100%" stop-color="{t["mint"]}" stop-opacity="0.07"/>'
        f'</linearGradient>'
    )


def _computational_interior(t, uid):
    """Surface texture reflects state: a measured grid, not noise."""
    return (
        f'<pattern id="{uid}-measure" width="16" height="16" patternUnits="userSpaceOnUse">'
        f'<path d="M16 0 L0 0 0 16" fill="none" stroke="{t["edge"]}" '
        f'stroke-width="0.75" stroke-opacity="0.55"/>'
        f'<circle cx="0" cy="0" r="1" fill="{t["mint"]}" fill-opacity="0.35"/>'
        f'</pattern>'
        f'<linearGradient id="{uid}-core" x1="0" y1="0" x2="0.8" y2="1">'
        f'<stop offset="0%" stop-color="{t["mint"]}" stop-opacity="0.06"/>'
        f'<stop offset="100%" stop-color="{t["violet"]}" stop-opacity="0.09"/>'
        f'</linearGradient>'
    )


# --------------------------------------------------------------------------
# use
# --------------------------------------------------------------------------
def body_fill(theme_name: str, material: str) -> str:
    return f"url(#{_uid(theme_name, material)}-body)"


def edge_fill(theme_name: str, material: str) -> str:
    return f"url(#{_uid(theme_name, material)}-edge)"


def core_fill(theme_name: str, material: str) -> str:
    return f"url(#{_uid(theme_name, material)}-core)"


def prism_fill(theme_name: str, material: str) -> str:
    return f"url(#{_uid(theme_name, material)}-prism)"


def role_for_material(material: str) -> str:
    """The semantic layer a material is allowed to represent."""
    if material not in T.MATERIAL_ROLE:
        raise KeyError(f"unknown material {material!r}; expected one of {T.MATERIALS}")
    return T.MATERIAL_ROLE[material][0]


def material_for_role(role: str) -> str:
    """Inverse of role_for_material, used when a generator thinks in layers."""
    for material, (assigned, _why) in T.MATERIAL_ROLE.items():
        if assigned == role:
            return material
    return "optical_glass"
