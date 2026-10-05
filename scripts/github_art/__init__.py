"""DUNG30N5 x NOAERTH hyperreal computational design system.

Layering is deliberate and one-directional:

    tokens      every literal value, and the only place one may appear
    materials   substance recipes, resolved per theme
    geometry    primitives that encode meaning
    typography  type and the document scaffold
    project_identity  per-system marks derived from the primitives
    validators  checks that run during generation, not after
    generators  the artefacts
    directions  competing visual directions, scored before rollout

Nothing below this package may hardcode a colour, radius, size, or duration.
"""
