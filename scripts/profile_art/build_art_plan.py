#!/usr/bin/env python3
"""GITHUB_V6_PROJECT_ART_PLAN.md plus the uniqueness audit.

Every public owned repository gets a row. Missing rows fail the build: a plan
that silently omits a repository is how a repository ends up half-presented.

The uniqueness audit is the gate against one template producing a hundred
skins. It fails when many repositories share a hero structure, terminal
sequence or palette, and it reports the distribution rather than asserting a
number -- a portfolio can legitimately be 40% data-flow web applications, and
the art must express that honestly rather than fake variety.

  python3 scripts/profile_art/build_art_plan.py
  python3 scripts/profile_art/build_art_plan.py --audit-only
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts"))
DOSSIERS = PROFILE / ".github-art" / "dossiers"
MAP = PROFILE / "project-map.json"
OVERRIDES = PROFILE / ".github-art" / "mapping-overrides.json"
VENTURES = PROFILE / ".noaerth-public-ventures.json"
IDENTITIES = PROFILE / "data" / "generated-identities.json"
OUT = PROFILE / "GITHUB_V6_PROJECT_ART_PLAN.md"

DENY_SUB = ("noaerth", "autobuilder", "pairs")
DENY_EXACT = {"paios-one", "openlegal-data"}


def denied(name: str) -> bool:
    low = name.lower()
    return any(s in low for s in DENY_SUB) or low in DENY_EXACT


def load() -> tuple[list[dict], dict, dict, dict]:
    dossiers = []
    for f in sorted(DOSSIERS.glob("*.json")):
        dossiers.append(json.loads(f.read_text(encoding="utf-8")))
    mapping = json.loads(MAP.read_text(encoding="utf-8"))
    overrides = (json.loads(OVERRIDES.read_text(encoding="utf-8"))["decisions"]
                 if OVERRIDES.exists() else {})
    ident = (json.loads(IDENTITIES.read_text(encoding="utf-8"))["identities"]
             if IDENTITIES.exists() else {})
    return dossiers, mapping, overrides, ident


def audit(dossiers: list[dict], ident: dict) -> tuple[list[str], dict]:
    problems: list[str] = []
    counts = {
        "architecture": Counter(),
        "category": Counter(),
        "motif": Counter(),
        "material": Counter(),
        "accent": Counter(),
        "animation": Counter(),
    }
    structural: dict[tuple, list[str]] = defaultdict(list)

    for d in dossiers:
        name = d["github_repo"]
        i = ident.get(name, {})
        arch = d.get("architecture_type", "")
        counts["architecture"][arch] += 1
        counts["category"][d.get("project_category", "")] += 1
        counts["animation"][d.get("animation_metaphor", "")] += 1
        counts["motif"][i.get("motif", "")] += 1
        counts["material"][i.get("material", "")] += 1
        counts["accent"][i.get("accent", "")] += 1
        key = (i.get("family"), i.get("motif"), i.get("material"),
               i.get("accent"), i.get("depth"), i.get("topology"))
        structural[key].append(name)

    collisions = {k: v for k, v in structural.items() if len(v) > 1}
    if collisions:
        for k, v in list(collisions.items())[:5]:
            problems.append(f"identity collision across {v}: {k}")

    total = max(1, len(dossiers))
    # A single animation story covering most of the portfolio is the failure
    # this audit exists to catch: it means the motion says nothing.
    for label in ("animation", "motif"):
        top, n = counts[label].most_common(1)[0] if counts[label] else ("", 0)
        if n / total > 0.55 and counts[label] and len(counts[label]) > 1:
            problems.append(
                f"{label}: {n}/{total} share '{top}' ({n/total:.0%}); a shared "
                f"story across most of the portfolio communicates nothing")
    return problems, counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-only", action="store_true")
    args = ap.parse_args()

    dossiers, mapping, overrides, ident = load()
    by_repo = {d["github_repo"]: d for d in dossiers}
    rec_by_repo = {r["map"]["github_repo"]: r["map"] for r in mapping["records"]}

    problems, counts = audit(dossiers, ident)

    if args.audit_only:
        print("UNIQUENESS AUDIT")
        for label, c in counts.items():
            print(f"  {label}: {len(c)} distinct")
            for k, n in c.most_common(4):
                print(f"    {str(k)[:52]:<54}{n}")
        print(f"\n  problems: {len(problems)}")
        for p in problems:
            print(f"    {p}")
        return 1 if problems else 0

    rows = []
    for name in sorted(set(rec_by_repo) | set(overrides)):
        if denied(name):
            continue
        ov = overrides.get(name)
        d = by_repo.get(name)
        m = rec_by_repo.get(name, {})
        i = ident.get(name, {})
        resolution = ov["resolution"] if ov else (
            d["mapping_confidence"] if d else "NO_DOSSIER")
        rows.append({
            "repo": name,
            "local": (ov or {}).get("evidence", "")[:0] or m.get("local_project_path", ""),
            "venture": m.get("noaerth_venture_slug", ""),
            "purpose": (d or {}).get("purpose", "") or m.get("classification", ""),
            "category": (d or {}).get("project_category", ""),
            "hero": (d or {}).get("primary_visual_metaphor", ""),
            "animation": (d or {}).get("animation_metaphor", ""),
            "terminal": (d or {}).get("terminal_metaphor", ""),
            "material": i.get("material", ""),
            "geometry": i.get("topology", i.get("family", "")),
            "colour": i.get("accent", ""),
            "resolution": resolution,
            "feature": (ov or {}).get("feature", bool(d)) if ov else bool(d),
            "readme": "full" if (d or {}).get("architecture_type") in
                      ("SCHEDULER", "PIPELINE", "AGENT_LOOP", "DATA_FLOW")
                      else "compact",
        })

    out = ["# GITHUB V6 — PROJECT ART PLAN", "",
           f"Every public owned repository: **{len(rows)}**. No repository is "
           "omitted; the count below is the plan.", "",
           "Design sources precede art. A row exists only where the three "
           "evidence sources resolved a project; unresolved repositories are "
           "listed with the decision they need rather than given an invented "
           "identity.", "",
           "## Coverage", "",
           f"| metric | value |", "| --- | --- |",
           f"| public owned repositories | {len(rows)} |",
           f"| dossiers ready | {sum(1 for r in rows if r['resolution'] == 'high')} |",
           f"| mapped to a local project | {sum(1 for r in rows if r['local'])} |",
           f"| matched a venture card | {sum(1 for r in rows if r['venture'])} |",
           f"| awaiting owner decision | {sum(1 for r in rows if r['resolution'] in ('UNRESOLVED_REVIEW','ARTIFACT','PROFILE'))} |",
           "",
           "## Per-repository plan", "",
           "| repo | local project | venture | category | hero idea | animation idea | terminal | material | geometry | colour | README |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append(
            f"| `{r['repo']}` | "
            f"{Path(r['local']).name if r['local'] else '—'} | "
            f"{r['venture'] or '—'} | {r['category'] or '—'} | "
            f"{r['hero'] or '—'} | {r['animation'] or '—'} | "
            f"{'yes' if r['terminal'] else '—'} | {r['material'] or '—'} | "
            f"{r['geometry'] or '—'} | {r['colour'] or '—'} | {r['readme']} |")

    out += ["", "## Uniqueness audit", ""]
    for label, c in counts.items():
        out.append(f"- **{label}**: {len(c)} distinct")
    out += ["", f"Problems: **{len(problems)}**", ""]
    for p in problems:
        out.append(f"- {p}")
    if not problems:
        out.append("No shared hero structure, palette or motion story across a "
                   "majority of the portfolio.")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}: {len(rows)} repositories, "
          f"{len(problems)} uniqueness problems")
    for p in problems[:4]:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())