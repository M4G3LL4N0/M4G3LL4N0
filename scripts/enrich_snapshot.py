#!/usr/bin/env python3
"""Enrich a raw ``gh api user/repos`` dump with the fields GitHubOS needs.

Reads a JSON array of repository objects and writes a JSON array to stdout
with four extra keys per public repository:

    root_files    names of the files at the repository root
    has_ci        whether .github/workflows contains any YAML workflow
    release_count number of GitHub releases
    latest_release tag name of the most recently published release

test_count is **not** fetched from GitHub, because no endpoint reports how many
tests a project has. Instead it is read from tests.json in this repository,
which an operator fills in after actually running the suite. A repository with
no entry renders as an em dash on the profile. That is the intended behaviour:
never substitute an estimate for a measurement.

Uses only the standard library. Run with the token in GH_TOKEN.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

API = "https://api.github.com"


def _token() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        raise SystemExit("GH_TOKEN is not set")
    return token


def _get(path: str) -> Any:
    request = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Authorization": f"Bearer {_token()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "noaerth-githubos",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise


def enrich(repo: dict[str, Any], recorded_tests: dict[str, int]) -> dict[str, Any]:
    name = repo["name"]
    repo["test_count"] = recorded_tests.get(name, 0)
    repo["license_spdx"] = str((repo.get("license") or {}).get("spdx_id") or "")
    if repo.get("visibility") != "public":
        repo.update({"root_files": [], "has_ci": False,
                     "release_count": 0, "latest_release": ""})
        return repo

    root = _get(f"/repos/{repo['full_name']}/contents")
    workflows = _get(f"/repos/{repo['full_name']}/contents/.github/workflows")
    releases = _get(f"/repos/{repo['full_name']}/releases?per_page=100")

    repo["root_files"] = [item["name"] for item in root if isinstance(item, dict)]
    repo["has_ci"] = any(
        str(item.get("name", "")).endswith((".yml", ".yaml")) for item in workflows
    )
    repo["release_count"] = len(releases)
    repo["latest_release"] = releases[0]["tag_name"] if releases else ""
    return repo


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: enrich_snapshot.py repos-raw.json > repos.json", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as handle:
        repos = json.load(handle)
    if not isinstance(repos, list):
        print("expected a JSON array of repositories", file=sys.stderr)
        return 2

    # Verified test counts, recorded by an operator. A missing entry means the
    # count is unknown, and unknown must render as unknown.
    recorded: dict[str, int] = {}
    tests_path = Path(__file__).resolve().parents[1] / "tests.json"
    if tests_path.is_file():
        raw = json.loads(tests_path.read_text(encoding="utf-8"))
        for key, value in raw.items():
            if key.startswith("_") or not isinstance(value, dict):
                continue
            recorded[key] = int(value.get("count") or 0)

    with ThreadPoolExecutor(max_workers=6) as pool:
        enriched = list(pool.map(lambda r: enrich(r, recorded), repos))

    json.dump(enriched, sys.stdout, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
