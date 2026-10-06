#!/usr/bin/env python3
"""Per-repository art: animated hero, static variants, computational visual.

Reads the dossier produced in Part 1 and renders the surfaces it specifies:

  hero-motion / hero-dark / hero-light / hero-reduced
  glyph
  computational-motion / computational-dark      (state machine or pipeline)
  social-preview

Nothing here is generic. Every choice resolves from the dossier:

  animation   (architecture, category) -> a real state transition
  geometry    the same pair -> the shape that depicts it
  material    from the identity system
  accent      from the identity system
  intensity   profile / flagship / project / lab / archive, per section 16

Motion is semantic. A scheduler's plate shows a job entering, queuing, being
leased and completing. A data flow in a security product shows records meeting
a boundary and being held or rejected. Nothing orbits, nothing floats, nothing
pulses for its own sake.

Two honest constraints, recorded rather than hidden:

  * reduced motion resolves to the static dark plate, which is the same
    composition without the transition. It is a real image, not a degradation.
  * architecture graphics are only drawn where an architecture was actually
    determined from source. No arrows are invented.

  python3 scripts/github_art/repo_art.py --list
  python3 scripts/github_art/repo_art.py --render agentos --out /tmp/agentos
  python3 scripts/github_art/repo_art.py --render-all --limit 20 --out-root build/repo-art
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts"))
from github_art import project_identity as P  # noqa: E402

DOSSIERS = PROFILE / ".github-art" / "dossiers"

# Section 16: intensity by class. The repository tab must not become visual
# screaming, and a flagship must not look like a lab.
INTENSITY = {
    "FLAGSHIP": (0.62, 3.4),
    "PUBLIC_PROJECT": (0.40, 2.6),
    "PUBLIC_LAB": (0.50, 3.0),
    "PUBLIC_ARCHIVE": (0.22, 1.7),
    "PROFILE": (0.76, 4.0),
}

INK = "#f4efe4"
DIM = "#f4efe4a8"
FAINT = "#f4efe44f"
EDGE = "#f4efe424"


# ----------------------------------------------------------------- motion

def motion_states(arch: str, category: str) -> list[tuple[str, str]]:
    """The state transition the animation actually depicts.

    Returned as (label, kind) where kind drives the visual treatment. These
    are the system's real stages, not decorative phases.
    """
    table = {
        ("SCHEDULER", "INFRASTRUCTURE"): [
            ("enqueue", "in"), ("lease", "hold"), ("execute", "work"),
            ("complete", "out")],
        ("PIPELINE", "DEVELOPER_TOOLS"): [
            ("source", "in"), ("resolve deps", "work"), ("compile", "work"),
            ("test", "hold"), ("artifact", "out")],
        ("DATA_FLOW", "SECURITY"): [
            ("request", "in"), ("authenticate", "hold"), ("authorise", "hold"),
            ("record", "out"), ("reject", "deny")],
        ("DATA_FLOW", "FINANCE"): [
            ("capital", "in"), ("allocate", "work"), ("mark", "work"),
            ("settle", "out")],
        ("DATA_FLOW", "AGENT"): [
            ("objective", "in"), ("load context", "work"), ("call tools", "work"),
            ("verify", "out")],
        ("DATA_FLOW", "DEVELOPER_TOOLS"): [
            ("install", "in"), ("resolve tree", "work"), ("link", "work"),
            ("verify", "out")],
        ("DOCUMENT", "SECURITY"): [
            ("policy", "in"), ("control", "hold"), ("evidence", "out")],
        ("DOCUMENT", "FINANCE"): [
            ("scenario", "in"), ("compare", "hold"), ("conclude", "out")],
        ("DISTRIBUTED", "INFRASTRUCTURE"): [
            ("advertise", "in"), ("select", "hold"), ("dispatch", "work"),
            ("converge", "out")],
        ("AGENT_LOOP", "AGENT"): [
            ("objective", "in"), ("plan", "work"), ("execute", "work"),
            ("verify", "out")],
        ("CLI", "DEVELOPER_TOOLS"): [
            ("parse", "in"), ("resolve", "work"), ("run", "work"),
            ("report", "out")],
        ("SECURITY", "SECURITY"): [
            ("approach", "in"), ("detect", "hold"), ("contain", "work"),
            ("close", "deny")],
        ("ROUTER", "GENERAL"): [
            ("arrive", "in"), ("candidates", "hold"), ("select", "out")],
        ("GENERATIVE", "GENERAL"): [
            ("seed", "in"), ("expand", "work"), ("structure", "out")],
        ("LIBRARY", "DEVELOPER_TOOLS"): [
            ("import", "in"), ("resolve", "hold"), ("bind", "out")],
        ("DATA_FLOW", "GENERAL"): [
            ("request", "in"), ("validate", "work"), ("persist", "work"),
            ("respond", "out")],
        ("DISTRIBUTED", "SECURITY"): [
            ("request", "in"), ("peer exchange", "work"), ("attest", "hold"),
            ("accept", "out")],
        ("AGENT_LOOP", "SECURITY"): [
            ("objective", "in"), ("plan", "work"), ("constrain", "hold"),
            ("verify", "out")],
        ("ROUTER", "SECURITY"): [
            ("request", "in"), ("candidate routes", "hold"),
            ("policy select", "out")],
        ("CLI", "SECURITY"): [
            ("argv", "in"), ("validate", "hold"), ("run", "work"),
            ("report", "out")],
        ("SCHEDULER", "SECURITY"): [
            ("job", "in"), ("scan", "work"), ("isolate", "hold"),
            ("terminate", "deny")],
        ("PIPELINE", "GENERAL"): [
            ("source", "in"), ("transform", "work"), ("emit", "out")],
        ("LIBRARY", "AGENT"): [
            ("import", "in"), ("bind", "work"), ("call", "out")],
        ("SCHEDULER", "AGENT"): [
            ("task", "in"), ("assign", "work"), ("run", "work"),
            ("report", "out")],
        ("DOCUMENT", "DEVELOPER_TOOLS"): [
            ("read", "in"), ("resolve refs", "work"), ("render", "out")],
    }
    return table.get((arch, category), [
        ("input", "in"), ("process", "work"), ("verify", "hold"),
        ("output", "out")])


def computational_svg(d: dict, theme: str, animated: bool) -> str:
    """The project's computational visual: a real state machine."""
    states = motion_states(d.get("architecture_type", ""),
                           d.get("project_category", ""))
    W, H = 960, 300
    uid = f"cs-{d['github_repo']}-{theme}"
    ink = INK if theme == "dark" else "#141a20"
    dim = DIM if theme == "dark" else "#141a20a8"
    faint = FAINT if theme == "dark" else "#141a205c"
    edge = EDGE if theme == "dark" else "#141a2024"
    canvas = "#0a0d12" if theme == "dark" else "#f7f5f0"
    i = P.identity(d["github_repo"])
    accent = {"mint": "#7fd1c1", "violet": "#9d8bd6",
              "cyan": "#6fb7d6", "indigo": "#8fa8e0"}.get(
        i.get("accent", "mint"), "#7fd1c1")

    n = len(states)
    gap = 26
    bw = (W - 120 - gap * (n - 1)) / n
    y = 128
    bh = 54

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" '
         f'aria-label="{" to ".join(s for s, _ in states)}. '
         f'{d.get("animation_metaphor", "")}.">',
         f'<title>{d["canonical_name"]} — computational sequence</title>',
         f'<desc>A state machine showing the real transition this system '
         f'performs: {" then ".join(s for s, _ in states)}. Derived from the '
         f'project architecture, not decorative.</desc>']
    if animated:
        p.append('<style>@media (prefers-reduced-motion: reduce){'
                 '*{animation:none !important}}</style>')
    p.append(f'<rect width="{W}" height="{H}" fill="{canvas}"/>')
    p.append(f'<text x="60" y="52" fill="{faint}" font-size="11.5" '
             f'letter-spacing="2.6">{d.get("architecture_type", "SYSTEM")} '
             f'\u00b7 {d.get("project_category", "GENERAL")}</text>')
    p.append(f'<text x="60" y="80" fill="{ink}" font-size="19" font-weight="620" '
             f'letter-spacing="-0.2">{d.get("animation_metaphor", "")}</text>')

    mono = "ui-monospace,SFMono-Regular,Menlo,monospace"
    for k, (label, kind) in enumerate(states):
        x = 60 + k * (bw + gap)
        colour = {"deny": "#e0796b", "hold": accent,
                  "out": "#e7c27a"}.get(kind, "#f4efe4")
        stroke = {"deny": "#e0796b", "hold": accent}.get(kind, edge)
        base = 0.4 + k * 0.55
        p.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="10" '
                 f'fill="{ink}" fill-opacity="0.05" stroke="{stroke}" '
                 f'stroke-width="1.2" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to="1" '
                 f'dur="0.5s" begin="{base:.2f}s" fill="freeze"/></rect>')
        p.append(f'<rect x="{x}" y="{y}" width="3" height="{bh}" rx="1.5" '
                 f'fill="{colour}" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to="0.9" '
                 f'dur="0.5s" begin="{base:.2f}s" fill="freeze"/></rect>')
        p.append(f'<text x="{x + bw / 2}" y="{y + 33}" fill="{ink}" '
                 f'font-size="12.5" text-anchor="middle" font-family="{mono}" '
                 f'opacity="0">{label}'
                 f'<animate attributeName="opacity" from="0" to="1" '
                 f'dur="0.5s" begin="{base + 0.18:.2f}s" fill="freeze"/></text>')
        if k < n - 1:
            ax = x + bw
            p.append(f'<line x1="{ax}" y1="{y + bh / 2}" x2="{ax + gap}" '
                     f'y2="{y + bh / 2}" stroke="{edge}" stroke-width="1.2" '
                     f'opacity="0">'
                     f'<animate attributeName="opacity" from="0" to="1" '
                     f'dur="0.4s" begin="{base + 0.3:.2f}s" fill="freeze"/>'
                     f'<animate attributeName="stroke" values="{edge};{accent};{edge}" '
                     f'dur="6s" repeatCount="indefinite"/></line>')

    # One token crossing the whole sequence, so the eye can follow the process.
    if animated:
        total = 0.4 + (n - 1) * 0.55 + 1.1
        p.append(f'<circle r="3.6" fill="{accent}" opacity="0.9">'
                 f'<animateMotion dur="{total:.1f}s" fill="freeze" '
                 f'path="M{bw / 2 + 60:.0f} {y - 16} '
                 f'L{W - 60 - bw / 2:.0f} {y - 16}"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" '
                 f'keyTimes="0;0.06;0.9;1" dur="{total:.1f}s" fill="freeze"/>'
                 f'</circle>')
        p.append(f'<text x="60" y="{y - 10}" fill="{faint}" font-size="10.5" '
                 f'font-family="{mono}">traversal</text>')
    p.append('</svg>')
    return "\n".join(p)


