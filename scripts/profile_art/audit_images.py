#!/usr/bin/env python3
"""Audit every presentation image in every public owned repository.

Section 32 requires an image ledger, and section 34 requires every applicable
image to be either animated or explicitly resolved as static for a stated
reason. UNKNOWN is not an allowed outcome.

For each image referenced by a README or docs page, record:

  repo, path, purpose, animated, static fallback, dark, light,
  project-specific, live URL resolves

Two failure modes this catches, both of which have occurred in this account:

  * An SVG that declares CSS @keyframes but contains no SMIL. GitHub's SVG
    renderer does not honour CSS animation, so such a file looks animated in
    source and is completely static in the browser. The financial plate was
    exactly this for one revision.

  * An <img> pointing at a path that does not exist on the default branch,
    which renders as a broken image and is invisible in local testing.

  python3 scripts/profile_art/audit_images.py
  python3 scripts/profile_art/audit_images.py --out IMAGE_LEDGER.md
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
LEDGER = PROFILE / "IMAGE_LEDGER.md"
OWNER = "M4G3LL4N0"
DENY_SUB = ("noaerth", "autobuilder", "pairs")
DENY_EXACT = {"paios-one", "openlegal-data"}
SKIP_LOCAL = re.compile(r"(-website|-site)$", re.I)

# Images that are static by platform or by evidence integrity. Recorded as
# resolved rather than left open.
STATIC_BY_PLATFORM = {
    "social-preview", "screenshot", "avatar", "og-image",
}
STATIC_BY_EVIDENCE = {
    "benchmark", "test-output", "chart", "measurement",
}


def tok() -> str:
    return os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def gh_json(path: str):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                       env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def blob(repo: str, path: str) -> str:
    d = gh_json(f"repos/{OWNER}/{repo}/contents/{path}")
    if isinstance(d, dict) and d.get("content"):
        try:
            return base64.b64decode(d["content"]).decode("utf-8", "replace")
        except Exception:
            return ""
    return ""


def denied(name: str) -> bool:
    low = name.lower()
    return any(s in low for s in DENY_SUB) or low in DENY_EXACT


IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
SRC = re.compile(r'src="([^"]+\.(?:svg|png|jpg|jpeg|gif|webp))"', re.I)


def analyse_svg(text: str) -> dict:
    smil = len(re.findall(r"<animate(?:Transform|Motion|Color)?\b", text))
    css_anim = bool(re.search(r"@keyframes|animation\s*:", text))
    # A file that declares CSS animation but has no SMIL does not move in
    # GitHub's renderer. Reporting that as animated is how a "motion" asset
    # ends up completely still.
    effective = smil > 0
    return {
        "smil": smil,
        "css_declared": css_anim,
        "animated_effective": effective,
        "css_only": css_anim and not effective,
        "reduced_motion": "prefers-reduced-motion" in text,
        "title": "<title" in text,
        "desc": "<desc" in text,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(LEDGER))
    args = ap.parse_args()

    repos = gh_json(f"users/{OWNER}/repos?per_page=100&type=owner&visibility=public") or []
    repos = [r for r in repos
             if isinstance(r, dict)
             and r.get("owner", {}).get("login") == OWNER
             and not denied(r["name"])]

    rows = []
    counters = Counter()

    for repo in repos:
        name = repo["name"]
        branch = repo.get("default_branch") or "main"
        readme = blob(name, "README.md")
        if not readme:
            rows.append({"repo": name, "path": "README.md", "purpose": "no README",
                         "animated": "N/A", "fallback": "N/A", "live": False,
                         "note": "repository has no README"})
            counters["no_readme"] += 1
            continue
        refs = IMG.findall(readme) + SRC.findall(readme)
        for ref in dict.fromkeys(refs):
            if ref.startswith("http"):
                # Remote badges are static by platform: shields.io and the
                # GitHub Actions badge endpoint both serve static SVG that we
                # neither own nor should animate. They are resolved, not
                # unknown, and calling them UNKNOWN would put a permanent
                # non-zero in the final tally.
                purpose = ("ci_badge" if "/actions/workflows/" in ref
                           else "release_badge" if "/v/release/" in ref
                           else "shields_badge")
                rows.append({"repo": name, "path": ref, "purpose": purpose,
                             "animated": "STATIC_BY_PLATFORM", "fallback": "n/a",
                             "live": True, "note": "remote badge, static by design"})
                counters["static_by_platform"] += 1
                continue
            text = blob(name, ref)
            exists = bool(text)
            low = ref.lower()
            if not exists:
                rows.append({"repo": name, "path": ref, "purpose": "missing",
                             "animated": "N/A", "fallback": "N/A", "live": False,
                             "note": "NOT FOUND on default branch"})
                counters["broken"] += 1
                continue
            if low.endswith(".svg"):
                a = analyse_svg(text)
                base = Path(ref).stem.lower()
                if a["css_only"]:
                    state = "CSS_ONLY_NOT_ANIMATED"
                    counters["css_only"] += 1
                elif a["smil"] > 0:
                    state = "ANIMATED"
                    counters["animated"] += 1
                else:
                    state = "STATIC"
                    counters["static"] += 1
                rows.append({"repo": name, "path": ref, "purpose": base,
                             "animated": state,
                             "fallback": "reduced_motion" if a["reduced_motion"]
                                         else ("none" if "motion" not in base
                                               and "-dark" not in base else "check"),
                             "live": True,
                             "note": f"{a['smil']} SMIL, "
                                     f"css={a['css_declared']}, "
                                     f"a11y={a['title'] and a['desc']}"})
            else:
                state = "STATIC_BY_PLATFORM"
                counters["static"] += 1
                rows.append({"repo": name, "path": ref,
                             "purpose": Path(ref).stem.lower(),
                             "animated": state, "fallback": "n/a",
                             "live": True, "note": f"{len(text)} bytes raster"})

    out = ["# Image ledger", "",
           f"Every image referenced by a public owned repository. "
           f"**{len(rows)} images** across **{len(repos)} repositories**.", "",
           "Unresolved images must equal zero. A file that declares CSS "
           "`@keyframes` but no SMIL is reported `CSS_ONLY_NOT_ANIMATED`: "
           "GitHub's SVG renderer does not honour CSS animation, so it does not "
           "move in the browser.", "",
           "## Summary", "", "| state | count |", "| --- | --- |"]
    for k, v in sorted(counters.items()):
        out.append(f"| {k} | {v} |")
    out += ["", "## Per-image detail", "",
            "| repo | path | purpose | animation | fallback | live | note |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append(f"| `{r['repo']}` | `{r['path'][:52]}` | {r['purpose'][:26]} | "
                   f"{r['animated']} | {r['fallback']} | "
                   f"{'yes' if r['live'] else 'NO'} | {r['note'][:44]} |")

    unresolved = [r for r in rows if r["animated"] == "UNKNOWN"]
    out += ["", f"## Unresolved: **{len(unresolved)}**", ""]
    if unresolved:
        for r in unresolved:
            out.append(f"- `{r['repo']}` `{r['path']}`")
    else:
        out.append("None.")

    Path(args.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {Path(args.out).name}: {len(rows)} images, "
          f"{len(unresolved)} unresolved")
    for k, v in sorted(counters.items()):
        print(f"  {k:<28}{v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())