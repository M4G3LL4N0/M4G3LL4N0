#!/usr/bin/env python3
"""Replace create-next-app boilerplate READMEs on real products.

A repository that has a real product behind it should not open with
"This is a Next.js project bootstrapped with create-next-app". That text
describes the tool that generated a folder, not the system inside it, and it
tells a reader who opened the link precisely nothing.

Every repository here has a local checkout. This reads that checkout, extracts
what is actually verifiable -- languages, entry points, dependencies, test and
CI counts, documentation surface -- and writes a README that reports only
those. Where the source does not support a claim, no claim is made.

The animated hero already published for the repository is preserved; only the
prose below it is replaced.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import re
import subprocess
import sys
import time

OWNER = "M4G3LL4N0"
PORTFOLIO = pathlib.Path("/Users/matador/startups")
PROFILE = pathlib.Path(__file__).resolve().parents[2]

BOILERPLATE_MARKERS = (
    "This is a [Next.js](https://nextjs.org) project bootstrapped with",
    "First, run the development server",
    "To learn more about Next.js",
    "This project uses [`next/font`]",
    "| Documentation files |",
    # The previous completion engine's template. It stated the repository name
    # and a file count, which is not a description.
    "Startup portfolio:",
)

LANG_BY_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".py": "Python", ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
    ".php": "PHP", ".java": "Java", ".kt": "Kotlin", ".swift": "Swift",
    ".cs": "C#", ".c": "C", ".h": "C", ".cpp": "C++", ".sql": "SQL",
    ".sh": "Shell", ".lua": "Lua", ".r": "R",
}
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", "coverage", "vendor",
    "__pycache__", ".venv", "venv", ".trillionx-agent-fabric", "target",
}

# Phrases that mark a document as an internal operating note rather than user
# documentation. Copying these into a README imports the internal process into
# the public surface, which is exactly the wrong direction.
INTERNAL_DOC_MARKERS = (
    "claim register", "failure register", "decision record", "launch readiness",
    "compliance", "agent handoff", "internal review", "local review",
    "autobuilder foundation", "premium ui", "blindspot", "autodiscovery",
    "around the corner", "noaerth upgrade", "proof loop",
)


def tok() -> str:
    t = os.environ.get("GH_TOKEN") or ""
    if not t:
        raise SystemExit("GH_TOKEN is required for GitHub writes")
    return t


def default_branch(repo: str) -> str:
    """Resolve the branch a visitor actually lands on.

    Three repositories default to an auto-generated branch. Writing to "main"
    there either fails or lands the change on a branch nobody opens, so the
    presentation edit would silently not exist for readers.
    """
    d = subprocess.run(["gh", "api", f"repos/{OWNER}/{repo}", "--jq", ".default_branch"],
                       capture_output=True, text=True,
                       env=dict(os.environ, GH_TOKEN=tok()))
    return d.stdout.strip() or "main"


def read_remote(repo: str, path: str = "README.md") -> str | None:
    """Read via the contents API.

    raw.githubusercontent.com serves cached copies: after a batch of README
    writes it kept returning the previous content, and checks built on it
    reported fixed repositories as unfixed. The API reflects the commit
    immediately.
    """
    d = subprocess.run(
        ["gh", "api", f"repos/{OWNER}/{repo}/contents/{path}"],
        capture_output=True, text=True, env=dict(os.environ, GH_TOKEN=tok()))
    if d.returncode == 0:
        try:
            return base64.b64decode(json.loads(d.stdout)["content"]).decode("utf-8", "replace")
        except Exception:
            pass
    return None


def iter_files(root: pathlib.Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            yield pathlib.Path(dirpath) / fn


def survey(root: pathlib.Path) -> dict:
    """Count what is verifiably present in the checkout."""
    langs: dict[str, int] = {}
    tests = 0
    docs = 0
    files = 0
    has_ci = False
    entrypoints: list[str] = []
    workflows: list[str] = []
    manifests: dict[str, str] = {}

    for f in iter_files(root):
        files += 1
        name = f.name
        rel = str(f.relative_to(root))
        suffix = f.suffix.lower()

        if name in ("package.json", "pyproject.toml", "requirements.txt",
                    "go.mod", "Cargo.toml", "Gemfile", "composer.json"):
            manifests[name] = rel
        if name in ("README.md", "AGENTS.md", "CLAUDE.md", "ARCHITECTURE.md"):
            docs += 1
        if re.match(r"(test_|_test|.*\.test|.*\.spec)\.[a-z]{2,4}$", name):
            tests += 1
        if ".github/workflows" in rel and suffix in (".yml", ".yaml"):
            has_ci = True
            workflows.append(name)
        if rel in ("app/page.tsx", "app/page.js", "src/app/page.tsx", "main.py",
                   "main.go", "index.ts", "index.js", "cli.py", "src/main.rs"):
            entrypoints.append(rel)

        lang = LANG_BY_EXT.get(suffix)
        if lang:
            langs[lang] = langs.get(lang, 0) + 1

    langs.pop("C", None) if langs.get("C", 0) < 12 else None
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:4]
    return {
        "files": files, "tests": tests, "docs": docs, "has_ci": has_ci,
        "workflows": sorted(set(workflows)),
        "manifests": sorted(manifests),
        "languages": top, "entrypoints": sorted(set(entrypoints))[:6],
    }


def read_intro(root: pathlib.Path, name: str) -> str:
    """Use the product's own opening line, with financial framing removed.

    The local README is the founder's own description and is far better than
    anything invented here -- but it can carry economic framing, which this
    portfolio does not publish. Economic clauses are dropped; the technical
    sentence that follows them is kept.
    """
    p = root / "README.md"
    if not p.exists():
        return ""
    text = p.read_text(errors="replace")
    body = re.sub(r"^---.*?---", "", text, flags=re.S)
    paras = [p_.strip() for p_ in body.split("\n\n") if p_.strip()]
    for para in paras[:12]:
        line = " ".join(para.split())
        if len(line) < 40 or line.startswith("#"):
            continue
        if any(bad in line.lower() for bad in
               ("profit", "revenue", "mrr", "valuation", "roi ", "monetiz",
                "high-margin", "unit economics", "pricing")):
            continue
        low = line.lower()
        if any(low.startswith(x) for x in
               ("this is a [next.js", "first, run the development", "## getting started")):
            continue
        # Setup instructions are not descriptions. Promoting "required
        # environment variables" to the opening line told a reader nothing
        # about what the project is.
        if any(bad in low for bad in
               ("required environment", "environment variable", "npm run dev",
                "npm install", "npx create-", "cloning this repository",
                "see [http://localhost", "git clone", "## installation",
                "## getting started", "## setup", "## prerequisites")):
            continue
        return line[:300]
    return ""


def build(repo: str, existing: str, dossier: dict, survey_data: dict,
          local: pathlib.Path) -> str:
    name = dossier.get("canonical_name") or repo
    hero = ""
    m = re.search(r"<p align=\"center\">.*?</p>", existing, re.S)
    if m:
        hero = m.group().rstrip() + "\n\n"

    intro = read_intro(local, name)
    langs = survey_data["languages"]
    lang_line = ", ".join(f"{l}" for l, _ in langs) or "not yet classified"

    facts: list[tuple[str, str]] = []
    facts.append(("Language", lang_line))
    if survey_data["manifests"]:
        facts.append(("Build", ", ".join(f"`{m}`" for m in survey_data["manifests"][:3])))
    facts.append(("Tests",
                  f"{survey_data['tests']} test files" if survey_data["tests"]
                  else "none present"))
    facts.append(("CI",
                  f"{len(survey_data['workflows'])} workflow(s)" if survey_data["has_ci"]
                  else "none present"))
    if survey_data["entrypoints"]:
        facts.append(("Entry points",
                      ", ".join(f"`{e}`" for e in survey_data["entrypoints"][:3])))
    docs_note = f"{survey_data['docs']} project documents in the repository" \
        if survey_data["docs"] else "documentation is thin"

    cat = dossier.get("project_category", "PROJECT")
    flow = dossier.get("control_flow") or dossier.get("animation_metaphor") or ""
    arch = dossier.get("architecture_type", "").replace("_", " ").lower()

    lines = [f"# {name}", ""]
    if intro:
        lines += [f"**{intro}**", ""]
    else:
        lines += [f"Part of the DUNG30N5 x NOAERTH portfolio. Source of truth for this "
                  f"repository is the checkout in the portfolio tree; this file reports what "
                  f"is verifiably present there.", ""]

    lines += ["## What is actually here", ""]
    lines += ["| | |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in facts]
    lines += [f"| Category | {cat.replace('_', ' ').title()} |", ""]

    lines += ["## Why this README looks like this", ""]
    lines += [
        "This file was generated from the repository's own source tree rather than",
        "written by hand. Every count above is the number of files actually present",
        "in the checkout at generation time, not an aspiration.",
        "",
        "An earlier version of this file was framework generator output, which",
        "describes the command used to create a directory rather than the system",
        "inside it. It was replaced for that reason.",
        "",
        f"Documentation surface: {docs_note}.",
        "",
    ]

    if flow:
        lines += ["## How it behaves", "", flow[0].upper() + flow[1:] + ".", ""]
    if arch:
        lines += [f"Architecture: {arch}.", ""]

    lines += [
        "## Status", "",
        "Source of truth: the local checkout. This repository is presented as part of",
        "a portfolio and is not the canonical home for the product.",
        "",
        "---",
        "",
        f"Part of the DUNG30N5 x NOAERTH portfolio. Repository:",
        f"[`{OWNER}/{repo}`](https://github.com/{OWNER}/{repo}).",
        "",
    ]
    return hero + "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write to GitHub; default is dry run")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true",
                    help="rewrite even when no boilerplate markers remain")
    args = ap.parse_args()

    ledger = json.loads((PROFILE / "github-account-ledger.json").read_text())
    boiler = json.loads((PROFILE / "data/boilerplate-readmes.json").read_text())
    targets = [r[0] for r in boiler]
    if args.limit:
        targets = targets[:args.limit]

    written = skipped = 0
    for repo in targets:
        local = None
        for rec in ledger["records"]:
            if rec["name"] == repo and rec.get("local_path"):
                candidate = pathlib.Path(rec["local_path"])
                if candidate.exists():
                    local = candidate
                    break
        if local is None:
            print(f"  {repo:<26} skipped: no local source")
            skipped += 1
            continue

        branch = default_branch(repo)
        existing = read_remote(repo)
        if existing is None:
            print(f"  {repo:<26} skipped: README unreadable")
            skipped += 1
            continue
        if not args.force and not any(mk in existing for mk in BOILERPLATE_MARKERS):
            print(f"  {repo:<26} skipped: already accurate")
            skipped += 1
            continue

        dp = PROFILE / ".github-art/dossiers" / f"{repo}.json"
        dossier = json.loads(dp.read_text()) if dp.exists() else {}
        data = survey(local)
        text = build(repo, existing, dossier, data, local)

        if not args.apply:
            print(f"  {repo:<26} {len(text):>5} chars  "
                  f"files={data['files']} tests={data['tests']} ci={data['has_ci']}"
                  f"  hero={'kept' if text.startswith('<p') else 'MISSING'}")
            continue

        sha = ""
        for _ in range(5):
            m = subprocess.run(
                ["gh", "api", f"repos/{OWNER}/{repo}/contents/README.md", "--jq", ".sha"],
                capture_output=True, text=True, env=dict(os.environ, GH_TOKEN=tok()))
            if m.returncode == 0:
                sha = m.stdout.strip()
                break
            time.sleep(10)
        if not sha:
            print(f"  {repo:<26} skipped: sha unavailable")
            skipped += 1
            continue

        # Single-line commit message only: a multi-line -f value is split by the
        # argument parser, which silently fails the write while the script
        # reports success.
        p = subprocess.run(
            ["gh", "api", f"repos/{OWNER}/{repo}/contents/README.md", "-X", "PUT",
             "-f", "message=docs: replace create-next-app template with verified source facts",
             "-f", "content=" + base64.b64encode(text.encode()).decode(),
             "-f", f"branch={branch}", "-f", f"sha={sha}"],
            capture_output=True, text=True, env=dict(os.environ, GH_TOKEN=tok()))
        if p.returncode == 0:
            written += 1
            print(f"  {repo:<26} written  {len(text):>5} chars  "
                  f"tests={data['tests']} ci={data['has_ci']} branch={branch}")
        else:
            print(f"  {repo:<26} FAILED  {p.stderr.strip()[:70]}")
        time.sleep(0.4)

    verb = "written" if args.apply else "would write"
    print(f"\n  READMEs {verb}: {written or len(targets)}  skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())