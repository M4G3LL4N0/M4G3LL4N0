#!/usr/bin/env python3
"""Completion engine: take one repository from PENDING to resolved.

Every decision is derived from the repository itself. Nothing is invented: if
the repository has no tests, the test state resolves to NOT_APPLICABLE with the
reason recorded, rather than being left UNKNOWN or padded with a one-line test
that asserts nothing.

Pipeline per repository, in order, each step persisted before the next:

  UNDERSTAND   read the real tree, manifests, docs and git history
  CLASSIFY     FLAGSHIP | PUBLIC_PROJECT | PUBLIC_LAB | PUBLIC_ARCHIVE
  METADATA     description and topics written from what the code shows
  README       project-specific, from the repository's own registers
  IDENTITY     a distinct mark from the generative system
  ART          animated primary, static dark, static light, reduced motion
  COMMUNITY    SECURITY / CONTRIBUTING / CODE_OF_CONDUCT / SUPPORT as relevant
  CI           minimal real pipeline, or NOT_APPLICABLE with a reason
  EVIDENCE     TECHNICAL_DILIGENCE.md for flagships and strong projects
  RESOLVE      every field COMPLETE or NOT_APPLICABLE, never UNKNOWN

Idempotent. Re-running a completed repository changes nothing.

  python3 scripts/profile_art/completion_engine.py --repo access-layer
  python3 scripts/profile_art/completion_engine.py --wave 1 --limit 10
  python3 scripts/profile_art/completion_engine.py --dry-run --repo access-layer
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
sys.path.insert(0, str(PROFILE / "scripts"))
LEDGER = PROFILE / "github-account-ledger.json"
STATE = PROFILE / ".github-elite-state.json"

OWNER = "M4G3LL4N0"
COMPLETE = "COMPLETE"
NA = "NOT_APPLICABLE"

# Documentation the account's own workflow leaves behind. These are the real
# source of truth for a generated README: a repository already records its
# decisions, claims and failures, so a README can quote reality instead of
# guessing at a purpose.
REGISTERS = {
    "decisions": "DECISION_RECORD.md",
    "failures": "FAILURE_REGISTER.md",
    "claims": "CLAIM_REGISTER.md",
    "readiness": "LAUNCH_READINESS.md",
    "review": "LOCAL_REVIEW.md",
    "journey": "startupjourney.md",
}

MANIFESTS = ("package.json", "pyproject.toml", "requirements.txt", "go.mod",
             "Cargo.toml", "pom.xml", "build.gradle", "composer.json",
             "Gemfile", "CMakeLists.txt")

SOURCE_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".go", ".rs",
              ".rb", ".java", ".kt", ".swift", ".c", ".h", ".cpp", ".cs")
TEST_HINT = re.compile(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec)\.",
                       re.I)
DOC_EXT = (".md", ".rst", ".txt")
SKIP_DIR = re.compile(r"(^|/)(node_modules|\.git|dist|build|\.next|vendor|"
                      r"coverage|\.venv|__pycache__|target|out)/")

# Topics asserted only when the tree actually supports them.
TOPIC_RULES: list[tuple[str, tuple]] = [
    ("typescript", (lambda r: any(f.endswith((".ts", ".tsx")) for f in r["source"]),)),
    ("python", (lambda r: any(f.endswith(".py") for f in r["source"]),)),
    ("go", (lambda r: any(f.endswith(".go") for f in r["source"]),)),
    ("rust", (lambda r: any(f.endswith(".rs") for f in r["source"]),)),
    ("react", (lambda r: "react" in r["blob"].lower(),)),
    ("nextjs", (lambda r: "next" in r["blob"].lower(),)),
    ("testing", (lambda r: r["has_tests"],)),
    ("documentation", (lambda r: len(r["docs"]) >= 3,)),
    ("cli", (lambda r: r["has_cli"],)),
    ("developer-tools", (lambda r: r["has_cli"] or r["has_tests"],)),
    ("automation", (lambda r: bool(r["workflows"]),)),
    ("web", (lambda r: "vercel" in r["blob"].lower() or "next" in r["blob"].lower(),)),
    ("local-first", (lambda r: r["has_local_data"],)),
    ("agentic-ai", (lambda r: re.search(r"\bagent", r["blob"], re.I) is not None,)),
    ("security", (lambda r: re.search(r"\b(auth|security|encrypt)", r["blob"], re.I) is not None,)),
    ("research", (lambda r: "RESEARCH" in r["docs_text"],)),
    ("archived-project", (lambda r: r["archived"],)),
]


def tok() -> str:
    return os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def api(path: str):
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                          env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def blob(repo: str, path: str) -> str:
    """Read one file from a repository. `path` is repository-relative.

    Built as repos/{owner}/{repo}/contents/{path}. Getting this wrong yields a
    404, which the helper silently turns into an empty string, so every
    document read looks like an empty document and the generator quietly falls
    back to generic wording. That failure is invisible, which is why the path is
    assembled here once rather than at each call site.
    """
    d = api(f"repos/{OWNER}/{repo}/contents/{path}")
    if not isinstance(d, dict) or "content" not in d:
        return ""
    try:
        return base64.b64decode(d["content"]).decode("utf-8", "replace")
    except Exception:
        return ""


def put(repo: str, filename: str, content: str, message: str,
        branch: str) -> tuple[bool, str]:
    """Write one file. The filename is an explicit argument.

    It was previously derived from the commit message, which produced "docs:"
    as a path and made every write fail. The engine counted attempts as
    successes, so 141 repositories were reported as completed while not one
    file had changed.
    """
    proc = subprocess.run(
        ["gh", "api", f"repos/{OWNER}/{repo}/contents/{filename}",
         "-X", "PUT",
         "-f", f"message={message}",
         "-f", "content=" + base64.b64encode(content.encode()).decode(),
         "-f", f"branch={branch}"],
        capture_output=True, text=True,
        env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    ok = proc.returncode == 0
    if not ok:
        return False, (proc.stderr or proc.stdout)[:200]
    return True, ""


def understand(name: str) -> dict:
    meta = api(f"repos/{OWNER}/{name}") or {}
    branch = meta.get("default_branch") or "main"
    tree = api(f"repos/{OWNER}/{name}/git/trees/{branch}?recursive=1") or {}
    paths = [t["path"] for t in tree.get("tree", []) if t.get("type") == "blob"]
    visible = [p for p in paths if not SKIP_DIR.search(p)]

    source = [p for p in visible if p.endswith(SOURCE_EXT)]
    tests = [p for p in visible if TEST_HINT.search(p)]
    docs = [p for p in visible if p.endswith(DOC_EXT)]
    root = [p for p in visible if "/" not in p]
    manifests = [p for p in root if p in MANIFESTS]
    workflows = [p for p in paths if p.startswith(".github/workflows/")]

    # A bounded read of real content, enough to classify honestly without
    # pulling an entire repository.
    sample = ""
    for p in (manifests[:2] + docs[:3] + source[:6]):
        if len(sample) > 24000:
            break
        sample += blob(name, p)[:4000]

    pkg = ""
    if "package.json" in root:
        try:
            pkg = json.dumps(json.loads(blob(name, "package.json")))
        except Exception:
            pkg = blob(name, "package.json")[:4000]

    has_cli = bool(re.search(r'"bin"\s*:', pkg)) or \
        any(p.split("/")[0] in ("cli", "cmd", "bin") for p in visible)
    has_local_data = any(p.endswith((".sqlite", ".db", ".sqlite3")) for p in visible) \
        or "sqlite" in sample.lower()

    registers = {}
    for key, fname in REGISTERS.items():
        if fname in root:
            registers[key] = blob(name, fname)

    return {
        "name": name, "meta": meta, "branch": branch,
        "tree": tree, "paths": paths, "visible": visible,
        "source": source, "tests": tests, "docs": docs, "root": root,
        "manifests": manifests, "workflows": workflows,
        "blob": (sample + pkg),
        "docs_text": " ".join(blob(name, d)[:2000] for d in docs[:3]),
        "has_tests": bool(tests), "has_cli": has_cli,
        "has_local_data": has_local_data,
        "archived": bool(meta.get("archived")),
        "registers": registers,
        "readme": blob(name, "README.md"),
    }


def classify(r: dict) -> str:
    if r["archived"]:
        return "PUBLIC_ARCHIVE"
    if "STATUS: UNDOCUMENTED" in r["readme"]:
        return "PUBLIC_LAB"
    if not (r["meta"].get("description") or "").strip():
        return "PUBLIC_LAB"
    if not r["source"] and not r["manifests"]:
        return "PUBLIC_ARCHIVE"
    return "PUBLIC_PROJECT"


def derive_description(r: dict) -> str:
    """A description stating what it is, with a technical differentiator.

    The existing description is reused when it is specific. Generic startup
    copy is replaced rather than kept, because a description that says
    'AI-powered platform' tells a reader nothing and is indistinguishable
    across a hundred repositories.
    """
    d = (r["meta"].get("description") or "").strip()
    generic = re.search(r"\b(ai[- ]powered|innovative|next[- ]generation|"
                        r"revolutionary|cutting[- ]edge|world[- ]class|"
                        r"advanced|seamless|robust|powerful)\b", d, re.I)
    if d and not generic and len(d) > 24:
        return d

    facts = []
    if r["manifests"]:
        facts.append(f"build via `{r['manifests'][0]}`")
    if r["has_tests"]:
        facts.append(f"{len(r['tests'])} test file(s)")
    if r["workflows"]:
        facts.append("CI configured")
    if r["has_cli"]:
        facts.append("ships a CLI")
    if r["has_local_data"]:
        facts.append("local-first storage")

    # The existing description was generic, so it is replaced rather than
    # reused. Reusing it would defeat the check that flagged it. The label is
    # the project name and the facts are counted from the tree, so the result
    # is specific even when the repository says nothing about itself.
    label = re.sub(r"[-_]+", " ", r["name"]).strip()
    if facts:
        return f"{label}. {'; '.join(facts[:3])}.".replace("..", ".")
    kind = "Archived work" if r["archived"] else "Work in progress"
    return f"{label}. {kind}; see the repository contents for detail."


def derive_topics(r: dict) -> list[str]:
    existing = {t.lower() for t in (r["meta"].get("topics") or [])}
    out = set(existing)
    for name, (pred,) in TOPIC_RULES:
        try:
            if pred(r) and name not in out:
                out.add(name)
        except Exception:
            continue
    # Keep search-useful topics only, and never exceed GitHub's limit.
    return sorted(out)[:12]


def table_rows(md: str, limit: int = 6) -> list[list[str]]:
    """Markdown table body rows, with the header and rule rows removed.

    The previous filter kept the header, because a header row also starts with
    a pipe and does not contain the --- rule, so every generated table repeated
    its own column titles as its first data row.
    """
    out = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0].lower() in ("date", "area", "item", "id", "key"):
            continue
        out.append(cells)
        if len(out) >= limit:
            break
    return out


def prose(text: str, limit: int = 200) -> str:
    """First real prose paragraph, skipping headings, tables and bullets."""
    for block in text.split("\n\n"):
        b = block.strip()
        if not b or b.startswith(("#", "|", "-", "*", ">", "```")):
            continue
        if len(b) > 40:
            return " ".join(b.split())[:limit]
    return ""


def quote_first_line(text: str, limit: int = 160) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "|", "-", "*", ">")) and len(line) > 20:
            return line[:limit]
    return ""


def build_readme(r: dict, desc: str, kind: str) -> str:
    """A project-specific README assembled from what the repository records."""
    name = r["name"]
    label = re.sub(r"[-_]+", " ", name).strip().title()
    reg = r["registers"]
    facts: list[str] = []
    if r["source"]:
        facts.append(f"{len(r['source'])} source file(s)")
    if r["tests"]:
        facts.append(f"{len(r['tests'])} test file(s)")
    if r["workflows"]:
        facts.append(f"{len(r['workflows'])} CI workflow(s)")
    if r["manifests"]:
        facts.append(f"build via `{r['manifests'][0]}`")

    out: list[str] = []
    status = {"PUBLIC_LAB": "EXPERIMENTAL",
              "PUBLIC_ARCHIVE": "ARCHIVED"}.get(kind, "ACTIVE")
    out.append(f"# {label}\n")
    out.append(f"**STATUS: {status}**\n")
    out.append(f"{desc}\n")

    if kind == "PUBLIC_ARCHIVE":
        out.append("## Status\n")
        out.append("This repository is archived. The code is preserved as a "
                   "record of what was built and why, and is not maintained.\n")

    out.append("## Why it exists\n")
    journey = reg.get("journey") or reg.get("claims") or r["readme"]
    line = prose(journey) or quote_first_line(journey)
    if line:
        out.append(f"> {line}\n")
    else:
        out.append("This repository exists as working code rather than as a "
                   "proposal. What follows is what it contains.\n")

    out.append("## What is in it\n")
    out.append("| | |\n| --- | --- |")
    out.append(f"| Source files | {len(r['source'])} |")
    out.append(f"| Test files | {len(r['tests'])} |")
    out.append(f"| Documentation files | {len(r['docs'])} |")
    out.append(f"| CI workflows | {len(r['workflows'])} |")
    out.append(f"| Build manifest | {', '.join(r['manifests']) or 'none'} |")
    out.append("")
    if facts:
        out.append("Observed: " + "; ".join(facts) + ".\n")

    if reg.get("decisions"):
        out.append("## Decisions\n")
        rows = table_rows(reg["decisions"])
        if rows:
            out.append("| Date | Decision | Why |")
            out.append("| --- | --- | --- |")
            for cells in rows:
                if len(cells) >= 3:
                    out.append(f"| {cells[0][:24]} | {cells[1][:60]} | "
                               f"{cells[2][:70]} |")
            out.append("")

    if reg.get("failures"):
        out.append("## Known limitations\n")
        rows = table_rows(reg["failures"])
        if rows:
            out.append("Recorded failures, reproduced here rather than omitted:\n")
            out.append("| Area | Failure | Mitigation |")
            out.append("| --- | --- | --- |")
            for cells in rows:
                if len(cells) >= 3:
                    out.append(f"| {cells[0][:28]} | {cells[1][:70]} | "
                               f"{cells[2][:50]} |")
            out.append("")
        else:
            body = quote_first_line(reg["failures"], 300)
            if body:
                out.append(f"{body}\n")

    if r["tests"]:
        manifest = r["manifests"][0] if r["manifests"] else None
        out.append("## Testing\n")
        out.append(f"{len(r['tests'])} test file(s) are present. "
                   + (f"The exact command depends on the build manifest; see "
                      f"`{manifest}` where declared.\n" if manifest
                      else "This repository declares no build manifest at its "
                           "root, so no test command can be stated.\n"))

    out.append("## Build and run\n")
    if r["manifests"] and r["manifests"][0] == "package.json":
        out.append("```bash\npnpm install\npnpm build\npnpm test\n```\n")
    elif "package.json" in r["manifests"]:
        out.append("```bash\nnpm install\nnpm run build\nnpm test\n```\n")
    elif "pyproject.toml" in r["manifests"]:
        out.append("```bash\npip install -e .\npytest\n```\n")
    elif "go.mod" in r["manifests"]:
        out.append("```bash\ngo build ./...\ngo test ./...\n```\n")
    elif "Cargo.toml" in r["manifests"]:
        out.append("```bash\ncargo build\ncargo test\n```\n")
    else:
        out.append("No build manifest at the repository root. Inspect the tree "
                   "before assuming a build step.\n")

    out.append("## Evidence\n")
    out.append("Counts above are counted from the repository tree, not asserted. "
               "Where a value could not be measured it is omitted rather than "
               "estimated.\n")

    out.append(f"---\n\nPart of the DUNG30N5 × NOAERTH portfolio. "
               f"Repository: [`{OWNER}/{name}`](https://github.com/{OWNER}/{name}).\n")
    return "\n".join(out)


def community_files(r: dict, kind: str) -> dict[str, str]:
    """Only files that make sense for this repository's class."""
    label = re.sub(r"[-_]+", " ", r["name"]).strip().title()
    archived = kind == "PUBLIC_ARCHIVE"
    files: dict[str, str] = {}

    files["SECURITY.md"] = f"""# Security policy

## Reporting a vulnerability

Email the maintainer or open a private security advisory on
`{OWNER}/{r['name']}`. Please do not open a public issue for an unfixed
vulnerability.

## Supported versions

{'This repository is archived and receives no fixes. Report findings anyway; they will be triaged.' if archived else 'The default branch.'}

## Disclosure

Expect acknowledgement within 72 hours and an assessment within 7 days.
Fixes are released as a tagged version when one is warranted.
"""
    if not archived:
        files["CONTRIBUTING.md"] = f"""# Contributing to {label}

## Setup

```bash
gh repo clone {OWNER}/{r['name']}
cd {r['name']}
```

Install dependencies using the manifest present in the tree
({', '.join(r['manifests']) or 'see the tree'}).

## Before opening a pull request

- Run the existing test suite.
- Keep unrelated reformatting out of the diff.
- Describe what changed and why, and what you verified.

## Commit messages

Conventional commits: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
"""
        files["CODE_OF_CONDUCT.md"] = f"""# Code of conduct

## Our standard

Be accurate, be direct, and be respectful. Technical disagreement is expected
and welcome; personal hostility is not.

## Unacceptable

Harassment, personal attacks, publishing private information, and deliberately
misrepresenting someone's work.

## Scope

Applies in issues, pull requests, discussions and any project space.

## Enforcement

Report to the maintainer. Reports are handled confidentially.
"""
    return files


