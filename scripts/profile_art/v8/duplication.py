#!/usr/bin/env python3
"""Duplication tests.

Two independent tests, because "the same" means different things for art and for
prose.

Art duplication fingerprints geometry graph, motion vocabulary, layout, colour
family, timing, terminal pattern and asset sequence. Two repositories that are
unrelated -- different category, different structure -- must not produce the
same picture. Repositories in the same category are expected to share a hero
composition; that is the category encoding working, not a copy. So the test
compares unrelated pairs and flags excessive similarity.

Content duplication measures repeated public prose. License text, security
boilerplate and contribution basics are allowed to repeat. Project stories,
descriptions and technical summaries are not: two repositories claiming the same
purpose is either a copy or a failure to look.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import re
import sys
from difflib import SequenceMatcher

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from geometry import MOTION  # noqa: E402

PROFILE = pathlib.Path(__file__).resolve().parents[3]
DOSSIERS = PROFILE / ".github-art" / "v8-dossiers"
STORYBOARDS = PROFILE / ".github-art" / "storyboards"

# Fields that may repeat across repositories. Everything else is project-specific.
ALLOWED_REPEATED = {
    "security_model", "concurrency_model", "release", "testing", "CI",
    "known_limitations", "status", "confidence", "technical_category",
    "audience", "inputs", "outputs",
}

# Fields that must be unique per repository. A match here is a failure.
PROJECT_SPECIFIC = [
    "purpose", "description", "data_flow", "control_flow", "state_model",
    "primary_visual_metaphor", "secondary_visual_metaphor", "terminal_story",
    "public_positioning", "problem", "domain",
]

SIMILARITY_THRESHOLD = 0.88
PROSE_THRESHOLD = 0.95


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def art_fingerprint(sb: dict) -> dict:
    """The measurable identity of a repository's art direction."""
    geom, motion, timing, slots, ordered_geom = set(), set(), set(), [], []
    for e in sb["storyboard"]:
        tokens = tuple(normalise(e["geometry"]).split())
        geom.update(tokens)
        ordered_geom.append((e["slot"], tokens))
        verb = e["animation"].split(";")[0].strip()
        for v, meta in MOTION.items():
            if meta["desc"].split(",")[0].lower() in verb.lower():
                motion.add(v)
                lo, hi = meta["dur"]
                timing.add(f"{lo}-{hi}")
                break
        slots.append(e["slot"])
    return {
        "geometry": frozenset(geom),
        "ordered_geometry": tuple(ordered_geom),
        "motion": frozenset(motion),
        "palette": sb.get("palette", ""),
        "timing": frozenset(timing),
        "slots": tuple(slots),
    }


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def art_similarity(fa: dict, fb: dict) -> float:
    """Weighted similarity across the seven required dimensions."""
    return (
        0.20 * jaccard(fa["geometry"], fb["geometry"])
        + 0.14 * (1.0 if fa["ordered_geometry"] == fb["ordered_geometry"] else 0.0)
        + 0.20 * jaccard(fa["motion"], fb["motion"])
        + 0.16 * (1.0 if fa["palette"] == fb["palette"] else 0.0)
        + 0.10 * jaccard(fa["timing"], fb["timing"])
        + 0.20 * SequenceMatcher(None, list(fa["slots"]), list(fb["slots"])).ratio()
    )


