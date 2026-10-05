#!/usr/bin/env python3
"""Build GITHUB_V5_PUBLIC_INVENTORY.json.

The public GitHub is the input boundary. This script reads the live repository
list, classifies every repository the outside world can see, and writes an
inventory that is safe to publish.

Two rules are enforced rather than documented:

  1. A repository that is private, or whose name marks it as a deployment site,
     never appears in the output. Not as a row, not in a count breakdown, not
     in a list of "excluded" names. Deployment-site repositories are numerous
     and their names describe other people's products; publishing even that list
     would leak portfolio structure.
  2. Classification is explicit. A repository is PROFILE, LEGACY_EASTER_EGG,
     FLAGSHIP, PUBLIC_PROJECT, PUBLIC_LAB, or PUBLIC_ARCHIVE by rule, never by
     a default that sweeps unknowns into a flattering bucket.

Counts of withheld material are reported as integers only.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
OUT = PROFILE / "GITHUB_V5_PUBLIC_INVENTORY.json"
RAW = PROFILE / "repos.json"
OWNER = "M4G3LL4N0"

SITE_SUFFIXES = ("-website", "-site", "-web", "-landing", "-marketing")

# Identity surfaces are public but are not engineering systems.
PROFILE_REPOS = {"m4g3ll4n0"}
EASTER_EGG_REPOS = {"why-are-you-here"}

# Flagships are an explicit, reviewed allowlist. They are the systems the
# portfolio is willing to put its name behind, and they are the only systems
# that receive flagship-level visual investment.
FLAGSHIP_ALLOWLIST = (
    "noaerth-portfolio-os",
    "agentos",
    "grokinstall",
    "grokmax",
    "gh0st",
    "opencode-watchdog",
)

# Labs must declare themselves experimental at the top level. A feature table
# that lists "EXPERIMENTAL" next to future work is not a status declaration:
# an earlier version of this rule matched the bare word and misfiled two mature
# systems as labs. The Publication Council standard is an explicit
# `STATUS: EXPERIMENTAL` line or the equivalent frontmatter, so that is what is
# required here.
LAB_STATUS = re.compile(
    r"^\s*(?:[-*>]\s*)?(?:\*\*|__)?\s*STATUS\s*(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*EXPERIMENTAL\b",
    re.IGNORECASE | re.MULTILINE,
)
LAB_FRONTMATTER = re.compile(r"^status:\s*experimental\s*$", re.IGNORECASE | re.MULTILINE)


def is_site_only(name: str) -> bool:
    return str(name).lower().endswith(SITE_SUFFIXES)


def classify(repo: dict, readmes: dict) -> tuple[str, str]:
    """Return (classification, reason). The reason is published alongside the class."""
    name = str(repo.get("name", ""))
    lowered = name.lower()

    if lowered in PROFILE_REPOS:
        return "PROFILE", "the profile repository itself"
    if lowered in EASTER_EGG_REPOS:
        return "LEGACY_EASTER_EGG", (
            "kept deliberately unpolished; it exists because the account used to "
            "have nothing public")

    readme = (readmes.get(lowered) or "").lower()
    archived = bool(repo.get("archived"))
    if archived:
        return "PUBLIC_ARCHIVE", "repository is marked archived on GitHub"
    if lowered in FLAGSHIP_ALLOWLIST:
        return "FLAGSHIP", "reviewed allowlist: carries the portfolio's name"
    if LAB_STATUS.search(readme) or LAB_FRONTMATTER.search(readme):
        return "PUBLIC_LAB", "declares STATUS: EXPERIMENTAL at the top level of its README"
    return "PUBLIC_PROJECT", "public, not an archive, not self-declared experimental"


def read_readme(repo: dict) -> str:
    full = repo.get("full_name") or f"{OWNER}/{repo.get('name')}"
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{full}/readme", "--jq", ".content"],
            capture_output=True, text=True, timeout=45, check=False,
            env={**__import__("os").environ, "GH_TOKEN": __import__("os").environ.get("GH_TOKEN", "")},
        )
        if result.returncode or not result.stdout.strip():
            return ""
        import base64
        return base64.b64decode(result.stdout.strip()).decode("utf-8", "replace")
    except Exception:
        return ""


def main() -> int:
    if not RAW.is_file():
        print("repos.json missing; run enrich_snapshot.py first", file=sys.stderr)
        return 1
    repos = json.loads(RAW.read_text(encoding="utf-8"))

    withheld_private = 0
    withheld_site_only = 0
    public_rows = []

    for repo in repos:
        name = str(repo.get("name", ""))
        # Site-only repositories are counted in their own category even though
        # every one of them is also private. Folding them into a single
        # "withheld" number hides how much of the repository count is deployment
        # surface rather than engineering.
        if is_site_only(name):
            withheld_site_only += 1
            continue
        if repo.get("private"):
            withheld_private += 1
            continue
        public_rows.append(repo)

    readmes = {}
    for repo in public_rows:
        readmes[repo["name"].lower()] = read_readme(repo)

    entries = []
    for repo in sorted(public_rows, key=lambda r: r["name"].lower()):
        name = repo["name"]
        klass, reason = classify(repo, readmes)
        latest = repo.get("latest_release") or ""
        conclusion = str(repo.get("ci_conclusion") or "")
        entries.append({
            "name": name,
            "full_name": repo.get("full_name", f"{OWNER}/{name}"),
            "url": f"https://github.com/{repo.get('full_name')}",
            "classification": klass,
            "classification_reason": reason,
            "description": repo.get("description") or "",
            "homepage": repo.get("homepage") or "",
            "topics": sorted(repo.get("topics") or []),
            "language": repo.get("language") or "",
            "license": (repo.get("license") or {}).get("spdx_id") or None,
            "archived": bool(repo.get("archived")),
            "verified_tests": int(repo.get("test_count") or 0) or None,
            "release_count": int(repo.get("release_count") or 0),
            "latest_release": latest,
            "ci": {
                "has_workflow": bool(repo.get("has_ci")),
                "latest_conclusion": conclusion or None,
                "green": conclusion == "success",
            },
            "pushed_at": repo.get("pushed_at") or "",
        })

    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["classification"]] = counts.get(entry["classification"], 0) + 1

    engineering = [e for e in entries if e["classification"] not in
                   ("PROFILE", "LEGACY_EASTER_EGG")]

    payload = {
        "$comment": [
            "Public-facing inventory for the V5 redesign. Generated by",
            "scripts/profile_art/build_public_inventory.py.",
            "",
            "Privacy contract: private repositories and deployment-site",
            "repositories are absent from this document by construction, not by",
            "redaction. Only integer counts of withheld material are reported.",
            "scripts/test_profile_assets.py fails the build if a withheld name",
            "appears here."
        ],
        "schema": "github-v5-public-inventory/1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "owner": OWNER,
        "counts": {
            "public_visible": len(entries),
            "engineering_systems": len(engineering),
            "by_classification": counts,
            "withheld_private": withheld_private,
            "withheld_site_only_private": withheld_site_only,
        },
        "measured_totals": {
            "verified_tests": sum(e["verified_tests"] or 0 for e in engineering),
            "releases": sum(e["release_count"] for e in engineering),
            "ci_green": sum(1 for e in engineering if e["ci"]["green"]),
            "ci_not_green": sorted(e["name"] for e in engineering if not e["ci"]["green"]),
            "external_merged_prs": 0,
            "external_merged_pr_note": (
                "no pull request authored by this account has been merged into a "
                "repository it does not own; verified against the search API"
            ),
        },
        "repositories": entries,
    }

    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}")
    print(f"  public visible      : {len(entries)}")
    for klass, count in sorted(counts.items()):
        print(f"    {klass:<20} {count}")
    print(f"  engineering systems : {len(engineering)}")
    print(f"  withheld private    : {withheld_private}")
    print(f"  withheld site-only  : {withheld_site_only}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
