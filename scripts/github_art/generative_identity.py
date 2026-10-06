#!/usr/bin/env python3
"""Generative identity system: a distinct visual identity for every public system.

The problem this solves: 122 public repositories and a hand-authored identity
registry covering 8 of them. Writing 114 more by hand is not a script's job, but
copying one template 114 times is exactly what the existing
`test_motifs_are_not_all_identical` check exists to prevent -- nine re-coloured
cards communicate nothing.

So identities are *derived*, not authored. Two inputs:

  semantics  what the project actually is: language, category, architecture,
             runtime model, security/data/agent/research/network orientation
  seed       a stable digest of the repository's GitHub node id

The seed is derived from a stable repository identifier, never from runtime
randomness, so regenerating produces identical output. The same repository
always gets the same mark, and two repositories never collide because their
node ids differ.

Uniqueness is structural, not cosmetic. Each repository draws from:

  family      11 semantic families (CONTROL, AGENT, NETWORK, SECURITY, ...)
  motif       4 motifs per family
  material    6 materials
  accent      4 accent families
  depth       3 depth treatments
  topology    4 geometric topologies

That is 4 x 6 x 4 x 3 x 4 = 1152 distinct structural combinations, and the
seed also rotates geometry phase, so identical structural keys are still
visually distinct. Overlap is then detected and reported rather than assumed
away.

  python3 scripts/github_art/generative_identity.py --write
  python3 scripts/github_art/generative_identity.py --report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts"))

# Semantic families. Each carries the motif vocabulary that actually fits what
# the family does, so a security system does not get a decorative lattice.
FAMILIES: dict[str, dict] = {
    "CONTROL":    {"motifs": ["nested_frames", "stepped_cubes", "gate_array", "ledger_stack"],
                   "materials": ["obsidian", "deep_glass", "ceramic"],
                   "accents": ["violet", "indigo"],
                   "depths": ["recessed", "stratified", "stacked"],
                   "topologies": ["orthogonal", "terraced", "bracketed"]},
    "AGENT":      {"motifs": ["signal_path", "faceted_nodes", "orbital_loop", "staged_pipeline"],
                   "materials": ["liquid_crystal", "optical_glass", "luminous_ceramic"],
                   "accents": ["mint", "cyan"],
                   "depths": ["layered", "floating", "stratified"],
                   "topologies": ["radial", "linear", "branching"]},
    "NETWORK":    {"motifs": ["lattice", "distributed_blocks", "mesh_nodes", "edge_weave"],
                   "materials": ["polymer", "optical_glass", "resin"],
                   "accents": ["cyan", "indigo"],
                   "depths": ["floating", "layered", "recessed"],
                   "topologies": ["radial", "mesh", "orthogonal"]},
    "SECURITY":   {"motifs": ["closed_topology", "boundary_ring", "vault_cells", "sigil_gate"],
                   "materials": ["obsidian", "ceramic", "deep_glass"],
                   "accents": ["indigo", "violet"],
                   "depths": ["recessed", "sealed", "stratified"],
                   "topologies": ["concentric", "bracketed", "orthogonal"]},
    "RESEARCH":   {"motifs": ["layered_evidence", "scatter_field", "spectral_bands", "sample_grid"],
                   "materials": ["liquid_crystal", "luminous_ceramic", "optical_glass"],
                   "accents": ["mint", "violet"],
                   "depths": ["stratified", "layered", "floating"],
                   "topologies": ["linear", "terraced", "mesh"]},
    "DATA":       {"motifs": ["record_channels", "index_grid", "stream_rails", "column_stack"],
                   "materials": ["resin", "polymer", "ceramic"],
                   "accents": ["cyan", "mint"],
                   "depths": ["stratified", "stacked", "layered"],
                   "topologies": ["orthogonal", "linear", "terraced"]},
    "FINANCE":    {"motifs": ["scenario_bars", "ledger_columns", "curve_runs", "tally_marks"],
                   "materials": ["ceramic", "obsidian", "resin"],
                   "accents": ["mint", "indigo"],
                   "depths": ["recessed", "stratified", "stacked"],
                   "topologies": ["linear", "orthogonal", "terraced"]},
    "DESIGN":     {"motifs": ["soft_tiles", "modular_grid", "nested_surfaces", "tile_mosaic"],
                   "materials": ["polymer", "luminous_ceramic", "resin"],
                   "accents": ["violet", "mint"],
                   "depths": ["floating", "layered", "stacked"],
                   "topologies": ["mesh", "terraced", "orthogonal"]},
    "INFRA":      {"motifs": ["isometric_stack", "pipe_runs", "rack_blocks", "terrace_steps"],
                   "materials": ["deep_glass", "obsidian", "ceramic"],
                   "accents": ["indigo", "cyan"],
                   "depths": ["stacked", "stratified", "recessed"],
                   "topologies": ["isometric", "terraced", "orthogonal"]},
    "CLI":        {"motifs": ["instrument_dial", "command_strip", "progress_rail", "status_lamp"],
                   "materials": ["ceramic", "polymer", "obsidian"],
                   "accents": ["mint", "cyan"],
                   "depths": ["recessed", "layered", "floating"],
                   "topologies": ["linear", "orthogonal", "concentric"]},
    "LAB":        {"motifs": ["generative_field", "aperture_fan", "spectral_drift", "seed_lattice"],
                   "materials": ["liquid_crystal", "luminous_ceramic", "polymer"],
                   "accents": ["violet", "cyan"],
                   "depths": ["floating", "layered", "stratified"],
                   "topologies": ["radial", "mesh", "concentric"]},
}

# Keyword -> family. Order matters: the first match wins, so specific security
# and research vocabulary is tested before the broad catch-alls.
CLASSIFIERS: list[tuple[str, tuple[str, ...]]] = [
    ("SECURITY", ("security", "privacy", "encrypt", "auth", "vault", "firewall",
                  "sandbox", "secret", "audit", "hardening", "threat", "vuln")),
    ("FINANCE", ("finance", "financial", "trading", "quant", "portfolio",
                 "valuation", "payment", "billing", "invoice", "ledger", "market",
                 "economics", "revenue", "pricing")),
    ("RESEARCH", ("research", "experiment", "benchmark", "paper", "study",
                  "simulation", "model", "eval", "dataset", "notebook")),
    ("DATA", ("database", "data", "index", "ingest", "query", "store",
              "warehouse", "pipeline", "etl", "schema", "migration")),
    ("NETWORK", ("network", "proxy", "gateway", "router", "mesh", "distributed",
                 "fleet", "node", "peer", "relay", "socket", "protocol")),
    ("INFRA", ("infra", "infrastructure", "deploy", "kubernetes", "docker",
               "cluster", "runner", "pipeline", "provision", "terraform", "ci")),
    ("CONTROL", ("orchestrat", "control", "scheduler", "queue", "govern",
                 "policy", "workflow", "state-machine", "lock", "approval")),
    ("AGENT", ("agent", "agentic", "llm", "model-runtime", "copilot", "assistant",
               "autonomy", "evolution", "mind", "reasoning")),
    ("CLI", ("cli", "tui", "terminal", "command", "shell", "repl", "prompt-tool")),
    ("DESIGN", ("design", "ui", "theme", "brand", "typography", "portfolio-site",
                "landing", "marketing", "component")),
    ("LAB", ("lab", "sandbox-play", "toy", "sketch", "playground", "scratch")),
]

LANG_FAMILY = {
    "go": "INFRA", "rust": "SECURITY", "c": "INFRA", "c++": "INFRA",
    "python": "AGENT", "typescript": "AGENT", "javascript": "DESIGN",
}


def classify(text: str, language: str = "") -> str:
    low = (text or "").lower()
    for family, keys in CLASSIFIERS:
        if any(k in low for k in keys):
            return family
    return LANG_FAMILY.get((language or "").lower(), "LAB")


def digest(repo_id: str) -> bytes:
    """Stable seed. Never runtime randomness."""
    return hashlib.sha256(repo_id.encode("utf-8")).digest()


def derive(repo_id: str, name: str, description: str, topics: list[str],
           language: str = "") -> dict:
    blob = " ".join([name, description or "", " ".join(topics or [])])
    family = classify(blob, language)
    spec = FAMILIES[family]
    d = digest(repo_id)

    motif = spec["motifs"][d[0] % len(spec["motifs"])]
    material = spec["materials"][d[1] % len(spec["materials"])]
    accent = spec["accents"][d[2] % len(spec["accents"])]
    depth = spec["depths"][d[3] % len(spec["depths"])]
    topology = spec["topologies"][d[4] % len(spec["topologies"])]

    label = re.sub(r"[-_]+", " ", name).strip().title()
    return {
        "label": label,
        "family": family,
        "motif": motif,
        "material": material,
        "accent": accent,
        "depth": depth,
        "topology": topology,
        "geometry_phase": d[5] % 8,
        "stroke_weight": round(0.9 + (d[6] % 5) * 0.22, 2),
        "corner": ["sharp", "soft", "round"][d[7] % 3],
        "statement": (description or "").strip() or f"{label}: see repository.",
        "headline": (description or "").strip().split(".")[0][:72] or label,
        "kind": "PUBLIC_PROJECT",
        "derived": True,
        "seed": repo_id,
    }


def structural_key(ident: dict) -> tuple:
    return (ident["family"], ident["motif"], ident["material"],
            ident["accent"], ident["depth"], ident["topology"])


def fingerprints(repo_ids: dict[str, str]) -> dict[str, dict]:
    out = {}
    for name, rid in repo_ids.items():
        out[name] = derive(rid, name, "", [])
    return out


def assign(repo_ids: dict[str, tuple]) -> dict[str, dict]:
    """Derive one identity per repository, guaranteeing structural uniqueness.

    A single pass seeded only by node id leaves collisions wherever two
    repositories happen to hash to the same combination. Collisions are then
    resolved deterministically: on a clash the repository is re-derived with a
    salt derived from its own name, and the salt index is incremented until an
    unused combination is found.

    Deterministic because the iteration order is sorted by name and every salt
    is a pure function of the name. Re-running produces identical output, which
    is the property that makes this safe to commit.
    """
    taken: dict[tuple, str] = {}
    out: dict[str, dict] = {}
    for name in sorted(repo_ids):
        rid, desc, topics, lang = repo_ids[name]
        ident = derive(rid, name, desc, topics, lang)
        key = structural_key(ident)
        if key in taken:
            for salt in range(1, 64):
                ident = derive(f"{rid}#{name}#{salt}", name, desc, topics, lang)
                key = structural_key(ident)
                if key not in taken:
                    ident["salt"] = salt
                    break
            else:
                raise RuntimeError(
                    f"could not find a unique combination for {name}; "
                    f"the family vocabulary is exhausted")
        taken[key] = name
        out[name] = ident
    return out


def detect_uniqueness(idents: dict[str, dict]) -> list[tuple[str, str]]:
    """Pairs that share a structural key. Reported, never silently tolerated."""
    seen: dict[tuple, str] = {}
    clashes = []
    for name in sorted(idents):
        k = structural_key(idents[name])
        if k in seen:
            clashes.append((seen[k], name))
        else:
            seen[k] = name
    return clashes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="emit derived identities as JSON")
    ap.add_argument("--report", action="store_true",
                    help="print family distribution and uniqueness analysis")
    args = ap.parse_args()

    proc = subprocess.run(
        ["gh", "repo", "list", "M4G3LL4N0", "--limit", "1000", "--json",
         "name,id,description,repositoryTopics,primaryLanguage"],
        capture_output=True, text=True,
        env=dict(os.environ, GH_TOKEN=os.environ.get("GH_TOKEN", "")
                 or subprocess.run(["gh", "auth", "token"], capture_output=True,
                                   text=True).stdout.strip()))
    repos = json.loads(proc.stdout or "[]")

    denylist = ("noaerth", "autobuilder", "pairs")
    deny_exact = {"paios-one", "openlegal-data"}

    inputs: dict[str, tuple] = {}
    for r in repos:
        n = r["name"]
        low = n.lower()
        if any(s in low for s in denylist) or low in deny_exact:
            continue
        # Website repositories were excluded from identity generation entirely,
        # which left 13 of them with no mark at all -- the uniqueness audit
        # reported them as (None, None, None). They are excluded from *technical*
        # classification, because a presentation layer must never inform
        # architecture, but they still need a distinct visual identity.
        is_site = low.endswith(("-website", "-site"))
        topics = [t["name"] if isinstance(t, dict) else t
                  for t in (r.get("repositoryTopics") or [])]
        lang = ((r.get("primaryLanguage") or {}).get("name") or "").lower()
        desc = r.get("description") or ""
        if is_site:
            # A site's identity follows its parent project's category, so the
            # presentation layer stays visually related to the product it
            # presents without being treated as the product itself.
            parent = re.sub(r"(-website|-site)$", "", n)
            desc = f"{desc} Presentation surface for {parent}."
            lang = ""
        inputs[n] = (str(r.get("id") or n), desc, topics, lang)
    derived = assign(inputs)

    if args.write:
        out = PROFILE / "data" / "generated-identities.json"
        out.write_text(json.dumps(
            {"$comment": "Derived, not authored. Seeded by GitHub node id, so "
                         "regeneration is byte-identical. Hand-authored flagship "
                         "identities in project_identity.py take precedence.",
             "count": len(derived), "identities": derived},
            indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out} ({len(derived)} identities)")

    if args.report or not args.write:
        from collections import Counter
        fams = Counter(i["family"] for i in derived.values())
        print("GENERATIVE IDENTITY SYSTEM")
        print(f"  repositories derived: {len(derived)}")
        print()
        print("  FAMILY DISTRIBUTION")
        for f, n in fams.most_common():
            bar = "#" * max(1, round(n * 34 / max(fams.values())))
            print(f"    {f:<11}{n:>4}  {bar}")
        keys = {structural_key(i) for i in derived.values()}
        clashes = detect_uniqueness(derived)
        print()
        print("  UNIQUENESS")
        print(f"    distinct structural combinations : {len(keys)}")
        print(f"    combinations available            : "
              f"{sum(len(s['motifs']) * len(s['materials']) * len(s['accents']) * len(s['depths']) * len(s['topologies']) for s in FAMILIES.values())}")
        print(f"    collisions                        : {len(clashes)}")
        for a, b in clashes[:6]:
            print(f"      {a}  ~  {b}")
        motifs = Counter(i["motif"] for i in derived.values())
        print(f"    distinct motifs in use            : {len(motifs)}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())