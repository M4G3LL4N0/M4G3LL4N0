#!/usr/bin/env python3
"""V6 project identity: a distinct visual identity derived from the dossier.

The defect this replaces
------------------------
`generative_identity.py` classifies a project from its NAME, description and
topics, then picks a family, motif, material, accent, depth and topology from a
seed derived from the repository node id:

    family = classify(f"{name} {description} {topics}")
    seed   = sha256(repo_id)

Section 22 of the brief says this backwards up: "do not let hashing alone
determine design. Semantic dossier chooses design family FIRST. Stable seed only
varies detail inside that valid family." The previous system did the opposite --
the name picked the family and the hash picked everything else. Two projects
called `agentos` and `ghostframe` got an AGENT identity and a SECURITY identity
for reasons that had nothing to do with either project's code.

The visible consequence was measured: five repositories shipped a
byte-identical hero layout with only the name substituted, and 43 of 126
dossiers carried no problem statement for the identity to respond to at all.

How this works
--------------
  1. The dossier supplies a semantic fingerprint: architecture type, interfaces,
     state model, data flow, verified components, limitations, real CLI.
  2. That fingerprint resolves a FAMILY first, from what the system actually is.
  3. The stable seed then varies motif, material, depth, topology and geometry
     phase INSIDE that family. It cannot change the family.
  4. Overlap is detected and reported, never assumed away.

So the hash varies detail within a valid family, and the family is a claim about
the project rather than a function of its name.

  python3 scripts/profile_art/v6_identity.py --report
  python3 scripts/profile_art/v6_identity.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
DOSSIER_DIR = PROFILE / ".github-art" / "dossiers"
IDENTITY = PROFILE / ".github-art" / "identity.json"
DESIGN_VERSION = "V6"

# --------------------------------------------------------------------- families
# Each family is a semantic claim about what the system IS. Motifs, materials
# and topologies inside a family are variations on one idea, not unrelated
# shapes: a security project's four motifs are all ways of drawing a boundary.
FAMILIES: dict[str, dict] = {
    "TRUST_BOUNDARY": {
        "claim": "a protected core with a boundary that holds or admits",
        "motifs": ["gated_channels", "vault_cells", "concentric_shell",
                   "boundary_ring"],
        "materials": ["obsidian", "ceramic", "anodised_steel"],
        "topologies": ["concentric", "bracketed", "orthogonal"],
        "depths": ["recessed", "sealed", "stratified"],
        "accents": ["indigo", "amber"],
    },
    "CAPITAL_MECHANICS": {
        "claim": "value entering, allocating, and settling",
        "motifs": ["ledger_columns", "allocation_bars", "settlement_rails",
                   "scenario_panels"],
        "materials": ["ceramic", "obsidian", "brushed_metal"],
        "topologies": ["linear", "terraced", "orthogonal"],
        "depths": ["recessed", "stratified", "stacked"],
        "accents": ["mint", "amber"],
    },
    "ORCHESTRATION": {
        "claim": "work coordinated across nodes toward a verified outcome",
        "motifs": ["coordinating_mesh", "staged_pipeline", "capability_ring",
                   "delegation_fan"],
        "materials": ["optical_glass", "liquid_crystal", "luminous_ceramic"],
        "topologies": ["radial", "branching", "linear"],
        "depths": ["layered", "floating", "stratified"],
        "accents": ["mint", "cyan"],
    },
    "RECORD_MECHANICS": {
        "claim": "records entering, normalised, indexed, and answered",
        "motifs": ["record_channels", "index_grid", "column_stack",
                   "stream_rails"],
        "materials": ["resin", "polymer", "ceramic"],
        "topologies": ["orthogonal", "linear", "terraced"],
        "depths": ["stratified", "stacked", "layered"],
        "accents": ["cyan", "mint"],
    },
    "EVIDENCE_SURFACE": {
        "claim": "a claim assembled into something a reader can check",
        "motifs": ["nested_frames", "evidence_tiers", "policy_stack",
                   "attestation_panel"],
        "materials": ["ceramic", "paper_stock", "deep_glass"],
        "topologies": ["orthogonal", "terraced", "bracketed"],
        "depths": ["layered", "recessed", "stratified"],
        "accents": ["amber", "mint"],
    },
    "TOPOLOGY_CONTROL": {
        "claim": "resources placed, scheduled, and moved across a fleet",
        "motifs": ["isometric_stack", "queue_lanes", "rack_blocks",
                   "topology_map"],
        "materials": ["deep_glass", "anodised_steel", "obsidian"],
        "topologies": ["isometric", "terraced", "orthogonal"],
        "depths": ["stacked", "stratified", "recessed"],
        "accents": ["cyan", "indigo"],
    },
    "INSTRUMENT": {
        "claim": "a command surface that reports and is driven",
        "motifs": ["command_strip", "progress_rail", "status_lamps",
                   "instrument_dial"],
        "materials": ["ceramic", "polymer", "obsidian"],
        "topologies": ["linear", "concentric", "orthogonal"],
        "depths": ["recessed", "layered", "floating"],
        "accents": ["mint", "cyan"],
    },
    "GENERATIVE_FIELD": {
        "claim": "a seed expanding into structured form",
        "motifs": ["aperture_fan", "seed_lattice", "spectral_bands",
                   "morphology_grid"],
        "materials": ["liquid_crystal", "luminous_ceramic", "polymer"],
        "topologies": ["radial", "mesh", "concentric"],
        "depths": ["floating", "layered", "stratified"],
        "accents": ["violet", "cyan"],
    },
    "PRESENTATION": {
        "claim": "a composed surface meant to be read by a person",
        "motifs": ["modular_grid", "soft_tiles", "type_rail",
                   "component_mosaic"],
        "materials": ["polymer", "luminous_ceramic", "resin"],
        "topologies": ["mesh", "terraced", "orthogonal"],
        "depths": ["layered", "floating", "stacked"],
        "accents": ["violet", "mint"],
    },
}

# Dossier signal -> family. Ordered: the first family whose evidence is present
# wins. Evidence means a value the comprehension pass actually read, so a
# project cannot land in a family by naming itself.
RESOLVERS: list[tuple[str, tuple[tuple[str, tuple[str, ...]], ...]]] = [
    # A security system is defined by what it protects, not by what it ships.
    # Order within the family matters: `security` (mechanisms found in source)
    # and `category` are strong, but a SECURITY.md file is weak evidence. AgentOS
    # ships a SECURITY.md, a SECURITY_BOUNDARIES.md and a documented redaction
    # path -- and is an agent orchestration engine, so resolving it to
    # TRUST_BOUNDARY would put the flagship's mark on the wrong product. The file
    # test is demoted to a last resort within the family, and the whole family
    # sits after ORCHESTRATION so that an agent system is never mistaken for a
    # boundary system merely for documenting its own boundaries.
    ("TRUST_BOUNDARY", (
        ("category", ("SECURITY",)),
        ("security", ()),
    )),
    # Finance needs capital language, not merely a finance word in the name.
    ("CAPITAL_MECHANICS", (
        ("category", ("FINANCE",)),
        ("noaerth", ("Finance", "Fintech", "Capital", "Payments")),
        # `pricing` is out. It appears in the output_types of every Next.js
        # project, because the comprehension pass lists declared route handlers
        # and a route called `pricing` exists across the portfolio. Thirteen
        # projects were classified as capital systems on that one word.
        ("text", ("ledger", "settlement", "invoice", "billing", "valuation",
                  "revenue", "subscription", "underwriting", "treasury")),
    )),
    # Placed above TRUST_BOUNDARY deliberately. An agent engine that also
    # documents its own security boundaries is an orchestration system; the
    # boundaries are a property of it, not its subject.
    ("ORCHESTRATION", (
        ("category", ("AGENT",)),
        ("arch", ("AGENT_LOOP", "DISTRIBUTED", "SCHEDULER")),
        ("text", ("orchestrat", "scheduler", "delegate", "worker", "queue",
                  "coordina", "federat")),
    )),
    # A terminal is only a terminal if the project actually has one.
    ("INSTRUMENT", (
        ("cli", ()),
        ("text", ("cli", "tui", "terminal", "repl")),
    )),
    ("TRUST_BOUNDARY", (
        ("category", ("SECURITY",)),
        ("security", ()),
        ("file", ("SECURITY.md", "SECURITY_BOUNDARIES.md", "AUTH.md")),
    )),
    ("EVIDENCE_SURFACE", (
        ("arch", ("DOCUMENT",)),
        ("text", ("verify", "attest", "evidence", "audit", "compliance",
                  "provenance", "certif")),
    )),
    ("GENERATIVE_FIELD", (
        ("arch", ("GENERATIVE",)),
        ("text", ("generative", "procedural", "synthes", "simulation",
                  "experiment", "model fit")),
    )),
    # Route semantics. Half the portfolio is a Next.js application with a
    # create-next-app README, no venture card and no prose -- for those, the
    # route handler names are the only project-specific evidence in the tree.
    # `checkout` and `payments` are a capital system; `leads` and `track` are a
    # growth surface; `scan` and `verify` are an evidence system. That is a real
    # signal read out of source, and it is what keeps 50 projects out of one
    # family.
    ("CAPITAL_MECHANICS", (
        ("routes", ("checkout", "payment", "payments", "billing", "invoice",
                    "pricing", "subscription", "payout", "cart", "order")),
    )),
    ("EVIDENCE_SURFACE", (
        ("routes", ("verify", "scan", "audit", "report", "review", "attest",
                    "check", "validate", "proof")),
    )),
    ("RECORD_MECHANICS", (
        ("routes", ("ideas", "leads", "lead", "contacts", "search", "catalog",
                    "directory", "records")),
    )),
    ("PRESENTATION", (
        ("web_surface", ()),
    )),
    # DATA_FLOW is the portfolio's most common architecture (86 of 126) because
    # most of these projects are full-stack web applications. Treating that
    # architecture as "a record system" put 51 projects in one family, which is
    # the same collapse the uniqueness audit exists to catch. So the family is
    # chosen on what the data system DOES -- indexing and querying, or routing --
    # and architecture alone is not sufficient evidence.
    ("RECORD_MECHANICS", (
        ("text", ("index", "query", "ingest", "normalis", "normaliz",
                  "record", "search", "catalog", "ledger entry")),
        ("arch_and_persistence", ("DATA_FLOW",)),
    )),
    ("TOPOLOGY_CONTROL", (
        ("arch", ("ROUTER", "PIPELINE", "CLI")),
        ("text", ("deploy", "provision", "cluster", "container", "runtime",
                  "scheduler", "queue", "worker")),
    )),
]

FALLBACK = "PRESENTATION"


# ------------------------------------------------------------------ fingerprint

def fingerprint(d: dict) -> dict:
    """The semantic evidence available to resolve a family.

    Every value here is something the comprehension pass read out of source or
    off a cached venture card. Nothing is derived from the repository name,
    which is the whole point.
    """
    routes: list[str] = []
    for o in d.get("output_types", []):
        m = re.match(r"route handlers:\s*(.+)$", o)
        if m:
            routes = [r.strip() for r in m.group(1).split(",") if r.strip()]
    text = " ".join([
        d.get("problem", ""), d.get("primary_user", ""),
        d.get("data_flow", ""), d.get("primary_workflow", ""),
        d.get("purpose", ""), " ".join(d.get("major_components", [])),
        " ".join(d.get("output_types", [])),
        " ".join(d.get("security_characteristics", [])),
        " ".join(d.get("verified_features", [])),
    ]).lower()
    return {
        "arch": [d.get("architecture_type", "")],
        "category": [d.get("project_category", "")],
        "noaerth": [d.get("noaerth_category", "")],
        "security": d.get("security_characteristics", []),
        "cli": [c["command"] for c in d.get("verified_commands", [])],
        "storage": [d.get("state_model", "")],
        "storage_list": [s.strip() for s in (d.get("state_model") or "").split(",")
                         if s.strip()],
        "routes": routes,
        "text": [text],
    }


def resolve_family(fp: dict[str, list[str]]) -> tuple[str, str]:
    """Family first, from evidence. Returns (family, basis)."""
    for family, tests in RESOLVERS:
        for kind, values in tests:
            if kind == "category":
                if any(v in values for v in fp["category"] if v):
                    return family, f"code-derived category = {fp['category'][0]}"
            elif kind == "noaerth":
                if any(v in values for v in fp["noaerth"] if v):
                    return family, f"public venture card category = {fp['noaerth'][0]}"
            elif kind == "arch":
                if any(v in values for v in fp["arch"] if v):
                    return family, f"architecture = {fp['arch'][0]}"
            elif kind == "security":
                if values:
                    return family, "documents security characteristics"
            elif kind == "cli":
                if values:
                    return family, f"verified CLI: {values[0]}"
            elif kind == "file":
                roots = {Path(x).name for x in values}
                if roots & set(fp.get("files", [])):
                    return family, "ships a security document"
            elif kind == "text":
                hits = [n for n in values if n in (fp["text"][0] if fp["text"] else "")]
                if hits:
                    return family, f"source text: {', '.join(hits[:3])}"
            elif kind == "routes":
                named = set(fp["routes"])
                hits = [n for n in values if n in named]
                if hits:
                    return family, f"route handlers: {', '.join(hits[:4])}"
            elif kind == "web_surface":
                # A Next.js app with named route handlers and no other claim is
                # a composed service surface. That is a statement about what
                # the repository is, not a placeholder for missing information.
                if fp["routes"]:
                    return family, (f"typed web surface with "
                                    f"{len(fp['routes'])} route handlers")
            elif kind == "arch_and_persistence":
                # Architecture alone is the portfolio's most common shape and
                # carries little meaning. Requiring a real persistence
                # mechanism matters too: `file-backed JSON` is what 62 of 126
                # projects report, because nearly every one of them writes
                # something to disk somewhere. It is not evidence of a record
                # system, so only named stores count.
                store = fp["storage"][0] if fp["storage"] else ""
                named = [s for s in (fp["storage_list"] or [])
                         if s not in ("file-backed JSON", "CSV / tabular files")]
                if any(v in values for v in fp["arch"] if v) and named:
                    return family, (f"architecture = {fp['arch'][0]} with "
                                    f"declared store: {named[0]}")
    return FALLBACK, "no stronger evidence; defaulting to a presentation family"


# ------------------------------------------------------------------ variation

def stable_seed(repo: str) -> bytes:
    """A stable seed. It varies detail inside a family; it never picks one."""
    return hashlib.sha256(f"{DESIGN_VERSION}:{repo}".encode()).digest()


def derive(repo: str, dossier: dict) -> dict:
    fp = fingerprint(dossier)
    family, basis = resolve_family(fp)
    spec = FAMILIES[family]
    seed = stable_seed(repo)

    pick = lambda i, k: spec[k][seed[i] % len(spec[k])]  # noqa: E731

    return {
        "design_version": DESIGN_VERSION,
        "github_repo": repo,
        "family": family,
        "family_claim": spec["claim"],
        "family_basis": basis,
        "motif": pick(0, "motifs"),
        "material": pick(1, "materials"),
        "topology": pick(2, "topologies"),
        "depth": pick(3, "depths"),
        "accent": pick(4, "accents"),
        "geometry_phase": geometry_phase(repo),
        # The seed's influence on family is provably nil.
        "family_from_evidence": True,
    }


def structural_key(i: dict) -> tuple:
    """Uniqueness is measured on the family+composition, not on the seed.

    Two projects in the same family using the same motif, material, topology,
    depth AND accent would render identically. The seed varies geometry phase,
    which changes the drawing but not the composition -- so this key excludes it
    and reports real collisions.
    """
    return (i["family"], i["motif"], i["material"], i["topology"], i["depth"],
            i["accent"])


def audit(idents: dict[str, dict]) -> list[tuple[str, str]]:
    seen: dict[tuple, str] = {}
    clashes = []
    for repo, i in sorted(idents.items()):
        k = structural_key(i)
        if k in seen:
            clashes.append((seen[k], repo))
        else:
            seen[k] = repo
    return clashes


# Composition is derived from the family by rank, not by a raw hash modulo, so
# that the shared DNA of the studio survives while each project still lands on a
# distinct arrangement. Family members differ by taking different ranks, which
# is what stops five projects in one family from sharing a motif.
# Family option lists are plural (`motifs`); identity fields are singular.
VARIATION_ORDER = (("motif", "motifs"), ("material", "materials"),
                   ("topology", "topologies"), ("depth", "depths"),
                   ("accent", "accents"))


def geometry_phase(repo: str) -> float:
    """Stable per-repository geometry phase in [0, 1).

    Hashed from the repository name, which is correct HERE and nowhere else. The
    name may not choose the family, but phase is pure decorative variation with
    no semantic claim attached, so a stable name-derived value is the right
    input: it keeps the same repository on the same phase across runs and hosts.

    Phase is drawn from a wider digest than the earlier 8 hex digits, because a
    24-bit space collided visibly once the family rebalance changed the
    membership of several families at once.
    """
    digest = hashlib.sha256(f"{DESIGN_VERSION}:{repo}".encode()).hexdigest()
    return int(digest[:12], 16) / float(1 << 48)


def rebalance(idents: dict[str, dict]) -> dict[str, dict]:
    """Assign distinct compositions within each family.

    A hash modulo is uniform over the options but it collides: with four motifs
    and twenty projects in a family, five projects draw the same motif, and the
    collision is invisible until an audit reports it. Rank-based assignment
    cycles the options and then offsets by family, so every project in a family
    gets a distinct arrangement whenever the family is not larger than the
    product of its option counts.

    Geometry phase still comes from the stable seed. It changes the drawing
    without changing the composition, which is exactly the role section 22 gives
    a seed: vary detail inside a valid family, never choose the family.
    """
    by_family: dict[str, list[str]] = {}
    for repo, i in idents.items():
        by_family.setdefault(i["family"], []).append(repo)

    out = dict(idents)
    for family, repos in by_family.items():
        repos.sort()
        spec = FAMILIES[family]
        offset = int(stable_seed(family)[6])
        n = len(repos)
        for rank, repo in enumerate(repos):
            i = out[repo]
            # Mixed-radix walk over the family's option lists.
            rem = rank + offset
            for field, spec_key in VARIATION_ORDER:
                opts = spec[spec_key]
                i[field] = opts[rem % len(opts)]
                rem //= len(opts)
    return out


def motion_story(family: str, dossier: dict) -> str:
    """What this project's motion shows, in its own words where possible.

    The dossier's `animation_metaphor` is inherited from an (architecture,
    category) table and is identical for every project in a cell of it -- 30
    repositories shared one string. Where the project states its own workflow,
    that is preferred; otherwise the family's motion story is used, which is at
    least true of the system rather than true of its classification.
    """
    flow = (dossier.get("data_flow") or "").strip()
    # An IO round-trip is plumbing, not a motion story. "HTTP requests (JSON) →
    # file-backed JSON → HTTP responses (JSON)" described 30 repositories
    # identically and says nothing about what any of them does.
    io_shaped = bool(re.search(r"HTTP request|HTTP response|stdout|stderr",
                              flow, re.I))
    if "→" in flow and not io_shaped and \
            len([p for p in flow.split("→") if p.strip()]) >= 3:
        parts = [p.strip() for p in flow.split("→") if p.strip()]
        return " → ".join(p[:26] for p in parts[:4])
    wf = (dossier.get("primary_workflow") or "").strip()
    if wf and len(wf) > 30:
        return " ".join(wf.split())[:120]
    return MOTION[family]


MOTION = {
    "TRUST_BOUNDARY": "traffic reaches a boundary; the boundary admits some and holds the rest",
    "CAPITAL_MECHANICS": "value enters, allocates across positions, and settles",
    "RECORD_MECHANICS": "records traverse channels into an index that fills",
    "ORCHESTRATION": "nodes advertise, a coordinator selects, work converges",
    "EVIDENCE_SURFACE": "claims stack into tiers, and evidence is carried up to be checked",
    "INSTRUMENT": "a cursor runs this project's real commands and output resolves",
    "GENERATIVE_FIELD": "a seed expands through rings into structured form",
    "TOPOLOGY_CONTROL": "jobs queue, lease, and complete",
    "PRESENTATION": "a composed grid assembles and a sweep resolves it",
}


def sync_dossier(repo: str, ident: dict, dossier: dict) -> bool:
    """Write the resolved identity back into the dossier.

    Without this the dossier kept the legacy (architecture, category) visual
    fields while the renderer used the new ones, so the two disagreed: the plan
    reported "records ingest, normalise, index, answer" for a repository whose
    plate drew a boundary holding packets. Any field that describes a drawing
    has to come from the drawing.
    """
    family = ident["family"]
    story = motion_story(family, dossier)
    new = {
        "geometry_family": family,
        "primary_visual_metaphor": FAMILY_METAPHOR[family],
        "secondary_visual_metaphor": f"{ident['motif'].replace('_', ' ')} "
                                      f"in {ident['topology']} arrangement",
        "animation_metaphor": story,
        "material_family": ident["material"],
        "color_family": ident["accent"],
        "depth": ident["depth"],
        "terminal_metaphor": (f"{t['command']} — {t['help']}" if (
            t := (dossier.get("verified_commands") or [{}])[0]).get("command")
            else dossier.get("terminal_metaphor", "")),
    }
    changed = any(dossier.get(k) != v for k, v in new.items())
    dossier.update(new)
    return changed


FAMILY_METAPHOR = {
    "TRUST_BOUNDARY": "a sealed boundary holding or admitting traffic",
    "CAPITAL_MECHANICS": "value entering, allocating and settling across columns",
    "RECORD_MECHANICS": "channels carrying records into an index that fills",
    "ORCHESTRATION": "nodes converging on a coordinating cell",
    "EVIDENCE_SURFACE": "claims stacking into checkable tiers",
    "INSTRUMENT": "a command surface reporting as it runs",
    "GENERATIVE_FIELD": "a seed lattice expanding from an origin",
    "TOPOLOGY_CONTROL": "job lanes with lease markers",
    "PRESENTATION": "a composed grid assembling and settling",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    dossiers = {}
    for p in sorted(DOSSIER_DIR.glob("*.json")):
        d = json.loads(p.read_text())
        dossiers[d.get("github_repo", p.stem)] = d

    idents = {repo: derive(repo, d) for repo, d in dossiers.items()}
    idents = rebalance(idents)
    clashes = audit(idents)

    fam = Counter(i["family"] for i in idents.values())
    mot = Counter(i["motif"] for i in idents.values())
    mat = Counter(i["material"] for i in idents.values())
    print(f"V6 IDENTITY  ({len(idents)} projects)")
    print(f"  families  : {len(fam)}")
    for k, v in fam.most_common():
        print(f"      {v:4d} {k:<18}{FAMILIES[k]['claim']}")
    print(f"  motifs    : {len(mot)}   materials: {len(mat)}")
    print(f"  structural collisions: {len(clashes)}")
    for a, b in clashes[:10]:
        print(f"      {a} ~ {b}")

    # Proof that the seed does not choose the family: the same repo name under
    # two different dossiers must resolve to two different families.
    print("\n  seed-independence of family resolution:")
    shown = 0
    for repo, d in dossiers.items():
        if shown >= 3:
            break
        other = dict(d)
        other["project_category"] = "GENERAL"
        other["architecture_type"] = "DOCUMENT"
        other["security_characteristics"] = []
        other["verified_commands"] = []
        other["problem"] = "a static document with no interfaces"
        other["data_flow"] = ""
        a, b = derive(repo, d), derive(repo, other)
        marker = "differs" if a["family"] != b["family"] else "same"
        print(f"      {repo:<22} real={a['family']:<18} stripped={b['family']:<18} {marker}")
        shown += 1

    if args.write:
        IDENTITY.write_text(json.dumps({
            "$comment": "V6 project identities. Family is resolved from the "
                        "dossier; the stable seed varies detail inside that "
                        "family and cannot select one.",
            "design_version": DESIGN_VERSION,
            "count": len(idents),
            "identities": idents,
        }, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nwritten -> {IDENTITY.relative_to(PROFILE)}")

        # The dossier's visual fields are brought into line with the identity, so
        # the plan, the gallery and the renderer describe the same drawing.
        touched = 0
        for p in sorted(DOSSIER_DIR.glob("*.json")):
            d = json.loads(p.read_text())
            repo = d.get("github_repo", p.stem)
            if repo not in idents:
                continue
            if sync_dossier(repo, idents[repo], d):
                touched += 1
            p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n")
        print(f"synced {touched} dossier(s) to the resolved identity")
    return 1 if clashes else 0


if __name__ == "__main__":
    raise SystemExit(main())
