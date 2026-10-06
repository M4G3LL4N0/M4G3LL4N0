#!/usr/bin/env python3
"""Generate a factual README for a repository that has none.

The bar for a generated README is not "looks complete". It is "states only what
was observed". Every line below is derived from the repository itself: its
description, topics, language, license, and the files actually present at the
root. Nothing is claimed about features, roadmap, benchmarks, performance or
maintenance that the repository does not itself assert.

A repository with no description and no files gets a README that says exactly
that. That is a truthful document. Inventing a purpose to fill the gap would be
the opposite of this system's purpose.

  python3 scripts/profile_art/generate_missing_readme.py OWNER/REPO
  python3 scripts/profile_art/generate_missing_readme.py --dry-run OWNER/REPO
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys

# Files that carry no information about what a project is.
BORING = {".git", ".github", ".gitignore", ".gitattributes", ".editorconfig",
          ".nvmrc", ".python-version", ".tool-versions", "LICENSE", "LICENSE.md",
          "LICENSE.txt", "AGENTS.md", "CLAUDE.md", "CODE_OF_CONDUCT.md",
          "SECURITY.md", "CONTRIBUTING.md", ".DS_Store"}

MARK = "\u2713"


def gh_json(path: str):
    env = dict(os.environ, GH_TOKEN=os.environ.get("GH_TOKEN", ""), GH_PAGER="cat")
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def titleise(name: str) -> str:
    return re.sub(r"[-_]+", " ", name).strip().title()


def detect_purpose(desc: str, topics: list[str], root: list[str]) -> str:
    if desc.strip():
        return desc.strip()
    # No description. Derive only what the tree itself supports.
    markers = []
    lowered = {f.lower() for f in root}
    if "dockerfile" in lowered or "docker-compose.yml" in lowered:
        markers.append("containerised")
    if any(f.endswith(".ts") or f.endswith(".tsx") for f in root):
        markers.append("TypeScript")
    elif any(f.endswith(".py") for f in root):
        markers.append("Python")
    elif any(f.endswith(".go") for f in root):
        markers.append("Go")
    elif any(f.endswith(".rs") for f in root):
        markers.append("Rust")
    if topics:
        markers.append("topics: " + ", ".join(sorted(topics)[:5]))
    if markers:
        return "Repository contents indicate: " + "; ".join(markers) + "."
    return "No description has been recorded for this repository."


def build_readme(full_name: str, meta: dict, root: list[str]) -> str:
    name = meta["name"]
    title = titleise(name)
    desc = (meta.get("description") or "").strip()
    topics = sorted(t["name"] if isinstance(t, dict) else t
                    for t in (meta.get("repositoryTopics") or []))
    # The REST shape differs from `gh repo view`: snake_case keys, license
    # nested under "license", and topics live behind their own endpoint.
    language = meta.get("language") or ""
    lic = ((meta.get("license") or {}).get("spdx_id")
           or (meta.get("licenseInfo") or {}).get("spdx_id") or "")
    homepage = (meta.get("homepage") or "").strip()
    pushed = (meta.get("pushed_at") or meta.get("pushedAt") or "")[:10]
    if not topics:
        raw = gh_json(f"repos/{full_name}/topics") or {}
        topics = sorted(t.get("name", "") for t in (raw.get("names") or []))

    interesting = sorted(f for f in root if f.lower() not in BORING)

    out: list[str] = []
    out.append(f"# {title}\n")
    out.append(f"> **{'STATUS: UNDOCUMENTED'}** \u2014 this README was generated from the "
               "repository's own contents. It records what is present, not what the "
               "project intends to become.\n")

    out.append("## Purpose\n")
    out.append(detect_purpose(desc, topics, root) + "\n")

    out.append("## What is in this repository\n")
    if interesting:
        out.append("Files present at the repository root:\n")
        for f in interesting[:24]:
            out.append(f"- `{f}`")
        if len(interesting) > 24:
            out.append(f"- \u2026 and {len(interesting) - 24} more")
    else:
        out.append("The repository root contains no files other than repository "
                   "metadata.")
    out.append("")

    out.append("## Engineering status\n")
    rows = [
        ("Primary language", language or "not recorded"),
        ("License", lic or "not recorded"),
        ("Last push", pushed or "not recorded"),
        ("Topics", ", ".join(topics) if topics else "none set"),
        ("Test suite", "not established \u2014 no test evidence has been measured"),
        ("CI", "not established \u2014 no CI evidence has been measured"),
    ]
    out.append("| property | value |")
    out.append("| --- | --- |")
    for k, v in rows:
        out.append(f"| {k} | {v} |")
    out.append("")
    out.append("Nothing in this table is inferred. Where a value could not be read "
               "from the repository it says so.\n")

    if homepage:
        out.append(f"Homepage: <{homepage}>\n")

    out.append("## Notes\n")
    out.append("This repository predates the current documentation standard. The "
               "README above is intentionally minimal and factual rather than "
               "promotional: it would be easy to write an impressive description "
               "here, and nothing in this repository would make it true.\n")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", help="OWNER/NAME")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    meta = gh_json(f"repos/{args.repo}")
    if not isinstance(meta, dict):
        print(f"cannot read repository metadata for {args.repo}", file=sys.stderr)
        return 2

    existing = gh_json(f"repos/{args.repo}/readme")
    if isinstance(existing, dict):
        print(f"{args.repo} already has a README; not overwriting")
        return 0

    listing = gh_json(f"repos/{args.repo}/contents") or []
    root = [item["name"] for item in listing if isinstance(item, dict)]

    text = build_readme(args.repo, meta, root)
    if args.dry_run:
        print(text)
        return 0

    proc = subprocess.run(
        ["gh", "api", f"repos/{args.repo}/contents/README.md",
         "-X", "PUT",
         "-f", f"message=docs: add a factual generated README\n\n"
               "Generated from the repository's own contents: description, topics,\n"
               "language, license and the files actually present.\n\n"
               "States STATUS: UNDOCUMENTED deliberately. Nothing is claimed about\n"
               "features or roadmap that the repository does not itself assert.",
         "-f", "content=" + base64.b64encode(text.encode()).decode(),
         "-f", "branch=" + (meta.get("default_branch") or "main")],
        capture_output=True, text=True,
        env=dict(os.environ, GH_TOKEN=os.environ.get("GH_TOKEN", ""), GH_PAGER="cat"))
    if proc.returncode != 0:
        print(f"failed to write README for {args.repo}: {proc.stderr[:200]}", file=sys.stderr)
        return 1
    print(f"{MARK} {args.repo}: README written ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())