"""Evidence payload for the profile repository itself.

The profile repository has almost no structure of its own, so deriving its art
from its own tree produced six slots and left the README pointing at three
files that were never generated. The profile is a view over the portfolio, so
its payload is built from the portfolio-wide measurement instead: the route
map, module map and test inventory are real, they just belong to all 136
repositories rather than to this one.
"""

from __future__ import annotations

import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import evidence as E  # noqa: E402
from geometry import palette_for  # noqa: E402
from renderers import seed_of  # noqa: E402

PROFILE_NAME = "M4G3LL4N0"

# The profile is a view across every category, so it gets the widest set.
SLOTS = ["hero", "terminal", "architecture", "data_flow", "state_machine",
         "component_map", "build", "workflow", "domain", "footer"]


def build(index: dict[str, dict], manifest: dict[str, dict]) -> dict:
    routes_all: list[str] = []
    for rec in index.values():
        routes_all.extend(rec.get("routes") or [])

    modules: collections.Counter = collections.Counter()
    prims: collections.Counter = collections.Counter()
    langs: collections.Counter = collections.Counter()
    for rec in index.values():
        modules.update(rec.get("modules") or [])
        prims.update(rec.get("cs_primitives") or [])
        for k, v in (rec.get("languages") or {}).items():
            langs[k] += v

    top_routes = [r for r, _ in collections.Counter(routes_all).most_common(8)]
    top_modules = [m for m, _ in modules.most_common(8)]
    top_prims = [p for p, _ in prims.most_common(8)]

    files = sum(r.get("files") or 0 for r in index.values())
    tests = sum(r.get("test_count") or 0 for r in index.values())
    tested = sum(1 for r in index.values() if (r.get("test_count") or 0) > 0)
    ci = sum(len(r.get("ci_workflows") or []) for r in index.values())
    surfaces = sum(len(v["files"]) for v in manifest.values())
    slots = sum(len(v["slots"]) for v in manifest.values())
    statuses = collections.Counter(v["status"] for v in manifest.values())
    categories = collections.Counter(
        v["project_category"] for v in manifest.values()).most_common()

    status_line = ", ".join(f"{k.lower()} {v}" for k, v in statuses.most_common())

    d: dict = {
        "repo": PROFILE_NAME,
        "canonical_name": "DUNG30N5 x NOAERTH",
        "project_category": "PORTFOLIO",
        "palette": "navy_lavender",
        "domain": "Venture operating company",
        "status": "PORTFOLIO",
        "confidence": "E3",
        "has_code": True,
        "slots": SLOTS,
        "geometry_set": "rosette",
        "animation_story_1": "graph_resolve",
        "animation_story_note": (
            f"{len(index)} repositories resolve as one navigable portfolio surface"),
        "problem": ("Operating layer for venture creation: measurable, "
                    "inspectable software instead of claims."),
        "public_positioning": "",
        "major_modules": top_modules,
        "cs_primitives": top_prims,
        "entry_points": [f"{len(index)} public repositories"],
        "routes": top_routes,
        "frameworks": ["Next.js", "React", "TypeScript"],
        "language": langs.most_common(1)[0][0] if langs else "TypeScript",
        "manifests": ["package.json"],
        "interfaces": [f"https://github.com/{E.OWNER}/{r}" for r in list(index)[:4]],
        "pipeline_stages": [c.replace("_", " ").title() for c, _ in categories[:6]],
        "inputs": [],
        "outputs": [],
        "testing": {
            "present": tests > 0,
            "count": tests,
            "note": f"counted across the portfolio; {tested} of {len(index)} repositories",
        },
        "release": {"ci": ci, "commits": str(len(index)), "tags": 0},
        "card_status": "",
        "card_site": "",
        "slug": "noaerth",
        "card_category": "Portfolio",
        "audience": "operator",
        "next_milestone": "",
        "website_positioning": "",
    }

    d["data_flow"] = (
        f"{len(index)} repositories contribute {len(routes_all):,} routes; "
        f"measured examples {', '.join(top_routes[:4])}"
    )
    d["architecture"] = (
        f"{len(modules)} distinct module roots; most common {', '.join(top_modules[:5])}"
    )
    d["workflow_steps"] = [c.replace("_", " ").title() for c, _ in categories[:6]]
    d["terminal_lines"] = [
        f"{len(index):>4} repositories",
        f"{len(routes_all):>4} routes",
        f"{modules.total():>4} module roots",
        f"{tests:>4} test files ({tested} repos)",
        f"{ci:>4} CI workflows",
        f"{surfaces:>4} generated surfaces",
    ]
    d["terminal_caption"] = (
        f"portfolio totals across {len(index)} repositories, {status_line}")
    d["state_model"] = ", ".join(top_prims[:5])
    d["state_model_note"] = (
        f"{len(prims)} distinct computer-science primitives detected in source")
    d["control_flow"] = (
        f"measure {files:,} files -> classify {len(index)} repositories -> "
        f"render {surfaces:,} surfaces -> publish {slots} slots")
    d["evidence"] = {
        "routes": top_routes,
        "entry_points": d["terminal_lines"],
        "modules": top_modules,
        "frameworks": d["frameworks"],
        "distinctive_frameworks": ["TypeScript"],
        "test_frameworks": [],
        "scaffold_frameworks": ["Next.js", "React"],
        "cs_primitives": top_prims,
        "manifests": ["package.json"],
        "tests": [],
        "ci_workflows": [],
        "language": d["language"],
        "files": files,
        "test_count": tests,
        "shared_template_files": 0,
    }
    d["palette"] = palette_for("PORTFOLIO", seed_of(PROFILE_NAME, "category"))
    return d


def main() -> int:
    from render_art import OUT, render_repo  # local import to avoid a cycle

    index = E.load_index()
    manifest = json.loads((OUT / "manifest.json").read_text())
    d = build(index, manifest)
    dest = OUT / PROFILE_NAME
    files = render_repo(d, dest)
    manifest[PROFILE_NAME] = {
        "slots": d["slots"],
        "files": files,
        "bytes": sum((dest / f).stat().st_size for f in files),
        "description": "Profile repository for DUNG30N5, founder of noaerth.com. "
                       "Generated artwork and measured evidence for 136 public "
                       "repositories: source-derived route, module and test maps "
                       "with dark, light and reduced-motion variants.",
        "topics": ["noaerth", "dung30n5", "portfolio", "profile", "svg",
                   "documentation", "developer-tools"],
        "project_category": "PORTFOLIO",
        "palette": d["palette"],
        "status": "PORTFOLIO",
        "confidence": "E3",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"  profile surfaces : {len(files)} files, {len(d['slots'])} slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
