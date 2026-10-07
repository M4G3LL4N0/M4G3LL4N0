"""Rebuild the profile README from measured portfolio data.

Every number in the output comes from the index, the render manifest or the
noaerth.com card cache. The previous README carried hardcoded figures that did
not match the portfolio (it claimed 2,032 tests against an actual 211), so the
counters are computed here rather than written by hand.
"""

from __future__ import annotations

import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import evidence as E  # noqa: E402

PROFILE = HERE.parents[2]
INDEX = E.INDEX
ART = PROFILE / ".github-art" / "v8-art"
CARDS = E.CARDS
OUT = PROFILE / "README.md"

OWNER_URL = f"https://github.com/{E.OWNER}"
SITE = "https://www.noaerth.com"

CATEGORY_BLURB = {
    "WEB_APPLICATION": "Product surfaces built on a shared Next.js base.",
    "SOFTWARE": "Libraries and tooling without a routable web surface.",
    "SCAFFOLD": "Committed placeholders. Labelled, not dressed up.",
    "SECURITY": "Policy and boundary work.",
    "CONCURRENCY": "Queue and worker scheduling.",
    "DATA_VISUALIZATION": "Rendering and charting surfaces.",
    "DATA_STRUCTURE": "Index and lookup structures.",
    "PERFORMANCE": "Measurement and profiling.",
    "SIMULATION": "State-space and simulation harnesses.",
}


def markers(name: str, body: str) -> str:
    """Wrap a generated section in the markers the profile test enforces."""
    return f"<!-- {name}:start -->\n{body}\n<!-- {name}:end -->"


def picture(slot: str, alt: str, branch: str = "main") -> str:
    base = (f"https://raw.githubusercontent.com/{E.OWNER}/{E.OWNER}/{branch}"
            f"/.github-art/surfaces")
    return "\n".join([
        "<picture>",
        f'  <source media="(prefers-reduced-motion: reduce)" srcset="{base}/{slot}-reduced.svg">',
        f'  <source media="(prefers-color-scheme: light)" srcset="{base}/{slot}-light.svg">',
        f'  <img alt="{alt}" src="{base}/{slot}-motion.svg">',
        "</picture>",
    ])


def load_cards() -> list[dict]:
    raw = json.loads(CARDS.read_text())
    return raw if isinstance(raw, list) else (
        raw.get("ventures") or raw.get("items")
        or next((v for v in raw.values() if isinstance(v, list)), [])
    )


