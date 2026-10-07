"""Normalise evidence for one repository into the payload the renderers read.

Every value here is traceable to a concrete artifact: the indexer walks real
files, the card file is scraped from noaerth.com, and the baseline is the
GitHub API response captured before any write. Nothing is inferred from a
repository name alone unless it is explicitly recorded as a hypothesis.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from geometry import palette_for  # noqa: E402
from renderers import seed_of  # noqa: E402

PROFILE = pathlib.Path(__file__).resolve().parents[3]
INDEX = PROFILE / ".github-art" / "v8-index.json"
CARDS = PROFILE / ".noaerth-public-ventures.json"

OWNER = "M4G3LL4N0"

# Slots are ordered by how much evidence they need. A slot is only offered when
# the evidence for it actually exists, which is what keeps the count per repo
# honest instead of always emitting ten near-identical surfaces.
SLOT_REQUIREMENTS: list[tuple[str, tuple[str, ...]]] = [
    ("hero", ()),
    ("terminal", ("entry_points",)),
    ("architecture", ("modules",)),
    ("data_flow", ("routes",)),
    ("state_machine", ("cs_primitives",)),
    ("component_map", ("frameworks", "modules")),
    ("build", ("manifests",)),
    ("workflow", ("cs_primitives", "modules")),
    ("domain", ("cs_primitives",)),
]

MAX_SLOTS = 10
MIN_SLOTS = 5

SCAFFOLD_MARKERS = ("work in progress", "placeholder", "wip")

# Frameworks present in most repositories come from the shared Next.js scaffold,
# so naming them tells a reader nothing about the individual project. They are
# reported as context only; the distinctive stack leads.
TEST_FRAMEWORKS = {"Jest", "Vitest", "Playwright", "Mocha", "Cypress", "Testing Library"}

TEMPLATE_SIGNATURE_RATIO = 0.5


def template_signature(index: dict[str, dict]) -> set[str]:
    """Frameworks shared by more than half the portfolio = scaffold, not signal."""
    counts: dict[str, int] = {}
    for rec in index.values():
        for fw in set(rec.get("frameworks") or []):
            counts[fw] = counts.get(fw, 0) + 1
    if not index:
        return set()
    cutoff = len(index) * TEMPLATE_SIGNATURE_RATIO
    return {fw for fw, k in counts.items() if k > cutoff}


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_cards() -> dict[str, dict]:
    """Map lowercased venture name/slug -> card record from noaerth.com."""
    raw = json.loads(CARDS.read_text())
    items = raw if isinstance(raw, list) else (
        raw.get("ventures") or raw.get("items") or next(
            (v for v in raw.values() if isinstance(v, list)), []
        )
    )
    out: dict[str, dict] = {}
    for it in items:
        for key in (it.get("name"), it.get("slug")):
            if key:
                out.setdefault(str(key).lower(), it)
    return out


def load_index() -> dict[str, dict]:
    return json.loads(INDEX.read_text())["repos"]


def load_baseline(path: pathlib.Path | None = None) -> dict:
    path = path or pathlib.Path("/tmp/remote-baseline.json")
    if not path.exists():
        return {"repos": {}}
    return json.loads(path.read_text()).get("repos", {})


# Motion vocabulary keys from geometry.MOTION. A renderer is handed one of
# these strings, not prose: passing a sentence used to raise KeyError and the
# whole art set failed to render.
PRIMITIVE_MOTION = {
    "queue": "queue_advance",
    "stream": "queue_advance",
    "worker": "queue_advance",
    "tree": "tree_traverse",
    "traversal": "tree_traverse",
    "graph": "graph_resolve",
    "protocol": "packet_route",
    "router": "packet_route",
    "api": "packet_route",
    "cache": "index_probe",
    "index": "index_probe",
    "search": "index_probe",
    "scheduler": "state_change",
    "state_machine": "state_change",
    "policy": "state_change",
    "pipeline": "tessellate",
    "compiler": "layer_separate",
    "parser": "layer_separate",
    "simulator": "tessellate",
    "benchmark": "bar_sweep",
    "crypto": "grid_snap",
}

GEOMETRY_SETS = ("cube", "rosette", "arch", "ring")


def motion_for(d: dict) -> str:
    """Pick the motion key that matches the repository's measured structure."""
    ev = d["evidence"]
    for prim in ev.get("cs_primitives") or []:
        key = PRIMITIVE_MOTION.get(prim)
        if key:
            return key
    routes = ev.get("routes") or []
    if any(r.startswith("/api") for r in routes):
        return "packet_route"
    if len(routes) >= 4:
        return "tree_traverse"
    if ev.get("modules"):
        return "layer_separate"
    if ev.get("entry_points"):
        return "terminal_exec"
    if ev.get("test_count"):
        return "test_progress"
    if d.get("has_code"):
        return "grid_snap"
    return "tile_assemble"


