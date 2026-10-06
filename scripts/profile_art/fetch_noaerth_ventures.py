#!/usr/bin/env python3
"""Cache the public Noaerth venture catalog once, then map it locally.

Source B of the project truth triangle: how a project is presented to an
external visitor. Fetched once and cached, because hitting noaerth.com per
repository per run is both slow and rude.

Only public information is extracted. Marketing language is captured as
positioning to reconcile against code, never copied into a README: the GitHub
audience is more technical, and a repository README that repeats a landing page
adds nothing a reader could not get from the landing page.

Why the card is parsed structurally
-----------------------------------
An earlier version matched the card wrapper and captured a name and a site URL,
then hardcoded `positioning`, `category` and `status` to the empty string. It
reported 108 cached ventures while carrying none of the content that makes a
venture card useful, and Source B of the truth triangle was therefore never
actually read: all 126 dossiers ended with an empty venture category, an empty
venture stage and an empty positioning.

The card markup carries all of it. Each card on /portfolio contains a category,
a status, a one-line pitch, operating-fact chips, signal meters and the next
milestone:

    <div class="venture-info-outline category-box"><span>Category</span>
      <strong title="Developer tools">Developer tools</strong></div>
    <div class="venture-info-outline status-box"><span>Status</span>
      <strong>Live</strong></div>
    <p class="nx-vos-pitch">Requested is not verified.</p>
    <span class="nx-vos-chip"><em>Stage</em>Live</span>
    <div class="nx-vos-meter-row"><span>Public surface</span><span>Ready</span></div>
    <span class="nx-vos-milestone-text">Improve conversion on AgentOS live surface</span>

One subtlety, and it was a real misparse: the enclosing <article> opens *after*
the <a> that wraps the card, so searching backwards from the anchor finds the
*previous* card's article and shifts every field by one row. The pitch that
looks like AgentOS's is SunsetX's. The card is located by searching forward.

The cache is also checked before it is accepted. A scraper that silently returns
names with no content must fail loudly rather than look like a successful run.

  python3 scripts/profile_art/fetch_noaerth_ventures.py
  python3 scripts/profile_art/fetch_noaerth_ventures.py --stale-hours 24
  python3 scripts/profile_art/fetch_noaerth_ventures.py --force
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import urllib.request
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
CACHE = PROFILE / ".noaerth-public-ventures.json"
SOURCE = "https://www.noaerth.com"
PORTFOLIO = "https://www.noaerth.com/portfolio"

# The anchor that identifies a card. The card body is located separately,
# forward from this match, because <article> opens after the <a>.
ANCHOR = re.compile(
    r'<a href="(?P<site>https?://[^"]+)"[^>]*aria-label="Open (?P<name>[^"]+?) site"')
ARTICLE_OPEN = "<article"
ARTICLE_CLOSE = "</article>"

SLUG = re.compile(r"/venture-favicons/(?P<slug>[a-z0-9-]+)\.svg")
CATEGORY = re.compile(
    r'class="venture-info-outline category-box"><span>Category</span>'
    r'<strong(?: title="(?P<title>[^"]*)")?>(?P<value>[^<]+)</strong>')
STATUS = re.compile(
    r'class="venture-info-outline status-box"><span>Status</span>'
    r'<strong>(?P<value>[^<]+)</strong>')
PITCH = re.compile(r'<p class="nx-vos-pitch">(?P<value>[^<]+)</p>')
CHIP = re.compile(
    r'<span class="nx-vos-chip"><em>(?P<key>[^<]+)</em>(?: <!-- -->)?(?P<value>[^<]*)</span>')
METER = re.compile(
    r'<div class="nx-vos-meter-row"><span>(?P<key>[^<]+)</span>'
    r'<span>(?P<value>[^<]+)</span></div>')
SIGNAL = re.compile(
    r'<span class="nx-vos-signal-chip-label">(?P<key>[^<]+)</span>'
    r'<span class="nx-vos-signal-chip-val">(?P<value>[^<]+)</span>')
MILESTONE = re.compile(
    r'<span class="nx-vos-milestone-text">(?P<value>[^<]+)</span>')
TONE = re.compile(r'data-tone="(?P<tone>[a-z]+)"')
HEADING = re.compile(r"<h2[^>]*>(?P<text>[^<]{4,90})</h2>")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "github-profile-inventory"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return fh.read().decode("utf-8", "replace")


def _text(m: re.Match | None) -> str:
    return m.group("value").strip() if m else ""


def parse(html: str) -> list[dict]:
    """Extract one record per venture card, with the card's own public fields."""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sections = [{"heading": h.strip()} for h in HEADING.findall(html) if h.strip()]
    out: list[dict] = []
    seen: set[str] = set()

    for m in ANCHOR.finditer(html):
        name = m.group("name").strip()
        # Forward search only. Searching backwards from the anchor lands in the
        # previous card and silently shifts every field by one row.
        start = html.find(ARTICLE_OPEN, m.end())
        if start < 0:
            continue
        end = html.find(ARTICLE_CLOSE, start)
        if end < 0:
            continue
        card = html[start:end]

        slug_m = SLUG.search(card)
        slug = slug_m.group("slug") if slug_m else re.sub(
            r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if slug in seen:
            continue
        seen.add(slug)

        cat = CATEGORY.search(card)
        out.append({
            "name": name,
            "slug": slug,
            "site": m.group("site"),
            "aria_label": f"Open {name} site",
            # Public positioning as the site presents it. Reconciled against
            # code, never copied into a README.
            "positioning": _text(PITCH.search(card)),
            "category": (cat.group("value").strip() if cat else ""),
            "category_path": ((cat.group("title") or "").strip() if cat else ""),
            "status": _text(STATUS.search(card)),
            "tone": (TONE.search(card).group("tone") if TONE.search(card) else ""),
            "operating_facts": {c.group("key").strip(): c.group("value").strip()
                                for c in CHIP.finditer(card)},
            "signal_meters": {x.group("key").strip(): x.group("value").strip()
                              for x in METER.finditer(card)},
            "signals": {s.group("key").strip(): s.group("value").strip()
                        for s in SIGNAL.finditer(card)},
            "next_milestone": _text(MILESTONE.search(card)),
            "public_links": [m.group("site")],
            "public_metrics": {},
            "page_sections": sections[:12],
            "retrieved_at": stamp,
        })

    return out


def summarise(ventures: list[dict]) -> dict:
    """Field-population counts, so an empty cache cannot pass as a full one."""
    keys = ("positioning", "category", "status", "next_milestone", "tone")
    got = {k: sum(1 for v in ventures if v.get(k)) for k in keys}
    return {
        "cards": len(ventures),
        "field_population": got,
        # Category and status are on every card. A scraper that captures names
        # but no content must fail this rather than look like a successful run.
        "complete": bool(ventures) and all(
            got[k] >= len(ventures) - 1 for k in ("category", "status")),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-hours", type=int, default=24,
                    dest="stale_hours")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--url", default=PORTFOLIO)
    args = ap.parse_args()

    if CACHE.exists() and not args.force:
        cached = json.loads(CACHE.read_text(encoding="utf-8"))
        got = cached.get("retrieved_at", "")
        try:
            age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(
                got.replace("Z", "+00:00"))
        except ValueError:
            age = dt.timedelta(hours=999)
        ventures = [v for v in cached.get("ventures", [])
                    if not v.get("name", "").startswith("_")]
        s = summarise(ventures)
        if age < dt.timedelta(hours=args.stale_hours) and s["complete"]:
            print(f"cache fresh ({age.seconds // 3600}h old): {s['cards']} cards, "
                  f"category {s['field_population']['category']}, "
                  f"status {s['field_population']['status']}")
            return 0
        # Stale in CONTENT as well as time is the failure that matters: a cache
        # full of slugs with no fields is not a cache, and refreshing only the
        # timestamp would have hidden that for a year.
        print(f"cache unusable (age {age.days}d, complete={s['complete']}, "
              f"category {s['field_population']['category']}/"
              f"{s['cards']}); re-fetching")

    try:
        html = fetch(args.url)
    except Exception as exc:
        print(f"fetch failed: {exc}")
        if CACHE.exists():
            print("  reusing existing cache")
            return 0
        return 1

    ventures = parse(html)
    if not ventures:
        print("no venture cards parsed; refusing to overwrite a good cache")
        return 1

    s = summarise(ventures)
    if not s["complete"]:
        print(f"parsed {s['cards']} cards but category/status coverage is "
              f"{s['field_population']['category']}/{s['field_population']['status']}; "
              "the site markup changed. Not overwriting the cache.")
        return 1

    CACHE.write_text(json.dumps({
        "$comment": "Public venture cards from noaerth.com/portfolio. Public "
                    "information only. Positioning is captured to reconcile "
                    "against code, never copied verbatim into a README.",
        "source": SOURCE,
        "portfolio_url": args.url,
        "retrieved_at": dt.datetime.now(dt.timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": s,
        "ventures": ventures,
    }, indent=1) + "\n", encoding="utf-8")

    print(f"cached {s['cards']} venture cards -> {CACHE.name}")
    print(f"  category {s['field_population']['category']} · "
          f"status {s['field_population']['status']} · "
          f"positioning {s['field_population']['positioning']} · "
          f"milestone {s['field_population']['next_milestone']}")
    for v in ventures[:6]:
        print(f"  {v['slug']:<24}{v['category']:<26}{v['status']:<10}"
              f"{v['positioning'][:40]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