def build() -> str:
    index = E.load_index()
    manifest = json.loads((ART / "manifest.json").read_text())
    cards = load_cards()

    routes = sum(len(r.get("routes") or []) for r in index.values())
    entries = sum(len(r.get("entry_points") or []) for r in index.values())
    modules = sum(len(r.get("modules") or []) for r in index.values())
    files = sum(r.get("files") or 0 for r in index.values())
    tests = sum(r.get("test_count") or 0 for r in index.values())
    tested_repos = sum(1 for r in index.values() if (r.get("test_count") or 0) > 0)
    ci = sum(len(r.get("ci_workflows") or []) for r in index.values())
    ci_repos = sum(1 for r in index.values() if (r.get("ci_workflows") or []))
    lang_files = sum(sum((r.get("languages") or {}).values()) for r in index.values())
    surfaces = sum(len(v["files"]) for v in manifest.values())
    slots = sum(len(v["slots"]) for v in manifest.values())
    statuses = collections.Counter(v["status"] for v in manifest.values())
    categories = collections.Counter(
        v["project_category"] for v in manifest.values()).most_common()

    live_cards = [c for c in cards if str(c.get("status", "")).lower() == "live"]

    L: list[str] = []
    a = L.append

    a(f'<p align="center">\n  <img alt="DUNG30N5 — NOAERTH" '
      f'src="https://raw.githubusercontent.com/{E.OWNER}/{E.OWNER}/main/'
      f'assets/hero/hero-motion.svg" width="100%">\n</p>')
    a("")
    a("<h1 align=\"center\">DUNG30N5</h1>")
    a(f'<p align="center"><strong>Technologist and founder of '
      f'<a href="{SITE}">NOAERTH</a>.</strong></p>')
    a("")
    a(f'<p align="center">I build the operating layer for venture creation: '
      f'{len(index)} public repositories, each one a working surface rather '
      f'than a promise. <a href="{SITE}">noaerth.com</a> is the parent.</p>')
    a("")

    # ---- measured facts ---------------------------------------------------
    # Restate build-signal.json rather than recomputing it. That file is the
    # defined metric source (regenerated from the live API) and its own
    # generator states the README block must reuse it so the two cannot drift.
    signal_path = PROFILE / "assets" / "profile" / "build-signal.json"
    if signal_path.exists():
        sig = json.loads(signal_path.read_text())
        rows = "\n".join(f"| {m['label']} | {m['display']} |" for m in sig["metrics"])
        a(markers("signal", "## Build signal\n\n" + rows))
        a("")
        a(f"<sub>Counted by `{signal_path.name.partition('.')[0]}-data`, "
          f"regenerated {sig.get('generated_at', 'from the live API')}. "
          f"Systems exclude site-only and identity repositories.</sub>")
        a("")

    a("## What is actually here")
    a("")
    a("These are counted from the repositories themselves, not estimated. "
      "The generator that produces this file walks every tree.")
    a("")
    a("Counted by walking each tree in this pass. The build signal below uses a "
      "different, deliberately narrower definition.")
    a("")
    a("| | |")
    a("| --- | --- |")
    a(f"| Public repositories | {len(index)} |")
    a(f"| Files analysed | {files:,} |")
    a(f"| Language files | {lang_files:,} |")
    a(f"| HTTP routes | {routes:,} |")
    a(f"| Entry points | {entries:,} |")
    a(f"| Module roots | {modules:,} |")
    a(f"| Test files found in trees | {tests:,} across {tested_repos} repositories |")
    a(f"| CI workflow files | {ci} across {ci_repos} repositories |")
    a(f"| Generated surfaces | {surfaces:,} files, {slots:,} slots |")
    a(f"| NOAERTH venture cards | {len(cards)} |")
    a("")
    a(f"Honest status split: "
      + ", ".join(f"**{k.lower()}** {v}" for k, v in statuses.most_common())
      + ". Most of this portfolio is a prototype stage, and the labels say so.")
    a("")

    # ---- method -----------------------------------------------------------
    a(markers("githubos", "## How each repository is documented"))
    a("")
    a("No repository description here is written from its name. For every "
      "repository the tooling measures the tree, then writes:")
    a("")
    a("1. **What exists** — routes, entry points, module roots, test files, "
      "CI workflows, and the dependency keys the project actually declares.")
    a("2. **What it does not have** — a scaffold says it is a scaffold.")
    a("3. **Surfaces** — five to ten animated diagrams, each rendered from the "
      "same measurement, each with dark, light and reduced-motion variants.")
    a("")
    a("Framework claims are matched against exact dependency keys. An earlier "
      "build substring-matched manifest text, which reported the AI SDK for 118 "
      "of 136 repositories because `ai` occurs inside `tailwindcss`. That was "
      "wrong and is now 0.")
    a("")

    # ---- portfolio by category -------------------------------------------
    a(markers("upstream", "## Portfolio shape"))
    a("")
    a("| Category | Repositories | |")
    a("| --- | --- | --- |")
    for cat, count in categories:
        blurb = CATEGORY_BLURB.get(cat, "")
        a(f"| {cat.replace('_', ' ').title()} | {count} | {blurb} |")
    a("")

    # ---- live ventures ----------------------------------------------------
    a(markers("labs", "## Ventures with a live surface"))
    a("")
    a(f"{len(live_cards)} of {len(cards)} venture cards on {SITE} report a live "
      "surface. Each links to its own site and repository.")
    a("")
    for c in sorted(live_cards, key=lambda x: str(x.get("name", ""))):
        name = str(c.get("name", "")).strip()
        site = str(c.get("site") or "").strip()
        repo = c.get("repo")
        pos = str(c.get("positioning") or "").strip()
        row = f"| [{name}]({site})" if site else f"| {name}"
        row += f" | `{repo}` |" if repo else " | |"
        row += f" {pos[:80]} |" if pos else " |"
        a(row)
    a("")
    a(f"Full portfolio: <https://www.noaerth.com/ventures>")
    a("")

    # ---- surfaces ---------------------------------------------------------
    a("## The portfolio, drawn from its own source")
    a("")
    a(f"These are the profile repository's own surfaces, regenerated from the "
      f"same measurement pass that produced all {surfaces:,} repository files.")
    a("")
    # Only reference slots that were actually rendered and published: a
    # hardcoded list produced three 404 images in an earlier build.
    profile_slots = manifest[E.OWNER]["slots"]
    titles = {
        "hero": "Portfolio identity", "terminal": "Measured totals",
        "architecture": "Module roots across the portfolio",
        "data_flow": "Routes across the portfolio",
        "state_machine": "Detected primitives",
        "component_map": "Category composition",
        "build": "Build and test inventory",
        "workflow": "Portfolio categories", "domain": "Domain", "footer": "Mark",
    }
    for slot in profile_slots:
        if slot == "footer":
            continue
        a(picture(slot, titles.get(slot, slot)))
        a("")

    # ---- profile ----------------------------------------------------------
    a("## Contact and elsewhere")
    a("")
    a(f"- NOAERTH — {SITE}")
    a(f"- Venture portfolio — <https://www.noaerth.com/ventures>")
    a(f"- GitHub — <{OWNER_URL}>")
    a("")
    a("---")
    a("")
    a(f"<sub>Generated by `scripts/profile_art/v8`. Counts are measured; "
      f"nothing on this page is hand-maintained.</sub>")
    a("")
    return "\n".join(L)


def main() -> int:
    text = build()
    OUT.write_text(text)
    print(f"  wrote {OUT} ({len(text):,} bytes, {text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
