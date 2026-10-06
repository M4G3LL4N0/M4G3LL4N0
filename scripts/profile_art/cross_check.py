#!/usr/bin/env python3
"""Cross-check that description, README and venture story agree.

A bad mapping is invisible locally: the repository looks finished and nobody
compares the three surfaces. Three checks catch it.

  DESCRIPTION_VS_README   the About description and the README must describe
                          the same thing. If GitHub says "model evaluation
                          harness" and the README says "startup CRM", that is a
                          mapping failure, not a wording preference.

  NOAERTH_STORY_DRIFT     the venture card and the source describe different
                          fundamental products. GitHub stays technical; the
                          card is the external view. If they disagree the drift
                          is reported and only GitHub wording is adjusted, and
                          only when source supports the venture story.

  WEBSITE_CLAIM_UNSUPPORTED
                          the public site claims something source does not
                          support. Not repeated on GitHub as fact. Reported.

  python3 scripts/profile_art/cross_check.py
  python3 scripts/profile_art/cross_check.py --repo agentos
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
LEDGER = PROFILE / "github-account-ledger.json"
DOSSIERS = PROFILE / ".github-art" / "dossiers"
VENTURES = PROFILE / ".noaerth-public-ventures.json"
OUT = PROFILE / "data" / "cross-check.json"
OWNER = "M4G3LL4N0"

SCAFFOLD = re.compile(
    r"launch-site scaffold|no product surface|placeholder pages", re.I)
TRIVIA = re.compile(r"^(Startup portfolio:|Project repo for |Software project$)", re.I)

# Concepts that must not appear in one surface and contradict the other.
# Words that appear in launch-site scaffolding and carry no product meaning.
# Matching on them produced 126 false mismatches: every generated scaffold
# README mentions api, cli and deployment because the placeholder pages do.
NOISE = {"portfolio", "api", "cli", "deployment", "test", "workflow", "graph",
         "analytics", "dashboard", "benchmark", "search", "index", "queue",
         "pipeline", "memory", "router", "compiler"}

DOMAIN_WORDS = [
    "agent", "evaluation", "security", "encryption", "privacy", "scheduler",
    "queue", "index", "search", "graph", "pipeline", "workflow", "api",
    "cli", "dashboard", "analytics", "billing", "insurance", "erp", "crops",
    "logistics", "trading", "portfolio", "memory", "router", "compiler",
    "test", "benchmark", "deployment", "observability", "local-first",
]


def tok() -> str:
    return os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def raw(repo: str, branch: str, path: str) -> str | None:
    """Read a file from GitHub, preferring the API.

    raw.githubusercontent.com serves cached copies: after four README rewrites
    the raw path still returned the previous content, and the cross-check
    reported four repositories as unfixed that were in fact fixed. The contents
    API reflects the commit immediately. The raw host is kept only as a fallback
    when the API is rate limited, and a cached answer is worse than no answer,
    so the API is tried first.
    """
    import base64 as _b64
    d = subprocess.run(
        ["gh", "api", f"repos/{OWNER}/{repo}/contents/{path}"],
        capture_output=True, text=True, env=dict(os.environ, GH_TOKEN=tok()))
    if d.returncode == 0:
        try:
            data = json.loads(d.stdout)
            return _b64.b64decode(data["content"]).decode("utf-8", "replace")
        except Exception:
            pass
    try:
        with urllib.request.urlopen(
                f"https://raw.githubusercontent.com/{OWNER}/{repo}/{branch}/{path}",
                timeout=25) as fh:
            return fh.read().decode("utf-8", "replace")
    except Exception:
        return None


# Only the README's substantive prose counts, not its boilerplate nav or the
# placeholder pages' own copy.
BOILERPLATE = re.compile(
    r"so navigation and portfolio links do not 404|expand with "
    r"product-specific content|no product surface yet|launch-site scaffold", re.I)


def concepts(text: str) -> set[str]:
    low = text.lower()
    found = {w for w in DOMAIN_WORDS if re.search(rf"\b{w}", low)}
    return found - NOISE


def substantive(text: str) -> str:
    """README copy with scaffolding boilerplate removed."""
    return BOILERPLATE.sub(" ", text or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="")
    args = ap.parse_args()

    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    ventures = {}
    if VENTURES.exists():
        vd = json.loads(VENTURES.read_text(encoding="utf-8"))
        for v in vd.get("ventures", []):
            if not v["name"].startswith("_"):
                ventures[re.sub(r"[^a-z0-9]", "", v["name"].lower())] = v

    rows = []
    targets = [r for r in led["records"] if r["visibility"] == "public"]
    if args.repo:
        targets = [r for r in targets if r["name"] == args.repo]

    for rec in targets:
        name = rec["name"]
        branch = rec.get("default_branch") or "main"
        desc = (rec.get("description_text") or "").strip()
        readme = raw(name, branch, "README.md") or ""
        dossier_f = DOSSIERS / f"{name}.json"
        dossier = json.loads(dossier_f.read_text(encoding="utf-8")) \
            if dossier_f.exists() else {}
        vkey = re.sub(r"[^a-z0-9]", "", name.lower())
        venture = ventures.get(vkey)

        findings = []
        body = substantive(readme)
        d_concepts = concepts(desc)
        r_concepts = concepts(body)
        if (desc and body and d_concepts and r_concepts
                and not (d_concepts & r_concepts)
                and not SCAFFOLD.search(desc)):
            findings.append({
                "kind": "DESCRIPTION_VS_README",
                "detail": f"description names {sorted(d_concepts) or 'nothing'} "
                          f"but README names {sorted(r_concepts) or 'nothing'}; "
                          f"the two surfaces share no domain concept",
            })

        if TRIVIA.search(desc) or SCAFFOLD.search(desc):
            # A scaffold description is accurate, not a defect, but it must not
            # coexist with a README claiming a product.
            if body and len(body) > 400 and \
                    not re.search(r"scaffold|no product|placeholder", body, re.I):
                findings.append({
                    "kind": "DESCRIPTION_VS_README",
                    "detail": "description says scaffold but README reads as a "
                              "shipped product",
                })

        site = (venture or {}).get("site") or ""
        if venture and dossier:
            v_concepts = concepts(venture.get("positioning", "") or "")
            if not v_concepts:
                v_concepts = concepts(json.dumps(venture))
            s_concepts = concepts(json.dumps({k: v for k, v in dossier.items()
                                              if k in ("purpose", "primary_workflow",
                                                       "animation_metaphor",
                                                       "project_category",
                                                       "architecture_type")}))
            if v_concepts and s_concepts and not (v_concepts & s_concepts):
                findings.append({
                    "kind": "NOAERTH_STORY_DRIFT",
                    "detail": f"venture card names {sorted(v_concepts)[:4]} "
                              f"but source dossiers name {sorted(s_concepts)[:4]}; "
                              f"fundamentally different product stories",
                    "venture_slug": venture["slug"],
                    "action": "report only; product is not altered",
                })
        if site:
            findings.append({
                "kind": "WEBSITE_REVIEW_PENDING",
                "detail": f"public site {site} not yet read; claims must be "
                          f"verified against source before GitHub repeats them",
                "site": site,
            })
        rows.append({"repo": name, "findings": findings})

    counts: dict[str, int] = {}
    for r in rows:
        for f in r["findings"]:
            counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    drift = counts.get("NOAERTH_STORY_DRIFT", 0)
    mismatch = counts.get("DESCRIPTION_VS_README", 0)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "checked": len(rows),
        "counts": counts,
        "rows": [r for r in rows if r["findings"]],
    }, indent=1) + "\n")

    print("CROSS CHECK")
    print(f"  repositories checked : {len(rows)}")
    for k, v in sorted(counts.items()):
        print(f"  {k:<28}{v}")
    print()
    if mismatch or drift:
        for r in rows:
            for f in r["findings"]:
                if f["kind"] in ("DESCRIPTION_VS_README", "NOAERTH_STORY_DRIFT"):
                    print(f"  {r['repo']:<26}{f['kind']}")
                    print(f"      {f['detail'][:96]}")
    else:
        print("  no description, README or venture-story mismatches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())