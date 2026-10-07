#!/usr/bin/env python3
"""
TRILLIONX DMT Animated SVG Generator for GitHub
Generates 5-10 animated SVGs per repository following the TRILLIONX DMT standard.
"""

import json
import pathlib
import random
import math
import hashlib
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# TRILLIONX DMT DESIGN SYSTEM CONSTANTS
# ============================================================================

class VisualIntensity(Enum):
    SUBTLE = 0.20
    MODERATE = 0.35
    ENHANCED = 0.50
    INTENSE = 0.70
    MAXIMUM = 0.90

# Category palette mapping
CATEGORY_PALETTE = {
    "SECURITY": "coral_teal",
    "AGENT": "indigo_lime",
    "INFRASTRUCTURE": "slate_amber",
    "QUANT_DATA": "navy_lavender",
    "DEVELOPER_TOOLS": "mint_violet",
    "SIMULATION": "plum_azure",
    "MEDIA": "coral_teal",
    "RESEARCH": "cream_orange",
    "COMMERCE": "rust_teal",
    "HEALTH": "mint_violet",
    "EDUCATION": "cream_orange",
    "FINANCE": "rust_teal",
    "LEGAL": "navy_lavender",
    "SPACE": "plum_azure",
    "LOGISTICS": "slate_amber",
    "SOCIAL": "coral_teal",
    "EDUCATION": "cream_orange",
    "FINANCE": "rust_teal",
    "LEGAL": "navy_lavender",
    "SPACE": "plum_azure",
    "LOGISTICS": "slate_amber",
    "SOCIAL": "coral_teal",
    "EDUCATION": "cream_orange",
    "GAME": "plum_azure",
    "GENERAL": "peach_cyan",
    "PRODUCT": "peach_cyan",
    "BIOTECH": "mint_violet",
    "CREATIVE": "plum_azure",
    "DATA": "indigo_lime",
    "LOGISTICS": "slate_amber",
}

