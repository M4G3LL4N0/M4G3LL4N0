#!/usr/bin/env python3
"""Publish the per-repository package: art, hero README section, metadata.

One adaptive package per repository, assembled from its dossier and its
generated art. Written through the GitHub contents API so it is idempotent:
re-running produces no commit when nothing changed, which keeps the
contribution graph honest.

The README hero is inserted only if the repository does not already reference
its own art. Existing hand-authored READMEs are never overwritten wholesale --
that is how a good README gets replaced by a generated one. The hero block is
appended above the first heading, and only when it is absent.

  python3 scripts/profile_art/publish_repo_package.py --limit 5
  python3 scripts/profile_art/publish_repo_package.py --repo agentos
  python3 scripts/profile_art/publish_repo_package.py --limit 5 --dry-run
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts"))
sys.path.insert(0, str(PROFILE / "scripts" / "github_art"))
sys.path.insert(0, str(PROFILE / "scripts" / "profile_art"))
from github_art import project_identity as P  # noqa: E402

DOSSIERS = PROFILE / ".github-art" / "dossiers"
ART = PROFILE / "build" / "repo-art"
STATE = PROFILE / ".github-elite-state.json"
OWNER = "M4G3LL4N0"
DENY_SUB = ("noaerth", "autobuilder", "pairs")
DENY_EXACT = {"paios-one", "openlegal-data"}


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


def read(repo: str, path: str) -> str:
    d = gh_json(f"repos/{OWNER}/{repo}/contents/{path}")
    if isinstance(d, dict) and d.get("content"):
        try:
            return base64.b64decode(d["content"]).decode("utf-8", "replace")
        except Exception:
            return ""
    return ""


def sha_of(repo: str, path: str) -> str:
    d = gh_json(f"repos/{OWNER}/{repo}/contents/{path}")
    return d.get("sha", "") if isinstance(d, dict) else ""


# GitHub applies a secondary abuse limit to rapid mutations from one account.
# Publishing 126 repositories back to back tripped it, and every subsequent
# measurement silently returned empty -- which looked like missing art rather
# than a throttled client. Mutations are therefore serialised and spaced.
MUTATION_DELAY = float(os.environ.get("PUBLISH_DELAY", "0.7"))
_last_mutation = [0.0]


def throttle() -> None:
    gap = time.monotonic() - _last_mutation[0]
    if gap < MUTATION_DELAY:
        time.sleep(MUTATION_DELAY - gap + random.uniform(0, 0.25))
    _last_mutation[0] = time.monotonic()


def write(repo: str, path: str, content: str, message: str,
          branch: str) -> tuple[bool, str]:
    throttle()
    cmd = ["gh", "api", f"repos/{OWNER}/{repo}/contents/{path}", "-X", "PUT",
           "-f", f"message={message}",
           "-f", "content=" + base64.b64encode(content.encode()).decode(),
           "-f", f"branch={branch}"]
    sha = sha_of(repo, path)
    if sha:
        cmd += ["-f", f"sha={sha}"]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    if p.returncode != 0:
        return False, (p.stderr or p.stdout)[:220]
    return True, ""


def hero_block(name: str, title: str, category: str, states: list[str]) -> str:
    """The hero block. Motion-first, with real static fallbacks."""
    seq = " &rarr; ".join(states[:5])
    return f"""<p align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="assets/hero/hero-reduced.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/hero/hero-light.svg">
    <img src="assets/hero/hero-motion.svg" alt="{title} — animated project plate showing {seq}. Motion depicts this project's real state transition." width="100%">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="assets/hero/computational-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/hero/computational-light.svg">
    <img src="assets/hero/computational-motion.svg" alt="State machine: {seq}." width="100%">
  </picture>
