#!/usr/bin/env python3
"""Product-code freeze guard.

This round is GitHub-only. The projects are read-only evidence; GitHub
presentation is the write target. Earlier rounds drifted into repairing product
CI and editing source, which is exactly what this guard exists to prevent.

The freeze is not a policy note. It records the state of every forbidden path
across the local portfolio, and refuses to declare the round clean if any of
them changed.

Forbidden: application source, manifests, lockfiles, framework and runtime
config, product tests, database code, and product deployment configuration.

Allowed: README, .github/**, docs/GITHUB_*.md, docs/TECHNICAL_*.md,
assets/github/**, assets/readme/**, assets/social/**, community files,
issue and PR templates, and repository metadata.

  python3 scripts/profile_art/freeze_guard.py --snapshot
  python3 scripts/profile_art/freeze_guard.py --verify
  python3 scripts/profile_art/freeze_guard.py --verify --since <snapshot.json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
PORTFOLIO = Path("/Users/matador/startups")
SNAPSHOT = PROFILE / ".github-art" / "product-freeze.json"
OWNER = "M4G3LL4N0"

# Paths a GitHub-presentation change must never touch.
FORBIDDEN = [
    "src", "app", "pages", "components", "server", "api", "lib", "packages",
    "native", "ios", "android", "backend", "frontend", "supabase",
    "prisma", "migrations", "database", "db",
]
FORBIDDEN_FILES = re.compile(
    r"^(package\.json|pnpm-lock\.yaml|package-lock\.json|yarn\.lock|"
    r"Cargo\.toml|go\.mod|go\.sum|pyproject\.toml|poetry\.lock|"
    r"requirements.*\.txt|Pipfile|composer\.json|Gemfile|"
    r"Dockerfile.*|docker-compose.*|vercel\.json|next\.config\..*|"
    r"nuxt\.config\..*|vite\.config\..*|svelte\.config\..*|"
    r"astro\.config\..*|tsconfig*.json|\.env|\.env\..*)$")
# Test files are product tests; changing them to make CI pass is product work.
FORBIDDEN_TEST = re.compile(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec)\.")

# Any source file is product code wherever it sits. The first guard matched only
# forbidden directory names, so appending to grokinstall/main.go at the repo
# root was reported as a clean freeze. Root-level source is common: main.go,
# index.ts, main.py.
SOURCE_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go",
              ".rs", ".rb", ".java", ".kt", ".kts", ".swift", ".c", ".h",
              ".cc", ".cpp", ".hpp", ".cs", ".php", ".scala", ".ex", ".exs",
              ".erl", ".clj", ".sh", ".bash", ".zsh", ".sql", ".css",
              ".scss", ".less", ".vue", ".svelte", ".astro")

SKIP = re.compile(r"(^|/)(\.git|node_modules|\.next|dist|build|out|target|"
                  r"coverage|\.venv|__pycache__|\.vercel|build)(/|$)")

# Documentation and presentation surfaces this round is allowed to write.
ALLOWED_MARKERS = (
    "README.md", ".github", "docs/GITHUB_", "docs/TECHNICAL_",
    "assets/github/", "assets/readme/", "assets/social/", "assets/hero/",
    "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md", "CODE_OF_CONDUCT.md",
    ".github/ISSUE_TEMPLATE", ".github/PULL_REQUEST_TEMPLATE",
)


def repo_dirs() -> list[Path]:
    if not PORTFOLIO.is_dir():
        return []
    out = []
    for child in sorted(PORTFOLIO.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            out.append(child)
    return out


def fingerprint(repo: Path) -> dict:
    """Hash every forbidden path plus every allowed path, separately.

    Two fingerprints, because the useful question is not 'did anything change'
    but 'did anything change that I was not allowed to change'.
    """
    forbidden: dict[str, str] = {}
    allowed: dict[str, str] = {}
    try:
        proc = subprocess.run(["git", "-C", str(repo), "ls-files"],
                              capture_output=True, text=True, timeout=30)
        files = [f for f in proc.stdout.splitlines() if f.strip()]
    except Exception:
        return {"forbidden": forbidden, "allowed": allowed}
    for f in files:
        if SKIP.search(f):
            continue
        top = f.split("/", 1)[0]
        name = Path(f).name
        is_forbidden = (
            top in FORBIDDEN
            or FORBIDDEN_FILES.match(name)
            or FORBIDDEN_TEST.search(f)
            or name.endswith(SOURCE_EXT)
        )
        if is_forbidden:
            forbidden[f] = ""
            continue
        if any(f.startswith(m) or m in f for m in ALLOWED_MARKERS):
            allowed[f] = ""
    # Hash file contents so a modification is detected, not just an addition.
    for bucket in (forbidden, allowed):
        for path in list(bucket):
            fp = repo / path
            if fp.is_file() and fp.stat().st_size < 2_000_000:
                try:
                    bucket[path] = hashlib.sha256(fp.read_bytes()).hexdigest()[:16]
                except OSError:
                    bucket[path] = "unreadable"
    return {"forbidden": forbidden, "allowed": allowed}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--since", default="")
    args = ap.parse_args()

    repos = repo_dirs()
    if not repos:
        print("no local repositories found")
        return 1

    state = {r.name: fingerprint(r) for r in repos}

    if args.snapshot or not args.verify:
        payload = {
            "$comment": "Fingerprint of every forbidden and allowed path across "
                        "the local portfolio. The freeze guard compares against "
                        "this to prove GitHub-only work touched no product code.",
            "owner": OWNER,
            "repos": len(state),
            "forbidden_paths": sum(len(v["forbidden"]) for v in state.values()),
            "allowed_paths": sum(len(v["allowed"]) for v in state.values()),
            "state": state,
        }
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        print(f"  snapshot written: {len(state)} repositories, "
              f"{payload['forbidden_paths']} forbidden paths, "
              f"{payload['allowed_paths']} allowed paths")
        return 0

    if args.since:
        path = Path(args.since)
    else:
        path = SNAPSHOT
    if not path.is_file():
        print(f"  no snapshot at {path}; run --snapshot first")
        return 1

    before = json.loads(path.read_text(encoding="utf-8"))["state"]
    violations = []
    for name, now in sorted(state.items()):
        was = before.get(name)
        if was is None:
            continue
        fb, fa = was["forbidden"], now["forbidden"]
        added = sorted(set(fa) - set(fb))
        removed = sorted(set(fb) - set(fa))
        modified = sorted(p for p in set(fa) & set(fb)
                          if fb[p] and fa.get(p) and fa[p] != fb[p])
        for p in added:
            violations.append(f"{name}: product path ADDED {p}")
        for p in removed:
            violations.append(f"{name}: product path REMOVED {p}")
        for p in modified:
            violations.append(f"{name}: product path MODIFIED {p}")

    print("PRODUCT CODE FREEZE")
    print(f"  repositories scanned : {len(state)}")
    print(f"  forbidden paths      : "
          f"{sum(len(v['forbidden']) for v in state.values())}")
    print(f"  violations           : {len(violations)}")
    for v in violations[:20]:
        print(f"    {v}")
    if violations:
        print()
        print("  PRODUCT CODE CHANGED.")
        print("  This round is GitHub-only. If a product defect was found,")
        print("  document it; do not fix it. Revert the change.")
        return 1
    print("  freeze holds: no product code changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())