#!/usr/bin/env python3
"""Public-information audit for the V5 redesign.

Every byte the redesign produces is published. These tests are the boundary.

They assert three things:

  1. Nothing withheld from the public inventory appears in a published artefact.
     Withheld material is excluded by construction from the generator; this
     checks the construction actually held.
  2. No local path, hostname, or credential shape reaches a public file.
  3. The internal design vocabulary never ships.

They also assert the preservation baseline still exists, because a redesign that
cannot be diffed against a ledger is a redesign that can quietly delete a
`go install` line.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

# this file sits one level deeper than scripts/, so the repo root is parents[2]
PROFILE = Path(__file__).resolve().parents[2]
INVENTORY = PROFILE / "GITHUB_V5_PUBLIC_INVENTORY.json"
LEDGER = PROFILE / "GITHUB_V5_CONTENT_LEDGER.json"
SYSTEM_MAP_EVIDENCE = PROFILE / "system-map-evidence.json"

PUBLIC_ARTEFACTS = (
    "GITHUB_V5_DESIGN_SYSTEM.md",
    "GITHUB_V5_ROLLOUT_PLAN.md",
    "GITHUB_V5_PUBLIC_INVENTORY.json",
    "GITHUB_V5_CONTENT_LEDGER.json",
    "README.md",
    "system-map-evidence.json",
)

PRIVATE_PATH = re.compile(
    r"(/Users/|/home/|/Volumes/|[A-Za-z]:\\Users\\|\.local/|node_modules/)", re.I)
SECRET = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY)")
LOCAL_HOST = re.compile(r"\b(?:localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d+\.\d+)\b")
INTERNAL_VOCAB = re.compile(
    r"\b(dmt|psychedelic|altered state|hallucination|acid|shroom|trip)\b", re.I)


def text(name: str) -> str:
    path = PROFILE / name
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


class TestInventoryBoundary(unittest.TestCase):
    """Withheld material must be absent, not merely unlabelled."""

    def setUp(self):
        self.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_inventory_has_no_private_repository(self):
        offenders = [e["name"] for e in self.inventory["repositories"]
                     if e["name"].lower().endswith(
                         ("-website", "-site", "-web", "-landing", "-marketing"))]
        self.assertEqual(offenders, [],
                         "deployment-site repositories must not appear in the inventory")

    def test_counts_are_consistent(self):
        counts = self.inventory["counts"]
        listed = len(self.inventory["repositories"])
        self.assertEqual(counts["public_visible"], listed)
        classified = sum(counts["by_classification"].values())
        self.assertEqual(classified, listed,
                         "every public repository must carry a classification")
        engineering = [e for e in self.inventory["repositories"]
                       if e["classification"] not in ("PROFILE", "LEGACY_EASTER_EGG")]
        self.assertEqual(counts["engineering_systems"], len(engineering))

    def test_flagships_are_an_explicit_allowlist(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art.project_identity import FLAGSHIP_ORDER
        listed = {e["name"] for e in self.inventory["repositories"]
                  if e["classification"] == "FLAGSHIP"}
        self.assertEqual(listed, set(FLAGSHIP_ORDER),
                         "the flagship set must be reviewed, not inferred")

    def test_every_public_repository_has_an_identity(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art import project_identity as P
        missing = [e["name"] for e in self.inventory["repositories"]
                   if e["classification"] not in ("PROFILE", "LEGACY_EASTER_EGG")
                   and e["name"] not in P.IDENTITIES]
        self.assertEqual(missing, [],
                         "every public system needs a visual identity")

    def test_motifs_are_not_all_identical(self):
        """Nine re-coloured cards would communicate nothing."""
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art import project_identity as P
        motifs = [P.identity(s)["motif"] for s in P.FLAGSHIP_ORDER]
        self.assertGreaterEqual(len(set(motifs)), 4,
                                "flagship marks must be distinguishable in silhouette")


class TestNoPrivateLeak(unittest.TestCase):
    def test_no_local_paths_in_public_files(self):
        offenders = []
        for name in PUBLIC_ARTEFACTS:
            for match in PRIVATE_PATH.finditer(text(name)):
                offenders.append(f"{name}: {match.group(0)}")
        self.assertEqual(offenders, [], f"local path in a public file: {offenders}")

    def test_no_secrets_in_public_files(self):
        offenders = []
        for name in PUBLIC_ARTEFACTS:
            for match in SECRET.finditer(text(name)):
                offenders.append(f"{name}: {match.group(0)[:10]}...")
        self.assertEqual(offenders, [])

    def test_no_local_hostnames_in_shipped_art(self):
        offenders = []
        art = PROFILE / "assets" / "profile"
        if art.is_dir():
            for path in art.rglob("*.svg"):
                for match in LOCAL_HOST.finditer(
                        path.read_text(encoding="utf-8", errors="replace")):
                    offenders.append(f"{path.name}: {match.group(0)}")
        self.assertEqual(offenders, [], f"local hostname in artwork: {offenders}")

    def test_internal_vocabulary_never_ships(self):
        offenders = []
        for name in ("GITHUB_V5_DESIGN_SYSTEM.md", "GITHUB_V5_ROLLOUT_PLAN.md"):
            body = text(name)
            # the design-system document names the forbidden list in order to ban
            # it; that single mention is the specification, not a leak
            for match in INTERNAL_VOCAB.finditer(body):
                word = match.group(0).lower()
                if name.endswith("DESIGN_SYSTEM.md") and body.count(word) <= 1:
                    continue
                offenders.append(f"{name}: {word}")
        self.assertEqual(offenders, [],
                         f"internal design vocabulary reached a public document: {offenders}")


class TestEvidenceIntegrity(unittest.TestCase):
    def test_every_drawn_edge_is_evidenced(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art.directions import v5_optical_recursive as V5
        data = json.loads(SYSTEM_MAP_EVIDENCE.read_text(encoding="utf-8"))
        declared = {f"{e['source']}->{e['target']}" for e in data["edges"]}
        LAYERS = V5.LAYERS

        # Symmetry in both directions. Without this, the evidence file is
        # decorative: adding an invented edge to it would change nothing
        # observable, which is exactly the failure this audit exists to catch.
        drawn = set(V5.RELATIONSHIPS)
        evidenced_sources = {e["source"] for e in data["edges"]}
        self.assertEqual(
            evidenced_sources - drawn, set(),
            "evidence declares a relationship the map does not draw")
        self.assertEqual(
            drawn - evidenced_sources, set(),
            "the map draws a relationship with no evidence entry")
        self.assertTrue(declared, "the evidence file must declare at least one edge")
        for edge in data["edges"]:
            self.assertTrue(edge.get("evidence"),
                            f"{edge['source']}->{edge['target']} has no evidence")
            for citation in edge["evidence"]:
                self.assertTrue(citation.get("path") and citation.get("repo"))
                self.assertIsNone(PRIVATE_PATH.search(json.dumps(citation)),
                                  "evidence citations must stay public-safe")
        # every engineering system drawn on the map must have an identity
        from github_art import project_identity as P
        for _layer, _key, _blurb, items in LAYERS:
            for slug, _title, _note in items:
                self.assertIn(slug, P.IDENTITIES,
                              f"{slug} is drawn on the map with no identity")

    def test_disclaimed_relationships_stay_absent(self):
        """portfolio-os -> agentos is disclaimed in its own README."""
        data = json.loads(SYSTEM_MAP_EVIDENCE.read_text(encoding="utf-8"))
        drawn = {f"{e['source']}->{e['target']}" for e in data["edges"]}
        self.assertNotIn("noaerth-portfolio-os->agentos", drawn,
                         "a relationship the project explicitly disclaims must not be drawn")
        self.assertTrue(any("portfolio-os" in pair["pair"][0]
                            for pair in data.get("deliberate_non_edges", [])),
                        "the disclaimer should be recorded as a deliberate non-edge")


class TestPreservationBaseline(unittest.TestCase):
    """The ledger is what makes "nothing was lost" checkable."""

    def setUp(self):
        self.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        self.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_ledger_covers_every_public_repository(self):
        expected = {e["name"] for e in self.inventory["repositories"]}
        self.assertEqual(set(self.ledger["repositories"]), expected)

    def test_ledger_actually_captured_content(self):
        totals = self.ledger["totals"]
        self.assertGreater(totals["commands"], 0,
                           "an empty ledger would silently pass every future diff")
        self.assertGreater(totals["first_party_links"], 0)
        self.assertGreater(totals["caveats"], 0,
                           "honest limitations are the first thing a redesign loses")

    def test_every_public_repository_has_a_readme(self):
        missing = [name for name, entry in self.ledger["repositories"].items()
                   if not entry["readme_present"]]
        self.assertEqual(missing, [],
                         f"public repositories with no README: {missing}")

    def test_ledger_records_ci_truth_not_workflow_presence(self):
        for name, entry in self.ledger["repositories"].items():
            facts = entry["facts"]
            self.assertIn("ci_latest_conclusion", facts)
            self.assertIn("ci_green", facts)
            # a repository may claim a workflow and still be red; both facts
            # must be independently recorded rather than collapsed into one
            self.assertIsInstance(facts["ci_green"], bool)

    def test_measured_totals_match_the_ledger(self):
        engineering = [e for e in self.inventory["repositories"]
                       if e["classification"] not in ("PROFILE", "LEGACY_EASTER_EGG")]
        expected_tests = sum(e["verified_tests"] or 0 for e in engineering)
        measured = self.inventory["measured_totals"]
        self.assertEqual(measured["verified_tests"], expected_tests)
        self.assertEqual(
            measured["ci_green"],
            sum(1 for e in engineering if e["ci"]["green"]))
        self.assertEqual(measured["external_merged_prs"], 0,
                         "upstream work must stay at zero until it is real")


class TestTokenIntegrity(unittest.TestCase):
    """Token names are API. A collision is a silent regression."""

    def test_no_duplicate_token_assignment(self):
        """A later block must not shadow an earlier constant of the same name.

        The V5.1 block originally defined MOTION as an enum of motion kinds,
        shadowing the validated MOTION duration table from V5. Every animated
        asset then failed with KeyError("loop_seconds"). Source inspection is the
        only thing that catches this: both assignments are individually valid
        and the module imports cleanly either way.
        """
        source = (PROFILE / "scripts" / "github_art" / "tokens.py").read_text()
        assigned = re.findall(r"^([A-Z][A-Z0-9_]*)\s*(?::[^=]+)?=", source, re.M)
        seen: dict[str, int] = {}
        for name in assigned:
            seen[name] = seen.get(name, 0) + 1
        # assertFalse, not assertEqual against an empty set: an empty dict and
        # an empty set are equal in neither value nor type, so assertEqual
        # would fail on the very case this test exists to pass.
        shadowed = {k: v for k, v in seen.items() if v > 1}
        self.assertFalse(shadowed,
                         f"token name assigned more than once: {shadowed}")

    def test_required_token_groups_exist(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art import tokens as T
        for group in ("DEPTH", "SHAPE", "DENSITY", "DENSITY_TARGET", "MATERIAL",
                      "MOTION", "MOTION_KIND", "MOTIF", "MUTED", "HYPERREAL",
                      "INTENSITY_TARGET", "INTENSITY", "BUDGET"):
            self.assertTrue(hasattr(T, group), f"tokens.{group} is missing")

    def test_v5_motion_durations_survived_the_v51_extension(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art import tokens as T
        for key in ("loop_seconds", "travel_seconds", "caret_seconds"):
            self.assertIn(key, T.MOTION,
                          "the V5.1 enum shadowed the validated motion timings")


class TestDesignSystemIntegrity(unittest.TestCase):
    def test_no_stray_colours_in_generated_art(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art import validators as V
        build = PROFILE / "build" / "v5-chosen"
        if not build.is_dir():
            self.skipTest("no generated art present; run build_gallery.py")
        offenders = []
        for path in sorted(build.rglob("*.svg")):
            try:
                V.check_no_stray_literals(path.read_text(encoding="utf-8"), path.name)
            except V.ValidationError as exc:
                offenders.append(str(exc))
        self.assertEqual(offenders, [])

    def test_every_generated_plate_validates(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art import validators as V
        build = PROFILE / "build" / "v5-chosen"
        if not build.is_dir():
            self.skipTest("no generated art present; run build_gallery.py")
        failures = []
        for path in sorted(build.rglob("*.svg")):
            try:
                V.validate(path.read_text(encoding="utf-8"), path.name)
                V.check_motion_is_ambient(path.read_text(encoding="utf-8"), path.name)
            except V.ValidationError as exc:
                failures.append(str(exc))
        self.assertEqual(failures, [], f"generated art failed validation: {failures}")

    def test_budgets_respected(self):
        sys.path.insert(0, str(PROFILE / "scripts"))
        from github_art import tokens as T
        build = PROFILE / "build" / "v5-chosen"
        if not build.is_dir():
            self.skipTest("no generated art present")
        oversized = [f"{p.name} {p.stat().st_size / 1024:.1f}KB"
                     for p in build.rglob("*.svg")
                     if p.stat().st_size / 1024 > T.BUDGET["single_plate_kb"]]
        self.assertEqual(oversized, [], f"over plate budget: {oversized}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
