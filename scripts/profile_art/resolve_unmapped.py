#!/usr/bin/env python3
"""Resolve the repositories that mapping deliberately refused to guess.

Ten repositories have no local project folder and no venture card, so
build_dossiers.py marked them MAPPING_REVIEW_REQUIRED rather than inventing a
correspondence. That refusal is correct and is preserved here: this script only
resolves a repository when its own contents identify it unambiguously, and it
records the evidence for each decision.

Three classes:

  PROFILE          the profile repository itself
  ARTIFACT         an accidental commit, not a project. Reported, never
                   featured, and never deleted without authorisation.
  MISNAMED_WORK    real engineering under a generic directory-style name

  python3 scripts/profile_art/resolve_unmapped.py
  python3 scripts/profile_art/resolve_unmapped.py --verify
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
MAP = PROFILE / "project-map.json"
OVERRIDES = PROFILE / ".github-art" / "mapping-overrides.json"
OWNER = "M4G3LL4N0"

# Each entry states what the repository actually is and how that was determined.
# Nothing here is a guess: every entry cites evidence observable in the
# repository itself.
DECISIONS: dict[str, dict] = {
    "M4G3LL4N0": {
        "resolution": "PROFILE",
        "canonical_project_name": "DUNG30N5 profile",
        "evidence": "repository contains README.md and assets/profile only; it "
                    "is the account profile, not an engineering system",
        "feature": False,
        "generate_art": False,
    },
    "why-are-you-here": {
        "resolution": "MISNAMED_WORK",
        "canonical_project_name": "Why Are You Here",
        "evidence": "single-page site with its own source; an intentional "
                    "authored page rather than an accidental artifact",
        "feature": False,
        "generate_art": True,
    },
    "src": {
        "resolution": "MISNAMED_WORK",
        "canonical_project_name": "src",
        "evidence": "contains app/, components/, docs/ and a Next.js tree. This "
                    "is a real application committed under a directory-style "
                    "name, not a stray folder.",
        "feature": False,
        "generate_art": True,
    },
    "styles": {
        "resolution": "MISNAMED_WORK",
        "canonical_project_name": "styles",
        "evidence": "contains main.css plus a docs/ directory: a design-token "
                    "and stylesheet system published under a directory-style name",
        "feature": False,
        "generate_art": True,
    },
    "node_modules": {
        "resolution": "ARTIFACT",
        "canonical_project_name": "node_modules",
        "evidence": "root contains .DS_Store, .package-lock.json and installed "
                    "packages (@supabase, @types, clsx, tslib, undici-types, "
                    "ws). This is a committed dependency directory, not source.",
        "feature": False,
        "generate_art": False,
        "action_required": "owner decision: deletion is not authorised",
    },
    "imessage": {
        "resolution": "UNRESOLVED_REVIEW",
        "canonical_project_name": "imessage",
        "evidence": "repository carries the standard portfolio register set but "
                    "no local checkout and no venture card; correspondence "
                    "cannot be established from available sources",
        "feature": False,
        "generate_art": False,
        "action_required": "owner decision: supply the local project path",
    },
    "ai-dev-workflow-starter": {
        "resolution": "UNRESOLVED_REVIEW",
        "canonical_project_name": "AI Dev Workflow Starter",
        "evidence": "template repository with no local checkout and no venture "
                    "card; correspondence cannot be established",
        "feature": False,
        "generate_art": False,
        "action_required": "owner decision: supply the local project path",
    },
    "FundMind": {
        "resolution": "UNRESOLVED_REVIEW",
        "canonical_project_name": "FundMind",
        "evidence": "no local checkout and no venture card",
        "feature": False,
        "generate_art": False,
        "action_required": "owner decision: supply the local project path",
    },
    "STRxGNTH": {
        "resolution": "UNRESOLVED_REVIEW",
        "canonical_project_name": "STRxGNTH",
        "evidence": "no local checkout and no venture card",
        "feature": False,
        "generate_art": False,
        "action_required": "owner decision: supply the local project path",
    },
    "Zaeus": {
        "resolution": "UNRESOLVED_REVIEW",
        "canonical_project_name": "Zaeus",
        "evidence": "no local checkout and no venture card",
        "feature": False,
        "generate_art": False,
        "action_required": "owner decision: supply the local project path",
    },
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    OVERRIDES.parent.mkdir(parents=True, exist_ok=True)

    if args.verify:
        if not OVERRIDES.exists():
            print("no mapping overrides recorded")
            return 1
        data = json.loads(OVERRIDES.read_text(encoding="utf-8"))
        decisions = data["decisions"]
        unresolved = [k for k, v in decisions.items()
                      if v["resolution"] == "UNRESOLVED_REVIEW"]
        artifacts = [k for k, v in decisions.items() if v["resolution"] == "ARTIFACT"]
        print("MAPPING RESOLUTION")
        print(f"  resolved            : {len(decisions)}")
        print(f"  profile             : {sum(1 for v in decisions.values() if v['resolution']=='PROFILE')}")
        print(f"  misnamed work       : {sum(1 for v in decisions.values() if v['resolution']=='MISNAMED_WORK')}")
        print(f"  artifacts           : {len(artifacts)}  {artifacts}")
        print(f"  awaiting owner input: {len(unresolved)}  {unresolved}")
        return 0

    data = {
        "$comment": "Repositories mapping refused to guess. Each entry states "
                    "what the repository is and the evidence for it. UNRESOLVED "
                    "entries remain unresolved rather than being assigned a "
                    "project by assumption.",
        "owner": OWNER,
        "decisions": DECISIONS,
    }
    OVERRIDES.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n",
                         encoding="utf-8")
    print(f"wrote {OVERRIDES.name}")
    for name, d in sorted(DECISIONS.items()):
        print(f"  {name:<28}{d['resolution']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())