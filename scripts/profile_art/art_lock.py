#!/usr/bin/env python3
"""Art Lock: make silent visual reversion structurally impossible.

The defect this exists to prevent
---------------------------------
The scheduled profile sync runs `generate.py`, which regenerates the entire
art directory -- hero, system map, terminal, every flagship window -- and then
commits whatever it produced. Its commit message asserted "no hand-authored
content is modified", which was false: `generate.py` writes design-controlled
assets wholesale.

So an approved hero could be replaced by whatever the generator emitted that
day, with a commit message denying it happened. That is how approved artwork was
reverted, and it will not happen again.

The rule
--------
Assets fall into two classes.

  DESIGN      composition, geometry, material, colour, motion, typography.
              These may only change when the design source in .github-art/
              changes. Automation may never alter them.

  FACTUAL     measured values that legitimately change: test counts, release
              version, CI state, last activity.

Automation may rewrite FACTUAL assets and bounded README regions. It may not
touch a DESIGN asset unless the design source hash changed, and if it tries,
this exits non-zero and the workflow fails before anything is committed.

  python3 scripts/profile_art/art_lock.py --lock     # write/refresh hashes
  python3 scripts/profile_art/art_lock.py --verify   # gate for CI
  python3 scripts/profile_art/art_lock.py --classify # show the classification
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
ART_DIR = PROFILE / ".github-art"
LOCK = ART_DIR / "art-lock.json"

# Design-controlled: these encode composition decisions. Automation may not
# rewrite them unless the design source changed.
DESIGN_GLOBS = (
    "assets/profile/hero-*.svg",
    "assets/profile/hero-motion.svg",
    "assets/profile/system-map-*.svg",
    "assets/profile/terminal-*.svg",
    "assets/profile/windows/*.svg",
    "assets/profile/nav/*.svg",
    "assets/profile/avatar/*.svg",
    "assets/profile/cards/*.svg",
    "assets/social-preview.svg",
    "assets/profile/portfolio-economics-*.svg",
)

# Factual: measured state that is expected to change on a schedule.
FACTUAL_GLOBS = (
    "assets/profile/build-signal.json",
    "assets/profile/build-signal-dark.svg",
    "assets/profile/build-signal-light.svg",
)

# Bounded README regions automation may rewrite. These are the markers the
# generators actually use, read from the renderers rather than assumed: the
# first version of this file used `githubos:signal:start`, which appears
# nowhere, and so reported two missing regions that were present under
# different names.
BOUNDED = {
    "signal": ("<!-- signal:start -->", "<!-- signal:end -->"),
    "githubos": ("<!-- githubos:start -->", "<!-- githubos:end -->"),
    "upstream": ("<!-- upstream:start -->", "<!-- upstream:end -->"),
    "labs": ("<!-- labs:start -->", "<!-- labs:end -->"),
}


def design_source_hash() -> str:
    """Hash of everything that legitimately authorises a design change."""
    h = hashlib.sha256()
    sources = sorted(
        [p for p in (PROFILE / "scripts" / "github_art").rglob("*.py")
         if "__pycache__" not in str(p)]
        + [p for p in (PROFILE / "scripts" / "profile_art").rglob("*.py")
           if "__pycache__" not in str(p)]
        + [p for p in (ART_DIR).rglob("*") if p.is_file()]
    )
    for p in sources:
        h.update(str(p.relative_to(PROFILE)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def classify() -> tuple[dict[str, str], dict[str, str]]:
    design: dict[str, str] = {}
    factual: dict[str, str] = {}
    for pattern in DESIGN_GLOBS:
        for p in sorted(PROFILE.glob(pattern)):
            design[str(p.relative_to(PROFILE))] = sha(p)
    for pattern in FACTUAL_GLOBS:
        for p in sorted(PROFILE.glob(pattern)):
            factual[str(p.relative_to(PROFILE))] = sha(p)
    return design, factual


def readme_bounded_state() -> dict[str, str]:
    readme = (PROFILE / "README.md").read_text(encoding="utf-8")
    out = {}
    for name, (start, end) in BOUNDED.items():
        m = re.search(re.escape(start) + r"(.*?)" + re.escape(end), readme, re.S)
        out[name] = hashlib.sha256((m.group(1) if m else "").encode()).hexdigest()
    return out


def lock() -> int:
    design, factual = classify()
    payload = {
        "$comment": "Design-controlled asset hashes. Automation must not "
                    "alter these unless design_source_sha changes. See "
                    "scripts/profile_art/art_lock.py.",
        "design_version": "V6",
        "design_source_sha": design_source_hash(),
        "design_assets": design,
        "factual_assets": factual,
        "bounded_readme_regions": readme_bounded_state(),
    }
    ART_DIR.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
    print(f"art lock written: {len(design)} design, {len(factual)} factual, "
          f"{len(payload['bounded_readme_regions'])} bounded regions")
    return 0


def verify() -> int:
    if not LOCK.exists():
        print("ART LOCK: no lock file. Run --lock to establish the baseline.")
        return 1
    saved = json.loads(LOCK.read_text(encoding="utf-8"))
    design, factual = classify()
    problems: list[str] = []

    # NOTE: a changed design source does NOT authorise anything here. Only an
    # explicit --lock does. When verify() could self-authorise, adding any file
    # to the design-source set -- including this file itself -- unlocked every
    # design asset, and a tampered hero passed. The baseline moves only when a
    # person runs --lock and commits it.
    src_changed = saved["design_source_sha"] != design_source_hash()
    if src_changed:
        print("  design source changed since the lock was written; the lock is "
              "still enforced")
        print("  run --lock only after a deliberate design edit")

    for path, h in design.items():
        was = saved["design_assets"].get(path)
        if was is None:
            problems.append(f"new design asset, not in the lock: {path}")
        elif was != h:
            problems.append(
                f"DESIGN ASSET ALTERED without an explicit --lock: {path}")

    for path in saved["design_assets"]:
        if path not in design:
            problems.append(f"design asset REMOVED without an explicit --lock: {path}")

    for path in saved["factual_assets"]:
        if path not in factual:
            problems.append(f"factual asset missing: {path}")

    readme_text = (PROFILE / "README.md").read_text(encoding="utf-8")
    for name, (start, end) in BOUNDED.items():
        if start not in readme_text or end not in readme_text:
            problems.append(
                f"bounded region {name} lost its markers in README.md; "
                f"automation can no longer be confined to it")

    print("ART LOCK")
    print(f"  design assets tracked   : {len(saved['design_assets'])}")
    print(f"  factual assets tracked  : {len(saved['factual_assets'])}")
    print(f"  bounded regions tracked : {len(saved['bounded_readme_regions'])}")
    print(f"  design source changed   : {'yes' if src_changed else 'no'}")
    print(f"  violations              : {len(problems)}")
    for p in problems[:12]:
        print(f"    {p}")
    if problems:
        print()
        print("  Automation may not alter design-controlled assets. Re-run with")
        print("  --lock only after a deliberate design edit, and say so in the")
        print("  commit message. The previous claim that a commit modifies no")
        print("  hand-authored content was false: generate.py rewrites the whole")
        print("  art directory, including the hero.")
        return 1
    print("  art lock holds")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--classify", action="store_true")
    args = ap.parse_args()
    if args.lock:
        return lock()
    if args.classify:
        design, factual = classify()
        print(f"design-controlled ({len(design)}):")
        for k in sorted(design):
            print(f"  {k}")
        print(f"factual ({len(factual)}):")
        for k in sorted(factual):
            print(f"  {k}")
        return 0
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())