</p>
"""


def publish(name: str, dry: bool) -> dict:
    f = DOSSIERS / f"{name}.json"
    if not f.exists():
        return {"repo": name, "skipped": "no dossier"}
    d = json.loads(f.read_text(encoding="utf-8"))
    meta = gh_json(f"repos/{OWNER}/{name}") or {}
    branch = meta.get("default_branch") or "main"
    art = ART / name
    if not art.is_dir():
        return {"repo": name, "skipped": "no art"}

    from repo_art import motion_states
    states = [s for s, _ in motion_states(d.get("architecture_type", ""),
                                          d.get("project_category", ""))]

    written, errors = 0, []
    plan = []
    for src in sorted(art.glob("*.svg")):
        rel = f"assets/hero/{src.name}"
        plan.append((rel, src.read_text(encoding="utf-8")))
    # the social card belongs at the repo root convention, but the same file
    # under assets/hero keeps the upload path identical for every repository
    for rel, content in plan:
        if dry:
            written += 1
            continue
        ok, err = write(name, rel, content,
                        f"art: add {Path(rel).name}\n\n"
                        f"Generated from this project's dossier: "
                        f"{d.get('architecture_type')} / "
                        f"{d.get('project_category')}. The animation depicts "
                        f"the real state transition, not a decorative loop.",
                        branch)
        if ok:
            written += 1
        else:
            errors.append(f"{Path(rel).name}: {err}")

    # README hero, only when the repository does not already reference its art
    readme = read(name, "README.md")
    inserted = False
    if readme and "assets/hero/hero-motion.svg" not in readme:
        block = hero_block(name, d["canonical_name"],
                           d.get("project_category", ""), states)
        # Insert after the H1 so the hero sits under the title, and never
        # replace the existing document: a hand-authored README is kept intact.
        lines = readme.split("\n")
        at = 0
        for i, ln in enumerate(lines):
            if ln.startswith("# "):
                at = i + 1
                while at < len(lines) and not lines[at].strip():
                    at += 1
                break
        new = "\n".join(lines[:at]) + "\n" + block + "\n" + "\n".join(lines[at:])
        if dry:
            written += 1
        else:
            ok, err = write(name, "README.md", new,
                            "docs: add project hero and computational plate\n\n"
                            "Animated primary with static dark, static light and "
                            "reduced-motion fallbacks. The hero and the state "
                            "machine are derived from this project's own "
                            "architecture, so the imagery is specific to it.",
                            branch)
            if ok:
                written += 1
                inserted = True
            else:
                errors.append(f"README.md: {err}")

    return {"repo": name, "class": d.get("classification"),
            "written": written, "readme_hero": inserted,
            "errors": errors, "states": states}


def persist(name: str, res: dict) -> None:
    st = json.loads(STATE.read_text()) if STATE.exists() \
        else {"records": {}, "queue": []}
    rec = st["records"].get(name, {})
    rec.update({
        "files_changed": res.get("written", 0),
        "branch": f"art/{name}",
        "next_action": ("art published" if not res.get("errors")
                        else f"{len(res['errors'])} write error(s)"),
        "updated_at": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                     capture_output=True, text=True).stdout.strip(),
    })
    rec["state"] = "ART_PUBLISHED" if not res.get("errors") else "IN_PROGRESS"
    st["records"][name] = rec
    for q in st.get("queue", []):
        if q["name"] == name:
            q["state"] = rec["state"]
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wave", default="", help="flagship|project|lab|all")
    ap.add_argument("--restart", action="store_true",
                    help="ignore persisted state and start from the beginning")
    args = ap.parse_args()

    if args.repo:
        r = publish(args.repo, args.dry_run)
        print(json.dumps(r, indent=1)[:900])
        return 0

    names = [d.stem for d in sorted(DOSSIERS.glob("*.json"))]
    if args.wave == "flagship":
        names = [n for n in P.FLAGSHIP_ORDER if n in names]
    # Resume rather than restart: repositories whose art is already published
    # are skipped before the limit is applied. Previously --limit sliced the
    # full alphabetical list, so every run after the first re-published the same
    # first N and made no progress.
    if not args.restart and STATE.exists():
        st = json.loads(STATE.read_text())
        done = {k for k, v in st.get("records", {}).items()
                if v.get("state") == "ART_PUBLISHED"}
        pending = [n for n in names if n not in done]
        if pending:
            names = pending
    names = names[: args.limit]

    for name in names:
        low = name.lower()
        if any(s in low for s in DENY_SUB) or low in DENY_EXACT:
            print(f"  {name:<28}SKIP denylisted")
            continue
        r = publish(name, args.dry_run)
        if r.get("skipped"):
            print(f"  {name:<28}{r['skipped']}")
            continue
        if not args.dry_run:
            persist(name, r)
        flag = "" if not r["errors"] else f"  ERRORS {len(r['errors'])}"
        print(f"  {name:<28}{r['written']:>3} files  "
              f"hero={'y' if r['readme_hero'] else 'n'}  "
              f"{' -> '.join(r['states'][:4])[:46]}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())