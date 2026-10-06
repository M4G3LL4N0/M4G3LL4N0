#!/usr/bin/env python3
"""Classify repositories that have no describable product.

Forty-eight repositories were rejected by the description guard because no
source said what the project does. Investigating rather than substituting
showed why: they carry the create-next-app route skeleton and nothing else.

    app/about  app/contact  app/demo  app/privacy  app/terms

That is a launch-site scaffold. Describing it as a product would be
fabrication, so these get an accurate description of what they actually are,
and they are never given an invented purpose.

Three classes:

  LAUNCH_SCAFFOLD   the starter route set, no product surface
  UNTOLD_SCAFFOLD    the starter set plus generated documentation, still no
                     product surface
  REAL_PRODUCT      has product code and must be described from it

  python3 scripts/profile_art/classify_scaffolds.py
  python3 scripts/profile_art/classify_scaffolds.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
PORTFOLIO = Path("/Users/matador/startups")
DESCRIPTIONS = PROFILE / ".github-art" / "descriptions.json"
OWNER = "M4G3LL4N0"

# The create-next-app route skeleton. A repository whose only pages are these
# has a launch site, not a product.
SCAFFOLD_ROUTES = {"about", "contact", "demo", "privacy", "terms"}
# Generated documentation that describes the scaffold rather than a product.
GENERATED_DOCS = re.compile(
    r"^(ACCESSIBILITY_REVIEW|AGENT_HANDOFF|ANALYTICS_PLAN|AI_EVALS|"
    r"API_CONTRACTS|ARCHITECTURE_DECISIONS|CLAIM_REGISTER|DECISION_RECORD|"
    r"FAILURE_REGISTER|LAUNCH_READINESS|LOCAL_REVIEW|NOAERTH_UPGRADE_REPORT|"
    r"PREMIUM_UI_UX_REPORT|PROOF_LOOP|RECOVERY_NOTES)\.md$", re.I)
BOILERPLATE = re.compile(
    r"create-next-app|boilerplate|Open \[?http://localhost|"
    r"confidently inferable|not confidently inferable", re.I)

SCAFFOLD_DESC = ("Next.js launch-site scaffold: about, contact, demo, privacy "
                 "and terms routes with no product surface yet.")
REAL_PRODUCT_HINT = re.compile(
    r"\b(api|route\.ts|server|action|controller|service|model|schema|"
    r"migration|queue|worker|pipeline|engine)\b", re.I)


def tok() -> str:
    return os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def local_for(name: str) -> Path | None:
    want = re.sub(r"[^a-z0-9]", "", name.lower())
    if not PORTFOLIO.is_dir():
        return None
    for child in sorted(PORTFOLIO.iterdir()):
        if child.is_dir() and re.sub(r"[^a-z0-9]", "", child.name.lower()) == want:
            return child
    return None


def classify(path: Path) -> dict:
    routes: list[str] = []
    for base in ("app", "src/app", "pages", "src/pages"):
        d = path / base
        if not d.is_dir():
            continue
        for item in d.rglob("page.tsx"):
            rel = item.parent.relative_to(d).as_posix()
            routes.append(rel if rel != "." else "")
        for item in d.rglob("*.tsx"):
            if item.name != "page.tsx":
                rel = item.relative_to(d).as_posix()
                routes.append(rel)
        break
    roots = {r for r in routes if r}
    readme = ""
    f = path / "README.md"
    if f.is_file():
        readme = f.read_text(encoding="utf-8", errors="replace")[:8000]
    docs = sorted(p.name for p in path.glob("*.md") if GENERATED_DOCS.match(p.name))

    only_scaffold = bool(roots) and roots.issubset(SCAFFOLD_ROUTES)
    product_signal = len(roots - SCAFFOLD_ROUTES)
    api_files = len([p for p in path.rglob("route.ts")
                     if "node_modules" not in str(p)])
    if api_files or product_signal:
        kind = "REAL_PRODUCT"
    elif only_scaffold and docs:
        kind = "UNTOLD_SCAFFOLD"
    elif only_scaffold:
        kind = "LAUNCH_SCAFFOLD"
    else:
        kind = "UNTOLD_SCAFFOLD" if BOILERPLATE.search(readme) else "REAL_PRODUCT"

    return {
        "class": kind,
        "routes": sorted(roots)[:12],
        "route_count": len(roots),
        "api_routes": api_files,
        "generated_docs": len(docs),
        "boilerplate_readme": bool(BOILERPLATE.search(readme)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the scaffold descriptions to GitHub")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    data = json.loads(DESCRIPTIONS.read_text(encoding="utf-8")) \
        if DESCRIPTIONS.exists() else {}
    rejected = {k: v for k, v in data.items() if v["rejected_because"]}
    print(f"  rejected descriptions to classify: {len(rejected)}")

    out = {}
    for name in sorted(rejected):
        path = local_for(name)
        if path is None:
            out[name] = {"class": "NO_LOCAL_SOURCE",
                         "reason": "no local checkout; cannot classify"}
            print(f"  {name:<26}NO_LOCAL_SOURCE")
            continue
        info = classify(path)
        info["old_description"] = rejected[name]["old"]
        if info["class"] in ("LAUNCH_SCAFFOLD", "UNTOLD_SCAFFOLD"):
            info["description"] = SCAFFOLD_DESC
        out[name] = info
        print(f"  {name:<26}{info['class']:<18}"
              f"routes={info.get('route_count', 0):<3}api={info.get('api_routes', 0):<3}")

    from collections import Counter
    print()
    for k, v in Counter(x["class"] for x in out.values()).most_common():
        print(f"  {k:<20}{v}")

    dest = Path(args.json) if args.json else PROFILE / ".github-art" / "scaffolds.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"\n  wrote {dest.name}")

    if args.apply:
        t = tok()
        ok = fail = 0
        for name, info in sorted(out.items()):
            desc = info.get("description")
            if not desc:
                continue
            p = subprocess.run(
                ["gh", "repo", "edit", f"{OWNER}/{name}", "--description", desc],
                capture_output=True, text=True, env=dict(os.environ, GH_TOKEN=t))
            if p.returncode == 0:
                ok += 1
            else:
                fail += 1
        print(f"  scaffold descriptions applied: {ok}  failed: {fail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())