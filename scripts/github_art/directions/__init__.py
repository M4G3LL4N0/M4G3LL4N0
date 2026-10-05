"""Competing visual directions, and the chosen synthesis.

Three directions were drawn and scored before anything was rolled out. Only
the winner is carried forward; the rejects stay importable here so the decision
is auditable, but they are never written into a public repository.
"""
from . import (a_optical_topology, b_deep_computational_glass,
               c_recursive_system_material, v5_optical_recursive)

DIRECTIONS = {
    a_optical_topology.SLUG: a_optical_topology,
    b_deep_computational_glass.SLUG: b_deep_computational_glass,
    c_recursive_system_material.SLUG: c_recursive_system_material,
}

CHOSEN = v5_optical_recursive

__all__ = ["DIRECTIONS", "CHOSEN"]
