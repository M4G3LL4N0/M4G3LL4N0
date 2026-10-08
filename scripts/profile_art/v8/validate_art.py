"""Validate the rendered surface set.

Beyond well-formedness this checks the two failure modes that are invisible in
a diff but obvious on GitHub:

  static frame   GitHub rasterises a README SVG as a still image, so any element
                 animated from opacity 0 is simply missing in the published
                 README. Every surface is therefore re-rendered with motion off
                 and compared for element count.
  unreduced      A reduced-motion variant must contain no animation at all.
"""

from __future__ import annotations

import pathlib
import re
import sys
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import clay_renderers as R  # noqa: E402
import evidence as E  # noqa: E402
import render_art as RA  # noqa: E402

ART = RA.OUT
ANIMATE_RE = re.compile(r"<animate|<animateTransform")
ANIMATE_TAG_RE = re.compile(r"<(?:animate|animateTransform)\b[^>]*/>")


def main() -> int:
    manifest = __import__("json").loads((ART / "manifest.json").read_text())
    index = E.load_index()
    cards = E.load_cards()
    signature = E.template_signature(index)

    xml_bad: list = []
    reduced_bad: list = []
    no_anim: list = []
    static_bad: list = []
    colour_bad: list = []
    total = 0

    for name in sorted(manifest):
        rec = index.get(name)
        if rec is None:
            continue
        d = E.build(name, rec, cards.get(name.lower()), {}, signature)
        art_dir = ART / name
        files = sorted(art_dir.glob("*.svg"))
        total += len(files)

        for f in files:
            body = f.read_text()
            try:
                ET.fromstring(body)
            except Exception as exc:
                xml_bad.append((name, f.name, str(exc)[:60]))
                continue
            n = len(ANIMATE_RE.findall(body))
            if "reduced" in f.name and n:
                reduced_bad.append((name, f.name))
            if "reduced" not in f.name and n == 0:
                no_anim.append((name, f.name))
            # Animation elements carry a SMIL fill="freeze" attribute, which is
            # not a paint; strip them before scanning for paint values.
            paint = ANIMATE_TAG_RE.sub("", body)
            for value in re.findall(r'(?:fill|stroke)="([^"]*)"', paint):
                if value in ("none", "") or value.startswith("url("):
                    continue
                if not re.fullmatch(r"#[0-9a-fA-F]{3,6}|rgba?\([^)]*\)", value):
                    colour_bad.append((name, f.name, value))

        # Static-frame fidelity: the animated and reduced renderings of the same
        # slot must draw the same shapes, or GitHub's still image is incomplete.
        for slot in manifest[name]["slots"]:
            if slot not in R.RENDERERS:
                continue
            moving = R.render(slot, d, name, motion=True)
            still = R.render(slot, d, name, motion=False)
            n_move = len(re.findall(r"<(?:rect|circle|path|ellipse|polygon)\b", moving))
            n_still = len(re.findall(r"<(?:rect|circle|path|ellipse|polygon)\b", still))
            if n_move != n_still:
                static_bad.append((name, slot, n_move, n_still))
            if ANIMATE_RE.search(still):
                static_bad.append((name, slot, "reduced still animates"))

    print(f"  files checked      : {total}")
    print(f"  xml errors         : {len(xml_bad)}")
    print(f"  reduced animates   : {len(reduced_bad)}")
    print(f"  unanimated surfaces: {len(no_anim)}")
    print(f"  static-frame drift : {len(static_bad)}")
    print(f"  invalid colours    : {len(colour_bad)}")
    problems = xml_bad + reduced_bad + no_anim + static_bad + colour_bad
    for p in problems[:10]:
        print(f"    - {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
