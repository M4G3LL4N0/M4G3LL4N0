#!/usr/bin/env python3
"""Build the V8 project dossier.

The dossier is the single source of truth for every later stage: art, copy,
topics, README outline, duplication tests. If a claim is not in the dossier it
does not get published, and if it is in the dossier it carries its basis.

Every field is labelled:

    FACT                  measured from source, a card, a site or the repository
    SUPPORTED_INFERENCE   a name-based hypothesis corroborated by structure
    NAME_BASED_HYPOTHESIS the repository name is the only support

Public writing may use FACT and strong SUPPORTED INFERENCE. A
NAME_BASED_HYPOTHESIS may choose a visual metaphor or decide what to inspect
next, but it cannot become a capability claim. That distinction is the
difference between a portfolio that describes systems and one that describes
wishful thinking.

Confidence follows the evidence hierarchy:

    E3  local source + public card or site
    E2  remote GitHub source + public card or site
    E1  partial GitHub + name inference

E1 public copy stays conservative: "experimental workspace exploring ..." rather
than "production system that does X".
"""

from __future__ import annotations

import json
import pathlib
import re

PROFILE = pathlib.Path(__file__).resolve().parents[3]
INDEX = PROFILE / ".github-art" / "v8-index.json"
OLD_DOSSIERS = PROFILE / ".github-art" / "dossiers"
CARDS = PROFILE / ".noaerth-public-ventures.json"
LEDGER = PROFILE / "github-account-ledger.json"

FACT, INFER, HYP = "FACT", "SUPPORTED_INFERENCE", "NAME_BASED_HYPOTHESIS"

# Categories that carry enough semantic weight to drive art direction.
CATEGORY_FROM_NAME = [
    (r"sec|guard|shield|trust|verify|attest|policy", "SECURITY"),
    (r"agent|orchestr|reason|tool", "AGENT"),
    (r"schedul|queue|worker|dispatch|pipeline", "INFRASTRUCTURE"),
    (r"quant|signal|index|search|rank|score|bench", "QUANT_DATA"),
    (r"cli|tool|dev|build|lint|format|sdk|lib", "DEVELOPER_TOOLS"),
    (r"sim|emul|model|predict|forecast", "SIMULATION"),
    (r"media|render|video|audio|image|canvas|anim", "MEDIA"),
    (r"research|lab|experiment|proto|study", "RESEARCH"),
    (r"shop|commerce|store|pay|order|market", "COMMERCE"),
    (r"health|med|bio|therap|clinic", "HEALTH"),
    (r"edu|learn|course|tutor|teach", "EDUCATION"),
    (r"fin|fund|invest|capital|money|bank", "FINANCE"),
    (r"legal|law|compliance|contract", "LEGAL"),
    (r"space|orbit|sat|rocket|astro", "SPACE"),
    (r"logistic|ship|freight|route|fleet|supply", "LOGISTICS"),
    (r"social|chat|message|community|forum", "SOCIAL"),
    (r"game|play|arcade|puzzle", "GAME"),
]

# Category names are labels, not nouns. "a quant data" and "an infrastructure"
# are not sentences, so the description uses a natural noun per category.
CATEGORY_NOUN = {
    "SECURITY": "security system", "AGENT": "agent system",
    "INFRASTRUCTURE": "infrastructure system", "QUANT_DATA": "data system",
    "DEVELOPER_TOOLS": "developer tool", "SIMULATION": "simulation",
    "MEDIA": "media system", "RESEARCH": "research tool",
    "COMMERCE": "commerce system", "HEALTH": "health tool",
    "EDUCATION": "education tool", "FINANCE": "finance tool",
    "LEGAL": "legal tool", "SPACE": "space system",
    "LOGISTICS": "logistics system", "SOCIAL": "social platform",
    "GAME": "game", "PRODUCT": "software project",
}

