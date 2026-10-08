"""Render the profile repository's own surfaces in the deeper clay style.

Profile-only by design. The 136 per-repository surfaces are produced by
render_art.py through clay_renderers.py and are deliberately left alone; this
writes just M4G3LL4N0 into the same staging tree so the existing publisher can
ship it unchanged.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay3d as X  # noqa: E402
import evidence as E  # noqa: E402
import profile_surfaces as PS  # noqa: E402

PROFILE = HERE.parents[2]
ART = PROFILE / ".github-art" / "v8-art"
OWNER = "M4G3LL4N0"


def payload(index: dict, manifest: dict) -> dict:
    """The portfolio seen from outside: the same measured totals, framed once."""
    routes = [r for rec in index.values() for r in (rec.get("routes") or [])]
    n_routes = len(routes)
    mods: dict[str, int] = {}
    for rec in index.values():
        for m in rec.get("modules") or []:
            mods[m] = mods.get(m, 0) + 1
    top_mods = [m for m, _ in sorted(mods.items(), key=lambda kv: (-kv[1], kv[0]))]
    prims: dict[str, int] = {}
    for rec in index.values():
        for pr in rec.get("cs_primitives") or []:
            prims[pr] = prims.get(pr, 0) + 1
    top_prims = [p for p, _ in sorted(prims.items(), key=lambda kv: (-kv[1], kv[0]))]

    fw: dict[str, int] = {}
    for rec in index.values():
        for f in rec.get("frameworks") or []:
            fw[f] = fw.get(f, 0) + 1
    top_fw = [f for f, _ in sorted(fw.items(), key=lambda kv: (-kv[1], kv[0]))]

    tests = sum(r.get("test_count") or 0 for r in index.values())
    ci = sum(len(r.get("ci_workflows") or []) for r in index.values())
    files = sum(r.get("files") or 0 for r in index.values())
    surfaces = sum(len(v["files"]) for v in manifest.values())

    from collections import Counter
    cats = Counter(v["project_category"] for v in manifest.values()).most_common()

    rows_labels = [f"{len(index)} repositories", f"{files:,} files",
                  f"{n_routes:,} routes"]
    route_top: dict[str, int] = {}
    for r in routes:
        route_top[r] = route_top.get(r, 0) + 1
    stages = [r for r, _ in sorted(route_top.items(), key=lambda kv: (-kv[1], kv[0]))]

    tiles = [(f"{len(index)}", "repositories"),
             (f"{n_routes:,}", "routes"),
             (f"{files:,}", "files analysed")]
    pairs = [("repositories", str(len(index))),
             ("files analysed", f"{files:,}"),
             ("http routes", f"{n_routes:,}"),
             ("test files", f"{tests:,}"),
             ("ci workflows", str(ci))]
    milestones = ["build the next company", "keep the ledger honest",
                  "measure everything", "ship measurable software", "compound"]

    return {
        "canonical_name": "DUNG30N5 x NOAERTH",
        "repo": OWNER,
        "project_category": "PORTFOLIO",
        "status": "PORTFOLIO",
        "confidence": "E3",
        "domain": "Venture operating company",
        "palette": "mesa_terracotta",
        "routes_count": n_routes,
        "modules_count": len(top_mods),
        "module_plinths": top_mods[:5],
        "terminal_lines": rows_labels,
        "pairs": pairs,
        "tiles": tiles,
        "note_routes": f"{n_routes:,}",
        "stages": stages[:5] or ["/"],
        "primitives": top_prims[:4],
        "frameworks": top_fw[:8],
        "tests": tests,
        "crates": max(1, min(6, tests // 10 + (1 if tests % 10 else 0))),
        "ci": ci,
        "steps": [c.replace("_", " ").title() for c, _ in cats[:5]],
        "surfaces": surfaces,
        "routes_line": f"{n_routes:,}",
        "hero_tiles": [(f"{len(index)}", "repositories"),
                       (f"{n_routes:,}", "routes"),
                       (f"{files:,}", "files")],
        "bodies": top_prims[:5] or ["index", "pipeline"],
        "racks": max(2, min(6, len(top_mods) // 2 + 1)),
        "milestone": milestones[0],
        "problem": ("Operating layer for venture creation: measurable, "
                    "inspectable software instead of claims."),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ART))
    args = ap.parse_args()

    index = E.load_index()
    art_root = pathlib.Path(args.out)
    manifest_path = art_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    d = payload(index, manifest)

    dest = art_root / OWNER
    dest.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for slot in PS.RENDERERS:
        for suffix, light, motion in PS.VARIANTS:
            svg = PS.render(slot, d, OWNER, light=light, motion=motion)
            fname = f"{slot}-{suffix}.svg"
            (dest / fname).write_text(svg)
            written.append(fname)
    for stale in dest.glob("*.svg"):
        if stale.name not in written:
            stale.unlink()

    manifest[OWNER] = {
        "slots": list(PS.RENDERERS),
        "files": written,
        "bytes": sum((dest / f).stat().st_size for f in written),
        "description": "Profile repository for DUNG30N5, founder of noaerth.com. "
                       "Measured evidence for 136 public repositories, rendered as "
                       "seamlessly looping clay scenes: source-derived route, module "
                       "and test maps in the New Mexico visual system.",
        "topics": ["noaerth", "dung30n5", "portfolio", "profile", "svg",
                   "documentation", "developer-tools"],
        "project_category": "PORTFOLIO",
        "palette": "mesa_terracotta",
        "status": "PORTFOLIO",
        "confidence": "E3",
    }
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")
    loops = sum((dest / f).read_text().count('repeatCount="indefinite"')
                for f in written if f.endswith("-motion.svg") or f.endswith("-light.svg"))
    print(f"  profile slots    : {len(PS.RENDERERS)}")
    print(f"  files written    : {len(written)}")
    print(f"  looping tracks   : {loops}")
    print(f"  bytes            : {manifest[OWNER]['bytes']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())