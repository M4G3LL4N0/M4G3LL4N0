#!/usr/bin/env python3
"""Cache the public Noaerth venture catalog once, then map it locally.

Source B of the project truth triangle: how a project is presented to an
external visitor. Fetched once and cached, because hitting noaerth.com per
repository per run is both slow and rude.

Only public information is extracted. Marketing language is captured as
positioning to reconcile against code, never copied into a README: the GitHub
audience is more technical, and a repository README that repeats a landing page
adds nothing a reader could not get from the landing page.

  python3 scripts/profile_art/fetch_noaerth_ventures.py
  python3 scripts/profile_art/fetch_noaerth_ventures.py --stale-hours 24
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import urllib.request
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
CACHE = PROFILE / ".noaerth-public-ventures.json"
SOURCE = "https://www.noaerth.com"

CARD = re.compile(
    r'<a href="(?P<site>https?://[^"]+)"[^>]*aria-label="Open (?P<name>[^"]+?) site"'
    r'.*?</article>', re.S)
NAME_H1 = re.compile(r"<h[1-3][^>]*>(?P<n>[^<]{2,80})</h[1-3]>")
TAG = re.compile(r'class="nx-vos-[a-z-]+"[^>]*>(?P<t>[^<]{2,120})<')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "github-profile-inventory"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return fh.read().decode("utf-8", "replace")


def parse(html: str) -> list[dict]:
    out: list[dict] = []
    for m in CARD.finditer(html):
        name = m.group("name").strip()
        block = m.group(0)
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        out.append({
            "name": name,
            "slug": slug,
            "site": m.group("site"),
            "aria_label": f"Open {name} site",
            "positioning": "",
            "category": "",
            "status": "",
            "public_links": [m.group("site")],
            "public_metrics": {},
            "retrieved_at": dt.datetime.now(dt.timezone.utc)
                              .strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    # Section headings give category and status vocabulary without needing a
    # per-venture API. Captured once as page-level context.
    sections = [{"heading": h.strip()}
                for h in re.findall(r'<h2[^>]*>([^<]{4,90})</h2>', html)]

    # Named projects appear in prose lists; capture those names too so a
    # repository with no card can still be matched by name.
    named = set()
    for m in re.finditer(r"<li>([^<]{2,70})</li>", html):
        text = re.sub(r"\s+", " ", m.group(1)).strip()
        if "—" in text:
            named.add(text.split("—")[0].strip())

    for v in out:
        v["page_sections"] = sections[:12]
    if named:
        out.append({"name": "_named_in_prose", "slug": "_prose",
                    "site": "", "positioning": "", "category": "", "status": "",
                    "public_links": [], "public_metrics": {},
                    "names": sorted(named),
                    "retrieved_at": dt.datetime.now(dt.timezone.utc)
                                    .strftime("%Y-%m-%dT%H:%M:%SZ")})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-hours", type=int, default=24)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if CACHE.exists() and not args.force:
        cached = json.loads(CACHE.read_text(encoding="utf-8"))
        got = cached.get("retrieved_at", "")
        try:
            age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(
                got.replace("Z", "+00:00"))
        except ValueError:
            age = dt.timedelta(hours=999)
        if age < dt.timedelta(hours=args.stale_hours):
            print(f"cache fresh ({age.seconds // 3600}h old): "
                  f"{len(cached.get('ventures', []))} ventures")
            return 0

    try:
        html = fetch(SOURCE)
    except Exception as exc:
        print(f"fetch failed: {exc}")
        if CACHE.exists():
            print("  reusing existing cache")
            return 0
        return 1

    ventures = parse(html)
    CACHE.write_text(json.dumps({
        "$comment": "Public venture cards from noaerth.com. Public information "
                    "only. Positioning is captured to reconcile against code, "
                    "never copied verbatim into a README.",
        "source": SOURCE,
        "retrieved_at": dt.datetime.now(dt.timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ventures": ventures,
    }, indent=1) + "\n", encoding="utf-8")
    cards = [v for v in ventures if not v["name"].startswith("_")]
    print(f"cached {len(cards)} venture cards + prose names -> {CACHE.name}")
    for v in cards[:12]:
        print(f"  {v['name']:<28}{v['slug']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())