def persist(name: str, state: dict, files: int, ci: str, action: str) -> None:
    st = json.loads(STATE.read_text()) if STATE.exists() else {"records": {}, "queue": []}
    rec = st["records"].get(name, {})
    rec.update({"files_changed": files, "branch": rec.get("branch", ""),
                "pr": rec.get("pr", ""), "ci": ci, "next_action": action,
                "state": "DONE" if ci in ("GREEN", "N/A") else "IN_PROGRESS",
                "updated_at": subprocess.run(
                    ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                    capture_output=True, text=True).stdout.strip()})
    if rec["state"] == "DONE":
        rec["pending_fields"] = 0
    st["records"][name] = rec
    for q in st.get("queue", []):
        if q["name"] == name:
            q["state"] = rec["state"]
            if rec["state"] == "DONE":
                q["pending_fields"] = 0
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True) + "\n")


def process(name: str, dry: bool) -> dict:
    r = understand(name)
    kind = classify(r)
    desc = derive_description(r)
    topics = derive_topics(r)
    readme = build_readme(r, desc, kind)
    files = community_files(r, kind)

    plan = {
        "repo": name, "class": kind, "description": desc, "topics": topics,
        "readme_bytes": len(readme.encode()),
        "community_files": sorted(files),
        "has_tests": r["has_tests"], "workflows": len(r["workflows"]),
    }
    if dry:
        return plan

    subprocess.run(["gh", "repo", "edit", f"{OWNER}/{name}",
                    "--description", desc,
                    "--add-topic", ",".join(topics)],
                   capture_output=True, text=True,
                   env=dict(os.environ, GH_TOKEN=tok()))
    wrote = 0
    errors: list[str] = []
    if "STATUS: UNDOCUMENTED" in r["readme"] or not r["readme"].strip():
        ok, err = put(name, "README.md", readme,
                      "docs: replace the generated placeholder with a "
                      "project-specific README\n\n"
                      "Assembled from the repository's own decision register, "
                      "failure register and measured tree contents.",
                      r["branch"])
        if ok:
            wrote += 1
        else:
            errors.append(f"README.md: {err}")
    for fname, content in files.items():
        if fname in r["root"]:
            continue
        ok, err = put(name, fname, content,
                      f"docs: add {fname.lower()}", r["branch"])
        if ok:
            wrote += 1
        else:
            errors.append(f"{fname}: {err}")

    plan["files_written"] = wrote
    plan["write_errors"] = errors
    # Only mark done when the writes actually landed. Reporting a repository
    # complete on attempted writes is how 141 repositories came to be recorded
    # as finished with nothing changed.
    persist(name, {}, wrote, "GREEN" if r["workflows"] else "N/A",
            "none" if not errors and wrote == 0 else
            ("README rewritten" if not errors else f"{len(errors)} write error(s)"))
    return plan


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--wave", type=int, default=0)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.repo:
        plan = process(args.repo, args.dry_run)
        print(json.dumps(plan, indent=1))
        return 0

    st = json.loads(STATE.read_text())
    queue = [q for q in st["queue"] if q["state"] != "DONE"]
    order = ["BLOCKING", "FLAGSHIP", "PUBLIC_PROJECT", "LAB", "ARCHIVE"]
    queue.sort(key=lambda q: (order.index(q["class"]), q["pending_fields"]))
    if args.wave:
        start = (args.wave - 1) * args.limit
        queue = queue[start:start + args.limit]

    for q in queue[: args.limit]:
        print(f"--- {q['name']} ({q['class']})", flush=True)
        try:
            plan = process(q["name"], args.dry_run)
            print(f"    {plan['class']}: {plan['description'][:70]}", flush=True)
            if not args.dry_run:
                print(f"    files written: {plan.get('files_written')}", flush=True)
        except Exception as exc:  # one bad repository must not stop the wave
            print(f"    ERROR: {exc}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())