#!/usr/bin/env python3
"""Persistent, resumable completion state.

The previous run of this work ran out of budget with substantial work
unfinished. This file exists so that never costs more than the remaining work:
every repository's completion state is persisted, and a new run reads it and
continues from the first incomplete repository rather than from repository one.

Idempotent by construction. Re-running any operation recomputes the same state
from the same inputs and writes the same result; nothing accumulates and
nothing depends on having run in a particular order.

  python3 scripts/profile_art/resume_state.py --init
  python3 scripts/profile_art/resume_state.py --status
  python3 scripts/profile_art/resume_state.py --record <repo> <state> \
      --files N --branch B --pr URL --ci STATE --next "action"
  python3 scripts/profile_art/resume_state.py --next
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
STATE = PROFILE / ".github-elite-state.json"
LEDGER = PROFILE / "github-account-ledger.json"

# Ordered exactly as the completion queue requires: blocking account fixes
# first, then flagships, then projects, then labs, then archives. Within a
# class, smallest remaining completion cost first, so the completion percentage
# rises quickly while critical defects still get priority.
CLASS_ORDER = ["BLOCKING", "FLAGSHIP", "PUBLIC_PROJECT", "LAB", "ARCHIVE"]

FIELDS_COMPLETE = [
    "description_complete", "topics_complete", "homepage_complete",
    "readme_complete", "hero_complete", "animated_art_complete",
    "static_fallback_complete", "social_preview_complete", "license_state",
    "security_state", "contributing_state", "code_of_conduct_state",
    "support_state", "issues_state", "discussions_state", "issue_forms_state",
    "pr_template_state", "ci_state", "tests_state", "fresh_clone_state",
    "benchmark_state", "technical_review_state", "security_review_state",
    "release_state", "ruleset_state", "changelog_state",
]


def load() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def save(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n",
                     encoding="utf-8")


def now() -> str:
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True).stdout.strip()


def pending_fields(rec: dict) -> list[str]:
    return [f for f in FIELDS_COMPLETE
            if isinstance(rec.get(f), dict) and rec[f].get("state") != "COMPLETE"]


def cost(rec: dict) -> int:
    return len(pending_fields(rec))


def classify(rec: dict) -> str:
    if rec.get("denylisted") or rec.get("site_only"):
        return "BLOCKING"
    led = load().get("records", {}).get(rec["name"], {})
    if led.get("classification") in ("FLAGSHIP",):
        return "FLAGSHIP"
    topics = {t.lower() for t in (rec.get("topics") or [])}
    if led.get("blockers"):
        return "BLOCKING"
    if rec.get("classification") == "PUBLIC_ARCHIVE" or rec.get("archived"):
        return "ARCHIVE"
    if not rec.get("description_complete", {}).get("state") == "COMPLETE":
        return "LAB"
    return "PUBLIC_PROJECT"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--next", action="store_true", dest="show_next")
    ap.add_argument("--record")
    ap.add_argument("--files", type=int, default=0)
    ap.add_argument("--branch", default="")
    ap.add_argument("--pr", default="")
    ap.add_argument("--ci", default="")
    ap.add_argument("--action", default="", dest="next_action")
    args = ap.parse_args()

    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    records = led["records"]

    if args.init or not STATE.exists():
        state = {
            "$comment": "Resumable completion state. Written after every "
                        "repository so an interrupted run continues from the "
                        "first incomplete record rather than from the start.",
            "schema": 1,
            "canonical_count": led["canonical_count"],
            "initiated_at": now(),
            "records": {},
            "queue": [],
        }
        for rec in sorted(records, key=lambda r: (CLASS_ORDER.index(classify(r)),
                                                 cost(r), r["name"].lower())):
            if rec.get("denylisted"):
                continue
            state["queue"].append({
                "name": rec["name"],
                "class": classify(rec),
                "pending_fields": cost(rec),
                "state": "PENDING",
            })
        # Denylisted repositories are permanently private and carry no
        # completion obligation. Listing them as pending work would put a
        # permanent non-action at the head of the queue forever.
        def initial_state(r: dict) -> str:
            if r.get("denylisted"):
                return "EXCLUDED_DENYLISTED"
            if r.get("site_only"):
                return "PENDING"
            return "PENDING"

        state["records"] = {r["name"]: {"state": initial_state(r),
                                        "pending_fields": 0 if r.get("denylisted")
                                        else cost(r),
                                        "class": classify(r)} for r in records}
        save(state)
        print(f"initialised {STATE.name} from {led['canonical_count']} records")
        if not (args.status or args.show_next):
            return 0

    state = load()

    if args.record:
        rec = state["records"].get(args.record)
        if rec is None:
            print(f"unknown repository {args.record}", flush=True)
            return 2
        rec.update({
            "state": args.record and rec["state"],
            "files_changed": args.files,
            "branch": args.branch,
            "pr": args.pr,
            "ci": args.ci,
            "next_action": args.next_action,
            "updated_at": now(),
        })
        if args.ci in ("GREEN", "PASS", "SUCCESS"):
            rec["state"] = "DONE"
        elif args.pr:
            rec["state"] = "IN_REVIEW"
        else:
            rec["state"] = "IN_PROGRESS"
        if rec["state"] == "DONE":
            rec["pending_fields"] = 0
        for q in state["queue"]:
            if q["name"] == args.record:
                q["state"] = rec["state"]
        save(state)
        print(f"recorded {args.record}: {rec['state']}")
        return 0

    done = sum(1 for r in state["records"].values() if r["state"] == "DONE")
    excluded = sum(1 for r in state["records"].values()
                   if r["state"] == "EXCLUDED_DENYLISTED")
    total = len(state["queue"])

    if args.status or not args.record:
        print("COMPLETION STATE")
        print(f"  canonical repositories : {state['canonical_count']}")
        print(f"  excluded (denylisted)  : {excluded}")
        print(f"  in completion queue    : {total}")
        print(f"  done                   : {done}")
        print(f"  remaining              : {total - done}")
        print()
        by_class: dict[str, list] = {}
        for q in state["queue"]:
            by_class.setdefault(q["class"], []).append(q)
        for c in CLASS_ORDER:
            items = by_class.get(c, [])
            if not items:
                continue
            d = sum(1 for i in items if i["state"] == "DONE")
            print(f"  {c:<15}{d:>4}/{len(items):<4} "
                  f"pending fields: {sum(i['pending_fields'] for i in items)}")
        pct = 100.0 * done / total if total else 0.0
        filled = int(round(pct / 100 * 24))
        print()
        print(f"  OVERALL  [{'#' * filled}{'.' * (24 - filled)}] {pct:.0f}%")

    if args.show_next:
        pend = [q for q in state["queue"] if q["state"] != "DONE"]
        pend.sort(key=lambda q: (CLASS_ORDER.index(q["class"]), q["pending_fields"]))
        if not pend:
            print("\n  nothing pending")
            return 0
        print("\n  NEXT UP")
        for q in pend[:5]:
            print(f"    {q['name']:<34}{q['class']:<15}"
                  f"{q['pending_fields']:>3} fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())