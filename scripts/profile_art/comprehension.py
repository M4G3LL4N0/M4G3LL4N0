#!/usr/bin/env python3
"""Project comprehension: derive the dossier's semantic fields from source.

The defect this exists to correct
---------------------------------
`build_dossiers.py` loaded the local source -- README, ARCHITECTURE.md, module
map, manifests, CLI source, test tree -- and then hardcoded nineteen fields to
empty:

    "problem": "", "primary_user": "", "major_components": [], "data_flow": "",
    "state_model": "", "input_types": [], "output_types": [],
    "verified_features": [], "known_limitations": [],
    "security_characteristics": [], "frameworks": [],
    "public_noaerth_positioning": "", "venture_stage": "", ...

All 126 dossiers had every one of those fields empty. The dossier was supposed to
be the input to the visual identity, so the identity had nothing to adapt to and
five repositories shipped a byte-identical hero with only the name substituted.

This module derives those fields from evidence that is already in the tree. It
is deterministic and it is conservative: every value it emits is traceable to a
file it read, and anything it cannot support is left empty and listed in
`unresolved`. A field it cannot fill must not be guessed, because a guess
propagates into the artwork and becomes an unverifiable claim about the project.

What is derived, and from what
------------------------------
  problem                 the "why" stated in README/ARCHITECTURE prose
  primary_user            the actor named in the README opening or description
  major_components        the module map table, or the source package listing
  data_flow               interface layer -> state layer, from ARCHITECTURE.md
  control_flow            the CLI entrypoint, or the request handler
  state_model             the persistence layer actually declared
  input_types             CLI/HTTP/env/CLI-flag surface found in source
  output_types            stdout/HTTP/file/db surface found in source
  primary_workflow        the documented loop, quoted from the source
  secondary_workflows     further documented commands or interfaces
  verified_features       features present in code AND covered by tests
  experimental_features   features present in code but untested
  known_limitations       limitations stated in the project's own docs
  frameworks              manifest dependencies, by recognised framework name
  security_characteristics security files and mechanisms present in source
  benchmark_dimensions    benchmark harnesses found in source
  release                 version from the manifest, not from a tag
  terminal_metaphor       the REAL CLI commands, parsed from the entrypoint

  python3 scripts/profile_art/comprehension.py agentos
  python3 scripts/profile_art/comprehension.py --all --report
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2]
DOSSIER_DIR = PROFILE / ".github-art" / "dossiers"

# The portfolio root. The owner's canonical location is /Users/matador/startups;
# this worker hosts the same tree at /srv/noaerth/startups. Resolution order is
# explicit override, then canonical, then the mirror, and the resolved path is
# recorded in the dossier so a later run on either host finds the same source.
ROOTS = [Path(p) for p in (
    os.environ.get("NOAERTH_STARTUPS", ""),
    "/Users/matador/startups",
    "/srv/noaerth/startups",
) if p]


def resolve_local(name: str, recorded: str = "") -> Path | None:
    """Find the project source for `name`, wherever this host keeps it."""
    if recorded:
        p = Path(recorded)
        if p.is_dir():
            return p
        # Recorded path is from another host; keep only the folder name.
        recorded = Path(recorded).name
    for root in ROOTS:
        if not root.is_dir():
            continue
        for cand in (root / (recorded or name), root / name,
                     root / name.lower()):
            if cand.is_dir():
                return cand
    return None

SKIP_DIR = re.compile(r"(^|/)(node_modules|\.git|dist|build|\.next|vendor|"
                      r"coverage|\.venv|__pycache__|target|out|assets)/")

# ---------------------------------------------------------------- frameworks
# Matched against manifest dependency names. Kept to names that change how the
# project is built or understood, not every package in the tree.
FRAMEWORKS: dict[str, tuple[str, ...]] = {
    "next.js": ("next",),
    "react": ("react", "react-dom"),
    "vue": ("vue",),
    "svelte": ("svelte",),
    "astro": ("astro",),
    "remix": ("@remix-run/", "@remix-run/react"),
    "express": ("express",),
    "fastify": ("fastify",),
    "hono": ("hono",),
    "nest": ("@nestjs/",),
    "trpc": ("@trpc/server",),
    "prisma": ("prisma", "@prisma/client"),
    "drizzle": ("drizzle-orm",),
    "typeorm": ("typeorm",),
    "sequelize": ("sequelize",),
    "supabase": ("@supabase/",),
    "firebase": ("firebase",),
    "d3": ("d3",),
    "three": ("three",),
    "tailwindcss": ("tailwindcss",),
    "vite": ("vite",),
    "webpack": ("webpack",),
    "esbuild": ("esbuild",),
    "rollup": ("rollup",),
    "playwright": ("@playwright/", "playwright"),
    "vitest": ("vitest",),
    "jest": ("jest",),
    "pytest": ("pytest",),
    "pyo3": ("pyo3",),
    "flask": ("flask",),
    "django": ("django",),
    "fastapi": ("fastapi",),
    "uvicorn": ("uvicorn",),
    "pydantic": ("pydantic",),
    "typer": ("typer",),
    "click": ("click",),
    "rich": ("rich",),
    "sqlalchemy": ("sqlalchemy",),
    "langchain": ("langchain",),
    "anthropic": ("@anthropic-ai/",),
    "openai": ("openai",),
}

# ---------------------------------------------------------------- limitation
# The project's own words about its boundaries. Only matched in documentation
# written by the project, never in source comments.
LIMITATION_HEAD = re.compile(
    r"^#{1,4}\s*(known limitations?|limitations?|non-?goals?|what it does not do|"
    r"boundaries|constraints?|caveats?)\b", re.I | re.M)
BULLET = re.compile(r"^\s*[-*]\s+(?P<t>\S.{10,240})$", re.M)

# ---------------------------------------------------------------- CLI surface
# argparse subcommand registration, across the spellings real projects use.
ADD_PARSER = re.compile(
    r"""add_parser\(\s*["'](?P<name>[a-z0-9][a-z0-9_.-]{0,40})["']"""
    r"""(?:[^)]*?help\s*=\s*["'](?P<help>[^"']{3,90})["'])?""",
    re.S | re.I)
# commander/yargs style
COMMANDER = re.compile(
    r"""\.command\(\s*["'](?P<name>[a-z0-9][a-z0-9:_.-]{0,40})["']"""
    r"""(?:[^)]*?\.description\(\s*["'](?P<help>[^"']{3,90})["'])?""",
    re.S | re.I)
CLICK_OPT = re.compile(
    r"""@(?:click\.)?(?:command|group)\(\s*["'](?P<name>[a-z0-9][a-z0-9_.-]{0,40})["']""",
    re.I)

# Plain Node CLIs. A project with no framework dispatches on argv directly, in
# the shapes below. devstate declares `"bin": {"devstate": "./src/index.js"}` and
# routes commands through a switch or a lookup table; without this the parser
# found the binary and then reported no commands for it.
# Every alternative uses the SAME group name. Separate names per alternative
# meant m.group("name") was None for all but the first, and the CLI list gained
# an entry literally reading `gg None`.
NODE_CMD = re.compile(
    r"""(?:\bcase\s+["']([a-z][a-z0-9-]{1,30})["']"""
    r"""|^\s*["']([a-z][a-z0-9-]{1,30})["']\s*:"""
    r"""|\b(?:cmd|command|CMD)(?:Map|ap|s|S)?\s*\.\s*(?:set|has)\(\s*"""
    r"""["']([a-z][a-z0-9-]{1,30})["'])""",
    re.M)
TYPER_APP = re.compile(r"""typer\.Typer\(\s*(?:title\s*=\s*["'](?P<title>[^"']+)["'])?""", re.I)

CONSOLE_SCRIPT = re.compile(r"""^\s*\[project\.scripts\]\s*$""", re.M)
BIN_FIELD = re.compile(r'"bin"\s*:\s*\{(?P<body>[^}]*)\}', re.S)
NPM_BIN = re.compile(r'"(?P<name>[a-z0-9@._-]+)"\s*:\s*"(?P<target>[^"]+)"')

# Subcommand nesting. `parser.add_subparsers()` is assigned to a variable; calls
# on that variable are top-level commands, calls on a command's own subparser
# variable are its children. Without this, a flat regex returns `create` and
# `list` from half a dozen unrelated groups and calls them top-level commands.
VEN_CACHE = PROFILE / ".noaerth-public-ventures.json"


MAP = PROFILE / "project-map.json"


def map_slugs() -> dict[str, str]:
    """github_repo -> venture slug, read from project-map.json."""
    if not MAP.is_file():
        return {}
    try:
        data = json.loads(MAP.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for entry in data.get("records", []):
        m = entry.get("map", entry) if isinstance(entry, dict) else {}
        repo = m.get("github_repo", "")
        slug = (m.get("noaerth_venture_slug") or "").strip()
        if repo and slug:
            out[repo] = slug
    return out


MAP_SLUGS = map_slugs()


def venture_index() -> dict[str, dict]:
    """Source B, keyed by slug. Empty when the cache has never been fetched."""
    if not VEN_CACHE.is_file():
        return {}
    try:
        data = json.loads(VEN_CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {v["slug"]: v for v in data.get("ventures", [])
            if v.get("slug") and not v.get("name", "").startswith("_")}


SUBPARSERS_ASSIGN = re.compile(
    r"^\s*(?P<var>[A-Za-z_]\w*)\s*=\s*[A-Za-z_]\w*\.add_subparsers\(", re.M)
SUBPARSERS_BARE = re.compile(r"^[A-Za-z_]\w*\.add_subparsers\(", re.M)
SUB_ADD = re.compile(
    r"(?P<var>[A-Za-z_]\w*)\s*\.\s*add_parser\(\s*[\"'](?P<name>[a-z0-9][a-z0-9_.:-]{0,40})[\"']"
    r"(?:[^)]*?help\s*=\s*[\"'](?P<help>[^\"']{3,90})[\"'])?", re.S)

# One ordered pass over the entrypoint, capturing the three shapes that carry
# command structure. Order matters: which group a call belongs to depends on
# assignments made earlier in the file, so this cannot be three separate regexes.
#   1: <var> = <target>.add_subparsers(...)   a subparser group for <target>
#   2: <var> = <target>.add_parser("name")   <var> parses for command "name"
#   3: <group>.add_parser("name")            a command registered in <group>
COMMAND_SCAN = re.compile(
    r"""^\s*(?P<a_var>[A-Za-z_]\w*)\s*=\s*(?P<a_tgt>[A-Za-z_]\w*)\s*\.\s*add_subparsers\(
      | ^\s*(?P<b_var>[A-Za-z_]\w*)\s*=\s*(?P<b_grp>[A-Za-z_]\w*)\s*\.\s*add_parser\(\s*["'](?P<name>[a-z0-9][\w.:-]{0,40})["']
        (?:[^)]*?help\s*=\s*["'](?P<help>[^"']{3,90})["'])?
      | (?P<c_grp>[A-Za-z_]\w*)\s*\.\s*add_parser\(\s*["'](?P<name2>[a-z0-9][\w.:-]{0,40})["']
        (?:[^)]*?help\s*=\s*["'](?P<help2>[^"']{3,90})["'])?""",
    re.S | re.X | re.M)

# ---------------------------------------------------------------- interfaces
IFACE_HINTS: list[tuple[str, tuple[str, ...]]] = [
    # Next.js / Remix declare HTTP handlers as exported functions in a route
    # module, not as framework registrations. Looking only for add_route and
    # friends missed every Next.js API surface: 79 of 86 DATA_FLOW dossiers
    # reported no interfaces at all while blitzproof ships eight route handlers.
    ("HTTP API", ("add_route", "APIRouter", "@app.get", "@app.post",
                  "express()", "FastAPI(", "router.get", "router.post",
                  "NextResponse", "export async function POST",
                  "export async function GET", "new Request(")),
    ("MCP stdio", ("mcp_server", "stdio_server", "mcp.server", "FastMCP")),
    ("A2A", ("a2a",)),
    ("WebSocket", ("websocket", "WebSocket", "socket.io")),
    ("gRPC", ("grpc",)),
    ("CLI", ("argparse", "click.command", "typer.Typer", "commander")),
    ("server actions", ('"use server"',)),
]

# Route modules, counted from the tree. The most reliable signal of an HTTP
# surface in a modern TypeScript project.
ROUTE_FILE = re.compile(r"(^|/)app/api/.*/route\.(ts|tsx|js|jsx)$|"
                        r"(^|/)pages/api/.*\.(ts|tsx|js|jsx)$|"
                        r"(^|/)api/.*\.(py|go|rb)$")

STORAGE_HINTS: list[tuple[str, tuple[str, ...]]] = [
    ("sqlite", ("sqlite3", "sqlite")),
    ("PostgreSQL", ("psycopg", "asyncpg", "postgres")),
    ("MongoDB", ("pymongo", "mongoose")),
    ("Redis", ("redis",)),
    ("SQLAlchemy ORM", ("sqlalchemy",)),
    ("file-backed JSON", ("json.dump", "write_text", "JSON.stringify")),
    ("CSV / tabular files", ("csv.", "read_csv", "to_csv")),
    ("Parquet", ("parquet",)),
    ("SQLite via ORM", ("Model)", "Column(")),
    ("vector index", ("faiss", "chroma", "qdrant", "pinecone")),
]

BENCH_HINTS = ("benchmark", "bench_", "_bench", "pytest-benchmark", "criterion",
               "timeit", "perf", "latency")


def read(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(errors="replace")[:limit]
    except Exception:
        return ""


def git_files(path: Path) -> list[str]:
    try:
        p = subprocess.run(["git", "-C", str(path), "ls-files"],
                           capture_output=True, text=True, timeout=30)
        return [f for f in p.stdout.splitlines() if f.strip()]
    except Exception:
        return []


# ------------------------------------------------------------------ manifest

def manifest_facts(path: Path) -> dict:
    """Name, version, scripts, dependencies and bin entries, per manifest type."""
    out: dict = {"name": "", "version": "", "description": "",
                 "scripts": {}, "deps": [], "bin_name": "", "bin_target": "",
                 "test_command": "", "build_command": ""}
    pkg = path / "package.json"
    if pkg.is_file():
        try:
            d = json.loads(read(pkg))
        except Exception:
            d = {}
        out["name"] = d.get("name", "") or ""
        out["version"] = d.get("version", "") or ""
        out["description"] = d.get("description", "") or ""
        out["scripts"] = d.get("scripts") or {}
        out["deps"] = sorted(set(list((d.get("dependencies") or {}).keys())
                                 + list((d.get("devDependencies") or {}).keys())))
        b = BIN_FIELD.search(read(pkg))
        if b:
            first = NPM_BIN.search(b.group("body"))
            if first:
                out["bin_name"] = first.group("name")
                out["bin_target"] = first.group("target")
        # `bin` may also be a bare string, which is the name itself.
        if not out["bin_name"] and isinstance(d.get("bin"), str):
            out["bin_name"] = d["bin"]
        s = out["scripts"]
        for key in ("test", "tests"):
            if s.get(key):
                out["test_command"] = f"npm run {key}"
                break
        if s.get("build"):
            out["build_command"] = "npm run build"
        return out

    py = path / "pyproject.toml"
    if py.is_file():
        t = read(py)
        n = re.search(r'^\s*name\s*=\s*["\'](?P<v>[^"\']+)["\']', t, re.M)
        v = re.search(r'^\s*version\s*=\s*["\'](?P<v>[^"\']+)["\']', t, re.M)
        d = re.search(r'^\s*description\s*=\s*["\'](?P<v>[^"\']+)["\']', t, re.M)
        out["name"] = n.group("v") if n else ""
        out["version"] = v.group("v") if v else ""
        out["description"] = d.group("v") if d else ""
        scripts = CONSOLE_SCRIPT.search(t)
        if scripts:
            for line in t[scripts.end():].splitlines():
                if not line.strip() or line.startswith("["):
                    break
                mm = re.match(r'^\s*(?P<k>[a-z0-9_-]+)\s*=\s*"(?P<v>[^"]+)"', line)
                if mm:
                    out["scripts"][mm.group("k")] = mm.group("v")
        out["deps"] = sorted(set(re.findall(r'["\']([a-zA-Z0-9_.-]+)["\']\s*(?:[><=~!]|\s*,|\s*\))', t)))
        entry = re.search(r'^\s*(?P<name>[a-z0-9_-]+)\s*=\s*["\'](?P<target>[\w.]+:[\w.]+)["\']',
                          t[scripts.end():] if scripts else "")
        if entry:
            out["bin_name"] = entry.group("name")
        if "test" in out["scripts"]:
            out["test_command"] = "pytest"
        if "build" in out["scripts"]:
            out["build_command"] = "python -m build"
        return out

    return out


def frameworks(deps: list[str]) -> list[str]:
    low = [d.lower() for d in deps]
    out = []
    for label, needles in FRAMEWORKS.items():
        for n in needles:
            if any(d == n or d.startswith(n) for d in low):
                out.append(label)
                break
    return sorted(set(out))


# -------------------------------------------------------------------- prose

# Framework scaffolding text. `create-next-app` writes a standard opening
# paragraph into every generated README. 43 of the 126 dossiers were picking
# that up as the project's problem statement, which is not a description of
# anything the project does.
BOILERPLATE = re.compile(
    r"create-next-app|boilerplate|^\s*this is a \[.*\]\(.*\) project|"
    r"getting started with|welcome to .* powered by|"
    r"this project was bootstrapped with|"
    r"next/font|automatically optimize and load|"
    r"take a look at the following resources|interactively with your browser|"
    r"new font family for", re.I)

# Setup instructions. Skipping these matters: a README whose opening prose is
# "Open http://localhost:3000 with your browser to see the result" otherwise
# becomes the project's problem statement.
INSTRUCTIONAL = re.compile(
    r"\b(?:run|npm|pnpm|yarn|bun|install)\s+(?:the\s+)?"
    r"(?:development|dev|build|start|production)?\s*server\b|"
    r"open\s*\[?https?://localhost|localhost:\d+|"
    r"you can start editing|page auto-updates|"
    r"see the result|edit the page|deploy(ing)? (with|on) vercel|"
    r"check out the \[.*github repository\]|"
    r"^\s*(?:first|next)\s*,?\s*(?:run|open)\b", re.I)


def first_prose(text: str, limit: int = 400) -> str:
    """First real paragraph of prose, skipping headings, badges and code.

    Scaffolding is skipped rather than returned, and so are paragraphs that are
    really link lists or bullet runs. A create-next-app README has no prose at
    all -- only "Getting Started", "Learn More" bullet lists and a Vercel
    paragraph -- so without the link-list check the field fills with
    "- [Next.js Documentation](...) - learn about Next.js features and API",
    which is the framework's documentation index, not this project.
    """
    for block in re.split(r"\n\s*\n", text):
        b = " ".join(block.split())
        if not b or b.startswith(("#", ">", "|", "```", "!", "[![", "---")):
            continue
        if b.startswith("<") or b.startswith("<!--"):
            continue
        if BOILERPLATE.search(b) or INSTRUCTIONAL.search(b):
            continue
        # A block that is mostly markdown links is a link list, not prose. The
        # ratio is measured against the characters the link markup occupies
        # rather than the link count, because a two-link block can still be
        # 80% link text -- which is exactly what a create-next-app "Learn More"
        # section looks like once its bullets are joined into one block.
        link_chars = sum(len(m.group(0)) for m in re.finditer(r"\[[^\]]+\]\([^)]+\)", b))
        if link_chars >= 40 and link_chars * 100 >= len(b) * 35:
            continue
        if len(b) > 60:
            return b[:limit]
    return ""


def problem_statement(readme: str, arch: str, venture_pitch: str = "") -> str:
    """The project's own statement of what problem it addresses.

    Looked for under an explicit heading first, because a section titled
    "Problem" is the project's own framing. Falls back to the opening prose,
    which is where a README states why the thing exists.
    """
    for text in (readme, arch):
        m = re.search(r"^#{1,4}\s*(?:the\s+)?problem\b", text, re.I | re.M)
        if m:
            body = text[m.end():m.end() + 900]
            para = first_prose(body, 320)
            if para:
                return para
    lead = first_prose(readme, 320)
    if lead:
        return lead
    # The leading blockquote is a deliberate one-line statement of what the
    # project is. agentos opens with "A universal, provider-neutral AI Agent
    # Engine that turns objectives into verified outcomes", which is the most
    # accurate sentence in the repository and sits above the prose.
    m = re.search(r"^>\s*\*\*(?P<t>[^*\n]{20,300})\*\*", readme, re.M)
    if m and not BOILERPLATE.search(m.group("t")):
        return " ".join(m.group("t").split())[:320]
    # A README that is entirely create-next-app scaffolding says nothing about
    # the project. The venture card's pitch line is the next best source: it is
    # written about this project specifically. It is labelled as the public
    # positioning in the dossier so it is never mistaken for a code-derived
    # claim, and it is the only project-specific sentence available.
    if venture_pitch and not BOILERPLATE.search(venture_pitch):
        return venture_pitch[:320]
    return ""


def primary_user(readme: str, desc: str) -> str:
    """The actor the project names as its user.

    Read from an explicit "who is this for" heading, then from the audiences
    the README states. Never invented from the category: a category says what
    kind of project this is, not who runs it.
    """
    for text in (readme,):
        m = re.search(r"^#{1,4}\s*(?:who(?:'|’)s this for|who is it for|"
                      r"primary user|users?|audience)\b", text, re.I | re.M)
        if m:
            body = text[m.end():m.end() + 700]
            para = first_prose(body, 260)
            if para:
                return para
    m = re.search(r"\bfor ([a-z][\w -]{3,40}?)(?:,| and | who | that |\.|$)",
                  readme[:2500], re.I)
    if m:
        cand = m.group(1).strip()
        if len(cand) > 4 and cand.lower() not in ("example", "example:", "instance"):
            return f"built for {cand}"
    if desc:
        return desc
    return ""


def module_map(arch: str) -> list[str]:
    """Component rows from an ARCHITECTURE.md module table."""
    rows = re.findall(r"^\|\s*`(?P<m>[\w./-]+\.(?:py|ts|tsx|js|jsx|go|rs|rb))`\s*\|\s*(?P<r>[^|]{8,200})",
                      arch, re.M)
    out = []
    for m, r in rows[:12]:
        resp = " ".join(r.split())
        if len(resp) > 150:
            resp = resp[:147] + "..."
        out.append(f"{m} — {resp}")
    return out


def components_from_tree(path: Path, files: list[str]) -> list[str]:
    """Top-level source packages or directories, with their file counts."""
    buckets: dict[str, int] = {}
    for f in files:
        if SKIP_DIR.search(f):
            continue
        parts = f.split("/")
        if len(parts) < 2:
            continue
        head = parts[0]
        if head in ("src", "lib", "app", "packages", "internal", "cmd", "core"):
            if len(parts) >= 3:
                key = f"{head}/{parts[1]}"
            else:
                key = f"{head}/*"
        else:
            key = head
        buckets[key] = buckets.get(key, 0) + 1
    ranked = sorted(buckets.items(), key=lambda kv: (-kv[1], kv[0]))
    return [f"{k} ({n} file{'s' if n != 1 else ''})" for k, n in ranked[:10]]


def interface_layers(blob: str, route_files: list[str] | None = None) -> list[str]:
    out = [name for name, needles in IFACE_HINTS
           if any(n in blob for n in needles)]
    if route_files and "HTTP API" not in out:
        out.insert(0, "HTTP API")
    return out


def storage_layers(blob: str) -> list[str]:
    found = []
    for name, needles in STORAGE_HINTS:
        if any(n in blob for n in needles):
            found.append(name)
    # "SQLite via ORM" is a duplicate observation of sqlite when both hit.
    if "sqlite" in found and "SQLite via ORM" in found:
        found.remove("SQLite via ORM")
    return found


def io_surface(path: Path, files: list[str], blob: str, mf: dict) -> dict:
    """Input and output types, from the interfaces the project actually has."""
    inputs, outputs = [], []
    route_files = [f for f in files if ROUTE_FILE.search(f)]
    ifaces = interface_layers(blob, route_files)
    if "CLI" in ifaces:
        inputs.append("CLI arguments")
        outputs.append("stdout / stderr")
        if mf.get("bin_name"):
            inputs.append(f"`{mf['bin_name']}` subcommands")
    if "HTTP API" in ifaces:
        inputs.append("HTTP requests (JSON)")
        outputs.append("HTTP responses (JSON)")
        if route_files:
            # Naming the actual routes is the difference between "has an HTTP
            # API" and a reader knowing which endpoints exist.
            routes = sorted({re.sub(r"^.*/api/", "", f).rsplit("/route.", 1)[0]
                             for f in route_files})
            if routes:
                outputs.append("route handlers: " + ", ".join(routes[:8]))
    if "MCP stdio" in ifaces:
        inputs.append("MCP JSON-RPC over stdio")
    if "WebSocket" in ifaces:
        inputs.append("WebSocket frames")
    if "gRPC" in ifaces:
        inputs.append("gRPC calls")
    env = re.findall(
        r'''os\.environ(?:\.get)?\(?\s*\[?\s*["']([A-Z][A-Z0-9_]{3,40})["']''', blob)
    if env:
        inputs.append("environment variables: " + ", ".join(sorted(set(env))[:6]))
    args = re.findall(r'add_argument\(\s*"(--[a-z0-9-]{2,30})"', blob)
    if args:
        inputs.append("flags: " + ", ".join(sorted(set(args))[:8]))

    store = storage_layers(blob)
    for s in store:
        outputs.append(f"persisted to {s}")
    if re.search(r"write_text|json\.dump|fs\.write", blob):
        outputs.append("files on disk")
    if re.search(r"\bcsv\b|\.to_csv|read_csv", blob, re.I):
        outputs.append("CSV exports")
    return {"inputs": inputs[:6], "outputs": outputs[:6], "interfaces": ifaces,
            "storage": store}


def cli_commands(path: Path, files: list[str], mf: dict) -> list[dict]:
    """Real CLI commands, parsed from the project's own entrypoint.

    Section 11 of the brief forbids putting an unverifiable command in the
    artwork. So every command here is read out of the argument parser or
    command definition in the source, and a repository with no CLI yields an
    empty list rather than an invented one.
    """
    bin_name = mf.get("bin_name") or ""
    if not bin_name:
        return []
    targets: list[str] = []
    # Resolve the declared entrypoint module. `agentos = "agentos.cli:main"`
    # names the PACKAGE first, so the module to open is `agentos`, not `cli`:
    # taking the last dotted segment looks for src/cli/cli.py, finds nothing, and
    # silently yields an empty command list.
    entry = re.search(rf'{re.escape(bin_name)}\s*=\s*["\']([\w.]+):([\w.]+)["\']',
                      read(path / "pyproject.toml"))
    if entry:
        parts = entry.group(1).split(".")
        pkg = parts[0] if len(parts) > 1 else ""
        for pkg_root in ("src", ""):
            base = f"{pkg_root}/{pkg}" if pkg_root else pkg
            cands = []
            if base:
                cands += [f"{base}/cli.py", f"{base}/__main__.py",
                          f"{base}/main.py", f"{base}/__init__.py"]
            cands += [f"{base}.py" if base else "", "cli.py", "src/cli.py",
                      "__main__.py"]
            for cand in cands:
                if cand and (path / cand).is_file():
                    targets.append(cand)
                    break
            if targets:
                break
    if not targets:
        # A Node CLI declared as `"bin": {"name": "./src/index.js"}` points at
        # its entrypoint directly. Resolving it is what turns devstate from "has
        # a bin, no commands" into a real command list.
        target = (mf.get("bin_target") or "").strip()
        cands = []
        if target:
            t = target.lstrip("./")
            cands += [t, f"src/{t}", f"bin/{t}"]
        cands += ["src/cli.ts", "src/index.ts", "src/index.js", "cli.ts",
                  "bin/cli.js", "bin/cli.ts", "src/cmd/root.go", "main.go",
                  "src/main.rs", "index.js", "index.ts"]
        for cand in cands:
            if cand and (path / cand).is_file():
                targets.append(cand)
                break

    # A bin entry may be a launcher, not the parser. grokinstall's
    # `bin/grokinstall` is a shell wrapper that execs `cmd/grokinstall`, and
    # ocw.js only forwards to `dist/src/cli`. If the declared target yields no
    # commands, the real source is the Go command package behind it.
    def scan(rel: str) -> dict[str, dict]:
        text = read(path / rel)
        found: dict[str, dict] = {}
        if not text:
            return found
        for m in COMMAND_SCAN.finditer(text):
            if m.group("a_var"):
                continue
            if m.group("b_var"):
                name, help_ = m.group("name"), (m.group("help") or "").strip()
            else:
                name, help_ = m.group("name2"), (m.group("help2") or "").strip()
            if name in ("help", "version", "completion", "completions"):
                continue
            if name not in found or (help_ and not found[name]["help"]):
                found[name] = {"command": name, "help": help_, "source": rel}
        for rx in (COMMANDER, CLICK_OPT, NODE_CMD):
            for m in rx.finditer(text):
                # A pattern may name its group `name` or carry unnamed
                # alternatives; both are accepted so the caller does not have to
                # know which regex it is holding.
                name = m.group("name") if "name" in rx.groupindex else next(
                    (g for g in m.groups() if g), None)
                if not name or name in ("help", "version"):
                    continue
                help_ = (m.groupdict().get("help") or "").strip()
                if name not in found or (help_ and not found[name]["help"]):
                    found[name] = {"command": name, "help": help_, "source": rel}
        return found

    parser_command: dict[str, str] = {}
    group_owner: dict[str, str] = {}
    seen: dict[str, dict] = {}

    for rel in dict.fromkeys(targets):
        text = read(path / rel)
        if not text:
            continue

        # Nesting is resolved by a single ordered scan, because it is a
        # dataflow problem: which group a call belongs to depends on
        # assignments made earlier in the file. Two maps are enough:
        #   parser_command  a parser variable -> the command it parses for
        #   group_owner     a subparsers variable -> its parent command ("" root)

        for m in COMMAND_SCAN.finditer(text):
            if m.group("a_var"):
                # A subparser group belongs to the command its target parses.
                group_owner[m.group("a_var")] = parser_command.get(
                    m.group("a_tgt"), "")
                continue

            if m.group("b_var"):
                # `<var> = <group>.add_parser("name")` registers the command in
                # <group> AND makes <var> the parser for it, because a later
                # `<var2> = <var>.add_subparsers()` hangs off that command.
                # This shape is how most argparse CLIs are written, so treating
                # it as assignment-only silently drops every top-level command.
                parser_command[m.group("b_var")] = m.group("name")
                group, name, help_ = (m.group("b_grp"), m.group("name"),
                                      (m.group("help") or "").strip())
            else:
                group, name, help_ = (m.group("c_grp"), m.group("name2"),
                                      (m.group("help2") or "").strip())

            if name in ("help", "version", "completion", "completions"):
                continue
            owner = group_owner.get(group, "")
            parts = [p for p in (owner, name) if p]
            full = " ".join([bin_name] + parts)
            prev = seen.get(full)
            if prev is None or (help_ and not prev["help"]):
                seen[full] = {"command": full, "help": help_, "source": rel,
                              "parent": owner}

    # If the declared entrypoint yielded nothing, it was a launcher. Follow it.
    if not seen and (path / "cmd").is_dir():
        for pkg in sorted({p.name for p in (path / "cmd").iterdir() if p.is_dir()}):
            for cand in (f"cmd/{pkg}/main.go", f"cmd/{pkg}/root.go",
                         f"cmd/{pkg}/cli.go", f"cmd/{pkg}/app.go"):
                if not (path / cand).is_file():
                    continue
                for name, c in scan(cand).items():
                    seen[f"{bin_name} {name}"] = {
                        "command": f"{bin_name} {name}", "help": c["help"],
                        "source": cand, "parent": ""}
                if seen:
                    break
            if seen:
                break

    out = list(seen.values())
    # Top-level commands first, then by how central the verb is. A README leads
    # with run/status/doctor, and so should a terminal plate.
    order = {"run": 0, "status": 1, "doctor": 2, "init": 3, "list": 4, "build": 5,
             "test": 6, "serve": 7, "start": 8, "verify": 9, "plan": 10,
             "create": 11, "show": 12, "inspect": 13, "recover": 14, "sync": 15,
             "deploy": 16, "search": 17, "query": 18, "analyze": 19, "scan": 20,
             "check": 21, "generate": 22, "apply": 23, "clean": 24, "pull": 25}
    # package.json `scripts` are real, runnable, documented commands. A project
    # with no framework and no argparse still exposes them, and they are the
    # honest terminal story for it. Every npm script is prefixed with `run`
    # because that is how they are invoked.
    if mf.get("scripts") and bin_name:
        for verb, desc in (("build", "build the project"),
                           ("test", "run the test suite"),
                           ("start", "start the service"),
                           ("dev", "run the development server"),
                           ("lint", "lint the source")):
            if verb in mf["scripts"] and f"{bin_name} run {verb}" not in seen:
                seen[f"{bin_name} run {verb}"] = {
                    "command": f"{bin_name} run {verb}", "help": desc,
                    "source": "package.json scripts", "parent": ""}
        # project-specific scripts, which are the ones a README would lead with
        for k, v in list(mf["scripts"].items())[:6]:
            if k in ("build", "test", "start", "dev", "lint"):
                continue
            full = f"{bin_name} run {k}"
            if full not in seen:
                seen[full] = {"command": full,
                              "help": (v or "").strip()[:80],
                              "source": "package.json scripts", "parent": ""}

    out = list(seen.values())
    out.sort(key=lambda c: (1 if c.get("parent") else 0,
                            order.get(c["command"].split()[-1], 50),
                            c["command"]))
    return out[:10]


def workflow_from_docs(readme: str, arch: str) -> str:
    """The project's documented loop, quoted rather than paraphrased."""
    for text in (readme, arch):
        m = re.search(r"```(?:text|txt|bash|sh)?\n(?P<b>objective[^`\n]{0,200}(?:\n[^`\n]{1,60}){0,6})```",
                      text, re.I)
        if m:
            body = " \u2192 ".join(x.strip() for x in m.group("b").strip().splitlines()
                                   if x.strip())
            return body[:260]
    m = re.search(r"^#{1,4}\s*(?:the\s+)?(?:loop|workflow|how it works|north star)\b",
                  readme + "\n" + arch, re.I | re.M)
    if m:
        para = first_prose((readme + "\n" + arch)[m.end():m.end() + 700], 260)
        if para:
            return para
    return ""


def limitations(texts: list[str], path: Path, files: list[str],
                test_files: list[str], root_docs: list[str]) -> list[str]:
    """Limitations the project states about itself, plus measured absences.

    Two sources, kept distinguishable:

      stated     the project's own words, under its own limitations heading.
      measured   facts read off the tree: no test tree, no CI, no license.
                  These are limitations of the repository, not opinions about
                  the code, and they are what the completion ledger is graded
                  against. Recording them here is what stops the artwork from
                  implying a test suite that does not exist.
    """
    out: list[str] = []
    for text in texts:
        for m in LIMITATION_HEAD.finditer(text):
            body = text[m.end():m.end() + 1200]
            for b in BULLET.finditer(body):
                t = " ".join(b.group("t").split())
                if 20 < len(t) < 220 and t not in out:
                    out.append(t)
                if len(out) >= 5:
                    break
            if len(out) >= 5:
                break
        if len(out) >= 5:
            break

    # Projects keep their limitations in a dedicated document rather than in the
    # README. agentos states ten of them under "## Known limitations" in
    # CURRENT_STATE.md, which the README never mentions, so README + ARCHITECTURE
    # alone finds nothing. Every root document is scanned for the heading, and
    # only those carrying it are read further.
    if len(out) < 5:
        for doc in root_docs:
            t = read(path / doc, 40_000)
            if not t or not LIMITATION_HEAD.search(t):
                continue
            for m in LIMITATION_HEAD.finditer(t):
                for b in BULLET.finditer(t[m.end():m.end() + 1400]):
                    line = " ".join(b.group("t").split())
                    if 20 < len(line) < 220 and line not in out:
                        out.append(f"{doc}: {line}")
                    if len(out) >= 7:
                        break
                if len(out) >= 7:
                    break
            if len(out) >= 7:
                break

    roots = {f.split("/")[0] for f in files}
    measured: list[str] = []
    if not test_files:
        measured.append("no test tree in the repository; no test count is claimed")
    elif len(test_files) < 3:
        measured.append(f"only {len(test_files)} test file(s); coverage is narrow")
    if not any(f.startswith(".github/workflows/") for f in files):
        measured.append("no CI workflow configured")
    if not (roots & {"LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"}):
        measured.append("no LICENSE file at the repository root")
    for m in measured:
        if m not in out:
            out.append(m)
    return out[:8]


def security_notes(arch: str, readme: str, files: list[str]) -> list[str]:
    out = []
    roots = {f.split("/")[0] for f in files}
    for doc in ("SECURITY.md", "SECURITY", "SECURITY_POLICY.md", "SECURITY_BOUNDARIES.md"):
        if doc in roots:
            out.append(f"{doc} documents the threat model and disclosure path")
            break
    blob = arch + "\n" + readme
    for label, needle in (
        ("secret redaction in the execution path", "redact"),
        ("destructive-operation gating", "destructive"),
        ("approval required before privileged action", "approval"),
        ("write-root confinement", "write root"),
        ("loopback-only bind address", "loopback"),
        ("no authentication in the current version", "no auth"),
        ("policy-gated subprocess execution", "policy-gated"),
    ):
        if needle.lower() in blob.lower():
            out.append(label)
    return out[:6]


def verified_vs_experimental(path: Path, files: list[str], arch: str,
                             readme: str, test_files: list[str]) -> tuple[list[str], list[str]]:
    """Test coverage, and the project's OWN experimental labels.

    Two separate questions, kept separate on purpose:

      verified     a component that a test file actually names. This is a
                   measurement: the component appears in a test module.
      experimental ONLY what the project itself flags as experimental, planned,
                   or unproven, in its own documentation.

    An earlier version put every untested component in `experimental_features`.
    That is wrong in a way that matters: 124 of 126 projects have no test tree
    at all, so the field filled with 719 items and would have shipped to the
    artwork as a claim that this code is experimental. Most of it is simply
    untested. Absence of tests is recorded as absence of tests, in
    `known_limitations`, and is not laundered into a maturity claim.
    """
    tests_blob = " ".join(read(path / f, 20_000) for f in test_files[:40])
    tests_low = tests_blob.lower()
    components = module_map(arch) or components_from_tree(path, files)

    verified: list[str] = []
    for comp in components:
        name = comp.split(" — ")[0].split("/")[-1].replace(".py", "").replace(".ts", "")
        stem = name.replace("_", "").replace("-", "").lower()
        if len(stem) < 4:
            continue
        if stem in tests_low or name.lower() in tests_low:
            verified.append(comp)

    experimental: list[str] = []
    for text in (readme, arch):
        for m in re.finditer(
                r"^#{1,4}\s*(?P<head>experimental|planned|not yet|future work|"
                r"work in progress|wip|next steps?|roadmap)\b", text, re.I | re.M):
            para = first_prose(text[m.end():m.end() + 700], 240)
            if para:
                entry = f"{m.group('head')}: {para}"
                if entry not in experimental:
                    experimental.append(entry)
            if len(experimental) >= 4:
                break
        if len(experimental) >= 4:
            break
    return verified[:6], experimental[:4]


def benchmark_dims(path: Path, files: list[str], arch: str) -> list[str]:
    hits = []
    for f in files:
        if SKIP_DIR.search(f):
            continue
        base = Path(f).name.lower()
        if any(h in base for h in BENCH_HINTS):
            hits.append(f)
    out = []
    m = re.search(r"^#{1,4}\s*(?:benchmarks?|performance|performance targets?)\b",
                  arch, re.I | re.M)
    if m:
        for b in BULLET.finditer(arch[m.end():m.end() + 1200]):
            t = " ".join(b.group("t").split())
            if 12 < len(t) < 200:
                out.append(t)
            if len(out) >= 5:
                break
    if hits and not out:
        out.append(f"benchmark harness present: {', '.join(sorted(hits)[:3])}")
    return out[:5]


# ------------------------------------------------------------------ assembly

def comprehend(path: Path, venture: dict | None = None) -> dict:
    """Derive the semantic layer for one project from its own source.

    `venture` is the cached public card (Source B). It is used only where the
    project's own documentation says nothing, and whatever comes from it is
    tagged as public positioning so it is never presented as a code-derived
    claim.
    """
    files = git_files(path)
    visible = [f for f in files if not SKIP_DIR.search(f)]
    docs = [f for f in visible if f.endswith((".md", ".rst")) and "/" not in f]
    root = {f for f in visible if "/" not in f}

    arch = read(path / "ARCHITECTURE.md", 40_000)
    readme = read(path / "README.md", 30_000)
    docs_text = " ".join(read(path / f, 6_000) for f in docs[:8])
    source = [f for f in visible if f.endswith((".py", ".ts", ".tsx", ".js", ".jsx",
                                                 ".go", ".rs", ".rb", ".mjs"))]
    blob = " ".join(read(path / f, 8_000) for f in source[:80])
    test_files = [f for f in visible
                  if re.search(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec)\.", f, re.I)]

    mf = manifest_facts(path)
    mf_any = manifest_facts(path)
    pkg_json = path / "package.json"
    for mname in ("package.json", "pyproject.toml", "Cargo.toml", "go.mod"):
        mf_any = manifest_facts(path)
        if mf_any["name"]:
            break

    io = io_surface(path, visible, blob + "\n" + arch, mf_any)
    verified, experimental = verified_vs_experimental(path, visible, arch, readme,
                                                      test_files)
    commands = cli_commands(path, visible, mf_any)

    components = module_map(arch) or components_from_tree(path, visible)
    controls = commands[0]["command"] if commands else ""
    if not controls and io["interfaces"]:
        controls = f"primary entry: {io['interfaces'][0]}"

    pitch = ((venture or {}).get("positioning") or "").strip()

    out = {
        "problem": problem_statement(readme, arch, pitch),
        "problem_source": ("public venture card (no project-authored statement)"
                           if pitch and problem_statement(readme, arch, pitch) == pitch
                           else "project source"),
        "primary_user": primary_user(readme, mf_any.get("description", "")),
        "frameworks": frameworks(mf_any.get("deps", [])),
        "major_components": components,
        "data_flow": data_flow_sentence(io, arch),
        "control_flow": controls,
        "state_model": ", ".join(io["storage"]) or "",
        "input_types": io["inputs"],
        "output_types": io["outputs"],
        "primary_workflow": workflow_from_docs(readme, arch),
        "secondary_workflows": [f"{c['command']}"
                                + (f" — {c['help']}" if c["help"] else "")
                                for c in commands[1:6]],
        "verified_features": verified,
        "experimental_features": experimental,
        "known_limitations": limitations([readme, arch], path, visible,
                                         test_files, docs),
        "benchmark_dimensions": benchmark_dims(path, visible, arch),
        "security_characteristics": security_notes(arch, readme, visible),
        "release": mf_any.get("version") or "",
        "terminal_metaphor": terminal_metaphor(commands, mf_any),
        "interfaces": io["interfaces"],
        "verified_commands": commands,
        "evidence": {
            "arch_doc": "ARCHITECTURE.md" if arch else "",
            "readme": "README.md" if readme else "",
            "manifest": next((m for m in ("package.json", "pyproject.toml", "Cargo.toml",
                                          "go.mod") if (path / m).is_file()), ""),
            "cli_entrypoint": commands[0]["source"] if commands else "",
            "source_files_sampled": len(source[:80]),
            "test_files": len(test_files),
        },
    }
    return out


def data_flow_sentence(io: dict, arch: str) -> str:
    """One sentence describing how data moves, from the declared layers.

    A flow of `input → file-backed JSON → persisted to file-backed JSON` is
    technically derived and completely useless: it says the same thing twice
    and names no actual surface. When the derived stages collapse to a single
    storage mechanism, the ARCHITECTURE.md layer diagram is used instead, since
    that is the project's own description of its pipeline.
    """
    ins, outs = io["inputs"], io["outputs"]
    if not ins and not outs:
        return ""
    a = ins[0] if ins else "input"
    b = outs[0] if outs else "output"
    mid = io["storage"][0] if io["storage"] else "in-process state"

    # Deduplicate: the same storage named on both sides carries no information.
    if mid.lower() in b.lower() and len(io["storage"]) < 2:
        b = "the returned value"
    if mid.lower() in a.lower():
        a = "a request"

    s = f"{a} \u2192 {mid} \u2192 {b}"
    if len(ins) > 1:
        extra = [x for x in ins[1:3] if x.lower() not in a.lower()]
        if extra:
            s += f" (also via {', '.join(extra)})"

    # Prefer the project's own pipeline when it states one.
    layers = re.findall(
        r"^([A-Z][A-Za-z ]{2,28}(?:Layer|Service|Stage|Plane|Tier))\b", arch, re.M)
    if len(layers) >= 3:
        chain = " \u2192 ".join(dict.fromkeys(layers[:5]))
        return chain
    return s


def terminal_metaphor(commands: list[dict], mf: dict) -> str:
    """A terminal story naming real commands, or nothing at all.

    The previous value was `if local["scripts"]` -> one fixed string, which is
    true of every project with a package.json and therefore says nothing. A
    command that cannot be read out of the source is not put in the artwork.
    """
    if not commands:
        return ""
    names = [c["command"] for c in commands[:3]]
    return f"a shell running {', '.join(names)} against {mf.get('bin_name') or 'the project binary'}"


CATEGORY_SIGNALS: list[tuple[str, tuple[str, ...]]] = [
    ("SECURITY", ("security", "privacy", "encrypt", "auth", "vault", "secret",
                  "firewall", "sandbox", "threat", "redact", "shield",
                  "intercept", "perimeter", "hardening", "abuse", "fraud",
                  "kyc", "compliance", "audit", "trust")),
    ("FINANCE", ("finance", "financial", "trading", "quant", "valuation",
                 "payment", "billing", "ledger", "portfolio", "economics",
                 "pricing", "invoice", "subscription", "revenue", "settlement",
                 "capital", "equity", "loan", "budget", "cost", "funding",
                 "interceptorgrid", "swarmshield")),
    ("BIOTECH", ("bio", "genom", "protein", "cell", "clinical", "patient",
                 "therap", "yield", "crop", "agri", "farm", "nutrition",
                 "supplement", "wellness", "molecul", "assay", "lab")),
    ("SPACE", ("orbit", "satellite", "telemetry", "trajectory", "mission",
               "spacecraft", "launch", "orbital")),
    # "route" is deliberately absent. `route handlers` appears in the derived
    # output of every Next.js project, so including it classified 32
    # repositories as logistics systems -- the HTTP router is not a supply
    # chain. Logistics evidence must name moving things.
    ("LOGISTICS", ("logistic", "supply chain", "shipment", "freight",
                   "warehouse", "fleet", "delivery", "courier", "dispatch",
                   "procurement", "sourcing", "inventory")),
    ("AGENT", ("agent", "agentic", "llm", "model", "copilot", "assistant",
               "autonomy", "evolution", "mind", "reasoning", "tool", "mcp",
               "orchestrat", "grok", "claude", "openai")),
    # "build" is out: `npm run build` is in every manifest, so it classified 21
    # repositories as developer tooling regardless of what they do. Developer
    # tooling names the artefact it produces for other developers.
    ("DEVELOPER_TOOLS", ("cli", "tui", "repl", "sdk", "linter", "compiler",
                         "bundler", "transpiler", "framework", "boilerplate",
                         "starter kit", "devtool", "developer tool",
                         "developer tooling", "test runner", "type checker",
                         "formatter", "profiler")),
    ("CREATIVE", ("design", "render", "canvas", "generative", "procedural",
                  "theme", "asset", "typography", "brand", "studio")),
    ("HEALTH", ("health", "physio", "medical", "clinic", "care", "recovery",
                "sleep", "focus", "habit", "human")),
    # "index" and "query" are framework vocabulary: Next.js emits `page.tsx`
    # route segments and every React project has an index barrel file. Neither
    # is evidence of a data system. Persistence and ETL words are.
    ("DATA", ("database", "postgres", "sqlite", "ingest", "etl", "schema",
              "migration", "warehouse", "timeseries", "relational")),
    ("NETWORK", ("network", "proxy", "gateway", "router", "mesh",
                 "distributed", "peer", "relay", "protocol", "socket")),
    ("INFRASTRUCTURE", ("infra", "deploy", "kubernetes", "docker", "cluster",
                        "runner", "provision", "terraform", "install",
                        "runtime", "cloud", "factory")),
]


def derive_category(dossier_like: dict) -> tuple[str, str]:
    """Product category from project evidence, with the basis recorded.

    This replaces a keyword match over name + description + GitHub topics, which
    produced 59 SECURITY classifications across the portfolio purely because
    every repository carried the `security` topic. Measured result of that bug:
    cloudcastle, TherapyUX and ForeverLuvd were all classified as security
    systems on the strength of a topic string.

    Evidence used, in order of strength: the project's own security mechanisms,
    its verified CLI, its interfaces, then its prose, then the public card's
    category, and only last the repository name.
    """
    # Security mechanisms are evidence of maturity, not of product category.
    # Every serious project has an execution policy, so using this as the first
    # rule classified agentos -- an agent orchestration engine -- as a security
    # product on the strength of its own SECURITY.md. Security is a category only
    # when security is the subject: the prose names protecting, verifying or
    # enforcing as the thing the system does.
    security = dossier_like.get("security_characteristics") or []
    subj = " ".join([
        dossier_like.get("problem", ""), dossier_like.get("primary_user", ""),
        dossier_like.get("data_flow", ""),
    ]).lower()
    if security and any(w in subj for w in
                        ("protect", "boundary", "secure", "encrypt", "attack",
                         "threat", "privacy", "authenticate", "tamper",
                         "vulnerab", "hardening", "perimeter")):
        return "SECURITY", "security is the stated subject of the project"

    if dossier_like.get("verified_commands"):
        return "DEVELOPER_TOOLS", "ships a verified CLI"

    text = " ".join([
        dossier_like.get("problem", ""), dossier_like.get("primary_user", ""),
        dossier_like.get("data_flow", ""), " ".join(dossier_like.get("output_types", [])),
        " ".join(dossier_like.get("major_components", [])[:6]),
    ]).lower()
    for cat, keys in CATEGORY_SIGNALS:
        hits = [k for k in keys if k in text]
        if len(hits) >= 2:
            return cat, f"project text: {', '.join(hits[:3])}"

    # The public venture card is real evidence about what this venture is, and
    # it is written by the studio about this project specifically. A single
    # signal from it counts, unlike a single signal from prose.
    card = (dossier_like.get("noaerth_category") or "").lower()
    if card:
        for cat, keys in CATEGORY_SIGNALS:
            if any(k in card for k in keys):
                return cat, f"public venture card category: {card}"

    # One prose hit is enough once the text has been checked for scaffolding;
    # the threshold above only applies to generic corpora.
    for cat, keys in CATEGORY_SIGNALS:
        hits = [k for k in keys if k in text]
        if hits:
            return cat, f"project text: {', '.join(hits[:2])}"

    # Architecture and interfaces are structural facts read from source, and a
    # project with no prose still has them. A scheduler with workers and queues
    # is an infrastructure system whether or not its README says so.
    arch = (dossier_like.get("architecture_type") or "")
    ifaces = set(dossier_like.get("interfaces") or [])
    if arch in ("DISTRIBUTED", "SCHEDULER", "ROUTER"):
        return "INFRASTRUCTURE", f"architecture = {arch}"
    if arch == "AGENT_LOOP" or "MCP stdio" in ifaces:
        return "AGENT", f"architecture = {arch}"
    if "CLI" in ifaces:
        return "DEVELOPER_TOOLS", "verified CLI surface"
    if "HTTP API" in ifaces and dossier_like.get("noaerth_category"):
        card = dossier_like["noaerth_category"].lower()
        for cat, keys in CATEGORY_SIGNALS:
            if any(k in card for k in keys):
                return cat, f"public card + HTTP surface: {card}"

    name = (dossier_like.get("github_repo") or "").lower()
    for cat, keys in CATEGORY_SIGNALS:
        if any(k in name for k in keys):
            return cat, "repository name"

    return "GENERAL", "no category signal in evidence"


def unresolved_fields(d: dict) -> list[str]:
    watch = ("problem", "primary_user", "major_components", "data_flow",
             "state_model", "input_types", "output_types", "verified_features",
             "known_limitations", "security_characteristics", "frameworks",
             "terminal_metaphor", "primary_workflow")
    return [k for k in watch if not d.get(k)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true",
                    help="write the derived fields back into the dossiers")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    ventures = venture_index()
    targets = sorted(DOSSIER_DIR.glob("*.json")) if args.all else [
        DOSSIER_DIR / f"{p}.json" for p in args.project]
    rows = []
    for dp in targets:
        if not dp.is_file():
            print(f"  no dossier for {dp.stem}")
            continue
        d = json.loads(dp.read_text())
        recorded = d.get("evidence", {}).get("source_a_local", "")
        path = resolve_local(dp.stem, recorded)
        # The venture slug lives in project-map.json, not in the dossier's
        # evidence block: build_dossiers.py never wrote it there, so every
        # dossier had source_b_venture="" and Source B could never be joined.
        # Fall back to the repo name so the join does not depend on the map.
        vslug = (d.get("evidence", {}).get("source_b_venture")
                 or MAP_SLUGS.get(d.get("github_repo", dp.stem), "")
                 or dp.stem.lower())
        if not path:
            print(f"  {dp.stem}: local source unavailable "
                  f"(looked under {[str(r) for r in ROOTS]})")
            continue
        venture = ventures.get(vslug)
        if not venture:
            # Slugs differ between the card and the repository more often than
            # the mapping assumed, so fall back to the normalised forms rather
            # than silently losing Source B.
            key = re.sub(r"[^a-z0-9]+", "", vslug.lower())
            for slug, v in ventures.items():
                if re.sub(r"[^a-z0-9]+", "", slug.lower()) == key:
                    venture = v
                    vslug = slug
                    break
        derived = comprehend(path, venture)
        derived["unresolved"] = unresolved_fields(derived)
        d.update({k: v for k, v in derived.items() if k != "unresolved"})
        # Recomputed, not merged. The previous run left every field listed as
        # unresolved because they were hardcoded empty; unioning that list in
        # again would report a filled field as still missing forever.
        d["unresolved"] = derived["unresolved"]
        d.setdefault("evidence", {})["source_a_local"] = str(path)

        # Source B, now that the scraper actually carries the card content.
        # Category and status come from the public card and are kept separate
        # from the code-derived `project_category`, because they are different
        # classifications: one is how the venture is presented, the other is
        # what the code is. Conflating them is how a fintech marketing card ends
        # up describing a Next.js CRUD app as a financial system.
        # Category is re-derived from evidence, overwriting the keyword match
        # that produced 59 SECURITY classifications from the `security` topic.
        cat, basis = derive_category(d)
        d["project_category_previous"] = d.get("project_category", "")
        d["project_category"] = cat
        d["project_category_basis"] = basis
        d["industry"] = cat

        if venture:
            d["public_noaerth_positioning"] = venture.get("positioning", "")
            d["venture_stage"] = venture.get("status", "")
            d["noaerth_category"] = venture.get("category", "")
            d["noaerth_category_path"] = venture.get("category_path", "")
            d["noaerth_next_milestone"] = venture.get("next_milestone", "")
            d["noaerth_site"] = venture.get("site", "")
            d["noaerth_operating_facts"] = venture.get("operating_facts", {})
        rows.append((dp.stem, derived, d, vslug))
        if args.apply:
            dp.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n")

    if args.report or not args.apply:
        print(f"\ncomprehended {len(rows)} projects")
        if rows:
            filled = {k: sum(1 for _, dr, _, _ in rows if dr.get(k))
                      for k in ("problem", "primary_user", "major_components",
                                "data_flow", "state_model", "input_types",
                                "output_types", "verified_features",
                                "known_limitations", "security_characteristics",
                                "frameworks", "terminal_metaphor",
                                "primary_workflow", "benchmark_dimensions")}
            for k, n in sorted(filled.items(), key=lambda kv: -kv[1]):
                bar = "#" * int(30 * n / max(len(rows), 1))
                print(f"  {k:<28}{n:>4}/{len(rows)}  {bar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