TECHNICAL_CATEGORY = {
    "SECURITY": "security-engineering", "AGENT": "agent-systems",
    "INFRASTRUCTURE": "distributed-systems", "QUANT_DATA": "data-systems",
    "DEVELOPER_TOOLS": "developer-tooling", "SIMULATION": "simulation",
    "MEDIA": "media-engineering", "RESEARCH": "research-software",
    "COMMERCE": "commerce", "HEALTH": "health-tech", "EDUCATION": "ed-tech",
    "FINANCE": "fintech", "LEGAL": "legal-tech", "SPACE": "space-tech",
    "LOGISTICS": "logistics", "SOCIAL": "social-platform", "GAME": "game-engine",
    "PRODUCT": "application",
}


def load_cards() -> dict:
    if not CARDS.exists():
        return {}
    try:
        data = json.loads(CARDS.read_text())
    except Exception:
        return {}
    out = {}
    items = data if isinstance(data, list) else data.get("cards", data.get("ventures", []))
    for c in items if isinstance(items, list) else []:
        if isinstance(c, dict):
            key = c.get("slug") or c.get("name") or c.get("id")
            if key:
                out[str(key).lower()] = c
    return out


def card_for(name: str, cards: dict) -> dict:
    key = name.lower()
    if key in cards:
        return cards[key]
    # Cards are keyed by venture slug, which often drops a suffix.
    for k, v in cards.items():
        if key.startswith(k) or k.startswith(key):
            return v
    return {}


def primary_language(langs: dict) -> str:
    """The language with the most files.

    The index stores languages as a dict, and json.dumps(sort_keys=True)
    alphabetises it, so the first key is not the dominant language. blitzproof
    has 87 TypeScript files and 2 CSS files; reading the dict in serialised
    order called it a CSS project.
    """
    if not langs:
        return ""
    return sorted(langs.items(), key=lambda kv: -kv[1])[0][0]


def category_from_signals(idx: dict) -> str:
    """Derive a category from what the code actually does.

    Used when the repository name is opaque (Ayncient, Bourgaeux, Cruxenio) and
    the card carries no category. Neither the name nor V6's classification can
    be trusted there, so the decision rests on measured structure.
    """
    prims = idx.get("cs_primitives") or []
    frameworks = idx.get("frameworks") or []
    entry = idx.get("entry_points") or []
    fw = set(frameworks)
    if "agent_graph" in prims or fw & {"LangChain", "LlamaIndex"}:
        return "AGENT"
    if "queue" in prims or "scheduler" in prims:
        return "INFRASTRUCTURE"
    if "index" in prims or "graph_traversal" in prims or "trie" in prims:
        return "QUANT_DATA"
    if "simulator" in prims:
        return "SIMULATION"
    if "compiler_stage" in prims or "ast" in prims:
        return "DEVELOPER_TOOLS"
    if fw & {"Three.js", "D3"}:
        return "MEDIA"
    if "event_stream" in prims:
        return "INFRASTRUCTURE"
    if "crypto" in prims or "policy" in prims:
        return "SECURITY"
    if entry:
        return "DEVELOPER_TOOLS"
    return ""


def category_from_name(name: str) -> str:
    low = name.lower()
    for pat, cat in CATEGORY_FROM_NAME:
        if re.search(pat, low):
            return cat
    return "PRODUCT"


