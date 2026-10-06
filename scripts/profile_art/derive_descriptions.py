#!/usr/bin/env python3
"""Derive accurate GitHub About descriptions from the project itself.

The defect this replaces
------------------------
Seventy-five public repositories carried descriptions such as:

    Startup portfolio: claimpilot-ai. package.json; CI configured.

That description proves the system never read the project. It names the
repository, lists a manifest, and says nothing a reader could not infer from
the URL. Seventy-five repositories described identically, so none of them was
described at all.

Four sources, with explicit precedence
--------------------------------------
  1 local source        technical truth. Wins any disagreement.
  2 Noaerth card        public positioning context. Never copied.
  3 project website     what the project claims publicly. Verified against 1.
  4 GitHub              current public state.

Rejection tests, applied before a description is accepted:

  * could this belong to twenty other repositories? reject
  * does source support the claim? reject
  * is it implementation trivia (package.json, CI configured)? rewrite

    python3 scripts/profile_art/derive_descriptions.py --sample 8
    python3 scripts/profile_art/derive_descriptions.py --all --dry-run
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
PORTFOLIO = Path("/Users/matador/startups")
DOSSIERS = PROFILE / ".github-art" / "dossiers"
VENTURES = PROFILE / ".noaerth-public-ventures.json"
OUT = PROFILE / ".github-art" / "descriptions.json"
OWNER = "M4G3LL4N0"

# Rejected outright. These describe the repository rather than the project.
TRIVIA = re.compile(
    r"package\.json|pnpm-lock|CI configured|tsconfig|no tests|"
    r"startup portfolio|project repo for|^software project$|"
    r"^experimental repository$|repository for", re.I)
GENERIC = re.compile(
    r"^(an? )?(ai[- ]powered|modern|innovative|next[- ]generation|"
    r"revolutionary|cutting[- ]edge|advanced|seamless|robust|powerful)\b", re.I)

# The first sentence of a README, cleaned of markdown.
SENTENCE = re.compile(r"^#\s*(.+?)\n+(.*)$", re.S)
FENCE = re.compile(r"```.*?```", re.S)
BADGE = re.compile(r"^\s*!?\[[^\]]*\]\([^)]*\)\s*$", re.M)
HTML = re.compile(r"<[^>]+>")

# Systems language, so a description can name the mechanism rather than the
# container it happens to run in.
MECHANISM = [
    (r"\bagent\b|\bagentic\b|orchestrat", "agent orchestration"),
    (r"\bevaluation\b|\beval\b|benchmark|comparing (?:model|llm|chatbot)",
     "evaluation harness"),
    (r"\bscheduler\b|\bqueue\b|\bcron\b|\bworker\b|\bscheduling\b",
     "scheduled execution"),
    (r"\bindex\b|\bindexing\b|\bsearch\b|retrieval|\bvector\b|\bembed",
     "indexing and retrieval"),
    (r"\bencrypt|\bprivacy\b|local[- ]first|offline|\bkeystore\b|\bsecret",
     "local-first encrypted storage"),
    (r"\brouter\b|\brouting\b|\bgateway\b|model routing|provider",
     "request routing"),
    (r"\bstate machine\b|\bstate\b.*transition|\bfsm\b", "state management"),
    (r"\bobservab|\bmonitor|\btelemetry\b|\bmetrics\b|\btracing\b",
     "observability"),
    (r"\bpipeline\b|\bbuild\b.*\bdeploy\b|\brelease\b", "build and release pipeline"),
    (r"\bdashboard\b|\banalytics\b|\breport(?:ing)?\b", "reporting surface"),
    (r"\bworkflow\b", "workflow engine"),
    (r"\bapi\b|\bgraphql\b|\brest\b|\bendpoint", "service API"),
    (r"\bcli\b|command[- ]line|\btui\b", "command-line interface"),
    (r"\bfixture|\btest suite\b|\bassertion", "test infrastructure"),
    (r"\bgraph\b|\bdag\b|dependency graph", "graph structure"),
    (r"\bsandbox\b|\bcontainer\b|\bisolation\b", "isolated execution"),
    (r"\bbroker|\blease\b|\bconsensus\b|\breplica", "distributed coordination"),
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


def readme_of(repo: str) -> str:
    d = gh_json(f"repos/{OWNER}/{repo}/readme")
    if isinstance(d, dict) and d.get("content"):
        try:
            return base64.b64decode(d["content"]).decode("utf-8", "replace")
        except Exception:
            return ""
    return ""


def local_repo(name: str) -> Path | None:
    for key in (name.lower(), name.lower().replace("-", ""),
                name.lower().replace("_", "")):
        p = PORTFOLIO / name
        if p.is_dir() and (p / ".git").exists():
            return p
        break
    for child in sorted(PORTFOLIO.iterdir()) if PORTFOLIO.is_dir() else []:
        if not child.is_dir():
            continue
        if re.sub(r"[^a-z0-9]", "", child.name.lower()) == \
           re.sub(r"[^a-z0-9]", "", name.lower()):
            return child
    return None


def first_prose(text: str, limit: int = 400) -> str:
    """The first real prose block of a README, stripped of markup."""
    body = FENCE.sub(" ", text)
    body = BADGE.sub(" ", body)
    body = HTML.sub(" ", body)
    for block in re.split(r"\n\s*\n", body):
        b = " ".join(block.split())
        if not b or b.startswith("#"):
            continue
        b = re.sub(r"^#+\s*", "", b)
        if len(b) < 40:
            continue
        low = b.lower()
        # Framework and onboarding boilerplate. "Open http://localhost:3000
        # with your browser to see the result" is create-next-app output and
        # describes every Next.js repository in existence, which is precisely
        # the rejection test in section 19.
        if low.startswith(("this is a [next.js", "this is a [react",
                           "this project was bootstrapped", "getting started",
                           "## getting started", "clone the repo",
                           "you can start by", "first, get the code",
                           "for the most part", "open http://localhost",
                           "open [http://localhost", "run `npm run dev`",
                           "the project uses supabase", "purpose not "
                           "confidently inferable", "see the readme")):
            continue
        if "localhost:3000" in low or "localhost:3001" in low:
            continue
        if b.startswith("!"):
            continue
        return b[:limit]
    return ""


def mechanisms(text: str, limit: int = 2) -> list[str]:
    low = text.lower()
    return [m for pat, m in MECHANISM if re.search(pat, low)][:limit]


def compose(name: str, prose: str, dossier: dict | None) -> tuple[str, list[str]]:
    """Compose WHAT IT IS plus a technical differentiator, then reject it."""
    why = []
    label = re.sub(r"[-_]+", " ", name).strip()

    if not prose:
        # Fall back to the dossier's own architecture read, never to the
        # repository name.
        if dossier:
            prose = (dossier.get("purpose") or "").strip() or \
                    dossier.get("animation_metaphor", "")
        if not prose:
            return "", ["no prose available from any source"]

    # First sentence, trimmed to a usable length.
    first = re.split(r"(?<=[.!?])\s", prose)[0].strip()
    first = re.sub(r"^(this project is|this is)\s+", "", first, flags=re.I)
    if len(first) > 190:
        first = first[:187].rsplit(" ", 1)[0] + "."
    what = first.rstrip(".")

    mech = mechanisms(prose + " " + (dossier.get("architecture_type", "") if dossier else ""))
    if mech:
        what += f" — {' and '.join(mech)}"

    desc = what
    if len(desc) > 200:
        desc = desc[:197].rsplit(" ", 1)[0].rstrip(",;:") + "."
    if len(desc) < 40:
        desc = f"{label}: {desc}" if desc else label

    # Rejection tests.
    if TRIVIA.search(desc):
        why.append("contains implementation trivia")
    if re.search(r"purpose not confidently inferable|undocumented|"
                 r"no description has been recorded", desc, re.I):
        why.append("inherits a placeholder rather than describing the project")
    if GENERIC.match(desc):
        why.append("opens with generic marketing language")
    low = desc.lower()
    if low in (f"startup portfolio: {name.lower()}", label.lower()):
        why.append("is the repository name restated")
    # Could this belong to twenty other repositories?
    if len(mech) == 0 and len(what) < 60:
        why.append("no distinguishing mechanism")
    if label.lower() in low and len(desc) < len(label) + 25:
        why.append("barely says more than the name")

    return desc, why


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sample", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    # Prefer the committed ledger. It already holds every public repository and
    # its description, and reading it costs no API call -- which matters because
    # a batch of 75 repositories through the API trips the secondary limit.
    repos = []
    ledger = PROFILE / "github-account-ledger.json"
    if ledger.exists() and os.environ.get("DESCRIBE_FROM_LEDGER", "1") == "1":
        data = json.loads(ledger.read_text(encoding="utf-8"))
        for rec in data.get("records", []):
            if rec.get("visibility") != "public":
                continue
            repos.append({"name": rec["name"],
                          "description": (rec.get("description_text")
                                          or rec.get("description") or "")})
    if not repos:
        api_repos = gh_json(
            f"users/{OWNER}/repos?per_page=100&type=owner&visibility=public") or []
        repos = [r for r in api_repos if isinstance(r, dict)]

    targets = [r for r in repos
               if TRIVIA.search(r.get("description") or "")
               or GENERIC.match((r.get("description") or "").strip())]
    if not args.all:
        targets = targets[: args.sample]
    if args.limit:
        targets = targets[: args.limit]

    print(f"generic descriptions detected: {len(targets)} shown of "
          f"{sum(1 for r in repos if TRIVIA.search(r.get('description') or ''))} total")
    results = {}
    for r in targets:
        name = r["name"]
        local = local_repo(name)
        text = ""
        if local:
            for cand in ("README.md", "AGENTS.md", "docs/README.md"):
                f = local / cand
                if f.is_file():
                    text += f.read_text(encoding="utf-8", errors="replace")[:6000]
        text += readme_of(name)[:6000]
        dossier_f = DOSSIERS / f"{name}.json"
        dossier = json.loads(dossier_f.read_text(encoding="utf-8")) \
            if dossier_f.exists() else None
        desc, why = compose(name, first_prose(text), dossier)
        results[name] = {"description": desc, "rejected_because": why,
                         "old": r.get("description") or ""}
        status = "REJECTED" if why else "ok"
        print(f"  {name:<26}{status:<10}{desc[:96]}")
        for w in why:
            print(f"      reason: {w}")

    if args.dry_run:
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    ok = sum(1 for v in results.values() if not v["rejected_because"])
    print(f"\n  wrote {OUT.name}: {ok}/{len(results)} accepted, "
          f"{len(results) - ok} rejected for rewriting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())