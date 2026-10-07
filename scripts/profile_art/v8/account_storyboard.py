#!/usr/bin/env python3
"""Generate GITHUB_V8_ART_STORYBOARD.md.

One row per public owned repository: purpose, confidence, and the visual titles
with what each animation represents. This is the document that proves the round
was planned before it was executed -- the mass rollout in Part 2 reads from it
rather than inventing per repository.

It is also the duplication reference: two repositories with the same titles,
the same concepts and the same motion are visible here before any asset exists.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from geometry import MOTION  # noqa: E402

PROFILE = pathlib.Path(__file__).resolve().parents[3]
DOSSIERS = PROFILE / ".github-art" / "v8-dossiers"
STORYBOARDS = PROFILE / ".github-art" / "storyboards"
OUT = PROFILE / "GITHUB_V8_ART_STORYBOARD.md"

# The ten profile surfaces. Fixed by the brief, not derived per repository.
PROFILE_SURFACES = [
    ("DUNG30N5 hero", "the studio identity assembling from modular units",
     "tile_assemble", "isometric blocks + rosette"),
    ("computer-science terminal", "how the portfolio is operated and verified",
     "terminal_exec", "terminal frame + output tree"),
    ("public systems atlas", "every public repository as a node in one field",
     "graph_resolve", "node graph + containment edges"),
    ("build / test / release pipeline", "how the portfolio is verified",
     "test_progress", "stage arches + progress bars"),
    ("language and technology constellation", "the technical surface area",
     "dot_propagate", "constellation nodes + edges"),
    ("systems-architecture landscape", "the dominant architectural patterns",
     "plane_slide", "layered planes + module frames"),
    ("algorithms and data structures", "the computational structures present",
     "index_probe", "indexed field + probe path"),
    ("open-source and upstream activity", "release and commit evidence",
     "bar_sweep", "activity bars + timeline"),
    ("selected-project constellation", "the strongest repositories as a field",
     "tessellate", "tessellated tiles + identity objects"),
    ("why-are-you-here terminal", "the closing statement",
     "terminal_exec", "terminal frame + signature mark"),
]


def visual_title(slot: str, concept: str) -> str:
    """A title that says what the surface is, not just which slot it fills."""
    titles = {
        "hero": f"{concept} -- identity",
        "terminal": "command surface",
        "architecture": f"module graph: {concept}",
        "state_machine": f"state cycle: {concept}",
        "data_flow": f"data path: {concept}",
        "component_map": f"composition: {concept}",
        "build": f"verification: {concept}",
        "workflow": f"operating loop: {concept}",
        "domain": f"domain model: {concept}",
        "footer": "identity object",
    }
    return titles.get(slot, concept)


def main() -> int:
    names = sorted(p.stem for p in DOSSIERS.glob("*.json"))
    rows = []
    for n in names:
        d = json.loads((DOSSIERS / f"{n}.json").read_text())
        sb = json.loads((STORYBOARDS / f"{n}.json").read_text())
        rows.append((n, d, sb))

    conf = {"E3": 0, "E2": 0, "E1": 0}
    for _, d, _ in rows:
        conf[d["confidence"]] = conf.get(d["confidence"], 0) + 1

    lines = [
        "# GitHub V8 -- Account Art Storyboard",
        "",
        "Every public owned repository, its purpose, its confidence, and the five to ten",
        "animated surfaces it will receive. Written before any asset was generated so the",
        "rollout executes a plan instead of inventing per repository.",
        "",
        f"**{len(rows)} public repositories** &#183; confidence E3 {conf['E3']} / "
        f"E2 {conf['E2']} / E1 {conf['E1']}",
        "",
        "---",
        "",
        "## Profile -- ten major visual surfaces",
        "",
        "The account reads as one studio that has built many distinctly different systems,",
        "not as one README template applied a hundred and thirty times.",
        "",
        "| # | Surface | What it represents | Motion | Geometry |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i, (title, represents, motion, geom) in enumerate(PROFILE_SURFACES, 1):
        lines.append(f"| {i} | **{title}** | {represents} | "
                     f"{MOTION[motion]['desc']} ({MOTION[motion]['dur'][0]}\u2013"
                     f"{MOTION[motion]['dur'][1]}s) | {geom} |")

    lines += ["", "---", "", "## Public repositories", ""]

    for name, d, sb in rows:
        lines += [
            f"### `{name}`",
            "",
            f"**{d['canonical_name']}** &#183; {d['project_category'].replace('_', ' ').title()} "
            f"&#183; {d['confidence']} &#183; {d['status']}",
            "",
            f"{d['purpose']}",
            "",
            f"{sb['surface_count']} surfaces:",
            "",
        ]
        for e in sb["storyboard"]:
            title = visual_title(e["slot"], e["computer_science_concept"])
            lines.append(
                f"{e['slot']:<15} **{title}** &#8212; {e['computer_science_concept']}. "
                f"{e['animation'].split(';')[0]}. {e['geometry']}.")
        lines.append("")

    lines += [
        "---",
        "",
        "## How to read this",
        "",
        "Each surface reveals a different facet. The hero is identity, the terminal is",
        "operation, the architecture is construction, the state machine is behaviour, the",
        "build surface is verification. Five images that repeat one composition is a",
        "failure, so the duplication test compares geometry graph, motion vocabulary,",
        "layout, colour family, timing, terminal pattern and asset sequence across every",
        "pair of unrelated repositories.",
        "",
        "A repository with no CLI does not get a terminal surface. A repository with no",
        "tests does not get a test animation. What a project cannot support is omitted",
        "rather than invented.",
        "",
    ]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"  account storyboard: {len(lines)} lines, {len(rows)} repositories, "
          f"10 profile surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())