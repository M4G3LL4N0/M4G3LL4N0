#!/usr/bin/env python3
"""Wrap GitHub's own rendered README HTML in a page that mimics github.com.

Why this exists: the markdown API returns GitHub's sanitised HTML, which is the
part that actually decides whether a <picture>, a <details>, or a media query
survives. Rendering that HTML inside a github.com-like shell is far closer to
the real page than re-rendering the markdown locally with a different engine
would be.

Relative asset paths are rewritten to the exact raw.githubusercontent.com URLs
GitHub serves them from, so the pictures resolve the same way they will live.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RENDERED = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OWNER_REPO = "M4G3LL4N0/M4G3LL4N0"
RAW = f"https://raw.githubusercontent.com/{OWNER_REPO}/main/"

DARK_BG, DARK_FG = "#0d1117", "#e6edf3"
LIGHT_BG, LIGHT_FG = "#ffffff", "#1f2328"

html = RENDERED.read_text(encoding="utf-8")

# GitHub rewrites repo-relative image paths to /<owner>/<repo>/raw/<branch>/...
# Mirror that by pointing them at raw.githubusercontent.com directly.
#
# srcset and src must be handled separately. An earlier version collapsed both
# into src=, which silently strips every <source> srcset in the document and
# makes every picture fall back to its <img>. That looks exactly like a broken
# theme-aware hero, so it is worth stating plainly: the bug was in the preview,
# not in the README.
def _absolutise(value: str) -> str:
    parts = []
    for candidate in value.split(","):
        candidate = candidate.strip()
        if not candidate:
            continue
        url, _, descriptor = candidate.partition(" ")
        if url.startswith(("http://", "https://", "/", "data:")):
            parts.append(candidate)
        else:
            parts.append(f"{RAW}{url}" + (f" {descriptor}" if descriptor else ""))
    return ", ".join(parts)


html = re.sub(r'srcset="([^"]*)"', lambda m: f'srcset="{_absolutise(m.group(1))}"', html)
html = re.sub(r'src="([^"]*)"',
              lambda m: f'src="{_absolutise(m.group(1)).split(",")[0]}"', html)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Profile preview</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
  }}
  .page {{ max-width: 1012px; margin: 0 auto; padding: 32px 32px 96px; }}
  .who {{ display:flex; gap:16px; align-items:center; margin-bottom: 24px; }}
  .avatar {{ width:64px; height:64px; border-radius:50%; background: var(--panel); }}
  .hd {{ font-size: 24px; font-weight: 600; }}
  .markup {{ font-size: 16px; }}
  .markup img {{ max-width: 100%; }}
  .markup h1, .markup h2 {{ border-bottom: 1px solid var(--border); padding-bottom: .3em; margin-top: 28px; }}
  .markup h2 {{ font-size: 24px; }}
  .markup a {{ color: var(--link); text-decoration: none; }}
  .markup table {{ border-collapse: collapse; display:block; overflow:auto; max-width:100%; }}
  .markup th, .markup td {{ border: 1px solid var(--border); padding: 6px 13px; }}
  .markup th {{ background: var(--panel); }}
  .markup code {{ background: var(--panel); padding: .2em .4em; border-radius: 6px; font-size: 85%; }}
  .markup hr {{ border: 0; border-top: 1px solid var(--border); margin: 24px 0; }}
  .markup details {{ border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; margin: 16px 0; }}
  .markup summary {{ cursor: pointer; font-weight: 600; }}
  .markup blockquote {{ border-left: .25em solid var(--border); padding-left: 1em; color: var(--muted); }}
  @media (prefers-color-scheme: dark) {{
    body {{ --bg: {DARK_BG}; --fg: {DARK_FG}; --panel: #161b22; --border: #30363d;
            --link: #4493f8; --muted: #8b949e; }}
  }}
  @media (prefers-color-scheme: light) {{
    body {{ --bg: {LIGHT_BG}; --fg: {LIGHT_FG}; --panel: #f6f8fa; --border: #d1d9e0;
            --link: #0969da; --muted: #59636e; }}
  }}
  @media (max-width: 700px) {{ .page {{ padding: 16px 16px 64px; }} }}
</style></head>
<body>
  <div class="page">
    <div class="who">
      <div class="avatar"></div>
      <div>
        <div class="hd">DUNG30N5</div>
        <div style="color:var(--muted);font-size:14px">systems builder &#183; hacker &#183; creative technologist</div>
      </div>
    </div>
    <article class="markup">
{html}
    </article>
  </div>
</body></html>
"""
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT} ({len(page)} bytes)")
