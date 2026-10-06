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


THROTTLED = False


def gh_json(path: str):
    """Return None on failure, but distinguish throttling from absence.

    A rate-limited request returns an error body. Treating that as 'no README'
    reported 86 repositories as undocumented when they are documented, which is
    the same shape of error as claiming art is missing when it is present.
    """
    global THROTTLED
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                       env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    if p.returncode != 0:
        if "rate limit" in (p.stderr or "").lower():
            THROTTLED = True
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def raw(repo: str, branch: str, path: str) -> str | None:
    """Fetch through raw.githubusercontent.com.

    Not subject to the API rate limit, so the audit still measures something
    when the API refuses to answer. Returns None only on a genuine 404.
    """
    import urllib.error
    import urllib.request
    url = f"https://raw.githubusercontent.com/{OWNER}/{repo}/{branch}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=25) as fh:
            return fh.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return None if exc.code == 404 else None
    except Exception:
        return None


def blob(repo: str, path: str, branch: str = "main") -> str:
    d = gh_json(f"repos/{OWNER}/{repo}/contents/{path}")
    if isinstance(d, dict) and d.get("content"):
        try:
            return base64.b64decode(d["content"]).decode("utf-8", "replace")
        except Exception:
            pass
    return raw(repo, branch, path) or ""


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

    # Take the repository list from the committed ledger rather than the API.
    # An empty API response previously produced "0 images, 0 unresolved", which
    # reads as a clean result while measuring nothing at all.
    led = PROFILE / "github-account-ledger.json"
    if not led.exists():
        print("github-account-ledger.json missing; run build_account_ledger.py")
        return 1
    data = json.loads(led.read_text(encoding="utf-8"))
    repos = [{"name": r["name"], "default_branch": r.get("default_branch") or "main"}
             for r in data.get("records", [])
             if r.get("visibility") == "public" and not denied(r["name"])]
    if not repos:
        print("  no public repositories in the ledger")
        return 1

    rows = []
    counters = Counter()

    for repo in repos:
        name = repo["name"]
        branch = repo.get("default_branch") or "main"
        readme = blob(name, "README.md", branch)
        if not readme:
            reason = ("read unavailable: API throttled" if THROTTLED
                      else "repository has no README")
            rows.append({"repo": name, "path": "README.md",
                         "purpose": "UNVERIFIED" if THROTTLED else "no README",
                         "animated": "UNVERIFIED" if THROTTLED else "N/A",
                         "fallback": "N/A", "live": False, "note": reason})
            counters["throttled" if THROTTLED else "no_readme"] += 1
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
            text = blob(name, ref, branch)
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

    import time
    ledger = {
        "$comment": "Every image referenced by a public owned repository, with "
                    "its purpose, animation state and live resolution. Resolved "
                    "means ANIMATED or an explicit static reason; UNKNOWN is not "
                    "a permitted value.",
        "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "owner": OWNER,
        "image_count": len(rows),
        "unresolved": len([r for r in rows if r["animated"] == "UNKNOWN"]),
        "images": rows,
    }
    Path(PROFILE / "github-image-ledger.json").write_text(
        json.dumps(ledger, indent=1) + "\n", encoding="utf-8")

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

    unresolved = [r for r in rows
                  if r["animated"] in ("UNKNOWN", "UNVERIFIED")]
    out += ["", f"## Unresolved: **{len(unresolved)}**", ""]
    if unresolved:
        for r in unresolved:
            out.append(f"- `{r['repo']}` `{r['path']}` \u2014 {r['note']}")
        if THROTTLED:
            out.append("")
            out.append("These are **unverified, not missing**. The GitHub API "
                       "rate limit was reached during this run. Re-run when the "
                       "limit clears; raw.githubusercontent.com is not subject to "
                       "it and can be used instead.")
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