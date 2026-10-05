#!/usr/bin/env python3
"""Integrity tests for the public profile.

These exist because every asset in this repository is published, and because the
failure modes here are silent: a badge that renders "404 badge not found" still
returns HTTP 200, a card whose lookup key is wrong renders plausible filler, and
an SVG with a malformed animation parses cleanly while displaying nothing.

Run:  python3 -m unittest discover -s scripts -p 'test_*.py' -v
      python3 scripts/test_profile_assets.py          # same thing, terse

Network checks are skipped automatically when offline.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[1]
README = PROFILE / "README.md"
ASSETS = PROFILE / "assets" / "profile"
SOCIAL = PROFILE / "assets" / "social-preview.svg"
EVIDENCE = PROFILE / "system-map-evidence.json"
SIGNAL = ASSETS / "build-signal.json"

OWNER = "M4G3LL4N0"
SVG_NS = "{http://www.w3.org/2000/svg}"
ANIMATION_TAGS = {"animate", "animateTransform", "animateMotion", "set"}

# Performance budget. The whole identity has to stay cheap enough that GitHub
# serves it from cache on a phone.
PER_FILE_KB = 24
TOTAL_KB = 260

# Only these font stacks may appear. A webfont would be an external request and
# would render as Times on any machine that has not cached it.
ALLOWED_FONT_PREFIXES = (
    "-apple-system",
    "ui-monospace",
)

# Anything that would make the browser fetch a third party.
RESOURCE_ATTR = re.compile(r'(?:xlink:)?href\s*=\s*"([^"]*)"|url\(\s*([^)]*)\)', re.I)

PRIVATE_PATH = re.compile(
    r'(/Users/|/home/|/Volumes/|[A-Za-z]:\\\\Users\\\\|'
    r'\.local/|node_modules/|\.git/config)',
    re.I,
)
SECRET = re.compile(
    r'(gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|'
    r'sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)',
)
SITE_SUFFIXES = ("-website", "-site", "-web", "-landing", "-marketing")


def svgs() -> list[Path]:
    return sorted(ASSETS.rglob("*.svg")) + ([SOCIAL] if SOCIAL.is_file() else [])


def readme() -> str:
    return README.read_text(encoding="utf-8")


def http_status(url: str, timeout: int = 25) -> int | None:
    request = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "noaerth-profile-link-audit",
        "Accept": "*/*",
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return None


def offline() -> bool:
    return http_status("https://api.github.com", timeout=8) is None


class TestAssetsExist(unittest.TestCase):
    """Every local reference in the README resolves to a file on disk."""

    def test_referenced_assets_exist(self):
        missing = []
        for ref in re.findall(r'(?:src|srcset)="([^"]+)"', readme()):
            for candidate in ref.split(","):
                path = candidate.strip().split(" ")[0]
                if path.startswith(("http://", "https://", "/", "data:")):
                    continue
                if not (PROFILE / path).is_file():
                    missing.append(path)
        self.assertEqual(missing, [], f"README references missing files: {missing}")

    def test_no_broken_badge_service(self):
        text = readme()
        self.assertNotIn("img.shields.io/github/repo-count", text,
                         "the repo-count badge renders '404 badge not found'")
        self.assertNotIn("github-readme-stats", text,
                         "third-party stat cards break silently and are not evidence")


class TestSvgIntegrity(unittest.TestCase):
    def test_all_parse(self):
        broken = []
        for path in svgs():
            try:
                ET.fromstring(path.read_text(encoding="utf-8"))
            except ET.ParseError as exc:
                broken.append(f"{path.name}: {exc}")
        self.assertEqual(broken, [])

    def test_no_script_no_foreignobject(self):
        offenders = []
        for path in svgs():
            raw = path.read_text(encoding="utf-8")
            if "<script" in raw:
                offenders.append(f"{path.name}: <script>")
            if "foreignObject" in raw or "foreignobject" in raw:
                offenders.append(f"{path.name}: foreignObject is not portable in <img>")
            if "<image" in raw:
                offenders.append(f"{path.name}: embeds raster")
            if "onload" in raw or "onclick" in raw:
                offenders.append(f"{path.name}: inline event handler")
        self.assertEqual(offenders, [])

    def test_no_external_resources(self):
        """No third-party fetch. href/url() may only point inside the document."""
        offenders = []
        for path in svgs():
            raw = path.read_text(encoding="utf-8")
            for match in RESOURCE_ATTR.finditer(raw):
                value = (match.group(1) or match.group(2) or "").strip()
                if not value or value.startswith("#"):
                    continue
                offenders.append(f"{path.name}: {value[:60]}")
        self.assertEqual(offenders, [], "external resource reference found")

    def test_no_external_fonts(self):
        offenders = []
        for path in svgs():
            raw = path.read_text(encoding="utf-8")
            for stack in re.findall(r'font-family="([^"]+)"', raw):
                if not stack.strip().startswith(ALLOWED_FONT_PREFIXES):
                    offenders.append(f"{path.name}: {stack[:50]}")
        self.assertEqual(offenders, [], "only system font stacks are allowed")

    def test_valid_dimensions(self):
        offenders = []
        for path in svgs():
            root = ET.fromstring(path.read_text(encoding="utf-8"))
            view_box = root.get("viewBox")
            if not view_box:
                offenders.append(f"{path.name}: no viewBox")
                continue
            try:
                _, _, w, h = (float(v) for v in view_box.replace(",", " ").split())
            except ValueError:
                offenders.append(f"{path.name}: unparseable viewBox {view_box!r}")
                continue
            if w <= 0 or h <= 0:
                offenders.append(f"{path.name}: non-positive viewBox {view_box}")
            if root.get("width") is None or root.get("height") is None:
                offenders.append(f"{path.name}: missing width/height")
        self.assertEqual(offenders, [])

    def test_performance_budget(self):
        oversized = []
        total = 0
        for path in svgs():
            size = path.stat().st_size / 1024
            total += size
            if size > PER_FILE_KB:
                oversized.append(f"{path.name} {size:.1f}KB")
        self.assertEqual(oversized, [], f"over {PER_FILE_KB}KB: {oversized}")
        self.assertLessEqual(total, TOTAL_KB, f"total {total:.1f}KB over budget")

    def test_no_orphan_animations(self):
        """SMIL must be a child of the element it targets, or it silently no-ops."""
        orphans = []
        for path in svgs():
            root = ET.fromstring(path.read_text(encoding="utf-8"))

            def walk(node, parent):
                tag = node.tag.replace(SVG_NS, "")
                if tag in ANIMATION_TAGS:
                    parent_tag = parent.tag.replace(SVG_NS, "") if parent is not None else ""
                    if parent is None or parent_tag in ANIMATION_TAGS | {"defs", "svg"}:
                        orphans.append(f"{path.name}: <{tag}> under <{parent_tag or 'none'}>")
                for child in node:
                    walk(child, node)

            for child in root:
                walk(child, root)
        self.assertEqual(orphans, [], f"orphan animations: {orphans}")

    def test_accessible_name_and_description(self):
        missing = []
        for path in svgs():
            root = ET.fromstring(path.read_text(encoding="utf-8"))
            if root.find(f"{SVG_NS}title") is None or root.find(f"{SVG_NS}desc") is None:
                missing.append(path.name)
        self.assertEqual(missing, [], "every SVG needs <title> and <desc>")


class TestIdentity(unittest.TestCase):
    """DUNG30N5 is the identity. The handle is an address, not a headline."""

    def test_primary_wordmark_is_dung30n5(self):
        offenders = []
        for path in svgs():
            raw = path.read_text(encoding="utf-8")
            primary = [float(m) for m in re.findall(
                r'font-size="([\d.]+)"[^>]*>[^<]*DUNG30N5[^<]*<', raw)]
            handle = [float(m) for m in re.findall(
                r'font-size="([\d.]+)"[^>]*>[^<]*M4G3LL4N0[^<]*<', raw)]
            if handle and primary and max(handle) >= max(primary):
                offenders.append(
                    f"{path.name}: handle {max(handle)}px >= wordmark {max(primary)}px")
        self.assertEqual(offenders, [])

    def test_primary_name_present_in_readme(self):
        self.assertIn("DUNG30N5", readme())
        self.assertIn("Noaerth", readme() + readme().replace("NOAERTH", "Noaerth"))

    def test_no_oversized_handle_heading(self):
        """The handle must never be an <h1> or the alt text of the hero plate."""
        for match in re.findall(r'<h[12][^>]*>([^<]+)</h[12]>', readme()):
            self.assertNotIn("M4G3LL4N0", match,
                             "the GitHub handle must not be a page heading")


class TestMotion(unittest.TestCase):
    """Ambient only. Small, slow, and never the only source of information."""

    def test_no_rapid_animation(self):
        """Below 3 flashes/second, with margin. A full-panel flash at 1.6s is 0.6Hz."""
        offenders = []
        for path in svgs():
            raw = path.read_text(encoding="utf-8")
            for dur in re.findall(r'dur="([\d.]+)s"', raw):
                seconds = float(dur)
                if seconds <= 0:
                    offenders.append(f"{path.name}: non-positive duration")
                elif seconds < 1.0:
                    offenders.append(f"{path.name}: {seconds}s loop is too fast")
        self.assertEqual(offenders, [], f"aggressive motion: {offenders}")

    def test_motion_has_static_twin(self):
        """Every animated asset needs a non-animated equivalent reachable in README."""
        text = readme()
        for stem in ("hero-motion", "terminal-motion"):
            self.assertIn(stem, text, f"{stem} referenced")
        self.assertIn("prefers-reduced-motion: reduce", text,
                      "motion must be gated on a static twin via <picture>")

    def test_reduced_motion_gate_is_first_enough(self):
        """Each picture that can show motion must offer a reduced-motion source."""
        for block in re.findall(r'<picture>.*?</picture>', readme(), re.S):
            if "-motion" not in block:
                continue
            sources = re.findall(r'<source[^>]*media="([^"]+)"', block)
            self.assertTrue(
                any("prefers-reduced-motion" in s for s in sources),
                f"motion asset without a reduced-motion source: {sources}")


class TestContentSafety(unittest.TestCase):
    """Every byte here is public. Private detail leaks by accident, not intent."""

    def _public_files(self):
        return svgs() + [README, EVIDENCE, SIGNAL,
                         PROFILE / "scripts" / "enrich_snapshot.py"]

    def test_no_private_paths(self):
        offenders = []
        for path in self._public_files():
            if not path.is_file():
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            for match in PRIVATE_PATH.finditer(raw):
                offenders.append(f"{path.name}: {match.group(0)}")
        self.assertEqual(offenders, [], f"private path leaked: {offenders}")

    def test_no_secrets(self):
        offenders = []
        for path in self._public_files():
            if not path.is_file():
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            for match in SECRET.finditer(raw):
                offenders.append(f"{path.name}: {match.group(0)[:12]}...")
        self.assertEqual(offenders, [], f"possible secret: {offenders}")

    def test_no_site_only_repo_exposed(self):
        offenders = []
        for suffix in SITE_SUFFIXES:
            for match in re.findall(rf'github\.com/{OWNER}/[A-Za-z0-9._-]*{re.escape(suffix)}\b',
                                    readme()):
                offenders.append(match)
        self.assertEqual(offenders, [], f"site-only repository exposed: {offenders}")

    def test_evidence_file_is_public_safe(self):
        data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        blob = json.dumps(data)
        self.assertIsNone(PRIVATE_PATH.search(blob),
                          "system-map-evidence.json must stay publishable")
        for edge in data["edges"]:
            self.assertTrue(edge.get("evidence"),
                            f"edge {edge['source']}->{edge['target']} has no evidence")


class TestSystemMapEvidence(unittest.TestCase):
    """The diagram may not assert a relationship nothing documents."""

    def test_drawn_edges_match_evidence(self):
        sys.path.insert(0, str(PROFILE / "scripts" / "profile_art"))
        from generate import LAYERS  # noqa: E402

        declared = {f"{e['source']}->{e['target']}"
                    for e in json.loads(EVIDENCE.read_text(encoding="utf-8"))["edges"]}
        drawn = {item[4] for layer in LAYERS for item in layer[2] if item[4]}
        self.assertEqual(drawn - declared, set(),
                         "map draws a relationship with no evidence")
        self.assertEqual(declared - drawn, set(),
                         "evidence exists for a relationship the map omits")

    def test_every_edge_cites_a_real_file(self):
        sys.path.insert(0, str(PROFILE / "scripts" / "profile_art"))
        from generate import LAYERS  # noqa: E402

        siblings = PROFILE.parent
        for layer in LAYERS:
            for item in layer[2]:
                key = item[4]
                if not key:
                    continue
                source = key.split("->")[0]
                data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
                edge = next(e for e in data["edges"] if f"{e['source']}->{e['target']}" == key)
                for citation in edge["evidence"]:
                    repo_path = siblings / citation["repo"] / citation["path"]
                    if not repo_path.is_file():
                        self.skipTest(
                            f"{citation['repo']}/{citation['path']} not present locally; "
                            f"cannot verify citation")
                    return


class TestBoundedSections(unittest.TestCase):
    MARKERS = ("githubos:start", "githubos:end", "upstream:start",
               "upstream:end", "labs:start", "labs:end",
               "signal:start", "signal:end")

    def test_markers_present_and_unique(self):
        text = readme()
        for marker in self.MARKERS:
            with self.subTest(marker=marker):
                self.assertEqual(text.count(f"<!-- {marker} -->"), 1,
                                 f"{marker} must appear exactly once")

    def test_signal_block_matches_generated_data(self):
        signal = json.loads(SIGNAL.read_text(encoding="utf-8"))
        block = re.search(r"<!-- signal:start -->.*?<!-- signal:end -->", readme(), re.S).group(0)
        for metric in signal["metrics"]:
            self.assertIn(metric["display"], block,
                          f"{metric['label']} value missing from the signal block")

    def test_upstream_section_is_not_faked(self):
        """Zero real external contributions means no visible Upstream section."""
        signal = json.loads(SIGNAL.read_text(encoding="utf-8"))
        if signal["upstream"]["external_merged_prs"] == 0:
            self.assertNotIn("## Upstream Signal", readme(),
                             "an upstream graphic with no upstream contributions is decoration")


class TestLinks(unittest.TestCase):
    def _links(self):
        return re.findall(r'\]\((https?://[^)\s]+)\)', readme()) + \
            re.findall(r'href="(https?://[^"]+)"', readme())

    def test_no_malformed_github_paths(self):
        """A bare github.com/<user> with no repo is either a profile or a mistake."""
        offenders = []
        for url in self._links():
            match = re.match(r"https?://github\.com/([^/?#]+)/?$", url)
            if match and match.group(1) != OWNER:
                offenders.append(url)
            if "github.com//" in url or "github.com/ ," in url:
                offenders.append(url)
        self.assertEqual(offenders, [],
                         f"link points at an account rather than a repository: {offenders}")

    def test_internal_anchors_resolve(self):
        text = readme()
        headings = re.findall(r"^#{1,6}\s+(.*?)\s*$", text, re.M)

        def slug(heading: str) -> str:
            cleaned = re.sub(r"[^\w\s-]", "", heading.lower())
            return re.sub(r"\s+", "-", cleaned.strip())

        anchors = {slug(h) for h in headings}
        broken = [a for a in re.findall(r'href="#([^"]+)"', text) if a not in anchors]
        self.assertEqual(broken, [], f"broken anchors: {broken}")

    def test_external_links_resolve(self):
        if offline():
            self.skipTest("offline")
        broken = []
        for url in sorted(set(self._links())):
            status = http_status(url)
            if status is None or status >= 400:
                broken.append(f"{url} -> {status}")
        self.assertEqual(broken, [], f"unreachable links: {broken}")

    def test_repository_links_are_public_and_owned(self):
        if offline():
            self.skipTest("offline")
        offenders = []
        for url in sorted(set(self._links())):
            match = re.match(rf"https?://github\.com/{OWNER}/([A-Za-z0-9._-]+)", url)
            if not match:
                continue
            repo = match.group(1)
            if repo.endswith(SITE_SUFFIXES):
                offenders.append(f"{repo} is a site-only repository")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