def _dominant_language(idx: dict) -> str | None:
    langs = {k: v for k, v in (idx.get("languages") or {}).items() if v}
    if not langs:
        return None
    return max(langs.items(), key=lambda kv: kv[1])[0]


def entry_label(path: str) -> str:
    """Keep enough of the path to tell two entry points apart.

    Collapsing to the filename made "index.html" and "public/index.html" render
    identically, so sibling repositories produced byte-identical prose.
    """
    if "/" in path:
        parent, _, leaf = path.rpartition("/")
        return f"{parent.rsplit('/', 1)[-1]}/{leaf}"
    return path


def route_summary(routes: list[str], limit: int = 3) -> str:
    """Prefer the most descriptive routes over the alphabet-first ones."""
    interesting = [r for r in routes if len(r) > 1 and ":" not in r and "*" not in r]
    pool = interesting or routes
    return ", ".join(pool[:limit])


FRAMEWORK_CATEGORY = {
    "Supabase": "WEB_APPLICATION",
    "Next.js": "WEB_APPLICATION",
    "React": "WEB_APPLICATION",
    "Express": "WEB_APPLICATION",
    "Prisma": "DATA_BACKEND",
    "Supabase": "DATA_BACKEND",
    "Postgres": "DATA_BACKEND",
    "D3": "DATA_VISUALIZATION",
    "OpenAI SDK": "AI_AGENT",
    "Vercel AI SDK": "AI_AGENT",
    "Tailwind CSS": "WEB_APPLICATION",
    "Zod": "WEB_APPLICATION",
    "Vitest": "WEB_APPLICATION",
    "Jest": "WEB_APPLICATION",
    "Playwright": "WEB_APPLICATION",
}

PRIMITIVE_CATEGORY = {
    "simulator": "SIMULATION",
    "state_machine": "STATE_MACHINE",
    "graph": "GRAPH_ALGORITHM",
    "index": "DATA_STRUCTURE",
    "queue": "CONCURRENCY",
    "pipeline": "PIPELINE",
    "compiler": "COMPILER",
    "parser": "COMPILER",
    "policy": "SECURITY",
    "crypto": "SECURITY",
    "scheduler": "SCHEDULER",
    "cache": "DATA_STRUCTURE",
    "protocol": "NETWORK_PROTOCOL",
    "benchmark": "PERFORMANCE",
}


def derive_category(d: dict) -> str:
    """Technical category from measured structure, not from the marketing name."""
    for fw in d.get("frameworks") or []:
        if fw in FRAMEWORK_CATEGORY:
            return FRAMEWORK_CATEGORY[fw]
    for prim in d.get("cs_primitives") or []:
        cat = PRIMITIVE_CATEGORY.get(prim)
        if cat:
            return cat
    if d.get("has_code"):
        return "SOFTWARE"
    return "SCAFFOLD"


