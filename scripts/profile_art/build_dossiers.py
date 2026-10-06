#!/usr/bin/env python3
"""Build project-map.json and per-repository dossiers from three sources.

  SOURCE A  local project source   /Users/matador/startups/<project>
  SOURCE B  public venture card    .noaerth-public-ventures.json
  SOURCE C  live GitHub repository

Nothing is asserted about a project that the sources do not support. A field
that cannot be determined is left empty and the dossier records why, because a
dossier full of confident guesses is worse than no dossier: it would then drive
the visual identity, and the art would encode the guess.

Mapping is never guessed. Where the local folder, the GitHub repository and the
venture slug do not correspond confidently, the record is marked
MAPPING_REVIEW_REQUIRED and no project claims are emitted.

  python3 scripts/profile_art/build_dossiers.py --limit 10
  python3 scripts/profile_art/build_dossiers.py --all
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
LOCAL = Path("/Users/matador/startups")
LEDGER = PROFILE / "github-account-ledger.json"
VENTURES = PROFILE / ".noaerth-public-ventures.json"
OUT_MAP = PROFILE / "project-map.json"
DOSSIER_DIR = PROFILE / ".github-art" / "dossiers"

OWNER = "M4G3LL4N0"
DENY_SUB = ("noaerth", "autobuilder", "pairs")
DENY_EXACT = {"paios-one", "openlegal-data"}
SKIP_LOCAL = re.compile(r"(-website|-site)$", re.I)

SOURCE_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".go", ".rs",
              ".rb", ".java", ".kt", ".swift", ".c", ".cpp", ".cs", ".sql")
MANIFEST = ("package.json", "pyproject.toml", "requirements.txt", "go.mod",
            "Cargo.toml", "pom.xml", "build.gradle", "composer.json")
TEST = re.compile(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec)\.", re.I)
SKIP_DIR = re.compile(r"(^|/)(node_modules|\.git|dist|build|\.next|vendor|"
                      r"coverage|\.venv|__pycache__|target|out)/")


def tok() -> str:
    return os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def gh_json(path: str):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                       env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def denied(name: str) -> bool:
    low = name.lower()
    return any(s in low for s in DENY_SUB) or low in DENY_EXACT


# ---------------------------------------------------------------- Source A

def local_index() -> dict[str, Path]:
    """Local project folders, keyed by every plausible alias.

    Website folders are indexed but flagged, because they are presentation
    layers and may inform positioning while never informing architecture.
    """
    out: dict[str, Path] = {}
    if not LOCAL.is_dir():
        return out
    for child in sorted(LOCAL.iterdir()):
        if not child.is_dir() or not (child / ".git").exists():
            continue
        key = child.name.lower()
        out[key] = child
        if SKIP_LOCAL.search(child.name):
            out[key + "#website"] = child
        else:
            out[key.replace("-", "")] = child
            out[key.replace("-", "_")] = child
    return out


def inspect_local(path: Path) -> dict:
    files: list[str] = []
    try:
        proc = subprocess.run(["git", "-C", str(path), "ls-files"],
                              capture_output=True, text=True, timeout=25)
        files = [f for f in proc.stdout.splitlines() if f.strip()]
    except Exception:
        pass
    visible = [f for f in files if not SKIP_DIR.search(f)]
    src = [f for f in visible if f.endswith(SOURCE_EXT)]
    tests = [f for f in visible if TEST.search(f)]
    docs = [f for f in visible if f.endswith((".md", ".rst", ".txt"))]
    root = [f for f in visible if "/" not in f]
    manifests = [f for f in root if f in MANIFEST]
    scripts: dict[str, str] = {}
    for m in manifests:
        if m == "package.json":
            try:
                scripts["npm"] = json.dumps(json.loads(
                    (path / m).read_text(errors="replace")).get("scripts") or {})[:1500]
            except Exception:
                pass
    commits = "unknown"
    try:
        c = subprocess.run(["git", "-C", str(path), "rev-list", "--count", "HEAD"],
                           capture_output=True, text=True, timeout=20)
        if c.returncode == 0:
            commits = c.stdout.strip()
    except Exception:
        pass
    return {
        "path": str(path), "files": len(visible), "source": src, "tests": tests,
        "docs": docs, "root": root, "manifests": manifests, "scripts": scripts,
        "commits": commits,
        "architecture_doc": (path / "ARCHITECTURE.md").read_text(errors="replace")[:6000]
                            if (path / "ARCHITECTURE.md").is_file() else "",
        "readme_text": (path / "README.md").read_text(errors="replace")[:4000]
                       if (path / "README.md").is_file() else "",
        "has_readme": "README.md" in root,
        "has_ci": any(f.startswith(".github/workflows/") for f in files),
        "is_website": bool(SKIP_LOCAL.search(path.name)),
    }


# ---------------------------------------------------------------- Source B

def venture_index() -> dict[str, dict]:
    if not VENTURES.exists():
        return {}
    data = json.loads(VENTURES.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for v in data.get("ventures", []):
        if v["name"].startswith("_"):
            continue
        for key in (v["slug"], v["name"].lower(),
                    re.sub(r"[^a-z0-9]+", "", v["name"].lower())):
            out[key] = v
    return out


# ---------------------------------------------------------------- Source C

def github_index() -> list[dict]:
    p = subprocess.run(
        ["gh", "repo", "list", OWNER, "--limit", "1000", "--json",
         "name,description,repositoryTopics,homepageUrl,isArchived,isFork,"
         "visibility,primaryLanguage,createdAt,pushedAt"],
        capture_output=True, text=True,
        env=dict(os.environ, GH_TOKEN=tok(), GH_PAGER="cat"))
    try:
        return json.loads(p.stdout or "[]")
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------- mapping

def slug_variants(name: str) -> list[str]:
    low = name.lower()
    return [low, low.replace("-", ""), low.replace("_", ""),
            low.replace("-", "_"), re.sub(r"[^a-z0-9]+", "", low)]


def map_repository(repo: dict, local: dict[str, Path],
                   ventures: dict[str, dict]) -> dict:
    name = repo["name"]
    local_path = None
    confidence = "none"
    basis: list[str] = []

    # A website repository maps to its parent project, never to itself.
    if SKIP_LOCAL.search(name):
        parent = name[:-len("-website")] if name.endswith("-website") else name
        cand = local.get(parent.lower())
        if cand and not cand.name.endswith(("-website", "-site")):
            local_path = cand
            confidence = "high"
            basis.append("website repository maps to its parent project folder")
    else:
        for key in slug_variants(name):
            cand = local.get(key)
            if cand and not SKIP_LOCAL.search(cand.name):
                local_path = cand
                confidence = "high"
                basis.append("local folder name matches repository name")
                break

    if local_path is None:
        # git remote match: does any local repo point at this GitHub repo?
        try:
            proc = subprocess.run(
                ["git", "-C", str(LOCAL), "config", "--get-regexp",
                 r"remote\..*\.url"], capture_output=True, text=True, timeout=25)
        except Exception:
            proc = None
        if proc and proc.stdout:
            for line in proc.stdout.splitlines():
                if re.search(rf"{re.escape(name)}(\.git)?\s*$", line.strip()):
                    folder = line.split()[1]
                    cand = LOCAL / folder
                    if cand.is_dir():
                        local_path = cand
                        confidence = "medium"
                        basis.append("matched by git remote URL")

    venture = None
    for key in slug_variants(name):
        if key in ventures:
            venture = ventures[key]
            confidence = "high" if confidence == "high" else confidence or "medium"
            basis.append("matched a public venture card")
            break

    if confidence == "none" and (local_path or venture):
        confidence = "low"

    record = {
        "github_repo": name,
        "github_url": f"https://github.com/{OWNER}/{name}",
        "local_project_path": str(local_path) if local_path else "",
        "noaerth_venture_slug": venture["slug"] if venture else "",
        "noaerth_venture_url": (f"https://www.noaerth.com/{venture['slug']}"
                                if venture else ""),
        "canonical_project_name": venture["name"] if venture else name,
        "aliases": [k for k in slug_variants(name) if k][:5],
        "classification": "EXCLUDED_DENYLISTED" if denied(name) else "",
        "confidence": confidence if confidence != "none" else "MAPPING_REVIEW_REQUIRED",
        "basis": basis,
        "visibility": str(repo.get("visibility", "")).lower(),
        "website_repository": bool(SKIP_LOCAL.search(name)),
    }
    return record


# ---------------------------------------------------------------- dossier

FLAGSHIP_ORDER = ("agentos", "grokinstall", "grokmax", "gh0st",
                  "opencode-watchdog")
FLAGSHIPS = set(FLAGSHIP_ORDER)

CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("SECURITY", ("security", "privacy", "encrypt", "auth", "vault", "secret",
                  "firewall", "sandbox", "threat", "redact")),
    ("FINANCE", ("finance", "trading", "quant", "valuation", "payment",
                 "billing", "ledger", "portfolio", "economics", "pricing")),
    ("QUANT", ("signal", "backtest", "simulation", "probability", "telemetry",
               "metric", "anomaly", "forecast")),
    ("BIOTECH", ("bio", "genom", "protein", "cell", "clinical", "health", "patient")),
    ("SPACE", ("orbit", "satellite", "telemetry", "trajectory", "mission")),
    ("LOGISTICS", ("logistic", "supply", "route", "shipment", "fleet", "warehouse")),
    ("DATA", ("database", "index", "ingest", "query", "store", "pipeline",
              "schema", "migration", "sync")),
    ("NETWORK", ("network", "proxy", "gateway", "router", "mesh", "distributed",
                 "peer", "relay", "protocol", "socket")),
    ("INFRASTRUCTURE", ("infra", "deploy", "kubernetes", "docker", "cluster",
                        "runner", "provision", "terraform", "install", "runtime")),
    ("AGENT", ("agent", "agentic", "llm", "model", "copilot", "assistant",
               "autonomy", "evolution", "mind", "reasoning", "tool")),
    ("DEVELOPER_TOOLS", ("cli", "tui", "terminal", "sdk", "library", "package",
                         "build", "linter", "compiler", "debug")),
    ("CREATIVE", ("design", "render", "canvas", "generative", "procedural",
                  "theme", "asset", "typography")),
]

# Architecture families -> animation metaphor. Motion must express what the
# system does, so the family is chosen from the architecture rather than from
# the category alone.
# Composed animation stories. Resolved from architecture AND category, because
# a data flow in a security product is not the same motion as a data flow in a
# financial one: the first is a boundary holding, the second is capital
# settling. Keyed (architecture, category) with an architecture-only fallback.
ARCH_CATEGORY_ANIMATION = {
    ("DATA_FLOW", "SECURITY"): "records cross a trust boundary, get validated, and are held or rejected",
    ("DATA_FLOW", "FINANCE"): "capital enters, allocates across positions, and settles into an outcome",
    ("DATA_FLOW", "AGENT"): "an objective becomes context, tools read and write state, the loop closes",
    ("DATA_FLOW", "DEVELOPER_TOOLS"): "a dependency graph resolves, packages install, the build advances",
    ("DATA_FLOW", "GENERAL"): "records ingest, normalise, index, answer",
    ("DOCUMENT", "SECURITY"): "policy surfaces assemble into a readable security posture",
    ("DOCUMENT", "FINANCE"): "scenarios lay out side by side for comparison",
    ("DOCUMENT", "GENERAL"): "sections assemble and settle into a readable surface",
    ("DOCUMENT", "AGENT"): "documentation resolves into an explanation a reader can follow",
    ("DISTRIBUTED", "INFRASTRUCTURE"): "nodes advertise capability, a coordinator selects, work converges",
    ("AGENT_LOOP", "AGENT"): "objective becomes a plan, tools execute, verification resolves the answer",
    ("SCHEDULER", "INFRASTRUCTURE"): "jobs enter, queue, lease, complete",
    ("CLI", "DEVELOPER_TOOLS"): "a cursor runs real commands and the output resolves",
    ("SECURITY", "SECURITY"): "threat approaches a boundary, the boundary reacts, the path closes",
    ("ROUTER", "GENERAL"): "requests arrive, candidates narrow, one route is selected",
    ("GENERATIVE", "GENERAL"): "a seed expands into structured form",
    ("LIBRARY", "DEVELOPER_TOOLS"): "symbols resolve against a dependency graph",
}

ARCH_CATEGORY_GEOMETRY = {
    ("DATA_FLOW", "SECURITY"): "gated channels passing through a sealed boundary",
    ("DATA_FLOW", "FINANCE"): "ledger columns with allocation flow between them",
    ("DATA_FLOW", "AGENT"): "a state ring with tool nodes attached",
    ("DATA_FLOW", "DEVELOPER_TOOLS"): "an orthogonal dependency lattice",
    ("DOCUMENT", "SECURITY"): "nested policy frames with a visible boundary edge",
    ("DOCUMENT", "FINANCE"): "scenario panels on a comparative plane",
    ("DISTRIBUTED", "INFRASTRUCTURE"): "a service mesh with one coordinating node",
    ("AGENT_LOOP", "AGENT"): "a closed loop with a verification terminus",
}

ARCH_ANIMATION = {
    "SCHEDULER": "jobs enter, queue, lease, complete",
    "PIPELINE": "source transforms through ordered stages into a verified result",
    "ROUTER": "requests arrive, candidates narrow, one route is selected",
    "AGENT_LOOP": "objective becomes a plan, tools execute, verification resolves",
    "CLI": "a cursor executes real commands and the output resolves",
    "DATA_FLOW": "records ingest, normalise, index, answer",
    "SECURITY": "threat approaches a boundary, the boundary reacts, the path closes",
    "DISTRIBUTED": "peers exchange state and converge",
    "GENERATIVE": "a seed expands into structured form",
    "DOCUMENT": "sections assemble and settle",
    "LIBRARY": "symbols resolve against a dependency graph",
    "STATIC": "a form resolves from a wireframe into solid geometry",
}

ARCH_GEOMETRY = {
    "SCHEDULER": "queue lanes with lease markers",
    "PIPELINE": "ordered faceted stages left to right",
    "ROUTER": "radial convergence onto a selected node",
    "AGENT_LOOP": "closed loop with a verification terminus",
    "CLI": "compact instrument panel with a terminal rail",
    "DATA_FLOW": "parallel channels converging into an index",
    "SECURITY": "closed concentric containment around a protected core",
    "DISTRIBUTED": "lattice with partial connectivity",
    "GENERATIVE": "aperture fan expanding from a seed point",
    "DOCUMENT": "nested frames with a typographic rail",
    "LIBRARY": "orthogonal dependency graph",
    "STATIC": "soft tiles on an isometric plane",
}


def detect_architecture(name: str, local: dict, description: str) -> str:
    """Architecture family, read from the project's own documentation.

    The previous version inferred PIPELINE for anything with a package.json,
    which collapsed most of the portfolio onto one geometry and one motion
    story. That is precisely the failure where one template produces a hundred
    skins. The signal is taken from ARCHITECTURE.md first, which every project
    here ships, then from structure, and only then from keywords.
    """
    doc = (local.get("architecture_doc") or "").lower()
    readme = (local.get("readme_text") or "").lower()
    blob = f"{name} {description} {' '.join(local.get('root', []))}".lower()
    text = f"{doc}\n{readme}\n{blob}"
    root = {f.lower() for f in local.get("root", [])}
    src = [f.lower() for f in local.get("source", [])]

    # Explicit runtime statements first: the project's own words beat inference.
    if "next.js" in doc or "nextjs" in doc:
        # Code structure decides, not prose. ARCHITECTURE.md here describes
        # layers including "API | app/api routes (if any)", so matching the
        # words "api route" classified a repository with no API routes at all
        # as DATA_FLOW. Presence of handlers is checked in the file list.
        if any("/api/" in f or f.startswith("app/api") for f in src):
            return "DATA_FLOW"
        return "DOCUMENT"          # a Next surface is a rendered document
    if "cli" in doc[:400] or "command-line" in doc[:400] or "command line" in doc[:400]:
        return "CLI"
    if any(k in doc for k in ("daemon", "long-running", "background worker")):
        return "SCHEDULER"
    if any(k in doc for k in ("websocket", "event stream", "sse", "realtime",
                             "real-time", "push channel")):
        return "DISTRIBUTED"
    if any(k in doc for k in ("queue", "lease", "retry", "backoff", "job runner",
                             "worker pool", "concurrency")):
        return "SCHEDULER"
    if any(k in doc for k in ("router", "routing", "provider selection",
                             "model selection", "route selection")):
        return "ROUTER"
    if any(k in doc for k in ("agent", "tool call", "plan", "verify", "loop")):
        return "AGENT_LOOP"
    if any(k in doc for k in ("encrypt", "keystore", "threat", "trust boundary",
                             "sandbox", "permission")):
        return "SECURITY"
    if any(k in doc for k in ("sqlite", "postgres", "index", "migration",
                             "schema", "repository")):
        return "DATA_FLOW"
    if any(k in doc for k in ("library", "package", "sdk", "published module")):
        return "LIBRARY"
    if any(k in doc for k in ("render", "canvas", "generative", "procedural",
                             "shader", "svg")):
        return "GENERATIVE"

    # No architecture document. Classify from what the project says it *does*,
    # read from its description, before falling back to keyword archaeology.
    #
    # grokinstall was classified SCHEDULER because "queue" appears somewhere in
    # its internals. It is a Go CLI that inspects a repository and installs the
    # smallest useful capability; there is no scheduler. Matching an incidental
    # keyword produces art that depicts a system the project is not.
    verb = description.lower()
    if re.search(r"\b(cli|command[- ]line)\b", verb) or \
            any(p in root for p in ("cli.py", "main.go", "cmd", "bin")):
        return "CLI"
    if re.search(r"\bwatchdog|monitor|observe|detect\b", verb):
        return "SCHEDULER"
    if re.search(r"\b(router|proxy|gateway|route)\b", verb):
        return "ROUTER"
    if re.search(r"\b(agent|planner|orchestrat|evolv)\b", verb):
        return "AGENT_LOOP"
    if re.search(r"\b(encrypt|privacy|offline|local[- ]first)\b", verb):
        return "SECURITY"
    if re.search(r"\b(store|database|index|query|records)\b", verb):
        return "DATA_FLOW"
    if re.search(r"\b(library|sdk|package|toolkit|helper)\b", verb):
        return "LIBRARY"

    # Structure, when there is no architecture document to read.
    if any("/api/" in f or f.startswith("app/api") for f in src):
        return "DATA_FLOW"
    if any(p in root for p in ("cli.py", "main.go", "index.ts", "__main__.py")):
        return "CLI"
    if any("/queue" in f or "/worker" in f or "/scheduler" in f for f in src):
        return "SCHEDULER"
    if any(k in blob for k in ("scheduler", "queue", "cron", "worker", "job")):
        return "SCHEDULER"
    if any(k in blob for k in ("router", "gateway", "proxy", "route")):
        return "ROUTER"
    if any(k in blob for k in ("agent", "mind", "evolution", "orchestrat")):
        return "AGENT_LOOP"
    if any(k in blob for k in ("encrypt", "security", "privacy", "auth")):
        return "SECURITY"
    if any(k in blob for k in ("database", "sqlite", "postgres", "index", "store")):
        return "DATA_FLOW"
    if any(k in blob for k in ("node", "peer", "mesh", "distributed", "fleet")):
        return "DISTRIBUTED"
    if any(k in blob for k in ("render", "canvas", "generative", "procedural")):
        return "GENERATIVE"
    if not local.get("source"):
        return "DOCUMENT" if local.get("docs") else "STATIC"
    return "PIPELINE"


def detect_category(name: str, description: str, topics: list[str]) -> str:
    blob = f"{name} {description} {' '.join(topics)}".lower()
    for cat, keys in CATEGORY_RULES:
        if any(k in blob for k in keys):
            return cat
    return "GENERAL"


def build_dossier(m: dict, repo: dict, local: dict, venture: dict | None) -> dict:
    desc = (repo.get("description") or "").strip()
    topics = [t["name"] if isinstance(t, dict) else t
              for t in (repo.get("repositoryTopics") or [])]
    arch = detect_architecture(m["github_repo"], local, desc)
    cat = detect_category(m["github_repo"], desc, topics)
    lang = ((repo.get("primaryLanguage") or {}).get("name") or "")

    d = {
        "canonical_name": m["canonical_project_name"],
        # Class comes from the identity registry, not from the repository, so
        # a flagship is a flagship everywhere: in its dossier, its hero, its
        # intensity budget and its README structure.
        "classification": ("FLAGSHIP" if m["github_repo"] in FLAGSHIPS
                           else "PUBLIC_ARCHIVE" if repo.get("isArchived")
                           else "PUBLIC_PROJECT"),
        "github_repo": m["github_repo"],
        "design_version": "V6",
        "mapping_confidence": m["confidence"],

        "purpose": desc,
        "problem": "",
        "primary_user": "",
        "project_category": cat,
        "industry": cat,
        "technical_category": arch,
        "languages": [lang] if lang else sorted({
            Path(f).suffix.lstrip(".") for f in local.get("source", [])
            if Path(f).suffix})[:4],
        "frameworks": [],
        "architecture_type": arch,
        "major_components": [],
        "data_flow": "",
        "control_flow": ARCH_CATEGORY_ANIMATION.get((arch, cat),
                                                    ARCH_ANIMATION[arch]),
        "state_model": "",

        "input_types": [],
        "output_types": [],

        "primary_workflow": ARCH_CATEGORY_ANIMATION.get((arch, cat),
                                                       ARCH_ANIMATION[arch]),
        "secondary_workflows": [],

        "verified_features": [],
        "experimental_features": [],
        "known_limitations": [],
        "tests": {
            "present": bool(local.get("tests")),
            "files": len(local.get("tests", [])),
            "executed": False,
            "note": "counted from the tree; not executed in Part 1",
        },
        "ci": {"present": bool(local.get("has_ci")),
               "workflows": [f for f in local.get("root", [])
                             if f.startswith(".github/workflows")]},
        "release": "unknown",
        "benchmark_dimensions": [],
        "security_characteristics": [],

        "public_noaerth_positioning": (venture or {}).get("positioning", ""),
        "venture_stage": (venture or {}).get("status", ""),
        "public_financial_context": "not published per venture",

        "primary_visual_metaphor": ARCH_CATEGORY_GEOMETRY.get(
            (arch, cat), ARCH_GEOMETRY[arch]),
        "secondary_visual_metaphor": "",
        "animation_metaphor": ARCH_CATEGORY_ANIMATION.get((arch, cat),
                                                           ARCH_ANIMATION[arch]),
        "terminal_metaphor": ("a cursor running real commands"
                              if local.get("scripts") else ""),
        "geometry_family": arch,
        "material_family": "",
        "color_family": "",
        "depth": "layered",
        "visual_density": "medium",
        "trillionx_intensity": "standard",

        "evidence": {
            "source_a_local": local.get("path", ""),
            "source_a_files": local.get("files", 0),
            "source_a_commits": local.get("commits", "unknown"),
            "source_b_venture": (venture or {}).get("slug", ""),
            "source_c_github": m["github_url"],
        },
        "unresolved": [],
    }
    missing = [k for k in ("purpose", "primary_user", "problem") if not d[k]]
    d["unresolved"] = missing
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    repos = [r for r in github_index()
             if str(r.get("visibility", "")).lower() == "public"
             and not denied(r["name"])]
    repos.sort(key=lambda r: r["name"].lower())
    if not args.all:
        repos = repos[: args.limit]

    local = local_index()
    ventures = venture_index()

    maps = []
    for repo in repos:
        m = map_repository(repo, local, ventures)
        ld = inspect_local(Path(m["local_project_path"])) \
            if m["local_project_path"] and Path(m["local_project_path"]).is_dir() \
            else {"path": "", "files": 0, "source": [], "tests": [], "docs": [],
                  "root": [], "manifests": [], "scripts": {}, "commits": "unknown",
                  "has_readme": False, "has_ci": False, "is_website": False}
        venture = ventures.get(m["noaerth_venture_slug"]) if m["noaerth_venture_slug"] \
            else None
        d = build_dossier(m, repo, ld, venture)
        maps.append({"map": m, "dossier": d})
        if m["confidence"] == "MAPPING_REVIEW_REQUIRED":
            continue
        DOSSIER_DIR.mkdir(parents=True, exist_ok=True)
        (DOSSIER_DIR / f"{repo['name']}.json").write_text(
            json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    OUT_MAP.write_text(json.dumps({
        "$comment": "Repository to local project to venture slug. Confidence is "
                    "never assumed; MAPPING_REVIEW_REQUIRED means no project "
                    "claims were emitted for that repository.",
        "owner": OWNER,
        "count": len(maps),
        "records": [{"map": m["map"],
                     "dossier_path": (f".github-art/dossiers/{m['map']['github_repo']}.json"
                                      if m["map"]["confidence"] != "MAPPING_REVIEW_REQUIRED"
                                      else "")}
                    for m in maps],
    }, indent=1) + "\n", encoding="utf-8")

    conf = {}
    for m in maps:
        conf[m["map"]["confidence"]] = conf.get(m["map"]["confidence"], 0) + 1
    print(f"mapped {len(maps)} repositories")
    for k, v in sorted(conf.items()):
        print(f"  {k:<28}{v}")
    vm = sum(1 for m in maps if m["map"]["noaerth_venture_slug"])
    lm = sum(1 for m in maps if m["map"]["local_project_path"])
    print(f"  with local project source: {lm}")
    print(f"  with venture card        : {vm}")
    print(f"  dossiers written         : "
          f"{len(list(DOSSIER_DIR.glob('*.json'))) if DOSSIER_DIR.exists() else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())