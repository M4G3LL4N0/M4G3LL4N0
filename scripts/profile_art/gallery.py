#!/usr/bin/env python3
"""Dossier gallery: see every project's identity before it ships.

The brief asks for a local-only gallery showing, per repository: venture card
summary, local source summary, category, primary visual metaphor, animation
concept, terminal concept, colour and material, and a hero wireframe. The point
is to catch a bad adaptation BEFORE implementation, so this renders from the
committed dossier and identity files -- the same inputs the generator reads --
and embeds the generated hero rather than describing it.

Every panel is annotated with its evidence. A viewer can see, per project, which
file each claim came from, which is what makes a wrong claim findable rather
than merely visible.

Local-only by construction: the gallery reads local files and writes one HTML
file. It fetches nothing.

  python3 scripts/profile_art/gallery.py
  python3 scripts/profile_art/gallery.py --out GITHUB_V6_DOSSIER_GALLERY.html
  python3 scripts/profile_art/gallery.py --family ORCHESTRATION
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROFILE / "scripts" / "profile_art"))

import repo_art as RA  # noqa: E402

DOSSIER_DIR = PROFILE / ".github-art" / "dossiers"
IDENTITY = PROFILE / ".github-art" / "identity.json"
DEFAULT_OUT = PROFILE / "GITHUB_V6_DOSSIER_GALLERY.html"

CSS = """
:root{--bg:#0a0d12;--panel:#10141b;--edge:#1d2430;--ink:#f4efe4;--dim:#9aa6b8;
--faint:#5d6a7d;--mint:#7fd1c1;--violet:#9d8bd6;--gold:#e7c27a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif}
header{padding:40px 32px 24px;border-bottom:1px solid var(--edge)}
h1{margin:0 0 6px;font-size:30px;letter-spacing:-.6px;font-weight:660}
.sub{color:var(--dim);font-size:14px;max-width:78ch}
.stats{display:flex;flex-wrap:wrap;gap:22px;margin-top:22px}
.stat{background:var(--panel);border:1px solid var(--edge);border-radius:12px;
padding:12px 16px;min-width:132px}
.stat b{display:block;font-size:24px;font-weight:660;letter-spacing:-.5px}
.stat span{color:var(--faint);font-size:11px;letter-spacing:1.4px;text-transform:uppercase}
.filters{padding:18px 32px;display:flex;flex-wrap:wrap;gap:8px;
border-bottom:1px solid var(--edge);position:sticky;top:0;background:var(--bg);z-index:5}
.filters a{color:var(--dim);text-decoration:none;border:1px solid var(--edge);
border-radius:999px;padding:5px 13px;font-size:12.5px}
.filters a:hover{border-color:var(--mint);color:var(--mint)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));
gap:20px;padding:26px 32px 60px}
.card{background:var(--panel);border:1px solid var(--edge);border-radius:14px;
overflow:hidden;display:flex;flex-direction:column}
.card figure{margin:0;background:#07090d;border-bottom:1px solid var(--edge)}
.card figure img{display:block;width:100%;height:auto}
.body{padding:16px 18px 18px;display:flex;flex-direction:column;gap:11px;flex:1}
h2{margin:0;font-size:19px;font-weight:660;letter-spacing:-.3px}
.kicker{font:11px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:2px;
color:var(--faint);text-transform:uppercase}
.kicker em{color:var(--mint);font-style:normal}
dl{margin:0;display:grid;grid-template-columns:104px 1fr;gap:5px 12px;font-size:13px}
dt{color:var(--faint);font-size:11px;letter-spacing:.9px;text-transform:uppercase;
padding-top:2px}
dd{margin:0;color:var(--dim)}
dd.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{border:1px solid var(--edge);border-radius:6px;padding:2px 8px;
font-size:11.5px;color:var(--dim)}
.tag.warn{border-color:#4a3a1f;color:var(--gold)}
.tag.mint{border-color:#1f443c;color:var(--mint)}
.ev{border-top:1px solid var(--edge);padding-top:10px;margin-top:auto;
font:11px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--faint);
word-break:break-all}
.unres{color:var(--gold);font-size:12px}
.empty{color:var(--faint);font-style:italic}
.foot{padding:20px 32px 50px;color:var(--faint);font-size:12.5px;
border-top:1px solid var(--edge)}
"""


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def dd(value, mono: bool = False) -> str:
    if not value:
        return '<dd class="empty">not derivable from source</dd>'
    cls = ' class="mono"' if mono else ""
    return f"<dd{cls}>{esc(value)}</dd>"


def dd_list(items) -> str:
    items = [i for i in (items or []) if i]
    if not items:
        return '<dd class="empty">none</dd>'
    out = "".join(f'<span class="tag">{esc(i)}</span>' for i in items[:8])
    return f"<dd><div class='tags'>{out}</div></dd>"


def venture_summary(d: dict) -> str:
    bits = []
    if d.get("noaerth_category"):
        bits.append(d["noaerth_category"])
    if d.get("venture_stage"):
        bits.append(d["venture_stage"])
    return " · ".join(bits) or "no public card"


def wireframe(d: dict, ident: dict) -> str:
    """A textual wireframe of the plate, so the layout is reviewable as text."""
    stages = RA.stages_for(d, ident["family"])
    rows = ["┌" + "─" * 46 + "┐"]
    rows.append(f"│ {ident['family'][:44]:<44} │")
    rows.append("│" + " " * 46 + "│")
    rows.append(f"│ {(d.get('canonical_name') or '')[:44]:<44} │")
    rows.append("│" + " " * 46 + "│")
    for s in stages[:4]:
        rows.append(f"│ [{s[:20]:<20}]" + " " * 24 + "│")
    rows.append("│" + " " * 46 + "│")
    rows.append(f"│ {ident['topology']} / {ident['depth']:<18}        │")
    rows.append("└" + "─" * 46 + "┘")
    return "\n".join(rows)


def panel(d: dict, ident: dict) -> str:
    name = d.get("github_repo", "?")
    family = ident["family"]
    motion_hero = RA.render(d, ident, "motion")
    static_hero = RA.render(d, ident, "dark")
    # The dark plate is inlined so the panel is readable at a glance; the animated
    # one is a download link, because inlining 126 animated SVGs makes the page
    # unusable and a reviewer who wants motion should see it full size anyway.
    static_b64 = base64.b64encode(static_hero.encode()).decode()
    motion_uri = "data:image/svg+xml;base64," + base64.b64encode(
        motion_hero.encode()).decode()

    stages = RA.stages_for(d, family)
    cmds = d.get("verified_commands") or []
    unres = d.get("unresolved") or []

    ev = d.get("evidence") or {}
    evidence = " · ".join(filter(None, [
        ev.get("arch_doc", ""), ev.get("manifest", ""),
        os.path.basename(ev.get("source_a_local", "")) if ev.get("source_a_local") else "",
    ]))

    return f"""
<article class="card" id="{esc(name)}">
  <figure>
    <img src="data:image/svg+xml;base64,{static_b64}"
         alt="{esc(name)} hero plate, static dark variant" loading="lazy">
  </figure>
  <div class="body">
    <div>
      <div class="kicker">{esc(d.get('project_category',''))} · <em>{esc(family)}</em></div>
      <h2>{esc(d.get('canonical_name') or name)}</h2>
    </div>
    <dl>
      <dt>venture card</dt>{dd(venture_summary(d))}
      <dt>problem</dt>{dd((d.get('problem') or '')[:240])}
      <dt>who for</dt>{dd((d.get('primary_user') or '')[:180])}
      <dt>architecture</dt>{dd(d.get('architecture_type'), True)}
      <dt>data flow</dt>{dd((d.get('data_flow') or '')[:160], True)}
      <dt>interfaces</dt>{dd_list(d.get('interfaces'))}
      <dt>components</dt>{dd_list([c.split(' — ')[0] for c in (d.get('major_components') or [])])}
      <dt>metaphor</dt>{dd(d.get('primary_visual_metaphor'))}
      <dt>animation</dt>{dd(d.get('animation_metaphor'))}
      <dt>stages</dt>{dd_list(stages)}
      <dt>terminal</dt>{dd_list([c['command'] for c in cmds])}
      <dt>material</dt>{dd(ident['material'], True)}
      <dt>geometry</dt>{dd(f"{ident['topology']} / {ident['depth']} / {ident['motif']}", True)}
      <dt>colour</dt>{dd_list([ident['accent']])}
    </dl>
    <pre class="ev">{esc(wireframe(d, ident))}</pre>
    {f'<div class="unres">unresolved: {esc(", ".join(unres))}</div>' if unres else ''}
    <div class="tags">
      <a class="tag mint" href="{esc(motion_uri)}" download="{esc(name)}-hero-motion.svg">animated plate</a>
      <span class="tag">{esc(d.get('design_version',''))}</span>
      <span class="tag">basis: {esc(ident['family_basis'][:46])}</span>
    </div>
    <div class="ev">{esc(evidence)}</div>
  </div>
</article>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--family")
    args = ap.parse_args()

    idents = json.loads(IDENTITY.read_text())["identities"]
    dossiers = {}
    for p in sorted(DOSSIER_DIR.glob("*.json")):
        d = json.loads(p.read_text())
        dossiers[d.get("github_repo", p.stem)] = d

    rows = []
    for repo, d in dossiers.items():
        ident = idents.get(repo)
        if not ident:
            continue
        if args.family and ident["family"] != args.family:
            continue
        rows.append((repo, d, ident))
    rows.sort(key=lambda r: (r[2]["family"], r[0].lower()))

    fam_count = Counter(i["family"] for _, _, i in rows)
    cat_count = Counter(d.get("project_category", "") for _, d, _ in rows)
    mot_count = Counter(i["motif"] for _, _, i in rows)
    mat_count = Counter(i["material"] for _, _, i in rows)
    with_cli = sum(1 for _, d, _ in rows if d.get("verified_commands"))
    with_card = sum(1 for _, d, _ in rows if d.get("noaerth_category"))
    unresolved_total = sum(len(d.get("unresolved") or []) for _, d, _ in rows)

    filters = ['<a href="#">all %d</a>' % len(rows)]
    for f, n in fam_count.most_common():
        filters.append(f'<a href="#">{esc(f.lower().replace("_","-"))} {n}</a>')

    parts = [f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GITHUB V6 — project dossier gallery</title>
<style>{CSS}</style></head><body>
<header>
<h1>GITHUB V6 — project dossier gallery</h1>
<p class="sub">Every panel is generated from the committed dossier and identity,
which are the same inputs the art generator reads. Each claim carries its
evidence, so a wrong adaptation is findable rather than merely visible. Rendered
from local files; this page fetches nothing.</p>
<div class="stats">
<div class="stat"><b>{len(rows)}</b><span>projects</span></div>
<div class="stat"><b>{len(fam_count)}</b><span>families</span></div>
<div class="stat"><b>{len(cat_count)}</b><span>categories</span></div>
<div class="stat"><b>{len(mot_count)}</b><span>motifs</span></div>
<div class="stat"><b>{len(mat_count)}</b><span>materials</span></div>
<div class="stat"><b>{with_cli}</b><span>verified CLIs</span></div>
<div class="stat"><b>{with_card}</b><span>venture cards</span></div>
<div class="stat"><b>{unresolved_total}</b><span>unresolved fields</span></div>
</div>
</header>
<div class="filters">{''.join(filters)}</div>
<div class="grid">"""]

    for repo, d, ident in rows:
        parts.append(panel(d, ident))

    parts.append(f"""</div>
<div class="foot">
Families: {', '.join(f'{esc(k)} {v}' for k, v in fam_count.most_common())}<br>
Categories: {', '.join(f'{esc(k) or "(none)"} {v}' for k, v in cat_count.most_common())}
</div></body></html>""")

    out = Path(args.out)
    out.write_text("".join(parts), encoding="utf-8")
    print(f"gallery: {len(rows)} panels -> {out.relative_to(PROFILE)}")
    print(f"  families {len(fam_count)} · motifs {len(mot_count)} · "
          f"materials {len(mat_count)} · verified CLIs {with_cli}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
