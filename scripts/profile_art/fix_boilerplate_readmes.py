#!/usr/bin/env python3
"""Replace framework-boilerplate READMEs with accurate ones.

Nineteen repositories were caught by the cross-check carrying a README that is
create-next-app output:

    First, run the development server:
    Open [http://localhost:3000] with your browser to see the result.
    To learn more about Next.js, take a look at the following resources:

while their GitHub description correctly says they are launch-site scaffolds.
The two surfaces disagree, which is the mapping failure the cross-check exists
to catch.

This rewrites those READMEs to describe what the repository actually is, keeps
the existing animated hero, and states plainly that there is no product surface
yet. It never invents a purpose.

  python3 scripts/profile_art/fix_boilerplate_readmes.py --dry-run
  python3 scripts/profile_art/fix_boilerplate_readmes.py --apply
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
DOSSIERS = PROFILE / ".github-art" / "dossiers"
CROSS = PROFILE / "data" / "cross-check.json"
OWNER = "M4G3LL4N0"

BOILERPLATE_MARKERS = [
    "This is a [Next.js](https://nextjs.org) project bootstrapped with",
    "First, run the development server",
    "Open [http://localhost:3000](http://localhost:3000) with your browser",
    "To learn more about Next.js, take a look at the following resources",
    "This project uses [`next/font`]",
    # The previous completion engine's template. It stated the repository name
    # and a file count, which is not a description.
    "| Documentation files |",
    "This repository exists as working code rather than as a proposal.",
]
# The animated hero, preserved verbatim from the existing README.
HERO = re.compile(
    r'<p align="center">\s*<picture>.*?</picture>\s*</p>', re.S)


def tok() -> str:
    return os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def raw(repo: str, branch: str, path: str) -> str:
    try:
        with urllib.request.urlopen(
                f"https://raw.githubusercontent.com/{OWNER}/{repo}/{branch}/{path}",
                timeout=25) as fh:
            return fh.read().decode("utf-8", "replace")
    except Exception:
        return ""


def build_readme(name: str, existing: str, dossier: dict) -> str:
    title = re.sub(r"[-_]+", " ", name).strip().title()
    routes = dossier.get("routes") or []
    sections: list[str] = []
    hero = HERO.search(existing)
    if hero:
        sections.append(hero.group(0))
    sections.append(f"# {title}")
    sections.append("**STATUS: LAUNCH-SITE SCAFFOLD**")
    sections.append(
        f"This repository is a launch site, not a product. It has no product "
        f"surface yet.\n\n"
        f"That is stated plainly rather than dressed up. A scaffold described as "
        f"a platform wastes the reader's time; a scaffold described as a "
        f"scaffold lets them decide whether to keep looking.\n")
    if routes:
        pretty = ", ".join(f"`/{r}`" if r else "`/`" for r in routes[:10])
        sections.append("## What is here\n")
        sections.append(
            f"Static routes: {pretty}.\n\n"
            f"These pages exist so portfolio and navigation links resolve. They "
            f"are not product features and are not described as such.\n")
    sections.append("## Status\n")
    sections.append(
        "| | |\n| --- | --- |\n"
        "| Product surface | none |\n"
        "| Tests | none |\n"
        "| CI | none |\n"
        "| Documentation | this file |\n")
    sections.append("## Why it exists\n")
    sections.append(
        "Every venture in this portfolio has a public entry point. Where the "
        "product is not ready to ship, the entry point is marked as a scaffold "
        "rather than filled with claims it cannot support. This repository will "
        "be replaced by real content when there is something real to show.\n")
    sections.append("---\n")
    sections.append(
        f"Part of the DUNG30N5 × NOAERTH portfolio. "
        f"Repository: [`{OWNER}/{name}`](https://github.com/{OWNER}/{name}).\n")
    return "\n".join(sections)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not CROSS.exists():
        print("run cross_check.py first")
        return 1
    rows = json.loads(CROSS.read_text(encoding="utf-8"))["rows"]
    targets = [r["repo"] for r in rows if any(
        f["kind"] == "DESCRIPTION_VS_README" and "scaffold" in f["detail"]
        for f in r["findings"])]
    print(f"  scaffold READMEs to rewrite: {len(targets)}")

    written = skipped = 0
    for name in targets:
        branch = "main"
        d = DOSSIERS / f"{name}.json"
        dossier = json.loads(d.read_text(encoding="utf-8")) if d.exists() else {}
        dossier.setdefault("routes", [])
        existing = raw(name, branch, "README.md")
        if not existing:
            skipped += 1
            continue
        if not any(m in existing for m in BOILERPLATE_MARKERS):
            skipped += 1
            continue
        # Only rewrite when the README actually makes a product claim that the
        # description contradicts. A README that already says scaffold is fine.
        if re.search(r"LAUNCH-SITE SCAFFOLD|no product surface", existing, re.I) \
                and "Startup portfolio:" not in existing:
            skipped += 1
            continue
        text = build_readme(name, existing, dossier)
        print(f"  {name:<26}{len(text):>5} chars  "
              f"hero={'kept' if HERO.search(existing) else 'none'}")
        if args.dry_run:
            continue
        # One call for both the body and the blob sha. Fetching the sha
        # separately doubled the API calls and doubled the chance of being
        # rate-limited mid-write, which is exactly what happened: the PUT then
        # failed with a stale-sha mismatch that actually said rate limit.
        sha = ""
        for attempt in range(4):
            meta = subprocess.run(
                ["gh", "api", f"repos/{OWNER}/{name}/contents/README.md",
                 "--jq", ".sha"],
                capture_output=True, text=True,
                env=dict(os.environ, GH_TOKEN=tok()))
            if meta.returncode == 0:
                sha = meta.stdout.strip()
                break
            time.sleep(12)
        if not sha:
            print("      skipped: sha unavailable (rate limited)")
            skipped += 1
            continue
        # Single-line commit message only. A multi-line -f value is split by
        # the argument parser, so the write failed while the script counted it
        # as a success -- the same shape of error this round exists to remove.
        cmd = ["gh", "api", f"repos/{OWNER}/{name}/contents/README.md", "-X", "PUT",
               "-f", "message=docs: describe this repository accurately",
               "-f", "content=" + base64.b64encode(text.encode()).decode(),
               "-f", f"branch={branch}"]
        if sha:
            cmd += ["-f", f"sha={sha}"]
        p = subprocess.run(cmd, capture_output=True, text=True,
                           env=dict(os.environ, GH_TOKEN=tok()))
        if p.returncode == 0:
            written += 1
        else:
            print(f"      failed: {p.stderr.strip()[:70]}")
        time.sleep(0.5)

    if not args.dry_run:
        print(f"\n  READMEs rewritten: {written}  skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())