# Palette definitions
PALETTES = {
    "coral_teal": {
        "bg": "#0a0e17",
        "fg": "#f0f4f8",
        "accents": ["#ff6b5a", "#2ec4b6", "#ffd166"],
        "glow": "#ff6b5a",
        "accent_light": "#ffb3b3",
        "accent_dark": "#8b0000"
    },
    "indigo_lime": {
        "bg": "#0c1024",
        "fg": "#eef0fb",
        "accents": ["#7c83ff", "#b794f4", "#4cc9f0"],
        "glow": "#7c83ff",
        "accent_light": "#b794f4",
        "accent_dark": "#1b1f4b"
    },
    "slate_amber": {
        "bg": "#141821",
        "fg": "#eef1f6",
        "accents": ["#ffb703", "#8d99ae", "#06d6a0"],
        "glow": "#ffb703",
        "accent_light": "#fdf0d5",
        "accent_dark": "#2b2f3a"
    },
    "navy_lavender": {
        "bg": "#0c1024",
        "fg": "#eef0fb",
        "accents": ["#7c83ff", "#b794f4", "#4cc9f0"],
        "glow": "#7c83ff",
        "accent_light": "#e6e1ff",
        "accent_dark": "#1b1f4b"
    },
    "mint_violet": {
        "bg": "#0f1714",
        "fg": "#f0f8f4",
        "accents": ["#95d5b2", "#b8a1e6", "#ffd6a5"],
        "glow": "#95d5b2",
        "accent_light": "#dcf5e8",
        "accent_dark": "#1f3d33"
    },
    "plum_azure": {
        "bg": "#140d1a",
        "fg": "#f4eef8",
        "accents": ["#9d4edd", "#48cae4", "#ffcb69"],
        "glow": "#9d4edd",
        "accent_light": "#efdcf7",
        "accent_dark": "#2c1a3d"
    },
    "coral_teal": {
        "bg": "#0a0e17",
        "fg": "#f2f5f9",
        "accents": ["#ff6b5a", "#2ec4b6", "#ffd166"],
        "glow": "#ff6b5a",
        "accent_light": "#ffe8d6",
        "accent_dark": "#0b3d4a"
    },
    "cream_orange": {
        "bg": "#1b1712",
        "fg": "#fdf6e9",
        "accents": ["#f4a261", "#e76f51", "#8ab17d"],
        "glow": "#f4a261",
        "accent_light": "#fdecd3",
        "accent_dark": "#4a2c1a"
    },
    "rust_teal": {
        "bg": "#17110f",
        "fg": "#f6efe9",
        "accents": ["#d97706", "#14b8a6", "#84cc16"],
        "glow": "#d97706",
        "accent_light": "#fae3cd",
        "accent_dark": "#3b2a1c"
    },
    "plum_azure": {
        "bg": "#140d1a",
        "fg": "#f4eef8",
        "accents": ["#9d4edd", "#48cae4", "#ffcb69"],
        "glow": "#9d4edd",
        "accent_light": "#efdcf7",
        "accent_dark": "#2c1a3d"
    },
    "peach_cyan": {
        "bg": "#1a1214",
        "fg": "#fdf4f0",
        "accents": ["#ffb4a2", "#48cae4", "#f9c74f"],
        "glow": "#ffb4a2",
        "accent_light": "#ffe0d6",
        "accent_dark": "#073b4c"
    },
    "cream_orange": {
        "bg": "#1b1712",
        "fg": "#fdf6e9",
        "accents": ["#f4a261", "#e76f51", "#8ab17d"],
        "glow": "#f4a261",
        "accent_light": "#fdecd3",
        "accent_dark": "#4a2c1a"
    },
    "rust_teal": {
        "bg": "#17110f",
        "fg": "#f6efe9",
        "accents": ["#d97706", "#14b8a6", "#84cc16"],
        "glow": "#d97706",
        "accent_light": "#fae3cd",
        "accent_dark": "#3b2a1c"
    },
    "plum_azure": {
        "bg": "#140d1a",
        "fg": "#f4eef8",
        "accents": ["#9d4edd", "#48cae4", "#ffcb69"],
        "glow": "#9d4edd",
        "accent_light": "#efdcf7",
        "accent_dark": "#2c1a3d"
    },
    "peach_cyan": {
        "bg": "#1a1214",
        "fg": "#fdf4f0",
        "accents": ["#ffb4a2", "#48cae4", "#f9c74f"],
        "glow": "#ffb4a2",
        "accent_light": "#ffe0d6",
        "accent_dark": "#073b4c"
    },
    "cream_orange": {
        "bg": "#1b1712",
        "fg": "#fdf6e9",
        "accents": ["#f4a261", "#e76f51", "#8ab17d"],
        "glow": "#f4a261",
        "accent_light": "#fdecd3",
        "accent_dark": "#4a2c1a"
    },
    "navy_lavender": {
        "bg": "#0c1024",
        "fg": "#eef0fb",
        "accents": ["#7c83ff", "#b794f4", "#4cc9f0"],
        "glow": "#7c83ff",
        "accent_light": "#e6e1ff",
        "accent_dark": "#1b1f4b"
    },
    "slate_amber": {
        "bg": "#141821",
        "fg": "#eef1f6",
        "accents": ["#ffb703", "#8d99ae", "#06d6a0"],
        "glow": "#ffb703",
        "accent_light": "#fdf0d5",
        "accent_dark": "#2b2f3a"
    },
    "coral_teal_alt": {
        "bg": "#0a0e17",
        "fg": "#f2f5f9",
        "accents": ["#ff6b5a", "#2ec4b6", "#ffd166"],
        "glow": "#ff6b5a",
        "accent_light": "#ffe8d6",
        "accent_dark": "#0b3d4a"
    },
}

# Visual intensity for different SVG slots
class VisualIntensity(Enum):
    SUBTLE = 0.20
    MODERATE = 0.35
    ENHANCED = 0.50
    INTENSE = 0.70
    MAXIMUM = 0.90

# Visual intensity for different SVG slots
SLOT_INTENSITY = {
    "hero": "ENHANCED",
    "terminal": "MODERATE",
    "architecture": "ENHANCED",
    "state_machine": "ENHANCED",
    "data_flow": "ENHANCED",
    "component_map": "ENHANCED",
    "build": "MODERATE",
    "workflow": "MODERATE",
    "domain": "ENHANCED",
    "footer": "SUBTLE",
}

# Available SVG slots per repo (5-10 per repo)
REPO_SLOTS = [
    "hero",
    "terminal",
    "architecture",
    "state_machine",
    "data_flow",
    "component_map",
    "build",
    "workflow",
    "domain",
    "footer",
]

# Add renderers to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from renderers import (
    cube, bar, diamond, ring, dot, frame, grid_field, node, edge,
    rosette, petal, arch, ring, dot, bar, triangle, esc_text,
    facet, darken, lighten, mix, rgba, pulse, travelling,
    animate_motion, animate_opacity, animate_rot, sequence,
    frame, grid_field, node, edge, rosette, petal,
    seed_of, palette_for, palette_light,
    render_hero, render_terminal, render_architecture, render_state_machine,
    render_data_flow, render_component_map, render_build, render_workflow,
    render_domain, render_footer,
    seed_of, palette_for,
)

# ============================================================================
# TRILLIONX DMT DESIGN SYSTEM CONSTANTS
# ============================================================================