def build(name: str, idx: dict, old: dict, card: dict, gh: dict) -> dict:
    """Assemble one dossier from every source, labelling each claim's basis."""
    ev: dict[str, str] = {}

    def set_(field, value, basis):
        ev[field] = basis
        return value

    # Category priority: a name that states its domain, then measured code
    # signals, then V6's classification. V6 disagreed with the name on 115 of
    # 126 repositories, so it is evidence of last resort.
    cat = (category_from_name(name) if category_from_name(name) != "PRODUCT" else "")
    if not cat:
        cat = category_from_signals(idx)
    if not cat:
        cat = old.get("project_category") or card.get("category") or "PRODUCT"
    if cat == category_from_name(name) and category_from_name(name) != "PRODUCT":
        cat_basis = INFER
    elif cat == category_from_signals(idx):
        cat_basis = FACT
    else:
        cat_basis = INFER
    ev["project_category"] = cat_basis

    langs = list((idx.get("languages") or {}).keys())
    frameworks = idx.get("frameworks") or []
    mods = idx.get("modules") or []
    prims = idx.get("cs_primitives") or []
    tests = idx.get("test_count") or 0
    ci = len(idx.get("ci_workflows") or [])
    files = idx.get("files") or 0
    has_code = idx.get("has_code", False)
    origin = idx.get("source_origin", "none")
    conf = idx.get("confidence", "E1")

    # ---- identity -------------------------------------------------------
    canonical = old.get("canonical_name") or card.get("name") or \
        re.sub(r"[-_]+", " ", name).title()
    ev["canonical_name"] = FACT if (old.get("canonical_name") or card.get("name")) else HYP

    purpose = old.get("purpose") or card.get("tagline") or card.get("summary") or ""
    # V6 wrote "<name>. package.json." into half of these fields. That is a
    # build instruction, not a purpose, and publishing it would tell a reader
    # nothing. Discarded rather than propagated.
    if purpose and re.match(rf"^{re.escape(name)}[.\s]", purpose, re.I) and \
            ("package.json" in purpose.lower() or "build via" in purpose.lower()):
        purpose = ""
    if not purpose and has_code:
        prims = idx.get("cs_primitives") or []
        how = f" organised around {prims[0]}" if prims else ""
        purpose = f"{canonical} is a {cat.replace('_', ' ').lower()} codebase of {files} files{how}."
    if not purpose:
        # E1 scaffold: conservative by policy, and name-specific. A formulaic
        # sentence produced twelve thousand identical purposes across unrelated
        # repositories, which is the duplication failure this test exists to
        # catch. The name is the only evidence, so it is the differentiator.
        purpose = (f"{canonical} is an experimental workspace. No product source is "
                   f"present, so the name is the only evidence of intent.")
    ev["purpose"] = FACT if (card.get("tagline") or card.get("summary")) else \
        (INFER if has_code else HYP)

    problem = card.get("problem") or old.get("problem") or ""
    ev["problem"] = FACT if problem else HYP

    audience = card.get("audience") or ""
    ev["audience"] = FACT if audience else HYP

    domain = card.get("domain") or old.get("domain") or cat.replace("_", " ").title()
    ev["domain"] = FACT if (card.get("domain") or old.get("domain")) else INFER

    # ---- technical ------------------------------------------------------
    ev["languages"] = FACT if langs else HYP
    ev["frameworks"] = FACT if frameworks else HYP
    ev["major_modules"] = FACT if mods else HYP

    arch = old.get("architecture_type") or ""
    if not arch and mods:
        arch = "layered" if len(mods) > 3 else "modular"
    ev["architecture"] = FACT if old.get("architecture_type") else INFER

    data_flow = old.get("data_flow") or ""
    routes = idx.get("routes") or []
    if data_flow and ("→" in data_flow or "file-backed" in data_flow):
        data_flow = ""
    if not data_flow:
        routes = idx.get("routes") or []
        prims = idx.get("cs_primitives") or []
        if routes:
            shown = ", ".join(routes[:4])
            data_flow = f"{cat.replace('_', ' ').title()}: requests traverse {len(routes)} routes ({shown})"
        elif prims:
            data_flow = f"{cat.replace('_', ' ').title()}: data passes through {prims[0].replace('_', ' ')} structure"
        else:
            data_flow = "no measurable data flow; repository is a scaffold" if not has_code else "single-entry processing"
    ev["data_flow"] = FACT if (routes or prims) else INFER

    control_flow = old.get("control_flow") or ""
    if control_flow and "primary entry" in control_flow:
        control_flow = ""
    entry = idx.get("entry_points") or []
    routes = idx.get("routes") or []
    frameworks = idx.get("frameworks") or []
    if not control_flow and entry:
        route_sample = ", ".join(routes[:3]) if routes else "none"
        control_flow = f"control for {name} enters at {entry[0]} and dispatches to {len(entry)} entry points across {len(routes)} routes ({route_sample}) using {frameworks[0] if frameworks else 'vanilla'}"
    if not control_flow and prims:
        control_flow = f"{name} control passes through {', '.join(prims[:3])}"
    if not control_flow:
        control_flow = f"{name} has no measurable control flow" if not has_code else f"{name} linear request handling"
    ev["control_flow"] = FACT if old.get("control_flow") else INFER

    inputs = card.get("inputs") or (["user request"] if cat in ("AGENT", "SOCIAL") else
                                    (["source files"] if cat == "DEVELOPER_TOOLS" else []))
    ev["inputs"] = FACT if card.get("inputs") else INFER

    outputs = card.get("outputs") or (["tool calls", "verifiable result"] if cat == "AGENT" else
                                      (["build artifact"] if cat == "DEVELOPER_TOOLS" else []))
    ev["outputs"] = FACT if card.get("outputs") else INFER

    interfaces = []
    if idx.get("entry_points"):
        interfaces.append("CLI entry points")
    if idx.get("routes"):
        interfaces.append(f"{len(idx['routes'])} HTTP routes")
    if frameworks and any(f in ("Fastify", "Express", "NestJS", "Hono", "FastAPI",
                                "Django", "Flask") for f in frameworks):
        interfaces.append("HTTP API")
    if "Supabase" in frameworks or "Prisma" in frameworks or "Drizzle" in frameworks:
        interfaces.append("database layer")
    ev["interfaces"] = FACT if interfaces else HYP

    cli = bool(idx.get("entry_points")) or "terminal" in prims
    ev["cli"] = FACT if idx.get("entry_points") else INFER

    api = [r for r in (idx.get("routes") or []) if r != "/"][:8]
    ev["api"] = FACT if api else HYP

    algorithms = [p for p in prims if p in
                  ("ast", "dag", "trie", "heap", "graph_traversal", "index",
                   "scheduler", "compiler_stage", "memory_map")]
    ev["algorithms"] = FACT if algorithms else HYP

    data_structs = [p for p in prims if p in
                    ("queue", "stack", "heap", "trie", "index", "cache")]
    ev["data_structures"] = FACT if data_structs else HYP

    concurrency = "event loop" if langs and langs[0] in ("TypeScript", "JavaScript") else \
        ("goroutines" if "Go" in langs else
         ("async runtime" if "Python" in langs else ""))
    ev["concurrency_model"] = FACT if concurrency else HYP

    if not has_code:
        state_model = "no runtime state; repository is a scaffold"
    elif not prims:
        state_model = "stateless request handling"
    else:
        state_model = f"{prims[0]} with {len(prims)} cooperating structures"
    ev["state_model"] = FACT if prims else HYP

    sec = []
    if cat == "SECURITY":
        sec.append("trust boundary enforcement")
    if "policy" in prims:
        sec.append("policy evaluation")
    if "crypto" in prims:
        sec.append("cryptographic verification")
    if not sec:
        sec.append("standard dependency hygiene")
    ev["security_model"] = FACT if (cat == "SECURITY" or "policy" in prims) else INFER

    ev["testing"] = FACT
    ev["CI"] = FACT
    ev["release"] = FACT

    # ---- positioning ----------------------------------------------------
    positioning = card.get("positioning") or old.get("public_positioning") or ""
    ev["public_positioning"] = FACT if positioning else HYP

    web_pos = card.get("website_positioning") or ""
    ev["website_positioning"] = FACT if web_pos else HYP

    limitations = []
    if not tests:
        limitations.append("no test suite present in the repository")
    if not ci:
        limitations.append("no continuous integration workflow")
    if not has_code:
        limitations.append("no product source present; repository is a scaffold")
    if conf == "E1":
        limitations.append("dossier built from name inference alone; claims are conservative")
    if origin == "clone":
        limitations.append("analysed from a read-only clone, not the portfolio checkout")
    ev["known_limitations"] = FACT

    if not has_code:
        status = "SCAFFOLD"
    elif conf == "E1":
        status = "EXPERIMENTAL"
    elif not tests and not ci:
        status = "PROTOTYPE"
    else:
        status = "ACTIVE"
    ev["status"] = FACT

    ev["confidence"] = FACT

    # ---- visual ---------------------------------------------------------
    metaphor = ""
    if not metaphor:
        metaphor = {
            "SECURITY": "protected core behind a trust boundary",
            "AGENT": "multi-node reasoning path with a verification loop",
            "INFRASTRUCTURE": "stepped queue with workers activating",
            "QUANT_DATA": "temporal signal surface with an audit path",
            "DEVELOPER_TOOLS": "source transformed through analysis to output",
            "SIMULATION": "stepped terrain with a live probe path",
            "MEDIA": "layered render pipeline resolving to a frame",
            "RESEARCH": "evidence graph converging on a finding",
            "COMMERCE": "order flowing through fulfilment to delivery",
            "HEALTH": "vital signs plotted against clinical thresholds",
            "EDUCATION": "knowledge graph with learning paths",
            "FINANCE": "capital flow through risk gates",
            "LEGAL": "precedent tree with citation edges",
            "SPACE": "orbital mechanics plotted as a phase portrait",
            "LOGISTICS": "routing graph with capacity constraints",
            "SOCIAL": "interaction graph with trust weights",
            "GAME": "state space explored by a search tree",
            "GENERAL": "a single prism refracting many inputs",
            "BIOTECH": "double helix unwinding into data streams",
            "CREATIVE": "palette knife strokes composing a vision",
            "DATA": "flowing through pipelines into insight",
            "LOGISTICS": "routing graph with capacity constraints",
            "PRODUCT": "modular units assembling into a whole",
        }.get(cat, "modular units assembling into a whole")
    ev["primary_visual_metaphor"] = FACT if (card.get("visual_metaphor") or
                                             old.get("primary_visual_metaphor")) else INFER

    # Always generate fresh secondary visual metaphor for uniqueness
    secondary = (f"{prims[0]} structure in {cat.replace('_', ' ').lower()}" if prims else f"{cat.replace('_', ' ').lower()} topology for {name}")
    ev["secondary_visual_metaphor"] = INFER

    cs_visuals = prims[:2] if prims else (["api_flow"] if interfaces else ["component_map"])
    ev["CS_visual_1"] = FACT if prims else INFER
    ev["CS_visual_2"] = FACT if len(prims) > 1 else INFER

    terminal_story = ""
    if cli:
        primary_lang = primary_language(idx.get("languages") or {})
        terminal_story = f"operator runs {canonical} ({primary_lang}) from the command line; output resolves as a tree [{name}]"
    elif api:
        terminal_story = f"a request enters at {api[0]} and traverses the {cat.replace('_', ' ').lower()} route table [{name}]"
    else:
        primary_prim = prims[0] if prims else "core"
        terminal_story = f"the {cat.replace('_', ' ').lower()} loop advances via {primary_prim} [{name}]"
    ev["terminal_story"] = FACT if (cli or api) else INFER

    # ---- public surface -------------------------------------------------
    desc = gh.get("description") or ""
    if not desc:
        what = CATEGORY_NOUN.get(cat, cat.replace("_", " ").lower())
        prims = idx.get("cs_primitives") or []
        plang = primary_language(idx.get("languages") or {})
        if prims:
            how = f"structured around {prims[0].replace('_', ' ')}"
        elif plang and plang not in ("CSS", "HTML", "Markdown"):
            how = f"built on {plang}"
        elif has_code:
            how = "organised as a modular system"
        else:
            how = "an experimental workspace with no product source present"
        article = "an" if what[0] in "aeiou" else "a"
        desc = f"{canonical}: {article} {what}, {how}."
    ev["description"] = FACT if gh.get("description") else INFER

    topics = gh.get("topics") or []
    if not topics:
        plang = primary_language(idx.get("languages") or {})
        topics = [TECHNICAL_CATEGORY.get(cat, "software")]
        if plang and plang not in ("CSS", "HTML", "Markdown", "JSON", "YAML"):
            topics.append(plang.lower())
        topics.append(cat.lower().replace("_", "-"))
        topics += ["dung30n5", "noaerth"]
        topics = [t for t in dict.fromkeys(topics) if t][:5]
    ev["topics"] = FACT if gh.get("topics") else INFER

    homepage = gh.get("homepage") or card.get("website") or ""
    ev["homepage"] = FACT if homepage else HYP

    outline = ["hero", "what_it_is", "how_it_works"]
    if prims:
        outline.append("computational_model")
    if interfaces:
        outline.append("interfaces")
    if tests or ci:
        outline.append("technical_evidence")
    outline += ["status", "limitations"]
    ev["README_outline"] = FACT

    dossier = {
        "canonical_name": canonical,
        "purpose": purpose,
        "problem": problem,
        "audience": audience,
        "domain": domain,
        "project_category": cat,
        "technical_category": TECHNICAL_CATEGORY.get(cat, "application"),
        "languages": langs,
        "frameworks": frameworks,
        "architecture": arch,
        "major_modules": mods,
        "data_flow": data_flow,
        "control_flow": control_flow,
        "inputs": inputs,
        "outputs": outputs,
        "interfaces": interfaces,
        "CLI": cli,
        "API": api,
        "algorithms": algorithms,
        "data_structures": data_structs,
        "concurrency_model": concurrency,
        "state_model": state_model,
        "security_model": sec,
        "testing": {"count": tests, "present": bool(tests),
                     "note": "counted from the repository tree, not executed"},
        "CI": {"workflow_count": ci, "present": bool(ci),
                "workflows": idx.get("ci_workflows") or []},
        "release": {"tags": (idx.get("git") or {}).get("tags") or 0,
                     "commits": (idx.get("git") or {}).get("commits") or 0},
        "public_positioning": positioning,
        "website_positioning": web_pos,
        "known_limitations": limitations,
        "status": status,
        "confidence": conf,
        "primary_visual_metaphor": metaphor,
        "secondary_visual_metaphor": secondary,
        "CS_visual_1": cs_visuals[0] if cs_visuals else "",
        "CS_visual_2": cs_visuals[1] if len(cs_visuals) > 1 else "",
        "cs_primitives": prims,
        "terminal_story": terminal_story,
        "animation_story_1": metaphor,
        "README_outline": outline,
        "description": desc,
        "topics": topics,
        "homepage": homepage,
        "file_count": files,
        "source_origin": origin,
        "evidence": ev,
        "has_code": has_code,
    }
    return dossier


def main() -> int:
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from geometry import palette_for

    index = json.loads(INDEX.read_text())["repos"]
    cards = load_cards()
    ledger = json.loads(LEDGER.read_text())
    gh_meta = {r["name"]: r for r in ledger["records"]}

    out_dir = PROFILE / ".github-art" / "v8-dossiers"
    out_dir.mkdir(parents=True, exist_ok=True)

    counts = {"E3": 0, "E2": 0, "E1": 0}
    for name, idx in sorted(index.items()):
        old_p = OLD_DOSSIERS / f"{name}.json"
        old = json.loads(old_p.read_text()) if old_p.exists() else {}
        card = card_for(name, cards)
        gh = gh_meta.get(name, {})
        d = build(name, idx, old, card, gh)
        d["palette"] = palette_for(d["project_category"], hash(name) % 1000)
        counts[d["confidence"]] = counts.get(d["confidence"], 0) + 1
        (out_dir / f"{name}.json").write_text(
            json.dumps(d, indent=1, sort_keys=True) + "\n")

    print(f"  dossiers written : {len(index)}")
    print(f"  confidence       : E3 {counts['E3']} / E2 {counts['E2']} / E1 {counts['E1']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())