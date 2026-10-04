#!/usr/bin/env python3
"""Generate assets/profile/build-signal.json from the live GitHub API.

The Build Signal graphic is only allowed to display measured values. This
script is what makes that true: it reads the API, and it writes the numbers the
renderer consumes. Nothing about the counts is written into the SVG source.

Run:  python3 scripts/profile_art/build_signal_data.py
Then: python3 scripts/profile_art/generate.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
OWNER = "M4G3LL4N0"
OUT = PROFILE / "assets" / "profile" / "build-signal.json"

# Reused by the generated profile block, so the two can never disagree.
TESTS_JSON = PROFILE / "tests.json"

# Two exclusions, both matching portfolio-os/portfolio_os/githubos.py exactly so
# this graphic can never disagree with the generated profile block:
#   1. deployment/marketing surfaces for another project are not systems;
#   2. identity surfaces (the profile repo, the easter egg) are not systems.
SITE_SUFFIXES = ("-website", "-site", "-web", "-landing", "-marketing")
IDENTITY_REPOS = {"m4g3ll4n0", "why-are-you-here"}

# Presentation order is deliberate: it reads as a build narrative rather than
# as an arbitrary ranking. Value is what the bar height encodes.
METRIC_SPEC = [
    ("public_systems", "SYSTEMS", "public engineering repositories"),
    ("verified_tests", "TESTS", "tests run and recorded by an operator"),
    ("ci_backed", "CI", "systems with a passing CI workflow"),
    ("public_releases", "RELEASES", "GitHub releases published"),
    ("open_issues_resolved", "MERGED PRs", "pull requests merged"),
]


def gh_json(*args: str):
    result = subprocess.run(["gh", "api", *args], capture_output=True, text=True,
                            timeout=90, check=False)
    if result.returncode or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def list_public_repos() -> list:
    """Enumerate public repositories.

    `repos/{owner}/repos` returns 404 for a user account with a personal
    access token, so fall back to the authenticated-user listing. Both paths
    are read-only.
    """
    direct = gh_json(f"repos/{OWNER}/repos?per_page=100&type=all&visibility=public")
    if isinstance(direct, list) and direct:
        return direct
    via_user = gh_json("user/repos?per_page=100&affiliation=owner&visibility=public")
    if isinstance(via_user, list) and via_user:
        return [r for r in via_user if r.get("full_name", "").lower().startswith(f"{OWNER}/".lower())]
    return []


def recorded_tests() -> dict[str, int]:
    if not TESTS_JSON.is_file():
        return {}
    raw = json.loads(TESTS_JSON.read_text(encoding="utf-8"))
    return {k: int(v.get("count") or 0) for k, v in raw.items()
            if not k.startswith("_") and isinstance(v, dict)}


def engineering_from(records: list) -> list:
    """Public engineering systems, excluding site and identity surfaces."""
    return [r for r in records
            if not str(r.get("name", "")).lower().endswith(SITE_SUFFIXES)
            and str(r.get("name", "")).lower() not in IDENTITY_REPOS
            and not r.get("private")]


def main() -> int:
    # Prefer the enriched snapshot the sync workflow has already built. Using it
    # guarantees the artwork and the README table are rendered from one identical
    # set of records. Re-querying the API here could disagree with the table, and
    # GITHUB_TOKEN cannot enumerate the owner's repositories at all, which would
    # silently undercount every metric rather than fail.
    snapshot = PROFILE / "repos.json"
    from_snapshot = False
    repos: list = []
    if "--inventory" in sys.argv[1:] and snapshot.is_file():
        repos = json.loads(snapshot.read_text(encoding="utf-8"))
        from_snapshot = True
    else:
        repos = list_public_repos()

    engineering = engineering_from(repos)
    if not engineering:
        raise SystemExit("could not enumerate public repositories; refusing to write a signal")
    tests = recorded_tests()

    releases = 0
    ci_backed = 0
    rel_map: dict[str, list] = {}
    for repo in engineering:
        if from_snapshot:
            # The snapshot was enriched with these fields by enrich_snapshot.py.
            count = repo.get("release_count")
            releases += int(count or 0)
            rel_map[repo["name"]] = ([{"tag_name": repo.get("latest_release")}]
                                     if repo.get("latest_release") else [])
            if repo.get("ci_conclusion") == "success":
                ci_backed += 1
            continue
        rel = gh_json(f"repos/{OWNER}/{repo['name']}/releases?per_page=100")
        rel_map[repo["name"]] = rel if isinstance(rel, list) else []
        releases += len(rel_map[repo["name"]])
        runs = gh_json(
            f"repos/{OWNER}/{repo['name']}/actions/runs"
            f"?branch={repo.get('default_branch') or 'main'}&per_page=1")
        latest = (runs or {}).get("workflow_runs", []) if isinstance(runs, dict) else []
        if latest and latest[0].get("conclusion") == "success":
            ci_backed += 1

    search = gh_json("search/issues?q=type:pr+is:merged+author:M4G3LL4N0&per_page=100")
    merged = search.get("total_count", 0) if isinstance(search, dict) else 0

    values = {
        "public_systems": len(engineering),
        "verified_tests": sum(tests.get(r["name"], 0) for r in engineering),
        "ci_backed": ci_backed,
        "public_releases": releases,
        "open_issues_resolved": merged,
    }

    metrics = []
    for key, label, _note in METRIC_SPEC:
        metrics.append({
            "key": key, "label": label,
            "value": values[key],
            "display": f"{values[key]:,}",
        })

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "owner": OWNER,
        "source": ("enriched repos.json snapshot + tests.json (operator-recorded test counts)"
                   if from_snapshot
                   else "GitHub API + tests.json (operator-recorded test counts)"),
        "excludes": "site-only (*-website) and identity surfaces are not engineering systems",
        "metrics": metrics,
        "per_system": {
            r["name"]: {
                "tests": tests.get(r["name"]),
                "releases": len(rel_map.get(r["name"], [])),
                "latest_release": rel_map.get(r["name"], [{}])[0].get("tag_name", "")
                if rel_map.get(r["name"]) else "",
                "license": ((r.get("license") or {}) or {}).get("spdx_id") or None,
            } for r in engineering
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for metric in metrics:
        print(f"{metric['display']:>8}  {metric['label']}")
    print(f"\nwrote {OUT.relative_to(PROFILE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())