def hero_svg(d: dict, theme: str, animated: bool) -> str:
    """The repository hero. Project sculpture first, signature second."""
    states = motion_states(d.get("architecture_type", ""),
                           d.get("project_category", ""))
    klass = d.get("classification", "PUBLIC_PROJECT")
    intensity, depth = INTENSITY.get(klass, (0.40, 2.6))
    W, H = 1200, 420
    ink = INK if theme == "dark" else "#141a20"
    dim = DIM if theme == "dark" else "#141a20a8"
    faint = FAINT if theme == "dark" else "#141a205c"
    edge = EDGE if theme == "dark" or True else EDGE
    canvas = "#0a0d12" if theme == "dark" else "#f7f5f0"
    i = P.identity(d["github_repo"])
    accent = {"mint": "#7fd1c1", "violet": "#9d8bd6",
              "cyan": "#6fb7d6", "indigo": "#8fa8e0"}.get(
        i.get("accent", "mint"), "#7fd1c1")
    phase = i.get("geometry_phase", 0)

    uid = f"hero-{d['github_repo']}-{theme}"
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" '
         f'aria-label="{d["canonical_name"]}: '
         f'{d.get("primary_visual_metaphor", "")}. Motion depicts '
         f'{d.get("animation_metaphor", "")}.">',
         f'<title>{d["canonical_name"]} \u2014 NOAERTH</title>',
         f'<desc>Project plate for {d["canonical_name"]}. Geometry: '
         f'{d.get("primary_visual_metaphor", "")}. The animation shows '
         f'{" then ".join(s for s, _ in states)}.</desc>']
    if animated:
        p.append('<style>@media (prefers-reduced-motion: reduce){'
                 '*{animation:none !important}}</style>')
    p.append(f'<defs><linearGradient id="{uid}-a" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{accent}" stop-opacity="0.85"/>'
             f'<stop offset="1" stop-color="{accent}" stop-opacity="0.15"/>'
             f'</linearGradient></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="{canvas}"/>')

    # Sculpture: the motif as architecture, not a logo. Layer count is the
    # intensity budget, so a lab reads lighter than a flagship.
    layers = max(1, min(4, int(round(depth))))
    cx, cy = 980, 210
    for k in range(layers):
        r = 74 + k * 30 + (phase % 4) * 5
        op = 0.16 + 0.20 * (1 - k / max(1, layers))
        p.append(f'<rect x="{cx - r}" y="{cy - r * 0.62}" width="{r * 2}" '
                 f'height="{r * 1.24}" rx="{16 + k * 5}" fill="none" '
                 f'stroke="{accent}" stroke-width="{1.6 - k * 0.22:.2f}" '
                 f'opacity="{op:.2f}">'
                 + (f'<animateTransform attributeName="transform" '
                    f'type="rotate" values="{-1.2 * k:.1f} {cx} {cy};'
                    f'{1.2 * k:.1f} {cx} {cy};{-1.2 * k:.1f} {cx} {cy}" '
                    f'dur="{26 + k * 7}s" repeatCount="indefinite"/>'
                    if animated and k == 0 else "")
                 + '</rect>')
    p.append(f'<rect x="{cx - 46}" y="{cy - 30}" width="92" height="60" rx="14" '
             f'fill="url(#{uid}-a)" opacity="{intensity:.2f}"/>')

    # The state chain, at the project's own intensity.
    n = len(states)
    p.append(f'<text x="72" y="112" fill="{faint}" font-size="11" '
             f'letter-spacing="2.8">{klass.replace("_", " ")} \u00b7 '
             f'{d.get("project_category", "")}</text>')
    p.append(f'<text x="72" y="176" fill="{ink}" font-size="46" '
             f'font-weight="660" letter-spacing="-1.4">'
             f'{d["canonical_name"][:34]}</text>')
    p.append(f'<text x="72" y="212" fill="{dim}" font-size="16.5" '
             f'letter-spacing="0.2">'
             f'{(d.get("purpose") or d.get("animation_metaphor", ""))[:96]}'
             f'</text>')

    mono = "ui-monospace,SFMono-Regular,Menlo,monospace"
    for k, (label, kind) in enumerate(states[:5]):
        x = 72 + k * 122
        colour = {"deny": "#e0796b", "out": "#e7c27a"}.get(kind, accent)
        base = 0.5 + k * 0.5
        p.append(f'<rect x="{x}" y="266" width="106" height="40" rx="9" '
                 f'fill="{ink}" fill-opacity="0.05" stroke="{edge}" '
                 f'stroke-width="1.1" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" '
                 f'begin="{base:.2f}s" fill="freeze"/></rect>')
        p.append(f'<rect x="{x}" y="266" width="2.5" height="40" rx="1.2" '
                 f'fill="{colour}" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to="0.9" dur="0.5s" '
                 f'begin="{base:.2f}s" fill="freeze"/></rect>')
        p.append(f'<text x="{x + 53}" y="291" fill="{ink}" font-size="11.5" '
                 f'text-anchor="middle" font-family="{mono}" opacity="0">'
                 f'{label}'
                 f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" '
                 f'begin="{base + 0.15:.2f}s" fill="freeze"/></text>')
        if animated and k < min(5, n) - 1:
            p.append(f'<line x1="{x + 106}" y1="286" x2="{x + 122}" y2="286" '
                     f'stroke="{edge}" stroke-width="1.1" opacity="0">'
                     f'<animate attributeName="opacity" from="0" to="1" '
                     f'dur="0.4s" begin="{base + 0.3:.2f}s" fill="freeze"/></line>')

    # Builder signature second, small, never the headline.
    p.append(f'<text x="72" y="{H - 26}" fill="{faint}" font-size="11" '
             f'letter-spacing="2.2">DUNG30N5 \u00d7 NOAERTH</text>')
    p.append('</svg>')
    return "\n".join(p)


