#!/usr/bin/env python3
"""Build the V7 technical signal for the profile.

Replaces the previous business-weighted signal with a computer-science one.
Section 29 is explicit: engineering depth, systems work, computer science,
experimentation, research, open source and tooling are what the profile
promotes. Valuation and economics are not, and were removed in V7.

Everything here is counted from the dossiers and the enriched repository
snapshot. Nothing is asserted that was not measured, and the historical
financial metrics are gone rather than hidden.

  python3 scripts/profile_art/build_v7_signal.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
DOSSIERS = PROFILE / ".github-art" / "dossiers"
LEDGER = PROFILE / "github-account-ledger.json"
SIGNAL = PROFILE / "assets" / "profile" / "build-signal.json"
OUT = PROFILE / "data" / "v7-signal.json"

# Technical domain clusters for the public universe. Derived from each
# dossier's category, not from economic value.
DOMAIN = {
    "AGENT": "AGENTS",
    "SECURITY": "SECURITY",
    "FINANCE": "QUANT / DATA",
    "QUANT": "QUANT / DATA",
    "DATA": "QUANT / DATA",
    "DEVELOPER_TOOLS": "DEVELOPER TOOLS",
    "INFRASTRUCTURE": "INFRASTRUCTURE",
    "NETWORK": "INFRASTRUCTURE",
    "CREATIVE": "CREATIVE COMPUTING",
    "LAB": "LABS",
    "GENERAL": "APPLICATIONS",
}


def main() -> int:
    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    public = [r for r in led["records"] if r["visibility"] == "public"]

    dossiers = []
    for f in sorted(DOSSIERS.glob("*.json")):
        dossiers.append(json.loads(f.read_text(encoding="utf-8")))

    domains = Counter()
    languages = Counter()
    architectures = Counter()
    motions = Counter()
    for d in dossiers:
        domains[DOMAIN.get(d.get("project_category", "GENERAL"), "APPLICATIONS")] += 1
        architectures[d.get("architecture_type", "?")] += 1
        motions[d.get("animation_metaphor", "")] += 1
        for lang in (d.get("languages") or []):
            lang = lang.lower().strip()
            if lang and lang not in ("ts", "tsx", "mjs", "cjs"):
                languages[lang] += 1

    # Engineering evidence, read from the ledger rather than recomputed.
    tests = sum(r.get("tests_state", {}).get("files", 0) for r in public)
    # tests.json is a single object: repo -> { count, command, verified_on }.
    # Counts are operator-recorded because GitHub has no API for test totals,
    # so they are only summed for repositories that are actually public.
    measured_tests = 0
    counted: list[str] = []
    public_names = {r["name"].lower() for r in public}
    tf = PROFILE / "tests.json"
    if tf.exists():
        data = json.loads(tf.read_text(encoding="utf-8"))
        for name, rec in data.items():
            if name.startswith("_") or not isinstance(rec, dict):
                continue
            if name.lower() not in public_names:
                continue          # private or denylisted: never counted publicly
            measured_tests += int(rec.get("count") or 0)
            counted.append(name)

    ci_configured = sum(
        1 for r in public if r.get("ci_state", {}).get("state") == "COMPLETE")
    security = sum(
        1 for r in public if r.get("security_state", {}).get("state") == "COMPLETE")
    contributing = sum(
        1 for r in public if r.get("contributing_state", {}).get("state") == "COMPLETE")
    readmes = sum(
        1 for r in public if r.get("readme_complete", {}).get("state") == "COMPLETE")
    releases = sum(
        1 for r in public if r.get("release_state", {}).get("state") == "COMPLETE")
    licenses = sum(
        1 for r in public if r.get("license_state", {}).get("state") == "COMPLETE")

    signal = {
        "$comment": "V7 technical signal. Engineering evidence only. Portfolio "
                    "economics were removed from GitHub by direction change.",
        "account": led["account"],
        # The measurement time belongs to the measurement, not to the render.
        # Reading the clock while rendering made render_v7_signal.py produce a
        # different README every run, so the "generated blocks are up to date"
        # gate could never pass.
        "measured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": {
            "public_repositories": len(public),
            "dossiers": len(dossiers),
        },
        "engineering": {
            "measured_tests": measured_tests,
            "repositories_with_tests": sum(
                1 for d in dossiers if d.get("tests", {}).get("present")),
            "ci_configured": ci_configured,
            "releases": releases,
            "licenses": licenses,
            "readmes_complete": readmes,
            "security_policies": security,
            "contributing_guides": contributing,
        },
        "technical_domains": dict(domains.most_common()),
        "architectures": dict(architectures.most_common()),
        "languages": dict(languages.most_common(12)),
        "distinct_motion_stories": len([m for m in motions if m]),
        "distinct_architectures": len(architectures),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(signal, indent=1, sort_keys=True) + "\n")
    print(f"  wrote {OUT.name}")
    print(f"    public repositories : {len(public)}")
    print(f"    dossiers            : {len(dossiers)}")
    print(f"    measured tests      : {measured_tests}")
    print(f"    ci configured       : {ci_configured}")
    print(f"    releases            : {releases}")
    print(f"    technical domains   : {len(domains)}")
    print(f"    distinct motions    : {signal['distinct_motion_stories']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())