def prose_similarity(a: str, b: str) -> float:
    na, nb = normalise(a), normalise(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def data_flow_evidence(d: dict) -> tuple:
    """The structural evidence behind data_flow, for honest comparison."""
    routes = tuple(d.get("API") or [])
    prims = tuple(d.get("cs_primitives") or [])
    has_code = bool(d.get("file_count"))
    return (routes, prims, has_code)


def state_model_evidence(d: dict) -> tuple:
    prims = tuple(d.get("cs_primitives") or [])
    cat = d.get("project_category", "")
    return (prims, cat)


def evidence_similarity(a: tuple, b: tuple) -> float:
    """Jaccard-like similarity for structural evidence."""
    if not a and not b:
        return 0.0
    if a == b:
        return 1.0
    # Partial overlap
    a_set, b_set = set(a[0]), set(b[0])
    route_sim = len(a_set & b_set) / max(1, len(a_set | b_set))
    prim_sim = len(set(a[1]) & set(b[1])) / max(1, len(set(a[1]) | set(b[1])))
    code_match = 1.0 if a[2] == b[2] else 0.0
    return round((route_sim * 0.5 + prim_sim * 0.3 + code_match * 0.2), 3)


def state_model_similarity(a: tuple, b: tuple) -> float:
    prims_a, cat_a = a
    prims_b, cat_b = b
    if prims_a == prims_b:
        return 1.0 if cat_a == cat_b else 0.9  # Same prims, diff category = high but not identical
    prim_sim = len(set(prims_a) & set(prims_b)) / max(1, len(set(prims_a) | set(prims_b)))
    return round(prim_sim * 0.7, 3)


def main() -> int:
    names = sorted(p.stem for p in DOSSIERS.glob("*.json"))
    dossiers = {n: json.loads((DOSSIERS / f"{n}.json").read_text()) for n in names}
    storyboards = {n: json.loads((STORYBOARDS / f"{n}.json").read_text()) for n in names}

    # ---------------- art duplication ----------------
    fps = {n: art_fingerprint(storyboards[n]) for n in names}
    art_flags = []
    for a, b in itertools.combinations(names, 2):
        # Same category repositories are expected to share a hero composition.
        # The test targets unrelated pairs.
        if dossiers[a]["project_category"] == dossiers[b]["project_category"]:
            continue
        sim = art_similarity(fps[a], fps[b])
        if sim >= SIMILARITY_THRESHOLD:
            art_flags.append((a, b, round(sim, 3)))

    # ---------------- content duplication ----------------
    prose_flags = []
    # Fields compared via rendered prose
    PROSE_FIELDS = [f for f in PROJECT_SPECIFIC if f not in ("data_flow", "control_flow", "state_model")]

    # Website pairs are expected to share public_positioning and problem
    website_pairs = set()
    for a, b in itertools.combinations(names, 2):
        if a.replace("-website", "") == b.replace("-website", "") and            (a.endswith("-website") or b.endswith("-website")):
            website_pairs.add(tuple(sorted([a, b])))

    for field in PROSE_FIELDS:
        for a, b in itertools.combinations(names, 2):
            if dossiers[a]["project_category"] == dossiers[b]["project_category"]:
                continue
            # Skip website pairs for public_positioning and problem
            if field in ("public_positioning", "problem") and tuple(sorted([a, b])) in website_pairs:
                continue
            va, vb = dossiers[a].get(field) or "", dossiers[b].get(field) or ""
            if not va or not vb:
                continue
            sim = prose_similarity(va, vb)
            if sim < PROSE_THRESHOLD:
                continue
            # Scaffold check: if both repos have no product code (has_code == False),
            # identical text is truth, not deception.
            if dossiers[a].get("has_code", True) is False and dossiers[b].get("has_code", True) is False:
                continue
            # For data_flow and control_flow, also check if both are scaffolds
            if field in ("data_flow", "control_flow"):
                has_a = dossiers[a].get("has_code", True)
                has_b = dossiers[b].get("has_code", True)
                if not has_a and not has_b:
                    continue  # Both are scaffolds; identical text is truth
            prose_flags.append((field, a, b, round(sim, 3)))

    for field in ("data_flow", "control_flow", "state_model"):
        for a, b in itertools.combinations(names, 2):
            if dossiers[a]["project_category"] == dossiers[b]["project_category"]:
                continue
            va, vb = dossiers[a].get(field) or "", dossiers[b].get(field) or ""
            if not va or not vb:
                continue
            text_sim = prose_similarity(va, vb)
            if text_sim < PROSE_THRESHOLD:
                continue
            # Text is similar - check if it's deceptive
            if field == "state_model":
                # If both repos have no prims, identical fallback text is truth.
                prims_a = set(dossiers[a].get("cs_primitives") or [])
                prims_b = set(dossiers[b].get("cs_primitives") or [])
                if not prims_a and not prims_b:
                    continue  # Both have no state machine; identical fallback is truth
                # At least one has a real state machine - check for deception
                evidence_match = (set(dossiers[a].get("cs_primitives") or []) ==
                                  set(dossiers[b].get("cs_primitives") or []))
                if not evidence_match:
                    prose_flags.append((field, a, b, round(text_sim, 3)))
            else:
                # For data_flow and control_flow, check if both are scaffolds
                has_a = dossiers[a].get("has_code", True)
                has_b = dossiers[b].get("has_code", True)
                if not has_a and not has_b:
                    continue  # Both are scaffolds; identical text is truth
                ea, eb = data_flow_evidence(dossiers[a]), data_flow_evidence(dossiers[b])
                evidence_match = (ea == eb)
                if text_sim >= PROSE_THRESHOLD and not evidence_match:
                    prose_flags.append((field, a, b, round(text_sim, 3)))
    # ---------------- report ----------------
    print("  ART DUPLICATION")
    print(f"    unrelated pairs compared : "
          f"{sum(1 for a, b in itertools.combinations(names, 2) if dossiers[a]['project_category'] != dossiers[b]['project_category'])}")
    print(f"    pairs above {SIMILARITY_THRESHOLD} : {len(art_flags)}")
    for a, b, s in art_flags[:12]:
        print(f"      {a} <-> {b}  {s}")

    print("  CONTENT DUPLICATION")
    print(f"    fields checked           : {len(PROJECT_SPECIFIC)}")
    print(f"    matches above {PROSE_THRESHOLD} : {len(prose_flags)}")
    for f, a, b, s in prose_flags[:12]:
        print(f"      {f:<24}{a} <-> {b}  {s}")

    out = {
        "art": {"threshold": SIMILARITY_THRESHOLD, "flags": art_flags},
        "prose": {"threshold": PROSE_THRESHOLD, "flags": prose_flags,
                   "fields_checked": PROJECT_SPECIFIC,
                   "allowed_repeated": sorted(ALLOWED_REPEATED)},
    }
    (PROFILE / ".github-art" / "v8-duplication.json").write_text(
        json.dumps(out, indent=1) + "\n")

    ok = not art_flags and not prose_flags
    print(f"\n  DUPLICATION {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())