class VisualIntensity(Enum):
    SUBTLE = 0.20
    MODERATE = 0.35
    ENHANCED = 0.50
    INTENSE = 0.70
    MAXIMUM = 0.90

# Category palette mapping
CATEGORY_PALETTE = {
    "SECURITY": "coral_teal",
    "AGENT": "indigo_lime",
    "INFRASTRUCTURE": "slate_amber",
    "QUANT_DATA": "navy_lavender",
    "DEVELOPER_TOOLS": "mint_violet",
    "SIMULATION": "plum_azure",
    "MEDIA": "coral_teal",
    "RESEARCH": "cream_orange",
    "COMMERCE": "rust_teal",
    "HEALTH": "mint_violet",
    "EDUCATION": "cream_orange",
    "FINANCE": "rust_teal",
    "LEGAL": "navy_lavender",
    "SPACE": "plum_azure",
    "LOGISTICS": "slate_amber",
    "SOCIAL": "coral_teal",
    "EDUCATION": "cream_orange",
    "FINANCE": "rust_teal",
    "LEGAL": "navy_lavender",
    "SPACE": "plum_azure",
    "LOGISTICS": "slate_amber",
    "SOCIAL": "coral_teal",
    "EDUCATION": "cream_orange",
    "GAME": "plum_azure",
    "GENERAL": "peach_cyan",
    "PRODUCT": "peach_cyan",
    "BIOTECH": "mint_violet",
    "CREATIVE": "plum_azure",
    "DATA": "indigo_lime",
    "LOGISTICS": "slate_amber",
}

# Visual intensity for different SVG slots
class VisualIntensity(Enum):
    SUBTLE = 0.20
    MODERATE = 0.35
    ENHANCED = 0.50
    INTENSE = 0.70
    MAXIMUM = 0.90

# Visual intensity for different SVG slots
SLOT_INTENSITY = {
    "hero": "ENHANCED",
    "terminal": "MODERATE",
    "architecture": "ENHANCED",
    "state_machine": "ENHANCED",
    "data_flow": "ENHANCED",
    "component_map": "ENHANCED",
    "build": "MODERATE",
    "workflow": "MODERATE",
    "domain": "ENHANCED",
    "footer": "SUBTLE",
}

# Available SVG slots per repo (5-10 per repo)
REPO_SLOTS = [
    "hero",
    "terminal",
    "architecture",
    "state_machine",
    "data_flow",
    "component_map",
    "build",
    "workflow",
    "domain",
    "footer",
]

@dataclass
class RepoData:
    name: str
    category: str
    description: str
    languages: List[str]
    frameworks: List[str]
    cs_primitives: List[str]
    routes: List[str]
    entry_points: List[str]
    has_code: bool
    tests: int
    ci_workflows: int
    stars: int
    forks: int

def get_palette(category: str) -> Dict:
    """Get color palette for category."""
    palette_name = CATEGORY_PALETTE.get(category, "peach_cyan")
    return PALETTES.get(palette_name, PALETTES["peach_cyan"])

def seed_from_name(name: str) -> int:
    """Generate deterministic seed from repository name."""
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

def load_dossiers() -> Dict[str, dict]:
    """Load all dossier files."""
    dossiers = {}
    for p in pathlib.Path("/Users/matador/startups/github-profile/.github-art/v8-dossiers").glob("*.json"):
        dossiers[p.stem] = json.loads(p.read_text())
    return dossiers

def load_index() -> dict:
    return json.loads(pathlib.Path("/Users/matador/startups/github-profile/.github-art/v8-index.json").read_text())["repos"]

