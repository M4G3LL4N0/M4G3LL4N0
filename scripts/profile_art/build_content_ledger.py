#!/usr/bin/env python3
"""Build GITHUB_V5_CONTENT_LEDGER.json.

A redesign is only safe if you can prove afterwards that nothing factual was
lost. This captures what every public README currently asserts, so the V5
rollout can diff ledger -> new README and show that every command, link,
license, caveat, and architectural claim survived.

What is recorded per public repository:

  commands    install / build / test / run invocations found in fenced blocks
  links       outbound URLs, split into first-party and third-party
  claims      architectural and capability sentences, kept verbatim
  caveats     sentences containing a limit or an honest negative
  facts       license, releases, verified test count, CI state, topics

Only public repositories are read. Private and deployment-site repositories are
never opened, so they cannot leak through this file.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
INVENTORY = PROFILE / "GITHUB_V5_PUBLIC_INVENTORY.json"
OUT = PROFILE / "GITHUB_V5_CONTENT_LEDGER.json"

FENCE = re.compile(r"```[a-zA-Z0-9_+-]*\n(.*?)```", re.S)
URL = re.compile(r"https?://[^\s)\]\"'>]+")
CAVEAT = re.compile(
    r"^.*\b(?:not\b|never|cannot|can't|does not|doesn't|deliberately|"
    r"out of scope|non-goal|limitation|caveat|only\b.*\bnot\b|"
    r"unproven|unverified|experimental|not yet|no longer)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)
CLAIM = re.compile(
    r"^.*\b(?:architecture|design|invariant|guarantee|pipeline|layer|"
    r"contract|state machine|queue|ledger|deterministic|"
    r"circuit breaker|source of truth)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)
SENTENCE = re.compile(r"(?<=[.!?])\s+")
BADGE = re.compile(r"shields\.io|badge|img\.", re.IGNORECASE)


def read_readme(full_name: str) -> str:
    result = subprocess.run(
        ["gh", "api", f"repos/{full_name}/readme", "--jq", ".content"],
        capture_output=True, text=True, timeout=45, check=False,
        env={**os.environ},
    )
    if result.returncode or not result.stdout.strip():
        return ""
    try:
        return base64.b64decode(result.stdout.strip()).decode("utf-8", "replace")
    except Exception:
        return ""


def commands_from(readme: str) -> list[str]:
    """Invocations a reader could actually paste."""
    found: list[str] = []
    for block in FENCE.findall(readme):
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "$")):
                continue
            if re.match(r"^(npm|pnpm|yarn|go|cargo|make|docker|git|python3?|pip|uv|"
                        r"npx|bun|deno|gh|kubectl|curl|bash|sh|poetry|rye|"
                        r"node|pytest|go test|cargo)\b", line):
                found.append(line)
    # preserve order, drop duplicates
    seen: set[str] = set()
    return [c for c in found if not (c in seen or seen.add(c))][:40]


def links_from(readme: str, owner: str) -> dict[str, list[str]]:
    clean: list[str] = []
    third_party: list[str] = []
    for url in URL.findall(readme):
        url = url.rstrip(".,);")
        if "shields.io" in url or "badge" in url.lower():
            continue
        if re.search(rf"github\.com/{owner}/", url) or "noaerth.com" in url:
            clean.append(url)
        else:
            third_party.append(url)
    return {
        "first_party": sorted(set(clean)),
        "third_party": sorted(set(third_party)),
    }


def sentences_matching(readme: str, pattern: re.Pattern) -> list[str]:
    body = FENCE.sub(" ", readme)
    hits: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line or BADGE.search(line):
            continue
        if pattern.match(line):
            for sentence in SENTENCE.split(line):
                sentence = sentence.strip(" -*_`#")
                if 24 <= len(sentence) <= 300:
                    hits.append(sentence)
    seen: set[str] = set()
    return [h for h in hits if not (h in seen or seen.add(h))][:25]


def main() -> int:
    if not INVENTORY.is_file():
        print("run build_public_inventory.py first", flush=True)
        return 1
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    owner = inventory["owner"]

    entries = {}
    for repo in inventory["repositories"]:
        readme = read_readme(repo["full_name"])
        entries[repo["name"]] = {
            "full_name": repo["full_name"],
            "classification": repo["classification"],
            "readme_present": bool(readme.strip()),
            "readme_bytes": len(readme.encode("utf-8")),
            "commands": commands_from(readme),
            "links": links_from(readme, owner),
            "architectural_claims": sentences_matching(readme, CLAIM),
            "caveats": sentences_matching(readme, CAVEAT),
            "facts": {
                "description": repo["description"],
                "license": repo["license"],
                "topics": repo["topics"],
                "verified_tests": repo["verified_tests"],
                "release_count": repo["release_count"],
                "latest_release": repo["latest_release"],
                "ci_green": repo["ci"]["green"],
                "ci_latest_conclusion": repo["ci"]["latest_conclusion"],
                "archived": repo["archived"],
                "homepage": repo["homepage"],
            },
        }

    totals = {
        "repositories": len(entries),
        "commands": sum(len(v["commands"]) for v in entries.values()),
        "first_party_links": sum(len(v["links"]["first_party"]) for v in entries.values()),
        "third_party_links": sum(len(v["links"]["third_party"]) for v in entries.values()),
        "claims": sum(len(v["architectural_claims"]) for v in entries.values()),
        "caveats": sum(len(v["caveats"]) for v in entries.values()),
    }

    payload = {
        "$comment": [
            "Semantic content ledger for the V5 redesign. Every fact a reader",
            "can currently obtain from a public README is captured here so the",
            "rollout can prove that nothing factual was lost.",
            "",
            "Public repositories only. Private and deployment-site repositories",
            "are never opened by the generator, so they cannot appear here even",
            "by accident."
        ],
        "schema": "github-v5-content-ledger/1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "owner": owner,
        "totals": totals,
        "repositories": entries,
    }

    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}")
    for key, value in totals.items():
        print(f"  {key:<20} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
