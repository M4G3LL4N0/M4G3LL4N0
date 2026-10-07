"""Render the per-repository art set from evidence.

Each repository gets between five and ten surfaces, and only the slots whose
evidence actually exists. Every surface is rendered three ways:

  <slot>.svg          animated, dark
  <slot>-light.svg    animated, light
  <slot>-reduced.svg  static (all SMIL removed), dark

The reduced variant is produced by the renderer's own motion switch rather than
by post-processing, so it cannot drift from the animated version.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import describe as D  # noqa: E402
import evidence as E  # noqa: E402
import renderers as R  # noqa: E402

PROFILE = HERE.parents[2]
OUT = PROFILE / ".github-art" / "v8-art"

# The animated dark variant is named -motion so motion is explicit in the
# filename, matching the convention the profile README test enforces
# (hero-motion.svg) and the assets/hero/ set that already exists.
VARIANTS = (("motion", False, True), ("light", True, True), ("reduced", False, False))


def render_repo(d: dict, out_dir: pathlib.Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for slot in d["slots"]:
        if slot not in R.RENDERERS:
            continue
        for suffix, light, motion in VARIANTS:
            svg = R.render(slot, d, d["repo"], light=light, motion=motion)
            fname = f"{slot}-{suffix}.svg"
            (out_dir / fname).write_text(svg)
            written.append(fname)
    return written


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="render a single repository")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    index = E.load_index()
    cards = E.load_cards()
    baseline = E.load_baseline()
    signature = E.template_signature(index)
    out_root = pathlib.Path(args.out)

    names = [args.only] if args.only else sorted(index)
    totals = {"repos": 0, "files": 0, "bytes": 0, "slots": {}}
    manifest: dict[str, dict] = {}

    for name in names:
        rec = index.get(name)
        if rec is None:
            print(f"  !! {name} is not in the index")
            continue
        d = E.build(name, rec, cards.get(name.lower()), baseline.get(name, {}), signature)
        dest = out_root / name
        files = render_repo(d, dest)
        for stale in dest.glob("*.svg"):
            if stale.name not in files:
                stale.unlink()
        size = sum((dest / f).stat().st_size for f in files)
        manifest[name] = {
            "slots": d["slots"],
            "files": files,
            "bytes": size,
            "description": D.describe(d),
            "topics": D.topics_for(d),
            "project_category": d["project_category"],
            "palette": d["palette"],
            "status": d["status"],
            "confidence": d["confidence"],
        }
        totals["repos"] += 1
        totals["files"] += len(files)
        totals["bytes"] += size
        for s in d["slots"]:
            totals["slots"][s] = totals["slots"].get(s, 0) + 1
        if not args.only and totals["repos"] % 25 == 0:
            print(f"  rendered {totals['repos']}/{len(names)} repositories")

    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"  repositories : {totals['repos']}")
    print(f"  svg files    : {totals['files']}")
    print(f"  total bytes  : {totals['bytes']:,}")
    print(f"  slot usage   : {json.dumps(totals['slots'], sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