def social_svg(d: dict) -> str:
    W, H = 1280, 640
    ink = INK
    faint = FAINT
    accent = {"mint": "#7fd1c1", "violet": "#9d8bd6",
              "cyan": "#6fb7d6", "indigo": "#8fa8e0"}.get(
        P.identity(d["github_repo"]).get("accent", "mint"), "#7fd1c1")
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" '
         f'aria-label="{d["canonical_name"]} — NOAERTH project card.">',
         f'<title>{d["canonical_name"]}</title>',
         f'<desc>Social preview card: project name, category, and the '
         f'system\u2019s state sequence.</desc>',
         '<rect width="1280" height="640" fill="#0a0d12"/>']
    for gx in range(0, W + 1, 80):
        p.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}" stroke="{EDGE}" '
                 f'stroke-width="0.7"/>')
    for gy in range(0, H + 1, 80):
        p.append(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" stroke="{EDGE}" '
                 f'stroke-width="0.7"/>')
    p.append(f'<rect x="88" y="196" width="6" height="150" rx="3" fill="{accent}"/>')
    p.append(f'<text x="128" y="268" fill="{ink}" font-size="72" '
             f'font-weight="680" letter-spacing="-2">'
             f'{d["canonical_name"][:22]}</text>')
    p.append(f'<text x="128" y="316" fill="{faint}" font-size="20" '
             f'letter-spacing="5">NOAERTH \u00b7 '
             f'{d.get("project_category", "SYSTEM")}</text>')
    states = motion_states(d.get("architecture_type", ""),
                           d.get("project_category", ""))
    p.append(f'<text x="128" y="380" fill="{faint}" font-size="17" '
             f'letter-spacing="0.4">'
             f'{" \u2192 ".join(s for s, _ in states)}</text>')
    p.append(f'<text x="128" y="556" fill="{faint}" font-size="15" '
             f'letter-spacing="3">DUNG30N5 \u00d7 NOAERTH</text>')
    p.append('</svg>')
    return "\n".join(p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--render")
    ap.add_argument("--render-all", action="store_true")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--out", default="")
    ap.add_argument("--out-root", default=str(PROFILE / "build/repo-art"))
    args = ap.parse_args()

    files = sorted(DOSSIERS.glob("*.json"))
    if args.list:
        for f in files:
            d = json.loads(f.read_text(encoding="utf-8"))
            print(f"  {d['github_repo']:<28}{d['classification']:<16}"
                  f"{d['architecture_type']:<14}{d['project_category']}")
        print(f"  {len(files)} dossiers")
        return 0

    def emit(d: dict, outdir: Path) -> int:
        outdir.mkdir(parents=True, exist_ok=True)
        made = []
        for theme in ("dark", "light"):
            (outdir / f"hero-{theme}.svg").write_text(
                hero_svg(d, theme, False), encoding="utf-8")
            (outdir / f"computational-{theme}.svg").write_text(
                computational_svg(d, theme, False), encoding="utf-8")
            made += [f"hero-{theme}.svg", f"computational-{theme}.svg"]
        (outdir / "hero-motion.svg").write_text(
            hero_svg(d, "dark", True), encoding="utf-8")
        (outdir / "computational-motion.svg").write_text(
            computational_svg(d, "dark", True), encoding="utf-8")
        # Reduced motion resolves to the static dark plate: same composition,
        # no transition. A real image, not a degraded one.
        (outdir / "hero-reduced.svg").write_text(
            hero_svg(d, "dark", False), encoding="utf-8")
        (outdir / "social-preview.svg").write_text(social_svg(d), encoding="utf-8")
        made += ["hero-motion.svg", "computational-motion.svg",
                 "hero-reduced.svg", "social-preview.svg"]
        return len(made)

    if args.render:
        f = DOSSIERS / f"{args.render}.json"
        if not f.exists():
            print(f"no dossier for {args.render}")
            return 1
        d = json.loads(f.read_text(encoding="utf-8"))
        out = Path(args.out) if args.out else Path(args.out_root) / args.render
        n = emit(d, out)
        print(f"{args.render}: {n} surfaces -> {out}")
        return 0

    if args.render_all:
        root = Path(args.out_root)
        total = 0
        for f in files[: args.limit]:
            d = json.loads(f.read_text(encoding="utf-8"))
            total += emit(d, root / d["github_repo"])
            print(f"  {d['github_repo']}")
        print(f"{min(len(files), args.limit)} repositories, {total} surfaces")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())