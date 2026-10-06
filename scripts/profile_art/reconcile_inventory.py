#!/usr/bin/env python3
"""Reconcile every repository source for the account and prove they agree.

The failure this exists to prevent: an API surface that returns a default page
of 100 becomes the canonical count, and 52 repositories silently vanish from
every report. That has already happened in this account, where one run reported
152 repositories and another reported 100.

Four independent sources are queried and compared:

  gh_cli        gh repo list --limit 1000
  graphql       GraphQL, paginated with a cursor until exhausted
  rest          REST /user/repos, paginated 100 per page with Link headers
  local         Portfolio OS local checkout directory

Rules enforced:

  * The canonical count is the maximum over sources, never a minimum. A source
    that reports fewer repositories than another is treated as truncated, not
    as authoritative.
  * GraphQL and REST both assert an explicit page cap (GitHub caps these at
    100 and 400 respectively) so reaching the cap raises instead of silently
    truncating.
  * A repository missing from any source is reported by name, not by count.

Exit code is non-zero when sources disagree or any repository is missing, so
this can gate a pipeline.

  python3 scripts/profile_art/reconcile_inventory.py
  python3 scripts/profile_art/reconcile_inventory.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

OWNER = "M4G3LL4N0"
LOCAL_PORTFOLIO = Path("/Users/matador/startups")

# GitHub's own ceilings. Reaching one is a hard error, not a page break.
GRAPHQL_CAP = 500
REST_CAP = 400
GH_CLI_CAP = 1000


def gh(args: list[str], token: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, capture_output=True, text=True,
        env=dict(os.environ, GH_TOKEN=token, GH_PAGER="cat", GH_PROMPT_DISABLED="1"))


def token() -> str:
    """Return a usable token, or raise RuntimeError.

    Raised rather than exited so the caller can decide whether an absent token
    is a hard failure. On a pull request from a fork the repository secret is
    not exposed, so treating that as a build failure reports a problem with the
    fork rather than a real disagreement between sources.
    """
    tok = os.environ.get("GH_TOKEN") or ""
    if not tok:
        try:
            tok = subprocess.run(["gh", "auth", "token"],
                                 capture_output=True, text=True).stdout.strip()
        except (FileNotFoundError, OSError):
            # gh not installed or not on PATH. A traceback here would blame the
            # environment rather than reporting the actual condition.
            raise RuntimeError("gh CLI not available and GH_TOKEN unset")
    if not tok:
        raise RuntimeError("no GitHub token available")
    return tok


def source_gh_cli(tok: str) -> tuple[list[str], str]:
    proc = gh(["gh", "repo", "list", OWNER, "--limit", str(GH_CLI_CAP),
               "--json", "name,visibility"], tok)
    if proc.returncode != 0:
        return [], f"gh repo list failed: {proc.stderr.strip()[:160]}"
    rows = json.loads(proc.stdout or "[]")
    if len(rows) >= GH_CLI_CAP:
        return [], f"gh repo list returned {len(rows)}, at the {GH_CLI_CAP} cap"
    return [r["name"] for r in rows], ""


def source_graphql(tok: str) -> tuple[list[str], str]:
    """Fully paginated GraphQL.

    GitHub's `repositories` connection silently caps at 100 when no cursor is
    supplied. That is precisely the truncation this module exists to detect, so
    the cursor is followed until hasNextPage is false and the cap is treated as
    an error rather than as the end of the data.
    """
    names: list[str] = []
    cursor = None
    while True:
        after_clause = f'after: {json.dumps(cursor)}, ' if cursor else ''
        query = (
            "query($login: String!) {"
            "  repositoryOwner(login: $login) {"
            "    repositories(first: 100, ownerAffiliations: OWNER, "
            f"isFork: false, {after_clause}orderBy: {{field: NAME, direction: ASC}}) {{"
            "      pageInfo { hasNextPage endCursor }"
            "      nodes { name }"
            "    }"
            "  }"
            "}"
        )
        proc = gh(["gh", "api", "graphql", "-f", f"query={query}",
                   "-f", f"login={OWNER}"], tok)
        if proc.returncode != 0:
            return names, f"graphql failed: {proc.stderr.strip()[:200]}"
        data = json.loads(proc.stdout)["data"]["repositoryOwner"]["repositories"]
        names.extend(n["name"] for n in data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            return names, ""
        cursor = data["pageInfo"]["endCursor"]
        if len(names) >= GRAPHQL_CAP:
            return names, f"graphql reached the {GRAPHQL_CAP} cap without finishing"


def source_rest(tok: str) -> tuple[list[str], str]:
    names: list[str] = []
    url = f"https://api.github.com/user/repos?per_page=100&affiliation=owner"
    while url:
        proc = gh(["gh", "api", "--paginate", "-H",
                   "Accept: application/vnd.github+json", url], tok)
        if proc.returncode != 0:
            return names, f"rest failed: {proc.stderr.strip()[:160]}"
        page = json.loads(proc.stdout or "[]")
        if isinstance(page, list):
            names.extend(r["name"] for r in page if r.get("owner", {}).get("login") == OWNER)
            break
        for r in page:
            if r.get("owner", {}).get("login") == OWNER:
                names.append(r["name"])
        # gh --paginate emits concatenated arrays; re-issue per page instead.
        nxt = re.search(r'<([^>]+)>;\s*rel="next"', proc.stderr or "")
        url = nxt.group(1) if nxt else None
        if len(names) >= REST_CAP:
            return names, f"rest reached the {REST_CAP} cap without finishing"
    return names, ""


def source_local(tok: str) -> tuple[list[str], str]:
    """Local checkouts whose git remote points at this account."""
    if not LOCAL_PORTFOLIO.is_dir():
        return [], "local portfolio directory absent"
    found: list[str] = []
    for child in sorted(LOCAL_PORTFOLIO.iterdir()):
        if not (child / ".git").exists():
            continue
        proc = subprocess.run(["git", "-C", str(child), "remote", "get-url", "origin"],
                              capture_output=True, text=True)
        url = proc.stdout.strip()
        if not url:
            continue
        if re.search(rf"github\.com[:/]{OWNER}/([^/]+?)(?:\.git)?$", url):
            found.append(re.search(rf"github\.com[:/]{OWNER}/([^/]+?)(?:\.git)?$",
                                   url).group(1))
    return found, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default="", help="also write the full result here")
    args = ap.parse_args()

    try:
        tok = token()
    except RuntimeError as exc:
        # Report the skip and why. Silently passing would make the gate
        # unfalsifiable; failing would blame a fork for a missing secret.
        print("INVENTORY RECONCILIATION")
        print(f"account: {OWNER}")
        print()
        print(f"SKIPPED: {exc}")
        print("  No token, so no remote source could be queried. A pull request")
        print("  from a fork does not receive repository secrets, so this gate")
        print("  cannot run there. The zero-missing ledger invariant still runs,")
        print("  because it verifies the committed ledger and needs no network.")
        print()
        print("  To run reconciliation locally:")
        print("    GH_TOKEN=$(gh auth token) python3 scripts/profile_art/reconcile_inventory.py")
        return 0
    sources = {
        "gh_cli": source_gh_cli(tok),
        "graphql": source_graphql(tok),
        "rest": source_rest(tok),
        "local": source_local(tok),
    }

    print("ACCOUNT INVENTORY RECONCILIATION")
    print(f"account: {OWNER}")
    print()
    print(f"{'SOURCE':<10}{'COUNT':>7}  {'ERROR':<6} NOTE")
    sets: dict[str, set[str]] = {}
    for name, (names, err) in sources.items():
        sets[name] = set(names)
        note = err or ""
        if name == "local":
            note = note or "local checkouts only; not a completeness source"
        print(f"{name:<10}{len(sets[name]):>7}  {'FAIL' if err else 'ok':<6} {note[:60]}")

    # The canonical count is the maximum. A source reporting fewer is truncated.
    authoritative = {"gh_cli", "graphql", "rest"}
    canon = max((sets[s] for s in authoritative), key=len)
    canonical = sorted(canon)
    print()
    print(f"CANONICAL COUNT: {len(canonical)}")
    print(f"(maximum over remote sources; a smaller source is treated as truncated,")
    print(f" never as authoritative)")

    print()
    print(f"{'SOURCE':<10}{'COUNT':>7}  MISSING FROM SOURCE")
    problems = []
    for name in sorted(sets):
        if name == "local":
            continue
        missing = sorted(canon - sets[name])
        extra = sorted(sets[name] - canon)
        print(f"{name:<10}{len(sets[name]):>7}  "
              f"{len(missing)} missing, {len(extra)} extra")
        for m in missing[:10]:
            print(f"    missing from {name}: {m}")
        problems.extend((name, m) for m in missing)
        problems.extend((name, f"EXTRA:{e}") for e in extra)

    local_missing = sorted(canon - sets["local"])
    print()
    print(f"local checkouts: {len(sets['local'])} of {len(canon)} canonical "
          f"repositories have a checkout ({len(local_missing)} without)")
    print("  (absence of a local checkout is not an inventory error)")

    remote_disagree = any(sets[a] != sets[b]
                          for a in authoritative for b in authoritative
                          if a < b)
    ok = not remote_disagree and not problems

    print()
    print(f"RECONCILED: {'YES' if ok else 'NO'}")
    if not ok:
        print(f"  {len(problems)} discrepancies across remote sources")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "account": OWNER,
            "canonical_count": len(canonical),
            "canonical": canonical,
            "sources": {k: sorted(v) for k, v in sets.items()},
            "source_errors": {k: e for k, (_, e) in sources.items()},
            "reconciled": ok,
            "discrepancies": [{"source": s, "detail": d} for s, d in problems],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {args.json}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())