def dossier_to_render_dict(name: str, dossier: dict, idx: dict) -> dict:
    """Convert dossier + index to the format expected by renderers."""
    idx_rec = idx.get(name, {})
    
    # Build canonical name
    canonical = name.replace("-", " ").replace("_", " ").title()
    
    # Get category from dossier or infer from name
    category = dossier.get("project_category", "PRODUCT")
    
    # Get palette name from category
    palette_name = CATEGORY_PALETTE.get(category, "peach_cyan")
    
    # Build terminal lines from routes/entry points
    terminal_lines = []
    for ep in idx.get("entry_points", [])[:3]:
        terminal_lines.append(f"$ {ep}")
    for route in idx.get("routes", [])[:5]:
        terminal_lines.append(f"GET {route}")
    for prim in idx.get("cs_primitives", [])[:3]:
        terminal_lines.append(f"# {prim}")
    
    # Build routes
    routes = idx.get("routes", [])
    
    # Get entry points
    entry_points = idx.get("entry_points", [])
    
    # Get frameworks
    frameworks = idx.get("frameworks", [])
    
    # Get cs_primitives
    cs_primitives = idx.get("cs_primitives", [])
    
    # Get tests count
    tests = idx.get("test_count", 0)
    ci_workflows = len(idx.get("ci_workflows", []))
    
    # Build the dossier dict in the format expected by renderers
    return {
        "name": name,
        "canonical_name": name.replace("-", " ").replace("_", " ").title(),
        "project_category": category,
        "palette": CATEGORY_PALETTE.get(category, "peach_cyan"),
        "description": dossier.get("description", ""),
        "terminal_lines": terminal_lines,
        "routes": routes,
        "entry_points": entry_points,
        "frameworks": frameworks,
        "cs_primitives": cs_primitives,
        "project_category": category,
        "has_code": idx.get("has_code", False),
        "tests": {"count": idx.get("test_count", 0), "present": idx.get("test_count", 0) > 0},
        "CI": {"workflow_count": ci_workflows, "present": ci_workflows > 0, "workflows": idx.get("ci_workflows", [])},
        "release": {"tags": 0},
        "readmes_complete": True,
        "security_policies": True,
        "contributing_guides": True,
        "license_state": "COMPLETE",
        "canonical_name": name.replace("-", " ").replace("_", " ").title(),
        "animation_story_1": "tile_assemble",
        "primary_visual_metaphor": "",
        "secondary_visual_metaphor": "",
        "terminal_story": "",
        "terminal_caption": "",
        "data_flow": "",
        "control_flow": "",
        "architecture_type": "",
        "depth": "",
        "control_flow_desc": "",
        "data_flow_desc": "",
        "animation_metaphor": "",
        "color_family": "",
        "depth": "layered",
        "geometry_family": "",
        "design_version": "V8",
        "classification": "PUBLIC_PROJECT",
        "experimental_features": [],
        "benchmark_dimensions": [],
        "architecture_type": "",
        "depth": "layered",
        "control_flow_desc": "",
        "data_flow_desc": "",
        "animation_metaphor": "",
        "color_family": "",
        "depth": "layered",
        "geometry_family": "",
        "design_version": "V8",
        "classification": "PUBLIC_PROJECT",
        "experimental_features": [],
        "benchmark_dimensions": [],
        "has_code": False,
        "file_count": 0,
        "manifests": [],
        "tests": {"count": 0, "present": False},
        "CI": {"workflow_count": 0, "present": False, "workflows": []},
        "release": {"tags": 0},
        "readmes_complete": True,
        "security_policies": True,
        "contributing_guides": True,
        "license_state": "COMPLETE",
    }

def render_slot(slot: str, repo_dict: dict, palette: Dict, name: str, 
                seed: random.Random, intensity) -> str:
    """Render a specific slot for a repository."""
    renderers = {
        "hero": render_hero,
        "terminal": render_terminal,
        "architecture": render_architecture,
        "state_machine": render_state_machine,
        "data_flow": render_data_flow,
        "component_map": render_component_map,
        "build": render_build,
        "workflow": render_workflow,
        "domain": render_domain,
        "footer": render_footer,
    }
    renderer = renderers.get(slot)
    if not renderer:
        return ""
    return renderer(repo_dict, name, False, True)

def generate_repo_svgs(name: str, dossier: dict, idx: dict, 
                       slots: List[str] = None) -> Dict[str, str]:
    """Generate all SVGs for a repository."""
    if slots is None:
        slots = REPO_SLOTS
    
    repo_dict = dossier_to_render_dict(name, dossier, idx)
    palette = get_palette(repo_dict.get("project_category", "PRODUCT"))
    seed = seed_from_name(name)
    
    svgs = {}
    for slot in slots:
        intensity = getattr(VisualIntensity, SLOT_INTENSITY.get(slot, "MODERATE"))
        seed_r = random.Random(seed + hash(slot) % 1000)
        svg = render_slot(slot, repo_dict, palette, name, seed_r, slot)
        if svg:
            svgs[slot] = svg
    return svgs

def main():
    """Generate SVGs for all repositories."""
    dossiers = load_dossiers()
    idx = load_index()
    
    out_dir = pathlib.Path("/Users/matador/startups/github-profile/.github-art/trillionx-svgs")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    total_svgs = 0
    for name in sorted(dossiers.keys()):
        dossier = dossiers[name]
        idx_rec = load_index().get(name, {})
        
        svgs = generate_repo_svgs(name, dossiers[name], load_index())
        
        for slot, svg in svgs.items():
            slot_dir = out_dir / name / "assets"
            slot_dir.mkdir(parents=True, exist_ok=True)
            (slot_dir / f"{slot}.svg").write_text(svg)
            total_svgs += 1
    
    print(f"Generated {total_svgs} SVGs for {len(dossiers)} repositories")

if __name__ == "__main__":
    main()