#!/usr/bin/env python3
"""Build PROFILE_ART_GALLERY.html — a local review surface for the art system.

Local only. Not deployed, not committed to the public profile repository.

Shows every generated asset in dark and light, at desktop and mobile widths,
plus the motion variants and the avatar studies, so the direction can be judged
before it is wired into the README.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROFILE = HERE.parents[1]
ASSETS = PROFILE / "assets" / "profile"
GALLERY = PROFILE / "PROFILE_ART_GALLERY.html"

MOTION_SIZES = ["hero-motion.svg", "terminal-motion.svg"]


def kb(path: Path) -> str:
    size = path.stat().st_size if path.is_file() else 0
    return f"{size / 1024:.1f} KB" if size else "missing"


def panel(theme: str, src: str, caption: str, width: str = "100%") -> str:
    return f"""
    <figure class="shot {theme}">
      <img src="assets/profile/{src}" alt="{caption}" style="width:{width}">
      <figcaption><span class="t-{theme}">{theme}</span> · {caption}
        <code>{src}</code> · {kb(ASSETS / src)}</figcaption>
    </figure>"""


def main() -> int:
    signal_path = ASSETS / "build-signal.json"
    signal = json.loads(signal_path.read_text(encoding="utf-8")) if signal_path.is_file() else {}
    generated = signal.get("generated_at", "not generated")

    hero = "".join(panel(t, f"hero-{t}.svg", "identity plate") for t in ("dark", "light"))
    nav = "".join(
        panel(t, f"nav/{slug}-{t}.svg", title, width="260px")
        for t in ("dark", "light")
        for slug, title in (("noaerth", "NOAERTH"), ("repositories", "REPOSITORIES"),
                            ("open-source", "OPEN SOURCE"), ("why", "WHY ARE YOU HERE?")))
    cards = "".join(
        panel(t, f"cards/{slug}-{t}.svg", name)
        for t in ("dark", "light")
        for slug, name in (("portfolio-os", "Portfolio OS"), ("agentos", "AgentOS"),
                           ("grokinstall", "GrokInstall"), ("grokmax", "GrokMax"),
                           ("gh0st", "gh0st"), ("opencode-watchdog", "OpenCode Watchdog")))
    maps = "".join(panel(t, f"system-map-{t}.svg", "operating stack")
                   for t in ("dark", "light"))
    sig = "".join(panel(t, f"build-signal-{t}.svg", "build signal (telemetry)")
                  for t in ("dark", "light"))
    term = "".join(panel(t, f"terminal-{t}.svg", "why are you here?")
                   for t in ("dark", "light"))
    motion = "".join(
        panel("dark", name, f"animated · {MOTION_SIZES[i]}")
        for i, name in enumerate(MOTION_SIZES) if (ASSETS / name).is_file())
    avatars = "".join(
        panel("dark", f"avatar/{slug}.svg", name, width="220px")
        for slug, name in (("avatar-monogram", "concept 1 · DUNG30N5 monogram"),
                           ("avatar-node", "concept 2 · spectral node"),
                           ("avatar-hybrid", "concept 3 · Noaerth × DUNG30N5"))
        if (ASSETS / "avatar" / f"{slug}.svg").is_file())
    svg_total = sum(f.stat().st_size for f in ASSETS.rglob("*.svg"))
    motion_total = sum((ASSETS / m).stat().st_size for m in MOTION_SIZES
                       if (ASSETS / m).is_file())

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DUNG30N5 × NOAERTH — profile art gallery</title>
<style>
:root{{color-scheme:light dark;--bg:#f5f6f8;--panel:#fff;--ink:#0d1117;--muted:#5a6572;--line:#d9dee4;--accent:#12a594}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0a0d12;--panel:#111722;--ink:#e6edf3;--muted:#8b949e;--line:#242d38;--accent:#5ee7d0}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
main{{max-width:1320px;margin:0 auto;padding:28px 20px 80px}}
h1{{font-size:clamp(26px,4vw,40px);letter-spacing:-.03em;margin:0 0 4px}}
h2{{font-size:15px;text-transform:uppercase;letter-spacing:.16em;color:var(--muted);margin:44px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}}
p.lede{{color:var(--muted);max-width:70ch;margin:0 0 8px}}
.meta{{font:12px ui-monospace,Menlo,monospace;color:var(--muted);margin-bottom:20px}}
.meta b{{color:var(--accent)}}
.grid{{display:grid;gap:16px}}
.grid.two{{grid-template-columns:1fr 1fr}}
@media(max-width:860px){{.grid.two{{grid-template-columns:1fr}}}}
.shot{{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:12px;overflow:hidden}}
.shot.dark{{background:#0d1117}} .shot.light{{background:#fff}}
.shot img{{display:block;border-radius:6px;height:auto}}
figcaption{{font:11.5px ui-monospace,Menlo,monospace;color:var(--muted);margin-top:9px;display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}}
.t-dark{{color:#5ee7d0}} .t-light{{color:#12a594}}
code{{background:rgba(127,127,127,.16);padding:1px 5px;border-radius:4px}}
.strip{{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-start}}
.avatars{{display:flex;gap:16px;flex-wrap:wrap}}
.phones{{display:flex;gap:20px;flex-wrap:wrap}}
.phone{{width:340px;background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:10px}}
.phone img{{display:block;width:100%;border-radius:8px}}
.phone .cap{{font:11px ui-monospace,Menlo,monospace;color:var(--muted);margin-top:8px;text-align:center}}
ul.notes{{color:var(--muted);max-width:80ch}} ul.notes li{{margin:5px 0}}
</style></head><body><main>

<h1>DUNG30N5 × NOAERTH</h1>
<p class="lede">Profile art system — liquid computing. Local review surface. Not deployed and not
committed to the public profile repository. Every asset is generated from
<code>scripts/profile_art/tokens.py</code>; no colour or radius is hand-written per file.</p>
<div class="meta">signal generated <b>{generated}</b> · static SVG payload <b>{svg_total/1024:.1f} KB</b> ·
animated payload <b>{motion_total/1024:.1f} KB</b></div>

<h2>Hero — recommended: dark on dark theme, light on light theme</h2>
<div class="grid">{hero}</div>

<h2>Liquid-glass navigation</h2>
<div class="strip">{nav}</div>

<h2>Build signal — telemetry, generated from the live API</h2>
<div class="grid">{sig}</div>

<h2>Flagship cards</h2>
<div class="grid two">{cards}</div>

<h2>Operating stack — relationships named only where source or docs cite them</h2>
<div class="grid">{maps}</div>

<h2>Why are you here — terminal footer</h2>
<div class="grid two">{term}</div>

<h2>Motion variants</h2>
<p class="lede">SMIL loops at 12s (hero) and 1.6s (caret). Both are far below any hazardous flash
threshold, and both are decorative only: every animated asset has a static equivalent above.</p>
<div class="grid two">{motion}</div>

<h2>Avatar studies — candidates for review, not applied</h2>
<div class="avatars">{avatars}</div>

<h2>Mobile width check</h2>
<div class="phones">
<div class="phone"><img class="m" src="assets/profile/hero-dark.svg" alt="hero at mobile width"><div class="cap">hero-dark · 340px</div></div>
<div class="phone"><img class="m" src="assets/profile/system-map-dark.svg" alt="system map at mobile width"><div class="cap">system-map-dark · 340px</div></div>
<div class="phone"><img class="m" src="assets/profile/cards/portfolio-os-dark.svg" alt="card at mobile width"><div class="cap">card · 340px</div></div>
<div class="phone"><img class="m" src="assets/profile/terminal-dark.svg" alt="terminal at mobile width"><div class="cap">terminal · 340px</div></div>
</div>

<h2>Council notes</h2>
<ul class="notes">
<li><b>Identity hierarchy.</b> DUNG30N5 is the largest element on the page. NOAERTH reads as the
studio. @M4G3LL4N0 appears only as small metadata and in links.</li>
<li><b>Opaque canvases.</b> Each variant paints its own background rather than relying on
transparency, so contrast is guaranteed wherever the SVG is rendered — including
third-party mirrors and camo caches.</li>
<li><b>Negative space is the signature.</b> The first hero ran the node lattice behind the wordmark
and read as clutter. Type and structure are now separate objects.</li>
<li><b>Relationships are named, not drawn.</b> Curved edges through a gutter crossed four panels.
The relationship now sits on the panel that owns it.</li>
<li><b>No third-party graphics.</b> The broken repo-count badge is replaced by locally generated
controls, so the profile survives the disappearance of every badge service.</li>
<li><b>Numbers are generated.</b> <code>build_signal_data.py</code> reads the API and writes
<code>build-signal.json</code>; the SVG never contains a literal metric.</li>
</ul>

</main></body></html>"""

    GALLERY.write_text(html, encoding="utf-8")
    print(f"wrote {GALLERY} ({GALLERY.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())