def build(name: str, idx: dict, card: dict | None, base: dict,
          signature: set[str] | None = None) -> dict:
    routes = list(idx.get("routes") or [])
    entries = list(idx.get("entry_points") or [])
    modules = list(idx.get("modules") or [])
    frameworks = list(idx.get("frameworks") or [])
    prims = list(idx.get("cs_primitives") or [])
    manifests = list(idx.get("manifests") or [])
    tests = idx.get("tests") or []
    ci = idx.get("ci_workflows") or []
    lang = _dominant_language(idx)

    signature = signature or set()
    distinctive = [f for f in frameworks if f not in signature and f not in TEST_FRAMEWORKS]
    test_fw = [f for f in frameworks if f in TEST_FRAMEWORKS]
    scaffold_fw = [f for f in frameworks if f in signature]

    has_code = bool(idx.get("has_code"))
    ev_files = idx.get("files") or 0
    evidence = {
        "distinctive_frameworks": distinctive,
        "test_frameworks": test_fw,
        "scaffold_frameworks": scaffold_fw,
        "routes": routes,
        "entry_points": entries,
        "modules": modules,
        "frameworks": frameworks,
        "cs_primitives": prims,
        "manifests": manifests,
        "tests": tests,
        "ci_workflows": ci,
        "language": lang,
        "files": idx.get("files") or 0,
        "test_count": idx.get("test_count") or 0,
        "shared_template_files": idx.get("shared_template_files") or 0,
    }

    # ---- slot selection: only slots backed by real evidence -----------------
    slots = [s for s, reqs in SLOT_REQUIREMENTS if all(evidence.get(r) for r in reqs)]
    slots = slots[:MAX_SLOTS - 1]

    # Every repository keeps identity and provenance even when it is a scaffold
    # with nothing else to measure, so the set never drops below five.
    if "hero" not in slots:
        slots.insert(0, "hero")
    for slot, _ in SLOT_REQUIREMENTS:
        if len(slots) >= MIN_SLOTS:
            break
        if slot not in slots:
            slots.append(slot)
    slots = slots[:MAX_SLOTS - 1]
    slots.append("footer")

    status = "PROTOTYPE" if has_code else "SCAFFOLD"
    if tests and (idx.get("test_count") or 0) > 0:
        status = "TESTED"
    if card and str(card.get("status", "")).strip().lower() == "live" and has_code:
        status = "LIVE"

    domain = (card or {}).get("category") or (card or {}).get("category_path") or ""

    d: dict = {
        "repo": name,
        "canonical_name": name,
        "project_category": "",
        "domain": domain,
        "status": status,
        "confidence": idx.get("confidence"),
        "has_code": has_code,
        "problem": (card or {}).get("positioning") or "",
        "problemSource": "noaerth.com card" if (card or {}).get("positioning") else "none",
        "homepage": (base.get("homepage") or (card or {}).get("site") or ""),
        "major_modules": modules,
        "cs_primitives": prims,
        "entry_points": entries,
        "routes": routes,
        "frameworks": frameworks,
        "language": lang,
        "manifests": manifests,
        "pipeline_stages": [],
        "inputs": [],
        "outputs": [],
        "interfaces": entries or routes[:4],
        "domain_detail": domain,
        "evidence": evidence,
        "slots": slots,
    }

    # ---- renderer payload fields, all derived from measured structure ------
    if routes:
        d["data_flow"] = (
            f"{len(routes)} App Router endpoints including "
            f"{route_summary(routes, 4)}"
        )
        d["pipeline_stages"] = route_summary(routes, 5).split(", ") or []
    elif entries:
        d["data_flow"] = (
            f"{len(entries)} entry point(s) with no routable HTTP surface: "
            f"{', '.join(entries[:3])}"
        )
        d["pipeline_stages"] = entries[:5]
    elif has_code:
        d["data_flow"] = (
            f"no HTTP routes; {len(modules)} module(s) "
            f"({', '.join(modules[:3]) or 'flat'}), {len(frameworks)} declared framework(s), "
            f"{ev_files} file(s), {lang or 'mixed'} source")
        d["pipeline_stages"] = modules[:5] or frameworks[:3]
    elif not has_code:
        d["data_flow"] = (
            f"no executable surface: {ev_files} committed file(s), "
            f"{len(idx.get('languages') or {})} language(s), "
            f"no routes and no entry points")
        d["pipeline_stages"] = []
    else:
        d["data_flow"] = (
            f"no HTTP routes; {len(modules)} module(s) "
            f"({', '.join(modules[:3]) or 'flat'}) and {len(entries)} entry point(s) "
            f"over {ev_files} file(s)")
        d["pipeline_stages"] = modules[:5]

    if modules:
        d["architecture"] = f"{len(modules)} top-level module boundaries: {', '.join(modules[:5])}"
        d["workflow_steps"] = modules[:5]
    elif frameworks:
        d["architecture"] = f"{len(frameworks)} declared frameworks, no module tree detected"
        d["workflow_steps"] = frameworks[:4]
    else:
        d["architecture"] = "single-package repository"
        d["workflow_steps"] = []

    if entries:
        d["terminal_lines"] = [entry_label(e) for e in entries[:4]]
        d["terminal_caption"] = f"{len(entries)} entry point(s) detected in source"
    else:
        # The fallback must reflect the real layout: reporting "flat" for a
        # repository that has three module roots is simply wrong.
        layout = (f"module roots: {', '.join(modules[:3])}" if modules
                  else f"flat layout, {ev_files} file(s)")
        d["terminal_lines"] = manifests[:3] or [
            f"no entry point; {layout}; {lang or 'no'} source"]
        d["terminal_caption"] = "no CLI or main entry point detected"

    if prims:
        d["state_model"] = ", ".join(prims[:4])
        d["state_model_note"] = f"{len(prims)} computer-science primitive(s) matched in source"
    else:
        d["state_model"] = "no distinctive algorithmic primitive detected"
        d["state_model_note"] = "structure is declarative/config; no primitive matcher hit"

    d["interfaces"] = entries[:3] or routes[:4] or manifests[:2]
    d["domain"] = domain
    # control_flow must carry repository-specific tokens, otherwise every repo
    # with the same shape produces the same sentence and the portfolio reads as
    # one template applied 136 times.
    if entries and routes:
        d["control_flow"] = (
            f"{entries[0]} boots {len(modules)} module(s) "
            f"({', '.join(modules[:2]) or 'flat'}) and serves {len(routes)} route(s) "
            f"beginning {route_summary(routes, 2)}"
        )
    elif routes:
        d["control_flow"] = (
            f"{len(routes)} route(s) served across {len(modules)} module(s): "
            f"{route_summary(routes, 3)}"
        )
    elif entries:
        d["control_flow"] = (
            f"{len(entries)} entry point(s) with no HTTP layer: "
            f"{', '.join(e.rsplit('/', 1)[-1] for e in entries[:3])}"
        )
    elif modules:
        d["control_flow"] = f"library surface across {', '.join(modules[:4])}"
    else:
        d["control_flow"] = "no executable control flow detected in this repository"

    d["testing"] = {
        "present": bool(tests),
        "count": idx.get("test_count") or 0,
        "note": "counted from the repository tree, not executed",
    }
    d["release"] = {
        "ci": len(ci),
        "commits": str((idx.get("git") or {}).get("commits", "?")),
        "tags": (idx.get("git") or {}).get("tags", 0),
    }
    d["geometry_set"] = GEOMETRY_SETS[seed_of(name, "geometry") % len(GEOMETRY_SETS)]
    d["animation_story_1"] = motion_for(d)
    d["animation_story_note"] = (
        f"{len(routes)} routes resolve as a navigable surface" if routes else (
            f"{len(modules)} modules resolve as a layered surface" if modules
            else "identity surface; no executable structure detected"
        )
    )
    # The visual metaphor has to name what is actually drawn, otherwise every
    # repository reports the same sentence and the portfolio reads as one
    # template applied 136 times.
    tokens: list[str] = []
    if routes:
        tokens.append("routes " + route_summary(routes, 3))
    if modules:
        tokens.append("modules " + ", ".join(modules[:3]))
    if prims:
        tokens.append("primitives " + ", ".join(prims[:3]))
    if not tokens:
        tokens.append(f"{ev_files} committed file(s), no runtime surface")
    d["primary_visual_metaphor"] = (
        f"{d['animation_story_1']} over " + "; ".join(tokens))
    d["audience"] = "developer" if has_code else "visitor"
    d["website_positioning"] = (card or {}).get("positioning") or ""
    d["public_positioning"] = (card or {}).get("positioning") or ""
    d["next_milestone"] = (card or {}).get("next_milestone") or ""
    d["card_status"] = (card or {}).get("status") or ""
    d["card_site"] = (card or {}).get("site") or ""
    d["card_slug"] = (card or {}).get("slug") or ""
    d["slug"] = _slugify(name)

    # Colour and category are resolved last: the palette must follow the
    # technical category that the measured structure produced, not the name.
    d["project_category"] = derive_category(d)
    d["palette"] = palette_for(d["project_category"], seed_of(name, "category"))
    d["card_category"] = domain
    # Resolved only now: most repositories have no noaerth.com card, and a
    # shared "Uncategorised" fallback made this field identical portfolio-wide.
    d["domain"] = domain or d["project_category"].replace("_", " ").title()

    return d
