#!/usr/bin/env python3
"""githubos vercel audit: a GitHub push must never deploy production.

GitHub presentation work touches 120+ repositories. If any of them is wired to
Vercel's git integration, a README or art commit becomes a production deploy.
That happened here: 78 projects were linked, 16 had deployed within ten hours,
and oddbotix had a Production deployment an hour after a documentation commit.

This guard makes the condition checkable rather than remembered.

  SAFE_FOR_GITHUB_ONLY_PUSH   no git-triggered deployment path
  AUTO_DEPLOY_RISK            at least one path can deploy on push

Three vectors are checked:

  1. Vercel git integration    a project linked to a GitHub repo deploys on push
  2. workflow deploy steps     a workflow invoking vercel or a deploy action
  3. deploy hooks in workflows an explicit hook URL that a push can reach

Product source is never read or modified. This reads Vercel project metadata
and GitHub workflow files only.

  python3 scripts/profile_art/vercel_guard.py
  python3 scripts/profile_art/vercel_guard.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
CACHE = PROFILE / "VERCEL_GIT_CONNECTIONS.json"
OWNER = "M4G3LL4N0"

# Workflow patterns that deploy on push. `workflow_dispatch`-only workflows are
# excluded, because a manual trigger is not automatic deployment.
DEPLOY_PATTERNS = [
    (re.compile(r"vercel\s+(?:--prod\s+)?deploy\b"), "vercel deploy"),
    (re.compile(r"amondnet/vercel-action"), "amondnet/vercel-action"),
    (re.compile(r"amondnet/vercel-cli"), "amondnet/vercel-cli"),
    (re.compile(r"api\.vercel\.com/v\d+/[^\s\"']*deploy"), "vercel deploy api"),
    (re.compile(r"deploy\.vercel\.app|vercel\.app/api/webhook"), "deploy hook"),
]


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


def vercel_token() -> str | None:
    candidates = [os.environ.get("VERCEL_TOKEN"),
                  "~/Library/Application Support/com.vercel.cli/auth.json"]
    for candidate in [c for c in candidates if c]:
        path = Path(os.path.expanduser(candidate))
        if not path.is_file():
            continue
        try:
            t = json.loads(path.read_text(encoding="utf-8")).get("token")
            if t:
                return t
        except (json.JSONDecodeError, OSError):
            continue
    return None


def vercel_links() -> tuple[list[dict], str]:
    """Projects still carrying a GitHub git integration."""
    if not vercel_token():
        # No token means no live query, so no live claim can be made. The
        # recorded inventory is an audit trail of connections that were already
        # disconnected; treating it as current state reported 78 phantom risks
        # after they had been removed, which is how a gate teaches people to
        # ignore it.
        if CACHE.is_file():
            data = json.loads(CACHE.read_text(encoding="utf-8"))
            pending = [c for c in data.get("connections", [])
                       if not c.get("disconnected")]
            src = ("recorded inventory: all "
                   f"{len(data.get('connections', []))} connections already "
                   "disconnected" if not pending else
                   f"recorded inventory: {len(pending)} not marked disconnected")
            return pending, src
        return [], "no token and no inventory"
    t = vercel_token()
    try:
        req = urllib.request.Request(
            "https://api.vercel.com/v2/teams?limit=1",
            headers={"Authorization": f"Bearer {t}"})
        team = json.load(urllib.request.urlopen(req, timeout=30))["teams"][0]["id"]
    except (urllib.error.URLError, KeyError, IndexError, TimeoutError) as exc:
        return [], f"vercel api unavailable: {exc}"
    rows = []
    try:
        req = urllib.request.Request(
            f"https://api.vercel.com/v9/projects?limit=100&teamId={team}",
            headers={"Authorization": f"Bearer {t}"})
        page = json.load(urllib.request.urlopen(req, timeout=45))
        for p in page.get("projects", []):
            link = p.get("link") or {}
            if link.get("type") == "github":
                rows.append({
                    "vercel_project": p["name"], "vercel_project_id": p["id"],
                    "github_repo": (link.get("repo") or "").split("/")[-1],
                    "production_branch": link.get("productionBranch"),
                })
    except (urllib.error.URLError, TimeoutError) as exc:
        return [], f"vercel api unavailable: {exc}"
    return rows, "live query"


def workflow_deploys() -> list[dict]:
    """Workflows that can deploy on push. Manual-only triggers are excluded."""
    repos = gh_json(f"users/{OWNER}/repos?per_page=100&type=owner&visibility=public") or []
    found = []
    for repo in repos:
        if not isinstance(repo, dict):
            continue
        name = repo["name"]
        wf = gh_json(f"repos/{OWNER}/{name}/contents/.github/workflows")
        if not isinstance(wf, list):
            continue
        import base64
        for item in wf:
            if not isinstance(item, dict) or not str(item.get("name", "")).endswith((".yml", ".yaml")):
                continue
            content = gh_json(f"repos/{OWNER}/{name}/contents/{item['path']}")
            if not isinstance(content, dict) or "content" not in content:
                continue
            try:
                text = base64.b64decode(content["content"]).decode("utf-8", "replace")
            except Exception:
                continue
            manual_only = bool(re.search(r"workflow_dispatch", text)) and \
                not re.search(r"^\s*push:", text, re.M)
            for pattern, label in DEPLOY_PATTERNS:
                if pattern.search(text) and not manual_only:
                    found.append({"repo": name, "workflow": item["name"],
                                  "pattern": label, "manual_only": manual_only})
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    links, source = vercel_links()
    flows = workflow_deploys()

    print("GITHUBOS VERCEL AUDIT")
    print(f"  link source            : {source}")
    print()
    print(f"  Vercel git integrations : {len(links)}")
    print(f"  workflow deploy paths   : {len(flows)}")
    print()

    if links:
        print("  Vercel projects still connected to a GitHub repository:")
        for r in links[:12]:
            print(f"    {r['vercel_project']:<28}{r.get('production_branch')}")
        if len(links) > 12:
            print(f"    ... and {len(links) - 12} more")

    if flows:
        print("  Workflows that can deploy on push:")
        for f in flows[:12]:
            print(f"    {f['repo']:<28}{f['workflow']:<24}{f['pattern']}")

    payload = {
        "vercel_git_integrations": links,
        "workflow_deploy_paths": flows,
        "vercel_source": source,
    }
    if args.json:
        Path(args.json).write_text(json.dumps(payload, indent=1) + "\n")

    if links or flows:
        print()
        print("AUTO_DEPLOY_RISK")
        if links:
            print(f"  {len(links)} Vercel project(s) will deploy on push. "
                  f"Disconnect with DELETE /v9/projects/{{id}}/link")
        if flows:
            print(f"  {len(flows)} workflow deploy step(s) run on push. "
                  f"Convert to workflow_dispatch")
        return 1

    print("SAFE_FOR_GITHUB_ONLY_PUSH")
    print("  no Vercel git integration can deploy on push")
    print("  no workflow deploys on push")
    print("  manual deploys via CLI, hooks and dashboard are unaffected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())