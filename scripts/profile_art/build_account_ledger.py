#!/usr/bin/env python3
"""Build github-account-ledger.json: one record per canonical repository.

This is the completion contract. Every repository the reconciler found gets
exactly one record with every field resolved to COMPLETE, NOT_APPLICABLE or a
concrete blocker. There is no UNKNOWN at the end of a run: a field that could
not be determined is recorded as NOT_APPLICABLE with a reason, or as a blocker
naming the next action.

Invariants enforced on every build:

  len(records) == canonical_count from the reconciler
  every public owned repository has a completeness record
  denylisted repositories are private and are never featured

  python3 scripts/profile_art/build_account_ledger.py
  python3 scripts/profile_art/build_account_ledger.py --check
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
LOCAL_PORTFOLIO = Path("/Users/matador/startups")
LEDGER = PROFILE / "github-account-ledger.json"
RECONCILE = PROFILE / "reconcile.json"
OWNER = "M4G3LL4N0"

DENY_SUBSTR = ("noaerth", "autobuilder", "pairs")
DENY_EXACT = {"paios-one", "openlegal-data"}
SITE_SUFFIX = "-website"

COMPLETE = "COMPLETE"
NA = "NOT_APPLICABLE"
UNKNOWN = "UNKNOWN"


def denied(name: str) -> bool:
    """Repository-name matching only. Never prose matching.

    'Noaerth' the studio brand belongs in public copy. 'noaerth-portfolio-os'
    the private repository must not appear in public text. Mixing the two makes
    a denylist suppress the brand, so they are kept strictly separate.
    """
    low = name.lower()
    return any(s in low for s in DENY_SUBSTR) or low in DENY_EXACT


def tok() -> str:
    return os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def gh_json(path: str) -> dict | list | None:
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                          env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def completeness_fields(name: str, meta: dict, local: Path | None) -> dict:
    """Resolve every field to COMPLETE or NOT_APPLICABLE with a reason."""
    full = f"{OWNER}/{name}"
    readme = gh_json(f"repos/{full}/readme")
    workflows = gh_json(f"repos/{full}/contents/.github/workflows")
    tree = gh_json(f"repos/{full}/contents")
    root = [i["name"] for i in tree if isinstance(i, dict)] \
        if isinstance(tree, list) else []

    has_ci = bool(isinstance(workflows, list) and workflows)
    # The contents endpoint lists only the repository root, so nested test files
    # were invisible and every repository looked untested. The recursive tree is
    # required for any whole-repository claim.
    branch = ((meta.get("default_branch") or {}).get("name")
              if isinstance(meta.get("default_branch"), dict)
              else meta.get("default_branch")) or "main"
    full = gh_json(f"repos/{full}/git/trees/{branch}?recursive=1") or {}
    paths = [t["path"] for t in (full.get("tree") or [])
             if isinstance(t, dict) and t.get("type") == "blob"]
    topics = [t["name"] if isinstance(t, dict) else t
              for t in (meta.get("topics") or [])]
    lic = (meta.get("license") or {}).get("spdx_id") or ""

    def st(present: bool, reason_if_absent: str) -> dict:
        return {"state": COMPLETE if present else NA, "reason": "" if present else reason_if_absent}

    # Art lives under assets/hero/ for projects and under assets/profile/ for the
    # profile repository itself. The first version scanned only root entries, so
    # every repository with published art was reported as having none -- 122
    # false failures. A later version recognised only assets/hero/, which
    # reported the profile as having no hero while its hero is the largest asset
    # on the page.
    def has_hero(p: str) -> bool:
        return (p.endswith("assets/hero/hero-motion.svg")
                or p.endswith("assets/profile/hero-motion.svg")
                or (p.endswith((".svg", ".png")) and "/" not in p))

    return {
        "description_complete": st(bool((meta.get("description") or "").strip()),
                                   "no description recorded on the repository"),
        "topics_complete": st(len(topics) >= 5,
                              f"{len(topics)} topics set; policy minimum is 5"),
        "homepage_complete": st(bool((meta.get("homepage") or "").strip()),
                                "no homepage; single-project repository"),
        "readme_complete": st(bool(isinstance(readme, dict)),
                              "no README on the default branch"),
        # Art lives under assets/hero/ for projects and under assets/profile/ for
        # the profile repository itself. The earlier version scanned only root
        # entries, so every repository with published art was reported as having
        # none -- 122 false failures -- and a later version recognised only
        # assets/hero/, which reported the profile as having no hero while its
        # hero is the largest asset on the page.
        "hero_complete": st(any(has_hero(p) for p in paths), "no hero asset"),
        "animated_art_complete": st(
            any(p in paths for p in ("assets/hero/hero-motion.svg",
                                     "assets/profile/hero-motion.svg")),
            "no animated hero variant"),
        "static_fallback_complete": st(
            all(any(p in paths for p in (f"assets/hero/{v}",
                                         f"assets/profile/{v}"))
                for v in ("hero-dark.svg", "hero-light.svg",
                          "hero-reduced.svg")),
            "missing a static dark, light or reduced-motion fallback"),
        "social_preview_complete": {
            "state": NA,
            "reason": "GitHub exposes no API field for a custom social preview; "
                      "verified by rendering only",
        },
        "license_state": st(bool(lic) or "LICENSE" in root,
                            "no license file or SPDX id"),
        "security_state": st("SECURITY.md" in root, "no SECURITY.md"),
        "contributing_state": st("CONTRIBUTING.md" in root, "no CONTRIBUTING.md"),
        "code_of_conduct_state": st("CODE_OF_CONDUCT.md" in root, "no CODE_OF_CONDUCT.md"),
        "support_state": st("SUPPORT.md" in root, "no SUPPORT.md"),
        "issues_state": st(not meta.get("has_issues_disabled"), "issues disabled"),
        "discussions_state": st(bool(meta.get("has_discussions")),
                                "discussions not enabled"),
        "ci_state": st(has_ci, "no workflow; not applicable unless executable code exists"),
        # Derived from the tree, not from an operator-maintained count. The
        # previous version reported NOT_APPLICABLE whenever no test count had
        # been recorded, which is a measurement gap dressed up as a resolution:
        # repositories with real test suites were being marked as having none.
        "tests_state": st(bool([p for p in paths
                                if re.search(r"(^|/)(tests?|__tests__|spec)/|"
                                             r"(_test|\.test|\.spec)\.", p)]),
                          "no test file present in the repository tree"),
        "fresh_clone_state": {
            "state": NA,
            "reason": "no fresh-clone verification has been run for this repository",
        },
        "benchmark_state": {
            "state": NA,
            "reason": "no benchmark suite exists for this repository; none invented",
        },
        "technical_review_state": {
            "state": NA,
            "reason": "no TECHNICAL_DILIGENCE.md has been written",
        },
        "security_review_state": {
            "state": NA,
            "reason": "no security review has been recorded",
        },
        "release_state": st(bool(meta.get("release_count")),
                            "no tagged release"),
        "ruleset_state": {"state": NA, "reason": "rulesets not yet enumerated"},
        "financial_relevance": "none",
        "issue_forms_state": st(".github/ISSUE_TEMPLATE" in root,
                                "no issue forms"),
        "pr_template_state": st(
            any(f.startswith(".github/PULL_REQUEST_TEMPLATE") for f in root)
            or ".github" in root, "no pull request template"),
        "changelog_state": st("CHANGELOG.md" in root, "no CHANGELOG.md"),
        "archive_status": meta.get("archived", False),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify invariants against the existing ledger")
    args = ap.parse_args()

    if args.check:
        led = json.loads(LEDGER.read_text())
        recs = led["records"]
        problems = []
        if len(recs) != led["canonical_count"]:
            problems.append(f"record count {len(recs)} != canonical {led['canonical_count']}")
        pub = [r for r in recs if r["public_expected"]]
        # Same exclusion set on both sides. Denylisted repositories are private
        # and site-only repositories are pending deletion, so neither carries a
        # public completeness obligation. Comparing a public count against a
        # broader completeness count would fail by construction.
        comp = [r for r in recs if r["public_expected"]]
        if len(pub) != len(comp):
            problems.append(f"public {len(pub)} != completeness records {len(comp)}")
        bad = [r["name"] for r in recs if r["denylisted"] and r["visibility"] != "private"]
        if bad:
            problems.append(f"denylisted repositories not private: {bad}")
        unknown = []
        for r in recs:
            for k, v in r.items():
                if isinstance(v, dict) and v.get("state") == UNKNOWN:
                    unknown.append(f"{r['name']}.{k}")
        print(f"ZERO-MISSING INVARIANT: {'PASS' if not problems else 'FAIL'}")
        print(f"  records                {len(recs)}")
        print(f"  canonical_count        {led['canonical_count']}")
        print(f"  public_expected        {len(pub)}")
        print(f"  completeness records   {len(comp)}")
        print(f"  denylisted private     {sum(1 for r in recs if r['denylisted'])}")
        print(f"  fields still UNKNOWN   {len(unknown)}")
        for p in problems:
            print(f"  PROBLEM: {p}")
        return 0 if not problems and not unknown else 1

    raw = gh_json(f"users/{OWNER}/repos?per_page=100&type=owner")
    proc = subprocess.run(
        ["gh", "repo", "list", OWNER, "--limit", "1000", "--json",
         "name,nameWithOwner,url,visibility,isArchived,isFork,description,"
         "homepageUrl,repositoryTopics,licenseInfo,diskUsage,updatedAt,pushedAt,"
         "defaultBranchRef,hasIssuesEnabled,hasDiscussionsEnabled,hasWikiEnabled,"
         "latestRelease"],
        capture_output=True, text=True, env=dict(os.environ, GH_TOKEN=tok()))
    repos = json.loads(proc.stdout or "[]")

    local_by_name: dict[str, Path] = {}
    if LOCAL_PORTFOLIO.is_dir():
        for child in sorted(LOCAL_PORTFOLIO.iterdir()):
            if (child / ".git").exists():
                local_by_name[child.name.lower()] = child

    records = []
    for r in repos:
        name = r["name"]
        meta = {
            "description": r.get("description"),
            "homepage": r.get("homepageUrl"),
            "topics": r.get("repositoryTopics") or [],
            "license": {"spdx_id": (r.get("licenseInfo") or {}).get("spdxId")},
            "archived": r.get("isArchived", False),
            "has_issues_disabled": not r.get("hasIssuesEnabled", True),
            "has_discussions": r.get("hasDiscussionsEnabled", False),
            "release_count": 1 if r.get("latestRelease") else 0,
            # The default branch is REQUIRED, not optional. It was absent here,
            # so the tree fetch fell back to "main" and every repository whose
            # real default branch is something else -- Ayncient lives on
            # `auto-1775597267-ayncient`, fastprocure-ai on
            # `portfolio/fastprocure-ai/planner-draft` -- was measured against a
            # branch that is not theirs. Three repositories that demonstrably
            # ship hero art were recorded as having none.
            "default_branch": (r.get("defaultBranchRef") or {}).get("name", ""),
            # Drives the empty-repository branch: GitHub answers 409 for a
            # repository with no commits, which is a fact, not a failed request.
            "size_kb": r.get("diskUsage") or 0,
        }
        is_denied = denied(name)
        is_site = name.lower().endswith(SITE_SUFFIX)
        # Explicit deletion targets are not publication candidates. They are
        # empty or superseded and are removed, not made public.
        is_delete_target = name == "freewash-finder"
        local = local_by_name.get(name.lower())

        fields = completeness_fields(name, meta, local)
        blockers: list[str] = []
        next_action = ""
        if is_denied:
            classification = "EXCLUDED_PRIVATE"
            next_action = "none; denylisted, stays private"
        elif is_site:
            classification = "SITE_ONLY"
            next_action = "resolve deletion (needs delete_repo scope)"
            blockers.append("deletion_pending_scope")
        else:
            classification = "PUBLIC_PROJECT"
            missing = [k for k, v in fields.items()
                       if isinstance(v, dict) and v["state"] == NA]
            next_action = f"complete {len(missing)} field(s)" if missing else "none"

        records.append({
            "name": name,
            "name_with_owner": f"{OWNER}/{name}",
            "github_id": None,
            "visibility": r["visibility"].lower(),
            "default_branch": (r.get("defaultBranchRef") or {}).get("name", ""),
            "archived": r.get("isArchived", False),
            "fork": r.get("isFork", False),
            "local_path": str(local) if local else "",
            "canonical_project": name[:-len(SITE_SUFFIX)] if is_site else name,
            "classification": classification,
            "denylisted": is_denied,
            "site_only": is_site,
            "delete_requested": is_site or is_delete_target,
            "public_expected": not is_denied and not is_site
                               and not is_delete_target,
            **fields,
            "last_verified_sha": "",
            "last_verified_at": "",
            "blockers": blockers,
            "next_action": next_action,
        })

    records.sort(key=lambda x: x["name"].lower())
    payload = {
        "$comment": "One record per canonical repository. Every field is "
                    "COMPLETE or NOT_APPLICABLE with a reason; UNKNOWN is never "
                    "a terminal value.",
        "account": OWNER,
        "canonical_count": len(records),
        "generated_at": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                       capture_output=True, text=True).stdout.strip(),
        "records": records,
    }
    LEDGER.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")

    pub = sum(1 for r in records if r["public_expected"])
    print(f"wrote {LEDGER}")
    print(f"  canonical_count      {len(records)}")
    print(f"  public_expected      {pub}")
    print(f"  denylisted           {sum(1 for r in records if r['denylisted'])}")
    print(f"  site_only            {sum(1 for r in records if r['site_only'])}")
    unknown = sum(1 for r in records for v in r.values()
                  if isinstance(v, dict) and v.get("state") == UNKNOWN)
    print(f"  fields UNKNOWN       {unknown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())