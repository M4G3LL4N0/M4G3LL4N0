#!/usr/bin/env python3
"""V7 public universe map: a technical topology, not an economic chart.

Clusters by technical domain derived from each project's dossier: agents,
developer tools, infrastructure, security, quant and data, research, creative
computing, systems, applications, labs.

Sized by engineering evidence rather than importance, and labelled so no one
reads cluster proximity as a runtime dependency. The clusters are semantic
categories of work, not a dependency graph, and the plate says so.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
DOSSIERS = PROFILE / ".github-art" / "dossiers"
OUT = PROFILE / "assets" / "profile"

W, H = 1280, 760
PALETTE = {
    "dark": {
        "canvas": "#0a0d12", "ink": "#f4efe4", "dim": "#f4efe4a8",
        "faint": "#f4efe45c", "edge": "#f4efe424",
        "AGENTS": "#7fd1c1", "DEVELOPER TOOLS": "#6fb7d6",
        "INFRASTRUCTURE": "#8fa8e0", "SECURITY": "#e0796b",
        "QUANT / DATA": "#e7c27a", "RESEARCH": "#9d8bd6",
        "CREATIVE COMPUTING": "#d68fb0", "SYSTEMS": "#7fbf9a",
        "APPLICATIONS": "#a8b0bd", "LABS": "#6b7280",
    },
    "light": {
        "canvas": "#f7f5f0", "ink": "#141a20", "dim": "#141a20a8",
        "faint": "#141a205c", "edge": "#141a2024",
        "AGENTS": "#2f8f7f", "DEVELOPER TOOLS": "#2b7ea3",
        "INFRASTRUCTURE": "#41568f", "SECURITY": "#a8463a",
        "QUANT / DATA": "#8a6414", "RESEARCH": "#5f4a99",
        "CREATIVE COMPUTING": "#8f4763", "SYSTEMS": "#3d7a58",
        "APPLICATIONS": "#5a636f", "LABS": "#6b7280",
    },
}
DOMAIN = {
    "AGENT": "AGENTS", "SECURITY": "SECURITY", "FINANCE": "QUANT / DATA",
    "QUANT": "QUANT / DATA", "DATA": "QUANT / DATA",
    "DEVELOPER_TOOLS": "DEVELOPER TOOLS", "INFRASTRUCTURE": "INFRASTRUCTURE",
    "NETWORK": "INFRASTRUCTURE", "CREATIVE": "CREATIVE COMPUTING",
    "LAB": "LABS", "GENERAL": "APPLICATIONS",
}


def layout(domains: dict[str, int], cx: float, cy: float, r: float):
    """Ring the clusters, larger domains further out, no overlap."""
    items = sorted(domains.items(), key=lambda kv: -kv[1])
    n = len(items)
    out = {}
    for i, (name, count) in enumerate(items):
        a = (i / n) * math.tau - math.pi / 2
        out[name] = (cx + math.cos(a) * r, cy + math.sin(a) * r, count)
    return out


def main() -> int:
    dossiers = [json.loads(f.read_text(encoding="utf-8"))
                for f in sorted(DOSSIERS.glob("*.json"))]
    counts: dict[str, int] = {}
    for d in dossiers:
        k = DOMAIN.get(d.get("project_category", "GENERAL"), "APPLICATIONS")
        counts[k] = counts.get(k, 0) + 1
    if not counts:
        print("no dossiers")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    for theme, pal in PALETTE.items():
        cx, cy, r = W / 2, 400, 250
        pos = layout(counts, cx, cy, r)
        p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'width="{W}" height="{H}" role="img" '
             f'aria-label="Technical domain map of {len(dossiers)} public systems '
             f'across {len(counts)} domains: ' +
             ", ".join(f"{k} {v}" for k, v in sorted(counts.items(),
                                                     key=lambda kv: -kv[1])) +
             '. Clusters are semantic categories of work, not runtime dependencies.">',
             '<title>Public universe \u2014 technical domains</title>',
             '<desc>Systems clustered by technical domain derived from each '
             'project\u2019s architecture and category. Cluster position and '
             'proximity carry no dependency meaning; these are categories of '
             'work.</desc>',
             f'<rect width="{W}" height="{H}" fill="{pal["canvas"]}"/>']

        p.append(f'<text x="64" y="70" fill="{pal["ink"]}" font-size="34" '
                 f'font-weight="660" letter-spacing="-0.8">Public universe</text>')
        p.append(f'<text x="64" y="102" fill="{pal["dim"]}" font-size="16">'
                 f'{len(dossiers)} systems \u00b7 {len(counts)} technical domains '
                 f'\u00b7 clustered by what they compute, not what they are '
                 f'worth</text>')

        # Node field: one mark per dossier, positioned by domain cluster.
        by_domain: dict[str, list] = {}
        for d in dossiers:
            k = DOMAIN.get(d.get("project_category", "GENERAL"), "APPLICATIONS")
            by_domain.setdefault(k, []).append(d)

        for name, (dx, dy, count) in pos.items():
            colour = pal.get(name, pal["dim"])
            members = by_domain.get(name, [])
            # cluster hull
            p.append(f'<circle cx="{dx:.0f}" cy="{dy:.0f}" '
                     f'r="{34 + count * 1.5:.0f}" fill="{colour}" '
                     f'opacity="0.055" stroke="{colour}" stroke-width="1" '
                     f'stroke-opacity="0.28"/>')
            p.append(f'<text x="{dx:.0f}" y="{dy + count * 0.9 + 44:.0f}" '
                     f'fill="{colour}" font-size="11.5" text-anchor="middle" '
                     f'letter-spacing="1.5" font-weight="600">{name}</text>')
            p.append(f'<text x="{dx:.0f}" y="{dy + count * 0.9 + 61:.0f}" '
                     f'fill="{pal["faint"]}" font-size="10.5" '
                     f'text-anchor="middle">{count} systems</text>')
            # individual systems, small marks on a jittered ring
            for i, m in enumerate(members):
                a = (i / max(1, len(members))) * math.tau
                rad = 20 + (i % 5) * 7
                nx = dx + math.cos(a) * rad
                ny = dy + math.sin(a) * rad * 0.72
                p.append(f'<rect x="{nx - 2.4:.1f}" y="{ny - 2.4:.1f}" '
                         f'width="4.8" height="4.8" rx="1.2" fill="{colour}" '
                         f'opacity="0.55"/>')

        p.append(f'<line x1="64" y1="{H - 96}" x2="{W - 64}" y2="{H - 96}" '
                 f'stroke="{pal["edge"]}" stroke-width="1"/>')
        p.append(f'<text x="64" y="{H - 68}" fill="{pal["faint"]}" '
                 f'font-size="12">Semantic portfolio map. Clusters group work by '
                 f'technical domain; proximity is not a runtime dependency and no '
                 f'system here calls another.</text>')
        p.append(f'<text x="64" y="{H - 44}" fill="{pal["faint"]}" '
                 f'font-size="12">Node size is uniform within a cluster; cluster '
                 f'radius reflects how many systems share the domain.</text>')
        p.append('</svg>')
        name = "public-universe-dark.svg" if theme == "dark" else "public-universe-light.svg"
        (OUT / name).write_text("\n".join(p), encoding="utf-8")
        print(f"  {name:<34}{len(dossiers)} systems  {len(counts)} domains")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())