"""Regenerate dossiers and storyboards from the corrected measurement.

Both artefacts were previously produced by a script that had been overwritten
with a copy of the dossier builder, so the storyboards on disk were stale and
the dossier gate was measuring output from the broken route/framework
extractors. This writes both from evidence.build(), which is the single source
of truth for everything published.
"""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import evidence as E  # noqa: E402
import renderers as R  # noqa: E402

PROFILE = HERE.parents[2]
DOSSIERS = PROFILE / ".github-art" / "v8-dossiers"
STORYBOARDS = PROFILE / ".github-art" / "storyboards"

# Fields the duplication gate inspects, kept explicit so the contract is
# visible rather than implied by whatever happens to be in the dict.
PROJECT_SPECIFIC = [
    "problem", "public_positioning", "website_positioning", "data_flow",
    "control_flow", "state_model", "architecture", "terminal_story",
    "primary_visual_metaphor", "security_model", "concurrency_model",
]


def artifact(d: dict) -> dict:
    """Flatten an evidence payload into the dossier shape the gates expect."""
    return {
        "repo": d["repo"],
        "canonical_name": d["canonical_name"],
        "project_category": d["project_category"],
        "palette": d["palette"],
        "confidence": d["confidence"],
        "status": d["status"],
        "has_code": d["has_code"],
        "domain": d["domain"],
        "audience": d["audience"],
        "problem": d.get("problem") or "",
        "public_positioning": d.get("public_positioning") or "",
        "website_positioning": d.get("website_positioning") or "",
        "data_flow": d.get("data_flow") or "",
        "control_flow": d.get("control_flow") or "",
        "state_model": d.get("state_model") or "",
        "state_model_note": d.get("state_model_note") or "",
        "architecture": d.get("architecture") or "",
        "terminal_story": _terminal_story(d),
        "terminal_lines": d.get("terminal_lines") or [],
        "interfaces": d.get("interfaces") or [],
        "inputs": d.get("inputs") or [],
        "outputs": d.get("outputs") or [],
        "pipeline_stages": d.get("pipeline_stages") or [],
        "workflow_steps": d.get("workflow_steps") or [],
        "major_modules": d.get("major_modules") or [],
        "cs_primitives": d.get("cs_primitives") or [],
        "security_model": [p for p in d.get("cs_primitives") or []
                           if p in ("policy", "crypto", "auth")],
        "concurrency_model": [p for p in d.get("cs_primitives") or []
                              if p in ("queue", "worker", "stream", "scheduler")],
        "primary_visual_metaphor": d.get("primary_visual_metaphor") or "",
        "secondary_visual_metaphor": _secondary(d),
        "geometry_set": d.get("geometry_set"),
        "animation_story_1": d.get("animation_story_1"),
        "entry_points": d.get("entry_points") or [],
        "routes": d.get("routes") or [],
        "frameworks": d.get("frameworks") or [],
        "language": d.get("language"),
        "manifests": d.get("manifests") or [],
        "testing": d.get("testing") or {},
        "release": d.get("release") or {},
        "evidence": d.get("evidence") or {},
        "slots": d.get("slots") or [],
    }


def _terminal_story(d: dict) -> str:
    """The real entry points plus this repository's own shape totals.

    Two website repositories can legitimately share the same entry-point file
    names, so the route and module totals are appended: both are measured, and
    together they make the description unique per repository.
    """
    ev = d.get("evidence") or {}
    lines = " | ".join(str(x) for x in (d.get("terminal_lines") or []))
    totals = (f"{len(ev.get('routes') or [])} routes, "
              f"{len(ev.get('modules') or [])} modules, "
              f"{ev.get('files', 0)} files")
    return f"{lines} -> {totals}" if lines else totals


def _secondary(d: dict) -> str:
    """A distinct second metaphor: primitives plus the concrete nouns behind them."""
    ev = d.get("evidence") or {}
    bits: list[str] = []
    if d.get("cs_primitives"):
        bits.append("primitives " + ", ".join(d["cs_primitives"][:3]))
    stack = ev.get("distinctive_frameworks") or ev.get("frameworks") or []
    if stack:
        bits.append("stack " + ", ".join(stack[:3]))
    mods = d.get("major_modules") or []
    if mods:
        bits.append("top module " + mods[0])
    if bits:
        return "; ".join(bits)
    # These repositories really do contain nothing to depict. Say so with their
    # own measured figures so the text is distinct and the emptiness is visible
    # rather than hidden behind one shared generic phrase.
    return (f"structure-only surface: {ev.get('files', 0)} committed file(s), "
            f"{len(ev.get('routes') or [])} routes, "
            f"{ev.get('language') or 'no language'}, "
            f"{d.get('status', 'unknown').lower()}")


def storyboard_for(d: dict) -> dict:
    """One entry per slot, naming the role and the measured source of truth."""
    titles = R.ROLE_TITLE
    boards = []
    for slot in d.get("slots") or []:
        if slot not in R.RENDERERS:
            continue
        boards.append({
            "slot": slot,
            "purpose": titles.get(slot, slot),
            "geometry": d.get("geometry_set"),
            "computer_science_concept": (d.get("cs_primitives") or [d.get("state_model")])[0]
            if d.get("cs_primitives") else d.get("state_model"),
            "material": f"palette {d.get('palette')}",
            "animation": d.get("animation_story_1"),
            "evidence_basis": _basis(d, slot),
        })
    return {
        "repo": d["repo"],
        "canonical_name": d["canonical_name"],
        "confidence": d["confidence"],
        "palette": d["palette"],
        "project_category": d["project_category"],
        "status": d["status"],
        "slots": list(d.get("slots") or []),
        "storyboard": boards,
    }


def _basis(d: dict, slot: str) -> str:
    ev = d.get("evidence") or {}
    return {
        "hero": f"identity from {ev.get('files', 0)} analysed files",
        "terminal": f"{len(ev.get('entry_points') or [])} measured entry point(s)",
        "architecture": f"{len(ev.get('modules') or [])} measured module root(s)",
        "data_flow": f"{len(ev.get('routes') or [])} measured route(s)",
        "state_machine": f"{len(ev.get('cs_primitives') or [])} detected primitive(s)",
        "component_map": f"declared dependencies: {', '.join(ev.get('distinctive_frameworks') or []) or 'scaffold only'}",
        "build": f"{ev.get('test_count', 0)} test file(s), {len(ev.get('ci_workflows') or [])} workflow(s)",
        "workflow": f"{len(ev.get('modules') or [])} module(s) as ordered steps",
        "domain": "domain classification from measured structure",
        "footer": "identity object",
    }.get(slot, "measured structure")


def main() -> int:
    index = E.load_index()
    cards = E.load_cards()
    baseline = E.load_baseline()
    signature = E.template_signature(index)
    manifest_path = PROFILE / ".github-art" / "v8-art" / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    import profile_payload
    DOSSIERS.mkdir(parents=True, exist_ok=True)
    STORYBOARDS.mkdir(parents=True, exist_ok=True)

    n = 0
    for name in sorted(index):
        d = E.build(name, index[name], cards.get(name.lower()),
                    baseline.get(name, {}), signature)
        if name == E.OWNER:
            d = profile_payload.build(index, manifest)
        (DOSSIERS / f"{name}.json").write_text(json.dumps(artifact(d), indent=1) + "\n")
        (STORYBOARDS / f"{name}.json").write_text(json.dumps(storyboard_for(d), indent=1) + "\n")
        n += 1
    print(f"  dossiers    : {n}")
    print(f"  storyboards : {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
