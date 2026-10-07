"""Compose one GitHub About description per repository from measured evidence.

Rules this file enforces, because the previous generation broke all of them:
  * no Markdown -- GitHub renders About as plain text, so "**bold**" and
    "[links](x)" ship as literal characters;
  * at most 350 characters, the GitHub About limit;
  * every number in the sentence is measured from the repository tree;
  * a repository with no executable surface says so instead of inventing one;
  * no two repositories get the same sentence.

Nothing here is invented: a claim can only mention a route, module, entry
point, framework, test file or CI workflow that exists in the index.
"""

from __future__ import annotations

import re

MAX_LEN = 350

# Words GitHub About renders literally, so they must never be emitted.
MARKDOWN_RE = re.compile(r"\*\*|__|!?\[|\]\(|\[[^\]]+\]\(https?://|`|<[^>]+>|\|.*\|")

SCAFFOLD_TEXT = (
    "Placeholder repository. No executable code, routes or entry points are "
    "committed yet - see the contents for what exists."
)


def _plural(n: int, singular: str, plural: str | None = None) -> str:
    return f"{n} {singular if n == 1 else (plural or singular + 's')}"


def _stack(d: dict, limit: int = 3) -> str:
    """Lead with what distinguishes this repository, not the shared scaffold."""
    ev = d["evidence"]
    distinctive = ev.get("distinctive_frameworks") or []
    if distinctive:
        return ", ".join(distinctive[:limit])
    if ev.get("language"):
        lang = ev["language"]
        base = ev.get("scaffold_frameworks") or []
        return f"{lang} on " + base[0] if base else lang
    base = ev.get("scaffold_frameworks") or []
    return base[0] if base else ""


def _clean(text: str) -> str:
    text = MARKDOWN_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def _sentence(*parts: str) -> str:
    out: list[str] = []
    for p in parts:
        p = _clean(p or "").strip()
        if p:
            out.append(p if p.endswith((".", "!", "?")) else p + ".")
    return " ".join(out)


def _fit(text: str) -> str:
    """Trim at a word boundary so the description always fits the About limit."""
    text = _clean(text)
    if len(text) <= MAX_LEN:
        return text
    cut = text[:MAX_LEN - 1]
    if " " in cut:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:-") + "."


def _route_clause(d: dict) -> str:
    routes = d["evidence"]["routes"]
    named = [r for r in routes if len(r) > 1 and ":" not in r and "*" not in r]
    pool = named or routes
    if not pool:
        return ""
    if len(pool) == 1:
        return f"one route ({pool[0]})"
    sample = ", ".join(pool[:3])
    return f"{len(routes)} routes ({sample})"


def _entry_clause(d: dict) -> str:
    entries = d["evidence"]["entry_points"]
    if not entries:
        return ""
    leaf = sorted({e.rsplit("/", 1)[-1] for e in entries})
    shown = ", ".join(leaf[:3])
    return f"{_plural(len(entries), 'entry point')} ({shown})"


def _verify_clause(d: dict) -> str:
    ev = d["evidence"]
    bits = []
    if ev["test_count"]:
        bits.append(f"{_plural(ev['test_count'], 'test file')}")
    runners = ev.get("test_frameworks") or []
    if runners:
        bits.append("via " + ", ".join(runners[:2]))
    if ev["ci_workflows"]:
        bits.append(f"{_plural(len(ev['ci_workflows']), 'CI workflow')}")
    return ", ".join(bits)


PROFILE_REPO = "M4G3LL4N0"

PROFILE_TEXT = (
    "Profile repository for DUNG30N5, founder of noaerth.com. Generated "
    "artwork and evidence for 136 public repositories: source-derived route, "
    "module and test maps with reduced-motion variants."
)

VENDORED_TEXT = (
    "Committed dependency tree, not a project. Vendored npm packages are "
    "tracked here by accident; the real work lives in the sibling repositories."
)


def describe(d: dict) -> str:
    """Return the GitHub About description for one evidence payload."""
    ev = d["evidence"]
    name = d["repo"]

    if name == PROFILE_REPO:
        return _fit(PROFILE_TEXT)
    if name == "node_modules":
        return _fit(VENDORED_TEXT)
    stack = _stack(d)

    if not ev["files"] and not ev["entry_points"]:
        return _fit(SCAFFOLD_TEXT)

    if not d["has_code"]:
        # Real repository, but nothing executable in it.
        return _fit(_sentence(
            f"Documentation and placeholder repository for {name}",
            f"{ev['files']} file(s) committed, no executable code detected",
        ))

    # What it is, from the Noaerth card when one exists, else from structure.
    subject = _clean(d.get("public_positioning") or "")
    if subject:
        subject = subject[0].upper() + subject[1:]
        if not subject.endswith("."):
            subject += "."
    else:
        subject = f"{name} is a {d['project_category'].replace('_', ' ').lower()} project."

    # What exists, measured.
    measured = [c for c in (_route_clause(d), _entry_clause(d)) if c]
    if not measured and ev["modules"]:
        shown = ", ".join(ev["modules"][:3])
        measured.append(f"{_plural(len(ev['modules']), 'module')} ({shown})")
    structure = "; ".join(measured) if measured else "no HTTP or CLI surface yet"

    impl = _sentence(
        f"Built in {stack}" if stack else "",
        structure[0].upper() + structure[1:] if structure else "",
    )

    verify = _verify_clause(d)
    status = d["status"]
    if status == "LIVE" and d.get("card_site"):
        tail = "Live at " + re.sub(r"^https?://|/+$", "", d["card_site"]) + "."
    elif status == "LIVE":
        tail = "Live."
    elif verify:
        tail = f"{status}: {verify}."
    else:
        tail = f"{status}. No test suite committed."

    return _fit(_sentence(subject, impl, tail))


def topics_for(d: dict, limit: int = 12) -> list[str]:
    """Topics derived from measured structure, with the house tags last."""
    ev = d["evidence"]
    out: list[str] = []

    def add(t: str) -> None:
        # GitHub topics must start with a lowercase letter or number, be at
        # most 50 characters, and may contain hyphens only -- no dots, spaces
        # or underscores. "next.js" or "next_js" makes the whole request fail
        # with HTTP 422, so the set is sanitised before it is sent.
        t = re.sub(r"[^a-z0-9-]+", "-", str(t).strip().lower()).strip("-")
        t = re.sub(r"-{2,}", "-", t)
        if t and t not in out and len(t) <= 50:
            out.append(t)

    add(d["project_category"].replace("_", "-").lower())
    for fw in ev["frameworks"][:4]:
        add(fw)
    for prim in ev["cs_primitives"][:3]:
        add(prim)
    for mod in ev["modules"][:2]:
        add(mod.split("/")[-1])
    if ev["language"]:
        add(ev["language"].lower())
    add(d["status"].lower())
    for house in ("dung30n5", "noaerth"):
        add(house)

    return out[:limit]
