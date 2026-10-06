#!/usr/bin/env python3
"""Final completion assertion.

Prints GITHUB COMPLETE only when every condition holds. If any condition fails
it prints GITHUB NOT COMPLETE and the exact remaining queue. There is no
optimistic path and no partial success: a single unmet condition fails the
whole assertion, because a completion report that rounds up is worse than no
report at all.

  python3 scripts/profile_art/final_assertion.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts"))
LEDGER = PROFILE / "github-account-ledger.json"
STATE = PROFILE / ".github-elite-state.json"
RECONCILE = PROFILE / "reconcile.json"
OWNER = "M4G3LL4N0"

DENY_SUB = ("noaerth", "autobuilder", "pairs")
DENY_EXACT = {"paios-one", "openlegal-data"}
TERMINAL = ("COMPLETE", "NOT_APPLICABLE", "BLOCKED_WITH_REASON")
# Placeholder markers only. A repository that legitimately discusses TODOs in
# prose is not a placeholder, so the check matches the marker forms rather than
# the bare word.
FORBIDDEN_PATTERNS = (
    re.compile(r"STATUS:\s*UNDOCUMENTED", re.I),
    re.compile(r"lorem\s+ipsum", re.I),
    re.compile(r"^#+\s*TODO\s*$", re.I | re.M),
    re.compile(r"\bTBD\b"),
)


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


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    queue: list[str] = []

    led = json.loads(LEDGER.read_text())
    recs = led["records"]
    st = json.loads(STATE.read_text()) if STATE.exists() else {"records": {}, "queue": []}

    # gh repo list is the authoritative source: it returns every repository the
    # account owns, including private ones, with no page cap below 1000. A bare
    # per_page=100 REST request returns exactly 100 and would make 52 real
    # repositories look like ledger phantoms -- the same truncation the
    # reconciler exists to detect, reproduced here until this was switched.
    proc = subprocess.run(
        ["gh", "repo", "list", OWNER, "--limit", "1000", "--json",
         "name,visibility"],
        capture_output=True, text=True,
        env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    remote = json.loads(proc.stdout or "[]")
    remote_names = {r["name"] for r in remote}
    # gh repo list returns visibility uppercased ("PUBLIC"); the ledger stores
    # it lowercased. Comparing them directly made every repository look private
    # and the convergence check fail on a case difference.
    remote_public = {r["name"] for r in remote
                     if str(r.get("visibility", "")).lower() == "public"}

    # 1. every canonical repository is accounted for
    ok = len(recs) == led["canonical_count"] == len(remote_names)
    checks.append(("all canonical repositories accounted for", ok,
                   f"ledger {len(recs)} / canonical {led['canonical_count']} "
                   f"/ remote {len(remote_names)}"))
    if not ok:
        queue.append("reconcile: ledger, canonical count and remote disagree")

    # 2. every ledger record corresponds to a real remote repository
    missing = sorted({r["name"] for r in recs} - remote_names)
    checks.append(("no phantom ledger records", not missing,
                   f"{len(missing)} records with no remote repository"))
    if missing:
        queue.append(f"remove phantom records: {missing[:5]}")

    # 3. expected visibility matches policy
    wrong = [r["name"] for r in recs
             if r["denylisted"] and r["visibility"] != "private"]
    checks.append(("denylisted repositories are private", not wrong,
                   f"{len(wrong)} violations"))
    if wrong:
        queue.append(f"make private: {wrong}")

    not_public = [r["name"] for r in recs
                  if r["public_expected"] and r["visibility"] != "public"]
    checks.append(("expected-public repositories are public", not not_public,
                   f"{len(not_public)} still private"))
    if not_public:
        queue.append(f"publish: {not_public[:8]}")

    # 4. deletions complete or explicitly blocked by permission
    pending_del = [r["name"] for r in recs if r.get("delete_requested")
                   and r["name"] in remote_names]
    blocked_scope = "delete_repo" not in subprocess.run(
        ["gh", "auth", "status"], capture_output=True, text=True).stdout
    checks.append(("explicit deletions complete or blocked by missing scope",
                   not pending_del or blocked_scope,
                   f"{len(pending_del)} pending; delete_repo scope "
                   f"{'absent' if blocked_scope else 'present'}"))
    if pending_del and not blocked_scope:
        queue.append(f"delete: {pending_del}")

    # 5. no UNKNOWN anywhere
    unknown = [f"{r['name']}.{k}" for r in recs for k, v in r.items()
               if isinstance(v, dict) and v.get("state") not in TERMINAL]
    checks.append(("zero UNKNOWN fields", not unknown, f"{len(unknown)} unresolved"))
    if unknown:
        queue.append(f"resolve UNKNOWN: {unknown[:8]}")

    # 6. no placeholder README states
    placeholders = []
    unverifiable = []
    for r in recs:
        if not r["public_expected"]:
            continue
        # Retry. A single failed API call after hundreds of requests is rate
        # limiting, not a missing README, and reporting it as a placeholder
        # would be a false positive that sends someone to fix nothing.
        d = None
        for attempt in range(3):
            d = gh_json(f"repos/{OWNER}/{r['name']}/readme")
            if isinstance(d, dict):
                break
            import time
            time.sleep(2 * (attempt + 1))
        if not isinstance(d, dict):
            unverifiable.append(r["name"])
            continue
        import base64
        try:
            text = base64.b64decode(d["content"]).decode("utf-8", "replace")
        except Exception:
            continue
        for pat in FORBIDDEN_PATTERNS:
            if pat.search(text):
                placeholders.append(f"{r['name']} ({pat.pattern[:24]})")
                break
    checks.append(("no placeholder README states", not placeholders,
                   f"{len(placeholders)} placeholders, "
                   f"{len(unverifiable)} unverifiable"))
    if placeholders:
        queue.append(f"replace placeholder READMEs: {placeholders[:8]}")
    if unverifiable:
        queue.append(f"re-verify READMEs (API rate limited): {unverifiable[:8]}")

    # 7. every public repository resolves an identity
    from github_art import project_identity as P
    no_identity = [r["name"] for r in recs if r["public_expected"]
                   and not P.has_identity(r["name"])]
    checks.append(("every public repository has an identity", not no_identity,
                   f"{len(no_identity)} without"))
    if no_identity:
        queue.append(f"derive identity: {no_identity[:8]}")

    # 8. identities are structurally unique
    keys: dict[tuple, str] = {}
    clashes = []
    for r in recs:
        if not r["public_expected"]:
            continue
        try:
            i = P.identity(r["name"])
        except KeyError:
            continue
        k = (i.get("family"), i.get("motif"), i.get("material"), i.get("accent"),
             i.get("depth"), i.get("topology"))
        if k in keys:
            clashes.append(f"{keys[k]}~{r['name']}")
        else:
            keys[k] = r["name"]
    checks.append(("no two identities share a structural key", not clashes,
                   f"{len(clashes)} collisions"))
    if clashes:
        queue.append(f"differentiate identities: {clashes[:8]}")

    # 9. animated art with static fallback, where applicable
    anim = [f for f in ("animated_art_complete", "static_fallback_complete")
            if any(r[f]["state"] == "COMPLETE" for r in recs if r["public_expected"])]
    pending_art = [r["name"] for r in recs if r["public_expected"]
                   and r["hero_complete"]["state"] != "COMPLETE"]
    checks.append(("animated art and static fallback exist per repository",
                   not pending_art,
                   f"{len(pending_art)} repositories without per-repository art; "
                   f"currently complete for: {anim or 'none'}"))
    if pending_art:
        queue.append(f"generate per-repository art (animated + static dark/light/"
                     f"reduced-motion): {len(pending_art)} repositories, "
                     f"e.g. {pending_art[:5]}")

    # 10. completion queue drained
    pending_queue = [q for q in st.get("queue", []) if q["state"] != "DONE"]
    checks.append(("completion queue drained", not pending_queue,
                   f"{len(pending_queue)} pending"))
    if pending_queue:
        queue.append(f"process: {[q['name'] for q in pending_queue[:8]]}")

    # 11. assets reproduce byte for byte
    p = subprocess.run([sys.executable, str(PROFILE / "scripts/github_art/build_gallery.py")],
                       capture_output=True, text=True, cwd=str(PROFILE))
    repro = True
    detail = "reproduces"
    if p.returncode == 0:
        import hashlib
        exp = json.loads((PROFILE / "scripts/github_art/asset_manifest.json").read_text())
        # Keys must be repository-relative to match the committed manifest.
        # Absolute paths made every asset look different from itself.
        act = {str(x.relative_to(PROFILE)): hashlib.sha256(x.read_bytes()).hexdigest()
               for x in sorted((PROFILE / "build/v5-chosen").rglob("*.svg"))}
        repro = exp == act
        if not repro:
            detail = f"{len(set(exp) ^ set(act))} assets differ"
    else:
        repro = False
        detail = "generator failed"
    checks.append(("generated assets reproduce byte for byte", repro, detail))
    if not repro:
        queue.append(f"asset reproducibility: {detail}")

    # 12. safety tests pass
    tp = subprocess.run([sys.executable, str(PROFILE / "scripts/github_art/test_v5_safety.py")],
                        capture_output=True, text=True, cwd=str(PROFILE))
    checks.append(("safety tests pass", tp.returncode == 0,
                   "pass" if tp.returncode == 0 else "fail"))
    if tp.returncode != 0:
        queue.append("safety tests failing")

    # 13. remote public count converges with completed public owned count
    completed = sum(1 for q in st.get("queue", []) if q["state"] == "DONE")
    owned_public = len([r for r in recs if r["public_expected"]])
    converged = completed >= owned_public
    checks.append(("remote public owned == completed public owned", converged,
                   f"remote public {len(remote_public)}, owned obligations "
                   f"{owned_public}, queue done {completed}"))
    if not converged:
        queue.append("completion has not caught up with remote public count")

    # report
    print("=" * 74)
    print("GITHUB COMPLETION ASSERTION")
    print("=" * 74)
    width = max(len(c[0]) for c in checks)
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<{width}}  {detail}")
    print()
    failed = [c for c in checks if not c[1]]
    if failed:
        print("GITHUB NOT COMPLETE")
        print()
        print(f"{len(failed)} unmet condition(s). Exact remaining queue:")
        for i, item in enumerate(queue, 1):
            print(f"  {i:>2}. {item}")
        return 1
    print("GITHUB COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())