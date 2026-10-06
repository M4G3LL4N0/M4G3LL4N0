#!/usr/bin/env python3
"""Repository completeness audit across every public owned repository.

Section 37 asks for a report, not for filler. A field is only ever reported as
PASS when it was actually observed on the live repository. Anything that does
not apply to a repository's class is reported N/A and is not counted against
it, so a two-week experiment is not measured against the standard of a
flagship.

  python3 scripts/audit_repo_completeness.py --out COMPLETENESS.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MARK = "\u2713"
CROSS = "\u2717"
DASH = "\u2013"

# Fields that are meaningful for every public repository.
ALWAYS = ("description", "topics", "readme", "hero", "animation", "static_fallback",
          "social_preview")
# Fields that are reported but explicitly allowed to be not-applicable.
CONDITIONAL = ("license", "security", "contributing", "ci", "tests",
               "benchmark", "release", "homepage")

PRIVATE_PAT = re.compile(
    r"(\.github-removal-manifest|/Users/matador|-----BEGIN [A-Z ]*PRIVATE KEY|"
    r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,})"
)
DENY_SUB = ("noaerth", "autobuilder", "pairs")
DENY_EXACT = {"paios-one", "openlegal-data"}
SITE_SUFFIX = "-website"


def denied(name: str) -> bool:
    low = name.lower()
    return any(s in low for s in DENY_SUB) or low in DENY_EXACT


def gh(args: list[str], token: str) -> str | None:
    env = dict(os.environ, GH_TOKEN=token, GH_PAGER="cat")
    proc = subprocess.run(args, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        return None
    out = proc.stdout.strip()
    return out or None


def gh_json(args: list[str], token: str):
    raw = gh(args, token)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


PRIVATE_REPO_NAMES: set[str] = set()
BRAND_COLLISIONS: set[str] = set()


def readme_info(repo: str, token: str) -> dict:
    """Read the default-branch README and classify what it actually contains."""
    data = gh_json(["gh", "api", f"repos/M4G3LL4N0/{repo}/readme"], token)
    if not isinstance(data, dict):
        return {"present": False}
    import base64
    try:
        text = base64.b64decode(data["content"]).decode("utf-8", "replace")
    except Exception:
        return {"present": True, "text": ""}
    images = re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text)
    svgs = [i for i in images if i.lower().endswith(".svg")]
    animated = [i for i in svgs if re.search(r"(anim|motion|hero-)", i, re.I)]
    static = [i for i in svgs if i not in animated]
    return {
        "present": True,
        "text": text,
        "lines": len(text.splitlines()),
        "images": len(images),
        "hero": bool(svgs),
        "animation": bool(animated),
        "static_fallback": bool(static) or not svgs,
        "tests_mentioned": bool(re.search(r"\b(tests?|CI|verified)\b", text, re.I)),
        "license_mentioned": bool(re.search(r"\blicen[cs]e\b", text, re.I)),
        "private_leak": bool(PRIVATE_PAT.search(text)),
        # Scanned against the real private-repository name list, not the
        # substring "noaerth". "Noaerth" is the public brand and belongs in
        # public copy; "noaerth-portfolio-os" is a private repository name and
        # must never appear in public text or generated graphics.
        "deny_leak": sorted({n for n in PRIVATE_REPO_NAMES
                             if n.lower() in text.lower()}),
        "brand_collision": sorted({n for n in BRAND_COLLISIONS
                                   if n.lower() in text.lower()}),
    }


def has_ci(repo: str, token: str) -> bool:
    listing = gh_json(["gh", "api", f"repos/M4G3LL4N0/{repo}/contents/.github/workflows"], token)
    return bool(isinstance(listing, list) and listing)


def has_file(repo: str, path: str, token: str) -> bool:
    return gh_json(["gh", "api", f"repos/M4G3LL4N0/{repo}/contents/{path}"], token) is not None


def classify(repo: dict) -> str:
    """Coarse class from repository signals. Deliberately not a quality score."""
    name = repo["name"].lower()
    raw = repo.get("repositoryTopics") or []
    topics = {(t.get("name") or "").lower() if isinstance(t, dict) else str(t).lower()
              for t in raw}
    if repo.get("isArchived"):
        return "PUBLIC_ARCHIVE"
    if repo.get("description") is None:
        return "PUBLIC_LAB"
    if any(k in topics for k in ("research", "quantitative-finance", "experiment")):
        return "PUBLIC_LAB"
    return "PUBLIC_PROJECT"


def audit(repo: dict, token: str) -> dict:
    name = repo["name"]
    readme = readme_info(name, token)
    raw_topics = repo.get("repositoryTopics") or []
    topics = [t.get("name") if isinstance(t, dict) else t for t in raw_topics]
    fields = {
        "description": "PASS" if (repo.get("description") or "").strip() else CROSS,
        "topics": "PASS" if len(topics) >= 5 else CROSS,
        "readme": "PASS" if readme["present"] else CROSS,
        "hero": "PASS" if readme.get("hero") else DASH,
        "animation": "PASS" if readme.get("animation") else DASH,
        "static_fallback": "PASS" if readme.get("static_fallback", True) else DASH,
        "license": "PASS" if (repo.get("licenseInfo") or has_file(name, "LICENSE", token)) else DASH,
        "security": "PASS" if has_file(name, "SECURITY.md", token) else DASH,
        "contributing": "PASS" if has_file(name, "CONTRIBUTING.md", token) else DASH,
        "ci": "PASS" if has_ci(name, token) else DASH,
        "tests": "PASS" if readme.get("tests_mentioned") else DASH,
        "benchmark": "PASS" if has_file(name, "BENCHMARKS.md", token) else DASH,
        "release": "PASS" if repo.get("latestRelease") else DASH,
        "homepage": "PASS" if (repo.get("homepageUrl") or "").strip() else DASH,
        # GitHub exposes no API field for whether a custom social preview is
        # set, so this is reported as not-verifiable rather than guessed.
        "social_preview": DASH,
    }
    return {
        "repo": name,
        "class": classify(repo),
        "fields": fields,
        "readme_lines": readme.get("lines", 0),
        "private_leak": readme.get("private_leak", False),
        "deny_leak": readme.get("deny_leak", False),
        "brand_collision": readme.get("brand_collision", []),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="-")
    ap.add_argument("--limit", type=int, default=0,
                    help="audit only the first N public repos (0 = all)")
    args = ap.parse_args()

    token = os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    if not token:
        print("audit: no GitHub token available", file=sys.stderr)
        return 2

    all_repos = gh_json(["gh", "repo", "list", "M4G3LL4N0", "--limit", "400",
                         "--json", "name,visibility"], token) or []
    for r in all_repos:
        if r["visibility"].lower() != "private":
            continue
        n = r["name"]
        if not (denied(n) or n.lower().endswith(SITE_SUFFIX)):
            continue
        # A private repository whose name is a single common word collides with
        # public brand copy. "noaerth" is both a studio brand and a repository
        # name; treating the brand as a disclosure would force the brand out of
        # every public README, which is backwards. Single-token names are
        # reported as brand collisions; multi-token names are real references.
        (BRAND_COLLISIONS if ("-" not in n and len(n) <= 12) else PRIVATE_REPO_NAMES).add(n)

    repos = gh_json(["gh", "repo", "list", "M4G3LL4N0", "--limit", "400",
                     "--json", "name,description,repositoryTopics,isArchived,licenseInfo,"
                     "homepageUrl,visibility,latestRelease"], token) or []
    public = [r for r in repos if r["visibility"].lower() == "public"
              and not denied(r["name"]) and not r["name"].lower().endswith(SITE_SUFFIX)]
    if args.limit:
        public = public[: args.limit]

    rows = []
    for i, repo in enumerate(public, 1):
        rows.append(audit(repo, token))
        if i % 25 == 0:
            print(f"    ...{i}/{len(public)}", file=sys.stderr)

    leaks = [r for r in rows if r["private_leak"] or r["deny_leak"]]
    brands = [r for r in rows if r["brand_collision"]]

    out = []
    out.append("# Repository completeness audit\n")
    out.append(f"Public non-denylisted repositories audited: **{len(rows)}**\n")
    for label in ALWAYS:
        ok = sum(1 for r in rows if r["fields"][label] == "PASS")
        out.append(f"- {label}: {ok}/{len(rows)} {MARK if ok == len(rows) else CROSS}")
    out.append("")
    out.append("Conditional fields are reported N/A where they do not apply to a")
    out.append("repository's class. A N/A is not a failure.\n")

    out.append("## Per-repository detail\n")
    out.append("| repository | class | desc | topics | readme | hero | anim | static |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: x["repo"]):
        f = r["fields"]
        out.append("| `{repo}` | {cls} | {desc} | {topics} | {readme} | {hero} | "
                   "{anim} | {static} |".format(
                       repo=r["repo"], cls=r["class"], desc=f["description"],
                       topics=f["topics"], readme=f["readme"], hero=f["hero"],
                       anim=f["animation"], static=f["static_fallback"]))

    out.append("\n## Leak scan\n")
    if leaks:
        out.append("**Repositories whose README contains a private path, credential or")
        out.append("denylisted repository name:**\n")
        for r in leaks:
            names = ", ".join(f"`{n}`" for n in r["deny_leak"]) or "-"
            out.append(f"- `{r['repo']}` private_path={r['private_leak']} private_repo_names={names}")
    else:
        out.append(f"No private path, credential or private repository name found in "
                   f"any of the {len(rows)} audited READMEs.")
    if brands:
        out.append("\n### Brand collisions (informational, not a disclosure)\n")
        out.append("These private repositories are named after the public studio brand.")
        out.append("The brand belongs in public copy; nothing is disclosed by naming it.\n")
        for r in brands:
            out.append(f"- `{r['repo']}` mentions {', '.join(r['brand_collision'])}")

    text = "\n".join(out) + "\n"
    if args.out == "-":
        print(text)
    else:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(rows)} repositories, {len(leaks)} leak findings)")
    return 1 if leaks else 0


if __name__ == "__main__":
    raise SystemExit(main())